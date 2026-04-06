# ADR-pool.structured-uat-walkthrough

- **Status:** Pool
- **Lane:** Heavy
- **Date:** 2026-04-05
- **Origin:** GSD v1 comparative analysis — verification walkthrough adaptation

## Intent

Add a structured, deliverable-by-deliverable user acceptance walkthrough to Gate 5
attestation. Currently, Gate 5 is powerful but unstructured — the human decides what
to observe, what to test, and what constitutes sufficient evidence. This works well
for experienced operators but creates two failure modes: (1) operators who skim
through attestation because the ceremony is unguided, and (2) operators who are
thorough but miss deliverables because there's no checklist generated from the actual
OBPI acceptance criteria.

A structured UAT walkthrough extracts testable deliverables from OBPI briefs, presents
them one at a time with verification commands, auto-diagnoses failures, and produces
a structured evidence trail for attestation.

## Target Scope

### Walkthrough Generation

`gz uat --adr ADR-X.Y.Z` generates and runs a structured acceptance walkthrough:

1. **Extract deliverables** from each OBPI brief's acceptance criteria section.
   Each criterion becomes a testable item with:
   - Description (what to verify)
   - Verification command(s) (how to verify — CLI commands, test runs, visual checks)
   - Expected outcome (what success looks like)
   - OBPI source (traceability back to the brief)

2. **Present each deliverable** to the operator sequentially:
   - Show the criterion and its OBPI source
   - Run or suggest the verification command
   - Ask the operator: "Pass / Fail / Skip with reason"
   - If Fail: auto-diagnose using available signals (test output, lint errors,
     runtime behavior) and produce a fix plan

3. **Produce UAT report:** `{ADR-dir}/audit/UAT-ADR-X.Y.Z.md` with:
   - Pass/fail status per deliverable
   - Evidence captured (command output, screenshots, operator notes)
   - Fix plans for failures (if any)
   - Summary: "N of M deliverables passed, K skipped, J failed"

### Auto-Diagnosis

When a deliverable fails verification:

- **Test failures:** Parse test output, identify failing assertion, trace to source
- **Lint/type errors:** Run `gz check` and correlate errors with the deliverable's scope
- **Runtime failures:** If the deliverable involves CLI commands, capture stderr and
  correlate with known error patterns
- **Fix plan output:** Structured description of what's wrong and what to fix,
  formatted as an OBPI-scoped patch plan that can be fed back to the implementer

### Integration with Gate 5

- `gz closeout --uat` runs the walkthrough as part of the closeout ceremony
- UAT report is attached as Gate 5 evidence alongside attestation
- If any deliverables are "Fail" status, closeout blocks until they're resolved
  or the operator explicitly attests with "Completed — Partial"
- UAT report feeds into `gz audit` evidence verification

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- UAT does not replace human judgment — the operator still attests. The walkthrough
  ensures they have structured evidence to attest against.
- No visual/UI testing automation — verification commands are CLI-scoped. Visual
  checks are presented as "please verify manually" items.
- No test generation — UAT uses existing tests and commands. It doesn't create
  new test cases.
- Not mandatory for Lite lane — Lite ADRs don't have Gate 5.

## Dependencies

- **Prerequisite:** OBPI briefs with structured acceptance criteria (already standard)
- **Complements:** ADR-pool.agent-execution-intelligence CAP-09 (goal-backward
  verification is the philosophical foundation; UAT is the operator-facing surface)
- **Complements:** ADR-pool.svfr-quick-adhoc (quick OBPIs under the maintenance ADR
  get a lightweight UAT during periodic review)
- **Related:** ADR-0.19.0 closeout/audit processes (UAT extends the closeout ceremony)

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Deliverable extraction from OBPI acceptance criteria is validated — confirm
   the parser produces meaningful testable items from real briefs.
3. Auto-diagnosis scope is bounded — define which failure types get auto-diagnosis
   vs. "please investigate manually."
4. UAT report format is accepted and integrates cleanly with existing audit artifacts.
5. At least 2 real ADR closeouts are run with the UAT walkthrough to validate the
   operator experience — is it helpful or bureaucratic?

## Inspired By

- [GSD](https://github.com/gsd-build/get-shit-done) `/gsd-verify-work` — extracts testable deliverables from implementation summaries, walks the user through each one, auto-diagnoses failures, and creates fix plans. No manual debugging required.
- Kubernetes Production Readiness Review — structured checklist of operational
  requirements that must be verified before a service goes to production.

## Notes

- The hardest part is extracting machine-parseable verification commands from
  free-text acceptance criteria. Consider: requiring acceptance criteria in OBPI
  briefs to include explicit `verify:` blocks (similar to GSD's `<verify>` XML tags).
  This connects directly to ADR-pool.structured-prompt-architecture.
- Risk: the walkthrough becomes a rubber-stamp checklist where operators click
  "Pass" without actually observing. Mitigation: require evidence capture (command
  output) for Pass verdicts, not just the operator's word.
- GSD's verification creates fix plans automatically. In gzkit, a failed deliverable
  could create a new OBPI brief under the same ADR — connecting UAT failures back
  into the governance pipeline rather than treating them as ad-hoc patches.
- Consider: `gz uat --quick OBPI-X.Y.Z-nn` for single-OBPI verification during
  development, not just at closeout time.
