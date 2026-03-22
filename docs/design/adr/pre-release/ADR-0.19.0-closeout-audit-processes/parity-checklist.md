# Cross-Project Parity Checklist: Closeout & Audit Pipelines

**ADR:** ADR-0.19.0-closeout-audit-processes
**OBPI:** OBPI-0.19.0-03
**Date:** 2026-03-22
**Scope:** Behavioral parity between gzkit (`gz closeout`, `gz audit`) and airlineops (`opsdev closeout`, `opsdev audit`)

> This checklist is a binding parity contract. Each row is a testable assertion.
> Parity means behavioral equivalence, not code sharing (REQ 7).
> No row defers verification to future work — the checklist itself is the verification instrument (REQ 8).

---

## 1. Closeout Pipeline Stage Parity

| Stage | gzkit (`gz closeout`) | airlineops (`opsdev closeout`) | Parity Status |
|-------|----------------------|-------------------------------|---------------|
| ADR resolution & canonicalization | Resolves ADR ID via ledger, resolves ADR file path from disk | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Pool ADR rejection | `_reject_pool_adr_for_lifecycle(adr_id, "closed out")` raises `GzCliError` | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Lane determination | Reads lane from ledger `adr_created` event (lite/heavy) | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| OBPI completion check | `_adr_closeout_readiness(obpi_rows)` returns `{ready, blockers, blocking_ids}` | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Verification step discovery | `_closeout_verification_steps(manifest, lane, project_root)` returns `[(label, command)]` | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Version sync check | `check_version_sync(project_root, adr_id)` returns `(current, target, needs_bump)` | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Closeout initiation event | `closeout_initiated_event()` appended to ledger | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Inline gate execution | `_run_closeout_quality_gates()` runs each step via `run_command()`, emits `gate_checked_event` per gate | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Gate result recording | `gate_checked_event(adr_id, gate_num, status, command, returncode)` per gate | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Attestation prompt | `_prompt_closeout_attestation()` presents 3 choices: Completed / Partial / Dropped | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Attestation recording | `attested_event(adr_id, status, by, reason)` appended to ledger | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Version bump | `sync_project_version(project_root, adr_ver)` updates pyproject.toml, `__init__.py`, README.md | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| ADR status transition | `lifecycle_transition_event(adr_id, "adr", "Proposed", "Completed"/"Dropped")` | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Closeout form generation | `_write_adr_closeout_form()` writes ADR-CLOSEOUT-FORM.md, updates attestation block | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |

### Closeout Verification Steps by Lane

| Lane | Gate | gzkit Command | airlineops Equivalent | Parity Status |
|------|------|--------------|----------------------|---------------|
| Lite | Gate 2 (TDD) | `uv run gz test` | `uv run opsdev test` (expected) | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Lite | Quality (Lint) | `uv run gz lint` | `uv run opsdev lint` (expected) | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Lite | Quality (Typecheck) | `uv run gz typecheck` | `uv run opsdev typecheck` (expected) | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Heavy | Gate 3 (Docs) | `uv run mkdocs build --strict` | `uv run mkdocs build --strict` (expected) | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Heavy | Gate 4 (BDD) | `uv run -m behave features/` | `uv run -m behave features/` (expected) | Gap — `ADR-pool.airlineops-direct-governance-migration` |

---

## 2. Audit Pipeline Stage Parity

| Stage | gzkit (`gz audit`) | airlineops (`opsdev audit`) | Parity Status |
|-------|-------------------|----------------------------|---------------|
| ADR resolution & canonicalization | Resolves ADR ID via ledger, resolves ADR file path | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Pool ADR rejection | `_reject_pool_adr_for_lifecycle(adr_id, "audited")` raises `GzCliError` | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Attestation guard | Checks `adr_info.get("attested") == True`; blocks if not attested | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Verification command discovery | `_manifest_verification_commands(manifest, include_docs=True)` returns `[(label, command)]` | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Audit directory creation | Creates `{adr-dir}/audit/` and `{adr-dir}/audit/proofs/` | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Verification command execution | `_run_audit_verifications()` runs each command via `run_command()`, captures output | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Proof file writing | Writes `{proofs_dir}/{label}.txt` with command, returncode, stdout, stderr | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| AUDIT_PLAN.md generation | Lists scope (ADR file), verification commands, proof output directory | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| AUDIT.md generation | Results table with PASS/FAIL per command, links to proof files | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Validation receipt emission | `audit_receipt_emitted_event()` appended to ledger (always, even on failure) | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| ADR status transition | `lifecycle_transition_event(adr_id, "adr", "Completed", "Validated")` — only if all checks pass | Not implemented | Gap — `ADR-pool.airlineops-direct-governance-migration` |

