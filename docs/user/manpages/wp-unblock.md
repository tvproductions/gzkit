# gz wp unblock

Record the operator's ruling on a blocked work package and clear the block.

## Usage

```bash
gz wp unblock <WP-id> --ruling <text> --operator <who> [--exit <exit>] [--req <REQ>] [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--ruling` | The operator's decision, verbatim. Required |
| `--operator` | Who ruled, never defaulted. Required |
| `--exit` | `reopen`, `departure`, `hold` or `terminate`. Required at the bound |
| `--req` | The REQ a `reopen` or `departure` names, from the frozen baseline |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The verb books one `work_package_unblocked` event. A block with no subject newly at
the bound clears on the ruling alone, and an exit there is refused unless a held
subject is open to one. A block with
one names one exit, and no exit opens a further repair cycle:

| Exit | Meaning |
|------|---------|
| `reopen` | The REQ at the bound changes through a reopening, which takes a new package. Usable once per requirement, across packages. The package takes no further repair |
| `departure` | A bounded claim on the REQ at the bound, a waiver recorded through `gz wp change --rung departure` since the block. The package carries on; the REQ takes no further repair |
| `hold` | The block clears; the subjects at the bound take no further repair, other subjects continue, and a held subject stays open to a later exit |
| `terminate` | The package takes no further repair and closes through Gate 5 (`gz wp close --decision terminate`) |

The exit names the act and does not perform it. A requirement that reaches the
bound again after a reopening has only `departure`, `hold` and `terminate`.

## Examples

Observed in a scratch project holding `WP-01-loop`, blocked with `#1200` at
the bound:

```console
$ uv run gz wp unblock WP-01-loop --ruling "again" --operator g0
#1200 at the bound; name an exit: reopen, departure, hold, terminate.
$ uv run gz wp unblock WP-01-loop --ruling "hold it" --operator g0 --exit hold
Unblocked WP-01-loop by exit hold.
$ uv run gz wp dispatch WP-01-loop --role Implementer --model sonnet --issue 1200
#1200 has used the bound of 2 fix cycles; no further repair cycle runs. Block
and take an exit: reopen, departure, hold, terminate.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The ruling was booked and the block cleared |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | The unblock is refused; nothing was booked |

## See also

[`gz wp block`](wp-block.md), [`gz wp dispatch`](wp-dispatch.md),
[`gz wp change`](wp-change.md), [`gz wp close`](wp-close.md)
