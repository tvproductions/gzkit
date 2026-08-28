---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-28T08:24:10Z'
agent: claude-code
session_id: 69255efb-df21-4cd4-a8d5-27b1585f3ea0
continues_from: .gzkit/handoffs/20260828T015945Z-ghi-900-close-and-787-reopen.md
---

## Current State Summary

GHI #787 closed (disposition fixed) by commit 0347dacb, and the repo is fully synced — tree clean, 0/0 against origin/main. The session opened by reviewing the resumed handoff 20260828T015945Z, booking the operator ruling "git sync first, then rule on 787" to Layer 2, then executing both halves in that order. The sync swept five dirty governance paths as 536994e3 and pushed the previously-unpushed 22ad1659. The #787 work found that the reopen understated its own defect: the coupling checklist did not merely omit the _STEP_GUARD_META obligation, it affirmatively declared that dict "NOT an obligation" and "a refinement, not a duty", while check_reachability.py reads that same dict as its SOLE evidence that a scope is gated. The new witness tests/governance/test_check_registry_coherence.py found a live instance on its first run — "OBPI lifecycle coherence" ran as a real gz check step while --obpi-lifecycle-coherence sat in the ungated grandfather as protecting nothing. Registered; baseline drained 52 to 51. uv run gz check returned REAL EXIT 0 on a fully staged tree, 58/58 steps.

## Important Context

The load-bearing mechanism is one regex. check_reachability.py:61 defines gated as _CHECK_REGISTRY_RE matching a kebab string followed by _mx_levels, read against src/gzkit/commands/quality.py, and the only construct in that file matching it is _STEP_GUARD_META — all 54 matches come from that dict. _seam falls back to a kebab-cased display name for an unlisted step, which keeps the MX seam correct and is INVISIBLE to that regex; that asymmetry is the whole reason the dict read as optional to every reader but the ratchet. Verified empirically that _STEP_GUARD_META membership was the sole gating evidence for wheel-path-literals: it has no independent HOOK/CI/PRECOMMIT caller, so deleting one line would have moved the ungated set 52 to 53 and breached the shrink-only ratchet. Second non-obvious point, measured rather than carried forward from the reopen: only ONE of the four obligations the reopen called default-tier actually is tier-dependent. QC_CLAIM_EXEMPTS and data/check_step_concurrency.json are per-step and bind at any tier (they were filed as family A items 5-7 alongside _STEP_GUARD_META); the genuine branch is the post-snapshot admission list, where DEFAULT tier takes an order-sensitive TUPLE and EXPLICIT tier a frozenset. Filing the first three under a tier branch would have reproduced the exact family-conflation defect the issue diagnosed. Old docstring items 5-8 renumbered to 8-11 to seat the new family-A entries, so any external prose citing item numbers from the 2026-08-09 close is now stale by design. Finally: the prior close refused a mechanical arm as prose-grading, and that refusal is CORRECT and preserved verbatim — the new test escapes it because both sides are produced by executing real code (the ratchet own check_registry_members against the live _build_check_steps population), never by reading text.

## Decisions Made

