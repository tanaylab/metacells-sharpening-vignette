# The context the notebook has by this point: the packages, the seed, this iteration's gene masks, and the metacells
# before any sharpening, with everything the analysis said about them. Those metacells are also the base every round is
# scored against.
import dafpy as dp
import metacellspy as mc

RNG_SEED = 123456

masks = dp.complete_daf("dafs/masks.I0", name="masks.I0")
metacells = dp.complete_daf("dafs/metacells.I0.R0", name="metacells.I0.R0")
base_manifold = metacells

# --- the notebook cell starts here ---
# Sharpening, which is the point of all of the above. A round re-groups the cells using what the round before it worked
# out about the manifold, and then works the manifold out again from the groups it arrived at. Each round reads the
# round before it and writes a repository of its own.
#
# Running a round does all of it. It decides again which cells belong together, by clustering each neighborhood on the
# gene modules the previous round found there. Cells which fit nothing are ejected, and are free to be placed again by
# the round after it. It then goes through the same steps the metacells we started from went through: it aggregates
# the cells into the new metacells, and works out what they say about the manifold. That last is what the next round
# reads. Finally, it scores the round against `base_manifold`, exactly as the metacells we started from were scored.
# The scores therefore make a series.
#
# Each round's repository rests on the gene masks, and through them on the cells. It does not rest on the round before
# it. What that round grouped the cells into is what this one is about to disagree with, and a repository can only hold
# one set of metacells.
#
# Each round advances the letters its metacells and its blocks are named with, so a name says which round it came from
# wherever it turns up. The metacells we started from are the `M` the `h5ad` named them, and their blocks are the `B`
# of the analysis above.
#
# The rounds never end by themselves, so the loop says when to stop. Two rounds here. None of them is the last word, so
# how many to run is a number rather than a decision. Raise it and the earlier rounds are untouched, since each already
# ran and wrote what it wrote.
SHARPENING_ROUNDS = 2

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
    metacells = sharpening_round.run(f"metacells.I0.R{sharpening_round.index}")

print(metacells.description())
