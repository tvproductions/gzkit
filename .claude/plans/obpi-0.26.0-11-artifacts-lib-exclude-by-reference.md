# Plan: OBPI-0.26.0-11 — Artifacts Library (Exclude-by-reference)

## Context

- **OBPI:** OBPI-0.26.0-11-artifacts-lib (Heavy lane, parent ADR-0.26.0)
- **Source under review:** `../airlineops/src/opsdev/lib/artifacts.py` (232 L)
- **gzkit equivalent (per brief Source Material):** Partial in `src/gzkit/sync.py`
  (369 L). The actual gzkit artifact-management surface is `src/gzkit/registry.py`
  (220 L) plus governance-artifact discovery utilities in `src/gzkit/sync.py`
  (`scan_existing_artifacts`, `parse_artifact_metadata`).
- **Canonical precedent:** OBPI-0.25.0-23-artifact-management-pattern
  (status `attested_completed`, attested 2026-04-11, **Decision: Exclude**).
  Eight-dimension comparison rationale already attested at ADR-0.25.0 closeout
  with the subtraction test as the decisive signal.
- **Pairing waiver:** Brief frontmatter already declares
  `paired_with: OBPI-0.25.0-23-artifact-management-pattern` (populated by
  cdd8e396 under GHI #376). The `gz validate --absorption-duplicates` audit
  (added under 2a21ebdc) consumes this waiver to suppress duplicate-OBPI
  fail-close on this brief.
- **Pattern lineage (this is the eighth structural instance):**

  | OBPI-0.26.0-NN | OBPI-0.25.0-NN paired | Decision | Lineage |
  |----------------|------------------------|----------|---------|
  | -04 adr-governance | -20 | Confirm-by-reference | landed |
  | -05 ledger-schema | -29 | Exclude-by-reference | landed 2026-05-01 |
  | -06 drift-detection | -26 | Absorb-by-reference | landed 2026-05-01 |
  | -07 adr-traceability | -22 | Confirm-by-reference | landed 2026-05-01 |
  | -08 validation-receipt | -31 | Confirm-by-reference | landed 2026-05-01 |
  | -09 adr-audit-ledger | -19 | Confirm-by-reference | landed 2026-05-01 |
  | -10 cli-audit-lib | -24 | Confirm-by-reference | landed 2026-05-02 |
  | **-11 artifacts-lib** | **-23** | **Exclude-by-reference** (this brief) | **in-flight** |

## Objective

Author the OBPI-0.26.0-11 brief body and evidence sections to record an
**Exclude-by-reference** verdict on `lib/artifacts.py`, anchored on
OBPI-0.25.0-23's attested Exclude rationale plus an updated surface inspection
showing the post-precedent state of `src/gzkit/registry.py` and the artifact-
related portion of `src/gzkit/sync.py`. Zero source/test edits — Exclude
decisions preserve the precedent attestation.

## Files

### Authored / modified

- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md`
  — fill brief body: `Lane`, refreshed `Discovery Checklist`, explicit
  `Denied Paths`, normalized `Source Material` body-level observation,
  `Comparison` table, `Decision` (Exclude) with rationale and duplicate-OBPI
  tracking table, `Implementation Summary`, `Key Proof`, `Closing Argument`,
  `Human Attestation`. Heading conventions: H3 for evidence sections per
  `.claude/rules/brief-heading-conventions.md`.

### Read-only references

- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-23-artifact-management-pattern.md`
  — canonical precedent and rationale spine
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-10-cli-audit-lib.md`
  — most-recent sibling pattern (Confirm-by-reference); follow heading layout
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md`
  — most-recent sibling Exclude-by-reference pattern (verdict-shape match)
- `../airlineops/src/opsdev/lib/artifacts.py` (232 L) — opsdev source
- `src/gzkit/registry.py` (220 L) — primary gzkit artifact-management surface
- `src/gzkit/sync.py` (369 L) — governance artifact discovery (`scan_existing_artifacts`,
  `parse_artifact_metadata`); brief Source Material's named comparator
- ADR-0.26.0 parent file — confirm WBS row 11 wording

### Scope guard

No edits to `src/gzkit/`, `tests/`, `pyproject.toml`, `../airlineops/`,
`config/**`, or any CI/lockfile surface. Brief-only patch. Allowed Paths
remain those declared in the brief frontmatter.

## Steps

1. **Cache governance reads.** Re-read the precedent (OBPI-0.25.0-23) and
   the two most-recent sibling shapes (OBPI-0.26.0-05 Exclude-by-reference,
   OBPI-0.26.0-10 most-recent sibling). Confirm parent-ADR WBS row 11
   wording and frontmatter `paired_with` waiver.

2. **Refresh surface inventory.** Run targeted reads on
   `src/gzkit/registry.py` and the artifact-related portion of
   `src/gzkit/sync.py` (focus on `scan_existing_artifacts`,
   `parse_artifact_metadata`, content-type registry surface). Capture
   line counts and any post-OBPI-0.25.0-23 changes that reinforce or
   weaken the precedent's Exclude verdict. opsdev source is unchanged
   (still 232 L) — confirm via `wc -l`.

3. **Author brief body sections** in this order:
   - **Lane** — Heavy (parent inheritance + doctrine choice carries
     attestation rigor).
   - **Discovery Checklist** — Governance reads cached, prerequisite paths
     existence-checked (opsdev 232 L; gzkit registry.py 220 L; gzkit
     sync.py 369 L), parent-ADR row 11 reviewed, duplicate-OBPI surface
     check pointing at GHI #376 + paired_with waiver.
   - **Denied Paths** — outside ADR-0.26.0 directory, `../airlineops/`,
     `pyproject.toml`, CI/lockfiles, `src/gzkit/` (no code under Exclude).
   - **Comparison** — body-level Source Material observation
     (parent-ADR matrix row 11 says "Partial in `src/gzkit/sync.py`";
     actual surface is `registry.py` + `sync.py` discovery primitives —
     intentionally not amending matrix); eight-dimension comparison table
     re-anchored from OBPI-0.25.0-23 with refreshed line anchors;
     subtraction-test paragraph naming the airlineops-specific
     `artifacts/` directory convention, hardcoded preserved files
     (`live_ingest_report.json`, `attestations/`), and convention
     conflicts (`@dataclass`, `shutil.rmtree(ignore_errors=True)`).
   - **Decision** — `**Exclude** (by reference to OBPI-0.25.0-23-artifact-
     management-pattern, attested 2026-04-11)`. Rationale section with
     ≥6 numbered points: (1) zero functional overlap (canonical precedent),
     (2) physical-file-management vs governance-content-type-metadata —
     fundamentally different problems, (3) airlineops-specific
     `artifacts/` directory convention with hardcoded preserved files,
     (4) convention violations: `@dataclass` (gzkit Pydantic policy) +
     `shutil.rmtree(ignore_errors=True)` (gzkit cross-platform policy),
     (5) gzkit registry.py + sync.py post-precedent state preserves the
     Exclude verdict — name observed line counts and any structural
     change since 2026-04-11, (6) subtraction test re-stated. Add
     **Brief-scaffold defect** sub-section noting the parent-ADR matrix
     row 11 wording is stale (the actual surface is broader than
     `sync.py` alone) — eighth structural instance of the same defect
     class across ADR-0.26.0 briefs (after 04/05/06/07/08/09/10) —
     tracked under GHI #376, mechanically suppressed by paired_with
     waiver. Add **Tracking the duplicate-evaluation signal** table
     (eight rows: 0.25.0-NN ↔ 0.26.0-NN pairs, decision, status). Add
     **Gate 4 (BDD): N/A** sub-section explicitly.
   - **Quality Gates** — flip Gate 1, Gate 2, Gate 3, Gate 4 to `[x]`
     with one-line evidence per gate; leave Gate 5 unchecked (recorded
     during Stage 4).
   - **Acceptance Criteria** — flip all five REQ checkboxes to `[x]`
     with `[doc]` prefix and concrete evidence pointer per row.
   - **Verification** — append two OBPI-specific verification commands:
     `rg -n '^decision: Exclude' …`, `uv run gz covers OBPI-0.26.0-11
     --json`. Keep existing Verification Commands section heading
     (rename to `## Verification` per OBPI-0.26.0-10 sibling shape).
   - **Completion Checklist (Heavy)** — flip Gates 1-4 to `[x]`, leave
     Gate 5 unchecked.
   - **Implementation Summary (H3)** — substantive bullets covering:
     decision (Exclude-by-reference + precedent), modules compared
     (opsdev 232 L vs gzkit registry.py 220 L + sync.py governance
     discovery), eight-dimension capability gap, post-precedent surface
     state, brief-scaffold-defect surfacing (eighth instance),
     duplicate-OBPI tracking under GHI #376 + paired_with waiver, no
     code changes (Exclude preserves precedent attestation).
   - **Key Proof (H3)** — concrete commands + observed/expected output
     pinning the verdict: `rg -n '^decision: Exclude' …`,
     `rg -c 'OBPI-0.25.0-23' …` (≥10 expected), `wc -l ../airlineops/
     src/opsdev/lib/artifacts.py src/gzkit/registry.py src/gzkit/sync.py`,
     `uv run gz covers OBPI-0.26.0-11 --json` (parity gate),
     `uv run gz validate --absorption-duplicates` (waiver check),
     `uv run gz obpi validate --authored …` (frontmatter shape).
     Append a one-line ARB-receipt-citation note (placeholder for
     Stage 3 receipts).
   - **Closing Argument (H3)** — 2-3 paragraph synthesis: opsdev
     module's two capabilities (regex source-scanning + airline-
     specific directory cleanup); gzkit registry.py + sync.py governance
     discovery surface; subtraction test fails completely; convention
     violations preclude clean absorption even if scope overlap existed;
     eighth structural instance of duplicate-OBPI scaffold defect;
     mechanically suppressed by paired_with waiver and `gz validate
     --absorption-duplicates` audit.

