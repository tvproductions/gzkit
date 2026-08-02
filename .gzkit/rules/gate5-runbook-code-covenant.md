---
id: gate5-runbook-code-covenant
paths:
  - "docs/**"
  - "src/gzkit/**"
description: Documentation-code covenant for Gate 5
---

# Gate 5 Runbook-Code Covenant (gzkit)

<!-- rule-version: 0.2.1 -->

> **Rule version:** `0.2.1` — reconciled to ADR-0.0.24/ADR-0.0.36 — attestation is universal and the validation bundle must cite ARB-wrapped invocations (`0.2.0`); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#gate5-runbook-code-covenantmd). Binding rules unchanged.

Documentation is a first-class deliverable and must track behavior changes in the same patch set.

## Three-layer documentation model

| Layer | Location | Purpose |
|---|---|---|
| Operator runbook | `docs/user/runbook.md` | daily execution workflow |
| Governance runbook | `docs/governance/governance_runbook.md` | governance-maintainer workflow |
| Command docs | `docs/user/manpages/**` | command contracts and examples |

## Required updates when behavior changes

- Update command docs and examples.
- Update runbook flows and verification commands.
- Ensure attestation language remains explicit where required.

## Validation bundle

Cite the **ARB-wrapped canonical invocations** — they emit the receipt IDs attestation requires. Bare (non-ARB) commands emit no receipt and **do not satisfy** the Gate-5 evidence requirement; on Heavy lane and `foundation` kind, missing receipt IDs are fail-closed (`gz adr emit-receipt` exits 3 before attestation is recorded). Locked by `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py`; see `AGENTS.md` § Attestation.

```bash
uv run gz arb ruff
uv run gz validate --documents --surfaces
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Do Not

- Do not leave placeholder output examples.
- Do not update code without docs when command output changes.
- Do not declare completion without explicit human attestation. Attestation is **universal** — required for every OBPI completion regardless of kind, lane, or sensitivity (ADR-0.0.36). The prior "for heavy/foundation scope" qualifier described branching collapsed at ADR-0.0.36 and is retired.
- Do not cite bare `uv run gz lint` / `uv run mkdocs build --strict` as attestation evidence — they produce no `arb-*` receipt.
