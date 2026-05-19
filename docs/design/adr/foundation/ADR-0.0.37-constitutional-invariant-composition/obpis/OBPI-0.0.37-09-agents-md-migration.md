---
id: OBPI-0.0.37-09-agents-md-migration
parent: ADR-0.0.37-constitutional-invariant-composition
item: 9
lane: Heavy
status: Draft
---

# OBPI-0.0.37-09-agents-md-migration: AGENTS.md Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #9 — "OBPI-0.0.37-09 — AGENTS.md migration (register existing AGENTS.md content as constitutional invariants; render AGENTS.md from registry; lock the inversion in CI)"

**Status:** Draft

## Objective

Migrate every existing AGENTS.md section into a constitutional invariant registered under `.gzkit/invariants/`, then re-render AGENTS.md from the registry via OBPI-02's renderer, then lock the inversion: `gz validate --invariant-coherence` (OBPI-03) becomes part of CI; future hand-edits to AGENTS.md fail-close. This is the test of the framework — without it, CIC-1 ships as theater.

## Lane

**Heavy** — Rewrites `AGENTS.md` (the universal agent contract) and adds CI enforcement. The most blast-radius surface in the project. Heavy + foundation + universal Gate 5 per ADR-0.0.36.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` (parent reference; read-only)
- `AGENTS.md` (rewritten from registry output via OBPI-02 renderer)
- `.gzkit/invariants/*.yaml` (new entries — one per migrated AGENTS.md section)
- `.gzkit/invariants/MIGRATION-MANIFEST.md` (new) — per-section → invariant-id mapping for traceability
- `src/gzkit/templates/agents.md` (modify) — template body updated to consume rendered invariant slots from OBPI-02
- `src/gzkit/templates/adr.md` (modify) — adjacent template surface for future composition targets
- `src/gzkit/sync_surfaces.py` (modify) — AGENTS.md regeneration path must call into OBPI-02 renderer when the registry is present (sync becomes a renderer wrapper)
- `tests/governance/test_invariant_coherence.py` (modify) — add migration round-trip test: parse pre-migration AGENTS.md sections, assert each section's canonical claim text appears in some registered invariant
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-09-agents-md-migration.md` (this brief)

## Denied Paths

- Paths not listed in Allowed Paths
- `CLAUDE.md` (operator-facing summary that includes `@AGENTS.md` — out of scope here; if it ever becomes a composition target, that's a future feature ADR)
- `.claude/rules/*.md`, `.gzkit/rules/*.md` (rules are separate canon surface — out of scope; covered by future feature ADR per ADR § Scope boundary)
- Skill READMEs, persona files (forward-references per ADR § Scope boundary)
- CI workflow files (CI lock for `gz validate --invariant-coherence` lands via existing `gz check` inclusion in OBPI-03; this OBPI does not modify `.github/workflows/`)
- CI files (other), lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Every section in pre-migration AGENTS.md (every H2 heading and its content) is analyzed and either:
   - (a) registered as one constitutional invariant in `.gzkit/invariants/<slug>.yaml` with a non-empty `structural_witness` array, OR
   - (b) explicitly downgraded out of AGENTS.md if no structural witness is available (downgraded content moves to a rule file under `.gzkit/rules/` or to a runbook). Downgrade decisions are recorded in `MIGRATION-MANIFEST.md` with rationale.
2. REQUIREMENT: `MIGRATION-MANIFEST.md` is the migration audit trail: a table of (pre-migration AGENTS.md § heading, action: register|downgrade, target: invariant-id or rule path, rationale).
3. REQUIREMENT: Per ADR § Consequences Negative #2 (mitigation against "theater of structure"): every migrated invariant MUST have at least one assertion-bearing test in `tests/governance/` whose assertion enforces the invariant. An invariant with placeholder `structural_witness` and no enforcing test counts as a migration failure.
4. REQUIREMENT: After migration, `uv run gz governance render --target agents-md` reproduces the AGENTS.md content byte-for-byte from the registry. `uv run gz validate --invariant-coherence` exits 0.
5. REQUIREMENT: Round-trip semantic preservation: for each pre-migration H2 section, the canonical claim text (the core load-bearing assertion of that section) appears in at least one registered invariant's `claim` field. Round-trip test enforces this by parsing pre-migration AGENTS.md, extracting canonical claims, and asserting their presence in the registry.
6. REQUIREMENT: `src/gzkit/sync_surfaces.py` AGENTS.md regeneration path now routes through OBPI-02's renderer when `.gzkit/invariants/` contains entries beyond the OBPI-01 seeds. Existing template-based synthesis path remains as fallback only when registry is empty.
7. REQUIREMENT: Operator attests EACH migrated section individually (foundation-kind brief-level Gate 5 stacks; per-section attestation is recorded inline in the MIGRATION-MANIFEST.md with attestor name and date).
8. REQUIREMENT: This OBPI does NOT change the AGENTS.md content semantics — it only changes the authoring layer (canonical YAML invariants → rendered markdown). Any operator-judgment changes to AGENTS.md text belong in a separate ADR amendment (per ADR § Scope boundary, formal constitution-amendment ceremony is `ADR-pool.adr-amendment-tracking`'s scope).

> STOP-on-BLOCKERS: OBPIs 01, 02, 03 must be landed (registry + renderer + drift validator).

## Discovery Checklist

**Parent ADR:**

- [ ] Quote ADR § Decision item #9 (migration) verbatim
- [ ] ADR § Consequences Negative #2 (one-shot risk + mitigation: every migrated invariant requires an assertion-bearing test)
- [ ] ADR § Consequences Negative #10 (reversibility assessment — one-way door justification)

**Governance:**

- [ ] `AGENTS.md` (every H2 section — the migration source-of-truth)
- [ ] `docs/governance/state-doctrine.md` — Layer 1 / 3 distinction this migration enacts
- [ ] `docs/governance/trust-doctrine.md` — T1/T2/T3 invariants that the migrated invariants must satisfy

**Context (exemplars):**

- [ ] `src/gzkit/templates/agents.md` — current template synthesis (will route through renderer post-migration)
- [ ] `src/gzkit/sync_surfaces.py` — current AGENTS.md regeneration path
- [ ] Three seed invariants from OBPI-01 — the schema shape every migrated invariant must satisfy

**Prerequisites:**

- [ ] OBPIs 01/02/03 landed
- [ ] `AGENTS.md` is present and readable
- [ ] Existing test suite in `tests/governance/` is the target dir for new assertion-bearing tests

## Quality Gates

- [ ] Gate 1: Migration paragraph quoted; per-section migration decision recorded in MIGRATION-MANIFEST.md
- [ ] Gate 2: Round-trip semantic-preservation test + per-invariant assertion-bearing tests; RGR followed
- [ ] Code Quality: lint + typecheck
- [ ] Gate 3: Migration manifest published as governance doc; runbook update for "if AGENTS.md needs an edit: go via `.gzkit/invariants/` and re-render"; mkdocs strict
- [ ] Gate 4: `features/constitutional_invariants.feature` includes migration round-trip scenarios tagged `@REQ-0.0.37-09-*`; behave passes
- [ ] Gate 5: Per-section operator attestation in MIGRATION-MANIFEST.md (foundation-kind + universal Gate 5)

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_invariant_coherence -v
uv run mkdocs build --strict
uv run -m behave features/constitutional_invariants.feature --tags=REQ-0.0.37-09

# REQ-04: registry renders AGENTS.md exactly
uv run gz governance render --target agents-md --check && echo "REQ-04 OK"
uv run gz validate --invariant-coherence && echo "REQ-04 OK validator"

# REQ-05: round-trip — every pre-migration H2 has a registered invariant
uv run python -c "
from pathlib import Path
from gzkit.governance.invariants import load_invariants
inv = load_invariants(Path('.'))
# pre-migration AGENTS.md saved as fixture under tests/fixtures/agents_md_pre_migration.md
pre = Path('tests/fixtures/agents_md_pre_migration.md').read_text()
import re
h2s = re.findall(r'^## (.+)$', pre, re.MULTILINE)
claim_texts = ' '.join(i.claim for i in inv.values())
missing = [h for h in h2s if h not in claim_texts]
assert not missing, f'sections not represented in registry: {missing}'
print(f'REQ-05 OK — all {len(h2s)} pre-migration H2 sections represented')
"

# REQ-03: every invariant has an enforcing test
uv run python -c "
import subprocess
from pathlib import Path
from gzkit.governance.invariants import load_invariants
inv = load_invariants(Path('.'))
tests_dir = Path('tests/governance')
for inv_id in inv:
    grep = subprocess.run(['rg', '-q', inv_id, str(tests_dir)], capture_output=True)
    assert grep.returncode == 0, f'no enforcing test references invariant {inv_id}'
print(f'REQ-03 OK — all {len(inv)} invariants have enforcing tests')
"

# Migration manifest exists and is non-trivial
test -f .gzkit/invariants/MIGRATION-MANIFEST.md
wc -l .gzkit/invariants/MIGRATION-MANIFEST.md
```

## Acceptance Criteria

- [ ] REQ-0.0.37-09-01: Every H2 section in pre-migration AGENTS.md is accounted for in `MIGRATION-MANIFEST.md` with action (register|downgrade), target (invariant-id or rule-path), and rationale
- [ ] REQ-0.0.37-09-02: After migration, `gz governance render --target agents-md --check` exits 0 (rendered registry output byte-equals committed AGENTS.md)
- [ ] REQ-0.0.37-09-03: After migration, `gz validate --invariant-coherence` exits 0
- [ ] REQ-0.0.37-09-04: Round-trip — for each pre-migration H2 section, the section's canonical claim text appears in at least one registered invariant's `claim` field (test asserts against `tests/fixtures/agents_md_pre_migration.md` snapshot)
- [ ] REQ-0.0.37-09-05: Every registered invariant has at least one assertion-bearing test in `tests/governance/` whose test body references the invariant id (anti-theater-of-structure mitigation per ADR § Consequences Negative #2)
- [ ] REQ-0.0.37-09-06: `src/gzkit/sync_surfaces.py` routes AGENTS.md regeneration through OBPI-02's renderer when `.gzkit/invariants/` contains entries beyond OBPI-01 seeds
- [ ] REQ-0.0.37-09-07: Operator attestation per migrated section recorded in `MIGRATION-MANIFEST.md` with name + date

## Completion Checklist

- [ ] All gates satisfied
- [ ] `gz brief reconcile OBPI-0.0.37-09-agents-md-migration` reports zero drift
- [ ] Per-section attestation table in MIGRATION-MANIFEST.md is complete

## Evidence

```text
# Per-gate outputs
```

### Value Narrative

<!-- Before: AGENTS.md was Layer-1 prose canon — every claim only as trustworthy as the prose it was encoded in. After: AGENTS.md is a derived view rendered from schema-validated, ledger-witnessed YAML invariants; hand-edits fail-close in CI. -->

### Key Proof

<!-- `gz governance render --target agents-md --check` exit 0 + `gz validate --invariant-coherence` exit 0 + MIGRATION-MANIFEST.md with attestor-signed table -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #495, GHI #485

## Human Attestation

- Attestor: `<name>` per-section in MIGRATION-MANIFEST.md
- Attestation: substantive text per section grounded in semantic-preservation diff
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
