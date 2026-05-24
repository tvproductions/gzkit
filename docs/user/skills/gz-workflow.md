# /gz-workflow

Namespace router — end-to-end workflow skills (design through release).

---

## Purpose

`/gz-workflow` is a first-stage intent router. It presents a small table of workflow intents and routes you to the matched concrete skill. It does not duplicate ceremony or governance procedures — those live in the concrete skill's own manpage.

## When to Use

Use `/gz-workflow` when you know you're doing end-to-end workflow work but haven't decided which stage you're at. If you already know the concrete skill (`/gz-design`, `/gz-plan`, etc.), invoke it directly.

## Intent Table

| Intent | Invoke |
|--------|--------|
| design | `/gz-design` |
| plan | `/gz-plan` |
| implement | `/gz-obpi-pipeline` |
| verify | `/gz-implement` |
| attest | `/gz-adr-closeout-ceremony` |
| release | `/gz-patch-release` |

## Related

- `/gz-skill-router` — full catalog with cross-namespace discovery
- `/gz-governance` — ADR, OBPI, and ledger governance intents
