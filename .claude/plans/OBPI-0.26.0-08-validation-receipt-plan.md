# Plan: OBPI-0.26.0-08 Validation Receipt (Confirm-by-Reference)

**OBPI:** `OBPI-0.26.0-08-validation-receipt`
**Parent ADR:** `ADR-0.26.0-governance-library-module-absorption` (Heavy lane,
`feature` kind)
**Lane:** Heavy
**Plan kind:** Doc-only — Confirm-by-reference (no `src/` or `tests/` edits)
**Author date:** 2026-05-01

---

## Context

### Brief

`docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md`
asks: evaluate `../airlineops/src/opsdev/lib/validation_receipt.py` (274 lines)
and decide **Absorb**, **Confirm**, or **Exclude**. Brief Source Material
asserts gzkit equivalent is "Partial in `src/gzkit/validate.py`."

### What the brief asserts vs what is observable

`src/gzkit/validate.py` is a 121-line re-export shim that delegates to the
`validate_pkg/` submodules. The actual gzkit receipt-validation surface is
distributed across:

- `src/gzkit/events.py` (556 L, including the typed `EventAnchor` model at line 355)
- `src/gzkit/ledger_semantics.py` (547 L)
- `src/gzkit/validate_pkg/ledger_check.py` (379 L)
- `src/gzkit/temporal_drift.py` (348 L; absorbed via OBPI-0.25.0-26)
- `src/gzkit/utils.py` `capture_validation_anchor_with_warnings` (lines 64-105)
- `src/gzkit/commands/obpi_complete.py` atomic transaction (`_execute_transaction`)

That is **~1830 lines** across the surface — versus airlineops's 274-line
single module. The brief's "Partial in `src/gzkit/validate.py`" wording is
stale brief-scaffold drift (the same drift class as OBPI-04/05/06/07's
Source-Material wording).

### Canonical precedent — OBPI-0.25.0-31-validation-receipts-pattern

The same opsdev source module — `lib/validation_receipt.py`, 274 lines — was
already evaluated under **OBPI-0.25.0-31-validation-receipts-pattern**, which
landed `status: attested_completed` on **2026-04-13** with **Decision:
Confirm**. The five-point rationale established gzkit's superiority on twelve
named dimensions:

1. Strict superset of capability (~1396 L vs 274 L distributed).
2. Single narrow win (typed `ValidationAnchor`) is structurally entangled.
3. Architectural mismatch — central `.gzkit/ledger.jsonl` vs per-ADR storage.
4. Atomic transaction semantics already exist in gzkit (`obpi_complete.py`).
5. CLI integration only exists in gzkit (`gz obpi complete`, `gz adr emit-receipt`,
   `gz obpi reconcile`, `gz adr status`).

### New observation since 2026-04-13 — `EventAnchor` hardened

The "single narrow win" airlineops had at OBPI-0.25.0-31's authoring (typed
`ValidationAnchor` Pydantic model versus gzkit's `dict[str, str] | None`) has
since been **closed**. `src/gzkit/events.py:355` defines `EventAnchor` as a
frozen Pydantic model with `extra="forbid"`, replacing the prior dict shape
on `events.py:378, 389`. The OBPI-0.25.0-31 Closing Argument noted this as a
"future schema-hardening OBPI scoped independently of absorption" tracked
under GHI #143; that hardening has already landed. This makes the Confirm
verdict structurally stronger today than at 2026-04-13.

### Duplicate-OBPI signal — fifth instance

This is the **fifth** instance of the duplicate-OBPI defect tracked under
**GHI #376** (open):

