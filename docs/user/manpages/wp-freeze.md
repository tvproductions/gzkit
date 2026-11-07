# gz wp freeze

Freeze a work package's REQ baseline after the independent reviewer's nine-criteria check.

## Usage

```bash
gz wp freeze <WP-id> --risk-note <text> --review-receipt <id> --evidence <text> [--baseline REQ-<n>@<rev>]... [--approve-alteration <id>]... [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--baseline` | A REQ frozen at its revision, `REQ-<n>@<revision>`. Repeatable; a delivery package needs at least one |
| `--risk-note` | The short risk note. Required |
| `--review-receipt` | The reviewer's nine-criteria receipt. Required |
| `--approve-alteration` | An alteration the operator approves. Repeatable; every planned alteration must be approved |
| `--evidence` | What justifies the freeze. Required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Moves an initiated delivery package to `frozen`. Each baseline entry must be a
catalog REQ the catalog holds at that revision and a member of the package's
outcome, and the baseline may not be empty. The operator approves each planned
alteration at freeze (ruling of 2026-10-28), so the approved set must equal the
package's alterations.

A repair package moves only `initiated` to `closed`, and its orders carry the run's
states (RP-12 ruling 44, `docs/governance/harbor-ro12-contractor-kit.md`). Its
freeze is refused with exit 3 and names [`gz wp order freeze`](wp-order-freeze.md),
where each order's freeze seals the package's footprint (ruling 56) and approves
the alterations no earlier order's freeze approved (ruling 63).

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

A repair package must carry a valid footprint, as a brief must carry valid Allowed Paths (RO-14 ruling 24), and `gz wp order freeze` holds it to that: it exits 3 on a repair package with no `modules`, on a module that does not exist, on a generated vendor mirror, on a directory not ending `/`, and on a module with no literal root, such as `*.*` or `s*`. A new file is declared by its existing parent directory. The refusal names the recovery: a change order with `--drop-module` and `--module`. A delivery package reads its outcome's `modules`, so this does not apply to it. The freeze books the footprint on the ledger, which is what the airlock reads from then on.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp freeze WP-02-resume --baseline REQ-1@2 --risk-note "touches the chain" \
    --review-receipt review-01 --approve-alteration ALT-1 --evidence review-01
WP-02-resume: initiated -> frozen
```

On a repair package, in a scratch project at `/private/tmp/gz-act5` holding
`WP-01-stamp` initiated:

```console
$ uv run gz wp freeze WP-01-stamp --risk-note R --review-receipt V --evidence E
Repair package WP-01-stamp moves only initiated -> closed; its orders carry the
run's states (RP-12 ruling 44). Run `uv run gz wp order freeze <ORD-id>` on the
order instead.
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
