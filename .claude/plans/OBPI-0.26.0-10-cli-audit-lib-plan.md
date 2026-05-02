# Plan: OBPI-0.26.0-10 CLI Audit Library (Confirm-by-Reference)

**OBPI:** `OBPI-0.26.0-10-cli-audit-lib`
**Parent ADR:** `ADR-0.26.0-governance-library-module-absorption` (Heavy lane,
`feature` kind)
**Lane:** Heavy
**Plan kind:** Doc-only — Confirm-by-reference (no `src/` or `tests/` edits)
**Author date:** 2026-05-01

---

## Context

### Brief

`docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md`
asks: evaluate `../airlineops/src/opsdev/lib/cli_audit.py` (238 lines) and
decide **Absorb**, **Confirm**, or **Exclude**. Brief Source Material asserts
gzkit equivalent is "Partial in `src/gzkit/cli.py`." That assertion is stale —
gzkit's CLI audit surface lives in `src/gzkit/commands/cli_audit.py` (235 L)
plus the `src/gzkit/doc_coverage/` package (1,065 L across 6 files), totaling
~1,300 L. Brief frontmatter already records `paired_with: OBPI-0.25.0-24-cli-audit-pattern`.

### Canonical precedent — OBPI-0.25.0-24-cli-audit-pattern

The same opsdev source module (`lib/cli_audit.py`, 238 lines) was already
evaluated under **OBPI-0.25.0-24-cli-audit-pattern** and recorded **Decision:
Confirm** with a six-point rationale anchored on:

1. **AST-based vs private API introspection.** gzkit's `discover_commands()`
   uses static AST parsing; airlineops walks `parser._actions` and
   `argparse._SubParsersAction` (undocumented private APIs).
2. **5-surface documentation coverage vs parser structural checks.** gzkit
   enforces 5 documentation surfaces (manpage, index_entry, operator_runbook,
   governance_runbook, docstring); airlineops checks parser tree structure
   only.
3. **Manifest-driven obligations vs ad-hoc checks.** gzkit's
   `config/doc-coverage.json` declares per-command obligations; airlineops
   has no extensibility mechanism.
4. **Type-safe models vs untyped dicts.** gzkit uses 7 frozen Pydantic
   `BaseModel` classes with `extra="forbid"`; airlineops uses
   `dict[str, Any]`.
5. **76 tests vs 1 test.** gzkit's test suite covers AST discovery, all 5
   surface checks, orphan detection, manifest loading/validation; airlineops
   has a single test verifying JSON artifact files are written.
6. **Subtraction test.** Removing gzkit's coverage from airlineops leaves
   parser-internal introspection, which is unsuitable for gzkit's AST-based
   approach. Narrower problem already subsumed by broader coverage model.

### New observation since OBPI-0.25.0-24 authoring

Surface growth: `commands/cli_audit.py` grew from 226 L to 235 L (+9 L, +4%).
The `doc_coverage/` package grew from ~802 L to 1,065 L (+263 L, +33%) —
adding `flag_scanner.py` (182 L) and expanding `scanner.py` to 538 L. The
total surface is now ~1,300 L vs ~1,028 L at the precedent attestation. The
post-precedent extensions deepen the coverage rigor (flag-level scanning,
expanded scanner heuristics) without altering the architectural foundation.
Confirm holds *a fortiori*.

### Duplicate-OBPI signal — seventh instance

This is the seventh instance of the duplicate-OBPI defect tracked under GHI
#376. Same root cause as the prior six (OBPI-0.26.0-04, -05, -06, -07, -08,
-09): ADR-0.26.0 authoring did not check whether ADR-0.25.0's earlier
absorption sweep had already covered each module in scope.

### Sibling pattern

`OBPI-0.26.0-09-adr-audit-ledger` (just attested) recorded
`decision: Confirm` despite the same brief-scaffold drift. This brief
follows that exact precedent.

---

## Files

**Edited (this OBPI):**

- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md`
  — frontmatter (`decision: Confirm`, `status: pending`); body
  (Lane + Denied Paths + Discovery Checklist + Comparison + Decision +
  Tracking + Gate 4 N/A + Implementation Summary + Key Proof + Human
  Attestation placeholder + Closing Argument). ALL-CAPS section headings
  → title case.

**Read-only (reference):**

- `src/gzkit/commands/cli_audit.py` (235 L)
- `src/gzkit/doc_coverage/{scanner,flag_scanner,manifest,models,runner,__init__}.py` (1,065 L)
- `../airlineops/src/opsdev/lib/cli_audit.py` (238 lines)
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-24-cli-audit-pattern.md`
  (canonical precedent; Decision: Confirm)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-09-adr-audit-ledger.md`
  (most-recently-attested sibling Confirm-by-reference precedent)

**Out of scope (not touched):**

- `src/gzkit/commands/cli_audit.py` and `src/gzkit/doc_coverage/` —
  Confirm; no modification needed
- `tests/commands/test_cli_audit.py` and related — same
- `../airlineops/`, `pyproject.toml`, lockfiles, CI files

---

## Steps

1. **Discovery (cache).**
   - Read parent ADR Cross-Reference Matrix row 10.
   - Read OBPI-0.25.0-24-cli-audit-pattern in full (six-point rationale
     anchored on AST vs private API, 5-surface coverage, manifest
     obligations, Pydantic vs dict, 76 tests vs 1, subtraction test).
   - Read OBPI-0.26.0-09 (just attested) for the freshest sibling shape.
   - Confirm GHI #376 instance count is now 6 (this brief becomes #7).

2. **Verify gzkit cli-audit surface.**
   - `wc -l src/gzkit/commands/cli_audit.py` → 235 L.
   - `wc -l src/gzkit/doc_coverage/*.py` → 1,065 L total across 6 files.
   - Spot-read `commands/cli_audit.py` for `discover_commands()` (AST-based)
     and `doc_coverage/flag_scanner.py` (post-precedent extension).

3. **Brief scaffold drift correction.**
   - ALL-CAPS headings → title case (`OBJECTIVE` → `Objective`, etc.).
   - Add `Lane`, `Denied Paths`, `Discovery Checklist` sections.
   - Status `Pending` → `pending`.
   - Rename `Verification Commands (Concrete)` → `Verification`.

4. **Author Comparison body.**
   - Add `## Comparison` with the six-dimension table from OBPI-0.25.0-24,
     refreshed to current line anchors (235 L for cli_audit.py + 1,065 L
     for doc_coverage/ = ~1,300 L total).
   - Add `### Source-material observation`: brief says "Partial in
     `src/gzkit/cli.py`"; actual surface is `commands/cli_audit.py` +
     `doc_coverage/` package.

5. **Author Decision section.**
   - `## Decision`: Confirm-by-reference to OBPI-0.25.0-24.
   - Six-point rationale citing the precedent verbatim, plus a seventh
     point recording the post-precedent surface growth (+26% across
     ~1,300 L).
   - Surface the brief-scaffold defect (seventh instance).
   - Tracking the duplicate-evaluation signal (table of all 7 instances).
   - Gate 4 (BDD): N/A.

6. **Mark Acceptance Criteria** as `[doc]` REQs satisfied.

7. **Author Implementation Summary, Key Proof, Closing Argument.**

8. **Stage 3 verification (canonical ARB-wrapped, OBPI-scoped):**
   - `uv run gz arb ruff`
   - `uv run gz arb typecheck`
   - `uv run gz arb step --name unittest -- uv run gz test --obpi OBPI-0.26.0-10-cli-audit-lib`
   - `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
   - `uv run gz covers OBPI-0.26.0-10-cli-audit-lib --json` → uncovered_reqs:0

9. **Stage 5 ceremony.**
   - `uv run gz obpi precomplete OBPI-0.26.0-10-cli-audit-lib`
   - `uv run gz obpi lock claim OBPI-0.26.0-10-cli-audit-lib`
   - Add Human Attestation placeholder to brief.
   - `uv run gz obpi complete ... --attestor 'g0'
     --attestation-text "..." --attestor-present`
   - `uv run gz obpi lock release ... --force`
   - Clear pipeline markers.
   - Git-sync #1, reconcile, ADR status, git-sync #2.

10. **GHI #376 extension (operator-authorized; deferred).**

---

## Verification (per brief)

```bash
test -f ../airlineops/src/opsdev/lib/cli_audit.py
test -f src/gzkit/commands/cli_audit.py && test -d src/gzkit/doc_coverage
rg -n '^decision: Confirm' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
rg -n 'OBPI-0.25.0-24' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
uv run gz test --obpi OBPI-0.26.0-10-cli-audit-lib
rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md
```

---

## Notes — Plan-Before-Exploration Disclosure (Step 6a)

### Destination-in-mind

Conclusion already formed: **Confirm-by-reference to OBPI-0.25.0-24**,
mirroring OBPI-0.26.0-09's (and 04/07/08's) just-attested pattern. The
six-point rationale already exists in the precedent; surface growth since
2026-04-09 strengthens it. No novel decision space.

### Rejected alternatives

1. **Absorb.** Rejected: would replace gzkit's AST-based discovery with
   `parser._actions` private-API introspection — strict regression on
   maintainability. Would also require a stdlib-dataclass-to-Pydantic
   rewrite. OBPI-0.25.0-24 attestation would be invalidated.
2. **Exclude.** Rejected: CLI audit is governance-generic, not
   ops-specific. The narrower problem opsdev solves (parser tree
   consistency) is subsumed by gzkit's broader coverage model.
3. **Honor "Partial in cli.py" literally.** Rejected: same scaffold-defect
   class as OBPI-04/05/06/07/08/09. The actual gzkit surface lives in
   `commands/cli_audit.py` + `doc_coverage/`, not `cli.py`.
4. **Re-run comparison from scratch.** Rejected: OBPI-05 NON-GOAL forbids
   divergent rationale on identical source.
5. **File a new GHI for the seventh duplicate.** Rejected: GHI #376
   already names the same root cause.

### Plan-before-exploration honesty

Reading order: brief → parent ADR matrix row 10 → OBPI-0.25.0-24 (six-point
Confirm rationale) → sibling OBPI-0.26.0-09 (just-attested pattern) →
verified gzkit surface line counts (`commands/cli_audit.py` 235 L +
`doc_coverage/*.py` 1,065 L = ~1,300 L total). Destination crystallized at
the precedent decision; surface-growth observation strengthened it.

---

## Acceptance

- [x] Discovery items have citable file locations.
- [x] Decision rationale cites OBPI-0.25.0-24 six-point rationale.
- [x] Destination-in-mind disclosure names the conclusion.
- [x] ≥4 rejected alternatives with concrete reasons.
- [x] Verification block reproduces brief-required commands.
- [x] No `src/` or `tests/` paths in Files-Edited list.
