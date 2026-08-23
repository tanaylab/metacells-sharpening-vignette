"""Execute the notebooks whose code changed since they were last executed.

Executing a notebook runs the whole sharpening pipeline, which is expensive and needs the input
data, while editing the prose around that pipeline costs nothing and changes none of its outputs.
Each notebook therefore records the fingerprint of the code cells it was last executed with, and
this compares that against what its code cells hold now. Only a difference re-executes it, so
rewording a paragraph regenerates the documents without recomputing anything.

Executing is done in place, so the outputs are replaced while the prose around them stays as it is
now rather than as it was when the pipeline last ran.

With `--check` nothing is executed and nothing is written: it only reports the notebooks whose
outputs no longer describe their code, which is what the CI server can ask, having neither the
input data nor a way to run the pipeline.
"""

import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

#: Where the fingerprint of the code a notebook was last executed with is kept. It is stored in the
#: notebook rather than beside it so that a fresh clone knows whether the committed outputs are
#: current, which a file in an ignored build directory could not say.
METADATA_KEY = "metacells_sharpening_vignette"

FINGERPRINT_KEY = "code_fingerprint"

#: What separates one code cell from the next when they are fingerprinted, so that moving a line
#: from the end of one cell to the start of the next changes the fingerprint.
CELL_SEPARATOR = "\0"


def code_fingerprint(notebook: Dict[str, Any]) -> str:
    """Compute the fingerprint of a notebook's code, which is its code cells and nothing else."""
    sources = [source_of(cell) for cell in notebook["cells"] if cell["cell_type"] == "code"]
    return sha256(CELL_SEPARATOR.join(sources).encode()).hexdigest()


def source_of(cell: Dict[str, Any]) -> str:
    """Return the source of a cell, which the format allows to be either one string or a list."""
    source = cell["source"]
    return source if isinstance(source, str) else "".join(source)


def executed_fingerprint(notebook: Dict[str, Any]) -> Optional[str]:
    """Return the fingerprint of the code a notebook was last executed with, if it ever was."""
    return notebook["metadata"].get(METADATA_KEY, {}).get(FINGERPRINT_KEY)


def read(path: Path) -> Dict[str, Any]:
    """Read a notebook as the JSON it is, so that checking one needs nothing installed."""
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def execute(path: Path) -> None:
    """Execute one notebook in place, and record the code it was executed with."""
    subprocess.run(
        ["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", str(path)],
        check=True,
    )

    # Written through `nbformat` rather than through `json`, so that the file keeps the exact
    # formatting every other tool writes it with and the change is the recorded fingerprint alone.
    # Importing it here rather than at the top keeps checking a notebook free of it: this is the
    # one path which writes, and it runs where the notebook was just executed, so it is installed.
    import nbformat  # pylint: disable=import-outside-toplevel

    # Read again rather than reusing what was read before, because executing rewrote the file.
    notebook = nbformat.read(path, as_version=4)
    notebook.metadata.setdefault(METADATA_KEY, {})[FINGERPRINT_KEY] = code_fingerprint(notebook)
    nbformat.write(notebook, path)


def main() -> int:
    """Execute, or report, every notebook whose code changed since it was last executed."""
    arguments = sys.argv[1:]
    is_check = "--check" in arguments
    paths = [Path(argument) for argument in arguments if argument != "--check"]

    if not paths:
        print("::error::there are no notebooks to execute")
        return 1

    stale: List[Path] = []
    for path in paths:
        notebook = read(path)
        if code_fingerprint(notebook) == executed_fingerprint(notebook):
            print(f"UP TO DATE {path}: its outputs are of the code it holds now")
            continue

        if is_check:
            stale.append(path)
        else:
            print(f"EXECUTING {path}: its code changed since it was last executed")
            execute(path)

    for path in stale:
        print(f"::error file={path}::its code changed since it was last executed; run `make run`")
        print(f"FAILED {path}: its outputs do not describe the code it holds")

    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