4. **Set frontmatter `decision: Exclude` and `status: Pending`**
   (status flips at Stage 5 via `gz obpi complete`). Confirm
   `paired_with: OBPI-0.25.0-23-artifact-management-pattern` already
   present (it is — populated under cdd8e396).

## Verification

Stage 3 baseline checks (ARB-wrapped per AGENTS.md § Attestation):

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

Brief-scoped verification:

```bash
# Frontmatter and body verdict pin
rg -n '^decision: Exclude|\*\*Exclude\*\*' \
  docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md

# Precedent citation density
rg -c 'OBPI-0.25.0-23' \
  docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md

# Source surface confirmation
test -f ../airlineops/src/opsdev/lib/artifacts.py
test -f src/gzkit/registry.py
test -f src/gzkit/sync.py
wc -l ../airlineops/src/opsdev/lib/artifacts.py src/gzkit/registry.py src/gzkit/sync.py

# Decision + Gate 4 N/A presence
rg -n 'Absorb|Confirm|Exclude' \
  docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md
rg -n 'Gate 4|N/A|behavioral proof' \
  docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md

# REQ→@covers parity gate
uv run gz covers OBPI-0.26.0-11-artifacts-lib --json

# Brief frontmatter + heading shape
uv run gz obpi validate --authored \
  docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-11-artifacts-lib.md

# Heading conventions
uv run gz validate --brief-headings

# Duplicate-OBPI guard (waiver consumption)
uv run gz validate --absorption-duplicates

# BDD only when operator-visible behavior changes — Exclude has none, recorded N/A
# (not run; brief records N/A rationale)
```

