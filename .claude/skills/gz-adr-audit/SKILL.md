---
name: gz-adr-audit
description: Gate-5 audit templates and procedure for ADR verification. GovZero v6 skill.
compatibility: GovZero v6 framework; provides audit procedure for COMPLETED→VALIDATED ADR transition
metadata:
  skill-version: "6.3.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/audit-protocol.md"
  govzero-gates-covered: "Gate 5 (Human Attestation)"
  govzero_layer: "Layer 2 — Ledger Consumption"
  trust_model: "Trusts Layer 1 ledger proof; does NOT re-verify evidence"
gz_command: audit
invocation: uv run gz audit <adr-id>
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-adr-audit

Execute reproducible ADR verification to move from COMPLETED → VALIDATED.

**Two-phase workflow:** See [AGENTS.md](../../../AGENTS.md) § Two-Phase ADR Workflow

---

## Layer 2 Trust Model

This is a **Layer 2** tool — it consumes proof from the ledger rather than re-running verification commands.

**Trust Chain:**

1. **Layer 1 tools** (`gz-obpi-audit`, `gz-adr-verification`) run tests, check coverage, validate evidence
2. **Layer 1 writes proof** to `logs/obpi-audit.jsonl` with status entries
3. **This tool reads proof** — if all briefs show PASS/Completed, skip re-verification
4. **Gate 5 attests** to the presence of proof, not re-execution

**Why trust the ledger?**

- Re-running tests in Layer 2 duplicates Layer 1 work
- Gate 5's job is to verify *proof exists*, not regenerate proof
- Human attestation observes artifacts, not re-executes them

**When to force re-verification:**

- If ledger entries are older than 7 days (staleness threshold)
- If you suspect ledger corruption or tampering
- If Layer 1 tools have been updated since last audit

In these cases, run `uv run gz audit <adr-id>` first to regenerate ledger proof.

---

## Assets

- `assets/AUDIT_PLAN.template.md` — Plan scaffold (scope, checks, risk focus)
- `assets/AUDIT.template.md` — Annotation shell (✓/✗/⚠, summary, attestation)

---

## Audit Procedure

**Prerequisite:** ADR is COMPLETED (all briefs done, tests/coverage/docs pass).

### 1. Plan

```bash
ADR_DIR=docs/design/adr/adr-x.y.x/ADR-x.y.z-slug
mkdir -p "${ADR_DIR}/audit/proofs"
```

- Read ADR prose, extract all claims
- Create `audit/AUDIT_PLAN.md` with checks for each claim
- Run `uv run gz cli audit` for governance issues
- Legacy note: `docs/design/audit/**` remains historical only; new audits live under the ADR folder.

### 2. Verify Ledger Completeness

Before running any commands, check ledger proof:

```bash
uv run gz adr audit-check <adr-id>
```

**If ledger is complete (all briefs PASS):**

- Skip to Step 3 (Demonstrate Value) — no re-verification needed
- Trust Layer 1 proof from obpi-audit
- Record "Ledger proof verified" in audit notes

**If ledger is incomplete or missing:**

- Run: `uv run gz audit <adr-id>`
- This will audit all briefs and write ledger entries
- Return to Step 2 after reconciliation

**Force re-verification (optional):**

If you need to regenerate proof (staleness, suspicion, etc.), run the validation commands:

```bash
uv run -m unittest -q > "${ADR_DIR}/audit/proofs/unittest.txt" 2>&1
uv run mkdocs build -q > "${ADR_DIR}/audit/proofs/mkdocs.txt" 2>&1
uv run gz gates --adr <adr-id> > "${ADR_DIR}/audit/proofs/gates.txt" 2>&1
```

Record ✓/✗/⚠ outcomes for each check.

### 3. Demonstrate Value (MANDATORY)

**An audit that only verifies mechanical checks (tests pass, coverage met) without demonstrating what the ADR delivers is incomplete.**

This step shows the ADR's achieved capabilities through live commands. It answers: "What can the operator do now that they couldn't before?"

**Procedure:**

1. **Summarize the ADR's delivered capabilities** — 3-5 bullet points of what the ADR enables
2. **Run product surface commands** that exercise each capability:
   - Use `gz` CLI commands, not ad-hoc scripts
   - Show actual output (not "tests pass" — show the *feature working*)
   - For foundation/0.0.x ADRs with no CLI surface: show the tool/library in action via its integration point
3. **Include a "Feature Demonstration" section in `audit/AUDIT.md`** with:
   - Each capability named
   - The command run and representative output
   - A value summary explaining *why this matters*

**Examples of good demonstrations:**

- Reconciliation ADR → run `uv run gz adr status ADR-<x.y.z>`, show the warnings panel
- Adapter ADR → run the ingest command, show data flowing through
- Schema ADR → show validation catching bad input

**Examples of BAD audits (what this step prevents):**

- "121 tests pass, coverage 47%, lint clean" — this is verification, not demonstration
- Alignment check saying "ALIGNED" without showing the feature running
- Audit that could apply to *any* ADR because it never mentions this ADR's specific capabilities

