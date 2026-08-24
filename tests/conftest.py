"""Make the scripts importable, so they can be tested as code rather than run as commands."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
