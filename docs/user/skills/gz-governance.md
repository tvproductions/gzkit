# /gz-governance

Namespace router — ADR/OBPI/ledger governance skills.

---

## Purpose

`/gz-governance` is a first-stage intent router for governance work. It presents a table of governance intents and routes to the matched concrete skill. Ceremony details live in the concrete skill's own manpage.

## When to Use

Use `/gz-governance` when you need to perform ADR, OBPI, or ledger governance work and want to identify the right concrete skill. If you already know the concrete skill, invoke it directly.

## Intent Table

| Intent | Invoke |
|--------|--------|
| adr create | `/gz-adr-create` |
| adr promote | `/gz-adr-promote` |
| adr audit | `/gz-adr-audit` |
| adr evaluate | `/gz-adr-evaluate` |
| adr status | `/gz-adr-status` |
| adr sync | `/gz-adr-sync` |
| adr closeout | `/gz-adr-closeout-ceremony` |
| obpi specify | `/gz-obpi-specify` |
| obpi sync | `/gz-obpi-sync` |
| obpi lock | `/gz-obpi-lock` |
| plan audit | `/gz-plan-audit` |
| gates | `/gz-gates` |
| justify | `/gz-justify` |
| foundation triage | `/gz-foundation-triage` |
| competitor discovery | `/gz-competitor-radar` |
| ledger receipt | `/gz-adr-emit-receipt` |
| validate | `/gz-validate` |

## Related

- `/gz-skill-router` — full catalog with cross-namespace discovery
- `/gz-workflow` — end-to-end workflow intents (design through release)
