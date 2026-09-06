# ADR-0.35.0 Quality and Readiness Review

Date: 2026-09-05 (local); final checks 2026-09-06 UTC.

**Technical authoring verdict: GO — 3.25/4.00.**
**Package design-readiness verdict: GO.** Operator g0 ratified the final publication
amendment with the verbatim approval **"approve the 07 work"**.
This score evaluates the complete ratified contracts, including that amendment. It is not
an implementation draw, completion attestation, or a claim that pending prerequisites shipped.

## Result and evidence

All thirteen checklist items have briefs. Ledger-grounded completion remains five attested
(01, 02, 03, 04, 09) and eight pending. All eight pending briefs pass authored validation.
Documents, decomposition, REQ-kind discipline, command shape and brief reconciliation pass.
The machine structural pre-screen is separately **3.55/4.00**, with thirteen briefs scored.
The previous **2.70 Conditional Go** review was superseded by actual brief repairs below.

Independent quality review reports PASS with no remaining technical authoring findings.
Narrator red-team review reports **10/10 PASS** after adding the delivery schedule.
Independent spec review also reports PASS with no remaining technical authoring findings.
These are actual session reviews, not fabricated ledger dispatch receipts: the generated
scorecard still reports no receipted dispatch and ungraded machine substance channels.

## Recorded operator decision

[OBPI-07, Publication Amendment (Ratified)](obpis/OBPI-0.35.0-07-content-land-orchestrator.md)
contains the approved contract. Its original Requirement 4 says:

> ALWAYS write atomically across the whole consumer set — temp-then-rename for every consumer, with no rename performed until every consumer's bytes are staged. A failure at consumer 2 of 3 MUST leave all three committed renditions unmodified.

Its REQ-05 simultaneously says:

> Given a landing interrupted after the first consumer, when the filesystem is inspected, then the landing state file EXISTS

Sequential renames cannot give atomic visibility of a whole set. **Approved: journaled per-file publication:** stage and verify everything first; atomically replace
each file; retain durable journal evidence through interruption; identify actual old/new/
indeterminate states by hashes; resume without rewriting verified files or re-attesting the
same corpus delta; emit success only after every artifact verifies. Readers of individual
files may observe mixed bytes while publication is incomplete.

The alternative is atomic activation of an immutable generation, requiring a changed storage
and reader protocol. That is not what the current file-layout/resume requirements describe.
The operator's approval resolves the final policy choice; existing decisions settle routing,
metrics and corpus-attestation reuse. AGENTS.md Behavior Rule Always #9 requires:
**“On inconsistencies: STOP, name confusion, present tradeoff, wait. Don't resolve unilaterally.”**
The explicit ruling above now ratifies the proposal; no policy decision remains pending.

## ADR rubric and structural-score reconciliation

| Dimension | Weight | CLI | Manual | Weighted | Rationale |
|---|---:|---:|---:|---:|---|
| Problem clarity | 15% | 4 | 4 | 0.60 | Concrete source/delivery, retirement and provenance gaps; agrees with CLI. |
| Decision justification | 15% | 4 | 3 | 0.45 | Existing rulings now reconcile; the publication amendment is approved. Specific alternatives and integration tradeoffs justify the manual score rather than section depth alone. |
| Checklist completeness | 15% | 1 | 3 | 0.45 | All thirteen items earn their place and map 1:1; prefix/granularity lint understates substantive coverage. |
| Decomposition quality | 15% | 4 | 3 | 0.45 | Explicit acyclic prerequisites and bounded responsibilities; 07/12 are broad transactions, which count heuristics miss. |
| Lane assignment | 10% | 4 | 3 | 0.30 | Public runtime/validator contracts justify Heavy; gates are specified without confusing corpus and completion attestation. |
| Scope discipline | 10% | 4 | 3 | 0.30 | Parser, shared scanner, generated artifacts and schema consumers are now included; actual boundaries matter more than section presence. |
| Evidence requirements | 10% | 4 | 4 | 0.40 | Specific unittest/BDD commands, negative controls and failure-state assertions define delivery; agrees with CLI after repairs. |
| Architectural alignment | 10% | 4 | 3 | 0.30 | Shared scanner, separate lineage, source identity and ledger prerequisites follow real modules; the publication guarantee is explicitly ratified. |
| **Total** | **100%** | **3.55** | | **3.25** | **GO; implementation dependencies remain explicit.** |

## All OBPI scores

I/T/V/S/C = independence, testability, value, size, clarity. Scores describe briefs, not
re-attestation of completed work. Seven test groups becoming three state-machine groups
does not hide work: 07/12 retain Size=2 and all semantic failure cases.

