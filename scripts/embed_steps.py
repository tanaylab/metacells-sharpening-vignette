"""Put the code developed in ``steps`` into the notebook's code cells.

Each script in ``steps`` is one code cell, and holds two parts: the context the notebook would have
in memory by that point, and - below the marker - what the cell actually is. Only that lower half is
published. The steps are what the code *is*; the notebook holds the prose around them, and says
where each step goes.

Which cell holds which step is recorded in the cell's own metadata rather than left to the order of
the cells, so that inserting a paragraph, or reordering the prose, cannot silently put a step's code
into the slot of another. A code cell with no step, a step named twice, a step with no cell and a
cell naming a step which no longer exists are all reported rather than guessed at.

The steps are named on the command line, in the order they run, since that order is `steps/Makefile`
to define rather than something to infer from what files happen to be in the directory. It matters,
a notebook being run from the top: the steps ran in one order, and the notebook must hold them in
that same order, or what is published is not what was verified.

With ``--check`` nothing is written: it only reports whether the notebook already holds what the
steps say, which is what the CI server can ask without running anything.
"""

import ast
import json
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

#: What separates a step's context from the cell itself. Everything below it is the cell.
CELL_MARKER = "# --- the notebook cell starts here ---"

#: Where a cell records which step it holds. The same key the notebook uses for the fingerprint of
#: the code it was last executed with, so there is one name to know rather than two.
METADATA_KEY = "metacells_sharpening_vignette"

STEP_KEY = "step"

STEPS = Path("steps")


def cell_of_step(path: Path) -> str:
    """Return the part of a step which becomes a notebook cell."""
    text = path.read_text()
    _, marker, cell = text.partition(CELL_MARKER + "\n")
    if marker == "":
        raise ValueError(f"{path}: has no {CELL_MARKER!r} line")
    return cell.strip("\n")


def imports_of(cell: str) -> List[str]:
    """Return what a cell imports, which only the first one may do."""
    imported = []
    for node in ast.walk(ast.parse(cell)):
        if isinstance(node, ast.Import):
            imported += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "...")
    return imported


def step_of_cell(cell: Dict[str, Any]) -> str:
    """Return the name of the step a cell holds, or an empty string if it names none."""
    return cell["metadata"].get(METADATA_KEY, {}).get(STEP_KEY, "")


def source_of_cell(cell: Dict[str, Any]) -> str:
    """Return the source of a cell, which the format allows to be either one string or a list."""
    source = cell["source"]
    return source if isinstance(source, str) else "".join(source)


def problems_of(step_names: List[str], cell_step_names: List[str]) -> List[Tuple[str, str]]:
    """Report every way the notebook's code cells and the steps fail to be the same, in order.

    Each problem is the file it is about, which may be nothing when it is about the notebook as a
    whole, and what is wrong.
    """
    problems: List[Tuple[str, str]] = []

    for index, cell_step_name in enumerate(cell_step_names):
        if cell_step_name == "":
            problems.append(("", f"code cell {index + 1} names no step in its metadata"))
        elif cell_step_name not in step_names:
            problems.append(("", f"code cell {index + 1} names the step {cell_step_name}, which does not exist"))
        elif cell_step_names.count(cell_step_name) > 1:
            problems.append(("", f"code cell {index + 1} names the step {cell_step_name}, as does another cell"))

    for step_name in step_names:
        if step_name not in cell_step_names:
            problems.append((f"{STEPS}/{step_name}.py", "no code cell names this step"))

    named = [cell_step_name for cell_step_name in cell_step_names if cell_step_name in step_names]
    ordered = [step_name for step_name in step_names if step_name in named]
    if not problems and named != ordered:
        problems.append(("", f"the code cells are in the order {named}, and the steps run in the order {ordered}"))

    return problems


def main() -> int:
    """Copy each step's cell into the cell which names it, or report that the two do not agree."""
    arguments = [argument for argument in sys.argv[1:] if argument != "--check"]
    is_check = "--check" in sys.argv[1:]

    if len(arguments) < 2:
        print("::error::name the notebook, and then the steps in the order they run")
        return 1

    notebook_path = Path(arguments[0])
    step_names = arguments[1:]
    step_paths: Dict[str, Path] = {step_name: STEPS / f"{step_name}.py" for step_name in step_names}

    missing = [str(path) for path in step_paths.values() if not path.exists()]
    for path in missing:
        print(f"::error file={path}::the `steps/Makefile` names this step, and there is no such file")
        print(f"FAILED {path}: named as a step, and there is no such file")
    if missing:
        return 1

    with open(notebook_path, encoding="utf-8") as file:
        notebook = json.load(file)

    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    cell_step_names = [step_of_cell(cell) for cell in code_cells]

    problems = problems_of(step_names, cell_step_names)

    # A notebook runs from the top, so the first cell is where what everything uses comes from. A later cell importing
    # for itself would work and would be wrong: the reader would meet the same import several times, and a step whose
    # context imports something it uses would go unnoticed until the notebook is run, rather than now.
    for step_name in step_names[1:]:
        path = step_paths[step_name]
        try:
            imported = imports_of(cell_of_step(path))
        except SyntaxError as exception:
            problems.append((str(path), f"is not valid Python: {exception}"))
            continue
        if imported:
            problems.append((str(path), f"imports {', '.join(imported)}, which the first cell is where to do"))

    if problems:
        for path, description in problems:
            print(f"::error file={path}::{description}" if path else f"::error::{description}")
            print(f"FAILED {path + ': ' if path else ''}{description}")
        return 1

    stale = []
    for cell, cell_step_name in zip(code_cells, cell_step_names):
        cell_source = cell_of_step(step_paths[cell_step_name])
        if source_of_cell(cell) != cell_source:
            stale.append(cell_step_name)
            cell["source"] = cell_source

    if not stale:
        print(f"UP TO DATE {notebook_path}: its code is what {STEPS} holds")
        return 0

    if is_check:
        for step_name in stale:
            print(f"::error file={STEPS}/{step_name}.py::its cell is not what the notebook holds; run `make embed`")
            print(f"FAILED {STEPS}/{step_name}.py: the notebook does not hold this step's cell")
        return 1

    # Written as the JSON it is, which is byte for byte what `nbformat` writes for the same content,
    # and needs nothing installed - only the source of some cells changed, so there is nothing here
    # for `nbformat` to normalise.
    with open(notebook_path, "w", encoding="utf-8") as file:
        json.dump(notebook, file, indent=1)
        file.write("\n")
    for step_name in stale:
        print(f"EMBEDDED {step_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