| OBPI (ADR-0.25.0) | Decision | OBPI (ADR-0.26.0) | This-pipeline framing |
|-------------------|----------|-------------------|------------------------|
| OBPI-0.25.0-20 (`adr_governance.py`) | Confirm 2026-04-11 | OBPI-0.26.0-04 | Confirm-by-reference |
| OBPI-0.25.0-29 (`ledger_schema.py`) | Exclude 2026-04-13 | OBPI-0.26.0-05 | Exclude-by-reference |
| OBPI-0.25.0-26 (`drift_detection.py`) | Absorb 2026-04-09 | OBPI-0.26.0-06 | Absorb-by-reference |
| OBPI-0.25.0-22 (`adr_traceability.py`) | Confirm 2026-04-09 | OBPI-0.26.0-07 | Confirm-by-reference |
| **OBPI-0.25.0-31 (`validation_receipt.py`)** | **Confirm 2026-04-13** | **OBPI-0.26.0-08 (this brief)** | **Confirm-by-reference** |

Same root cause as the GHI #376 canonical: ADR-0.26.0 authoring did not check
whether ADR-0.25.0's absorption sweep had already covered each module in
scope.

### Sibling pattern — Confirm-by-reference precedent

`OBPI-0.26.0-07-adr-traceability` (attested 2026-05-01, today) recorded
`decision: Confirm` despite the same brief-scaffold "stale gzkit equivalent"
wording. The validator accepted the verdict; this brief follows that exact
precedent.

### Anti-pattern guard

Per OBPI-0.26.0-05's NON-GOAL: "Re-running the comparison work already
attested... on identical source material — divergent rationale on identical
material is itself a doctrine-drift signal." The same applies here.

---

## Files

**Edited (this OBPI):**

- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md`
  — frontmatter (`decision: Confirm`, `status` transitions through ceremony),
  body (Lane + Denied Paths + Discovery Checklist + Comparison + Decision +
  Tracking + Gate 4 N/A + Implementation Summary + Key Proof + Human
  Attestation placeholder + Closing Argument). ALL-CAPS section headings
  renamed to title case. `status: Pending` → `pending` if needed.

**Read-only (reference):**

- `src/gzkit/events.py` — gzkit's typed `EventAnchor` model (closes
  airlineops's narrow win)
- `src/gzkit/ledger_semantics.py` — semantic validation surface
- `src/gzkit/validate_pkg/ledger_check.py` — ledger-check surface
- `src/gzkit/temporal_drift.py` — anchor-consuming drift detection (absorbed
  via OBPI-0.25.0-26)
- `src/gzkit/utils.py` — `capture_validation_anchor_with_warnings`
- `src/gzkit/commands/obpi_complete.py` — atomic transaction
- `../airlineops/src/opsdev/lib/validation_receipt.py` (274 lines) — opsdev source
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-31-validation-receipts-pattern.md`
  — canonical precedent (Confirm)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md`
  — sibling Confirm-by-reference precedent (attested today)

**Out of scope (not touched):**

- `src/gzkit/events.py` and the rest of the receipt surface — Confirm; no
  modification needed
- `tests/test_events.py` and related — same
- `../airlineops/` (per brief — opsdev is upstream-only)
- `pyproject.toml`, lockfiles, CI files

---

## Steps

1. **Discovery checklist (bind-once cache).**
   - Read parent ADR `ADR-0.26.0-...md` to re-confirm the subtraction-test
     framing and Cross-Reference Matrix row 8.
   - Read brief frontmatter and body to identify scaffold-drift to correct
     (ALL-CAPS headings → title case; missing `Lane`/`Denied Paths`/`Discovery
     Checklist` sections; brief Source Material's "Partial in
     `src/gzkit/validate.py`" — stale, since `validate.py` is now a 121 L
     re-export shim).
   - Read OBPI-0.25.0-31-validation-receipts-pattern in full to extract the
     five-point Confirm rationale and twelve-dimension capability table that
     will be cited verbatim by reference.
   - Read OBPI-0.26.0-07 to mirror its Confirm-by-reference structural pattern.
   - Confirm GHI #376's duplicate-OBPI tracking contract.

2. **Verify gzkit receipt surface state.**
   - Spot-read `src/gzkit/events.py` to confirm `EventAnchor` exists at line
     355 (frozen Pydantic, `extra="forbid"`) and that `events.py:378, 389` use
     `EventAnchor | None` instead of the prior `dict[str, str] | None`.
   - Confirm the discriminated event-union still spans 17+ lifecycle event
     types (project init, ADR/OBPI creation, attestation, gate check, closeout,
     audit/OBPI receipt emission, artifact rename, etc.).
   - Confirm `commands/obpi_complete.py` still carries the atomic
     `_execute_transaction` with rollback semantics.
   - Confirm `temporal_drift.py` still consumes anchors from the central
     `.gzkit/ledger.jsonl`.

3. **Brief scaffold drift correction (in flight, mirroring OBPI-05/06/07).**
   - Rename ALL-CAPS section headings to title case (`OBJECTIVE` →
     `Objective`, etc.). Match `src/gzkit/schemas/obpi.json` required-headers
     contract.
   - Add missing structural sections: `Lane`, `Denied Paths`,
     `Discovery Checklist`. Use OBPI-07 wording as the template.
   - If frontmatter status is capital `Pending`, normalize to lowercase
     `pending`.
   - Rename `Verification Commands (Concrete)` → `Verification` and add two
     OBPI-specific verification commands.
   - Run `uv run gz obpi validate --authored ...` and address any reported
     drift before proceeding.

4. **Author comparison body (by reference).**
   - Add `## Comparison` section with the twelve-dimension table from
     OBPI-0.25.0-31, refreshed to current line anchors. Update the anchor-typing
     row to reflect that `EventAnchor` has closed the prior gap.
   - Add `### Source-material observation` subsection mirroring OBPI-07:
     brief Source Material says "Partial in `src/gzkit/validate.py`"; actual
     surface is `events.py` + `ledger_semantics.py` + `validate_pkg/ledger_check.py`
     + `temporal_drift.py` + `utils.capture_validation_anchor_with_warnings`
     + `commands/obpi_complete.py` (~1830 L). Body-level observation; do not
     amend the parent-ADR header.

