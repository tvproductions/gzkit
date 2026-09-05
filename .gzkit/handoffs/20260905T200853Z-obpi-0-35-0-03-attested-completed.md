---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-09-05T20:08:53Z'
agent: claude-code
obpi_id: OBPI-0.35.0-03-retire-duplicate-invariant-entries
session_id: 100cf1f1-6de7-4ef3-a3ce-5ffffc6349f2
continues_from:
- 20260905T181329Z-obpi-0-35-0-04-attested-completed-correction-batch.md
- 20260902T042217Z-trailer-closed-config-gate-render-order-absorbed.md
---

## Current State Summary

OBPI-0.35.0-03-retire-duplicate-invariant-entries is ATTESTED COMPLETED (attestor g0, 2026-09-05T20:05:13Z, operator verbatim 'attest completed'). The pipeline ran from --from verify: no Stage 2 (the brief writes no code; src/** and tests/** are Denied Paths), Stage 3 green on canonical ARB receipts, Stage 4 narrator-composed with two tier-1 Codex adversary rounds, Stage 5 completion emitted obpi_receipt_emitted, four task_completed events and obpi_lock_released. The eight retirements themselves were already on disk from earlier sessions; this pass verified and reconciled them onto provable channels and did NOT touch .gzkit/corpus/AGENTS.md.jsonl. Remaining Stage 5 work at the time of writing: git-sync #1, gz obpi sync, gz adr status, git-sync #2, and the separate commit of a stashed skill amendment.

## Important Context

Three things a resuming agent will not infer from the brief. First, the working tree carried an operator-authored amendment to the gz-obpi-pipeline skill (v6.44.0, the Step 4b independent-closure rule) across four byte-identical mirrors. The operator ruled it must stay separately accounted for from OBPI-03. Committing it was REFUSED by the pre-commit staged-diff gate because src/gzkit/skills/gz-obpi-pipeline/SKILL.md is a src/** production path and the OBPI-03 pipeline marker sat at current_stage verify, past Stage 2. It is therefore held in git stash entry 0, labelled skill-amendment-v6.44.0-hold-until-after-OBPI-0.35.0-03-marker-clears. The markers are now removed, so the block has cleared and the stash can be popped and committed on its own. Second, that stash reverted the skill file on disk to its pre-amendment text; the operator ruling still governs regardless of file state, and no mechanical gate reads the skill (gz obpi precomplete reads the brief). Third, gz obpi complete failed once with a stale reconciliation receipt and cleared on the named remediation, gz obpi brief-drift, with zero deltas; that is the documented recovery, not a workaround.

## Decisions Made

- [operator-ruled] Gate 5 attestation given verbatim as 'attest completed' (2026-09-05), relayed through --attestation-text enriched with session receipt ids per AGENTS.md Attestation.
- [operator-ruled] Step 4b closes on independent confirmation of the corrected state, superseding the 2026-09-03 severity-only stopping condition (verbatim: 'I don't think we should attest without the fixes creating a clean adversarial (4b) review'). A fix confirmed only by the implementing agent does not close a finding.
- [operator-ruled] Three Stage-4 corrections were required before attestation: cite the CANONICAL_STEP_COMMANDS unittest-parallel receipt rather than the non-canonical uv run -m unittest -q run, dispatch the Stage-4 narrator rather than treating the absent attestation channel as a waiver, and reconcile the stale REQ-02 witness sentence against the ledger.
- [operator-ruled] The pipeline-skill amendment and the unrelated session-exit bookmark must be separately accounted for from OBPI-03, neither swept into its completion commit nor discarded.
- [agent-chose] Held the skill amendment in a labelled git stash rather than committing three of four mirrors, because a partial commit would have left the four control surfaces drifted.
- [agent-chose] Declared Stage 2 single-driver via gz obpi dispatch --single-driver rather than dispatching implementer and reviewers against a brief with no code surface to review.
- [agent-chose] Did not dispatch an adversary round 3. Round 2 returned CORROBORATED / not-refuted with 'Unresolved IN-SCOPE findings: none', and the skill forbids re-dispatching merely to remove caveat wording once independent closure is established.
- [agent-chose] Omitted the harness-supplied Claude-Session trailer from both commits, per the closed trailer set in .claude/rules/task-discovery.md.

## Immediate Next Steps

1. Run uv run gz git-sync --apply (git-sync #1 [settled]) to commit the OBPI-03 completion edits: the brief, the ledger, the audit log, the insights record, the exchange record and the plan-audit receipt.
2. Run uv run gz obpi sync OBPI-0.35.0-03-retire-duplicate-invariant-entries to confirm receipt and brief agree.
3. Run uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing --json so the parent ADR view reflects the reconciled state.
4. Run uv run gz git-sync --apply (git-sync #2 [settled]) to commit the reconcile output.
5. Run git stash pop and commit the four gz-obpi-pipeline SKILL.md mirrors on their own, message docs(obpi-pipeline): Step 4b closes on independent confirmation of the corrected state, trailer Task: TASK-obpi-pipeline-step4b-independent-closure. The pipeline marker is gone, so the src/** staged-diff gate no longer blocks it.

## Pending Work / Open Loops

- git stash entry 0 holds the v6.44.0 skill amendment across four mirrors (+48/-16). It is not committed and must not be discarded. This is the single most losable item in this session.
- GHI #965 is open with a blocker comment: gz obpi present-evidence executes every physical line of a multi-line Demo fence as its own command (src/gzkit/governance/stage4_evidence.py lines 86 to 111), so the tool-generated Stage-4a packet reports NOT-ATTESTABLE on a brief whose probes both exit 0. src/** was a Denied Path for OBPI-03; the direct fix is now unblocked.
- GHI #964 remains for the operator to route (direct fix versus chore), carried from the prior session on OBPI-0.35.0-04.
- REQ-0.35.0-03-04 is a STRUCTURAL-FENCE requirement audited at ADR-0.35.0 closeout, not per-OBPI; the no-byte-identical-live-invariants property must be re-checked after each later ADR-0.35.0 OBPI lands.
- Remaining ADR-0.35.0 briefs are drawn only by the operator under the IRON LAW; run uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing for the landed count rather than trusting any figure transcribed here.

## Verification Checklist

- uv run gz obpi status OBPI-0.35.0-03-retire-duplicate-invariant-entries should report attested completed.
- uv run gz obpi lock list should report no active locks.
- git stash list should show the entry labelled skill-amendment-v6.44.0-hold-until-after-OBPI-0.35.0-03-marker-clears until it is popped and committed.
- git status --short should show no .pipeline-active marker files under .claude/plans/.
- uv run gz obpi sync OBPI-0.35.0-03-retire-duplicate-invariant-entries should report receipt and brief in agreement.
- Both probes in the brief Demo section should exit 0 and print eight targets retired with zero duplicate invariant texts.

## Evidence / Artifacts

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md` (the brief, now status Completed, carrying both Step 4b rounds)
- `.gzkit/locks/exchange/20260905T200513Z-OBPI-0.35.0-03-retire-duplicate-invariant-entries-complete.md` (completion exchange record that discharged the lock release)
- `artifacts/receipts/arb-step-codexadversary-bdfaf2a751b24a77878c0bc33d5dd584.json` (Step 4b round 1, CORROBORATED-WITH-CAVEATS)
- `artifacts/receipts/arb-step-codexadversary-0e8982ddb8a846e7a1f80edaea7e68ad.json` (Step 4b round 2, CORROBORATED, standing verdict)
- `artifacts/receipts/arb-step-unittest-a0c70f5175df46fc9437565e626d769e.json` (canonical unittest-parallel, 9423 tests, exit 0)
- `.gzkit/evidence/OBPI-0.35.0-03-retire-duplicate-invariant-entries.evidence.json` (tool-generated Stage-4a packet; NOT-ATTESTABLE only because of GHI #965)
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/logs/obpi-audit.jsonl` (ADR-level audit ledger carrying the Gate-5 attestation)
- `.gzkit/ledger.jsonl` (adversarial_validation, obpi_receipt_emitted, four task_completed, obpi_lock_released at 2026-09-05T20:05:13Z)

## Settled Rulings

725 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
