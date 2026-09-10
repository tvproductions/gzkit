# gz obpi acceptance

Execute requirement proof, import independent review output, and derive acceptance
readiness from retained obligations and findings.

---

## Usage

```bash
gz obpi acceptance <OBPI-ID> init --author <implementing-session-id>
gz obpi acceptance <OBPI-ID> prove --spec <controls.json>
gz obpi acceptance <OBPI-ID> review --receipt <arb-run-id>
gz obpi acceptance <OBPI-ID> human-review --attestor g0 --ruling '<operator verbatim review>'
gz obpi acceptance <OBPI-ID> status --stage stage2 --json
gz obpi acceptance <OBPI-ID> status --stage stage2 --req <REQ-ID> --json
gz obpi acceptance <OBPI-ID> status --stage stage4 --json
```

Use these commands within an operator-initiated OBPI pipeline. They do not
authorize starting an OBPI or completing it without human attestation.

## Runtime Behavior

`init` captures the canonical obligation population and implementing session in
the configured ledger. Repeating the same initialization is idempotent; a changed
author or roster cannot replace the existing contract and erase its findings.

`prove` executes a requirement's proof channel and records its observed result,
including unsuccessful controls. The specification supplies instructions, never
an authored test outcome. For BEHAVIOR requirements it runs the selected covering
tests, applies each exact production substitution, observes nominated assertion
failures, restores the source, and runs the restored baseline. Runtime errors,
skipped selectors, absent substitutions, and unchanged source do not demonstrate
behavioral sensitivity. SUPPORT and STRUCTURAL-FENCE use their existing canonical
resolvers and require no mutation specification.

`review` reads the identified ARB receipt and imports exactly one
`gzkit.acceptance.review.v1` object from its actual execution output. The receipt
must record a successful recognized agent invocation. Printing a separately
authored JSON file is not a review execution. The importer assigns review identity
from the receipt; the CLI accepts no separate result file or verdict override.

`status` returns readiness plus its blockers, retained open finding IDs, current
input digest, contract, proof history, and review history. Stage 2 requires spec
and quality approval; Stage 4 additionally requires adversarial approval. Repeat
`--req` to inspect an intermediate task's Stage-2 obligations. Final Stage-2
advancement and Stage 4 require the complete canonical population.

Mapped findings remain blocking until an independent review explicitly closes
their original identity against current proof. A new proof supersedes previous
approvals and closure unless it is a consecutive successful execution with the
same explicitly witnessed claim. Claim identity includes the specification,
controls, observed results, declared execution conditions, contract, and artifact
identity. A new UUID alone does not invalidate approval. Legacy proofs without
claim identity retain exact-ID behavior. A failed execution breaks reuse, including
when followed by another successful execution. Removing auxiliary
commentary cannot remove a mapped finding. Historical verdict prose cannot
substitute for current readiness.

Well-formed delayed reviews of a known historical subject are retained, including
mapped findings, but their approvals apply only to their reviewed proof claim.
An identical finding repeated against an older proof preserves a newer verified
closure. A counterexample against the current proof still reopens acceptance.
Each review's position in the ledger fixes which proofs were current when it was
recorded. A later equivalent execution cannot erase that counterexample. This
position is reconstructed on replay; reviewer receipts remain unchanged.

## Proof Specification

This illustrative specification describes a threshold boundary control. Replace
its identifiers and exact source text with the canonical requirement and inspected
production source for the work being reviewed:

```json
{
  "req_id": "REQ-X.Y.Z-NN-01",
  "source": "src/example/limits.py",
  "selectors": ["tests.test_limits.TestLimit.test_exact_limit_is_rejected"],
  "mutations": [
    {
      "label": "allow-exact-limit",
      "find": "return total >= limit",
      "replace": "return total > limit",
      "expected_tests": ["tests.test_limits.TestLimit.test_exact_limit_is_rejected"]
    }
  ]
}
```

All selectors must be fully qualified covering unittest IDs for the nominated
requirement. Each mutation must nominate selected test IDs. Its source must be a
Python production file inside the configured source root. A non-BEHAVIOR request
requires only its `req_id`.

An optional `environment_keys` array names environment variables necessary to a
particular proof claim. Their values are hashed, never printed or persisted.
Execution and readiness both check these explicitly declared conditions. Ambient
variables outside this list do not change artifact identity or approval.

## Review Output Contract

Give the independent reviewer the actual `status --json` result, relevant source,
tests, contract, and proof payloads. It emits the following shape in its executed
output, using real identities from that context. This is a schema example, not a
claim that a review ran:

```json
{
  "schema": "gzkit.acceptance.review.v1",
  "stage": "spec",
  "input_digest": "<current input digest>",
  "obligation_ids": ["<reviewed obligation ID>"],
  "proof_ids": ["<reviewed proof ID>"],
  "accepted_proof_ids": ["<independently approved proof ID>"],
  "findings": [],
  "closures": [],
  "reviewer_id": "<independent reviewing session>",
  "verdict": "accepted"
}
```

An adversarial review that replayed the proof rather than only reading it adds a
`replay` array. Each record names `obligation_id`, `proof_id`, the
`workspace_digest` of the disposable checkout it ran in (see
[adversary workspace](obpi-adversary-workspace.md)), the executed `selectors`, the
`mutation_label` applied, three runs (`baseline`, `mutated`, `restored`, each with
`exit_status`, `tests_run` and `output_tail`), and `source_digest_before` /
`source_digest_after` around the edit.