5. **Author the decision section.**
   - Set frontmatter `decision: Confirm` (mirroring OBPI-07's precedent that
     this is permitted despite the brief's stale Source Material wording).
   - Add `## Decision` section: "**Confirm** (by reference to
     OBPI-0.25.0-31-validation-receipts-pattern, attested 2026-04-13)."
   - Author a five-point rationale citing the OBPI-0.25.0-31 precedent's
     five points verbatim, with a sixth point recording the new observation
     that the prior "narrow win" (typed `ValidationAnchor`) has been closed
     by `EventAnchor` at `events.py:355`.
   - **Surface the brief-scaffold defect explicitly** in a sub-paragraph:
     the brief Source Material asserts "Partial in `src/gzkit/validate.py`"
     but the actual gzkit receipt surface is ~1830 L distributed across six
     modules, structurally a strict superset; the assumption is itself a
     scaffold defect (fourth instance of the same defect class — also
     present in OBPI-04/05/06/07 briefs).
   - Add `### Tracking the duplicate-evaluation signal` subsection mirroring
     OBPI-04/05/06/07: extend GHI #376 via `gh issue comment` rather than
     file parallel GHI; this is the fifth structural instance.
   - Add `### Gate 4 (BDD): N/A` subsection: no operator-visible behavior
     change; existing receipt surface continues to function identically.

6. **Mark Acceptance Criteria.**
   - REQ-0.26.0-08-01: brief records `Confirm` decision (frontmatter + body).
     Tag `[doc]`.
   - REQ-0.26.0-08-02: rationale cites concrete capability differences;
     references OBPI-0.25.0-31 precedent's five rationale points + the
     EventAnchor hardening update. Tag `[doc]`.
   - REQ-0.26.0-08-03: Absorb path — N/A (Confirm outcome).
   - REQ-0.26.0-08-04: Confirm/Exclude path — gzkit's existing receipt surface
     is a strict superset on twelve named dimensions; opsdev's per-ADR
     storage model contradicts gzkit's central-ledger doctrine. Tag `[doc]`.
   - REQ-0.26.0-08-05: Gate 4 — `N/A` rationale (no operator-visible change).
     Tag `[doc]`.

