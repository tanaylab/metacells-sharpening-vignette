# The context the notebook has by this point: the packages, and the cells that were imported and cleaned.
import dafpy as dp
import metacellspy as mc

cells = dp.files_daf("dafs/cells", "r+", name="cells")

# --- the notebook cell starts here ---
# The types, and the color of each, which is what makes the graphs readable. The file decides which
# types there are and in what order they are listed - usually a meaningful order rather than an
# alphabetical one. It may name a type no cell has; a type of some cell which it does not name is an
# error, in the file or in the data. Skip this and everything still runs, uncolored.
mc.import_type_colors_csv(cells, type_colors_csv="input/type_colors.csv")

# `AnnData` has two axes, so everything else it knows is flattened onto the cells: which batch a cell
# came from, and with it every fact about that batch, repeated across its cells. Reconstructing an
# axis puts each fact where it belongs - one value per batch rather than 110,746 copies of it - and
# says so in the structure rather than in a naming convention.
#
# What is per batch, and what is merely constant within a batch by accident, is decided by looking:
# a property whose value differs between two cells of a batch is left alone. That is convenient and
# slightly dangerous, since a property which happens to be uniform is moved as readily as one which
# is uniform for a reason. These are the pipeline's own, which belong to the cells whatever their
# values happen to look like here - `is_excluded` is false for every cell of this data set, which
# says nothing about where it belongs.
KEEP_PER_CELL = {"is_excluded", "is_properly_sampled", "is_rare", "rare_gene_module", "spike_count"}

for axis in ("batch", "embryo"):
    dp.reconstruct_axis(cells, existing_axis="cell", implicit_axis=axis, skipped_properties=KEEP_PER_CELL)

# A batch was on a plate and was sequenced in a run, so those are properties of the batch now, and
# each is an axis of its own with the batch's facts divided again between them. The wet lab's record
# lands where it is read: the plate's owner and dates on the plate, the batch's concentration and QC
# on the batch, the sequencing dates on the run.
#
# The coarser axis goes first. Each plate was sequenced in one run, so a fact about a run is also
# constant within each of its plates, and reconstructing the plate first would take the run's dates
# with it - leaving the run with nothing. The reverse cannot happen: a run holds many plates, so a
# plate's own owner and dates are not constant within it.
for axis in ("sequencing_run", "plate"):
    dp.reconstruct_axis(cells, existing_axis="batch", implicit_axis=axis, skipped_properties=KEEP_PER_CELL)

# Each plate belongs to one sequencing run, but nothing has said so where a plate can be asked. It
# cannot be reconstructed: the cells sequenced by 10x have a run and no plate at all, so moving the
# run onto the plate would discard theirs. Connecting says it while leaving the batch's own run
# alone, and fails if any plate's batches disagree about which run they were in.
dp.connect_axes(cells, base_axis="batch", from_axis="plate", to_axis="sequencing_run")

print(cells.description())