Ingestion refuses a replay claim the record does not support: a baseline that was
not green, a mutated run whose failure class is `error` rather than `assertion`, a
selector that executed zero tests, a record carrying no substitution, a source not
restored byte-identically, or a digest naming a tree other than the one under
review. An execution error, a skipped check, and a merely inspected record are
never independent replay. Omitting the block claims nothing and is accepted; only
a claim is checked (GHI #961).

`stage` is `spec`, `quality`, or `adversarial`. Explicit proof approvals govern
readiness; the `accepted`/`refuted` verdict remains review history and does not
author the approved set. A reviewer must not emit `id` or `receipt_id`: ingestion
derives both from the executed receipt.

The pipeline composers validate the supplied status context before dispatch and
generate the response schema from the same `ReviewResponse` model used by the
importer. Context includes the captured input components, requested obligation
scope, proof history, and open finding IDs. Missing or contradictory context is a
local error. The reviewer owns approvals and closure judgments; a generated
example supplies neither. The legacy `ReviewResult` is a separate envelope:
`verification_gaps` belongs there, and `description` belongs to findings, never
closures. Formatting repair uses a fresh invocation that references the original
receipt and preserves its subject and substantive judgment; receipts are not edited.

Each finding contains `id`, `obligation_id`, `kind` (`counterexample` or
`missing-proof`), and `description`. Auxiliary observations use a null obligation;
a real requirement defect discovered through an auxiliary audit remains mapped.
Every verified closure names `finding_id`, `obligation_id`, and the current
`proof_id`. A later approval without that closure cannot erase an open finding.
When the required proof is missing, retain the obligation in `obligation_ids`,
leave its proof and approval lists empty, and record the mapped `missing-proof`
finding. Missing evidence is a recordable review outcome, not a reason to invent
a proof ID or leave the finding outside the ledger.

Wrap the actual reviewer invocation in `gz arb step --max-output-chars -1` to
retain the complete structured output. Import its resulting run ID with `review`.
Stage-2 native Claude reviewers are supported; Step 4b follows the pipeline's
binding vendor and fallback rules. An execution receipt establishes captured
producer/output provenance, not cryptographic authentication of reviewer identity.

For an adversarial native Claude fallback, the reviewer output must also include
`fallback_reason` naming the observed cross-vendor unavailability. Stage-2 native
Claude review needs no fallback reason. The runtime derives the tier from the
executed command; reviewers must not supply `tier` themselves. The pipeline's
tier order and availability checks still apply.

`human-review` is the existing degraded human floor. Invoke it only after the
operator explicitly judges the displayed current proof and outstanding findings;
pass their exact words through `--ruling` and record their identity as `g0`.
The command approves current proof and closes the displayed mapped findings as
that human judgment, recording tier 3 without fabricating an agent receipt.
General permission to repair or implement is not this ruling. It does not replace
the operator's separate completion attestation.

A ledger-backed single-driver declaration preserves the existing implementation
fallback: it removes the Stage-2 spec/quality channel requirement, while Stage 4
still requires adversarial approval. Valid executed proof and open finding closure
remain mandatory. A pipeline marker or an unrecorded claim cannot grant this mode.

## Freshness and Limits

The input digest conservatively covers the canonical contract, configured source
and tests, features, data, scripts, rules, schemas, workflow configuration, selected
project configuration files. It excludes process environment, interpreter, and
platform provenance. Explicitly declared execution dependencies belong to the
proof claim and are checked separately.
An unrelated change within this broad population can require fresh proof and
review. This is not dependency-minimal invalidation.

Explicit evidence/history sections are excluded from the normative contract
digest; unknown sections remain included conservatively. Ledger and receipts are
excluded to permit appending execution history. Non-BEHAVIOR proof resolvers run
again during readiness evaluation.

Mechanical validity does not establish that a test oracle or mutation expresses
the requirement. Independent reviewers must assess that meaning and legitimate
positive behavior against the observed records. No mutation count or receipt
presence check supplies that judgment.

Completion retains the necessary scoped approvals and explicit closure reviews
through `acceptance_review_ids` on the completion's adversarial-validation event.
Each ID resolves to immutable acceptance history with its actual receipt and tier.
The summary tier reflects the most degraded necessary adversarial review; a later
unrelated review cannot replace the required provenance set.

## Example

Observed help output, abridged from `uv run gz obpi acceptance --help`:

```text
Execute requirement controls, record independent reviews, and derive readiness.

positional arguments:
  obpi                  Canonical OBPI identifier
  {init,prove,review,human-review,status}
```

## Exit Codes

- `0`: initialization or review import succeeded, proof was valid, or requested
  readiness is satisfied.
- `3`: proof/readiness is blocked or the acceptance command rejects the request.

A successful review import can record a refutation. Run `status` to determine
readiness; importing a review is not itself approval.

The separate [`present-evidence`](obpi-present-evidence.md) command can generate
Step-4a review input after Stage-2 proof is ready, while Step-4b closure remains
pending. Its exit `0` means the packet can be reviewed; the packet's `attestable`
field remains false until proof and review conditions both clear. Acceptance
`status --stage stage4` continues to exit `3` while that review is outstanding.

## See Also

- [OBPI pipeline skill](../skills/gz-obpi-pipeline.md)
- [Acceptance obligations and closure](../../governance/acceptance-obligations.md)
- [OBPI status](obpi-status.md)
