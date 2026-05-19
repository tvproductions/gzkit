---
id: OBPI-0.0.37-10-doctrine-refresh
parent: ADR-0.0.37-constitutional-invariant-composition
item: 10
lane: Lite
status: Draft
---

# OBPI-0.0.37-10-doctrine-refresh: Doctrine Refresh

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #10 — "OBPI-0.0.37-10 — Doctrine refresh (update ADR-0.0.18 kind-axis distinction; re-route pool stubs `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation`; update contributing docs)"

**Status:** Draft

## Objective

Refresh the doctrinal surfaces that previously assumed AGENTS.md was the structural-witness anchor: amend ADR-0.0.18 to distinguish "structural-witness foundation" from "prose-asserted claim"; add re-routing notes to the two pool stubs naming CIC-1/CIC-2 as their prerequisite foundation; update contributing docs to direct future foundation-ADR authors at the invariant registry before authoring.

## Lane

**Lite** — Documentation/process changes only. No CLI verb, no schema, no runtime contract surface changes. Per AGENTS.md Gate Covenant: "Documentation/process/template-only changes stay Lite unless they change one of those external surfaces." (Lane corrected under GHI #495; previous Heavy assignment in the scaffolded brief was templated boilerplate.)

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md` (modify — append kind-axis amendment with explicit "structural-witness vs prose-assertion" distinction; reference ADR-0.0.37 as the structural anchor)
- `docs/design/adr/pool/ADR-pool.brief-authoring-evidence-checks*` (modify — add re-routing note naming CIC-2 as prerequisite foundation; clarify the stub becomes a feature-kind defense once CIC-2 lands)
- `docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation*` (modify — add re-routing note naming CIC-2 as prerequisite foundation; same framing as above)
- `docs/governance/contributing.md` OR equivalent contributing/governance doc (modify — add "Before proposing a foundation-kind ADR" section directing authors at `.gzkit/invariants/`)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` (parent reference — read-only)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-10-doctrine-refresh.md` (this brief)

## Denied Paths

- Paths not listed in Allowed Paths
- `AGENTS.md` (OBPI-09 owns the rewrite-through-registry path; this OBPI must not edit AGENTS.md directly — doing so would re-instance the inversion)
- `.gzkit/invariants/*.yaml` (OBPI-01/09 — read-only here)
- Any `src/` file (this OBPI is docs-only)
- Manpages, runbook (those belong to the OBPIs introducing the relevant CLI verbs — OBPI-02/06)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: ADR-0.0.18 receives an amendment block (separate H2 section, dated, referencing ADR-0.0.37 as the structural anchor) that explicitly states the kind-axis carries the structural-witness vs prose-assertion distinction. Foundation kind = invariant intent with structural witness (schema + validator + ledger event); promoted to ADR only when the invariant is registered in `.gzkit/invariants/`. Prose-asserted-only claims do NOT qualify as foundation kind.
2. REQUIREMENT: `ADR-pool.brief-authoring-evidence-checks*` gets a "Re-routing note (post-ADR-0.0.37)" block stating: the pool stub's Alternative-C self-rejection rested on AGENTS.md § operative-claim-4 being a trustworthy invariant; ADR-0.0.37 ships CIC-2 as the actual foundation invariant; this stub becomes a feature-kind defense of CIC-2 (not a foundation candidate) once ADR-0.0.37 is Validated.
3. REQUIREMENT: `ADR-pool.obpi-pipeline-dispatch-attestation*` gets the same shape of re-routing note (CIC-2 prerequisite; promotes to feature-kind once CIC-2 lands).
4. REQUIREMENT: `docs/governance/contributing.md` (or the canonical contributing doc) gets a new section titled "Before proposing a foundation-kind ADR" containing the algorithm: (1) identify the constitutional invariant the proposed ADR registers; (2) if none exists, propose the invariant first (author a `.gzkit/invariants/<slug>.yaml` draft); (3) only then promote to ADR.
5. REQUIREMENT: This OBPI does NOT edit AGENTS.md, does NOT modify any `src/` file, does NOT introduce any CLI verb or manpage.
6. REQUIREMENT: All four edits include cross-references to ADR-0.0.37 by full path so they survive ADR renumbering.

## Discovery Checklist

**Parent ADR:**

- [ ] Quote ADR § Decision item #10 (doctrine refresh) verbatim
- [ ] ADR § Consequences Negative #4 (pool-stub re-routing risk + mitigation: this OBPI documents the dependency)

**Governance:**

- [ ] `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md` — full current text (the amendment target)
- [ ] `docs/design/adr/pool/` — locate the two named pool stubs
- [ ] `docs/governance/` — find the canonical contributing doc (may be `CONTRIBUTING.md`, `governance_runbook.md`, or similar)

**Context:**

- [ ] ADR-pool stub naming convention (`ADR-pool.<slug>` per `.gzkit/rules/governance-core.md`)
- [ ] Examples of past ADR amendments (search for "Amendment" or "Update" H2 sections in foundation ADRs)

**Prerequisites:**

- [ ] ADR-0.0.18 file exists
- [ ] Both named pool stubs exist (`brief-authoring-evidence-checks`, `obpi-pipeline-dispatch-attestation`)
- [ ] Canonical contributing doc identified

## Quality Gates

### Gate 1: ADR

- [ ] Doctrine-refresh paragraph quoted; each of the four edits enumerated with its target file

### Gate 2: Tests

- [ ] No code changes → no unit tests added. Mark Gate 2 satisfied with explicit "no test deliverable — docs-only OBPI; verification is `mkdocs build --strict` + cross-reference resolution checks below"

### Code Quality

- [ ] Lint clean on changed markdown: `uv run gz lint`
- [ ] (No typecheck — no Python changes)

### Gate 3: Docs (Lite — but docs ARE the deliverable)

- [ ] Lane Lite per Gate Covenant, but the Lite-lane docs deliverable here is the work itself; mkdocs build clean: `uv run mkdocs build --strict`

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Operator attestation recorded (universal — applies regardless of lane)

> Note: Lite lane does not fire Gate 4 (BDD). No BDD scenarios for doctrine refresh.

## Verification

```bash
uv run gz lint
uv run mkdocs build --strict

# REQ-01: ADR-0.0.18 amendment references ADR-0.0.37
rg -n "ADR-0\.0\.37|CIC-1|CIC-2" docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ && echo "REQ-01 OK"

# REQ-02/03: pool stubs reference CIC-2
rg -nl "CIC-2" docs/design/adr/pool/ | rg -q "brief-authoring-evidence-checks|obpi-pipeline-dispatch-attestation" && echo "REQ-02/03 OK"

# REQ-04: contributing doc has the new section
rg -n "Before proposing a foundation-kind ADR" docs/governance/ && echo "REQ-04 OK"

# REQ-05: this OBPI did NOT touch AGENTS.md or any src/ file
# Check working-tree status (not post-commit history, which is commit-boundary-dependent)
git status --porcelain | rg -v '^.. docs/' | rg -v '^.. \.gzkit/(ledger|insights)' | grep -q . && echo "WARNING: out-of-scope edits detected" || echo "REQ-05 OK: only docs/ and governance files modified"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-10-01: ADR-0.0.18 contains a dated amendment H2 section that names ADR-0.0.37 as the structural anchor and explicitly distinguishes structural-witness foundation from prose-asserted claims; the amendment text includes the words "structural witness" and a pointer to `.gzkit/invariants/`
- [ ] REQ-0.0.37-10-02: `ADR-pool.brief-authoring-evidence-checks*` contains a "Re-routing note (post-ADR-0.0.37)" block referencing CIC-2 as the prerequisite foundation and reclassifying the stub as feature-kind once CIC-2 lands
- [ ] REQ-0.0.37-10-03: `ADR-pool.obpi-pipeline-dispatch-attestation*` contains the same shape of re-routing note
- [ ] REQ-0.0.37-10-04: The canonical contributing doc contains a "Before proposing a foundation-kind ADR" section with the three-step algorithm (identify invariant; propose invariant first if missing; then promote to ADR)
- [ ] REQ-0.0.37-10-05: No `src/` files modified by this OBPI; AGENTS.md untouched; verified by `git diff --name-only` post-implementation

## Completion Checklist

- [ ] Gate 1 / Gate 2 (test-deferral noted) / Gate 3 / Gate 5 satisfied
- [ ] `gz brief reconcile OBPI-0.0.37-10-doctrine-refresh` reports zero drift
- [ ] Lane assignment is Lite (the brief's frontmatter already corrected under GHI #495)

## Evidence

```text
# Per-gate outputs
```

### Value Narrative

<!-- Before: ADR-0.0.18 kind-axis text allowed prose-asserted "foundation" claims; pool stubs cited AGENTS.md as their anchor; contributing docs did not direct authors at the invariant registry. After: the kind-axis is structurally typed; pool stubs are correctly routed; future foundation ADRs flow through the registry first. -->

### Key Proof

<!-- `rg -n "ADR-0.0.37" docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/` returns the amendment lines. -->

### Implementation Summary

- Files created/modified:
- Tests added: n/a (docs-only)
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #495 — ADR-0.0.37 OBPI briefs in unindividualized scaffold state (this brief authored under that GHI; lane corrected from Heavy → Lite under same GHI)
- GHI #485 — `gz specify` --author root-cause

## Human Attestation

- Attestor: `<name>` (universal Gate 5 per ADR-0.0.36)
- Attestation: substantive text grounded in cross-reference grep output
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
