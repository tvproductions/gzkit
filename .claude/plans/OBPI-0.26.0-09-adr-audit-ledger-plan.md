# Plan: OBPI-0.26.0-09 ADR Audit Ledger (Confirm-by-Reference)

**OBPI:** `OBPI-0.26.0-09-adr-audit-ledger`
**Parent ADR:** `ADR-0.26.0-governance-library-module-absorption` (Heavy lane,
`feature` kind)
**Lane:** Heavy
**Plan kind:** Doc-only — Confirm-by-reference (no `src/` or `tests/` edits)
**Author date:** 2026-05-01

---

## Context

### Brief

`docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md`
asks: evaluate `../airlineops/src/opsdev/lib/adr_audit_ledger.py` (249 lines)
and decide **Absorb** or **Exclude**. Brief Source Material asserts gzkit
equivalent is "None" and brief Assumptions explicitly forecloses the Confirm
path ("No existing gzkit equivalent means either Absorb or Exclude — there is
no Confirm path"). The brief frontmatter already records
`paired_with: OBPI-0.25.0-19-adr-audit-ledger-pattern`, signaling the canonical
precedent.

### What the brief asserts vs what is observable

The brief asserts no gzkit equivalent. That assertion is **stale at this
brief's authoring time**: gzkit ships an audit ledger / Gate 5 completeness
surface distributed across:

- `src/gzkit/commands/adr_audit.py` (**758 L** — grown from 415 L at
  OBPI-0.25.0-19 authoring, +83%)
- `src/gzkit/validate_pkg/ledger_check.py` (**379 L** — JSONL ledger schema
  validation, unchanged)
- `src/gzkit/commands/obpi_audit_cmd.py` (**423 L** — evidence gathering: test
  discovery, execution, coverage, unchanged)

That is **~1,560 L** distributed across three modules — versus airlineops's
249-line single module. The brief Source Material's "gzkit equivalent: None"
wording is stale brief-scaffold drift (the same drift class as
OBPI-04/05/06/07/08's Source-Material wording, all of which landed
`decision: Confirm` despite the assertion).

### Canonical precedent — OBPI-0.25.0-19-adr-audit-ledger-pattern

The same opsdev source module — `lib/adr_audit_ledger.py`, 249 lines — was
already evaluated under **OBPI-0.25.0-19-adr-audit-ledger-pattern**, which
landed `status: attested_completed` on **2026-04-11** with **Decision:
Confirm**. The five-point rationale established gzkit's superiority on five
named dimensions:

1. **Architecture (State Doctrine):** gzkit reads the central ledger graph
   (Layer 1/2 source of truth), not a local `obpi-audit.jsonl` file.
   Architecturally superior — single source of truth, no local cache
   divergence risk.
2. **Evidence depth:** gzkit's `_inspect_obpi_brief()` checks brief file
   content (Implementation Summary, Key Proof, Human Attestation sections),
   not just ledger status values. Catches evidence gaps that ledger entries
   alone cannot detect.
3. **REQ traceability:** `adr_audit_check()` also verifies `@covers`
   annotations — a verification dimension airlineops does not check at all.
4. **Convention compliance:** airlineops uses stdlib `dataclass` for
   `LedgerCheckResult`, which violates gzkit's Pydantic model policy.
   Absorbing would require a full rewrite to Pydantic `BaseModel`, defeating
   the purpose of pattern absorption.
5. **Dependency isolation:** airlineops module depends on `adr_recon`
   helpers (`find_adr_folder`, `find_adr_ledger_path`, `normalize_adr_id`,
   `parse_obpi_table`, `read_ledger_entries`). gzkit has its own ADR
   resolution pipeline (`resolve_adr_file`, `resolve_adr_ledger_id`, ledger
   graph queries).

### New observation since 2026-04-11 — `adr_audit.py` has grown 83%

Since the OBPI-0.25.0-19 attestation, `src/gzkit/commands/adr_audit.py` has
grown from **415 L to 758 L** (+343 L, +82.7%). The growth is layered on the
same architectural foundation (central ledger graph, brief content inspection,
REQ `@covers` traceability) but materially deepens the audit surface — adding
the `_requires_human_obpi_attestation` three-axis predicate (kind × lane ×
sensitivity, ADR-0.0.22), the `_enforce_human_attestation_authenticity` TTY
gate (GHI #290), the `--attestor-present` co-presence proxy (GHI #292), and
multiple validator extensions absorbed under OBPI-0.0.22-01..06. The current
gzkit surface is therefore **structurally stronger** than at the 2026-04-11
precedent attestation, not weaker. The Confirm verdict holds *a fortiori*.

### Duplicate-OBPI signal — sixth instance

This is the **sixth** instance of the duplicate-OBPI defect tracked under
**GHI #376** (open):

| OBPI (ADR-0.25.0) | Decision | OBPI (ADR-0.26.0) | This-pipeline framing |
|-------------------|----------|-------------------|------------------------|
| OBPI-0.25.0-20 (`adr_governance.py`) | Confirm 2026-04-11 | OBPI-0.26.0-04 | Confirm-by-reference |
| OBPI-0.25.0-29 (`ledger_schema.py`) | Exclude 2026-04-13 | OBPI-0.26.0-05 | Exclude-by-reference |
| OBPI-0.25.0-26 (`drift_detection.py`) | Absorb 2026-04-09 | OBPI-0.26.0-06 | Absorb-by-reference |
| OBPI-0.25.0-22 (`adr_traceability.py`) | Confirm 2026-04-09 | OBPI-0.26.0-07 | Confirm-by-reference |
| OBPI-0.25.0-31 (`validation_receipt.py`) | Confirm 2026-04-13 | OBPI-0.26.0-08 | Confirm-by-reference |
| **OBPI-0.25.0-19 (`adr_audit_ledger.py`)** | **Confirm 2026-04-11** | **OBPI-0.26.0-09 (this brief)** | **Confirm-by-reference** |

Same root cause as the GHI #376 canonical: ADR-0.26.0 authoring did not check
whether ADR-0.25.0's earlier absorption sweep had already covered each module
in scope.

### Sibling pattern — Confirm-by-reference precedent

`OBPI-0.26.0-08-validation-receipt` (attested 2026-05-01) recorded
`decision: Confirm` despite the same brief-scaffold "stale gzkit equivalent"
wording. The validator accepted the verdict; this brief follows that exact
precedent. Notable: OBPI-0.26.0-08's brief Assumptions also contained an
explicit "no Confirm path" forecloser (struck through and flagged as
brief-scaffold defect in the completed body) — exactly the same shape as
this brief's Assumption block.

### Anti-pattern guard

Per OBPI-0.26.0-05's NON-GOAL: "Re-running the comparison work already
attested... on identical source material — divergent rationale on identical
material is itself a doctrine-drift signal." The same applies here.

---

## Files

**Edited (this OBPI):**

- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md`
  — frontmatter (`decision: Confirm`, `status: Completed`), body
  (Lane + Denied Paths + Discovery Checklist + Comparison + Decision +
  Tracking + Gate 4 N/A + Implementation Summary + Key Proof + Human
  Attestation placeholder + Closing Argument). ALL-CAPS section headings
  (`OBJECTIVE`, `SOURCE MATERIAL`, `ASSUMPTIONS`, `NON-GOALS`,
  `REQUIREMENTS (FAIL-CLOSED)`, `ALLOWED PATHS`, `QUALITY GATES (Heavy)`)
  renamed to title case per `src/gzkit/schemas/obpi.json` required-headers
  contract. `Verification Commands (Concrete)` → `Verification` with two
  OBPI-specific verification commands.

**Read-only (reference):**

- `src/gzkit/commands/adr_audit.py` (758 L) — gzkit's audit completeness
  check, three-axis attestation predicate, brief content inspection
- `src/gzkit/validate_pkg/ledger_check.py` (379 L) — JSONL ledger validation
- `src/gzkit/commands/obpi_audit_cmd.py` (423 L) — evidence gathering: test
  discovery, execution, coverage
- `../airlineops/src/opsdev/lib/adr_audit_ledger.py` (249 lines) — opsdev
  source under review
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-19-adr-audit-ledger-pattern.md`
  — canonical precedent (Decision: Confirm, attested 2026-04-11)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md`
  — sibling Confirm-by-reference precedent (attested 2026-05-01)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-07-adr-traceability.md`
  — earlier Confirm-by-reference precedent (attested 2026-05-01)

**Out of scope (not touched):**

- `src/gzkit/commands/adr_audit.py` and the rest of the audit surface —
  Confirm; no modification needed
- `tests/commands/test_adr_audit.py` and related — same
- `../airlineops/` (per brief — opsdev is upstream-only)
- `pyproject.toml`, lockfiles, CI files

---

## Steps

1. **Discovery checklist (bind-once cache).**
   - Read parent ADR `ADR-0.26.0-governance-library-module-absorption.md` to
     re-confirm the subtraction-test framing and Cross-Reference Matrix row 9
     ("`adr_audit_ledger.py` | None | Strong absorption candidate unless
     ADR-specific audit semantics should remain implicit").
   - Read brief frontmatter and body to identify scaffold-drift to correct
     (ALL-CAPS headings → title case; missing `Lane`/`Denied Paths`/`Discovery
     Checklist` sections; brief Source Material's "gzkit equivalent: None" —
     stale, since gzkit ships ~1,560 L distributed across three modules).
   - Read OBPI-0.25.0-19-adr-audit-ledger-pattern in full to extract the
     five-point Confirm rationale and dimension comparison table that will be
     cited verbatim by reference.
   - Read OBPI-0.26.0-08 to mirror its Confirm-by-reference structural pattern
     (the freshest sibling precedent).
   - Confirm GHI #376's duplicate-OBPI tracking contract is open and the
     count of structural instances is now 5 (this brief becomes #6).

2. **Verify gzkit audit surface state.**
   - `wc -l src/gzkit/commands/adr_audit.py` — confirm 758 L (was 415 L at
     OBPI-0.25.0-19 authoring).
   - `wc -l src/gzkit/validate_pkg/ledger_check.py` — confirm 379 L
     (unchanged).
   - `wc -l src/gzkit/commands/obpi_audit_cmd.py` — confirm 423 L (unchanged).
   - Spot-read `commands/adr_audit.py` for `_requires_human_obpi_attestation`,
     `_enforce_human_attestation_authenticity`, `--attestor-present` handler,
     and `_inspect_obpi_brief` — confirm three-axis predicate + TTY gate +
     co-presence proxy + brief content inspection are all present (these are
     the post-OBPI-0.25.0-19 strengthenings that justify "Confirm holds *a
     fortiori*").
   - Confirm `adr_audit_check()` still walks the central
     `.gzkit/ledger.jsonl` graph rather than per-ADR audit files.

3. **Brief scaffold drift correction (in flight, mirroring OBPI-05/06/07/08).**
   - Rename ALL-CAPS section headings to title case (`OBJECTIVE` → `Objective`,
     `SOURCE MATERIAL` → `Source Material`, `ASSUMPTIONS` → `Assumptions`,
     `NON-GOALS` → `Non-Goals`, `REQUIREMENTS (FAIL-CLOSED)` →
     `Requirements (FAIL-CLOSED)`, `ALLOWED PATHS` → `Allowed Paths`,
     `QUALITY GATES (Heavy)` → `Quality Gates`). Match
     `src/gzkit/schemas/obpi.json` required-headers contract.
   - Add missing structural sections: `Lane`, `Denied Paths`,
     `Discovery Checklist`. Use OBPI-08 wording as the template.
   - If frontmatter status is capital `Pending`, normalize as needed (matrix
     pattern from sibling 08 is `status: Completed` at completion time).
   - Rename `Verification Commands (Concrete)` → `Verification` and add two
     OBPI-specific verification commands citing OBPI-0.25.0-19 precedent.
   - Run `uv run gz obpi validate --authored ...` and address any reported
     drift before proceeding.

4. **Author comparison body (by reference).**
   - Add `## Comparison` section with the dimension comparison table from
     OBPI-0.25.0-19, refreshed to current line anchors (758 L for
     `adr_audit.py`, plus the post-precedent strengthenings: three-axis
     attestation predicate, TTY gate, `--attestor-present`).
   - Add `### Source-material observation` subsection mirroring OBPI-08:
     brief Source Material says gzkit equivalent is "None"; actual surface is
     `commands/adr_audit.py` + `validate_pkg/ledger_check.py` +
     `commands/obpi_audit_cmd.py` (~1,560 L). Body-level observation; do not
     amend the parent-ADR Cross-Reference Matrix header (mirror of
     OBPI-04/05/06/07/08 pattern).

5. **Author the decision section.**
   - Set frontmatter `decision: Confirm` (mirroring OBPI-07/08's precedent
     that this is permitted despite the brief's stale "no Confirm path"
     Assumption).
   - Add `## Decision` section: "**Confirm** (by reference to
     OBPI-0.25.0-19-adr-audit-ledger-pattern, attested 2026-04-11)."
   - Author a six-point rationale: cite the OBPI-0.25.0-19 precedent's five
     points verbatim, with a sixth point recording the new observation that
     `adr_audit.py` has grown 83% since 2026-04-11 with strengthening
     extensions (three-axis attestation, TTY gate, co-presence proxy).
   - **Surface the brief-scaffold defect explicitly** in a sub-paragraph:
     the brief Source Material asserts gzkit equivalent is "None" but the
     actual gzkit audit surface is ~1,560 L distributed across three
     modules, structurally a strict superset; the assumption is itself a
     scaffold defect (sixth instance of the same defect class — also
     present in OBPI-04/05/06/07/08 briefs).
   - Add `### Tracking the duplicate-evaluation signal` subsection mirroring
     OBPI-04/05/06/07/08: extend GHI #376 via `gh issue comment` rather than
     file parallel GHI; this is the sixth structural instance.
   - Add `### Gate 4 (BDD): N/A` subsection: no operator-visible behavior
     change; existing audit surface continues to function identically.

6. **Mark Acceptance Criteria.**
   - REQ-0.26.0-09-01: brief records `Confirm` decision (frontmatter + body).
     Tag `[doc]`.
   - REQ-0.26.0-09-02: rationale cites concrete capability differences;
     references OBPI-0.25.0-19 precedent's five rationale points + the
     `adr_audit.py` 83% growth update. Tag `[doc]`.
   - REQ-0.26.0-09-03: Absorb path — N/A (Confirm outcome).
   - REQ-0.26.0-09-04: Exclude path — N/A (Confirm outcome). Note the brief
     phrasing is "If Exclude: document why the module is domain-specific";
     the Confirm verdict satisfies the same operator-decision constraint
     (no upstream absorption warranted, with documented rationale).
   - REQ-0.26.0-09-05: Gate 4 — `N/A` rationale (no operator-visible change).
     Tag `[doc]`.

7. **Author Implementation Summary, Key Proof, Human Attestation,
   Closing Argument.**
   - Implementation Summary: bullet `- Key: value` form per
     `_has_substantive_implementation_summary`.
   - Key Proof: at least one concrete command + observed output; cite ARB
     receipt IDs from Stage 3 inline.
   - Human Attestation: H2 placeholder section per OBPI-05/06/07/08 pattern
     (CLI fills it from `--attestation-text` at completion time).
   - Closing Argument: full prose paragraph mirroring OBPI-08's
     "**Confirm-by-reference**" framing.

8. **Stage 3 verification (canonical ARB-wrapped, OBPI-scoped).**
   - `uv run gz arb ruff` (clean)
   - `uv run gz arb typecheck` (clean)
   - `uv run gz arb step --name unittest -- uv run gz test --obpi
     OBPI-0.26.0-09-adr-audit-ledger` (canonical OBPI-scoped per
     OBPI-05/06/07/08 precedent — vacuous green for `[doc]` REQs)
   - `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
     (Heavy lane)
   - `uv run gz covers OBPI-0.26.0-09-adr-audit-ledger --json` →
     `uncovered_reqs: 0`

9. **Stage 5 ceremony.**
   - Pre-flight: `uv run gz obpi precomplete OBPI-0.26.0-09-adr-audit-ledger`
   - `uv run gz obpi complete ... --attestor 'Jeffry Babb'
     --attestation-text "..." --attestor-present`
     (primary path per Stage 5 Step 2 GHI #292; pipeline marker satisfies
     co-presence proxy)
   - `uv run gz obpi lock release ...` (use `--force` if shell-session ID
     differs from claim session, per OBPI-06/07/08 observation)
   - Remove pipeline markers
   - Git-sync #1, reconcile, ADR status, git-sync #2

10. **GHI #376 extension (sixth-instance comment).**
    - Operator-authorized step: `gh issue comment 376 --body "..."` adding
      this brief as the sixth structural instance. Permission gate is on
      this command — the operator must explicitly authorize it (per the
      OBPI-07/08 pipeline observation that `attest completed` does not
      authorize external GitHub comment posts).

---

## Verification (per brief)

```bash
test -f ../airlineops/src/opsdev/lib/adr_audit_ledger.py
# Expected: opsdev source under review exists

test -f src/gzkit/commands/adr_audit.py && test -f src/gzkit/commands/obpi_audit_cmd.py
# Expected: gzkit existing audit surface exists (Confirm precedent under OBPI-0.25.0-19)

rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: brief frontmatter and Decision body record the Confirm verdict

rg -n 'OBPI-0.25.0-19' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: brief cites the canonical precedent in body and Closing Argument

rg -n 'Absorb|Exclude|Confirm' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-09-adr-audit-ledger
# Expected: vacuous parity-gate pass on [doc] REQ pattern via _synthesize_doc_proof_linkage

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes (Confirm: not required)

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md
# Expected: brief captures Gate 4 N/A rationale
```

---

## Notes — Plan-Before-Exploration Disclosure (Step 6a)

### Destination-in-mind

After reading the brief, parent ADR Cross-Reference Matrix row 9, and
discovering OBPI-0.25.0-19's Decision: Confirm with the five-point rationale
plus dimension comparison table showing gzkit's existing audit surface
(~800 L at the time, now ~1,560 L with `adr_audit.py` 83% growth) is
**architecturally a strict superset** of opsdev's 249-line module, the
conclusion I had already formed before plan authoring was: **Confirm-by-
reference to OBPI-0.25.0-19**, mirroring OBPI-0.26.0-08's pattern (which
landed `decision: Confirm` despite the brief's stale "no Confirm path"
Assumption — the wording is itself a brief-scaffold defect, not a binding
constraint). The new observation since 2026-04-11 — that `adr_audit.py` has
grown 83% with three-axis attestation, TTY gate, and co-presence proxy
strengthenings — only makes the Confirm verdict structurally stronger today
than at the precedent attestation.

### Rejected alternatives

1. **Decide Absorb.** Rejected: would require copying opsdev's per-ADR
   audit-ledger model into gzkit, which contradicts the central-ledger
   doctrine (`.gzkit/ledger.jsonl` is the single canonical event log). The
   OBPI-0.25.0-19 precedent established this approach is materially
   inferior to gzkit's central-ledger-graph audit (single source of truth,
   no local cache divergence), and absorbing it would degrade governance
   compliance. Also would invalidate the OBPI-0.25.0-19 attestation. The
   convention-compliance dimension (stdlib `dataclass` vs gzkit Pydantic)
   would require a full rewrite, defeating the purpose of pattern
   absorption.

2. **Decide Exclude.** Rejected: gzkit's surface IS the answer to
   ADR-0.26.0 item 9's question (does gzkit have ADR-audit-ledger
   capability?). Naming the outcome "Exclude" while gzkit's superior
   surface ships across three modules is a semantic miscoding of the
   precedent. "Exclude" is reserved for source modules whose semantics are
   ops-specific (cf. OBPI-0.26.0-05 `ledger_schema` Exclude-by-reference);
   the audit-ledger pattern is governance-generic, not airline-specific.

3. **Honor the brief's "no Confirm path" Assumption literally.** Rejected:
   OBPI-0.26.0-08 already established the precedent that stale brief
   Source Material wording (and matching Assumption foreclosers) are
   scaffold defects, not binding constraints, and that `decision: Confirm`
   is accepted by the validator. Honoring an incorrect brief assumption
   over a known-correct decision would be doctrine drift.

4. **Re-run the comparison from scratch.** Rejected: OBPI-05's NON-GOAL
   names this as doctrine drift on identical source material.

5. **Decide Confirm but suppress the brief-scaffold-defect surfacing.**
   Rejected: the assumption is itself a structural defect that crosses
   multiple ADR-0.26.0 briefs (04/05/06/07/08/09). Surfacing it explicitly
   serves the broader doctrine — operators need to see the pattern and
   GHI #376 needs the structural-instance count to drive mitigation
   prioritization.

6. **File a new GHI for the sixth duplicate.** Rejected: GHI #376
   already names the same root cause. A parallel GHI fragments
   tracking; the canonical mitigation
   (`gz validate --absorption-duplicates`) is one canonical surface.

### Plan-before-exploration honesty

Reading order before writing this plan:

1. Session orientation showed ADR-0.26.0 with 8/12 OBPIs attested and
   OBPI-09 next pending; user invoked `/gz-obpi-pipeline OBPI-0.26.0-09`.
2. CLI plan-audit reported `FAIL` (no plan file); skill mandate is to
   author one in `.claude/plans/` before implementation.
3. Read OBPI-0.26.0-09 brief (the contract): Source Material asserts no
   gzkit equivalent; Assumptions explicitly forecloses Confirm.
4. Read parent ADR `ADR-0.26.0-governance-library-module-absorption.md`
   to re-confirm subtraction-test framing and matrix row 9.
5. Read sibling OBPI-0.26.0-08 (most-recently-attested precedent) brief
   end-to-end to extract the Confirm-by-reference pattern.
6. Read sibling OBPI-0.26.0-08's plan file to mirror plan structure.
7. **Found** `OBPI-0.25.0-19-adr-audit-ledger-pattern.md` via
   `find docs/design/adr -path '*OBPI-0.25.0-19*'`.
8. OBPI-0.25.0-19 Decision: Confirm with five-point rationale and
   dimension comparison table (the precedent).
9. Verified airlineops source exists at 249 lines (`wc -l`).
10. Verified gzkit equivalent surface line counts:
    - `commands/adr_audit.py`: 758 L (was 415 L at OBPI-0.25.0-19
      authoring; +83%)
    - `validate_pkg/ledger_check.py`: 379 L (unchanged)
    - `commands/obpi_audit_cmd.py`: 423 L (unchanged)
    - Total: ~1,560 L (vs ~800 L at OBPI-0.25.0-19 authoring)

The destination crystallized at step 8 (precedent decision). Step 10
strengthened it (the gzkit audit surface has grown 83%, making the
Confirm verdict *a fortiori* stronger). Steps 1-7 were read-only
orientation; step 9 confirmed the source artifact still matches the
precedent's 249-line shape. Plan written after that.

---

## Acceptance

Plan is ready when:

- [x] All Step 1 discovery items have a citable file location.
- [x] All Step 5 rationale points name OBPI-0.25.0-19's five-point rationale
      verbatim, with a sixth point for the new `adr_audit.py` 83% growth
      observation.
- [x] The destination-in-mind disclosure names the conclusion already formed
      (Confirm-by-reference to OBPI-0.25.0-19).
- [x] Rejected alternatives section names ≥4 alternatives with concrete
      reasons (this plan names 6).
- [x] Verification block reproduces every brief-required command.
- [x] No `src/` or `tests/` paths in Files-Edited list (Confirm is doc-only).
