# The first cell has no context to establish: it is the first thing the notebook does.

# --- the notebook cell starts here ---
import numpy as np

import dafpy as dp
import metacellspy as mc
import somegraphspy as sg

print("dafpy", dp.__version__)
print("somegraphspy", sg.__version__)
print("metacellspy", mc.__version__)

# Read from Julia at import, so printing it means Python reached Julia rather than merely that the
# Python packages are installed.
print("regularization", mc.GENE_FRACTION_REGULARIZATION_FOR_CELLS)
