# The context the notebook has by this point: the packages the first cell imported.
import dafpy as dp
import metacellspy as mc

# --- the notebook cell starts here ---
# What to take out of the `AnnData`, and under what name. Anything not named here is copied as it is,
# after the importer's own renaming: a `something_cell` or `something_gene` mask arrives as
# `is_something`, and a `something_umis` as `something_UMIs`. Naming a property here overrides that
# for it alone, so the rest of the import is unaffected.
COPY_DATA = {
    # Which metacell each cell belongs to. This is what the pipeline sharpens rather than computes,
    # and it is the one property the importer skips by default, since it usually comes from a
    # separate metacells file. Here the cells are the only place it exists, so we ask for it.
    "metacell_name": ("metacell", None),
    # The type of each cell. **Specify this whenever the data has a type per cell**: the type axis is
    # built from a vector called `type`, and the column holding it is rarely called that. Leave it
    # out and everything still runs, with no types and uncolored graphs.
    "cell_type": ("type", None),
    # This dataset has a column of its own called `type` - the platform each cell was measured on,
    # which is not a cell type at all. Left alone it would collide with the line above.
    "type": ("platform", None),
    #
    # The batch, the plate it was on, and the run it was sequenced in. These become axes of their
    # own further down, so they are given the names those axes will have. Three other columns hold
    # the same batch identifier - `batch_set_id` is identical to it, `plate` is it with 1212 cells
    # saying the literal string `NA`, and `Plate` is it with the 10x cells left blank - so they are
    # dropped rather than imported and then explained.
    "amp_batch_id": ("batch", None),
    "batch_set_id": None,
    "Plate": None,
    "plate": None,
    "Plate..": ("plate", None),
    "seq_batch_id": ("sequencing_run", None),
    #
    # The wet lab's record of each batch, plate and run. These are spelled as they were typed into a
    # spreadsheet, dots, capitals, typos and all, and are about to become properties of those axes
    # where they will be read rather than merely stored.
    "Comment": ("comment", None),
    "Conc...ng.ul.": ("concentration_ng_per_ul", None),
    "Evarage.size..bp.": ("average_size_bp", None),
    "External.Index": ("external_index", None),
    "Internal.Index": ("internal_index", None),
    "QC1": ("qc1", None),
    "QC2": ("qc2", None),
    "delta_CT": ("delta_ct", None),
    "Libprep.Cycles": ("libprep_cycles", None),
    "Owner": ("owner", None),
    "Plate.Date": ("plate_date", None),
    "Production.Date": ("production_date", None),
    "Sort.Date": ("sort_date", None),
    "Last.sequensing.date": ("last_sequencing_date", None),
    "Sequencing.Dates": ("sequencing_dates", None),
    "Experiment": ("experiment", None),
    # Not a genotype: the values are free text describing the sample the batch was made from - the
    # strain, the stage, which embryos, whether it is placenta - and only some of them are strains.
    # It is constant per batch and per plate, and *not* per embryo, which is the giveaway.
    "Genotype": ("description", None),
    #
    # Columns which hold one value, or none at all: `Ref` is `mm10` for every cell that has it,
    # `Empty.Wells` is one list of wells repeated, `X.1` is the string `NA` for all 110,746 cells,
    # `X` is blank for most of them, and `not_na` is true throughout. None of them distinguishes
    # anything, so none of them is worth carrying.
    "Ref": None,
    "Empty.Wells": None,
    "X": None,
    "X.1": None,
    "not_na": None,
}

cells = dp.files_daf("dafs/cells", "w", name="cells")

mc.import_cells_h5ad(cells, cells_h5ad="input/assigned_cells.h5ad", copy_data=COPY_DATA)

print(cells.description())
