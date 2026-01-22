# ADR Closeout Form: {adr_id}

**Status**: Phase 1 — Pre-Attestation

---

## Pre-Attestation Checklist

Before requesting attestation, verify:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
{heavy_gates}
- [ ] Code reviewed

## Evidence Paths

<!-- Agent presents these paths; human executes and observes -->

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `{adr_path}` |
| Gate 2 | Tests pass | `uv run -m pytest tests/` |
{heavy_evidence}

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
gz attest {adr_id} --status <completed|partial|dropped> [--reason "..."]
```

Then the audit phase begins automatically.