Expected:
- `decision: Exclude` pinned in frontmatter and body.
- ≥10 OBPI-0.25.0-23 citations across body, Decision rationale, Implementation
  Summary, Closing Argument.
- opsdev source 232 L (unchanged); gzkit registry.py 220 L; sync.py 369 L.
- `gz covers` parity-gate vacuous pass (`uncovered_reqs: 0` on `[doc]` REQ
  pattern via `_synthesize_doc_proof_linkage`).
- `gz obpi validate --authored` returns "OBPI Validation Passed".
- `gz validate --brief-headings` exits 0.
- `gz validate --absorption-duplicates` exits 0 (paired_with waiver consumed).

## Notes

- **Why not native plan mode first?** Per gz-obpi-pipeline § The Plan-Mode
  Gate / GHI #288, native plan mode pins plans to harness-named random
  paths under `~/.claude/plans/`; the canonical-name file in
  `.claude/plans/` is what the project-local plan-audit hook expects, and
  the plan-audit-gate can deadlock if no canonical-name plan exists yet.
  Authoring this canonical-name file first is the documented sidestep.
- **Confidence in direction:** ≥95%. The eight-instance precedent chain
  (OBPI-0.26.0-04 through -10) is mechanical at this point; the only
  decision points specific to -11 are (a) is the precedent verdict
  Absorb/Confirm/Exclude (precedent says **Exclude**), and (b) does the
  post-precedent gzkit surface state still preserve that verdict
  (registry.py and sync.py are unchanged in their artifact-management
  semantics — Exclude holds *a fortiori* if anything). The Stage 1→2
  Confidence Gate threshold (90%) is comfortably cleared; no
  `gz justify` walkthrough required.
- **Gate 4 BDD:** N/A — Exclude verdict introduces zero operator-visible
  behavior change, zero new CLI verbs, zero generated-surface change.
  Brief records N/A explicitly per parent-ADR lane definition.
- **Stage 5 attestation routing:** Heavy lane requires brief-level human
  attestation (matrix: feature/heavy/absent → Required). `--attestor-present`
  is the primary path (pipeline marker satisfies co-presence proxy);
  PTY+`ATTEST` is the fallback per Stage 5 Step 2.
- **No GHI to file.** GHI #376 already covers the duplicate-OBPI class
  and is closed by the mechanical guard (`gz validate
  --absorption-duplicates`). The eighth structural instance is recorded
  in the Decision rationale but does not need a new GHI; it is a
  documentation-of-pattern, not a new defect surface.
