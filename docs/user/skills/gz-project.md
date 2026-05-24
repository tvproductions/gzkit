# /gz-project

Namespace router — project lifecycle skills (init, requirements, constitution, status).

---

## Purpose

`/gz-project` is a first-stage intent router for project lifecycle work. It presents a table of project intents and routes to the matched concrete skill. Procedure details live in the concrete skill's own manpage.

## When to Use

Use `/gz-project` when you need to initialize, configure, or check the status of a gzkit-governed project and want to identify the right concrete skill. If you already know the concrete skill, invoke it directly.

## Intent Table

| Intent | Invoke |
|--------|--------|
| init | `/gz-init` |
| prd | `/gz-prd` |
| constitution | `/gz-constitute` |
| status | `/gz-status` |
| state | `/gz-state` |
| config check | `/gz-check-config-paths` |
| deps upgrade | `/gz-deps-upgrade` |

## Related

- `/gz-skill-router` — full catalog with cross-namespace discovery
- `/gz-manage` — repo and release management intents
