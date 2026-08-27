# gz obpi block

Record that an OBPI is waiting on an operator ruling.

## Usage

```bash
gz obpi block OBPI-<X.Y.Z-NN> --reason "..." --next-action "..."
gz obpi block OBPI-<X.Y.Z-NN> --reason "..." --next-action "..." --dry-run
```

## Description

Records an `obpi_blocked_on_operator` event in the ledger, declaring that the
OBPI's next legitimate action belongs to a human rather than to an agent.
While the block stands, `gz obpi pipeline` refuses to launch against the OBPI
and `gz obpi precomplete` reports the block instead of `READY`.

**Why this exists (GHI #887).** The pipeline had no state meaning "waiting on a
human", so an agent that correctly identified a blocking operator decision — a
REQ amendment under attestation, a Denied-Path collision, a conflicting-canon
ruling — could only write it into a handoff and keep working the surrounding
surface. Measured on `OBPI-0.35.0-02`: 21 `red_receipt_emitted`, 10
`task_started`, zero `task_completed`, four `pipeline_launched` and three
adversary rounds in the 24 hours after the brief became structurally
uncompletable. The loop's only terminator was the operator noticing.

**Reversible and unattested.** A block is not a disposition. It states that a
decision is owed, not that work ended, and `gz obpi unblock` clears it. It
requires no attestor: requiring a human to authorize the statement *"a human is
needed"* would reproduce the deadlock it exists to break. Contrast
`gz obpi withdraw` (permanent, one-way, attested); and the `obpi_parked` event,
whose `parked_to` names the pool id a parent ADR became — here the parent is live.

**Layer 2, not the marker.** The block is a ledger event because ADR-0.0.9
Rule 5 is verbatim that *"Layer 3 artifacts cannot block gates. Only L1 (canon)
and L2 (events) can be gate evidence."* The pipeline marker's
`required_human_action` key is Layer 3 and cannot carry a gate.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `obpi` | Yes | OBPI identifier (e.g. OBPI-0.35.0-02) |

## Flags

| Flag | Description |
|------|-------------|
| `--reason` | Why the OBPI cannot proceed without a human (non-empty) |
| `--next-action` | The concrete decision the operator owes (non-empty) |
| `--dry-run` | Show the event without writing it |
| `--quiet` | Suppress non-error output |
| `--verbose` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

`--next-action` is required, not optional politeness. A block naming only a
reason records a complaint; naming the awaited action is what lets a reader
other than its author discharge it.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error (unknown OBPI, empty reason or next-action) |

## Examples

```bash
# Block on a REQ amendment that only a human can make
uv run gz obpi block OBPI-0.35.0-02 \
  --reason "REQ-04 says the retired row stays verbatim; the counterexample test asserts the opposite" \
  --next-action "amend REQ-04 under attestation, or change persistence to append without reserializing"

# Preview the event without writing it
uv run gz obpi block OBPI-0.35.0-02 --reason "..." --next-action "..." --dry-run
```

## See Also

- [`obpi-unblock`](obpi-unblock.md) — record the ruling and release the block
- [`obpi-pipeline`](obpi-pipeline.md) — the launch surface the block gates
- [`obpi-precomplete`](obpi-precomplete.md) — surfaces the block as a precondition
- [`obpi-withdraw`](obpi-withdraw.md) — permanent, attested retirement
