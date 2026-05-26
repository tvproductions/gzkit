# Model Selection — Rationale

> Expansion doc for `.gzkit/rules/model-selection.md` § Rationale (ADR-0.0.54-04 lift).
> Prose preserved verbatim; see rule file for binding bullets.

## Rationale

At 20x max subscription and beyond, context and token budgets are real constraints. Model selection is not a comfort/speed optimization — it is a strategic resource allocation decision. A Haiku that closes its decision space is strictly better than an Opus doing the same work; an Opus that is necessary is worth the cost.

Every decision made by a lower model frees tokens for a higher model to spend on work that genuinely needs it. The routing matrix names the decision complexity (what would make this task fail if assigned to a weaker model?) so that the choice is mechanical, not intuitive.

## See also

- `docs/governance/opus-tuning.md` — per-turn thinking and effort tuning within Opus
- `docs/governance/agent-contract-rationale.md` — context and token economy rationale
