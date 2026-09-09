# Acceptance obligations and independent closure

GHI #985 repairs the existing pipeline's acceptance record. Stage 2, Step 4a,
Step 4b, precompletion, and completion consume the same canonical obligations,
executed proof, and independent review history through
[`gz obpi acceptance`](../user/manpages/obpi-acceptance.md).

## Authority and execution

The brief and parent ADR supply the approved obligation population and contract
digest. BEHAVIOR retains its covering-test channel; SUPPORT retains its ledger
and validator channel; STRUCTURAL-FENCE retains its parent-invariant channel.
Initializing the record does not invent acceptance requirements or authorize OBPI
work. The operator's initiation and completion attestation remain required.

The ledger-vocabulary hook can verify a registered producer through fresh
isolated execution before its first authorized use in the project. It checks
the typed persisted record against the probe's expected contract and reports
the observation separately from live counts. A cached report cannot grant
credit, and the probe does not write the project's live ledger (operator ruling
2026-09-08, GHI #985).

Proof records contain exact executed payloads and their input identities. For
BEHAVIOR, the execution producer observes baseline execution, actual production
substitutions, named assertion failures, restoration, and restored green tests.
Import failures and runtime errors cannot stand in for behavioral sensitivity.
Canonical resolvers produce the other proof kinds. Independent review still
determines whether the observations demonstrate the required semantics.

The configured ledger retains contract, proof, and review records. Readiness is
a derived view rebuilt from that history against current canon and inputs. ARB
review ingestion takes the structured judgment from the actual agent execution's
captured output. Receipt provenance and subject binding constrain interpretation;
they do not cryptographically authenticate the human or agent behind a name.

## Findings retain their subject

A finding names its stable identity, canonical obligation, and concrete
counterexample or missing proof. Severity does not discharge a mapped obligation.
Auxiliary observations have no obligation binding and do not independently create
acceptance prerequisites. A required-proof defect discovered by an optional
diagnostic remains mapped even if the diagnostic is later removed.

The resulting lifecycle is:

```text
open finding → repaired proof → independent closure against that proof
```

A closure references the original finding, original obligation, and current proof.
Changing a finding's identity or obligation cannot launder its history. A repaired
test plus a later general approval leaves the original finding open until closure
is recorded. A new concrete report of the same finding can reopen it.

Reviews explicitly name which proofs they approve. Historical verdict words do
not silently grant or revoke approval. The earlier Markdown standing-verdict
convention remains readable history; it no longer owns current acceptance state.

## Tracking corrections during implementation

An operator-initiated OBPI owns corrections necessary to satisfy its approved
obligations. Keep implementation, test, documentation, and evidence adjustments
in `### Change Log` under the brief's `## Evidence` section. Cite the existing
finding identity when present, affected REQ or contract clause, change, and
proof/independent-closure references. Group related repairs and link execution
artifacts; do not duplicate transcripts or introduce another finding roster.

This log is an index for readers, not acceptance authority. The existing ledger
still owns proof and closure. History edits alone do not create another review
obligation; an actual counterexample against required behavior or proof does.
Normative amendments remain in the relevant contract sections with the existing
operator ruling, referenced from the log. An unmet obligation cannot be moved
into history to make it disappear.

Create a GHI only for an independent work order or disposition, or an explicit
operator request. Separate infrastructure defects and post-acceptance defects
can need issues; routine corrections within the active OBPI do not. Filing an
issue never discharges required work. See
[defect-fix routing](defect-fix-routing.md#corrections-within-an-active-obpi).

## Advancement and invalidation

Intermediate task review uses the task's Stage-2 obligation scope while retaining
the complete canonical roster and history. Leaving implementation requires the
complete population to have valid current proof and independent spec and quality
approval. Step 4b adds adversarial approval and explicit independent closure of
mapped findings before attestation is solicited. Quality gates remain required.

The Step-4a producer checks Stage-2 proof readiness and reports Step-4b review
blockers separately. This permits generating the packet that the independent
reviewer needs before that review has run. A review-ready packet can exit zero
with `attestable` false. Final Stage-4 validation and ceremony require both proof
and review blockers to be clear; packet generation alone cannot authorize
soliciting attestation.

The existing ledger-backed single-driver declaration omits Stage-2 spec/quality
channels, while retaining executed proof, open findings, and Step-4b review.
The runtime derives review tier from the execution. A native Claude adversarial
fallback requires its observed cross-vendor unavailability; a human degraded
review requires the operator's explicit verbatim judgment of current proof and
findings. General implementation permission authorizes neither a human review
nor completion attestation.

Freshness is conservative: source, test, configuration, contract, and environment
changes can invalidate the complete proof population. Source bytes distinguish
different dirty trees at the same HEAD. Appending evidence records or editing
recognized history sections alone does not invalidate executable proof. Unknown
contract sections remain included, and live non-BEHAVIOR resolvers run again.

New proof identity invalidates previous review approvals and closures even if its
input digest matches. Thus a repaired artifact cannot inherit an earlier review
silently. Schema validity proves neither oracle independence nor comprehensive
requirement fulfillment; those judgments remain explicit independent review work.

## Existing work and recovery

An older pipeline with only prose verdicts and legacy receipts has no synthetic
acceptance credit. Within the operator-initiated run, initialize the canonical
population, produce current execution proof, and obtain structured independent
reviews. Preserve historical reports and their real findings; do not relabel
optional corpus diagnostics as new requirements or edit unrelated live briefs.

The CLI has no roster-reset shortcut. A changed requirement population is surfaced
as a contract mismatch; it requires the existing operator-governed amendment
process. Reinitialization cannot erase outstanding findings. GHI repairs remain
authorized direct corrective work rather than grounds to invent another ADR or
OBPI ceremony.
