# gz canary review

Record the operator's review of one or more guard mutation canaries as
`guard_canary_reviewed` ledger events.

## Usage

```bash
gz canary review --claim <claim-id>... --attestor <id> --operator-text "<words>" [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--claim` | Claim id whose canary was reviewed. Repeatable; required |
| `--operator-text` | The operator's verbatim review words. Required |
| `--attestor` | Operator identity that reviewed. Required and never defaulted: this is a human-act verb under the GHI #1036 ruling |
| `--ruling-source` | Where the words were first recorded, when the review is booked after the fact |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

A guard canary (`data/guard_canaries.json`) binds one reviewed mutant to one
registered enforcement claim. The operator reviews the mutant; this verb
records that review.

Each claim gets one `guard_canary_reviewed` event carrying the operator's
verbatim words, the attestor, and the binding the operator reviewed
(`binding_sha256`). `reviewed_by` in the registry is written as a readable
projection.

**The event is the only witness.** A canary counts as reviewed only when the
ledger holds a `guard_canary_reviewed` event at the canary's *current* binding
(`gzkit.guard_canary.unreviewed`, which session orientation also calls). A
hand-edited `reviewed_by` does not count. When a canary is rebound because its
guard, claim or designated test changed, the old review no longer matches, and
the canary waits for a fresh review.

Every input is checked before anything is written. A refusal leaves the ledger
and the registry untouched:

- empty words, an empty attestor, or a claim with no canary exits 1;
- a stale binding exits 3, because a review now would accept a mutant against
  a guard nobody re-read.

Session orientation lists the canaries still awaiting review.

## Examples

Book a review given earlier in the session, citing the commit that first
recorded the words:

```bash
gz canary review --claim arb-receipt-red-run-refused --claim validate-json-exit-classified \
  --claim support-citation-declared-only --claim pointer-back-pointer-matched \
  --claim pointer-reverse-arm-orphan-refused --claim tidy-breach-exits-three \
  --claim waiver-identity-new-entry-refused \
  --attestor g0 --operator-text "accept all 8" --ruling-source 7f1ace88f
```

```text
Recorded the operator's review of 7 canaries:
  arb-receipt-red-run-refused
  validate-json-exit-classified
  support-citation-declared-only
  pointer-back-pointer-matched
  pointer-reverse-arm-orphan-refused
  tidy-breach-exits-three
  waiver-identity-new-entry-refused
```

Machine-readable output:

```bash
gz canary review --claim gate-enrollment --claim gate-enrollment-disclosed \
  --attestor g0 --operator-text "a" --ruling-source b00cef943 --json
```

```json
{"status": "reviewed", "claims": ["gate-enrollment", "gate-enrollment-disclosed"], "attestor": "g0"}
```

The event that run appended for one claim:

```json
{"schema":"gzkit.ledger.v1","event":"guard_canary_reviewed","id":"gate-enrollment-disclosed","ts":"2026-10-03T00:50:26.736000+00:00","binding_sha256":"71a986bc929039836a8509c71c6b2bc58ab463b776e21938cdd914446b6083f8","attestor":"g0","operator_text":"a","ruling_source":"b00cef943"}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Empty words or attestor, or a claim with no canary; nothing written |
| 2 | Usage error (a required flag missing) |
| 3 | Policy breach: a binding is stale; nothing written |

## See Also

- [`gz arb red`](arb-red.md): witness a test failing without the code it covers
- [`gz handoff decide`](handoff-decide.md): the same verbatim-words pattern for handoff rulings