| Item | I | T | V | S | C | Mean | Disposition |
|---|---:|---:|---:|---:|---:|---:|---|
| 01 | 4 | 3 | 4 | 3 | 3 | 3.4 | Attested; unchanged |
| 02 | 3 | 3 | 4 | 3 | 3 | 3.2 | Attested; unchanged |
| 03 | 3 | 3 | 4 | 4 | 3 | 3.4 | Attested; unchanged |
| 04 | 4 | 3 | 4 | 2 | 3 | 3.2 | Attested; unchanged |
| 05 | 3 | 3 | 4 | 3 | 3 | 3.2 | Ready for implementation planning |
| 06 | 3 | 3 | 4 | 3 | 3 | 3.2 | Ready against declared 05 dependency |
| 07 | 3 | 3 | 4 | 2 | 3 | 3.0 | Approved contract; predecessor and ledger repairs required |
| 08 | 3 | 3 | 4 | 4 | 3 | 3.4 | Ready after 07 and explicit draw; Active residue preserved |
| 09 | 4 | 3 | 4 | 3 | 3 | 3.4 | Attested; unchanged |
| 10 | 3 | 3 | 4 | 3 | 3 | 3.2 | Explicit identity/reconciliation and publication dependencies |
| 11 | 3 | 3 | 4 | 4 | 4 | 3.6 | Ready for planning; independently bounded |
| 12 | 3 | 3 | 4 | 2 | 3 | 3.0 | Complete migration contract, depends on 05/06/07 |
| 13 | 3 | 3 | 4 | 3 | 3 | 3.2 | Lossless ordering contract, depends on generation/landing |

## Finding closure

| Finding | Resolution and evidence |
|---|---|
| F01 Missing 11/12 | Both are semantically authored and validate; thirteen-file decomposition preserved. |
| F02 Retired consumers | 05/07 consume manifest routes; root only for AgentContract. Multi-consumer tests use isolated declared fixtures. Equal candidate spans are valid. |
| F03 Mixed metrics | Parent Decision 4, Fidelity Assertions and 05/06 distinguish ownership-span coverage/ratchet from entry-text population statistics. The recorded span-based ruling governs; historical counts are not runtime constants. |
| F04 Atomicity contradiction | Concrete journaled-publication amendment in 07; technical review passed and operator ratification recorded. |
| F05 Provenance conflict | BI-03 and 05 prohibit embedded lineage while permitting the optional commit-time landing_id expressly required by Decision 6. Old sidecars remain readable. |
| F06 Attestation condition | 07 refuses new unattested corpus deltas; unchanged re-render and verified resume reuse evidence. 12 does not add a downstream attestation gate to valid remember capture. |
| F07 Missing parser scope | 06 includes parser_maintenance.py; 05 includes content parser/help. Both include named tests and BDD surfaces. |
| F08 Classification identities | 10 retains section-qualified row identities and explicit source/section/effective-entry mapping; no fuzzy first-match authority. Reconciliation preserves old raw rows and prefix fingerprint while deliberately changing the full fingerprint. |
| F09 08 readiness residue | Historical unauthorized Active status preserved; dependency on 07 now explicit. Advisory proof uses observable combined output and real exception branches. |
| F10 13 scope/acceptance | Six REQs match metadata; raw-byte permutation, required generated artifacts, repeat-generation persistence and independent delivery findings replace file-presence checks. Configurable cap is explicit. |
| R11 Shared boundaries | 05 owns one fence-aware byte iterator and ownership regression tests; 13 reuses it. No claim that the old scanner already handled fences. |
| R12 Durable ledger | 07 names verified GHI #952/#953 correction as an entry prerequisite; no private ledger writer or assumption that current append is durable. |
| R13 Candidate versus committed audit | 06 distinguishes public committed-state audit from pure candidate verification so 07 can repair stale committed output. |
| R14 Invariant inventory/fidelity | BI-01 includes all new readers. BI-06 preserves valid capture while existing type/identity validation remains. Fidelity proof uses isolated semantic tests rather than a production append or a substring gate incapable of detecting duplicates. |
| R15 Schedule | Parent Remaining Delivery Plan records estimates, external prerequisites, parallel opportunities and serialization of shared publication. |

## Ten red-team challenges

| Challenge | Result | Evidence |
|---|---|---|
| So what? | PASS | Thirteen distinct source, retirement, ownership, delivery and witness capabilities. |
| Scope | PASS | Rule vendor/nested consumers are coupled; ordering excludes rank/cap edits. |
| Alternatives/granularity | PASS | Generator, verifier and publisher stay separate; broad 07/12 size acknowledged. |
| Dependencies | PASS | 05 -> 06 -> 07 spine; 11 independent; ledger corrections explicitly precede 07. |
| Gold standard | PASS | Compared with validated ADR-0.0.26: traceability and proof commands retained, interruption controls extended; pending execution evidence is not claimed. |
| Timeline | PASS | 9–15 idealized critical-path engineering days; 15–24 single-implementer days, excluding prerequisite repairs/approval/integration waits. |
| Evidence | PASS | Every brief provides specific proof commands; pending tests are deliverables, not asserted results. |
| Consumer | PASS | Status/resume/rollback, corpus attestation and actual delivery findings are specified. |
| Regression | PASS | Effective-view, duplicate, identity, artifact-integrity and byte-boundary controls are explicit. |
| Parity/doctrine | PASS | Root-only route, source authority, configurable budget and remaining publication decision are honestly bounded. |

## Codex cap and next work

Codex project_doc_max_bytes is configurable; 32 KiB is the default, not an immutable ceiling.
The order-only comparison holds its observed configuration fixed without declaring that
configuration unchangeable. See [official configuration guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
No configuration was changed during authoring.

**Next implementation: 05**, after its plan is reviewed. It unlocks 06 and the landing spine.
11 is an independent planning candidate. **Before 07:** verify the GHI #952/#953 ledger corrections, in addition to its OBPI prerequisites.
No implementation, completion attestation, commit or push was performed by this repair pass.
