# The context the notebook has by this point: the packages, and the first iteration's gene masks.
import numpy as np

import dafpy as dp

masks = dp.complete_daf("dafs/masks.I0", name="masks.I0")

# --- the notebook cell starts here ---
# The second iteration is the same analysis with the gene masks corrected by hand. Reading the first iteration's
# results is what suggests the corrections. The ones here are those of the pipeline this vignette is drawn from.
#
# The corrections go into a repository of their own, resting on the first iteration's masks. It holds only the two
# masks which change. The other two are read through it, and the first iteration's masks stay as they were.
masks = dp.complete_chain(
    base_daf=masks,
    new_daf=dp.files_daf("dafs/masks.I1", "w", name="masks.I1"),
    name="masks.I1",
)

# Genes which may not be used to predict the others.
FORBIDDEN_GENES = ("Tead2", "Mitf", "Trerf1", "Elof1", "Gtf3a", "Hmga1", "Foxn2", "Atf6", "Atf6b", "Nfe2l2")

# Genes the `h5ad` marked as lateral, which may drive the metacells after all.
NOT_LATERAL_GENES = ("Id2", "Id3", "Pou5f1", "Tdgf1")

# Genes the `h5ad` did not mark as lateral, which may not drive the metacells.
MORE_LATERAL_GENES = ("Fosl2", "Cebpz", "Mt1", "Mt2")

# Both masks already exist below this repository, so setting them says `overwrite`. The new values go into this
# repository alone, and hide the old ones only when read through it.
is_forbidden_per_gene = np.zeros(masks.axis_length("gene"), dtype=bool)
is_forbidden_per_gene[masks.axis_np_indices("gene", FORBIDDEN_GENES)] = True
masks.set_vector("gene", "is_forbidden", is_forbidden_per_gene, overwrite=True)

is_lateral_per_gene = masks.get_np_vector("gene", "is_lateral").copy()
is_lateral_per_gene[masks.axis_np_indices("gene", NOT_LATERAL_GENES)] = False
is_lateral_per_gene[masks.axis_np_indices("gene", MORE_LATERAL_GENES)] = True
masks.set_vector("gene", "is_lateral", is_lateral_per_gene, overwrite=True)

print(masks.description())

masks = masks.read_only()
