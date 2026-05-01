# Plan: OBPI-0.26.0-06 Drift Detection (Absorb-by-Reference)

**OBPI:** `OBPI-0.26.0-06-drift-detection`
**Parent ADR:** `ADR-0.26.0-governance-library-module-absorption` (Heavy lane,
`feature` kind)
**Lane:** Heavy
**Plan kind:** Doc-only — Absorb-by-reference (no `src/` or `tests/` edits)
**Author date:** 2026-05-01

---

## Context

### Brief

`docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md`
asks: evaluate `../airlineops/src/opsdev/lib/drift_detection.py` (384 lines) and
decide **Absorb** (opsdev is better) or **Exclude** (domain-specific). The brief
explicitly forbids a `Confirm` path because it asserts gzkit has no equivalent
module.

### What the brief asserts vs what is observable

The brief asserts "gzkit equivalent: None." That assertion is stale.

`src/gzkit/temporal_drift.py` (348 lines) exists and its module docstring
explicitly states:

> Lineage: adapted from `opsdev.lib.drift_detection` in airlineops, with
> gzkit-specific changes documented in
> `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-26-drift-detection-pattern.md`.

The same opsdev source module — `lib/drift_detection.py`, 384 lines — was
already evaluated under **OBPI-0.25.0-26-drift-detection-pattern**, which
landed `status: attested_completed` on **2026-04-09** with the gzkit module
adapted into `src/gzkit/temporal_drift.py`.

### Duplicate-OBPI signal

This is the **third** instance of the duplicate-OBPI defect already tracked
under **GHI #376** (open):

| OBPI | Parent ADR | Source | Decision | Status |
|------|------------|--------|----------|--------|
| OBPI-0.25.0-20-adr-governance-pattern | ADR-0.25.0 | `lib/adr_governance.py` | Confirm | attested 2026-04-11 |
| OBPI-0.26.0-04-adr-governance | ADR-0.26.0 | (same source) | Confirm-by-reference | attested |
| OBPI-0.25.0-29-ledger-schema-pattern | ADR-0.25.0 | `lib/ledger_schema.py` | Exclude | attested 2026-04-13 |
| OBPI-0.26.0-05-ledger-schema | ADR-0.26.0 | (same source) | Exclude-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-26-drift-detection-pattern | ADR-0.25.0 | `lib/drift_detection.py` | Absorb | attested 2026-04-09 |
| **OBPI-0.26.0-06-drift-detection** | **ADR-0.26.0** | **(same source)** | **Absorb-by-reference** (this brief) | **in-flight** |

Same root cause as the GHI #376 canonical: ADR-0.26.0 authoring did not check
whether ADR-0.25.0's absorption sweep had already covered each module in scope.

### Sibling pattern (OBPI-0.26.0-05)

`OBPI-0.26.0-05-ledger-schema` (attested 2026-05-01) established the
**reference-by-precedent** pattern for this class of duplicate. That brief
landed `decision: Exclude` by reference to OBPI-0.25.0-29, with a six-point
rationale, refreshed line anchors, and a section tracking the duplicate-OBPI
signal under GHI #376. This plan mirrors that structure with `Absorb` instead
of `Exclude`.

### Anti-pattern guard

The OBPI-05 brief's NON-GOALS section names the explicit anti-pattern this
plan must avoid:

> Re-running the comparison work already attested under OBPI-0.25.0-29-...
> on identical source material — divergent rationale on identical material
> is itself a doctrine-drift signal.

The same applies here. Re-deriving a comparison rationale from scratch on
`lib/drift_detection.py` when OBPI-0.25.0-26 already authored it (and the
gzkit absorption already shipped) would be the doctrine drift the OBPI-05
NON-GOAL prohibits.

---

## Files

**Edited (this OBPI):**

- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md`
  — frontmatter (`decision: Absorb`, `status` transitions through ceremony),
  body (Comparison, Decision, Implementation Summary, Key Proof, Closing
  Argument sections per the OBPI-05 template).

**Read-only (reference):**

- `src/gzkit/temporal_drift.py` (348 lines) — gzkit equivalent already
  shipped under OBPI-0.25.0-26.
- `../airlineops/src/opsdev/lib/drift_detection.py` (384 lines) — opsdev
  source under review.
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-26-drift-detection-pattern.md`
  — canonical precedent.
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md`
  — sibling brief establishing the reference-by-precedent pattern.

**Out of scope (not touched):**

- `src/gzkit/` — Absorb-by-reference; the absorption already shipped under
  OBPI-0.25.0-26. No new module additions.
- `tests/` — same; no new test files. Existing
  `tests/test_temporal_drift.py` (or equivalent) covers the absorbed surface.
- `pyproject.toml`, lockfiles, CI files.
- `../airlineops/` (per brief — opsdev is upstream-only).
- Any path outside the brief's Allowed Paths.

---

## Steps

1. **Discovery checklist (bind-once cache).**
   - [ ] Read parent ADR `ADR-0.26.0-governance-library-module-absorption.md`
     to re-confirm subtraction-test framing and Cross-Reference Matrix row 6.
   - [ ] Read brief frontmatter and body to identify scaffold-drift the
     OBPI-05 ceremony corrected (ALL-CAPS headings → title case, missing
     `Lane`, `Denied Paths`, `Discovery Checklist` sections).
   - [ ] Read OBPI-0.25.0-26-drift-detection-pattern brief in full to extract
     the comparison rationale that will be cited verbatim by reference.
   - [ ] Read OBPI-0.26.0-05-ledger-schema brief to mirror its structural
     pattern (frontmatter `decision:` field, Comparison/Decision sections,
     Implementation Summary template, Key Proof template, Closing Argument).
   - [ ] Read GHI #376 body to confirm the duplicate-OBPI tracking contract.

2. **Verify gzkit absorption is current.**
   - [ ] Re-read `src/gzkit/temporal_drift.py` end-to-end (348 lines).
   - [ ] Confirm the module's public surface matches opsdev's (`DriftStatus`,
     `DriftResult`, `ObpiDriftResult`, `classify_drift`, `detect_drift`,
     `detect_obpi_drift`).
   - [ ] Note any documented gzkit-specific deltas (HEAD cache via
     `git_cmd`, ledger-driven anchor extraction instead of per-ADR
     `validation_receipt` reads, SHA-7 normalization).
   - [ ] Confirm `tests/` contains coverage for the absorbed surface.

3. **Brief scaffold drift correction (in flight, mirroring OBPI-05).**
   - [ ] Rename ALL-CAPS section headings to title case where the brief
     authored them as ALL CAPS (`OBJECTIVE` → `Objective`, etc.). Match
     `src/gzkit/schemas/obpi.json` required-headers contract.
   - [ ] Add missing structural sections if the brief lacks them: `Lane`,
     `Denied Paths`, `Discovery Checklist`. Use OBPI-05 wording as the
     template.
   - [ ] Run `uv run gz obpi validate --authored
     docs/.../OBPI-0.26.0-06-drift-detection.md` and address any reported
     header drift before proceeding.

4. **Author the comparison body (by reference, refreshed anchors).**
   - [ ] Add a `## Comparison` section with the per-dimension table from
     OBPI-0.25.0-26, refreshed to current line anchors in
     `src/gzkit/temporal_drift.py` and the unchanged opsdev source.
   - [ ] Note any capability deltas since 2026-04-09 in inline annotations
     (gzkit module size grew/shrank by N lines; public surface stable).
   - [ ] Add a `### Source-material observation` subsection mirroring OBPI-05
     where the parent-ADR-authored Source Material header asserts "gzkit
     equivalent: None" but the actual surface is `temporal_drift.py` (348 L)
     plus its tests. Body-level observation; do not amend the parent-ADR
     header.

5. **Author the decision section.**
   - [ ] Set frontmatter `decision: Absorb`.
   - [ ] Add a `## Decision` section: "**Absorb** (by reference to
     OBPI-0.25.0-26-drift-detection-pattern, attested 2026-04-09)."
   - [ ] Author a six-point rationale mirroring the OBPI-05 structure,
     anchored on:
     1. Canonical precedent (OBPI-0.25.0-26 attested 2026-04-09 on identical
        source artifact).
     2. Module already shipped: `src/gzkit/temporal_drift.py` exists with
        full public surface and lineage docstring.
     3. Subtraction test passed: drift detection is governance-integrity,
        not airline-specific; opsdev's storage-layout assumptions
        (per-ADR `validation_receipt.py` reads) were re-architected against
        gzkit's central `.gzkit/ledger.jsonl` during the OBPI-25.0-26
        absorption.
     4. Pure-classifier-plus-orchestrator architecture preserved (`classify_drift`
        is testable without mocks; orchestrators isolate I/O).
     5. No-narrow-idiom standalone absorption needed beyond what shipped.
     6. Duplicate-OBPI surface tracked under GHI #376 (third instance).
   - [ ] Add `### Tracking the duplicate-evaluation signal` subsection
     mirroring OBPI-05: extend GHI #376 via `gh issue comment` rather than
     file a parallel GHI; root cause and mitigation are identical.
   - [ ] Add `### Gate 4 (BDD): N/A` subsection: no operator-visible
     behavior change introduced by this brief — the absorption already
     shipped under OBPI-0.25.0-26 and its operator-visible Gate 4 evidence
     was attested then.