---

## 3. Exit Code Parity

| Condition | gzkit Exit Code | airlineops Exit Code (expected) | Parity Status |
|-----------|----------------|-------------------------------|---------------|
| **Closeout: all gates pass, attestation recorded, version bumped** | 0 | 0 | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Closeout: blocker (incomplete OBPIs)** | 1 | 1 | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Closeout: quality gate failure** | 1 | 1 | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Closeout: pool ADR rejection** | 1 (GzCliError) | 1 (expected) | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Closeout: invalid attestation selection** | 1 (GzCliError) | 1 (expected) | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Audit: all verifications pass** | 0 | 0 | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Audit: not attested (Gate 5 block)** | 1 | 1 | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Audit: verification command failure** | 1 | 1 | Gap — `ADR-pool.airlineops-direct-governance-migration` |

> Exit code semantics MUST be identical: 0 = full pipeline success, 1 = any blocker or failure. The same conditions produce the same exit code in both projects.

---

## 4. Error Message Parity

| Failure Mode | gzkit Error Message | airlineops Error Message (expected) | Parity Status |
|-------------|--------------------|------------------------------------|---------------|
| **Unattested ADR (audit)** | `"Audit blocked: human attestation is required first (Gate 5)."` with next-steps: `"uv run gz closeout {adr_id}"`, `"uv run gz attest {adr_id} --status completed"` | Same text with `opsdev` replacing `gz`: `"uv run opsdev closeout {adr_id}"`, `"uv run opsdev attest {adr_id} --status completed"` | Gap — Permitted Divergence (tool name only) — `ADR-pool.airlineops-direct-governance-migration` |
| **Incomplete OBPIs (closeout)** | `"Closeout blocked: {adr_id}"` with BLOCKERS list and next-steps | Same structure with `opsdev` replacing `gz` in next-step commands | Gap — Permitted Divergence (tool name only) — `ADR-pool.airlineops-direct-governance-migration` |
| **Gate failure (closeout)** | `"Closeout halted: {Gate Label} failed (exit {returncode})"` | Same text | Gap — Permitted Divergence (tool name only) — `ADR-pool.airlineops-direct-governance-migration` |
| **Pool ADR rejection** | `"Pool ADRs cannot be closed out: {adr_id}. Promote this ADR from pool first."` | Same text with `opsdev` context | Gap — Permitted Divergence (tool name only) — `ADR-pool.airlineops-direct-governance-migration` |
| **Missing ADR in ledger** | `"ADR not found in ledger: {adr_id}"` | Same text | Gap — Permitted Divergence (tool name only) — `ADR-pool.airlineops-direct-governance-migration` |
| **Invalid attestation input** | `"Invalid selection: {selection}. Expected 1, 2, or 3."` | Same text | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Reason required (partial/dropped)** | `"Reason required for {partial/dropped} attestation"` | Same text | Gap — `ADR-pool.airlineops-direct-governance-migration` |

> Permitted Divergence: tool name substitution (`gz` → `opsdev`) is the only allowed textual difference. Message structure, specificity, and next-step guidance must be identical.

---

## 5. Ledger Event Parity

| Event Type | gzkit Event Name | Evidence Schema (required fields) | airlineops Event Name (expected) | Parity Status |
|-----------|-----------------|----------------------------------|-------------------------------|---------------|
| Closeout initiation | `closeout_initiated` | `{by, mode, evidence: {adr_file, obpi_files, obpi_summary, verification_steps}}` | `closeout_initiated` | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Gate check result | `gate_checked` | `{gate, status, command, returncode}` | `gate_checked` | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Attestation | `attested` | `{status, by, reason}` | `attested` | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Lifecycle transition (closeout) | `lifecycle_transition` | `{content_type: "adr", from_state, to_state}` | `lifecycle_transition` | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Audit validation receipt | `audit_receipt_emitted` | `{receipt_event: "validated", attestor, evidence: {audit_date, pass_count, fail_count, audit_file, audit_plan_file, proofs_dir}}` | `audit_receipt_emitted` | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| Lifecycle transition (audit) | `lifecycle_transition` | `{content_type: "adr", from_state: "Completed", to_state: "Validated"}` | `lifecycle_transition` | Gap — `ADR-pool.airlineops-direct-governance-migration` |

