# Three-pillars corrective delivery

Dated 2026-09-19. Persona: main-session. This account covers the operator's
explicitly selected repair list after the earlier five-row plan omitted retained
experimental leads. It supersedes that plan's repair-completeness claim, not its
recorded proof-currency or pool rulings. No OBPI is initiated by this work.

## Selected work and evidence

| Work | GHI | Semantic verification |
| --- | --- | --- |
| Plan scope containment | #1057 | Out-of-allowlist edits fail with a FAIL receipt; valid exact/subtree/glob paths pass. Explicit paths outside conventional roots, coordinates, and parent traversal receive regression coverage. |
| Smoke runtime membership and discovery | #1055 | Source-only markers cannot satisfy required membership; aliased markers execute; discovery/import failures return 1 even with an otherwise passing member. Empty optional tier remains advisory, required empty tier returns 3. |
| Smoke guidance consumers | #1047 reopened | Parser, command recovery, quality docstring and manpage agree on opt-in emptiness, execution-only budget, and runtime plus policy amendment. |
| Promotion applied-state recovery | #1058 | Four post-write failure causes preserve promoted files and ledger history; output names applied state and existing-target recovery; recovery runs without a second promotion or duplicate events. |
| Configured manifest generation and IO | #1056 | Explicit roots beat decoy default directories; unconfigured discovery remains; read/write/preserved rules and sync reporting select the configured manifest. |
| Configured CLI documentation source | #1059 | Main parser, split parsers and command registrars beneath the configured root supply both command and flag discovery; decoy default commands stay excluded. |
| Coupled source-audit corrections | #1050 reopened | Real-tree fixture loads repository config and proves a nonempty source population; census instructions use configured roots; classifier prose describes actual ancestor/descendant matching. |
| Source audit completeness | #1061 | Read, decode and parse failures produce project-relative issues and a failing CLI result; readable neighboring files are still audited. |
| Sync documentation | #1060 | Vendor roster and generated path account follow configured vendors and include the shared agent skill surface. |
| Draft reconciliation only | #960 reopened | OBPI-0.36.0-07 and operative parent text require independent current-envelope re-review; resolution prose alone cannot clear either refuting verdict. Original verdict retained; lifecycle and implementation untouched. |

The runtime regressions were observed failing before each implementation change.
Independent review covered the required outcomes, found missed plan extraction
cases and a draft-section editing error, and required their correction. Promotion
recovery was independently executed. Full integration results are recorded below
only after completion.

## Boundaries and remaining observation

Broad proof invalidation remains the operator-selected disposition under #1029.
`ADR-pool.bounded-advisory-impact` remains pooled and unbuilt under #1053.
ADR-0.36.0 remains Proposed and its OBPI-07 remains Draft; this correction changes
requirements and examples only. There is no new second-opinion runtime, no pool
implementation, and no OBPI initiation or completion in this repair set.

At 2026-09-19T23:13:34Z, parsing ledger timestamps after treatment commit
`6b440453e67afd49ec8d94c17515740b5383369f` (2026-09-19T00:30:58Z) still found
zero `pipeline_launched`, `acceptance_recorded`, `adversarial_validation`, or
`obpi_receipt_emitted` events. GHI #1028 was read live and remains open: a future
normal, separately operator-initiated OBPI must supply its production comparison.
Passing this repair set's tests does not supply that observation.

The smoke review also exposed an independent script-import defect:
`scripts/check_proof_freshness.py` assumes captured stdout supports `reconfigure`.
It is recorded in the insights store at 2026-09-19T23:11:51.248631+00:00. The
budget unit fixtures now exercise their own deterministic result contract;
fresh-interpreter smoke discovery was separately run successfully. This script
robustness finding is not represented as fixed by the smoke repair.

Remaining experimental leads were disposed explicitly: current mirror filename
advice resolves to existing canonical targets; no mapping defect was reproduced.
The flag-substring and expanded smoke-timer proposals were experimental stimuli,
not established violations of the existing contract. CLI source-absence fallback
is preserved as existing framework behavior. Source read/parse suppression was
confirmed and repaired under #1061.

## Verification and delivery

Pending final integration checks and guarded delivery. Issue closure comments
will cite the actual landed commit and verified receipts, individually.
