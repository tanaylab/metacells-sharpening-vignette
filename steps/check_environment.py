# The first cell has no context to establish: it is the first thing the notebook does.

# --- the notebook cell starts here ---
import os

import numpy as np

import dafpy as dp
import metacellspy as mc
import somegraphspy as sg

# What the packages say while they work. `mcs_results` is the summary of each computation - the mean
# cells in a metacell, the number of blocks - which is worth reading and is a line or two apiece.
# The other groups narrate every call and every loop, which is for working on the packages rather
# than for using them.
#
# Set here rather than left to the environment, so that this notebook says the same thing wherever
# it runs, and so that reading it shows what running it shows.
os.environ["JULIA_DEBUG"] = "mcs_results"

print("dafpy", dp.__version__)
print("somegraphspy", sg.__version__)
print("metacellspy", mc.__version__)

# Read from Julia at import, so printing it means Python reached Julia rather than merely that the
# Python packages are installed.
print("regularization", mc.GENE_FRACTION_REGULARIZATION_FOR_CELLS)
