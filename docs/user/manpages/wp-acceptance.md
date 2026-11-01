# gz wp acceptance

Execute proof, record independent reviews and derive readiness on a work package.

## Usage

```bash
gz wp acceptance <WP-id> {init,prove,review,human-review,status} [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `action` | `init`, `prove`, `review`, `human-review` or `status`. Required |
| `--author` | The implementing session's identity (`init`) |
| `--spec` | JSON proof instructions, never execution results (`prove`) |
| `--receipt` | The ARB run id holding the review JSON (`review`) |
| `--stage` | `stage2` or `stage4`, default `stage4` (`status`) |
| `--req` | Narrow `status` to these obligations, at `stage2` only. Repeatable |
| `--attestor` | Who ruled (`human-review`) |
| `--ruling` | The operator's verbatim ruling (`human-review`) |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

This is the acceptance runtime of [`gz obpi acceptance`](obpi-acceptance.md), run on a package from commencement. The verbs, records and readiness are the same. Only the source of the obligations differs.

A delivery package's obligations are its frozen REQs at their frozen revisions, less any a `departure` exit moved out. A repair package's are its carried issues, one each, named `#<issue>`. An issue or a catalog REQ has no `@covers` scan, so its proof names its tests directly and they must kill every named mutant.

[`gz wp accept`](wp-accept.md) refuses until `status` reads ready. Appending objective quality evidence with `gz wp evidence` makes no review stale; any other edit to the record does.

A package gets three adversarial rounds with a mapped finding: the first and two follow-ups (GHI #1028). A review is recorded past the limit, so no finding is lost. Past the limit, `gz wp dispatch`, `gz wp accept` and `human-review` refuse until [`gz wp block`](wp-block.md), which reports the refutations per subject, and the operator's ruling through `gz wp unblock`. That ruling restarts the round count; the fix-cycle bound still holds any repair, and `--exit terminate` is open on any block. A departed REQ leaves the package's acceptance with its proofs and findings, which stay on the ledger.

## Examples

Observed in a scratch project holding `WP-01-loop`, a repair package carrying `#1206`:

```console
$ uv run gz wp acceptance WP-01-loop init --author implementing-session
{
  "author_id": "implementing-session",
  "obligations": [
    {
      "id": "#1206",
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The action succeeded |
| 1 | `review` or `human-review` named an id with no brief |
| 2 | Usage error |
| 3 | Acceptance is blocked; the message names what to repair |

## See also

- [`gz wp accept`](wp-accept.md)
- [`gz wp block`](wp-block.md)
- [`gz obpi acceptance`](obpi-acceptance.md)
