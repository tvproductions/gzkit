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
| `--json` | Output the tags as JSON, each the `tag_issued` event's fields with `is_open`, `state` and `hang` |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The tag-out log is ledger events, and the log is a Layer 3 view rendered from
them, never edited (RP-12 ruling 4). `gz wp tag show` renders it, the open tags
by default and every tag on request (ruling 110).
`docs/governance/harbor-ro12-contractor-kit.md` § Rulings holds the rulings
cited here.

- Each tag is a block (ruling 126): its id and order, then who hung it (the
  `Repair` dispatch, or `not hung`), its class (Danger or Caution), the surface as
  written at issue, the position it is to be hung in, the check level, the
  source, the hazard and the removal procedure, one labelled line each, so the
  whole line item reads at any width. Under `--all` the first line marks it
  `(open)` or `(closed)`. An unhung tag reads closed once its order has closed
  (ruling 122); a hung tag stays open until it is cleared, whatever its order's
  state (ruling 129).
- With no tag open, it prints `No tag is open.`; under `--all` with none issued,
  `No tag has been issued.`
- `--json` prints a list, oldest first: each tag's `tag_issued` event, as
  [`gz wp tag issue`](wp-tag-issue.md) booked it, with `is_open`, `state`
  (`issued` or `hung`) and `hang`, the `tag_hung` event or `null`. An empty log
  prints `[]`.

The verb writes nothing and needs no MX session. Unlike `issue`, it is not
refused from a subagent's call: a read is not the coordinator's act.

## Examples

Observed 2026-11-17 in scratch projects set up as `tests/commands/test_wp_tag.py`
sets them up, `WP-01-stamp` initiated and `ORD-01-import` opened; each MX marker was
opened by the test helper, so the session ids below are that fixture's.

Before any tag is issued:

```console
$ uv run gz wp tag show
No tag is open.
```

After `gz wp tag issue` booked `TAG-01-hexagon`, not yet hung:

```console
$ uv run gz wp tag show
TAG-01-hexagon on ORD-01-import
  Hung by:     not hung
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
  Hung by:     not hung
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
    "hang": null,
    "hazard": "The scope reads a half-built map.",
    "id": "TAG-01-hexagon",
    "is_open": true,
    "mx_session_id": "test-session",
    "order": "ORD-01-import",
    "position": "advisory",
    "removal_procedure": "Run the scope; it passes.",
    "schema": "gzkit.ledger.v1",
    "source": "order-work",
    "state": "issued",
    "surface": "validator:hexagon-tests",
    "surface_kind": "validator",
    "surface_name": "hexagon_tests",
    "tag_class": "Caution",
    "tag_id": "TAG-01-hexagon",
    "ts": "2026-11-17T09:14:50.369514+00:00",
    "work_package": "WP-01-stamp"
  }
]
```

After the `Repair` dispatch hung `TAG-01-stamp-hook` (ruling 129):

```console
$ uv run gz wp tag show
TAG-01-stamp-hook on ORD-01-import
  Hung by:     D-ce067ddfdaf515ee
  Class:       Danger
  Surface:     path:src/stamp.py
  Position:    off
  Check level: C
  Source:      order-work
  Hazard:      The stamp reads no root.
  Removal:     Run the stamp tests; they pass.
```

and with `--all --json`:

```console
$ uv run gz wp tag show --all --json
[
  {
    "check_level": "C",
    "event": "tag_issued",
    "hang": {
      "check_level": "C",
      "dispatch_id": "D-ce067ddfdaf515ee",
      "event": "tag_hung",
      "hazard": "The stamp reads no root.",
      "id": "TAG-01-stamp-hook",
      "issued_by_session": "test-session",
      "mx_session_id": "test-session",
      "order": "ORD-01-import",
      "position": "off",
      "removal_procedure": "Run the stamp tests; they pass.",
      "schema": "gzkit.ledger.v1",
      "source": "order-work",
      "surface": "path:src/stamp.py",
      "surface_kind": "path",
      "surface_name": "src/stamp.py",
      "tag_class": "Danger",
      "tag_id": "TAG-01-stamp-hook",
      "ts": "2026-11-17T09:14:50.722476+00:00",
      "work_package": "WP-01-stamp"
    },
    "hazard": "The stamp reads no root.",
    "id": "TAG-01-stamp-hook",
    "is_open": true,
    "mx_session_id": "test-session",
    "order": "ORD-01-import",
    "position": "off",
    "removal_procedure": "Run the stamp tests; they pass.",
    "schema": "gzkit.ledger.v1",
    "source": "order-work",
    "state": "hung",
    "surface": "path:src/stamp.py",
    "surface_kind": "path",
    "surface_name": "src/stamp.py",
    "tag_class": "Danger",
    "tag_id": "TAG-01-stamp-hook",
    "ts": "2026-11-17T09:14:50.703382+00:00",
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