> Event names MUST be semantically identical. Evidence schema shapes MUST have the same required fields. File path values will differ between projects (e.g., `src/gzkit/` vs `src/airlineops/`) — this is a permitted divergence.

---

## 6. Flag Behavior Parity

### `--dry-run` Flag

| Aspect | gzkit Behavior | airlineops Behavior (expected) | Parity Status |
|--------|---------------|-------------------------------|---------------|
| **Closeout: human output** | Shows gate plan, OBPI completion, version bump, attestation choices; no side effects | Same structure with `opsdev` tool references | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Closeout: JSON output** | `{adr, mode, dry_run, allowed, blockers, verification_steps, attestation_choices, version_sync}` | Same top-level keys | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Audit: human output** | Lists audit dir, proofs dir, commands to run, receipt emission, status transition | Same structure with `opsdev` tool references | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Audit: JSON output** | `{adr, dry_run, audit_dir, proofs_dir, commands, validation_receipt, status_transition}` | Same top-level keys | Gap — `ADR-pool.airlineops-direct-governance-migration` |

### `--json` Flag

| Aspect | gzkit Behavior | airlineops Behavior (expected) | Parity Status |
|--------|---------------|-------------------------------|---------------|
| **Closeout: success output** | `{adr, gate_results: [{label, command, returncode, success}], attestation: {status, by, reason}, version_sync: {current, target, needs_bump, files_updated}, status_transition: {from, to}}` | Same top-level keys and nesting | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Closeout: blocker output** | `{adr, mode, allowed: false, blockers: [...], next_steps: [...]}` | Same structure | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Audit: success output** | `{adr, audit_file, audit_plan_file, results: [{label, command, returncode, success, proof_file}], passed, validation_receipt: {event, attestor, evidence}, status_transition: {from, to}}` | Same top-level keys and nesting | Gap — `ADR-pool.airlineops-direct-governance-migration` |
| **Audit: not-attested output** | `{adr, allowed: false, reason, next_steps, dry_run}` | Same structure with `opsdev` in next-step commands | Gap — `ADR-pool.airlineops-direct-governance-migration` |

> JSON output MUST have structurally identical schemas: same field names, same nesting depth, same array shapes, same value types. File paths and tool names are permitted divergences.

---

## Verification Method

To verify parity once airlineops implements these commands:

```bash
# Closeout schema comparison
uv run gz closeout ADR-X.Y.Z --dry-run --json > /tmp/gzkit-closeout.json
cd ../airlineops && uv run opsdev closeout ADR-X.Y.Z --dry-run --json > /tmp/airlineops-closeout.json
diff <(jq 'keys | sort' /tmp/gzkit-closeout.json) <(jq 'keys | sort' /tmp/airlineops-closeout.json)

# Audit schema comparison
uv run gz audit ADR-X.Y.Z --dry-run --json > /tmp/gzkit-audit.json
cd ../airlineops && uv run opsdev audit ADR-X.Y.Z --dry-run --json > /tmp/airlineops-audit.json
diff <(jq 'keys | sort' /tmp/gzkit-audit.json) <(jq 'keys | sort' /tmp/airlineops-audit.json)

# Exit code comparison (gate failure scenario)
gz closeout ADR-failing --json; echo "gzkit exit: $?"
opsdev closeout ADR-failing --json; echo "airlineops exit: $?"
```

---

## Gap Summary

All 36 parity rows are currently **Gap** status. The entire closeout and audit command surface is missing from airlineops.

**Remediation:** `ADR-pool.airlineops-direct-governance-migration`

This pool ADR tracks the work to implement `opsdev closeout` and `opsdev audit` in airlineops with behavioral equivalence to gzkit. When that work completes, each row in this checklist should transition from Gap to Identical (or Permitted Divergence for tool-name substitutions).

### Permitted Divergence Rules

The following divergences are acceptable and do not count as parity violations:

1. **Tool name:** `gz` vs `opsdev` in command strings, error messages, and next-step guidance
2. **File paths:** `src/gzkit/` vs `src/airlineops/` in evidence and audit artifacts
3. **Package references:** `gzkit` vs `airlineops` in version file paths
4. **Module paths:** `src/gzkit/__init__.py` vs `src/airlineops/__init__.py` for version sync

All other behavioral differences (stage ordering, exit codes, event names, JSON keys, attestation choices, error message structure) are parity violations and must be remediated.
