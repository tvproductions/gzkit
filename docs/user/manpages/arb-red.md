# gz arb red

Witness a BEHAVIOR REQ's covering test failing against the base tree.

---

## Usage

```bash
gz arb red --req <REQ-ID> [--base <commit>] [--obpi <OBPI-ID>]
```

Reconstructs the base tree in a throwaway git worktree, copies in **only** the
test files, and runs the REQ's covering test there. The production hunks are
deliberately left behind — that asymmetry is the whole experiment: the test meets
the code as it was before the implementation landed.

`@covers` parity proves a BEHAVIOR REQ has a covering test. It never proves that
test can fail. A test authored after the production code, passing on its first
run, is byte-indistinguishable from a genuine RED-first test. This command is the
mechanical witness the pipeline's Red-Green-Refactor instruction lacked (GHI #642).

Emits an ARB red receipt and a `red_receipt_emitted` ledger event.

---

## Options

| Option | Description |
|--------|-------------|
| `--req` | BEHAVIOR REQ id to witness (required) |
| `--base` | Commit to run the test against (default: `HEAD`, the pre-change tree) |
| `--obpi` | Owning OBPI id, recorded on the ledger event |

---

## Failure classes

The `failure_class` is the verdict, not decoration.

| Class | Meaning | Verdict |
|-------|---------|---------|
| `assertion` | The test failed on an assertion | **Strong RED.** The test genuinely depends on the implementation. |
| `error` | The test failed on an ImportError or other exception | **Weak RED.** It failed for the wrong reason — usually the new symbol does not exist yet. Recorded as `error`; never silently equated with an assertion RED. |
| `none` | The test **passed** with the production hunks withheld | **No RED.** The test cannot fail when the business logic changes (`AGENTS.md` § DO IT RIGHT Rule 6), so it witnesses nothing. Blocking. |

---

## Examples

```bash
# Witness a REQ whose implementation is uncommitted in the working tree.
gz arb red --req REQ-0.33.0-01-01

# Attribute the witness to its owning OBPI.
gz arb red --req REQ-0.33.0-01-01 --obpi OBPI-0.33.0-01-airlock-data-model-and-events

# Witness against an explicit base (e.g. before the implementation commit).
gz arb red --req REQ-0.33.0-01-01 --base HEAD~1
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | A RED was witnessed (`assertion`, or the weaker `error`); receipt created |
| 1 | No covering test found, or `failure_class: none` — the test cannot fail |
| 2 | ARB internal error (worktree creation failed, git unavailable) |

---

## Receipt

- Schema: `gzkit.arb.red_receipt.v1` (`data/schemas/arb_red_receipt.schema.json`)
- Prefix: `arb-red-<REQ-ID>-<uuid4 hex>`
- Read by `gz validate --red-parity`, a bound `gz check` step.

---

## Notes

Running this against a REQ whose implementation is **already committed** yields
`failure_class: none` — the base tree contains the implementation, so nothing was
withheld. The witness is meaningful only while the production change is
uncommitted, or against an explicit `--base` that predates it.

gzkit's trunk is green and pre-commit runs unittest, so a RED can never be
committed to `main`. That is why the witness is an isolated base-tree run rather
than superpowers' commit-the-failing-test.

---

## See Also

- [`gz arb`](arb.md) — ARB parent reference
- [`gz arb step`](arb-step.md) — generic command wrapper
- [`gz covers`](covers.md) — `@covers` parity (coverage, not falsifiability)
- Rule: `.gzkit/rules/tests.md` § Red-Green-Refactor / `AGENTS.md` § DO IT RIGHT Rule 6
