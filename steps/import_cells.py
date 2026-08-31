# The context the notebook has by this point: the packages the first cell imported.
import dafpy as dp
import metacellspy as mc

# --- the notebook cell starts here ---
# What to take out of the `AnnData`, and under what name. Anything not named here is copied as it is,
# after the importer's own renaming: a `something_cell` or `something_gene` mask arrives as
# `is_something`, and a `something_umis` as `something_UMIs`. Naming a property here overrides that
# for it alone, so the rest of the import is unaffected.
COPY_DATA = {
    # The type of each cell. **Specify this whenever the data has a type per cell**: the type axis is
    # built from a vector called `type`, and the column holding it is rarely called that. Leave it
    # out and everything still runs, with no types and uncolored graphs.
    ("cell", "cell_type"): ("type", None),
    # This dataset has a column of its own called `type` - the platform each cell was measured on,
    # which is not a cell type at all. Left alone it would collide with the line above.
    ("cell", "type"): ("platform", None),
    #
    # The batch, the plate it was on, and the run it was sequenced in. These become axes of their
    # own further down, so they are given the names those axes will have. Three other columns hold
    # the same batch identifier - `batch_set_id` is identical to it, `plate` is it with 1212 cells
    # saying the literal string `NA`, and `Plate` is it with the 10x cells left blank - so they are
    # dropped rather than imported and then explained.
    ("cell", "amp_batch_id"): ("batch", None),
    ("cell", "batch_set_id"): None,
    ("cell", "Plate"): None,
    ("cell", "plate"): None,
    ("cell", "Plate.."): ("plate", None),
    ("cell", "seq_batch_id"): ("sequencing_run", None),
    #
    # The wet lab's record of each batch, plate and run. These are spelled as they were typed into a
    # spreadsheet, dots, capitals, typos and all, and are about to become properties of those axes
    # where they will be read rather than merely stored.
    ("cell", "Comment"): ("comment", None),
    ("cell", "Conc...ng.ul."): ("concentration_ng_per_ul", None),
    ("cell", "Evarage.size..bp."): ("average_size_bp", None),
    ("cell", "External.Index"): ("external_index", None),
    ("cell", "Internal.Index"): ("internal_index", None),
    ("cell", "QC1"): ("qc1", None),
    ("cell", "QC2"): ("qc2", None),
    ("cell", "delta_CT"): ("delta_ct", None),
    ("cell", "Libprep.Cycles"): ("libprep_cycles", None),
    ("cell", "Owner"): ("owner", None),
    ("cell", "Plate.Date"): ("plate_date", None),
    ("cell", "Production.Date"): ("production_date", None),
    ("cell", "Sort.Date"): ("sort_date", None),
    ("cell", "Last.sequensing.date"): ("last_sequencing_date", None),
    ("cell", "Sequencing.Dates"): ("sequencing_dates", None),
    ("cell", "Experiment"): ("experiment", None),
    # Not a genotype: the values are free text describing the sample the batch was made from - the
    # strain, the stage, which embryos, whether it is placenta - and only some of them are strains.
    # It is constant per batch and per plate, and *not* per embryo, which is the giveaway.
    ("cell", "Genotype"): ("description", None),
    #
    # Columns which hold one value, or none at all: `Ref` is `mm10` for every cell that has it,
    # `Empty.Wells` is one list of wells repeated, `X.1` is the string `NA` for all 110,746 cells,
    # `X` is blank for most of them, and `not_na` is true throughout. None of them distinguishes
    # anything, so none of them is worth carrying. Nor does `cell`, which repeats the cell's own name
    # for 64,675 of them and says `NA` for the other 46,071.
    #
    # `X` is why a key names the axis and not just the property: the UMIs matrix is called `X` as
    # well, and naming that one would be `("cell", "gene", "X")`.
    ("cell", "cell"): None,
    ("cell", "Ref"): None,
    ("cell", "Empty.Wells"): None,
    ("cell", "X"): None,
    ("cell", "X.1"): None,
    ("cell", "not_na"): None,
}

cells = dp.files_daf("dafs/cells", "w", name="cells")

# Which metacell each cell belongs to is not imported - it is one analysis of these cells rather than a fact about
# them, and every sharpening round produces another - but the importer has the file open, so it hands it back rather
# than making the next cell read it again. That cell is where it goes, into the repository of the round it answers.
base_metacell_per_cell = mc.import_cells_h5ad(cells, cells_h5ad="input/assigned_cells.h5ad", copy_data=COPY_DATA)

# The total UMIs of a cell look like data and are not: they are the sum of the UMIs already imported. An `h5ad` which
# happens to carry them is imported with them and is left alone; this one does not, so they are computed here, once,
# rather than by whichever computation needs them first.
if not cells.has_vector("cell", "total_UMIs"):
    mc.compute_vector_of_total_UMIs_per_cell(cells)

print(cells.description())
