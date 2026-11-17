# gz wp tag show

Show the tag-out log: the open tags by default, every tag issued with `--all`.

## Usage

```bash
gz wp tag show [--all] [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--all` | Every tag issued, open and closed, each marked which |
| `--json` | Output the tags as JSON, each the `tag_issued` event's fields with `is_open` |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The tag-out log is ledger events, and the log is a Layer 3 view rendered from
them, never edited (RP-12 ruling 4). `gz wp tag show` renders it, the open tags
by default and every tag on request (ruling 110).
`docs/governance/harbor-ro12-contractor-kit.md` § Rulings holds the rulings
cited here.

- Each tag is a block (ruling 126): its id and order, then its class (Danger or
  Caution), the surface as written at issue, the position it is to be hung in,
  the check level, the source, the hazard and the removal procedure, one
  labelled line each, so the whole line item reads at any width. Under `--all`
  the first line marks it `(open)` or `(closed)`; a tag reads closed once its
  order has closed (ruling 122).
- With no tag open, it prints `No tag is open.`; under `--all` with none issued,
  `No tag has been issued.`
- `--json` prints a list, oldest first: each tag's `tag_issued` event, as
  [`gz wp tag issue`](wp-tag-issue.md) booked it, with `is_open`. An empty log
  prints `[]`.

The verb writes nothing and needs no MX session. Unlike `issue`, it is not
refused from a subagent's call: a read is not the coordinator's act.

## Examples

Observed 2026-11-17 in a scratch project set up as `tests/commands/test_wp_tag.py`
sets one up, `WP-01-stamp` initiated and `ORD-01-import` opened; its MX marker was
opened by the test helper, so the session id below is that fixture's.

Before any tag is issued:

```console
$ uv run gz wp tag show
No tag is open.
```

After `gz wp tag issue` booked `TAG-01-hexagon`:

```console
$ uv run gz wp tag show
TAG-01-hexagon on ORD-01-import
  Class:       Caution
  Surface:     validator:hexagon-tests
  Position:    advisory
  Check level: D
  Source:      order-work
  Hazard:      The scope reads a half-built map.
  Removal:     Run the scope; it passes.
```

With `--all`:

```console
$ uv run gz wp tag show --all
TAG-01-hexagon on ORD-01-import (open)
  Class:       Caution
  Surface:     validator:hexagon-tests
  Position:    advisory
  Check level: D
  Source:      order-work
  Hazard:      The scope reads a half-built map.
  Removal:     Run the scope; it passes.
```

With `--all --json`:

```console
$ uv run gz wp tag show --all --json
[
  {
    "check_level": "D",
    "event": "tag_issued",
    "hazard": "The scope reads a half-built map.",
    "id": "TAG-01-hexagon",
    "is_open": true,
    "mx_session_id": "test-session",
    "order": "ORD-01-import",
    "position": "advisory",
    "removal_procedure": "Run the scope; it passes.",
    "schema": "gzkit.ledger.v1",
    "source": "order-work",
    "surface": "validator:hexagon-tests",
    "surface_kind": "validator",
    "surface_name": "hexagon_tests",
    "tag_class": "Caution",
    "tag_id": "TAG-01-hexagon",
    "ts": "2026-11-17T07:39:13.577189+00:00",
    "work_package": "WP-01-stamp"
  }
]
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Shown, an empty log included |
| 1 | The project is not initialized |
| 2 | Usage error |
| 3 | A `tag_issued` row on the ledger does not parse; the refusal names it and its void |

## See also

[`gz wp tag issue`](wp-tag-issue.md), [`gz wp order show`](wp-order-show.md)
