# gz wp block

Record that a work package awaits the operator.

## Usage

```bash
gz wp block <WP-id> --reason <text> --next-action <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--reason` | Why the package cannot proceed. Required |
| `--next-action` | The decision the operator owes. Required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The verb books one `work_package_blocked` event. The runtime writes the facts into
it from the ledger: each subject's fix cycles, the bound, the subjects newly at the
bound, the subjects a hold left open, the exits the package has used, and any baseline REQ already reopened in
any package. An escalation may carry the agent's recommendation, and these
facts sit beside it. A blocked package takes no dispatch until `gz wp unblock`.

## Examples

Observed in a scratch project holding `WP-01-loop`, with `#1200` at the bound:

```console
$ uv run gz wp block WP-01-loop --reason "REQ refuted again" --next-action "rule on the exit"
Blocked WP-01-loop on the operator: rule on the exit
  fix cycles (bound 2): #1200: 2
  at the bound: #1200
  held: none
  exits used: none
  reopened: none
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The block was booked |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | The block is refused: the package is not live, is already blocked, or a field is empty |

## See also

[`gz wp dispatch`](wp-dispatch.md), [`gz wp unblock`](wp-unblock.md)
