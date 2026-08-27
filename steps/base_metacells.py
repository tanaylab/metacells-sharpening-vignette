# The context the notebook has by this point: the packages, and the cells with their axes.
import dafpy as dp
import metacellspy as mc

cells = dp.files_daf("dafs/cells", "r", name="cells")

# --- the notebook cell starts here ---
# The metacells we start from, in a repository of their own resting on the cells. Everything computed
# from here on lives in such a repository, and the cells are never written to again - which is what
# lets one set of cells carry several analyses of them without copying a single UMI.
base_metacells = dp.complete_chain(
    base_daf=cells,
    new_daf=dp.files_daf("dafs/metacells.base", "w", name="metacells.base"),
    name="metacells.base",
)

# Which metacell each cell belongs to is an input here rather than something computed: it came with
# the `h5ad`, and it stays in the cells, where every analysis of them reads it. Sharpening does not
# change it - each round writes a new assignment into a repository of its own, and each starts again
# from this one.
#
# The metacells themselves, named by the values of that property. `reconstruct_axis` would also move
# to the new axis every per-cell property which happens to be constant per metacell; here it is asked
# for the axis alone, since anything per metacell is about to be computed rather than inherited.
dp.reconstruct_axis(
    base_metacells, existing_axis="cell", implicit_axis="metacell", implicit_properties=set()
)

# What the cells say about their metacells: how many cells each has, their UMIs, and the fraction of
# each gene in each of them. Then the marker genes - the ones which distinguish between metacells.
#
# Neither depends on the gene masks, which is why they are here rather than in each analysis: this
# repository is shared by all of them.
mc.prepare_metacells(base_metacells)
mc.prepare_markers(base_metacells)

print(base_metacells.description())
