"""Test putting the code developed in ``steps`` into the notebook's cells.

The notebook and the steps can disagree in several ways, and each of them silently publishing the
wrong code is exactly what naming the cells is meant to prevent. Each way therefore has a test.
"""

# pylint: disable=missing-function-docstring

import json
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import embed_steps


def write_step(steps: Path, name: str, cell: str) -> None:
    steps.mkdir(exist_ok=True)
    (steps / f"{name}.py").write_text(f"# The context.\nimport os\n\n{embed_steps.CELL_MARKER}\n{cell}\n")


def code_cell(step: Optional[str], source: str = "") -> Dict[str, Any]:
    metadata: Dict[str, Any] = {} if step is None else {embed_steps.METADATA_KEY: {embed_steps.STEP_KEY: step}}
    return {"cell_type": "code", "execution_count": None, "metadata": metadata, "outputs": [], "source": source}


def write_notebook(path: Path, cells: List[Dict[str, Any]]) -> None:
    path.write_text(json.dumps({"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}, indent=1) + "\n")


def embed(monkeypatch, tmp_path: Path, notebook: Path, *names: str, check: bool = False) -> int:
    monkeypatch.setattr(embed_steps, "STEPS", tmp_path / "steps")
    arguments = ["embed_steps.py"] + (["--check"] if check else []) + [str(notebook)] + list(names)
    monkeypatch.setattr("sys.argv", arguments)
    return embed_steps.main()


def a_good_pair(tmp_path: Path) -> Path:
    """Two steps, and a notebook whose cells name them in the right order and hold their code."""
    steps = tmp_path / "steps"
    write_step(steps, "first", "print('first')")
    write_step(steps, "second", "print('second')")
    notebook = tmp_path / "notebook.ipynb"
    write_notebook(notebook, [code_cell("first", "print('first')"), code_cell("second", "print('second')")])
    return notebook


def test_up_to_date_does_not_touch_the_notebook(monkeypatch, tmp_path, capsys) -> None:
    notebook = a_good_pair(tmp_path)

    # The generated documents depend on the notebook, so rewriting it when nothing changed would
    # regenerate them for nothing.
    modified_at = notebook.stat().st_mtime_ns
    assert embed(monkeypatch, tmp_path, notebook, "first", "second") == 0
    assert notebook.stat().st_mtime_ns == modified_at
    assert "UP TO DATE" in capsys.readouterr().out


def test_embeds_the_code_of_each_step(monkeypatch, tmp_path, capsys) -> None:
    notebook = a_good_pair(tmp_path)
    write_step(tmp_path / "steps", "second", "print('changed')")

    assert embed(monkeypatch, tmp_path, notebook, "first", "second") == 0

    cells = json.loads(notebook.read_text())["cells"]
    assert [cell["source"] for cell in cells] == ["print('first')", "print('changed')"]
    assert "EMBEDDED second" in capsys.readouterr().out


def test_only_the_cell_is_embedded(monkeypatch, tmp_path) -> None:
    notebook = a_good_pair(tmp_path)
    write_step(tmp_path / "steps", "first", "print('only this')")

    embed(monkeypatch, tmp_path, notebook, "first", "second")

    # The context above the marker is what the notebook already has, and is not published.
    assert json.loads(notebook.read_text())["cells"][0]["source"] == "print('only this')"


def test_checking_reports_without_writing(monkeypatch, tmp_path, capsys) -> None:
    notebook = a_good_pair(tmp_path)
    write_step(tmp_path / "steps", "second", "print('changed')")
    modified_at = notebook.stat().st_mtime_ns

    assert embed(monkeypatch, tmp_path, notebook, "first", "second", check=True) == 1
    assert notebook.stat().st_mtime_ns == modified_at
    assert "does not hold this step's cell" in capsys.readouterr().out


def test_a_cell_naming_no_step(monkeypatch, tmp_path, capsys) -> None:
    notebook = a_good_pair(tmp_path)
    cells = json.loads(notebook.read_text())["cells"] + [code_cell(None)]
    write_notebook(notebook, cells)

    assert embed(monkeypatch, tmp_path, notebook, "first", "second") == 1
    assert "code cell 3 names no step" in capsys.readouterr().out


def test_a_cell_naming_a_step_which_does_not_exist(monkeypatch, tmp_path, capsys) -> None:
    notebook = a_good_pair(tmp_path)
    cells = json.loads(notebook.read_text())["cells"] + [code_cell("third")]
    write_notebook(notebook, cells)

    assert embed(monkeypatch, tmp_path, notebook, "first", "second") == 1
    assert "names the step third, which does not exist" in capsys.readouterr().out


def test_two_cells_naming_one_step(monkeypatch, tmp_path, capsys) -> None:
    notebook = a_good_pair(tmp_path)
    cells = json.loads(notebook.read_text())["cells"] + [code_cell("second")]
    write_notebook(notebook, cells)

    assert embed(monkeypatch, tmp_path, notebook, "first", "second") == 1
    assert "as does another cell" in capsys.readouterr().out


def test_a_step_with_no_cell(monkeypatch, tmp_path, capsys) -> None:
    notebook = a_good_pair(tmp_path)
    write_notebook(notebook, [code_cell("first", "print('first')")])

    assert embed(monkeypatch, tmp_path, notebook, "first", "second") == 1
    assert "no code cell names this step" in capsys.readouterr().out


def test_the_cells_in_the_wrong_order(monkeypatch, tmp_path, capsys) -> None:
    notebook = a_good_pair(tmp_path)
    cells = json.loads(notebook.read_text())["cells"]
    write_notebook(notebook, list(reversed(cells)))

    # A notebook runs from the top, so cells out of the order the steps ran in would publish
    # outputs which were never produced that way.
    assert embed(monkeypatch, tmp_path, notebook, "first", "second") == 1
    assert "the steps run in the order" in capsys.readouterr().out


def test_a_later_step_importing(monkeypatch, tmp_path, capsys) -> None:
    # A notebook runs from the top, so the first cell is where what everything uses comes from.
    a_good_pair(tmp_path)
    notebook = tmp_path / "notebook.ipynb"
    write_step(tmp_path / "steps", "second", "import numpy\nprint('second')")

    assert embed(monkeypatch, tmp_path, notebook, "first", "second") == 1
    assert "imports numpy, which the first cell is where to do" in capsys.readouterr().out


def test_the_first_step_may_import(monkeypatch, tmp_path, capsys) -> None:
    a_good_pair(tmp_path)
    notebook = tmp_path / "notebook.ipynb"
    write_step(tmp_path / "steps", "first", "import numpy\nprint('first')")

    assert embed(monkeypatch, tmp_path, notebook, "first", "second") == 0
    assert "EMBEDDED first" in capsys.readouterr().out


def test_a_step_which_is_not_python(monkeypatch, tmp_path, capsys) -> None:
    a_good_pair(tmp_path)
    notebook = tmp_path / "notebook.ipynb"
    write_step(tmp_path / "steps", "second", "this is not python(")

    assert embed(monkeypatch, tmp_path, notebook, "first", "second") == 1
    assert "is not valid Python" in capsys.readouterr().out


def test_a_step_with_no_file(monkeypatch, tmp_path, capsys) -> None:
    notebook = a_good_pair(tmp_path)

    assert embed(monkeypatch, tmp_path, notebook, "first", "second", "third") == 1
    assert "there is no such file" in capsys.readouterr().out
