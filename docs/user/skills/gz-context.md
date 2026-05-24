# /gz-context

Namespace router — context preservation and orientation skills.

---

## Purpose

`/gz-context` is a first-stage intent router for context and orientation work. It presents a table of context intents and routes to the matched concrete skill. Procedure details live in the concrete skill's own manpage.

## When to Use

Use `/gz-context` when you need to preserve session context, orient to an ADR, or check parity with an upstream canonical source. If you already know the concrete skill, invoke it directly.

## Intent Table

| Intent | Invoke |
|--------|--------|
| session handoff | `/gz-session-handoff` |
| adr map | `/gz-adr-map` |
| parity scan | `/airlineops-parity-scan` |

## Related

- `/gz-skill-router` — full catalog with cross-namespace discovery
- `/gz-governance` — ADR and OBPI governance intents
