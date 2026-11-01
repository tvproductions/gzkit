# gz wp withdraw-legacy

Withdraw a legacy unit, permanently, on a human witness. The successor to `gz obpi withdraw`, accepting legacy ids.

## Usage

```bash
gz wp withdraw-legacy <OBPI-id> --reason <text> --attestor <human> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `OBPI-id` | The legacy unit's full id, slug included, as the ledger holds it. Required |
| `--reason` | Why, and where its REQs went. Required, non-empty |
| `--attestor` | The human witness, never defaulted. Required, non-empty |
| `--dry-run` | Show the event without booking it |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Books one `legacy_unit_withdrawn` event. The withdrawal is one-way, and the unit stays
in the ledger for audit history. A unit withdrawn here reads as withdrawn everywhere a
unit withdrawn by `gz obpi withdraw` does: the artifact graph, `gz state`, run
position and the closeout proof. The two verbs share one rule, so a unit already
withdrawn or superseded through either is refused by both.

RO-8 runs this verb on the operator's word to withdraw legacy briefs as superseded. See
`docs/governance/harbor-ro14-obpi-forward-migration.md` § Act 7's reading.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The withdrawal was booked, or shown under `--dry-run` |
| 1 | The ledger holds no such unit |
| 2 | Usage error |
| 3 | The reason or witness is blank, or the unit is already withdrawn or superseded; nothing was written |

## See also

[`gz wp show`](wp-show.md), [`gz obpi withdraw`](obpi-withdraw.md).
