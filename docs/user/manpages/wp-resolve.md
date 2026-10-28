# gz wp resolve

Record an issue's close against its repair package.

## Usage

```bash
gz wp resolve <WP-id> <issue> --commit <sha> --reviewer <name> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The repair package's id. Required |
| `issue` | The GitHub issue number. Required |
| `--commit` | The fix's commit SHA. Required |
| `--reviewer` | The reviewer who confirmed the fix. Required |
| `--json` | Output as JSON, with the issues still open and the package's state |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

`ghi-close` records each fixed issue against the repair package that carries it
(RO-5 ruling 10, `docs/governance/harbor-ro5-work-packages.md`). The verb books
one `work_package_issue_closed` event naming the issue, the fix's commit and the
reviewer, then prints the package's issues still open.

The close of a package's last issue never closes the package: it stays in its
state and closes only through Gate 5 (`gz wp close`), once its
list-of-discrepancies lines are cleared and its safeguards restored. The verb
refuses, exits 3 and books nothing for an issue the package does not carry, a
delivery package, a package not initiated or already closed, an issue already
recorded, or an empty commit or reviewer.

The verb is drydock RO-5 tranche 3; the operator ruled its shape on 2026-10-28
("New event + gz wp verb (Recommended)").

## Examples

Observed in a scratch project holding `WP-01-astral`, initiated, carrying
`#1183` and `#1184`:

```console
$ uv run gz wp resolve WP-01-astral 1183 --commit abc1234 --reviewer spec-reviewer
Recorded #1183 closed against WP-01-astral at abc1234.
  still open: #1184
$ uv run gz wp resolve WP-01-astral 1184 --commit def5678 --reviewer spec-reviewer
Recorded #1184 closed against WP-01-astral at def5678.
  every issue is closed; WP-01-astral stays initiated and closes only through
Gate 5 (gz wp close).
$ uv run gz wp resolve WP-01-astral 1184 --commit def5678 --reviewer spec-reviewer
Issue #1184 is already recorded closed against WP-01-astral.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The close was booked |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | The close is one ruling 10 refuses; nothing was booked |

## See also

[`gz wp attach`](wp-attach.md), [`gz wp close`](wp-close.md),
[`gz wp show`](wp-show.md)
