# The context the notebook has by this point: the packages, the seed, the base metacells, the second iteration's gene
# masks, and the base every round is scored against.
import dafpy as dp
import metacellspy as mc

RNG_SEED = 123456
SHARPENING_ROUNDS = 2

base_metacells = dp.complete_daf("dafs/metacells.base", name="metacells.base")
masks = dp.complete_daf("dafs/masks.I1", name="masks.I1")
base_manifold = dp.complete_daf("dafs/metacells.I0.R0", name="metacells.I0.R0")

# --- the notebook cell starts here ---
# The second iteration runs the steps of the first on its own masks. It starts again from the base metacells, analyzes
# and scores them, and then sharpens them for the same number of rounds.
#
# Every round is scored against the same base as the first iteration's rounds. The scores therefore continue one series,
# and say whether the corrected masks did better.
metacells = dp.complete_chain(
    base_daf=[base_metacells, masks],
    new_daf=dp.files_daf("dafs/metacells.I1.R0", "w", name="metacells.I1.R0"),
    name="metacells.I1.R0",
)
mc.analyze_metacells(metacells, module_status=True, rng=RNG_SEED)
mc.qc_metacells(daf=metacells, score_daf=base_manifold)

for sharpening_round in mc.sharpening_rounds(
    initial_daf=metacells,
    base_daf=masks,
    score_daf=base_manifold,
    directory="dafs",
    module_status=True,
    rng=RNG_SEED,
):
    if sharpening_round.index > SHARPENING_ROUNDS:
        break
    metacells = sharpening_round.run(f"metacells.I1.R{sharpening_round.index}")

print(metacells.description())
