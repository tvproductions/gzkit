# gz obpi dispatch

Record a Stage-2 subagent dispatch, or declare a single-driver run.

## Usage

```
gz obpi dispatch OBPI-X.Y.Z-NN --role ROLE --model MODEL [--task N]
gz obpi dispatch OBPI-X.Y.Z-NN --single-driver --reason "TEXT"
gz obpi dispatch OBPI-X.Y.Z-NN
```

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier with an active pipeline marker |
| `--role ROLE` | Mandated Stage-2 role: `Implementer`, `SpecReviewer`, or `QualityReviewer` |
| `--model MODEL` | Model tier used for the dispatch |
| `--task N` | 1-based task index (default: 1) |
| `--single-driver` | Declare this run knowingly single-driver (requires `--reason`) |
| `--reason TEXT` | Why the mandated dispatch could not run |

Invoked with no flags, the command prints the current dispatch channel without
changing it.

## Runtime Behavior

- Appends a `stage2_dispatch_recorded` event to `.gzkit/ledger.jsonl`, which is
  what `gz obpi precomplete` credits at Stage 5. The active pipeline marker's
  `dispatch_state` is refreshed too, but only as a cache `gz roles` reads — no
  verdict consults it (GHI #886)
- Prints the full mandated roster after every invocation, including roles that
  have not been dispatched
- **Credit is never inferred.** A role reports `DISPATCHED` only when a record
  says so. It is never derived from the presence of code, tests, or a completed
  stage — that inference is what made a properly dispatched run and an inline
  one byte-indistinguishable (GHI #845)
- **Partial dispatch is still `SINGLE-DRIVER`.** The two reviewers exist to
  catch what the implementer cannot see in its own work, so crediting the
  implementer alone would launder the review that never happened

## Declared vs. silent single-driver

`--single-driver` is the compliant path for a session that genuinely cannot
dispatch — a cron run, a harness without an Agent tool, an operator instruction
forbidding subagents. The declaration and its reason are recorded as a
`stage2_single_driver_declared` ledger event and rendered in the channel.

Declared single-driver **passes** `gz obpi precomplete`. Silent single-driver
does not. A gate with no compliant path for a dispatch-less session is
un-compliable, and an un-compliable gate gets worked around rather than obeyed.

## Why the ledger, not the marker

Both facts this command records are **Layer-2 evidence** (GHI #886). `ADR-0.0.9`
names pipeline markers Layer 3 and its Rule 5 states the consequence: *"Layer 3
artifacts cannot block gates. Only L1 (canon) and L2 (events) can be gate
evidence."*

Measured on `OBPI-0.35.0-02`, 2026-08-26: a run that dispatched 3/3 across two
tasks had its credit destroyed by `gz obpi pipeline --clear-stale` — the
sanctioned recovery path, not misuse — and Stage 5 then reported 0 of 3 against a
run that had complied. Because the channel never infers credit (correctly), the
loss was unrecoverable except by a prose declaration asserting the lost fact.

Two consequences worth knowing at the command line:

- Dispatch credit and a single-driver declaration both **survive** clearing the
  marker and relaunching the pipeline.
- Hand-writing `dispatch_state` or `single_driver_declaration` into a marker file
  buys **nothing**. Only this command's ledger events are credited.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Dispatch recorded, declaration written, or channel rendered |
| 1 | No active pipeline marker, unknown role, or `--single-driver` without `--reason` |
| 2 | System error |

## Examples

```bash
gz obpi dispatch OBPI-0.1.0-01 --role Implementer --model sonnet --task 1
gz obpi dispatch OBPI-0.1.0-01 --role SpecReviewer --model opus --task 2
gz obpi dispatch OBPI-0.1.0-01 --single-driver --reason "cron run, no Agent tool"
gz obpi dispatch OBPI-0.1.0-01
```

## See Also

- [`gz obpi pipeline`](obpi-pipeline.md) — the ceremony whose Stage 2 makes the dispatch
- [`gz roles`](roles.md) — display dispatch history for a pipeline run
