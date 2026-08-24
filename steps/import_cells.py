# The context the notebook has by this point: the packages the first cell imported.
import dafpy as dp
import metacellspy as mc

# --- the notebook cell starts here ---
# What to take out of the `AnnData`, and under what name. Anything not named here is copied as it
# is, after the importer's own renaming: a `something_cell` or `something_gene` mask arrives as
# `is_something`, and a `something_umis` as `something_UMIs`. Naming a property here overrides that
# for it alone, so the rest of the import is unaffected.
COPY_DATA = {
    # Which metacell each cell belongs to. This is what the pipeline sharpens rather than computes,
    # and it is the one property the importer skips by default, since it usually comes from a
    # separate metacells file. Here the cells are the only place it exists, so we ask for it.
    "metacell_name": ("metacell", None),
    # The type of each cell. **Specify this whenever the data has a type per cell**: the type axis
    # is built from a vector called `type`, and the column holding it is rarely called that. Leave
    # it out and everything still runs, with no types and uncolored graphs.
    "cell_type": ("type", None),
    # This dataset has a column of its own called `type` - the platform each cell was measured on,
    # which is not a cell type at all. Left alone it would collide with the line above, so it is
    # given the name it deserves.
    "type": ("platform", None),
}

cells = dp.files_daf("dafs/cells", "w", name="cells")

mc.import_cells_h5ad(
    cells,
    cells_h5ad="input/assigned_cells.h5ad",
    copy_data=COPY_DATA,
    # The types, and the color of each, which is what makes the graphs readable. The file decides
    # which types there are and in which order they are listed; it may name types no cell has, but a
    # type of some cell which it does not name is an error in one or the other of them. Leave this
    # out, and everything still runs with no types at all.
    type_colors_csv="input/type_colors.csv",
    # What this data spells "this cell has no type" as. Which values those are is a property of the
    # data set rather than something to guess at, and they are the only values exempt from having to
    # appear in the file above. Give one of them, or several.
    empty_type="Outliers",
)

print(cells.description())
