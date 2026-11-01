# gz wp accept

Record final inspection of a commenced work package.

## Usage

```bash
gz wp accept <WP-id> --evidence <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--evidence` | What justifies the move, such as the final inspection. Required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Moves a commenced package to `accepted` (C10 of the contractor-kit record:
final inspection with no tag still hung). RO-12's refusals read this state.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

While a package is accepted and not yet closed, the production-write fence applies across the whole tree, so land the package's production code before accepting it (GHI #1206). See [`gz wp block`](wp-block.md) for what the fence refuses.

The verb refuses until `gz wp acceptance` reads ready: current proof on every obligation, with accepted spec, quality and adversarial reviews and no open finding, and a single-driver package's adversarial review alone. It also refuses past the round limit. A package stopped by a `reopen` or `terminate` exit is excused, and unless its acceptance reads ready it closes as `redirect`, `pause` or `terminate`.

## Examples

Observed in a scratch project whose acceptance reads ready seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp accept WP-02-resume --evidence final-inspection
WP-02-resume: commenced -> accepted
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The move was booked |
| 1 | The work package is not in `data/catalog/work_packages.json` |
| 2 | Usage error |
| 3 | The lifecycle or the move's own rules refuse it; nothing was written |

## See also

[`gz wp new`](wp-new.md), [`gz wp show`](wp-show.md),
[`gz validate --catalog`](validate.md)
