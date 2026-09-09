# GHI #985 acceptance-action evaluation

Date: 2026-09-09. These are disposable infrastructure trials, not live OBPI
execution, human attestation, or an estimate of review time saved.

## Method and preserved evidence

Starting from the [GHI #984 scenario work](obpi-review-984-evaluation.md), four
cases each ran twice with old context and twice with candidate context: sixteen
fresh native Claude CLI invocations. Every invocation requested and reported
`claude-opus-5`, with explicitly requested effort `xhigh`. The CLI was version
2.1.266. The prompt was the first positional argument, followed by identical
model, effort, output, session and tool options. Separate temporary directories
allowed fixture-only writes; no concurrent writer touched the governed checkout.

The compared contexts are four exact relevant pipeline-skill excerpts: the
rationalization table, attestation barrier, closure/repair instructions, and
checkout coordination. They are a bounded sample of delivered instructions,
not the entire root contract, skill, or another vendor's delivery. Paired trials
received the same task, source, tests, canonical requirement, actual executed
proof, and synthetic seeded review history. Input identity matched before and
after all sixteen trials. The acceptance runtime used by their consumer was
unchanged during execution.

Each model had Read, Glob, Grep and Write. It had to inspect the fixture and
write its actual acceptance disposition. Where it produced `review.json`, the
controller imported those unedited bytes through a disclosed synthetic receipt
into the real fixture store and reloaded readiness. Model tool traces and written
files, rather than final prose alone, establish the reported actions. This is an
artifact-producing coordination sample, not an actual adversarial-tier dispatch.

- [Observations and actual model dispositions](obpi-review-985/observations.json)
- [Original CLI streams and written files, losslessly compressed](obpi-review-985/actual-cli-traces.jsonl.gz)
- [Identical paired fixture inputs](obpi-review-985/fixtures.json)
- [Runtime source fingerprints](obpi-review-985/runtime-snapshot.json)
- [Executed evaluation harness](obpi-review-985/evaluation-harness.txt)
- [Old context](obpi-review-985/old-delivered-context.json)
- [Sampled candidate context](obpi-review-985/candidate-delivered-context.json)

The context JSON containers preserve the exact delivered text and its SHA-256,
including trailing newlines, without requiring raw evidence to violate repository
end-of-file formatting. Every trial context hash matches its container.

The compressed stream contains one JSON object per trial with `stdout`, `stderr`,
and original model-written files. This preserves the native stream rather than
substituting the controller's interpretation for reviewer output.

## Observed actions

| Case | Old, trials 1 and 2 | Candidate, trials 1 and 2 | Real consumer result |
|---|---|---|---|
| Invalid required RED: a TypeError is presented as a behavioral kill | Both write repair-required and a mapped missing-proof review | Both write repair-required; trial 1 writes a review, trial 2 retains the existing invalid-proof blocker | All remain blocked; no invalid proof earns approval |
| Corrected state: independent closure followed by equivalent successful execution | Both write request-attestation and retain three approvals plus the historical refutation | Both write request-attestation and retain the three applicable approval IDs | All remain ready with no open finding; no new review is manufactured |
| Auxiliary naming commentary, no unmet obligation | Both write request-attestation and preserve required approvals | Both write request-attestation and preserve required approvals | All remain ready; no implementation or review obligation is invented |
| Auxiliary diagnostic exposes a required shared-oracle gap | Both write repair-required and retain the existing finding | Both write repair-required and retain the existing finding | All retain `F-required-oracle` and remain blocked |

The invalid-RED candidate trial 2 deliberately omitted a new finding because
the invalid proof already durably blocked the same obligation. Its disposition
examined the actual TypeError and lack of assertion comparison. The trial task
asked for a review on a newly established gap but also forbade manufactured
review; whether an existing proof blocker needed a duplicate finding was not
settled by that task. Rejection is demonstrated; new-finding capture is not
demonstrated in that trial. This is neither acceptance of bad proof nor loss of
an existing finding, and it does not justify a blanket finding-per-proof-error rule.
The auxiliary-required-gap case directly demonstrates existing finding retention.

In the positive cases, tool traces show source/test/brief/evidence inspection.
The dispositions distinguish the literal expected value, actual assertion kill,
source restoration, unchanged claim identity and applicable review IDs. Their
claim is therefore narrower and better witnessed than merely echoing `ready=true`.
The controller still does not perform a live human-facing ceremony on their behalf.

## Instruction and delivery disposition

The [sampled delta](obpi-review-985/candidate.diff) removes contradictory
same-turn freshness and raw-verdict repair commands, and states one writer per
checkout. Independent inspection found that its barrier heading still repeated
the old turn command. The [final proposal](obpi-review-985/proposed-final.diff)
also corrects that heading and bumps the skill version. It is now applied to the
canonical pipeline skill following the operator's source-authoring ruling. Those final heading and
metadata edits were not part of this sixteen-trial sample. The runtime and
sampled substantive repair instructions were unchanged by that inspection.
The final proposal adds 317 characters to the complete skill: explicit current
proof applicability and checkout coordination replace shorter but contradictory
turn and parallel-session commands. That increase carries required distinctions;
it adds no stage, proof census, or mandatory extra review.

The [source-authoring proposal](obpi-review-985/source-authoring-proposal.txt)
was accepted with the operator's September 9 correction, verbatim:
"skills are not corpus constructed. only agents/claude and rules."
Skills are not awaiting corpus migration. The owning substrate documentation now
distinguishes content models from corpus construction; canonical skill files
remain the authoring source for vendor and package copies. The original proposal
is preserved beneath its disposition; its enrollment/migration premise is
superseded, while the remaining provisions are accepted.

Actual synchronization delivered version 6.54.0 to canonical, Claude, Codex and
packaged skill files. All four share SHA-256
`595f983479eb6c178ca1c6d61837c83872474ef7ec78f651f76096320e9c8d16`.
`uv run gz validate --surfaces --distribution` passed both scopes. Delivery is
verified separately from the behavioral sample; final source-authoring wording
was not part of those sixteen trials.

## Result and limits

The selected cases preserve required rejection, existing finding retention and
legitimate advancement under both contexts. **No behavioral improvement over the
old context is demonstrated.** The proposed changes resolve concrete contradictory
instructions; these sixteen observations do not predict future review counts or
establish cross-harness compliance. Seeded reviews and import transport are
synthetic, while proof execution, model tool actions and the store consumer are
real. Only the separate actual native spec-review handoff exercises an unedited
model response through an actual ARB transport receipt.

Deterministic acceptance regressions and the real process/ceremony BDD remain
the runtime correctness evidence. This small agent sample cannot waive those
checks, required independent reviews, or human completion attestation.
