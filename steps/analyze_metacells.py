# The context the notebook has by this point: the packages, the base metacells, and this iteration's gene masks.
import dafpy as dp
import metacellspy as mc

base_metacells = dp.complete_daf("dafs/metacells.base", name="metacells.base")
masks = dp.complete_daf("dafs/masks.I0", name="masks.I0")

# --- the notebook cell starts here ---
# The first round of the first iteration. It rests on two repositories: the metacells the cells were aggregated into,
# which every iteration shares, and this iteration's gene masks. Both rest in turn on the same cells, so the cells are
# reached through either arm and are used once.
#
# The name says which iteration and which round: `I0` is this set of masks and `R0` is the metacells before any
# sharpening. Each round of sharpening writes an `R1`, an `R2` and so on beside this one, and each iteration starts
# again at its own `R0`.
metacells = dp.complete_chain(
    base_daf=[base_metacells, masks],
    new_daf=dp.files_daf("dafs/metacells.I0.R0", "w", name="metacells.I0.R0"),
    name="metacells.I0.R0",
)

# Everything these metacells say about the manifold: which genes are skeleton, how far the metacells are from each
# other and how they lay out, the blocks they fall into with their neighborhoods and environments, and the gene modules
# of each block. This is what sharpening reads, so it is also what has to be recomputed after each round of it.
#
# `module_status` records why each gene ended up in the module it did, which is worth having while reading a result.
mc.analyze_metacells(metacells, module_status=True)

print(metacells.description())
