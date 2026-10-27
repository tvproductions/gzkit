---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-27T08:41:50Z'
agent: claude-code
session_id: 39291f64-4dcf-4725-ba9e-8be4e294c629
continues_from:
- .gzkit/handoffs/20261027T083342Z-model-class-safe-mode-lint.md
- .gzkit/handoffs/20261027T083438Z-session-exit-bookmark.md
---

## Current State Summary

Question-only session in safe mode; no code changed. The operator asked where the guard canaries came from and whether they work around something turned off. Answer: they came from GHI #1154 (filed 2026-09-30, twelve gates green without holding) and the 2026-09-24 test-suite integrity audit section 10 row 'Reviewed guard mutation canaries'; they landed 2026-10-02 (a267eed2b through 75f33a003, GHI #1154 and #1161). They are not a workaround for a disabled feature. Second question: the guard-canary sweep runs in safe mode (CI ubuntu run 2026-10-27T01:28Z: 'Guard canary sweep 372.40s', passed) but a failure is demoted: sweep_main exits 3 on a survivor and the step is ERROR level, so _apply_mx_seam turns it advisory while .gzkit/mx.json (committed, mode safe) is open. It is not one of the slow-alarm hooks; it runs only under gz check --full. Folds in the session-exit bookmark 20261027T083438Z, which recorded nothing beyond the exit.

## Important Context

Cosmic Ray provenance as found this session: the 2026-07-18 enforcement audit (docs/governance/enforcement-claim-nc-audit-2026-07-18.md:211) recommended adopting cosmic-ray scoped to enforcement modules as a diagnostic with no repo-wide score floor, and found it compatible with unittest. Its work order OBPI-0.31.0-07-mutate was removed in commit 993a16c11 (2026-05-23, GHI #520), the bulk demotion of 25 Pending feature ADRs to pool, not on its merits. The general engine is now parked as an open option in docs/design/adr/pool/ADR-pool.test-integrity-tooling.md (pooled 2026-10-01). CONFLICT for the operator to rule: the rulings store carries, from 20260822T132232Z, 'Handoff steps 1, 2, 4, 5 taken up; step 3 (mutation testing) DECLINED as a STDLIB-FIRST departure needing its own ADR.' Today the operator said they have resolved more than once to use Cosmic Ray and may not need an ADR (AGENTS.md STDLIB-FIRST: 'A runtime dependency, new or existing, needs ADR or OBPI rationale'; Cosmic Ray would be test tooling, which the pool ADR says stays out of the runtime set). The earlier pro-Cosmic-Ray resolutions the operator recalls were not found by gz handoff rulings --search cosmic (zero hits); a search is not a read, so they may exist in prose elsewhere. Canaries and Cosmic Ray are complementary: one reviewed mutant per guard claim versus generated mutants across modules.

## Decisions Made

- [operator-ruled] Cosmic Ray adoption is recorded for later, not acted on now (verbatim, voice-transcribed: "Well, we can't promote that in the middle of safe mode, but I think we've resolved on more than one occasion to use cosmic arrays, so I think this is an error that got caught up in that sweep. I'm not even sure that I need to wait for an ADR to use certain tooling. There are exceptions to standard lib first. Pydantic is a good example of that. But just put this into handoff notes, because I'm not necessarily going to take action right now.") 'cosmic arrays' is the voice transcription of Cosmic Ray.
- [agent-chose] Surfaced the 2026-08-22 decline ruling beside today's words rather than treating either as superseding the other; the operator rules which stands.

## Immediate Next Steps

1. Ask the operator whether to resume the contractor-kit R&D through gz-rnd (docs/rnd/contractor-kit.md), carried from the predecessor's step 1.
2. Then the mode contract's syntax: candidate Python affordances for code controls, after reading the census and the seven chore --self-test arms (carried).
3. When the operator takes up GHI #1273, carry the 2026-10-26 trap table, the report-only ruling, the 2026-10-27 full-lint-in-safe-mode ruling, and the GZKIT_MX_FULL_STRENGTH=1 observation (carried).
4. After gz mx exit, offer the operator the Cosmic Ray route: rule on the 2026-08-22 decline versus today's words, and on whether test-only tooling needs an ADR or only a recorded STDLIB-FIRST exception like Pydantic's in .gzkit/rules/models.md; then either promote ADR-pool.test-integrity-tooling or book the exception directly.
5. Remind the operator to turn off cowork-plugin-management via /plugin (carried).

## Pending Work / Open Loops

- Cosmic Ray: 993a16c11 (GHI #520 [settled]) swept OBPI-0.31.0-07-mutate into the pool; the operator calls this an error of that sweep. Unresolved until ruled after safe-mode exit.
- Guard canary sweep is advisory while safe mode is open: a surviving mutant shows as a demoted warning in CI, not a red step, until gz mx exit.
- GHI #1273: MX-system review; cognitive-baseline half of trap 6, trap 3 and the marker's place in git remain (carried).
- GHI #1268: arb red --commit grading; commit witness stays off the per-act record until fixed (carried).
- GHI #1263: parked; reference patch no longer applies cleanly (carried).
- RO-0 punch list line 1: four alarm hooks and the verifier pipe gate remain off until exit (carried).
- advisory-rules-audit Coverage Ledger: mx-mode.md scored at 1.10.0 while the rule is 1.14.0 (carried).
- 11 older CI unit-test failures not yet checked against the punch list or any GHI (carried).
- Safe-mode lease runs to about 2026-10-28T01:07Z; advisory debt keeps aging (carried).

## Verification Checklist

- uv run gz handoff rulings --search mutation shows the 2026-08-22 decline ruling quoted in Important Context.
- git show --stat 993a16c11 shows the demotion that removed OBPI-0.31.0-07-mutate.
- grep -n 'Guard canary sweep' src/gzkit/commands/quality.py shows the ERROR-level registration; sweep_main in src/gzkit/guard_canary.py returns 3 on a survivor.
- .gzkit/mx.json still present with "mode": "safe" (the gz-mx skill reads it) confirms safe mode is still open before acting on step 4.

## Evidence / Artifacts

- `src/gzkit/guard_canary.py` (sweep_main exit codes)
- `src/gzkit/commands/quality.py` (_STEP_GUARD_META and _apply_mx_seam)
- `data/guard_canaries.json` (canary registry)
- `docs/design/adr/pool/ADR-pool.test-integrity-tooling.md` (Cosmic Ray option)
- `docs/governance/enforcement-claim-nc-audit-2026-07-18.md` (cosmic-ray recommendation)
- `docs/evals/test-suite-integrity-audit-2026-09-24.md` (section 10 canary proposal)
- `.gzkit/mx.json` (open safe-mode marker)

## Settled Rulings

1765 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
