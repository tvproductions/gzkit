<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Governance Runbook (gzkit)

**Purpose:** Operator procedures for executing GovZero workflows in gzkit: ADR/OBPI lifecycle work, reconciliation, closeout, audit, and parity maintenance.

**Version:** GovZero v6 extraction surface
**Scope:** Governance operations in this repository
**Companion:** [Operator Runbook](../user/runbook.md) (daily execution loop)

This document is procedural ("how to"), not policy ("what the rules are"). Canonical policy remains in `docs/governance/GovZero/**`.

---

## Governance Quick Reference

### Status and health

```bash
uv run gz status --table
uv run gz adr status ADR-<X.Y.Z> --json
uv run gz state --json
uv run gz adr audit-check ADR-<X.Y.Z>
uv run gz gates --adr ADR-<X.Y.Z>
```

### Lifecycle execution

```text
/gz-adr-create
/gz-adr-manager   # compatibility alias for /gz-adr-create
/gz-obpi-brief
/gz-obpi-reconcile ADR-<X.Y.Z>
/gz-adr-recon ADR-<X.Y.Z>
/gz-adr-sync
```

### Validation and proof surfaces

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz validate --documents --surfaces
uv run mkdocs build --strict
```

---

## Concepts

### Gate system

| Gate | Name | Verification |
|---|---|---|
| 1 | ADR recorded | `uv run gz validate --documents` |
| 2 | TDD | `uv run gz test` |
| 3 | Docs | `uv run gz lint` + `uv run mkdocs build --strict` |
| 4 | BDD | `features/` scenarios if present |
| 5 | Human attestation | `uv run gz attest ADR-<X.Y.Z> --status completed` |

Lane rule: `lite` requires Gates 1-2; `heavy` requires Gates 1-5.

### Layered trust

| Layer | Trust source | Typical tooling |
|---|---|---|
| 1 | Runtime evidence generation | `gz implement`, `gz gates`, `gz adr audit-check` |
| 2 | Ledger-driven reconciliation | `/gz-obpi-reconcile`, `/gz-adr-recon`, `gz audit` |
| 3 | File sync and indexing | `/gz-obpi-sync`, `/gz-adr-sync`, `gz agent sync control-surfaces` |

### OBPI discipline

- OBPI is the atomic implementation unit.
- ADR status is a roll-up of OBPI completion plus attestation.
- Heavy or Foundation parent ADRs require explicit human attestation before OBPI/ADR completion claims.

---

## Workflow: Create or Promote ADR

**When:** New governance work must be planned.

1. Inspect active and pending ADR state.

```bash
uv run gz status --table
```

2. If promoting from pool, use deterministic promotion.

```bash
uv run gz adr promote ADR-pool.<slug> --semver X.Y.Z --status proposed
```

3. Create or update OBPI briefs for checklist items.

```text
/gz-obpi-brief
```

4. Validate artifact and document integrity.

```bash
uv run gz validate --documents
uv run gz check-config-paths
```

---

## Workflow: OBPI Increment

**When:** Implementing one checklist item.

1. Orient on current state.

```bash
uv run gz adr status ADR-<X.Y.Z> --json
uv run gz status --table
```

2. Implement + verify Gate 2 (+ Gate 3 when docs changed).

```bash
uv run gz implement --adr ADR-<X.Y.Z>
uv run gz gates --adr ADR-<X.Y.Z>
uv run gz lint
```

3. Update brief evidence fields (implementation summary must be concrete and parser-safe).
4. Emit OBPI completion receipt with explicit attestor evidence.

```bash
uv run gz obpi emit-receipt OBPI-<X.Y.Z-NN>-<slug> --event completed --attestor "<Human Name>" --evidence-json '{"attestation":"I attest I understand the completion of OBPI-<X.Y.Z-NN>.","date":"YYYY-MM-DD"}'
```

---

## Workflow: Reconciliation and Drift Detection

**When:** Before closeout, after multi-session work, or when status drift is suspected.

Run in trust order:

```text
/gz-obpi-reconcile ADR-<X.Y.Z>   # Layer 2
/gz-adr-recon ADR-<X.Y.Z>        # Layer 2
/gz-adr-sync                     # Layer 3
```

Then verify no unresolved evidence gaps:

```bash
uv run gz adr audit-check ADR-<X.Y.Z>
uv run gz adr status ADR-<X.Y.Z> --json
```

If `audit-check` fails, fix the referenced OBPI brief evidence and rerun until PASS.

---

## Workflow: ADR Closeout and Audit

**When:** All linked OBPIs are completed and evidenced.

1. Pre-closeout blocking check.

```bash
uv run gz adr audit-check ADR-<X.Y.Z>
```

2. Closeout ceremony initiation (dry-run first, then live).

```bash
uv run gz closeout ADR-<X.Y.Z> --dry-run
uv run gz closeout ADR-<X.Y.Z>
```

3. Human attestation.

```bash
uv run gz attest ADR-<X.Y.Z> --status completed
```

4. Post-attestation audit and accounting.

```bash
uv run gz audit ADR-<X.Y.Z>
uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated --attestor "<Human Name>" --evidence-json '{"scope":"ADR-<X.Y.Z>","date":"YYYY-MM-DD"}'
```

Rules:

- Do not run `gz audit` before attestation.
- Do not treat passing checks as implied attestation.
- Record attestation terms explicitly (`Completed`, `Completed — Partial: <reason>`, `Dropped — <reason>`).

---

## Workflow: Session Handoffs

**When (MUST):**

- Session ending with incomplete OBPI work
- Scope switch between ADRs
- Explicit human request

**Procedure:**

```text
/gz-session-handoff CREATE
/gz-session-handoff RESUME
```

Staleness handling:

- `Fresh` (<24h) resume directly.
- `Slightly stale` (24-72h) resume with explicit verification.
- `Stale` (>72h) or `Very stale` (>7d) require human re-validation before proceeding.

---

## Workflow: Parity Maintenance Against AirlineOps

**When:** Weekly cadence, before pool ADR promotion, or after canonical governance changes in AirlineOps.

Filter rule:

- Apply the [Parity Intake Rubric](parity-intake-rubric.md) to each candidate import before implementation.

1. Resolve canonical root deterministically and fail closed.

```bash
test -d ../airlineops && test -d .
```

2. Run parity-scan ritual checks.

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz adr audit-check ADR-<target>
uv run mkdocs build --strict
```

