# gz handoff

Operator surface over the session-handoff authoring gate (ADR-0.0.65).

---

## Overview

`gz handoff` is the operator surface over the handoff authoring API
(`gzkit.handoff_api`, shipped by OBPI-0.0.65-02). A handoff is the register
entry that preserves intent across a session or lock boundary; historically
these were hand-written markdown that bypassed validation. This verb routes
authoring through the fail-closed `validate_handoff_document` gate so a handoff
is mechanically validated rather than trusted.

Handoffs live in the single canonical store `.gzkit/handoffs/`. `create` writes
through the validation gate; `list` and `resume` are read-only projections over
that store.

The three verbs:

| Verb | Purpose |
|------|---------|
| [`gz handoff list`](handoff-list.md) | List handoffs newest-first, optionally scoped by ADR |
| [`gz handoff resume`](handoff-resume.md) | Report the newest handoff for an ADR, its staleness, and first next step |
| [`gz handoff create`](handoff-create.md) | Author a handoff, fail-closed through the validation gate |
| [`gz handoff decide`](handoff-decide.md) | Book the operator's transit decision on a resumed handoff (only `proceed` lifts the resume gate) |
| [`gz handoff archive`](handoff-archive.md) | Move handoffs older than a threshold into `.gzkit/handoffs/archive/` (move-not-delete) |

A handoff **advises**; it does not authorize. Resuming a handoff surfaces its
advised next step for the operator to ratify — it is never a Gate-5 completion
attestation.

---

## Example

```bash
uv run gz handoff list --adr ADR-0.0.65
uv run gz handoff resume --adr ADR-0.0.65
uv run gz handoff create --adr ADR-0.0.65 --slug my-work --agent g0 --decisions "Chose X over Y"
```
