# gz test-shape

Advisory inventory of test-shape debt. **Always exits 0 — this is a reporting surface, never a gate.**

---

## Usage

```bash
gz test-shape [--kind {tautological,output,all}] [--undeclared-only] [--json]
```

Two read-only screens over `tests/`:

1. **Tautological operations** — a filesystem read plus an assertion, with no call into
   production code. Content-echo tests that prove what a file *says*, not what the code
   *does*. Reported with the proposed disposition (`convert`, `fold-to-validator`,
   `replace-with-ledger`, `keep-as-fixture`).

2. **Output/render assertions** — a test asserting on `result.output`, a captured
   `stdout`/`stderr`, a `.getvalue()`, or via `assertRegex` / `assertMultiLineEqual`,
   with whether its output-form carve-out is **declared**.

---

## Options

| Option | Description |
|--------|-------------|
| `--kind {tautological,output,all}` | Which screen to report (default: `all`) |
| `--undeclared-only` | Show only output assertions with no declared carve-out |
| `--json` | Machine-readable output, including the `by_disposition` roll-up |

---

## Why this is advisory and must stay advisory

Most output/render assertions are legitimate. `.gzkit/rules/tests.md`
§ Output-form fixture carve-out **permits** render-contract assertions, and
`.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3 **requires** some of them.

A fail-closed screen would redden a green trunk against tests the doctrine explicitly
allows. What this command reports is not "these are defects" — it is "these have not
been classified."

Declare the carve-out either way:

```python
class TestStatusRendering(unittest.TestCase):      # class-name form
    def test_table_header(self):
        self.assertIn("REQ", result.output)

    def test_row_alignment(self):
        # output-contract: the column layout IS the operator contract (Invariant 3)
        self.assertRegex(result.output, r"REQ-\d")
```

Accepted class-name suffixes: `*OutputForm`, `*OutputContract`, `*Rendering`.
The `# output-contract: <reason>` comment must sit **inside** the test function; a
module-level marker does not declare the whole file.

---

## Relationship to the fail-closed gate

`gz validate --tautological-test-audit` is the **growth** gate: it fails closed (exit 3)
when a tautological operation appears that is neither in
`data/tautological_test_baseline.json` nor waived. It proves no new content-echo test
lands. It does not tell an operator what debt remains, and it exposes no per-disposition
roll-up.

`gz test-shape` answers that second question. Together: the gate holds the line, the
inventory routes the cleanup.

---

## Examples

```bash
gz test-shape                                   # both screens, human-readable
gz test-shape --kind tautological               # just the disposition roll-up
gz test-shape --kind output --undeclared-only   # what still needs classifying
gz test-shape --json                            # by_disposition + per-op records
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Always. Findings are reported, never enforced. |

---

## See Also

- [`gz validate`](validate.md) — `--tautological-test-audit` is the fail-closed growth gate
- [`gz covers`](covers.md) — REQ → `@covers` parity (coverage, not test shape)
- [`gz arb red`](arb-red.md) — falsifiability witness (whether a test *can fail*)
- Rule: `.gzkit/rules/tests.md` § The discriminator / § Output-form fixture carve-out
- Audit: `docs/design/adr/foundation/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine/audit/RECURRENCE_DEFENSE_AUDIT_2026-07-09.md`
