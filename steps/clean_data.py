# The context the notebook has by this point: the packages, and the cells that were imported.
import dafpy as dp
import numpy as np  # Which the notebook has from the first cell, and a script has to import for itself.

cells = dp.files_daf("dafs/cells", "r+", name="cells")

# --- the notebook cell starts here ---
# How this data spells "there is no value here", which is not one way but several, sometimes several
# in the same property: `embryo` says both `NA` and nothing at all. Nothing infers these - a type
# genuinely called `NA` is possible - so each is named, and a property named here whose data happens
# to be clean is simply left alone.
#
# This has to happen before any axis is built, since building one asks of each cell whether it has a
# value: a property still saying `NA` would put `NA` on the axis, sitting among the real entries.
EMPTY_VALUES = {
    "embryo": ("NA",),
    "metacell": ("Outliers",),
    "type": ("Outliers", "Doublet"),
    "projected_type": ("(Missing)",),
    "cell": ("NA",),
    "coordinates": ("NA",),
    "source": ("NA",),
}

for property_name, empty_values in EMPTY_VALUES.items():
    dp.unify_empty_vector_values(cells, axis="cell", property=property_name, empty_values=empty_values)

# Numbers which arrived as text, because a few of their entries say `NA` and one `NA` makes a whole
# column of measurements a column of strings. Converting and unifying is one step, not two: what
# `23.5` should become is obvious, and what `NA` should become is only obvious once we are told that
# it means nothing. A number which is neither is an error rather than a silent `NaN`.
AS_NUMBERS = {
    "qc1": ("NA", np.float32),
    "qc2": ("NA", np.float32),
    "delta_ct": ("NA", np.float32),
    "concentration_ng_per_ul": ("NA", np.float32),
    # 1..32, so `0` is free to mean "none" - the convention `Daf` already uses for module indices.
    # The cells with no plate are the ones sequenced by 10x, which has no plates.
    "internal_index": ("", np.uint32),
}

for property_name, (empty_values, dtype) in AS_NUMBERS.items():
    dp.unify_empty_vector_values(
        cells, axis="cell", property=property_name, empty_values=empty_values, dtype=dtype
    )

# A sentinel which is not obviously one: the smallest 32 bit integer, which survived a cast to float
# and so is an ordinary number as far as anything reading it is concerned. Left alone, the mean of
# this property is wrong by a couple of billion rather than visibly absent.
dp.unify_empty_vector_values(
    cells, axis="cell", property="transcriptional_rank", empty_values=np.float64(-2147483648.0)
)