6. **Mark Acceptance Criteria.**
   - [ ] REQ-0.26.0-06-01: brief records `Absorb` decision (frontmatter +
     body). Tag `[doc]` per OBPI-05 convention.
   - [ ] REQ-0.26.0-06-02: rationale cites concrete capability and
     architectural differences; references OBPI-0.25.0-26 precedent.
     Tag `[doc]`.
   - [ ] REQ-0.26.0-06-03: Absorb outcome — gzkit contains the adapted
     module. **Already-shipped** under OBPI-0.25.0-26 at
     `src/gzkit/temporal_drift.py`. Tag `[doc]`.
   - [ ] REQ-0.26.0-06-04: Exclude path — N/A (Absorb outcome).
   - [ ] REQ-0.26.0-06-05: Gate 4 — `N/A` with rationale (no
     operator-visible behavior change introduced by this brief).
     Tag `[doc]`.

7. **Author Implementation Summary, Key Proof, Closing Argument.**
   - [ ] Implementation Summary: bullet-form `- Key: value` shape that
     `_has_substantive_implementation_summary` accepts (per
     `.claude/rules/brief-heading-conventions.md` — H3 not H2).
   - [ ] Key Proof: at least one concrete command + observed output. Cite
     ARB receipt IDs from Stage 3 inline.
   - [ ] Closing Argument: full prose paragraph mirroring OBPI-05's
     "**Absorb-by-reference**" framing, naming the canonical precedent,
     the gzkit module location, and the duplicate-OBPI surface.

8. **Stage 3 verification (canonical ARB-wrapped).**
   - [ ] `uv run gz arb ruff` (clean, receipt cited)
   - [ ] `uv run gz arb typecheck` (clean, receipt cited)
   - [ ] `uv run gz arb step --name unittest -- uv run -m unittest -q`
     (passing, receipt cited)
   - [ ] `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
     (Heavy lane — passing, receipt cited)
   - [ ] `uv run gz covers OBPI-0.26.0-06-drift-detection --json` →
     `uncovered_reqs: 0` (vacuous parity-gate pass for `[doc]` REQs via
     `_synthesize_doc_proof_linkage`).

9. **Stage 5 ceremony.**
   - [ ] Pre-flight: `uv run gz obpi precomplete OBPI-0.26.0-06-drift-detection`
     — fix every reported precondition before invoking complete.
   - [ ] Closure-narrative gate: present resolved Implementation Summary +
     Key Proof inline before invoking `gz obpi complete`.
   - [ ] `uv run gz obpi complete OBPI-0.26.0-06-drift-detection
     --attestor 'g0' --attestation-text "..." --attestor-present`
     (primary path; PTY fallback only if `--attestor-present` is refused).
   - [ ] `uv run gz obpi lock release OBPI-0.26.0-06-drift-detection`
   - [ ] Remove pipeline markers
     (`.claude/plans/.pipeline-active-OBPI-0.26.0-06-drift-detection.json`).
   - [ ] `uv run gz git-sync --apply` (sync #1: governance edits).
   - [ ] `uv run gz obpi reconcile OBPI-0.26.0-06-drift-detection`
   - [ ] `uv run gz adr status ADR-0.26.0 --json`
   - [ ] `uv run gz git-sync --apply` (sync #2: reconcile + ADR status).

10. **GHI #376 extension.**
    - [ ] `gh issue comment 376 --body "..."` adding this brief as the
      third instance of the duplicate-OBPI defect, with same root cause
      (ADR-0.26.0 authoring did not check ADR-0.25.0 prior absorptions)
      and same mitigation (proposed `gz validate --absorption-duplicates`).

---

## Verification (per brief)

```bash
# Brief's verification commands (repeated here for the plan-audit receipt):

test -f ../airlineops/src/opsdev/lib/drift_detection.py
# Expected: opsdev source under review exists.

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Expected: completed brief records the Absorb decision.

rg -n 'src/gzkit/|tests/|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Expected: Absorb path names concrete target paths
# (`src/gzkit/temporal_drift.py` cited as the already-shipped target).

uv run gz test --obpi OBPI-0.26.0-06-drift-detection
# Expected: OBPI-scoped tests green (vacuous pass on [doc] REQ pattern via
# _synthesize_doc_proof_linkage; covered by gz covers parity gate).

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes; Absorb-by-
# reference introduces none, so brief records `N/A` rationale.

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Expected: completed brief captures Gate 4 N/A rationale.

