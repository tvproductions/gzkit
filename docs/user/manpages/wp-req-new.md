# gz wp req new

Write one repair requirement with the next id, held on its repair package.

## Usage

```bash
gz wp req new <WP-id> --statement <text> --criterion <STATE|OUTCOME|EVIDENCE> --kind <kind> --problem-report <issue> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The repair package the REQ is held on. Required |
| `--statement` | Effect and rationale. Required |
| `--criterion` | One acceptance criterion, its state or input, required outcome and evidence joined by `\|`. Required, repeatable |
| `--kind` | `BEHAVIOR`, `SUPPORT` or `STRUCTURAL-FENCE`, the proof channel that binds it. Required |
| `--problem-report` | The GitHub issue the REQ answers, one the package carries. Required |
| `--aligns-to` | A catalog REQ of design the repair aligns to |
| `--supersedes` | The REQ this one supersedes, which stays whole |
| `--json` | Output the REQ as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

A repair requirement states what must hold again after a repair (requirements
model § 12). It lives in `data/catalog/reqs.json` beside the catalog's
requirements, one `REQ-<n>` sequence for both, marked `"specialization":
"repair"` (RP-12 ruling 45). The verb writes it through the store's writer,
checking the edit against the rules `gz validate --catalog` reads before the
file is touched, so a refusal writes nothing.

- The id is the next `REQ-<n>` past every REQ of either specialization, at
  revision 1.
- It is held on a repair package that is initiated and not closed, since the
  package stays open while its REQs are found (rulings 2, 48). A delivery
  package is refused.
- Its problem report is a GitHub issue the package carries (ruling 9: the issue
  stays the problem report).
- `--aligns-to` names a catalog REQ the store holds. `--supersedes` names any REQ
  the store holds, other than itself.
- Any kind serves, so a docs repair is an honest `SUPPORT` REQ.

The verb writes repair REQs only; catalog REQs are RP-11's intake. Nothing edits
a REQ once written. A change to its obligation is a new REQ carrying
`--supersedes`, and `revision` counts editorial amendments only (ruling 31). The
verb that edits a REQ before an order freezes it is RP-5's tranche 6, ruled to
land after RP-11; until it does, a REQ written in error is left unbound and a
corrected one written beside it (ruling 48's stated limit).

## Examples

Observed in a scratch project holding repair package `WP-01-stamp` (initiated,
carrying #1301) and delivery package `WP-02-resume`:

```console
$ uv run gz wp req new WP-01-stamp --statement "The stamp generator imports by its public name." --criterion "the hook is generated|it imports a public name|the import ratchet test" --kind BEHAVIOR --problem-report 1301
Wrote REQ-1, a repair REQ held on WP-01-stamp.
$ uv run gz wp req new WP-01-stamp --statement "The generator and its test share one public name." --criterion "the hook is generated|it imports a public name|the import ratchet test" --kind BEHAVIOR --problem-report 1301 --supersedes REQ-1
Wrote REQ-2, a repair REQ held on WP-01-stamp.
$ uv run gz wp req new WP-01-stamp --statement "S." --criterion "the hook is generated|it imports a public name|the import ratchet test" --kind SUPPORT --problem-report 7
Repair REQ REQ-3 names problem report #7, which WP-01-stamp does not carry. The
rulings are in docs/governance/harbor-ro12-contractor-kit.md. Nothing was
written; correct the call and re-run `uv run gz wp req new <WP-id> --statement
<text> --criterion '<state>|<outcome>|<evidence>' --kind <kind> --problem-report
<issue>`.
$ uv run gz wp req new WP-02-resume --statement "S." --criterion "the hook is generated|it imports a public name|the import ratchet test" --kind BEHAVIOR --problem-report 1301
Repair REQ REQ-3 is held on WP-02-resume, which is a delivery package. The
rulings are in docs/governance/harbor-ro12-contractor-kit.md. Nothing was
written; correct the call and re-run `uv run gz wp req new <WP-id> --statement
<text> --criterion '<state>|<outcome>|<evidence>' --kind <kind> --problem-report
<issue>`.
$ uv run gz wp req new WP-01-stamp --statement "S." --criterion "only|two" --kind BEHAVIOR --problem-report 1301
--criterion 'only|two' is not three non-empty parts joined by '|'. A criterion
names its state or input, required outcome, evidence (requirements model § The
records). Nothing was written; correct the call and re-run `uv run gz wp req new
<WP-id> --statement <text> --criterion '<state>|<outcome>|<evidence>' --kind
<kind> --problem-report <issue>`.
$ uv run gz wp req new WP-09-ghost --statement "S." --criterion "the hook is generated|it imports a public name|the import ratchet test" --kind BEHAVIOR --problem-report 1
Work package 'WP-09-ghost' is not in data/catalog/work_packages.json. A repair
REQ is held on a package the catalog holds; create one with `gz wp new`.
```

The second REQ as written to `data/catalog/reqs.json`:

```json
{
  "id": "REQ-2",
  "statement": "The generator and its test share one public name.",
  "criteria": [
    {
      "state_or_input": "the hook is generated",
      "required_outcome": "it imports a public name",
      "evidence": "the import ratchet test"
    }
  ],
  "kind": "BEHAVIOR",
  "revision": 1,
  "supersedes": "REQ-1",
  "specialization": "repair",
  "held_on": "WP-01-stamp",
  "problem_report": 1301,
  "aligns_to": null
}
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Written |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | The REQ is refused: a criterion, a field, the package's kind or state, the problem report, `--aligns-to` or `--supersedes`; nothing written |

## See also

[`gz wp order new`](wp-order-new.md), [`gz wp new`](wp-new.md),
[`gz validate --catalog`](validate.md)
