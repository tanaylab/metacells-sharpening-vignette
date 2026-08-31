# The context the notebook has by this point: the packages, and the cells.
import numpy as np

import dafpy as dp
import metacellspy as mc

cells = dp.files_daf("dafs/cells", "r", name="cells")

# --- the notebook cell starts here ---
# Which genes are what, which is the one thing an iteration of this analysis is free to disagree about. Everything
# computed from here on depends on these four masks, and on nothing else which varies, so a repository of them is what
# an iteration *is*: change them, and every result below changes with them.
masks = dp.complete_chain(
    base_daf=cells,
    new_daf=dp.files_daf("dafs/masks.I0", "w", name="masks.I0"),
    name="masks.I0",
)

n_genes = masks.axis_length("gene")

# Genes which may not be used to predict the others, whatever the data says about them. There is no such list to start
# with: this first iteration takes the data as it comes, so that the second has something to be better than.
masks.set_vector("gene", "is_forbidden", np.zeros(n_genes, dtype=bool))

# `is_lateral` - the genes which are not to drive the metacells - is left exactly as the `h5ad` carried it, for the
# same reason. Patching it is the other half of what a later iteration does.

# Which genes regulate others, and which are transcription factors, fetched from Gmara rather than decided here. These
# describe the species and not this experiment, so they do not vary between iterations; they live here only because
# `is_regulator` is one of the four masks, and keeping the set together is what makes an iteration one thing.
mc.fetch_gmara_vector_of_is_regulator_per_gene(masks, species="mouse")
mc.fetch_gmara_vector_of_is_transcription_factor_per_gene(masks, species="mouse")

print(masks.description())