**Relationship to closeout ceremony:** If a full closeout ceremony (`/gz-adr-closeout-ceremony`) is being run, its Step 4 (Runbook Walkthrough) satisfies this requirement. If the audit is standalone (no ceremony), this step is mandatory and cannot be skipped.

### 4. Document

Populate `audit/AUDIT.md` with:

- **Feature Demonstration** section (from Step 3 — capabilities, commands, output, value)
- Execution log (✓/✗/⚠ per check)
- Evidence index (links to proof files)
- Summary table (completeness, integrity, alignment)

### 5. Identify Shortfalls

Review for:

- Incomplete implementations (claimed features not shipped)
- Misalignments (code ≠ docs ≠ tests)
- Missing value demonstration (feature never shown working)
- Unexplained anomalies

### 6. Remediate

For each shortfall:

- Severity (blocking/non-blocking)
- Proposed fix
- Effort estimate

Implement fixes, re-validate, update `AUDIT.md`.

### 7. Mark VALIDATED

When all shortfalls resolved:

- Sign attestation: human name + date
- Update ADR: `Status: Validated`

### 8. Emit Validation Receipt

After a successful audit, emit a validation receipt to the ADR ledger for temporal anchoring:

```bash
# Emit "validated" receipt (after Gate 5 attestation)
uv run gz adr emit-receipt <adr-id> --event validated \
  --attestor "human:<name>" \
  --evidence '{"gate": 5, "tests_passed": true, "coverage_pct": 48.5}'

# Emit "completed" receipt (when marking ADR as Completed, pre-validation)
uv run gz adr emit-receipt <adr-id> --event completed \
  --attestor "human:<name>" \
  --evidence '{"briefs_completed": 6}'
```

**Rules:**

- **Audit fails → no receipt.** Only emit after all shortfalls are resolved.
- **Idempotent:** Running twice produces two ledger entries (audit trail preserved).
- **Git unavailable:** Command warns but returns exit code 0 (doesn't fail the audit).

**Recommended evidence fields:**

| Field | Type | Description |
|-------|------|-------------|
| `gate` | int | Gate number (e.g., 5) |
| `tests_passed` | bool | Whether unit tests passed |
| `coverage_pct` | float | Coverage percentage |
| `briefs_completed` | int | Number of briefs completed |
| `shortfalls_resolved` | int | Number of shortfalls fixed |

---

## Validation Commands

| Type | Command | Layer |
|------|---------|-------|
| **Ledger check** | `uv run gz adr audit-check <adr-id>` | L2 |
| Unit tests | `uv run -m unittest -q` | L1 |
| Docs build | `uv run mkdocs build -q` | L1 |
| Governance | `uv run gz cli audit` | L1 |
| ADR status | `uv run gz adr status <adr-id>` | L1 |
| Config paths | `uv run gz check-config-paths` | L1 |
| Heavy gates | `uv run gz gates --adr <adr-id>` | L1 |
| CLI audit | `uv run gz cli audit` | L1 |
| OBPI reconcile | `uv run gz audit <adr-id>` | L1+L2 |
| **Emit receipt** | `uv run gz adr emit-receipt <adr-id> --event validated` | L2 |

**Layer key:** L1 = runs verification, L2 = reads ledger proof

---

## Gate Checklist

**COMPLETED (Phase 1):**

- [ ] All features shipped
- [ ] Unit tests pass, coverage ≥40%
- [ ] Docs complete, mkdocs builds clean
- [ ] Linting/formatting/type checks pass

**VALIDATED (Phase 2):**

- [ ] Audit plan created
- [ ] All checks executed with proofs
- [ ] **Value demonstrated** — ADR capabilities shown working with live output
- [ ] No unresolved ✗ failures
- [ ] Code matches documentation
- [ ] Examples are executable
- [ ] Validation receipt emitted to ledger
- [ ] Attestation signed

---

## Failure Modes

- **Mechanical-only audit** — tests pass and coverage met but the feature is never demonstrated working. The human cannot assess value from a checklist of green checkmarks alone.
- Audits drift from template structure
- No proof artifacts captured
- Shortfalls not remediated before marking VALIDATED
- Audit skips Step 3 (Demonstrate Value) and jumps straight to documentation

---

## Relationship to Closeout Ceremony

`gz-adr-audit` and `gz-adr-closeout-ceremony` are **complementary but independent**:

| Concern | gz-adr-audit | gz-adr-closeout-ceremony |
|---------|-------------|--------------------------|
| **Focus** | Evidence verification + value demonstration | Human-witnessed runbook walkthrough |
| **Mode** | Agent-driven with human attestation | Human-driven with agent presenting |
| **Outputs** | AUDIT.md + proofs/ + ledger entries | Closeout form + attestation record |
| **Value demo** | Step 3 (agent demonstrates) | Step 4 (human walks through runbook) |

**If both are run:** The closeout ceremony's Step 4 (Runbook Walkthrough) satisfies the audit's Step 3 (Demonstrate Value). No duplication needed.

**If only audit is run:** Step 3 is mandatory. The agent must demonstrate value, not just verify mechanics.