- [operator-ruled] Sequence: "git sync first, then rule on 787" (verbatim). Booked via gz handoff decide against 20260828T015945Z, decision proceed. Handoff steps 4 (#866) and 5 (#899) were neither selected nor declined, so nothing was set aside.
- [operator-ruled] Scope of the #787 fix: map fix plus coherence test (selection from a three-option menu; the ratchet stays at pre-commit rather than moving into gz check). Rejected: moving the 44.5s ratchet into gz check, which would also have triggered four family-A registrations of its own; and the prose-only remedy the reopen suggested, which reproduces the defect class.
- [agent-chose] Routed #787 as a direct fix without asking. AGENTS.md Operator Doctrine settles it verbatim — "GHIs are AUTHORIZED for direct repair, always" and "the GHI is the work order and the receipt" — so presenting routing as a question would have been the drift vector Operator Economy #7 forbids. Routing facts computed anyway: 3 files, single module, 452 fix( commits in 60 days, in-flight defect, unit-test coverage.
- [agent-chose] Corrected the reopen own framing rather than implementing it as written. It reported item 4 as an omission; source reading showed an affirmative inversion, which is the worse defect because it steers a reader away from a required edit and leaves them confident.
- [agent-chose] Placed the three per-step obligations in family A rather than the reopen suggested default-tier branch, on measurement of what each surface keys on.
- [agent-chose] Drained --obpi-lifecycle-coherence from data/validator_reachability_grandfather.json via the script own --report --write rather than hand-editing, per DO IT RIGHT 1a (the baseline is a coupled consumer of the fact just corrected).
- [agent-chose] Did NOT record an insight for this work. Behavior Rule 11 covers operator course-corrections; a selection from a menu the agent offered is not one, and the finding is captured in the docstring, the test, and the close comment.
- [agent-chose] Noted --doc-surface-parity (tier-D orphan, delete candidate, surfaced by the ratchet --report) in the close comment rather than filing a GHI. It is already disclosed by the shrink-only baseline, so it is tracked rather than silent.
- [self-corrected] A first attempt at this handoff described GHI #854 as open. The authoring gate settled-citation annotation marked it closed, which it has been since 2026-08-22. The claim came from reading its cross-link comment in the #787 thread and inferring state rather than querying it. Document rewritten; the inference is recorded here because the same shortcut is what the whole session was repairing elsewhere.

## Immediate Next Steps

1. Re-derive GHI #866 blocking premise. Its title claims that no new gz validate flag can be added, and 22ad1659 added one (--wheel-path-literals), so a counter-example now sits in HEAD. That may dispose of the issue outright rather than needing the re-derivation the prior handoff advised. OBPI-0.35.0-06-validate-rendition-lineage should still be re-checked against the current tree before disposal.
2. Dispose GHI #899 — the operator-name-in-wheel sibling of #900 [settled]. Open and untouched across two sessions now.
3. Optional, and NEW work rather than a reopen: GHI #854 [settled] closed 2026-08-22 via 63ce179a on the same checklist-undercount class, but its remedy is a corrected prose list guarded by gz validate --advisory-scorecard and --bullet-retention, not an execute-both-sides witness. Its own close comment names an EIGHTH coupled surface (bumping a rule version obliges an advisory-scorecard re-scoring pass). Whether the shape that closed #787 [settled] transfers to the new-CLI-verb obligation set is unexamined.
4. No campaign work was drawn this session. The active plan (docs/governance/build-to-1.0-campaign-2026-08-16.md, Movement B topmost) remains at 7/25 with the airlock transit counters unmoved.

## Pending Work / Open Loops

GHI #866 — open; commented in a prior session, not disposed of; its premise has measurably changed and a direct counter-example now exists in HEAD, but the class-of-failure question (a shrink-only ratchet on a sole registration point) is not established as resolved. GHI #899 — open, untouched by two consecutive sessions. Those two are the only open GHIs this session touched or surfaced. Uncovered causes deliberately left by the #787 [settled] close and stated in its comment: a future consumer added without updating the map has NO witness (the prose-grading refusal is why), and the tier branch in item 9 is prose with no mechanical arm. Ratchet --report names --doc-surface-parity as a tier-D orphan with no caller anywhere — disclosed by the shrink-only baseline, not silent, but never triaged. Advisory drift reported by gz check throughout: 696 unlinked specs, 1 unjustified code change (down from 11 last session). AGENTS.md continues to warn that must-survive sections operator-doctrine-verbatim-canon and architectural-boundaries straddle or sit past the codex 32768 B delivery cap — undelivered canon is not in force, and raising the budget cannot relieve a vendor cap.

## Verification Checklist

uv run gz check  (expect REAL EXIT 0 on a fully staged tree; git add -A first; 58/58 steps)
uv run python -m unittest tests.governance.test_check_registry_coherence  (expect 2 tests OK)
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py  (expect ungated 51, baseline 51, ratchet holds)
git rev-list --left-right --count origin/main...HEAD  (expect 0 0)
gh issue view 787 --json number,state  (expect CLOSED)
Mutation check if the coherence test is edited: remove the "OBPI lifecycle coherence" entry from _STEP_GUARD_META and confirm the forward test fails naming that step; inject a guard-meta key with no live step and confirm the inverse test fails naming it. Both were observed this session.

## Evidence / Artifacts

src/gzkit/commands/quality.py — _STEP_GUARD_META (new entry plus corrected fallback comment) and the _build_check_steps coupling checklist (families A/B, items 1-11, the tier branch, and the recorded exception to the prose-grading refusal)
tests/governance/test_check_registry_coherence.py — 2 tests, both directions, both mutation-killed
data/validator_reachability_grandfather.json — --obpi-lifecycle-coherence drained; baseline 52 to 51
.gzkit/chores/control-surface-validator-reachability/check_reachability.py:61 — _CHECK_REGISTRY_RE, the regex that made _STEP_GUARD_META load-bearing
.pre-commit-config.yaml:77 — validator-reachability-ratchet, the pre-commit placement the operator ruled stands
Commit 0347dacb (the fix, 3 files, +182/-25); commit 536994e3 (governance sweep); commit 22ad1659 (the GHI #900 close this was measured across)
GHI #787 close comment: https://github.com/tvproductions/gzkit/issues/787#issuecomment-5450143342

## Settled Rulings

563 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
