# /gz-quality

Namespace router — quality and complexity skills.

---

## Purpose

`/gz-quality` is a first-stage intent router for quality work. It presents a table of quality intents and routes to the matched concrete skill. Procedure details live in the concrete skill's own manpage.

## When to Use

Use `/gz-quality` when you need to run quality checks, review complexity, or manage technical debt and want to identify the right concrete skill. If you already know the concrete skill, invoke it directly.

## Intent Table

| Intent | Invoke |
|--------|--------|
| check / lint / test / typecheck | `/gz-check` |
| complexity preview | `/gz-complexity-advisor` |
| complexity authoring | `/gz-complexity-guide` |
| complexity distill | `/gz-complexity-distill` |
| tech debt | `/gz-tech-debt-review` |
| arb receipts | `/gz-arb` |
| chore runner | `/gz-chore-runner` |
| cli audit | `/gz-cli-audit` |
| obpi simplify | `/gz-obpi-simplify` |
| pythonic detect | `/gz-pythonic-pattern-detect` |
| pythonic apply | `/gz-pythonic-pattern-apply` |

## Related

- `/gz-skill-router` — full catalog with cross-namespace discovery
- `/gz-workflow` — end-to-end workflow intents
