# /gz-chores

Namespace router — maintenance and code-quality chore skills.

---

## Purpose

`/gz-chores` is a first-stage intent router. It presents a small table of maintenance and code-quality chore intents and routes you to the matched concrete skill. It does not duplicate ceremony or governance procedures — those live in the concrete skill's own manpage.

## When to Use

Use `/gz-chores` when you know you're doing maintenance or code-quality chore work but haven't decided which skill to invoke. If you already know the concrete skill (`/gz-chore-runner`, `/gz-deps-upgrade`, etc.), invoke it directly.

## Intent Table

| Intent | Invoke |
|--------|--------|
| chore runner | `/gz-chore-runner` |
| deps upgrade | `/gz-deps-upgrade` |
| foundation triage | `/gz-foundation-triage` |
| pythonic detect | `/gz-pythonic-pattern-detect` |
| pythonic apply | `/gz-pythonic-pattern-apply` |
| config check | `/gz-check-config-paths` |
| cli audit | `/gz-cli-audit` |

## Related

- `/gz-skill-router` — full catalog with cross-namespace discovery
- `/gz-quality` — quality and complexity intents (check, lint, tech debt, complexity)
