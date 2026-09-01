# The context the notebook has by this point: the packages, this iteration's gene masks, and the metacells before any
# sharpening, with everything the analysis said about them.
import dafpy as dp
import metacellspy as mc

masks = dp.complete_daf("dafs/masks.I0", name="masks.I0")
metacells = dp.complete_daf("dafs/metacells.I0.R0", name="metacells.I0.R0")

# --- the notebook cell starts here ---
# Sharpening, which is the point of all of the above. A round re-groups the cells using what the round before it worked
# out about the manifold, and then works the manifold out again from the groups it arrived at - so each round is the
# same five calls, reading the round before it and writing a repository of its own.
#
# Two rounds here. Each is cheap to add and none of them is the last word, so how many to run is a number rather than a
# decision: raise it and the rounds below it are untouched, since each already ran and wrote what it wrote.
SHARPENING_ROUNDS = 2

for sharpening_round in range(1, SHARPENING_ROUNDS + 1):
    # The round's own repository, resting on the gene masks and through them on the cells. Not on the round before it:
    # what that round grouped the cells into is what this one is about to disagree with, and a repository can only hold
    # one set of metacells.
    name = f"metacells.I0.R{sharpening_round}"
    sharpened = dp.complete_chain(
        base_daf=masks,
        new_daf=dp.files_daf(f"dafs/{name}", "w", name=name),
        name=name,
    )

    # Which cells belong together, decided again - by clustering each neighborhood on the gene modules the previous
    # round found there. Cells which fit nothing are ejected, and are free to be placed again by the round after this.
    #
    # Each round advances the letter its metacells and its blocks are named with, so a name says which round it came
    # from wherever it turns up. The metacells we started from are the `M` the `h5ad` named them and their blocks the
    # `B` of the analysis above - round zero, in effect - so each round here is that many letters further on.
    mc.sharpen_metacells(
        sharp_daf=sharpened,
        base_daf=metacells,
        prefix=chr(ord("M") + sharpening_round),
        sharpening_round=sharpening_round,
    )

    # The same two steps the metacells we started from went through, now that this round has said which cells are which
    # metacell: aggregate the cells into them along with the genes which tell them apart, and work out what they say
    # about the manifold. That last is what the next round reads.
    mc.prepare_metacells(sharpened)
    mc.analyze_metacells(
        sharpened,
        prefix=chr(ord("B") + sharpening_round),
        prev_daf=metacells,
        module_status=True,
    )

    metacells = sharpened

print(metacells.description())
