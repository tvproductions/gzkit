# Operator Runbook

This runbook is a primary proof artifact for gzkit.

Gate 3 is only satisfied when all three proof surfaces are current:

1. User documentation
2. Command manpages (`docs/user/commands/*.md`)
3. This runbook

---

## Purpose

Use this runbook to execute and verify the governance workflow end to end.

If behavior changes, update this file in the same change.

---

## Proof Checklist

For Heavy lane work, verify all items:

- [ ] User docs describe the current workflow and outcomes
- [ ] Command manpages match current command flags and examples
- [ ] Runbook commands still execute as written
- [ ] Latest AirlineOps parity report is no older than 14 days
- [ ] `uv run mkdocs build --strict` passes
- [ ] `uv run gz lint` passes

---

## Standard Verification Flow

```bash
# 1) Check current gate status
uv run gz status

# 2) Run required gates
uv run gz gates

# 3) Validate docs proof surface
uv run mkdocs build --strict
uv run gz lint

# 4) Observe closeout steps directly (Heavy lane)
uv run gz closeout ADR-<X.Y.Z>

# 5) Human attestation
uv run gz attest ADR-<X.Y.Z> --status completed
```

---

## Parity Cadence

Run a parity scan at least weekly and before promoting pool ADRs:

1. Use skill: `$airlineops-parity-scan`
2. Produce: `docs/proposals/REPORT-airlineops-parity-YYYY-MM-DD.md`
3. Use template: `docs/proposals/REPORT-TEMPLATE-airlineops-parity.md`

Do not promote an ADR from pool unless a parity report exists from the last 14 days.

---

## Update Rules

- Update runbook steps whenever command behavior changes.
- Do not mark work complete if any step here is stale.
- Keep examples deterministic and runnable with `uv run`.
