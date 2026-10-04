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

# One line per message, rather than Julia's default of a box with the source location under it.
# Each message says when it was emitted and on which thread, which is worth having while it runs.
dp.setup_logger()

# The seed every computation which makes random choices is given. Clustering metacells is one of
# them, so without a seed two runs of this notebook place cells in different metacells and every
# number below them differs a little. Any non-zero value will do; what matters is that it is fixed
# and that it is passed, since zero means "use Julia's own generator" - which is to say, do not
# reproduce.
RNG_SEED = 123456

# The global generators are seeded with it as well. Everything below passes `RNG_SEED` explicitly,
# which is what makes the results reproducible; this is only so that anything which draws without
# being given a generator still starts from a known place instead of from the clock.
np.random.seed(RNG_SEED)
mc.jl.seval("using Random")
mc.jl.Random.seed_b(RNG_SEED)

print("dafpy", dp.__version__)
print("somegraphspy", sg.__version__)
print("metacellspy", mc.__version__)

# Read from Julia at import, so printing it means Python reached Julia rather than merely that the
# Python packages are installed.
print("regularization", mc.GENE_FRACTION_REGULARIZATION_FOR_CELLS)