7. **Author Implementation Summary, Key Proof, Human Attestation,
   Closing Argument.**
   - Implementation Summary: bullet `- Key: value` form per
     `_has_substantive_implementation_summary`.
   - Key Proof: at least one concrete command + observed output; cite ARB
     receipt IDs from Stage 3 inline.
   - Human Attestation: H2 placeholder section per OBPI-05/06/07 pattern (CLI
     fills it from `--attestation-text` at completion time).
   - Closing Argument: full prose paragraph mirroring OBPI-07's
     "**Confirm-by-reference**" framing.

8. **Stage 3 verification (canonical ARB-wrapped, OBPI-scoped).**
   - `uv run gz arb ruff` (clean)
   - `uv run gz arb typecheck` (clean)
   - `uv run gz arb step --name unittest -- uv run gz test --obpi
     OBPI-0.26.0-08-validation-receipt` (canonical OBPI-scoped per OBPI-05/06/07
     precedent — vacuous green for `[doc]` REQs)
   - `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
     (Heavy lane)
   - `uv run gz covers OBPI-0.26.0-08-validation-receipt --json` →
     `uncovered_reqs: 0`

9. **Stage 5 ceremony.**
   - Pre-flight: `uv run gz obpi precomplete OBPI-0.26.0-08-validation-receipt`
   - `uv run gz obpi complete ... --attestor 'Jeffry Babb'
     --attestation-text "..." --attestor-present`
   - `uv run gz obpi lock release ...` (use `--force` if shell-session ID
     differs from claim session, per OBPI-06/07 observation)
   - Remove pipeline markers
   - Git-sync #1, reconcile, ADR status, git-sync #2

10. **GHI #376 extension (fifth-instance comment).**
    - Operator-authorized step: `gh issue comment 376 --body "..."` adding
      this brief as the fifth structural instance. Permission gate is on
      this command — the operator must explicitly authorize it (per the
      OBPI-07 pipeline observation that `attest completed` does not authorize
      external GitHub comment posts).

---

## Verification (per brief)

```bash
test -f ../airlineops/src/opsdev/lib/validation_receipt.py
# Expected: opsdev source under review exists

test -f src/gzkit/events.py && test -f src/gzkit/validate_pkg/ledger_check.py
# Expected: gzkit existing receipt surface exists (Confirm precedent under OBPI-0.25.0-31)

rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Expected: brief frontmatter and Decision body record the Confirm verdict

rg -n 'OBPI-0.25.0-31' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Expected: brief cites the canonical precedent in body and Closing Argument