# Plan-specific addition:
rg -n 'OBPI-0.25.0-26' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-06-drift-detection.md
# Expected: brief cites the canonical precedent in body and Closing Argument.
```

---

## Notes — Plan-Before-Exploration Disclosure (Step 6a)

### Destination-in-mind

Before writing this plan, after reading the brief, the parent ADR row,
the opsdev source, and discovering `src/gzkit/temporal_drift.py` with its
explicit OBPI-0.25.0-26 lineage docstring, the conclusion I had already
formed was: **this is a duplicate-OBPI of OBPI-0.25.0-26 and the structurally
correct landing is Absorb-by-reference**, mirroring the doc-only ceremony
the OBPI-0.26.0-05 sibling executed for `lib/ledger_schema.py` (with
`Absorb` instead of `Exclude` because the gzkit module already exists).

The plan reconstructs that destination. The discovery is empirical (a
single `find` + `grep` confirmed `temporal_drift.py` exists with explicit
OBPI-0.25.0-26 lineage), so the destination is grounded in observable
evidence rather than pattern-matching.

### Rejected alternatives

1. **Re-run the comparison from scratch.** Rejected: the OBPI-0.26.0-05
   NON-GOAL section explicitly names this as doctrine drift —
   "divergent rationale on identical material is itself a doctrine-drift
   signal." OBPI-0.25.0-26 already authored the dimension comparison;
   re-deriving it would either reproduce it (waste) or diverge from it
   (drift).

2. **Decide Exclude.** Rejected: the gzkit module exists. `temporal_drift.py`
   is the absorbed implementation. Naming the outcome "Exclude" while the
   absorbed module ships in `src/gzkit/` is internally inconsistent.

3. **Decide Confirm.** Rejected: the brief explicitly forbids the Confirm
   path ("No existing gzkit equivalent means either Absorb or Exclude —
   there is no Confirm path"). The brief is wrong about "no equivalent" —
   `temporal_drift.py` exists — but the brief's allowed-decision set is
   the contract; expanding it would be scope creep into ADR-0.26.0
   authoring rather than this OBPI's evaluation.

4. **Treat the duplicate-OBPI signal as out-of-scope.** Rejected: GHI #376
   is the canonical tracking surface and OBPI-0.26.0-05 set the precedent
   that each new instance extends GHI #376 via `gh issue comment`. Not
   recording this third instance would let the duplicate-OBPI defect
   silently grow.

5. **Touch `src/gzkit/temporal_drift.py` to "refresh" the absorbed module
   under this brief's name.** Rejected: the absorbed module is already
   attested (OBPI-0.25.0-26, 2026-04-09); modifying it under a doc-only
   brief is scope creep and would invalidate that prior attestation. If
   `temporal_drift.py` needs maintenance, that's a separate fix routed
   per AGENTS.md § Defect-fix routing.

6. **File a new GHI for this third duplicate.** Rejected: GHI #376
   already names the same root cause and mitigation. A parallel GHI
   would fragment the tracking surface; OBPI-0.26.0-05 set the
   "extend via comment" precedent.

### Plan-before-exploration honesty

Reading order before writing this plan:

1. `gz adr status ADR-0.26.0` (operator-visible status — established the
   12-OBPI surface).
2. `gz plan audit OBPI-0.26.0-06-drift-detection` (CLI structural check —
   confirmed no plan exists; surfaced 327 advisory scope-collision
   notices).
3. OBPI-0.26.0-06 brief (the contract).
4. ADR-0.26.0 (parent).
5. OBPI-0.26.0-05 brief (sibling pattern).
6. opsdev `lib/drift_detection.py` (subject).
7. **Discovered** `src/gzkit/temporal_drift.py` and its OBPI-0.25.0-26
   lineage docstring via `find ... | xargs grep -l "drift|anchor.*commit"`.
8. OBPI-0.25.0-26 brief (canonical precedent).
9. GHI #376 (tracking surface).

The destination crystallized at step 7 (lineage discovery) and was
confirmed at step 8 (precedent). Steps 1-6 were brief reads, not plan
authorship; step 9 confirmed the tracking surface. Plan written after
that.

---

## Acceptance

Plan is ready when:

- [x] All Step 1 discovery items have a citable file location.
- [x] All Step 5 rationale points name the OBPI-0.25.0-26 precedent
  explicitly.
- [x] The destination-in-mind disclosure names the conclusion that was
  already formed before plan authoring.
- [x] Rejected alternatives section names ≥4 alternatives with concrete
  reasons.
- [x] Verification block reproduces every brief-required command.
- [x] No `src/` or `tests/` paths appear in the Files-Edited list (this is
  doc-only; the absorption already shipped).
