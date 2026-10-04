# The context the notebook has by this point: the packages, and the metacells we started from with everything the
# analysis said about them.
import dafpy as dp
import metacellspy as mc

metacells = dp.complete_daf("dafs/metacells.I0.R0", "r+", name="metacells.I0.R0")

# --- the notebook cell starts here ---
# How good are these metacells? Grouping cells says which of them belong together; whether that was right is a question
# about the cells, and it is answered by asking how well each cell is described by the metacell it was put in -
# correlating the two over the genes, with the cell's own UMIs taken out of its metacell so that it is not compared
# against itself.
#
# The question is asked separately in each location of the manifold, and both the locations and the genes to ask about
# come from a base repository: the blocks its metacells fell into, the cells of each block's neighborhood, and the
# genes which tell that block's environment apart. Fixing all of that in the base is what makes the answers mean
# anything - any metacells scored against the same base were asked the same question, so their answers can be put side
# by side.
#
# The base is these metacells, before any sharpening. They lay out the manifold every score is read in: this one, each
# sharpened round's, and each later iteration's. That is what makes all of the scores one series. The base is only ever
# read, so it is given as a read-only view.
base_manifold = metacells.read_only()

# This is the one call here which writes into a repository that already exists, so it says `overwrite`. Scoring
# metacells does not change them, and asking again is always allowed.
#
# The call reports the score. It is the mean over the base blocks which had any gene to score.
mc.qc_metacells(daf=metacells, score_daf=base_manifold, overwrite=True)
