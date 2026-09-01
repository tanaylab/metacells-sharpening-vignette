# The context the notebook has by this point: the packages, the cells with their axes, and the
# metacell each of them belongs to, which the notebook still holds from the cell which imported them.
# A script cannot, so it reads that one column again, through the same Muon the importer used - the
# `jl` of `metacellspy`, since importing `juliacall` before it is what these packages configure.
import numpy as np

import dafpy as dp
import metacellspy as mc

cells = dp.files_daf("dafs/cells", "r+", name="cells")

mc.jl.seval("using Muon")
base_metacell_per_cell = np.array(
    mc.jl.seval('path -> Vector{String}(readh5ad(path).obs[!, "metacell_name"])')("input/assigned_cells.h5ad"),
    dtype=str,
)

# --- the notebook cell starts here ---
# The metacells we start from, in a repository of their own resting on the cells. Everything computed
# from here on lives in such a repository, so that one set of cells can carry several analyses of
# them without copying a single UMI.
base_metacells = dp.complete_chain(
    base_daf=cells,
    new_daf=dp.files_daf("dafs/metacells.base", "w", name="metacells.base"),
    name="metacells.base",
)

# Which metacell each cell belongs to, which came with the `h5ad` rather than being computed. It
# goes into this repository rather than into the cells: it is one analysis of them, not a fact about
# them, and every sharpening round writes an assignment of its own.
#
# What does go into the cells is which of them this assignment left out, since that is the one thing
# about it the later rounds still need and cannot work out for themselves: a cell a round ejects also
# has no metacell, and the round after it may place that cell, but a cell the metacells we start from
# never placed stays out for good.
#
# `Outliers` is how this data spells "no metacell", the same way `clean_data` was told how it spells
# the rest of them. Left unsaid, `Outliers` would become a metacell of its own on the axis below.
mc.import_base_metacells(
    cells_daf=cells,
    metacells_daf=base_metacells,
    metacell_per_cell=base_metacell_per_cell,
    empty_metacells=("Outliers",),
    overwrite=True,
)

# The metacells themselves, named by the values of that property. `reconstruct_axis` would also move
# to the new axis every per-cell property which happens to be constant per metacell; here it is asked
# for the axis alone, since anything per metacell is about to be computed rather than inherited.
dp.reconstruct_axis(
    base_metacells, existing_axis="cell", implicit_axis="metacell", implicit_properties=set()
)

# What the cells say about their metacells: how many cells each has, their UMIs, the fraction of each
# gene in each of them, and the marker genes - the ones which distinguish between metacells.
#
# None of it depends on the gene masks, which is why it is here rather than in each analysis: this
# repository is shared by all of them.
mc.prepare_metacells(base_metacells)

print(base_metacells.description())
