# ADR-0.35.0 Quality and Readiness Review

Date: 2026-09-05
Scope: all thirteen OBPIs; current implementation evidence, amended intent and next-work readiness.
Verdict: **CONDITIONAL GO — 2.70/4.00**. Reconcile the named contracts before drawing dependent implementation.

## Evidence and disposition

The parent decomposition target and checklist both specify thirteen items. The missing files
were 11 and 12. They are now semantically authored, linked to their existing parent items,
and individually pass authored validation. Another concurrent session committed scaffold
versions during review; the reviewed authored versions were restored and revalidated.
This authoring does not constitute an implementation draw or completion attestation.

Ledger-grounded status reports thirteen total, five completed, eight remaining, zero missing
brief files. Completed: 01, 02, 03, 04 and 09. Remaining: 05, 06, 07, 08, 10, 11, 12 and 13.
08's Active status is explicitly unauthorized residue; its dated note forbids treating that
status as authorization to resume. The campaign permits ADR-0.35.0 to remain Draft through
implementation; Draft alone is not the blocker.

Independent session inputs were supplied by the spec-reviewer, quality-reviewer and narrator
agents. Final focused spec review found no remaining authoring blockers in 11/12.
The machine scorecard has no recorded dispatch receipts and therefore still reports
SINGLE-DRIVER / NOT DISPATCHED. These session inputs are not claimed as mechanically receipted
dispatches. No ten-challenge red-team protocol was run.

## Configurable Codex cap

