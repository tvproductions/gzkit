# ADR Closeout Form: ADR-0.1.0

**Status**: Phase 1 — Pre-Attestation

---

## Pre-Attestation Checklist

Before requesting attestation, verify:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Documentation builds (`uv run mkdocs build --strict`)
- [ ] Gate 4 (BDD): Acceptance scenarios pass (if applicable)
- [ ] Code reviewed

## Evidence Paths

<!-- Agent presents these paths; human executes and observes -->

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/adr-0.1.x/ADR-0.1.0-enforced-governance-foundation/` |
| Gate 2 | Tests pass | `uv run -m unittest discover tests` |
| Gate 3 | Docs build | `uv run mkdocs build --strict` |
| Gate 4 | BDD passes | (deferred to 0.2.0) |
| Gate 5 | Human attests | This form |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.1.0-01](briefs/OBPI-0.1.0-01-gz-init.md) | Implement `gz init` | Pending |
| [OBPI-0.1.0-02](briefs/OBPI-0.1.0-02-gz-prd.md) | Implement `gz prd` | Pending |
| [OBPI-0.1.0-03](briefs/OBPI-0.1.0-03-gz-constitute.md) | Implement `gz constitute` | Pending |
| [OBPI-0.1.0-04](briefs/OBPI-0.1.0-04-gz-specify.md) | Implement `gz specify` | Pending |
| [OBPI-0.1.0-05](briefs/OBPI-0.1.0-05-gz-plan.md) | Implement `gz plan` | Pending |
| [OBPI-0.1.0-06](briefs/OBPI-0.1.0-06-gz-state.md) | Implement `gz state` | Pending |
| [OBPI-0.1.0-07](briefs/OBPI-0.1.0-07-gz-status.md) | Implement `gz status` | Pending |
| [OBPI-0.1.0-08](briefs/OBPI-0.1.0-08-gz-attest.md) | Implement `gz attest` | Pending |
| [OBPI-0.1.0-09](briefs/OBPI-0.1.0-09-ledger-writer-hook.md) | Implement ledger-writer hook | Pending |
| [OBPI-0.1.0-10](briefs/OBPI-0.1.0-10-templates.md) | Create templates | Pending |

## Human Attestation

**IMPORTANT**: The human must execute the commands above and observe directly.
Do not trust agent summaries. Run the commands. See the output.

### Attestation (choose one):

- [ ] **Completed** — All work finished; all claims verified
- [ ] **Completed — Partial**: _______________
- [ ] **Dropped**: _______________

**Attested by**: _______________
**Date**: _______________

---

## Post-Attestation (Phase 2)

After attestation, run:

```bash
gz attest ADR-0.1.0 --status <completed|partial|dropped> [--reason "..."]
```

Then the audit phase begins automatically.
