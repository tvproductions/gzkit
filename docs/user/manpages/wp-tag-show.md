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
| `--json` | Output the tags as JSON, each the `tag_issued` event's fields with `is_open`, `state`, `hang`, `clearance` and `clear` |
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
  `Repair` dispatch, or `not hung`), whether its clearance is authorized (`gz wp
  tag authorize`), who cleared it and the position found (`gz wp tag clear`), its class (Danger or Caution), the surface as
  written at issue, the position it is to be hung in, the check level, the
  source, the hazard and the removal procedure, one labelled line each, so the
  whole line item reads at any width. Under `--all` the first line marks it
  `(open)` or `(closed)`. An unhung tag reads closed once its order has closed
  (ruling 122); a hung tag stays open until it is cleared, whatever its order's
  state (ruling 129), and a cleared tag reads closed.
- With no tag open, it prints `No tag is open.`; under `--all` with none issued,
  `No tag has been issued.`
- `--json` prints a list, oldest first: each tag's `tag_issued` event, as
  [`gz wp tag issue`](wp-tag-issue.md) booked it, with `is_open`, `state`
  (`issued`, `hung`, `authorized` or `cleared`), `hang`, the `tag_hung` event or
  `null`, `clearance`, the `tag_clearance_authorized` event or `null`, and `clear`,
  the `tag_cleared` event or `null`. An empty log
  prints `[]`.

The verb writes nothing and needs no MX session. Unlike `issue`, it is not
refused from a subagent's call: a read is not the coordinator's act.

## Examples

Observed 2026-11-18 in two scratch projects set up as `tests/commands/test_wp_tag.py`
sets them up, `WP-01-stamp` initiated and `ORD-01-import` opened; in the second the
order was frozen and a `Repair` dispatch booked on it. Each MX marker was opened by
the test helper, so the session ids below are that fixture's.

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
  Clearance:   not authorized
  Cleared by:  not cleared
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
  Clearance:   not authorized
  Cleared by:  not cleared
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
    "clear": null,
    "clearance": null,
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
    "ts": "2026-11-18T08:46:25.478839+00:00",
    "work_package": "WP-01-stamp"
  }
]
```

In a second project, after the `Repair` dispatch hung `TAG-01-stamp-hook` (ruling 129):

```console
$ uv run gz wp tag show
TAG-01-stamp-hook on ORD-01-import
  Hung by:     D-c978f7bbe77ca6ac
  Clearance:   not authorized
  Cleared by:  not cleared
  Class:       Danger
  Surface:     validator:hexagon-tests
  Position:    off
  Check level: C
  Source:      order-work
  Hazard:      The scope reads a half-built map.
  Removal:     Run the scope; it passes.
```

and with `--all --json`:

```console
$ uv run gz wp tag show --all --json
[
  {
    "check_level": "C",
    "clear": null,
    "clearance": null,
    "event": "tag_issued",
    "hang": {
      "check_level": "C",
      "dispatch_id": "D-c978f7bbe77ca6ac",
      "event": "tag_hung",
      "hazard": "The scope reads a half-built map.",
      "id": "TAG-01-stamp-hook",
      "issued_by_session": "test-session",
      "mx_session_id": "test-session",
      "order": "ORD-01-import",
      "position": "off",
      "removal_procedure": "Run the scope; it passes.",
      "schema": "gzkit.ledger.v1",
      "source": "order-work",
      "surface": "validator:hexagon-tests",
      "surface_kind": "validator",
      "surface_name": "hexagon_tests",
      "tag_class": "Danger",
      "tag_id": "TAG-01-stamp-hook",
      "ts": "2026-11-18T08:46:25.503186+00:00",
      "work_package": "WP-01-stamp"
    },
    "hazard": "The scope reads a half-built map.",
    "id": "TAG-01-stamp-hook",
    "is_open": true,
    "mx_session_id": "test-session",
    "order": "ORD-01-import",
    "position": "off",
    "removal_procedure": "Run the scope; it passes.",
    "schema": "gzkit.ledger.v1",
    "source": "order-work",
    "state": "hung",
    "surface": "validator:hexagon-tests",
    "surface_kind": "validator",
    "surface_name": "hexagon_tests",
    "tag_class": "Danger",
    "tag_id": "TAG-01-stamp-hook",
    "ts": "2026-11-18T08:46:25.485440+00:00",
    "work_package": "WP-01-stamp"
  }
]
```

After the order commenced, the hanging dispatch was voided and the coordinator
authorized the clearance (`gz wp tag authorize`); the tag stays hung and open
until its clear:

```console
$ uv run gz wp tag show
TAG-01-stamp-hook on ORD-01-import
  Hung by:     D-c978f7bbe77ca6ac
  Clearance:   authorized
  Cleared by:  not cleared
  Class:       Danger
  Surface:     validator:hexagon-tests
  Position:    off
  Check level: C
  Source:      order-work
  Hazard:      The scope reads a half-built map.
  Removal:     Run the scope; it passes.
```

After a `Restoration` dispatch cleared it, found in the position it was hung in
(`gz wp tag clear`), the tag reads closed (ruling 129). The default view omits it:

```console
$ uv run gz wp tag show
No tag is open.
```

and `--all` names the clear's dispatch and the position found:

```console
$ uv run gz wp tag show --all
TAG-01-stamp-hook on ORD-01-import (closed)
  Hung by:     D-c978f7bbe77ca6ac
  Clearance:   authorized
  Cleared by:  D-7b45765599187c69, found off
  Class:       Danger
  Surface:     validator:hexagon-tests
  Position:    off
  Check level: C
  Source:      order-work
  Hazard:      The scope reads a half-built map.
  Removal:     Run the scope; it passes.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Shown, an empty log included |
| 1 | The project is not initialized |
| 2 | Usage error |
| 3 | A `tag_issued` row on the ledger does not parse; the refusal names it and its void |

## See also

[`gz wp tag issue`](wp-tag-issue.md), [`gz wp tag authorize`](wp-tag-authorize.md),
[`gz wp order show`](wp-order-show.md)
