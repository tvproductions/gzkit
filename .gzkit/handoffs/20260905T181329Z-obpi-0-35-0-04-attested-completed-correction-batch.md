---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-09-05T18:13:29Z'
agent: claude-code-c0e76d04
obpi_id: OBPI-0.35.0-04-section-ownership-and-ratchet
session_id: c0e76d04-c377-4481-bbd7-cfe1d82006f8
continues_from:
- 20260905T125247Z-obpi-0-35-0-04-execution-paused-by-operator.md
- 20260905T164705Z-session-exit-bookmark.md
---

## Current State Summary

OBPI-0.35.0-04-section-ownership-and-ratchet is attested_completed (g0, 2026-09-05T18:11:12Z, operator verbatim 'Attest completed for OBPI-0.35.0-04'). Round 12 (tree f8952033) returned not-refuted from Codex tier 1 (arb-step-codexadversary-1e432720be4046cfaee3197e27a82a1a) and a separately attributable Claude review (arb-step-claudeacceptance-3eae42a1cd9845d2900a25e28b595617). Its medium, one low and the cosmetic were corrected as one frozen batch, commit d2280608 on main (saved Win32 error read in _windows_directory_error, three-arm mocked regression, a deterministic Windows-only native failure-path test, manpage exit-row split, roster comment). The batch was re-swept (44 of 44 KILLED at d2280608, W08 added for the correction, nothing historical recovered), passed Windows and Linux CI run 33981617383, and was confirmed not-refuted by Codex tier 1 (arb-step-codexadversary-fe5cf406644b4a688924c12b89071450, approve, no material findings). The lock was transferred from the consulting Codex agent through --force --abandon external_blocker and surrendered mechanically at completion. Stage 5 accounting (git-sync, obpi sync, ADR status refresh) is in flight in this session.

## Important Context

Operator scoping, verbatim: 'Do not reopen the malformed-metadata boundary or ledger exceptions. The historical-token preflight limitation is a separately tracked tooling issue; do not erase history or misstate a verdict to make it green.' The malformed-declaration low stays DISCLOSED in the brief's Tracked Defects (accepted hand-edit boundary); GHI #952/#953 ledger exceptions are unchanged. gz obpi precomplete fails adversarial_validation on historical refuted tokens by design (GHI #879) even though the brief states round 12 overturned them, and gz obpi pipeline --from=verify stops there after every verification passes; filed as GHI #964 (defect, runtime) and left open with a routing blocker for the operator. Completion proceeded on gz obpi complete's own chokepoint, which reads the flags. Codex remains a consulting agent; it must not be re-dispatched against this OBPI. Windows native failure-arm execution is established by the skipUnless gate plus the green Windows Test step, not a per-test listing (Codex named this the weakest point); closing it needs a verbose per-test Windows run, a CI-surface change outside the brief. The airlock entry diagnostic reports NO-GO on ten arb-red receipt seams after a re-sense; it is diagnostic-only and did not block.

## Decisions Made

1. Correction batch frozen at d2280608; no further implementation under this OBPI (operator: 'Do not reopen implementation or initiate another review cycle'). 2. Mutation roster rerun with the existing harness, 43 cases rebound by hash only plus W08; G19-G22 stay missing by ruling. 3. Lock ownership resolved through the supported abandon path mirroring the 13:13Z handover; orphaned-implementation audit passes. 4. Completion recorded with --adversary-verdict not-refuted --adversary-tier 1 --adversary-receipt arb-step-codexadversary-fe5cf406644b4a688924c12b89071450 and an --adversary-resolution citing rounds 6-12. 5. Preflight defect tracked separately as GHI #964; history in the brief preserved verbatim.

## Immediate Next Steps

1. Finish Stage 5 in this session: git-sync #1 [settled] (evidence, ledger, brief, appendix final/, exchange records, this handoff), gz obpi sync OBPI-0.35.0-04-section-ownership-and-ratchet, gz adr status ADR-0.35.0-canon-entry-corpus-landing --json, git-sync #2 [settled]. 2. Operator routes GHI #964 (direct fix vs. chore). 3. Next ADR-0.35.0 brief is drawn only by the operator via the gz-obpi-pipeline skill (IRON LAW); run uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing for the landed count rather than trusting a figure here.

## Pending Work / Open Loops

GHI #964 open (preflight false-red on discharged refutations). GHI #952/#953 open by ruling (ledger transaction boundary). Malformed-declaration REQ-09 prose gap disclosed in the brief, unfixed by ruling. Verbose per-test Windows evidence for the native failure-path test not captured (CI-surface change). Remaining ADR-0.35.0 briefs: see gz adr status.

## Verification Checklist

uv run gz obpi lock list -> No active locks. uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing shows OBPI-04 completed. git status clean after git-sync #2; git log -1 on main is the accounting commit. uv run gz check exit 0 (pre-push gate).

## Evidence / Artifacts

Correction commit d2280608. Receipts: arb-step-codexadversary-fe5cf406644b4a688924c12b89071450 (correction confirmation), arb-step-codexadversary-1e432720be4046cfaee3197e27a82a1a and arb-step-claudeacceptance-3eae42a1cd9845d2900a25e28b595617 (round 12), arb-step-unittest-8c04ad08c231472f9bbedd6684e2fbff (9,423 OK), arb-ruff-99d2427af2414c04b5d897223e8cada1, arb-step-typecheck-d5cd9e014d86422b820f0afafa5de7c9, arb-step-behave-8c596e4e37324a71ba0b6604a93097ec, arb-step-mkdocs-e2181dd3816e40bd9af39154b74fb9de. Appendix: docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/appendices/obpi-04-recovery-2026-09-05/final/ (summary-v5.json, postfix-mutation-evidence.zip, postfix-ci-result.json, postfix-ci-windows.log, postfix-codex-confirmation.log, round12-fix-mutation-witness.log). Exchange records: .gzkit/locks/exchange/20260905T174254Z-...-abandoned.md and 20260905T181112Z-...-complete.md. Ledger: obpi_completion, adversarial_validation, obpi_lock_released (force=false) at 2026-09-05T18:11:12Z.

## Settled Rulings

725 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
