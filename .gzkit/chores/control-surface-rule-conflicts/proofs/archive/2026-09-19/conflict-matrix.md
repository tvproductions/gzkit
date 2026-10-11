# Conflict matrix — 2026-09-19

Scope: 28 canonical files, 378 unordered pairs. Baseline `3dc6f613042117838f4f4cad55abe0b2e3044d35`; current hashes and merged judgments in [current-pair-review.json](current-pair-review.json). All 147 pairs touching the six repaired rules were re-reviewed; reviewers also revisited seven unchanged pairs. Counts describe review coverage, not a proof that every possible contradiction has been found.

## Remaining concrete conflict

| Rule A | Rule B | Worked example | Evidence | Mechanical winner | Suggested resolution | Severity |
|---|---|---|---|---|---|---|
| R01 `.gzkit/rules/chores.md`, Authoring Location: canonical chore packages live in `src/gzkit/chores/<slug>/` | `.gzkit/rules/skill-surface-sync.md`, Surface Map: `.gzkit/chores/<slug>/` is canonical, edit here | Edit a canonical-class project's CHORE.md, then damage its acceptance.json. Sync copies project to package; doctor replaces differing trio members from package while repairing the damaged slug. The two rules name opposite authoring sources. A healthy differing slug alone does not trigger repair. | GHI #1044 | No single winner: `src/gzkit/sync_surfaces.py` copies canonical-class project to package; `src/gzkit/commands/chores.py` repairs DAMAGED members from package. Both bodies read; no destructive live probe. | Resolve authoring authority separately from bootstrap/recovery provenance; define whether recovery preserves an otherwise valid edited trio member. Keep current behavior pending that decision. | theoretical |

No monthly or episodic encounter frequency was established. The GHI records this audit finding, not evidence of a production overwrite.

## Repairs through separate GHI work orders

The audit remains a proof-only chore. The following edits were executed under the operator-authorized GHI repair workflow, with complete before snapshots retained in `repair-before-3dc6f6130/`.

| Finding | Work order | Result and witness |
|---|---|---|
| R21 invisible top-level skill version | GHI #1040 | Example now uses quoted `metadata.skill-version`; existing validator rejects the old field and accepts the nested control. Model routing unchanged. |
| R23 GHI release approval mislabeled Gate 5 | GHI #1041 | Rule, scorecard and release-skill metadata distinguish operator release approval from OBPI/ADR completion. Release approval step remains. |
| R12 test selector and Lite/full-check scope | GHI #1042 | Default unit tier, explicit BDD selector and full repository checks now have distinct scopes. Runtime untouched. |
| CLI authoring incorrectly forces ADR/brief for direct repair; alignment allows later GHI instead of same-patch skill | GHI #1043 | Direct GHI route acknowledged; same-patch skill or existing explicit waiver retained. Existing audit body confirms a follow-up GHI is not a waiver predicate. |

Independent criterion-based reviews: `postrepair-20260919-part0.json`, `postrepair-20260919-part1.json`, `postrepair-20260919-part2.json`. These assess documentary contracts, not behavioral effectiveness in future model sessions.

## Prior rows and bounded candidates

The [September 12 matrix](archive/2026-09-12/conflict-matrix.md) and its full supporting proofs are preserved unchanged. Its dispositions of R02–R11, R13–R16 and R18–R20 remain historical findings; current pair records supply the fresh review rather than treating that archive as current evidence.

- R22's serial command was already repaired before this run; no duplicate fix.
- R17's obsolete “forthcoming” wording was already removed. The broader rendered-shape/template obligation remains in existing corpus/map work; no claim that this audit completed that capability.
- R09 remains unproven: human-readable output does not itself prohibit JSON.
- Chore/MX whole-hangar scope versus direct-repair boundaries is an unproven candidate, recorded on GHI #943. No MX doctrine change.
- Token reaper wording is subordinate to root operator-initiation canon. No runtime reaper defect or new lock authority inferred.
- Test help's mutual-exclusion description is independently inconsistent with the parser/handler; recorded through `gz insights remember`, outside the rule-text repair contract.