The operator's correction is accepted: Codex's default 32 KiB documentation budget is
configurable through project_doc_max_bytes. It is not an immutable vendor ceiling.
[Official AGENTS.md documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
describes increasing this value; the
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
documents the setting and configuration layers.

The observed local setting and declared-cap witness use 32768 bytes. The budget audit reported
46876 bytes, 14108 above that declaration, with advisory exit 0. This establishes a comparison
against the local declared value, not proof of the effective limit used by every running
Codex session. Configuration changes and manifest-witness changes are distinct operations.
No cap/configuration change was made by this review. OBPI-13 must state its desired configured
budget and ordering contract explicitly, without presenting the default as unchangeable.

## ADR dimensions and CLI reconciliation

The generated structural pre-screen is 3.55/4.00. It measures section presence, counts and
references; this manual score measures whether the contracts agree and can be implemented.

| Dimension | Weight | CLI | Manual | Weighted | Reason for manual assessment |
|---|---:|---:|---:|---:|---|
| Problem clarity | 15% | 4 | 4 | 0.60 | The source-to-delivery gap and retirement need are concrete; agree with CLI. |
| Decision justification | 15% | 4 | 3 | 0.45 | Extensive rationale satisfies presence heuristics, but later root-routing and metric rulings are not fully propagated. |
| Feature checklist | 15% | 1 | 3 | 0.45 | Prefix/granularity heuristics understate actual coverage: all thirteen numbered items now map to briefs. The delivery units remain uneven. |
| OBPI decomposition | 15% | 4 | 2 | 0.30 | Brief count and sections conceal broad 07/12 scope and unresolved prerequisite contracts. |
| Lane assignment | 10% | 4 | 3 | 0.30 | Heavy is defensible for public validators and runtime changes; implementation scope for 13 still needs reconciliation. |
| Scope discipline | 10% | 4 | 2 | 0.20 | Allowed/denied sections exist, but 06/13 omit required implementation paths and 13 contradicts exclusions. |
| Evidence requirements | 10% | 4 | 2 | 0.20 | Numerous commands satisfy heuristics; several assertions do not prove the intended failure states. |
| Architectural alignment | 10% | 4 | 2 | 0.20 | Architectural references exist, but lineage immutability and landing publication contracts conflict. |
| **Total** | **100%** | **3.55** | | **2.70** | **CONDITIONAL GO** |

## All OBPI scores

I = independence; T = testability; V = value; S = size; C = clarity. Scores evaluate
brief quality, not a reversal of existing human attestation. Passing historical items
are not reopened by current-template drift.

| OBPI | I | T | V | S | C | Mean | Readiness |
|---|---:|---:|---:|---:|---:|---:|---|
| 01 Tombstone schema/fold | 4 | 3 | 4 | 3 | 3 | 3.4 | Completed in ledger |
| 02 Withdraw verb | 3 | 3 | 4 | 3 | 3 | 3.2 | Completed in ledger |
| 03 Duplicate retirement | 3 | 3 | 4 | 4 | 3 | 3.4 | Completed in ledger |
| 04 Ownership/ratchet | 4 | 3 | 4 | 2 | 3 | 3.2 | Completed; its metric ruling must reach consumers |
| 05 Candidate generator | 3 | 3 | 4 | 3 | 2 | 3.0 | Reconcile root route, metrics and provenance before implementation |
| 06 Lineage validator | 3 | 3 | 4 | 4 | 2 | 3.2 | Depends on 05; repair parser allowlist |
| 07 Land orchestrator | 3 | 3 | 4 | 2 | 2 | 2.8 | Revise publication/recovery and attestation contracts |
| 08 Post-append advisory | 3 | 3 | 4 | 4 | 2 | 3.2 | Depends on 07; requires explicit draw |
| 09 Codex wiring | 4 | 3 | 4 | 3 | 3 | 3.4 | Completed; root-only amendment governs |
| 10 Classification ownership | 2 | 3 | 4 | 3 | 2 | 2.8 | Specify section-aware identity joins and failure cases |
| 11 Corpus shape witness | 3 | 3 | 4 | 4 | 3 | 3.4 | Authored; ready for planning against landed 01 |
| 12 Rules onboarding | 3 | 3 | 4 | 2 | 3 | 3.0 | Authored; depends on 05/06/07 and focused migration-plan review |
| 13 Render order | 4 | 2 | 4 | 4 | 1 | 3.0 | Mandatory revision: clarity dimension is 1 |

## Trackable findings and required corrections

Paths below are relative to this ADR package unless stated otherwise.

1. **F01 — Missing decomposition, repaired.** Parent Decomposition target is 13 and checklist
   items 11/12 already existed. Authored
   [11](obpis/OBPI-0.35.0-11-corpus-shape-witness.md) and
   [12](obpis/OBPI-0.35.0-12-rules-corpus-onboarding.md) now supply those items.
   11 audits effective corpus entries separately from the template and rendered-budget checks.
   12 preserves full rule documents, requires explicit migration assignments, uses the shared
   delivery chain and independently witnesses activation in the ledger.

2. **F02 — Root routing conflicts in 05/07.** OBPI-05 REQ-05 requires claude/heavy and
   codex/lite spans to differ; its demo still uses retired routing. OBPI-07 prerequisites
   likewise name claude/codex artifacts. OBPI-09's root-only amendment and current
   AgentContract manifest route govern. Rewrite the target matrix and expected spans;
   distinct consumers cannot be required where only root is configured.

3. **F03 — Metric contract unresolved in 05/06.** OBPI-04's operator amendment explicitly
   chooses section-span bytes for the ownership ratchet. Its coupling note preserves
   the parent's 31.2% entry-witness metric pending a separate ruling for 05/06.
   These are different denominators, not merely stale counts. Present the two calculations
   and obtain a scoped ruling before propagating either into generator/lineage acceptance.

4. **F04 — Whole-set atomicity is unproved in 07.** Staging every temporary file then
   sequentially renaming destinations cannot itself make publication of the whole set atomic.
   REQ-02 only proves staging failure behavior; REQ-05 must exercise failure after the
   first destination is published. Define observable mixed-state refusal and recovery,
   or an actual atomic publication mechanism, then test that state.

5. **F05 — Provenance shape conflicts.** Parent BI-03 says RenditionProvenance is
   unextended across every OBPI; 05 repeats the invariant. 07 explicitly permits adding
   landing_id. Reconcile storage ownership and the invariant before implementing 07.

6. **F06 — Attestation condition conflicts in 07.** Its unconditional empty-attestation
   rejection conflicts with its discovery note describing corpus-delta-only attestation.
   Specify initial/delta capture versus unchanged re-render behavior and refusal tests.

7. **F07 — Missing parser scope in 06.** Add the actual CLI forwarding surface
   src/gzkit/cli/parser_maintenance.py to both allowed-path representations and discovery.
   Declaring a new validator flag without its parser path is not execution-ready.

8. **F08 — Identity mapping ambiguity in 10.** The existing bullet-retention scorecard
   parser yields text/classification tuples without section identity. Define handling of
   identical text in distinct sections, missing matches and ambiguous matches. Prove
   identity-preserving ownership, not only equal totals.

9. **F09 — Unauthorized residue in 08.** Preserve the dated prohibition against resuming
   from Active status. Clarify its dependency on 07 instead of describing it as independent.
   A fresh explicit draw is required before implementation.

10. **F10 — Scope and acceptance mismatch in 13.** Frontmatter has three REQs while the
    body has six; allowed templates also appear denied; runtime/tests and the rendition
    required by its joint-commit contract are absent. Demo is a placeholder and file-presence
    checks cannot prove ordering/truncation behavior. Repair these together and express
    the configurable-budget assumption accurately.

## Next work

**Recommend 05 next as a brief-reconciliation task, followed by implementation once resolved.**
It advances the governing campaign's corpus-to-delivery chain and unlocks 06/07, then 08/12.
First resolve F02/F03/F05 using current root-only routing and an explicit metric ruling.
A scope recommendation is not authorization to pick between contradictory operator decisions.

**If selecting an implementation candidate with the fewest unresolved contracts, choose 11.**
Its fold prerequisite is delivered, it has a bounded audit surface, and the authored brief
includes semantic negative controls through the public validator. It is ready for planning,
not automatically drawn or attested. 12 is correctly authored but cannot precede 05/06/07.

## Verification limits

- Both new briefs pass individual gz obpi validate --authored checks after final edits.
- Document, decomposition, requirement-kind, command-shape and brief-reconcile validations pass.
- The full authored-validation batch also inspects completed briefs and reported historical
  completion/scope/template evidence issues; this review does not claim all thirteen pass
  that command or use those failures to nullify recorded attestation.
- No implementation test suite, runtime delivery gate or completion attestation was claimed.
- Existing brief conflicts remain tracked as F02–F10 here; they were not silently rewritten.

> Consider: uv run -m gzkit justify OBPI-0.35.0-05
