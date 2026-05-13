---
id: governance-core
paths:
  - "**/*"
description: Non-negotiable governance workflow rules
---

<!-- rule-version: 0.2.0 -->

# Governance Core (gzkit)

> **Rule version:** `0.2.0` — bumped under GHI #322 to canonize
> `gz register-adrs` as the regenerator for `docs/governance/GovZero/adr-status.md`
> and `gz validate --adr-status-fresh` as the drift fail-close. Prior
> unversioned content treated as `0.1.0`.

## Non-negotiable rules

- Read `AGENTS.md` before implementation work.
- Use `uv run` for Python command execution.
- Do not bypass Gate 5 when lane requirements require human attestation.
- Do not edit `.gzkit/ledger.jsonl` manually.
- Every defect must be fixed now or tracked (`gh issue create --label defect` or `.gzkit/insights/agent-insights.jsonl`).

## Required workflow order (OBPI implementation path)

Scope: planned OBPI implementation under an active ADR. For in-flight defect
fixes meeting the thresholds in AGENTS.md § Defect-fix routing, take the
direct `fix(<scope>): … (GHI #N)` path instead — this workflow does not apply.

1. `uv run gz state --json`
2. `uv run gz status --table`
3. Implement one OBPI increment
4. `uv run gz implement --adr ADR-<X.Y.Z>`
5. `uv run gz gates --adr ADR-<X.Y.Z>`
6. `uv run gz adr audit-check ADR-<X.Y.Z>`

## Proof commands

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz validate --documents --surfaces
uv run gz validate --distribution
uv run mkdocs build --strict
```

## Operator-doc verb resolution (binding)

Every `gz <verb>` string appearing in an operator-facing doc must resolve to a registered parser verb. Scope: `docs/**/*.md`, `docs/**/*.feature`, `features/**/*.feature`, `.gzkit/skills/**/SKILL.md`, and runbooks under `docs/user/runbook.md` + `docs/governance/governance_runbook.md`.

A `gz <verb>` reference that points at an unregistered or renamed CLI verb is the same class of defect as an unresolvable import — it breaks the cascade `tool → skill → runbook` that `.gzkit/rules/tool-skill-runbook-alignment.md` depends on. Multi-word subcommands count (`gz adr status`, `gz obpi complete`), not just top-level verbs.

Enforced by `gz validate --cli-alignment`. Exit 3 on any unresolvable reference. Recovery: either register the verb, rename the reference to an existing verb, or file a GHI if the doc is describing a planned-but-unlanded CLI surface (and mark the reference as speculative so the check skips it — see the validator for the exact escape marker).

This section is the canonical rule home; the validator implementation in `src/gzkit/trust_audits.py` (or wherever the scope function lives) is an enforcement artifact of this rule, not the rule itself.

## ADR status index regeneration (binding)

`docs/governance/GovZero/adr-status.md` is a Layer 3 derived view per
`docs/governance/state-doctrine.md` — never source-of-truth, never
hand-maintained. The canonical regenerator is **`uv run gz register-adrs`**:
it walks on-disk ADR packages under `docs/design/adr/{foundation,pre-release}/`
and rewrites the index from frontmatter + H1 truth, in the same ceremony as
ledger reconciliation.

Drift between the committed index and on-disk canon is fail-closed by
**`uv run gz validate --adr-status-fresh`**, which is part of the default
`uv run gz check` pipeline. Recovery from a flagged drift is a single
command: `uv run gz register-adrs`.

Authored under GHI #322 (Architectural Boundary 6 — *do not let derived
views silently become source-of-truth*).
