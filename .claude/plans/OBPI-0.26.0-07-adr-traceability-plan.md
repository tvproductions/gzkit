# Plan: OBPI-0.26.0-07 ADR Traceability (Confirm-by-Reference)

**OBPI:** `OBPI-0.26.0-07-adr-traceability`
**Parent ADR:** `ADR-0.26.0-governance-library-module-absorption` (Heavy lane,
`feature` kind)
**Lane:** Heavy
**Plan kind:** Doc-only — Confirm-by-reference (no `src/` or `tests/` edits)
**Author date:** 2026-05-01

---

## Context

### Brief

`docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md`
asks: evaluate `../airlineops/src/opsdev/lib/adr_traceability.py` (277 lines)
and decide **Absorb** or **Exclude**. The brief Assumptions forbid the Confirm
path ("No existing gzkit equivalent means either Absorb or Exclude — there is
no Confirm path"). That assumption is stale.

### What the brief asserts vs what is observable

The brief asserts "gzkit equivalent: None." That assertion is stale.

`src/gzkit/traceability.py` (22,256 bytes — substantial governance module)
ships with the `@covers` decorator, the AST-based linkage scanner, and the
coverage-report computation. `tests/test_traceability.py` covers it. The
module is consumed by `gz drift`, `gz covers`, and `gz adr audit-check`.

The same opsdev source module — `lib/adr_traceability.py`, 277 lines — was
already evaluated under **OBPI-0.25.0-22-adr-traceability-pattern**, which
landed `status: attested_completed` on **2026-04-09** with **Decision:
Confirm**. The six-point rationale established gzkit's superiority on six
dimensions (declarative `@covers` vs heuristic `infer()`; structured
`CoverageReport` vs heuristic sums; native `detect_drift` vs no equivalent;
domain-bonus terms in opsdev fail subtraction test; AST precision vs
text-line scanning; Pydantic vs stdlib dataclass).

### Duplicate-OBPI signal — fourth instance

This is the **fourth** instance of the duplicate-OBPI defect tracked under
**GHI #376** (open):

| OBPI (ADR-0.25.0) | Decision | OBPI (ADR-0.26.0) | This-pipeline framing |
|-------------------|----------|-------------------|------------------------|
| OBPI-0.25.0-20 (`adr_governance.py`) | Confirm 2026-04-11 | OBPI-0.26.0-04 | Confirm-by-reference |
| OBPI-0.25.0-29 (`ledger_schema.py`) | Exclude 2026-04-13 | OBPI-0.26.0-05 | Exclude-by-reference |
| OBPI-0.25.0-26 (`drift_detection.py`) | Absorb 2026-04-09 | OBPI-0.26.0-06 | Absorb-by-reference |
| **OBPI-0.25.0-22 (`adr_traceability.py`)** | **Confirm 2026-04-09** | **OBPI-0.26.0-07 (this brief)** | **Confirm-by-reference** |

Same root cause as the GHI #376 canonical: ADR-0.26.0 authoring did not check
whether ADR-0.25.0's absorption sweep had already covered each module in
scope.

### Sibling pattern — Confirm-by-reference precedent

`OBPI-0.26.0-04-adr-governance` (attested) recorded `decision: Confirm` and
landed Confirm-by-reference framing despite the same brief-scaffold
"no Confirm path" assumption. The brief's Assumptions section mis-stated the
allowed-decisions set; OBPI-0.26.0-04 surfaced the brief defect, set
`decision: Confirm`, and the validator accepted it. This brief follows that
exact precedent.

### Anti-pattern guard

Per OBPI-0.26.0-05's NON-GOAL: "Re-running the comparison work already
attested... on identical source material — divergent rationale on identical
material is itself a doctrine-drift signal." The same applies here.

---

## Files

**Edited (this OBPI):**

- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md`
  — frontmatter (`decision: Confirm`, `status` transitions through ceremony),
  body (Comparison + Decision + Tracking + Gate 4 N/A + Implementation
  Summary + Key Proof + Human Attestation placeholder + Closing Argument).

**Read-only (reference):**

- `src/gzkit/traceability.py` (22 KB) — gzkit's existing superior surface
- `tests/test_traceability.py` — test coverage
- `../airlineops/src/opsdev/lib/adr_traceability.py` (277 lines) — opsdev source
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-22-adr-traceability-pattern.md`
  — canonical precedent (Confirm)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-04-adr-governance.md`
  — sibling Confirm-by-reference precedent

**Out of scope (not touched):**

- `src/gzkit/traceability.py` — Confirm; no modification needed
- `tests/test_traceability.py` — same
- `../airlineops/` (per brief — opsdev is upstream-only)
- `pyproject.toml`, lockfiles, CI files

---

## Steps

1. **Discovery checklist (bind-once cache).**
   - Read parent ADR `ADR-0.26.0-...md` to re-confirm the subtraction-test
     framing and Cross-Reference Matrix row 7.
   - Read brief frontmatter and body to identify scaffold-drift to correct
     (ALL-CAPS headings → title case, missing `Lane`/`Denied Paths`/`Discovery
     Checklist` sections, brief assumption "no Confirm path" — flag as defect
     in the body but proceed under OBPI-0.26.0-04's precedent).
   - Read OBPI-0.25.0-22-adr-traceability-pattern in full to extract the
     six-point Confirm rationale that will be cited verbatim by reference.
   - Read OBPI-0.26.0-04 to mirror its Confirm-by-reference structural pattern.
   - Read GHI #376 to confirm the duplicate-OBPI tracking contract.

2. **Verify gzkit traceability surface state.**
   - Re-read `src/gzkit/traceability.py` end-to-end (22 KB, ~600 lines).
   - Confirm public surface: `@covers` decorator, `LinkageRecord`, scanner
     functions, coverage computation.
   - Note any documented integration with `gz drift`, `gz covers`,
     `gz adr audit-check` consumers.
   - Confirm `tests/test_traceability.py` exists and exercises the surface.

3. **Brief scaffold drift correction (in flight, mirroring OBPI-05/06).**
   - Rename ALL-CAPS section headings to title case (`OBJECTIVE` →
     `Objective`, etc.). Match `src/gzkit/schemas/obpi.json` required-headers
     contract.
   - Add missing structural sections: `Lane`, `Denied Paths`,
     `Discovery Checklist`. Use OBPI-06 wording as the template.
   - Run `uv run gz obpi validate --authored ...` and address any reported
     drift before proceeding.

4. **Author comparison body (by reference).**
   - Add `## Comparison` section with the per-dimension table from
     OBPI-0.25.0-22, refreshed to current line anchors in
     `src/gzkit/traceability.py` and the unchanged opsdev source.
   - Add `### Source-material observation` subsection mirroring OBPI-06:
     Source Material header asserts "gzkit equivalent: None"; actual surface
     is `traceability.py` + `triangle.py` + `tests/test_traceability.py`.
     Body-level observation; do not amend the parent-ADR header.

5. **Author the decision section.**
   - Set frontmatter `decision: Confirm` (mirroring OBPI-04's precedent that
     this is permitted despite the brief's stale assumption).
   - Add `## Decision` section: "**Confirm** (by reference to
     OBPI-0.25.0-22-adr-traceability-pattern, attested 2026-04-09)."
   - Author a six-point rationale citing the OBPI-0.25.0-22 precedent's
     six dimensions verbatim (with refreshed line anchors), plus a seventh
     point on the duplicate-OBPI surface tracked under GHI #376.
   - **Surface the brief-scaffold defect explicitly** in a sub-paragraph:
     the brief Assumptions forbid Confirm but gzkit's existing module
     IS superior; the assumption is itself a scaffold defect (third instance
     of the same defect class — also present in OBPI-04 and OBPI-06 briefs).
     OBPI-0.26.0-04 already established that `decision: Confirm` is
     accepted by the validator despite the assumption; this brief follows
     that precedent.
   - Add `### Tracking the duplicate-evaluation signal` subsection
     mirroring OBPI-04/05/06: extend GHI #376 via `gh issue comment` rather
     than file parallel GHI; this is the fourth structural instance.
   - Add `### Gate 4 (BDD): N/A` subsection: no operator-visible behavior
     change; existing traceability surface continues to function identically.

6. **Mark Acceptance Criteria.**
   - REQ-0.26.0-07-01: brief records `Confirm` decision (frontmatter + body).
     Tag `[doc]`. Note the brief's "Absorb / Exclude" wording — Confirm is
     the structurally correct verdict per precedent; the brief constraint
     is the defect.
   - REQ-0.26.0-07-02: rationale cites concrete capability differences;
     references OBPI-0.25.0-22 precedent's six dimensions. Tag `[doc]`.
   - REQ-0.26.0-07-03: Absorb path — N/A (Confirm outcome).
   - REQ-0.26.0-07-04: Confirm/Exclude path — gzkit's existing module is
     superior on six named dimensions; opsdev's heuristic approach has
     domain-specific bonus terms that fail the subtraction test. Tag `[doc]`.
   - REQ-0.26.0-07-05: Gate 4 — `N/A` rationale (no operator-visible change).
     Tag `[doc]`.

7. **Author Implementation Summary, Key Proof, Human Attestation,
   Closing Argument.**
   - Implementation Summary: bullet `- Key: value` form per
     `_has_substantive_implementation_summary`.
   - Key Proof: at least one concrete command + observed output; cite ARB
     receipt IDs from Stage 3 inline.
   - Human Attestation: H2 placeholder section per OBPI-05/06 pattern (CLI
     fills it from `--attestation-text` at completion time).
   - Closing Argument: full prose paragraph mirroring OBPI-04's
     "**Confirm-by-reference**" framing.

8. **Stage 3 verification (canonical ARB-wrapped, OBPI-scoped).**
   - `uv run gz arb ruff` (clean)
   - `uv run gz arb typecheck` (clean)
   - `uv run gz arb step --name unittest -- uv run gz test --obpi
     OBPI-0.26.0-07-adr-traceability` (canonical OBPI-scoped per OBPI-05/06
     precedent — vacuous green for `[doc]` REQs)
   - `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
     (Heavy lane)
   - `uv run gz covers OBPI-0.26.0-07-adr-traceability --json` →
     `uncovered_reqs: 0`

9. **Stage 5 ceremony.**
   - Pre-flight: `uv run gz obpi precomplete OBPI-0.26.0-07-adr-traceability`
   - `uv run gz obpi complete ... --attestor 'g0'
     --attestation-text "..." --attestor-present`
   - `uv run gz obpi lock release ...` (use `--force` if shell-session ID
     differs from claim session, per OBPI-06 observation)
   - Remove pipeline markers
   - Git-sync #1, reconcile, ADR status, git-sync #2

10. **GHI #376 extension (fourth instance comment).**
    - `gh issue comment 376 --body "..."` adding this brief as the fourth
      structural instance, with same root cause and same mitigation.

---

## Verification (per brief)

```bash
test -f ../airlineops/src/opsdev/lib/adr_traceability.py
# Expected: opsdev source under review exists

test -f src/gzkit/traceability.py
# Expected: gzkit existing module exists (Confirm precedent under OBPI-0.25.0-22)

rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Expected: brief frontmatter and Decision body record the Confirm verdict
# (OBPI-0.26.0-07-specific verification command)

rg -n 'OBPI-0.25.0-22' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Expected: brief cites the canonical precedent in body and Closing Argument

rg -n 'Absorb|Exclude|Confirm' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-07-adr-traceability
# Expected: vacuous parity-gate pass on [doc] REQ pattern

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes (Confirm: not required)

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md
# Expected: brief captures Gate 4 N/A rationale
```

---

## Notes — Plan-Before-Exploration Disclosure (Step 6a)

### Destination-in-mind

After reading the brief, parent ADR row, and discovering OBPI-0.25.0-22's
Decision: Confirm with the six-point rationale showing gzkit's existing
`@covers`+AST architecture is **architecturally superior** to opsdev's
heuristic `infer()` approach, the conclusion I had already formed before
plan authoring was: **Confirm-by-reference to OBPI-0.25.0-22**, mirroring
OBPI-0.26.0-04's pattern (which also landed `decision: Confirm` despite the
brief's "no Confirm path" assumption — the assumption is itself a brief
scaffold defect, not a binding constraint).

### Rejected alternatives

1. **Decide Absorb.** Rejected: would require copying opsdev's heuristic
   `infer()` into gzkit; OBPI-0.25.0-22's precedent established that
   approach is materially inferior to gzkit's declarative `@covers`+AST
   surface, and absorbing it would degrade governance compliance (heuristic
   keyword-matching introduces false positives unsuitable for audit). Also
   would invalidate the OBPI-0.25.0-22 attestation.

2. **Decide Exclude.** Rejected: gzkit's surface IS the answer to ADR-0.26.0
   item 7's question (does gzkit have ADR-to-artifact traceability?). Naming
   the outcome "Exclude" while gzkit's superior surface ships is a
   semantic miscoding of the precedent.

3. **Honor the brief's "no Confirm path" assumption literally.** Rejected:
   OBPI-0.26.0-04 already established the precedent that the brief's
   stale assumption is a scaffold defect, not a binding constraint, and
   that `decision: Confirm` is accepted by the validator. Honoring an
   incorrect brief assumption over a known-correct decision would be
   doctrine drift.

4. **Re-run the comparison from scratch.** Rejected: OBPI-05's NON-GOAL
   names this as doctrine drift on identical source material.

5. **Decide Confirm but suppress the brief-scaffold-defect surfacing.**
   Rejected: the assumption is itself a structural defect that crosses
   multiple ADR-0.26.0 briefs (06 and 07 share it; 05 does not). Surfacing
   it explicitly serves the broader doctrine — operators need to see the
   pattern.

6. **File a new GHI for the fourth duplicate.** Rejected: GHI #376
   already names the same root cause. A parallel GHI fragments tracking.

### Plan-before-exploration honesty

Reading order before writing this plan:

1. `gz adr status ADR-0.26.0` (operator-visible status — saw 6/12 done after OBPI-06 closed).
2. OBPI-0.26.0-07 brief (the contract).
3. opsdev `lib/adr_traceability.py` (size verified at 277 lines).
4. **Found** `src/gzkit/traceability.py` via `find ... | xargs grep -l "trace|traceability"`.
5. **Found** `OBPI-0.25.0-22-adr-traceability-pattern.md` via directory listing of ADR-0.25.0/obpis.
6. OBPI-0.25.0-22 Decision: Confirm with six-point rationale (the precedent).
7. Confirmed OBPI-0.26.0-04 used `decision: Confirm` despite same "no Confirm path" assumption (precedent for surfacing the scaffold defect).

The destination crystallized at step 6 (precedent decision). Steps 1-5 were
read-only orientation; step 7 confirmed the framing precedent. Plan written
after that.

---

## Acceptance

Plan is ready when:

- [x] All Step 1 discovery items have a citable file location.
- [x] All Step 5 rationale points name OBPI-0.25.0-22's six-point rationale.
- [x] The destination-in-mind disclosure names the conclusion already formed.
- [x] Rejected alternatives section names ≥4 alternatives with concrete reasons.
- [x] Verification block reproduces every brief-required command.
- [x] No `src/` or `tests/` paths in Files-Edited list (Confirm is doc-only).
