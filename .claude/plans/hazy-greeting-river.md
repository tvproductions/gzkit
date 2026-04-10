# Plan: OBPI-0.25.0-14 — OS Pattern (Exclude)

## Context

OBPI-0.25.0-14 evaluates whether airlineops's `common/os.py` (241 lines) should be absorbed into gzkit. The module provides UNC/SMB share path parsing, macOS mount enumeration, and SMB guest mount refresh. gzkit has no equivalent module — only a cross-platform development policy rule and scattered `path.replace("\\", "/")` normalization. The airlineops module is entirely deployment-environment-specific (airline network shares on macOS), not generic infrastructure. **Decision: Exclude.**

## Critical Files

- **Source under review:** `../airlineops/src/airlineops/common/os.py` (241 lines)
- **gzkit comparison point:** `.claude/rules/cross-platform.md` (policy only, no code)
- **Brief to update:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-14-os-pattern.md`
- **Completed Exclude example:** same ADR's `obpis/OBPI-0.25.0-03-signature-pattern.md`

## Implementation Steps

### Step 1: Update the OBPI brief with Exclude decision

Edit `obpis/OBPI-0.25.0-14-os-pattern.md` to add:

1. **DECISION section** — "Exclude" with rationale: the module is entirely UNC/SMB share handling (mount enumeration, UNC path parsing, SMB mount refresh). gzkit works with local files and has no UNC/SMB use case. The only generic parts (`is_macos()`, `is_windows()`) are trivial one-liners that don't justify a module.

2. **COMPARISON ANALYSIS** — Dimension table covering:
   - Purpose (SMB/UNC handling vs no equivalent)
   - Mount enumeration (`iter_mounts()` — macOS `/Volumes/` only)
   - UNC parsing (`parse_unc_share()`, `UncShare` NamedTuple)
   - UNC resolution (`resolve_unc_mount()`, `resolve_unc_path()`, `normalize_unc_path()`)
   - SMB refresh (`refresh_macos_guest_smb_mount()` — shell subprocess to `mount_smbfs`)
   - Platform detection (`is_macos()`, `is_windows()` — trivial)
   - Cross-platform policy (gzkit has policy rule + pathlib usage, not a code module)
   - Subtraction test result

3. **GATE 4 BDD: N/A Rationale** — Exclude decision, no operator-visible behavior change

4. **Quality Gates checkboxes** — Mark Gates 1-4 as checked, Gate 5 pending

5. **Acceptance Criteria** — Mark REQ-01 through REQ-05 as satisfied

6. **Evidence sections** — Gate 1, Gate 2, Code Quality, Value Narrative, Key Proof, Implementation Summary

7. **Closing Argument** — Synthesize the Exclude decision

### Step 2: Run verification checks

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
```

No code changes, so these confirm the existing suite remains green.

## Verification

- Brief records "Exclude" decision with comparison rationale
- All 5 REQs addressed in Acceptance Criteria
- All quality gates marked (Gate 5 pending human attestation)
- `uv run gz test` passes (no code changes)
- `uv run gz lint` clean
