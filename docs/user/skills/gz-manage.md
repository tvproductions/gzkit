# /gz-manage

Namespace router — repo and release management skills (git-sync, issues, releases, tidy).

---

## Purpose

`/gz-manage` is a first-stage intent router for repository and release management work. It presents a table of management intents and routes to the matched concrete skill. Procedure details live in the concrete skill's own manpage.

## When to Use

Use `/gz-manage` when you need to sync the repository, manage issues, create releases, or run maintenance tasks and want to identify the right concrete skill. If you already know the concrete skill, invoke it directly.

## Intent Table

| Intent | Invoke |
|--------|--------|
| git sync | `/git-sync` |
| issue author | `/ghi-author` |
| issue close | `/ghi-close` |
| issue triage | `/ghi-triage` |
| issue file (cross-repo) | `/gz-issue-file` |
| patch release | `/gz-patch-release` |
| semver migrate | `/gz-migrate-semver` |
| agent sync | `/gz-agent-sync` |
| tidy | `/gz-tidy` |

## Related

- `/gz-skill-router` — full catalog with cross-namespace discovery
- `/gz-project` — project lifecycle intents
