# gz wp tag issue

Issue a tag on an opened or frozen order, as the coordinator: book its whole line item with the next id.

## Usage

```bash
gz wp tag issue <ORD-id> --slug <slug> --class <Danger|Caution> --surface <kind>:<name> --position <off|advisory|recording> --hazard <text> --removal-procedure <text> --source <source> --check-level <C|D> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `ORD-id` | The order the tag is issued on. Required |
| `--slug` | Lowercase words joined by hyphens, the id's last part. Required |
| `--class` | `Danger` or `Caution`. Required |
| `--surface` | The surface isolated, `<kind>:<name>`, kind `validator`, `check`, `hook` or `path`. Required |
| `--position` | The position it is to be hung in: `off`, `advisory` or `recording`. Required |
| `--hazard` | The hazard the tag guards against. Required |
| `--removal-procedure` | How it is removed, legible to a worker not involved. Required |
| `--source` | What it is hung for: `order-work`, `standard-disconnect`, `mel-bypass` or `surveillant-stop`. Required |
| `--check-level` | The check level it is issued under, `C` or `D`. Required |
| `--json` | Output the booked `tag_issued` event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The tag-out log is ledger events, its open tags a derived view (RP-12 ruling 4).
The coordinator issues a tag as Authorizing Officer before the repair dispatch
hangs it (ruling 6), and the verb books one `tag_issued` event carrying the whole
line item (rulings 5 and 120). `docs/governance/harbor-ro12-contractor-kit.md`
§ Rulings holds the rulings cited here.

- The id is `TAG-<NN>-<slug>`, numbered past every tag the ledger names (ruling 111).
- The surface is `<kind>:<name>`, resolved against the registry that holds that
  kind today (rulings 112 and 123): `validator:` a `gz validate` scope in its
  flag's spelling, `validator:hexagon-tests`; `check:` a `gz check` step's name in
  lower case with its spaces hyphenated, `check:module-size`; `hook:` a hook
  script `.claude/settings.json` registers, with or without `.py`, or a hook id
  `.pre-commit-config.yaml` declares; `path:` a path in the tree, repo-relative
  with forward slashes. The event records the registry's own name beside what was
  written. An unresolved name, and a path escaping the project root, is refused.
- The check level is C or D, the two levels that disconnect (ruling 113).
- The open MX session holds the tag and is the coordinator's mark (rulings 3 and
  114); with no session open the issue is refused.
- A tag is issued on an opened or frozen order of an initiated repair package
  (ruling 121), and a surface carries one open tag at a time (ruling 122).
- The source is one of ruling 5's four kinds, with no reference yet (ruling 124).
- A call stamped as a subagent's is refused: the coordinator is the unstamped
  operator-facing session (ruling 114).

A refusal names what failed, why and what to do, and books nothing.

## Examples

Observed 2026-11-17 in a scratch project set up as `tests/commands/test_wp_tag.py` sets one up: `gz init`, the seeded catalog, `WP-01-stamp` initiated and `ORD-01-import` opened. Its MX marker was opened by the test helper, so the session id below is that fixture's.

With no MX session open, exit 3:

```console
$ uv run gz wp tag issue ORD-01-import --slug hexagon --class Caution --surface validator:hexagon-tests --position advisory --hazard 'The scope reads a half-built map.' --removal-procedure 'Run the scope; it passes.' --source order-work --check-level D
No MX session is open, so the tag would have no holder. A tag is held by the
open MX session, whose id is the coordinator's mark on the issue (RP-12 rulings
3, 113 and 114). Have the operator open one through the gz-mx skill (`uv run gz
mx enter`), then issue the tag.
```

With a session open, the issue books the tag, exit 0:

```console
$ uv run gz wp tag issue ORD-01-import --slug hexagon --class Caution --surface validator:hexagon-tests --position advisory --hazard 'The scope reads a half-built map.' --removal-procedure 'Run the scope; it passes.' --source order-work --check-level D
Issued TAG-01-hexagon on ORD-01-import.
```

A second tag on the same surface, exit 3:

```console
$ uv run gz wp tag issue ORD-01-import --slug again --class Caution --surface validator:hexagon-tests --position advisory --hazard 'The scope reads a half-built map.' --removal-procedure 'Run the scope; it passes.' --source order-work --check-level D
Surface 'validator:hexagon-tests' already carries open tag TAG-01-hexagon,
issued on ORD-01-import; a surface carries one tag-out at a time (RP-12 ruling
122). The tag leaves the open log when ORD-01-import closes; issue this one
after, or isolate another surface.
```

A check level that does not disconnect, exit 3:

```console
$ uv run gz wp tag issue ORD-01-import --slug hexagon --class Caution --surface validator:hexagon-tests --position advisory --hazard 'The scope reads a half-built map.' --removal-procedure 'Run the scope; it passes.' --source order-work --check-level B
Check level 'B' does not disconnect. Of the safe-mode doctrine's four levels
only C and D disconnect, so a tag is issued under one of them (RP-12 ruling
113). Issue it again with --check-level C or D.
```

A surface its registry does not hold, exit 3:

```console
$ uv run gz wp tag issue ORD-01-import --slug hexagon --class Caution --surface validator:hexagon-test --position advisory --hazard 'The scope reads a half-built map.' --removal-procedure 'Run the scope; it passes.' --source order-work --check-level D
Surface 'validator:hexagon-test' names no validator the registry holds, so the
tag would isolate nothing and one tag-out per surface could not be compared
(RP-12 rulings 112 and 123). Name a `gz validate` scope in its flag's spelling,
`validator:hexagon-tests`.
```

With `--json`, the `tag_issued` event booked, exit 0:

```console
$ uv run gz wp tag issue ORD-01-import --slug module --class Caution --surface check:module-size --position advisory --hazard 'The scope reads a half-built map.' --removal-procedure 'Run the scope; it passes.' --source order-work --check-level D --json
{"schema":"gzkit.ledger.v1","event":"tag_issued","id":"TAG-02-module","ts":"2026-11-17T07:22:53.775456+00:00","tag_id":"TAG-02-module","order":"ORD-01-import","work_package":"WP-01-stamp","tag_class":"Caution","surface":"check:module-size","surface_kind":"check","surface_name":"Module size","position":"advisory","hazard":"The scope reads a half-built map.","removal_procedure":"Run the scope; it passes.","source":"order-work","check_level":"D","mx_session_id":"test-session"}
```

Observed from a subagent's call in the gzkit checkout, stamped with its root:

```console
$ uv run gz wp tag issue ORD-01-import --slug hexagon --class Caution --surface validator:hexagon-tests --position advisory --hazard "The scope reads a half-built map." --removal-procedure "Run the scope; it passes." --source order-work --check-level D
A tag is refused from a subagent's call: the issue is the coordinator's act as
Authorizing Officer (RP-12 ruling 6), and the coordinator is the unstamped
operator-facing session (RP-12 ruling 114). Run `uv run gz wp tag issue` from
the main session.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Issued |
| 1 | A hook registry does not parse, or the project is not initialized |
| 2 | Usage error |
| 3 | Refused: a subagent's call, no MX session open, the check level, the slug, a blank hazard or removal procedure, the surface, the order, its package or its state, or a surface already tagged; nothing booked |

## See also

[`gz wp tag show`](wp-tag-show.md), [`gz wp order new`](wp-order-new.md),
[`gz wp order show`](wp-order-show.md)
