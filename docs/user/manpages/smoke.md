# gz smoke

Run the smoke/BVT tier against its declared time budget.

## Usage

```bash
gz smoke [OPTIONS]
```

## Description

Runs only the tests marked with the `@smoke` decorator, then fails closed if the
run exceeds the budget declared in `.gzkit/rules/tests.md`, or if the tier is
empty.

This is the bounded subset the 60-second ceiling was written for. The rule bound
that ceiling to a "Smoke/BVT" suite covering "current-scope surfaces only" —
subset language — but no subset existed, so the number was read against the full
unit tier and breached 4.5x (268.1s over 7497 tests) with nothing reading it
(GHI #724).

The full unit tier (`gz test`) carries no fixed ceiling by design: its runtime
grows with the REQ set, because every BEHAVIOR REQ owes a covering test. A
constant budget over a ratcheting workload can only be breached, never held.
Parallelism does not change that — the same suite measures 71.4s across 32
processes, still over.

An **empty** tier is treated as a policy breach, not a pass. A subset with no
members satisfies any budget trivially, which is the green-by-emptiness shape
`gz validate --qc-binding` refuses.

## Options

| Option | Description |
|--------|-------------|
| `--budget SECONDS` | Override the rule-declared ceiling (default: 60). Useful for probing headroom; the committed gate uses the rule's value |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Smoke tier passed within budget |
| 1 | One or more smoke tests failed — the build does not verify |
| 3 | Policy breach: the tier is empty, or the run exceeded its budget |

## Adding a smoke test

```python
from gzkit.smoke import smoke


class CliAnswers(unittest.TestCase):
    @smoke
    def test_every_registered_verb_answers_help(self) -> None:
        ...
```

There is no smoke directory: `gz validate --test-tiers` forbids a third tier
under `tests/`, and the runner boundary is the tier boundary. Membership is a
marker on an ordinary unittest.

Prefer members that enumerate coverage from a **live** source — the CLI parser,
a registry — over members that hard-code a list. A hand-maintained roster is
what rots; a sweep over the live parser covers a newly registered verb with no
upkeep at all.

## Examples

```bash
# Run the tier against its declared budget
gz smoke

# Check how much headroom is left
gz smoke --budget 5
```

## See Also

- [`test`](test.md) — the full unit tier
- [`check`](check.md) — runs the smoke tier as its `Smoke tier` step
- `.gzkit/rules/tests.md` § Smoke tier membership