rg -n 'Absorb|Exclude|Confirm' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-08-validation-receipt
# Expected: vacuous parity-gate pass on [doc] REQ pattern

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes (Confirm: not required)

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Expected: brief captures Gate 4 N/A rationale
```

---

## Notes — Plan-Before-Exploration Disclosure (Step 6a)

### Destination-in-mind

After reading the brief, parent ADR row 8, and discovering
OBPI-0.25.0-31's Decision: Confirm with the five-point rationale plus
twelve-dimension capability table showing gzkit's existing distributed
receipt surface (~1396 L at the time, now ~1830 L with EventAnchor
hardening) is **architecturally a strict superset** of opsdev's 274-line
module, the conclusion I had already formed before plan authoring was:
**Confirm-by-reference to OBPI-0.25.0-31**, mirroring OBPI-0.26.0-07's
pattern (which also landed `decision: Confirm` despite the brief's stale
Source Material wording — the wording is itself a brief scaffold defect,
not a binding constraint). The new observation since 2026-04-13 — that
`EventAnchor` has closed the prior narrow win — only strengthens the
Confirm verdict.

### Rejected alternatives

1. **Decide Absorb.** Rejected: would require copying opsdev's per-ADR
   storage model into gzkit, which contradicts the central-ledger doctrine
   (`.gzkit/ledger.jsonl` is the single canonical event log). The
   OBPI-0.25.0-31 precedent established this approach is materially
   inferior to gzkit's discriminated-union event surface, and absorbing
   it would degrade governance compliance (parallel storage systems
   double the audit footprint). Also would invalidate the OBPI-0.25.0-31
   attestation.

2. **Decide Exclude.** Rejected: gzkit's surface IS the answer to
   ADR-0.26.0 item 8's question (does gzkit have validation-receipt
   capability?). Naming the outcome "Exclude" while gzkit's superior
   surface ships across six modules is a semantic miscoding of the
   precedent.

3. **Honor the brief's "Partial in `src/gzkit/validate.py`" wording
   literally.** Rejected: `validate.py` is now a 121 L re-export shim,
   not the actual surface. OBPI-0.26.0-07 already established the
   precedent that stale brief Source Material wording is a scaffold
   defect, not a binding constraint, and that `decision: Confirm` is
   accepted by the validator. Honoring an incorrect brief assumption
   over a known-correct decision would be doctrine drift.

4. **Re-run the comparison from scratch.** Rejected: OBPI-05's NON-GOAL
   names this as doctrine drift on identical source material.

5. **Decide Confirm but suppress the brief-scaffold-defect surfacing.**
   Rejected: the assumption is itself a structural defect that crosses
   multiple ADR-0.26.0 briefs (04/05/06/07/08). Surfacing it explicitly
   serves the broader doctrine — operators need to see the pattern and
   GHI #376 needs the structural-instance count to drive mitigation
   prioritization.

6. **File a new GHI for the fifth duplicate.** Rejected: GHI #376
   already names the same root cause. A parallel GHI fragments
   tracking; the canonical mitigation
   (`gz validate --absorption-duplicates`) is one canonical surface.

### Plan-before-exploration honesty

Reading order before writing this plan:

1. Session orientation showed OBPI-0.26.0-07 stale and OBPI-0.26.0-08 invoked.
2. Resumed and completed OBPI-0.26.0-07 first (Confirm-by-reference; same
   pattern).
3. OBPI-0.26.0-08 brief (the contract).
4. opsdev `lib/validation_receipt.py` (size verified at 274 lines).
5. **Found** `src/gzkit/events.py`, `ledger_semantics.py`,
   `validate_pkg/ledger_check.py`, `temporal_drift.py`,
   `commands/obpi_complete.py` via the OBPI-0.25.0-31 precedent's
   citations (already known).
6. **Found** `OBPI-0.25.0-31-validation-receipts-pattern.md` via
   `find docs/design/adr -path '*OBPI-0.25*' -name '*validation*'`.
7. OBPI-0.25.0-31 Decision: Confirm with five-point rationale and
   twelve-dimension capability table (the precedent).
8. Verified `EventAnchor` exists at `events.py:355` as a frozen Pydantic
   model — confirms the prior narrow win has closed.
9. Confirmed OBPI-0.26.0-07 (just attested today) used `decision: Confirm`
   despite same scaffold-defect wording (precedent for surfacing the
   defect).

The destination crystallized at step 7 (precedent decision). Step 8
strengthened it. Steps 1-6 were read-only orientation; step 9 confirmed
the framing precedent. Plan written after that.

---

## Acceptance

Plan is ready when:

- [x] All Step 1 discovery items have a citable file location.
- [x] All Step 5 rationale points name OBPI-0.25.0-31's five-point rationale.
- [x] The destination-in-mind disclosure names the conclusion already formed.
- [x] Rejected alternatives section names ≥4 alternatives with concrete reasons.
- [x] Verification block reproduces every brief-required command.
- [x] No `src/` or `tests/` paths in Files-Edited list (Confirm is doc-only).
