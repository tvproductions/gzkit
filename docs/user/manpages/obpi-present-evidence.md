# gz obpi present-evidence

Generate the Step-4a evidence packet for independent review and the eventual
human acceptance ceremony.

---

## Usage

```bash
gz obpi present-evidence <OBPI-ID> [--json]
```

## Runtime Behavior

The command executes the brief's `## Demo` commands, reads canonical ARB receipts,
runs `gz covers`, and checks current Stage-2 acceptance proof. It writes the
result to `.gzkit/evidence/<OBPI-ID>.evidence.json` and displays it as text or JSON.

Step 4a supplies evidence to Step 4b. The independent review therefore need not
have completed before this command can prepare its input. The packet separates:

| Field | Meaning |
|-------|---------|
| `blockers` | Demo, receipt, coverage, or current Stage-2 acceptance conditions that prevent proof readiness |
| `review_blockers` | Current acceptance conditions still preventing Step-4b closure and attestation |
| `attestable` | True only when both blocker lists are empty |

When proof is ready and independent closure is pending, the command exits `0`,
keeps `attestable` false, and the human rendering reports that Step-4b closure is
pending. Give the generated packet and current acceptance records to the
independent reviewer; do not solicit attestation at this point.

After importing the review and any necessary independent finding closure,
regenerate the packet. Final Stage-4 validation checks both blocker lists against
current inputs. The pipeline prepares review evidence when only Step 4b remains,
and requests the acceptance ceremony only after the required proof and review
conditions clear.

An exit-zero packet-generation command is not an acceptance approval. Nor does
transcript reproduction establish the semantic adequacy of a test oracle; that
judgment remains with independent review.

## Example

Inspect the command without executing a live brief's Demo:

```bash
uv run gz obpi present-evidence --help
```

Observed positional-argument output, abridged:

```text
positional arguments:
  obpi           OBPI identifier (e.g. OBPI-0.0.74-16)
```

For an initiated OBPI, generate its review input using its canonical identifier:

```bash
uv run gz obpi present-evidence <OBPI-ID> --json
```

Inspect `blockers`, `review_blockers`, and `attestable`; the exit code alone does
not distinguish a review-ready packet from one ready for attestation.

## Exit Codes

- `0`: the Step-4a proof conditions are satisfied and the packet was generated;
  independent Step-4b review may still be pending.
- `1`: the canonical brief could not be resolved.
- `3`: one or more proof blockers remain.

## See Also

- [Acceptance proof and review records](obpi-acceptance.md)
- [OBPI pipeline skill](../skills/gz-obpi-pipeline.md)
- [Acceptance obligations](../../governance/acceptance-obligations.md)
