# Develop the notebook's code as one script per code cell.
#
# A notebook is a poor place to develop in: every run starts from the top, and the pipeline is far
# too expensive for that. Each code cell is therefore a script here, and `make` runs only the steps
# whose script changed, or which follow one that did.
#
# Each script has two parts, separated by the marker line below. Above it is the context the
# notebook would have in memory by that point - the imports, and the repositories earlier steps
# wrote. Below it is what actually becomes the notebook cell. Nothing but that lower half is
# published, which is why the context may be as repetitive as it likes.
#
# The state a step leaves behind is on disk, in `dafs`, since a script cannot leave anything in
# memory for the next one. That is not a workaround: it is what makes any step re-runnable on its
# own, and it is how the pipeline scripts this vignette is drawn from already work.
#
#     make list          say which steps there are, in order
#     make               run whatever is out of date, up to the last step
#     make 020_metacells run up to that step, and no further
#     make clean         forget that anything ran

ROOT := $(abspath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))..)

# The steps, in the order they run, which is also the order the notebook must hold them in. This
# list is the whole definition of what the notebook's code is: a step not named here does not run
# and is not published, whatever files happen to be in this directory.
STEP_NAMES = \
    check_environment \
    import_cells \
    clean_data \
    reconstruct_axes \
    base_metacells

STAMP_FILES = $(patsubst %, .stamp/%, $(STEP_NAMES))

# How to enter the vignette's environment, as in the top level `Makefile`. Set it to nothing when
# the environment this `make` was started from already is the vignette's:
#     make EXECUTE_IN=
EXECUTE_IN = conda run --no-capture-output --name metacells-sharpening

# The notebook these steps are the code of.
NOTEBOOK = sharpening.ipynb

# Which Python runs the scripts which put the code into the notebook and check that it is there.
# The top level `Makefile` passes the one of the document tool chain; on its own, whatever is in
# the path will do, since neither script needs anything beyond the standard library.
PYTHON = python3

.DEFAULT_GOAL := all

# Each step depends on the step before it, so editing an early one re-runs everything after it. The
# rules are generated because that dependency is on the *previous* step, which a pattern rule cannot
# express.
PREVIOUS_STAMP =

define STEP_RULE
.stamp/$(1): $(ROOT)/steps/$(1).py $(PREVIOUS_STAMP)
	@mkdir -p .stamp
	cd $(ROOT) && $$(EXECUTE_IN) python3 steps/$(1).py
	@touch $$@

.PHONY: $(1)
$(1): .stamp/$(1)

PREVIOUS_STAMP := .stamp/$(1)
endef

$(foreach STEP_NAME, $(STEP_NAMES), $(eval $(call STEP_RULE,$(STEP_NAME))))

.PHONY: all
all: $(lastword $(STAMP_FILES))  ## run every step which is out of date

.PHONY: list
list:  ## say which steps there are, in the order they run
	@echo $(STEP_NAMES) | tr ' ' '\n' | cat -n

# The notebook's code is these steps, in this order. Which cell holds which step is in the cell's
# own metadata, so the two are checked against each other by name rather than by position.
.PHONY: embed
embed:  ## put the code of each step into the notebook cell which names it
	cd $(ROOT) && $(PYTHON) scripts/embed_steps.py $(NOTEBOOK) $(STEP_NAMES)

.PHONY: check
check:  ## check the notebook holds the code of each step
	cd $(ROOT) && $(PYTHON) scripts/embed_steps.py --check $(NOTEBOOK) $(STEP_NAMES)

.PHONY: clean
clean:  ## forget that anything ran, without touching what the steps wrote
	rm -rf .stamp
