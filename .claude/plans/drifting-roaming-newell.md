# OBPI-0.26.0-02 — references.py Absorption Evaluation

## Context

OBPI-0.26.0-02 under ADR-0.26.0 (governance-library module absorption) requires
evaluating `../airlineops/src/opsdev/lib/references.py` (797 lines) against
gzkit's equivalents and recording an **Absorb** or **Exclude** decision with
concrete rationale. The brief's OBJECTIVE section anticipated a "dedicated
reference tracking for resolving links between ADRs, OBPIs, artifacts, and
governance documents." Reading the module directly contradicts that premise:
the file is an academic-PDF bibliography and APA-citation generator scoped to
`docs/references/` and `docs/airlineops_rosetta_stone.md`, with a hardcoded
airline-operations-research reference list. The subtraction test
(`opsdev − gzkit = pure ops domain`) fails decisively — this is domain content,
not a governance primitive. The OBPI therefore resolves as **Exclude**, with
no absorption, no new module, and no test addition required beyond the
decision artefact.

## Decision

**Exclude.** The opsdev module is airline-research-literature infrastructure,
not a governance cross-reference primitive. Its surface area, file dependencies,
and embedded data are all ops-domain-specific.

## Evidence Anchors (observed, not inferred)

Read in plan mode before authoring this plan:

- `../airlineops/src/opsdev/lib/references.py` lines 1-21 (module docstring),
  44-54 (file constants anchoring `docs/references/`,
  `docs/ANNOTATED_BIBLIOGRAPHY.md`, `docs/REFERENCES.md`,
  `docs/airlineops_rosetta_stone.md`), 56-63 (hardcoded
  `ROSETTA_REFERENCES_LIST` — Belobaba, Bazargan, Abdelghany, Littlewood,
  Talluri & van Ryzin airline OR texts), 617-670 (pypdf-driven
  `build_citation`), 731-760 (`run_apa_citations`), 782-797 (`run_rosetta_refs`)
- gzkit surface check: `docs/references/` (absent), `docs/REFERENCES.md`
  (absent), `docs/ANNOTATED_BIBLIOGRAPHY.md` (absent), no APA/bibliography/
  pypdf code anywhere in `src/gzkit/` — the `rg` matches for "reference" in
  gzkit are unrelated (skill surface audits, ADR governance verifiers,
  manifest references)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
  lines 25-37 (Cross-Reference Matrix row for `references.py` — "Strong absorption candidate unless link semantics are ops-specific")

## Ops-Specific Semantics (the Exclude rationale)

The module fails the subtraction test on every dimension the brief requires:

1. **Filesystem contract is domain-specific.** Module-level constants
   `REF_DIR = docs/references/`, `BIB_MD = docs/ANNOTATED_BIBLIOGRAPHY.md`,
   `REFERENCES_MD = docs/REFERENCES.md`, `ROSETTA_MD =
   docs/airlineops_rosetta_stone.md` all point at an academic-bibliography
   surface that gzkit does not have and has no plan to acquire.
2. **Content is airline-domain data.** `ROSETTA_REFERENCES_LIST`
   (references.py:56-63) hardcodes six airline operations research and
   revenue-management texts. Absorbing this into gzkit would inject airline
   content into a governance toolkit.
3. **Dependency is discipline-specific.** `pypdf` is carried solely to extract
   APA metadata from academic PDFs — a dependency gzkit has no other use for
   and would need to justify on its own merits. gzkit's 40% coverage floor and
   lint rules would both apply to code that serves no gzkit operator.
4. **Functional purpose is literature management, not artefact linkage.**
   `build_citation`, `render_apa_section`, `update_references_apa`,
   `crosslink_bibliography`, and `run_rosetta_refs` operate on academic
   literature, not on ADR → OBPI → artefact graphs. gzkit's governance
   cross-referencing lives in `src/gzkit/traceability.py`, `trust_audits.py`,
   and ADR autolink — none of which overlap with PDF-citation generation.
5. **Naming collision, not behavioral overlap.** The OBPI brief's OBJECTIVE
   anticipated generic governance reference resolution because the filename
   says "references". The module's docstring and implementation both make
   clear the name is short for "academic references / bibliography", not
   "cross-references between governance artifacts". This is a surface-level
   name collision with no behavioral overlap.

## Files to Modify

Single file — the brief itself:

- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-02-references.md`

Populate the existing template sections:

- Flip frontmatter `status: Pending` → `status: Completed`
- Add `decision: Exclude` frontmatter field (if the schema permits; otherwise
  record the decision in body prose and keep frontmatter minimal)
- Append a new `## Comparison` section with: module surface summary, gzkit
  equivalent check, dimension-by-dimension comparison (feature completeness,
  error handling, cross-platform robustness, test coverage) — all grounded in
  the evidence anchors above
- Append a new `## Decision` section with the final **Exclude** decision and
  the five-point rationale
- Populate the three canonical evidence H3s: `### Implementation Summary`,
  `### Key Proof`, `### Closing Argument`
- Populate `## Acceptance Criteria` REQ table evidence: REQ-01 (decision
  recorded), REQ-02 (rationale cites concrete differences), REQ-03 (Absorb path
  N/A — recorded as such), REQ-04 (Exclude rationale present), REQ-05 (Gate 4
  N/A rationale — no operator-visible behavior change)

No source code changes. No test additions. No allowed-path writes under
`src/gzkit/` or `tests/`.

## Gate Resolution

- **Gate 1 (ADR):** already recorded — parent ADR-0.26.0 in place, OBPI brief
  authored under `obpis/`.
- **Gate 2 (TDD):** baseline quality checks only. `uv run gz lint`,
  `uv run gz typecheck`, `uv run gz test --obpi OBPI-0.26.0-02-references`.
  No new tests because no code changes; REQ → `@covers` parity for this OBPI
  has no code-bearing requirement. REQ-03 (Absorb path) is vacuously satisfied.
- **Gate 3 (Docs):** the brief *is* the documentation deliverable. Completion
  writes the decision and rationale into the brief.
- **Gate 4 (BDD):** **N/A** with rationale — `Exclude` outcome with zero
  operator-visible behavior change, zero new CLI verbs, zero generated-surface
  change. Brief records the `N/A` rationale per REQ-05.
- **Gate 5 (Human):** Heavy-lane parent ADR → human attestation required at
  Stage 4 ceremony.

## Scope Boundary — Observed Path Drift (NOT in this patch)

The brief's `## Verification Commands` (lines 107, 110, 119) reference
`briefs/OBPI-0.26.0-02-references.md`, but the actual file lives at
`obpis/OBPI-0.26.0-02-references.md`. This is brief-author drift that will
cause the verification `rg` commands to find nothing. Fixing the brief's own
verification-command paths is in-scope (edits to the brief itself are allowed
and intended). Fixing any *other* OBPI brief in the ADR with the same drift is
**out of scope** — it belongs in a separate GHI if the drift is systematic,
or in the relevant OBPI brief's own Stage 2. This plan repairs only
OBPI-0.26.0-02's three drifted path references as part of completing its
own brief.

## Implementation Steps

1. Edit
   `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-02-references.md`
   to populate `## Comparison`, `## Decision`, `### Implementation Summary`,
   `### Key Proof`, `### Closing Argument`, and the REQ evidence.
2. Fix the three in-brief `briefs/` → `obpis/` path drifts in the
   Verification Commands section (lines 107, 110, 119).
3. Leave frontmatter `status: Pending`; the pipeline's Stage 5
   `gz obpi complete` atomic write flips status + writes completion receipt.

## Verification

- `uv run gz lint` — green (brief-only edit; markdownlint per the brief's
  existing `<!-- markdownlint-disable-file ... -->` marker or the ADR-level
  config)
- `uv run gz typecheck` — green (no code changes)
- `uv run gz test --obpi OBPI-0.26.0-02-references` — green (no code changes;
  no new REQ-derived tests required for Exclude)
- `uv run gz covers OBPI-0.26.0-02-references --json` — parity check; REQs
  1, 2, 4, 5 are brief-content REQs (verified by `rg` patterns in the
  brief's own Verification Commands), REQ-3 vacuously satisfied (Absorb path
  not taken)
- `uv run gz validate --documents --surfaces` — green (brief frontmatter
  + schema intact)
- `rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-02-references.md`
  — returns `Exclude` on the Decision line
- `rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-02-references.md`
  — returns the Gate 4 N/A rationale row

## Out of Scope (for this OBPI)

- Any `src/gzkit/**` change — this is an Exclude, by definition nothing lands
- Any test addition — REQ-03 vacuous; no code to test
- Fixing path drift in sibling briefs (01, 03-12) — separate scope
- Changing the ADR's Cross-Reference Matrix language for `references.py` —
  that row already anticipated `Exclude unless link semantics are ops-specific`
