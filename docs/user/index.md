# gzkit

Keep humans in the loop when AI writes code.

---

## Two Operator Surfaces

gzkit exposes two parallel surfaces for every operator moment:

| Surface | Syntax | When to use |
|---------|--------|-------------|
| **CLI commands** | `gz <verb>` | Terminal sessions, CI pipelines, scripts |
| **Skills** | `/gz-<name>` | Claude Code sessions — adds interviews, forcing functions, governance validation |

Skills are not optional wrappers around CLI commands. They carry governance
logic the CLI assumes has already happened: design interviews, quality
scoring, semantic authoring, and pipeline orchestration. When a skill exists
for your current workflow step, use it.

---

## Operational Contract

gzkit enforces a ledger-first GovZero workflow:

| Step | CLI | Skill |
|------|-----|-------|
| 1. Record intent | `gz prd`, `gz plan`, `gz specify` | `/gz-prd`, `/gz-plan`, `/gz-obpi-specify` |
| 2. Execute and verify | `gz obpi pipeline`, `gz gates` | `/gz-obpi-pipeline`, `/gz-gates` |
| 3. Reconcile closeout readiness | `gz obpi reconcile`, `gz adr audit-check` | `/gz-obpi-reconcile` |
| 4. Present closeout evidence | `gz closeout` | `/gz-adr-closeout-ceremony` |
| 5. Record human attestation | `gz attest` | (CLI only — human act) |
| 6. Reconcile post-attestation | `gz audit` | `/gz-adr-audit` |
| 7. Record receipts | `gz obpi emit-receipt`, `gz adr emit-receipt` | `/gz-adr-emit-receipt` |

---

## Start Here

- [Quickstart](quickstart.md) — One full cycle, start to finish
- [Runbook](runbook.md) — Daily operational loops
- [Skills](skills/index.md) — Skill reference (governance logic lives here)
- [Commands](commands/index.md) — CLI command reference
- [Canonical GovZero docs](../governance/GovZero/charter.md)

---

## Flow

```text
gz init -> gz prd -> gz plan -> gz specify -> gz obpi pipeline -> gz obpi emit-receipt -> gz obpi reconcile -> gz adr audit-check -> gz closeout -> gz attest -> gz audit -> gz adr emit-receipt
```
