# gz wp acceptance

Execute proof, record independent reviews and derive readiness on a work package
or an order.

## Usage

```bash
gz wp acceptance (<WP-id> | <ORD-id>) {init,prove,review,human-review,status} [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` or `ORD-id` | The work package's or the order's id. Required |
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

A delivery package's obligations are its frozen REQs at their frozen revisions, less any a `departure` exit moved out. A repair package's are its carried issues, one each, named `#<issue>`. An order's are its own frozen REQs at their frozen revisions, less any a `departure` exit on the order moved out, and its records are kept under the order's id, so it runs from the order's commencement while its package stays initiated (RP-12 ruling 60). [`gz wp order accept`](wp-order-accept.md) refuses until the order's `status` reads ready. An issue or a catalog REQ has no `@covers` scan, so its proof names its tests directly and they must kill every named mutant.

[`gz wp accept`](wp-accept.md) refuses until `status` reads ready. Appending objective quality evidence with `gz wp evidence` makes no review stale; any other edit to the record does.

A package gets three adversarial rounds with a mapped finding: the first and two follow-ups (GHI #1028). An order gets its own three, and past them `gz wp dispatch --order`, `gz wp order accept` and `human-review` on the order refuse until `gz wp block --order` and the operator's ruling on the order. A review is recorded past the limit, so no finding is lost. Past the limit, `gz wp dispatch`, `gz wp accept` and `human-review` refuse until [`gz wp block`](wp-block.md), which reports the refutations per subject, and the operator's ruling through `gz wp unblock`. That ruling restarts the round count; the fix-cycle bound still holds any repair, and `--exit terminate` is open on any block. A departed REQ leaves the package's acceptance with its proofs and findings, which stay on the ledger.

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

On an order, `ORD-01-import` commenced on `REQ-1@1` in repair package
`WP-01-stamp`, the obligation is the order's frozen REQ:

```console
$ uv run gz wp acceptance ORD-01-import init --author implementing-session
{
  "author_id": "implementing-session",
  "obligations": [
    {
      "id": "REQ-1",
      "kind": "BEHAVIOR",
      "statement": "The stamp imports again.",
      "authority": "data/catalog/orders.json#ORD-01-import",
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
- [`gz wp order accept`](wp-order-accept.md)
- [`gz wp block`](wp-block.md)
- [`gz obpi acceptance`](obpi-acceptance.md)
