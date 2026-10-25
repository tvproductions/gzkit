<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-7 specification — the rest of the context cut

**2026-10-25. Status: DRAFT, being ruled one question at a time.** Operator: **g0**. Repair order RO-7 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving the control plane. Every stage is measured by [RO-1's protocol](harbor-ro1-cut-measurement.md); each binding loss stops for the operator's ruling.

## Already ruled in the record

- The cut (operator, 2026-10-16): *"A (in safe mode - make backups!!! - help me test how much we can cut and remain effective…)"*; the backup is the tag `control-plane-baseline-2026-10-16`; canon is reset *"against the trimmed state"* through `gz content retire` and `land`.
- Exit numbers (GHIs #1250 and #1251, ruled A): at most 40 skills; descriptions at most 6,000 chars (met by RO-1 act (c)); every skill model-invoked or `disable-model-invocation: true`; bodies under ceiling; nested `AGENTS.md` at most 60 KB, agents 6 KB, personas 12 KB, hook text 4 KB per turn.
- The merge plan goes to the operator *"before the first deletion"*; a retired skill is deleted from every surface root in the same commit as its successor (#1250). *"most 'obpi' skills will change to work package skills"* (#1250, 2026-10-18).
- Rules: *"no binding clause is removed or reworded"* (#1246).
- Which skills become `disable-model-invocation` is the operator's choice (passage log, RO-1 act (c)).
- Cuts are chosen by cause; a clause kept as common cause cites records that pass `gz insights recurrence` (threshold 3).

## Settled by the record and the register order, not asked

- **Stage 1 is the rules narrative lift** (#1246), measured by RO-1 before the next stage begins.
- **Nested `AGENTS.md` is measured after the rules cut** (#1251: *"measure after those … before cutting rule bodies for it"*).
- **Rationalizations go to each skill's `references/`** (the row), lowering its grandfather ceiling in `skill_body_grandfather.json`.
- **The catalogue merge comes last,** after RO-5 (work-package skills replace OBPI skills) and RO-6 (which corrects four skills' meaning first); `gz-release` subsuming `gz-patch-release` (RO-4) counts as one merge.
- **AGENTS.md is cut only by the operator** retiring or re-tiering named corpus entries; no contractor cut.

## Current state (research of 2026-10-25)

73 skills, bodies 635,996 B; 11 bodies over 300 lines, each within its grandfather ceiling; descriptions 5,938 of 6,000 chars. Rules 150,889 B in 26 files against 60,000 B, 20 files over 4,000 chars. Agents 10,794 B against 6,000; personas 24,879 B against 12,000; nested `AGENTS.md` 210,505 B against 60,000; AGENTS.md 24,785 B against 25,000 (103 invariant entries). `CLAUDE.md` imports only the root `AGENTS.md`; no nested `CLAUDE.md` exists. No stage report exists yet.

## Rulings of 2026-10-25

(none yet)

## Open questions, in the order they are being ruled

1. Nested `AGENTS.md`: narrow `paths:`, stop generating subtree copies, or re-rule the 60 KB number.
2. Demotions to `disable-model-invocation`: designated per stage or as one list.
