---
id: OBPI-0.17.0-05-manifest-update-and-final-sync
parent: ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir
item: 5
lane: heavy
status: attested_completed
---

# OBPI-0.17.0-05-manifest-update-and-final-sync: Manifest Update and Final Sync

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir.md`
- **Checklist Item:** #5 - "Manifest Update and Final Sync"

**Status:** Draft

## Objective

Update `.gzkit/manifest.json` to include canonical `rules` and `schemas` paths introduced by OBPIs 02 and 04, fix stale mirror-only paths detected by `gz agent sync`, and verify all three control surface layers align after the full ADR-0.17.0 delivery.

## Lane

**heavy** - Inherited from parent ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir (heavy).

## Allowed Paths

- `src/gzkit/config.py` — Add canonical_rules and canonical_schemas to PathConfig
- `src/gzkit/sync.py` — Update generate_manifest() to emit rules/schemas entries
- `.gzkit/manifest.json` — Regenerated output
- `tests/test_sync.py` — Tests for manifest generation
- `tests/test_config.py` — Tests for new path config fields
- `.agents/skills/chore-runner/` — Remove stale mirror (naming mismatch)
- `.claude/skills/gz-obpi-lock/` — Promote to canonical or remove
- `.github/skills/AGENTS.md` — Remove stale file
- `docs/design/adr/pre-release/ADR-0.17.0-*/obpis/OBPI-0.17.0-05-*.md` — This brief

## Denied Paths

- Other OBPI briefs in this ADR
- CI files, lockfiles
- New dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Manifest must include `canonical_rules` and `canonical_schemas` entries in `control_surfaces`
2. REQUIREMENT: PathConfig must declare paths for `.gzkit/rules` and `.gzkit/schemas`
3. REQUIREMENT: `generate_manifest()` output must include the new entries
4. NEVER: Leave stale mirror-only paths after final sync
5. ALWAYS: Run `gz agent sync control-surfaces` with zero recovery warnings after cleanup

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Acceptance Criteria

- REQ-0.17.0-05-01: PathConfig includes `canonical_rules` and `canonical_schemas` fields
- REQ-0.17.0-05-02: `generate_manifest()` emits `canonical_rules` and `canonical_schemas` in control_surfaces
- REQ-0.17.0-05-03: Stale mirror-only paths resolved (zero recovery warnings from sync)
- REQ-0.17.0-05-04: `gz agent sync control-surfaces` runs clean
- REQ-0.17.0-05-05: Unit tests cover new manifest entries

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz agent sync control-surfaces
```

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 694 tests in 9.488s — OK
New tests: test_manifest_includes_canonical_rules_and_schemas,
test_manifest_control_surfaces_complete, test_gzkit_paths (updated)
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
uv run gz validate --documents — All validations passed
```

### Gate 3 (Docs)

```text
N/A — no command docs or runbook changes required for manifest-internal update
```

### Gate 4 (BDD)

```text
N/A — no BDD scenarios for manifest generation
```

### Gate 5 (Human)

```text
Attestor: jeff
Attestation: attest completed
Date: 2026-03-19
```

### Value Narrative

Before this OBPI, the manifest did not reflect the canonical `rules` and `schemas` directories added by OBPIs 02 and 04, and stale mirror-only paths caused sync warnings. After completion, the manifest is complete, all three control surface layers align, and `gz agent sync` runs with zero recovery warnings.

### Key Proof

```text
$ uv run -m unittest tests.test_sync.TestGenerateManifest.test_manifest_includes_canonical_rules_and_schemas -v
test_manifest_includes_canonical_rules_and_schemas ... ok
Ran 1 test in 0.001s — OK

$ python -c "import json; cs=json.load(open('.gzkit/manifest.json'))['control_surfaces']; print(cs['canonical_rules'], cs['canonical_schemas'])"
.gzkit/rules .gzkit/schemas

$ uv run gz agent sync control-surfaces
Sync complete.  # zero recovery warnings
```

### Implementation Summary

- Files modified: config.py, sync.py, cli.py, test_sync.py, test_config.py, test_audit.py
- Files created: .gzkit/skills/gz-obpi-lock/SKILL.md (promoted from mirror)
- Tests added: 2 new manifest tests + 1 updated PathConfig test
- Date completed: 2026-03-19
- Attestation status: Completed (human attested 2026-03-19)
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `human:jeff`
- Attestation: attest completed — manifest updated with canonical_rules and canonical_schemas, stale mirrors cleaned, gz-obpi-lock promoted to canonical, sync runs clean
- Date: 2026-03-19

---

**Brief Status:** Completed

**Date Completed:** 2026-03-19

**Evidence Hash:** -