3. Write dated reports.

- `docs/proposals/REPORT-airlineops-parity-YYYY-MM-DD.md`
- `docs/proposals/REPORT-airlineops-govzero-mining-YYYY-MM-DD.md`

4. Convert each `Missing`, `Divergent`, or high-impact `Partial` item into tracked ADR/OBPI follow-up.

Compatibility note:

- `gz-adr-create` is canonical in gzkit.
- `gz-adr-manager` is retained as a legacy alias for cross-repository parity.

---

## Workflow: Git Sync Ritual

```bash
uv run gz git-sync
uv run gz git-sync --apply --lint --test
```

Rules:

- No `--no-verify`.
- No force push.
- Keep governance docs, runbook, and command references synchronized in the same change set.

---

## Workflow: Readiness-Driven Design

```bash
uv run gz readiness audit
uv run gz readiness audit --json > docs/proposals/AUDIT-agent-readiness-gzkit-YYYY-MM-DD.json
```

Use readiness as a design input, not a one-time score:

1. Run `gz readiness audit` before parity extraction or major governance edits.
2. Capture a dated audit artifact in `docs/proposals/`.
3. Convert the top three gaps into tracked ADR/OBPI follow-up work.
4. Use Gate 2 (TDD) and Gate 4 (BDD) evidence as primary inputs for acceptance/evaluation improvements.
5. Re-run readiness after implementation and record score delta in the same proposal.
6. Only claim maturity improvements when quality gates (`gz check`) also pass.

---

## Quick Governance Checklist

### Before starting OBPI work

- [ ] `uv run gz status --table`
- [ ] `uv run gz adr status ADR-<X.Y.Z> --json`
- [ ] Brief scope and acceptance criteria reviewed
- [ ] Existing handoff reviewed if present

### Before requesting ADR closeout

- [ ] `/gz-obpi-reconcile ADR-<X.Y.Z>` complete
- [ ] `/gz-adr-recon ADR-<X.Y.Z>` complete
- [ ] `uv run gz adr audit-check ADR-<X.Y.Z>` passes
- [ ] `uv run gz closeout ADR-<X.Y.Z> --dry-run` reviewed

### After closeout

- [ ] `uv run gz attest ADR-<X.Y.Z> --status completed`
- [ ] `uv run gz audit ADR-<X.Y.Z>`
- [ ] ADR-level receipt emitted
- [ ] `/gz-adr-sync` run

---

## Reference Links

- [GovZero Charter](GovZero/charter.md)
- [ADR Lifecycle](GovZero/adr-lifecycle.md)
- [Audit Protocol](GovZero/audit-protocol.md)
- [Agent Readiness Audit Template](GovZero/audits/AUDIT-TEMPLATE-agent-readiness.md)
- [Agent-Era Prompting Summary (Nate B. Jones)](GovZero/agent-era-prompting-summary.md)
- [Gate 5 Architecture](GovZero/gate5-architecture.md)
- [Layered Trust](GovZero/layered-trust.md)
- [Session Handoff Obligations](GovZero/session-handoff-obligations.md)
- [Staleness Classification](GovZero/staleness-classification.md)
