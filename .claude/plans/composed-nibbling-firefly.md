# Plan: OBPI-0.25.0-30 — References Pattern (Exclude)

## Context

OBPI-0.25.0-30 is a pattern-absorption evaluation inside ADR-0.25.0 (Core Infrastructure Pattern Absorption). The brief asks whether `airlineops/src/opsdev/lib/references.py` (797 lines) — an academic bibliography index and APA citation generator — should be absorbed into gzkit, confirmed as already present, or excluded.

The brief explicitly names the decision axes: subtraction test ("if it's not airline-specific, it belongs in gzkit"), feature completeness, error handling, cross-platform robustness, and test coverage. The brief also states: "No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path."

Evidence gathered in Stage 1 exploration:
- **airlineops module** (`airlineops/src/opsdev/lib/references.py`, 797 L) does four things:
  1. Scans `docs/references/*.pdf` and builds `index.md` with rename-manifest annotations.
  2. Cross-links existing `ANNOTATED_BIBLIOGRAPHY.md` headings with `[PDF]` links.
  3. Extracts structured metadata from PDFs (title, authors, year, journal, volume, pages, DOI) via `pypdf`, renders APA-formatted markdown, and injects it between `<!-- BEGIN AUTO APA -->` / `<!-- END AUTO APA -->` markers in `docs/REFERENCES.md`.
  4. Rewrites a hardcoded aviation-research reference block in `docs/airlineops_rosetta_stone.md` from a built-in `ROSETTA_REFERENCES_LIST` containing six airline-industry textbooks (Belobaba, Bazargan, Abdelghany, Littlewood, Talluri, Barnhart).
- **gzkit surface** has no equivalent and no consumer:
  - `/Users/jeff/Documents/Code/gzkit/docs/references/` does not exist.
  - `/Users/jeff/Documents/Code/gzkit/docs/REFERENCES.md` does not exist.
  - `docs/ANNOTATED_BIBLIOGRAPHY.md` does not exist.
  - `pyproject.toml` has no `pypdf` dependency (confirmed via Grep).
  - No gzkit module imports `pypdf` or `PdfReader` (confirmed via Grep across `src/gzkit/`).
  - The string "APA" / "citation" / "bibliography" appears in gzkit only in unrelated skill-sync and traceability contexts, never as an academic-reference surface.
  - The only PDF under `docs/` is a single framework whitepaper (`GovZero_ AI Governance Framework and Next Steps.pdf`), not part of a research bibliography.

## Decision: Exclude

The subtraction test fails for this module. The *code* is not airline-specific, but the *need it addresses* — academic PDF bibliography and APA citation generation for a research-paper library — is specific to research-heavy domains like airlineops. gzkit is a governance toolkit: its "references" are ADR IDs, OBPI slugs, ledger event types, and commit hashes, not journal articles with DOIs. Absorbing `references.py` would introduce a ~800-line module plus a mandatory `pypdf` dependency for functionality no gzkit consumer exercises, and would bake airline-industry textbook titles into a framework meant to govern arbitrary downstream projects.

This Exclude decision follows the precedent established in OBPI-0.25.0-29 (ledger_schema Exclude): the tooling-layer-vs-consumer-layer distinction applies here too. `references.py` is a consumer-layer feature tightly coupled to airlineops's decision to maintain an annotated research library. A governance toolkit should not mandate that distinction on its adopters.

## Rationale (concrete dimensions)

1. **No consumer surface in gzkit.** The airlineops module's entire input corpus is `docs/references/*.pdf`. gzkit has no such directory, no `ANNOTATED_BIBLIOGRAPHY.md`, no `REFERENCES.md`, and no research-paper corpus. Every function in the module is a no-op against gzkit's filesystem. Absorbing dead code violates the "don't add features beyond what the task requires" discipline in CLAUDE.md.

2. **Hardcoded airline-domain content.** `ROSETTA_REFERENCES_LIST` (references.py:56-63) is six aviation-industry textbook citations (Belobaba, Bazargan, Abdelghany, Littlewood, Talluri, Barnhart). `run_rosetta_refs()` rewrites a block inside `docs/airlineops_rosetta_stone.md` (references.py:782-797). This is domain-specific content that does not generalize — it is not a "pattern" in the absorbable sense, it is an airlineops-specific data fixture.

3. **Dependency weight mismatched to consumer need.** `pypdf` is a non-trivial third-party dependency (PDF parsing, text extraction, metadata decoding). Adding it to gzkit for a feature zero downstream projects use would inflate `pyproject.toml`, slow `uv sync`, and add a supply-chain surface for no governance value. References.py already guards `pypdf` behind a try/except stub (references.py:31-34), confirming that even airlineops treats it as optional tooling.

4. **Subtraction test fails on the need, not the implementation.** The `ASSUMPTIONS` section of the brief names the test: "if it's not airline-specific, it belongs in gzkit." The subtraction axis here is not the Python code (citation parsing is generic) but the *governance need* it satisfies. Governance toolkits do not need academic-bibliography management. Research projects do. airlineops is the correct home for this module; gzkit is not.

5. **Tooling-vs-consumer-layer boundary.** gzkit is a framework that downstream projects adopt to govern their own development. Its surface must serve arbitrary consumers — governance events, ADR lifecycle, attestation, ledger. airlineops's `references.py` sits inside `opsdev/lib/` — an application-specific library within airlineops's own consumer project. Moving a consumer-layer module into the framework inverts the dependency: gzkit would ship framework features that are not framework concerns, and airlineops would grow a runtime dependency on its own absorbed code. The architectural direction is wrong.

6. **No narrow-idiom carve-out warrants surgical absorption.** Unlike OBPI-0.25.0-27's `_safe_print` (a narrow robustness helper absorbed surgically), `references.py` has no standalone utility that gzkit lacks. The Markdown block-replacement helper `_replace_block()` (references.py:763-779) is a twelve-line regex snippet — not absorbable tooling, not a reusable component worth a dedicated module. gzkit already handles markdown block injection in its own sync and manifest surfaces without a shared helper.

## Files modified

| File | Change |
|---|---|
| `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-30-references-pattern.md` | Add `## Comparison Evidence` table, `## Decision: Exclude` rationale section, update `## Completion Checklist (Heavy)` checkboxes (Gate 1/2/3/4 checked with rationale, Gate 5 pending human attestation), add `## Evidence` section with concrete Stage 1-3 evidence, replace `## Closing Argument` placeholder with the final decision summary. |

No source file edits. No test edits. No feature file edits. This is a documentation-only Exclude decision, mirroring the pattern set by OBPI-0.25.0-29 (ledger-schema Exclude) and OBPI-0.25.0-27 (safe_print surgical Absorb — opposite outcome, same ceremony).

## Gate rationale

- **Gate 1 (ADR):** Intent recorded in brief lines 18-24; scope aligned with ADR Heavy lane and the Absorb/Exclude contract.
- **Gate 2 (TDD):** N/A — the Exclude outcome introduces no code or tests. `uv run gz test` remains green because no source changed.
- **Gate 3 (Docs):** Decision rationale completed in the brief with concrete capability, dependency-weight, and tooling-vs-consumer-layer differences.
- **Gate 4 (BDD):** N/A — no operator-visible behavior change. No CLI command is added, removed, or modified. No ledger event type changes. `features/core_infrastructure.feature` is not touched. Rationale recorded inline in the brief.
- **Gate 5 (Human):** Human attestation recorded during Stage 4 ceremony of `gz-obpi-pipeline`.

## Verification (Stage 3 commands)

```bash
# Source-existence sanity — brief's own verification commands
test -f ../airlineops/src/opsdev/lib/references.py
# Expected: exit 0, airlineops source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-30-references-pattern.md
# Expected: at least one match for "Exclude" in the completed brief

# Baseline quality gates (Heavy lane)
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run mkdocs build --strict

# REQ parity gate (#113)
uv run gz covers OBPI-0.25.0-30-references-pattern --json
# Expected: summary.uncovered_reqs == 0
# Note: Exclude-decision REQs are satisfied by documentation evidence, not test code.
# If the parity gate reports uncovered REQs, add @covers references to the brief-evidence section
# or to a sentinel test, matching the OBPI-0.25.0-29 precedent.
```

Behavioral proof (`uv run -m behave features/core_infrastructure.feature`) is **not** required — the brief's own verification commands explicitly scope it to "only required when operator-visible behavior changes," and the Exclude outcome changes no operator surface.

## REQ coverage (for Stage 4 ceremony table)

| REQ | Mechanism | Coverage path | Result |
|---|---|---|---|
| REQ-0.25.0-30-01 | Brief records one final decision: `Exclude` | `OBPI-0.25.0-30-references-pattern.md` § Decision: Exclude | Pass |
| REQ-0.25.0-30-02 | Rationale cites concrete capability / dependency / layer differences | Same file § Rationale (6 numbered points, each grounded in file:line anchors) | Pass |
| REQ-0.25.0-30-03 | N/A — not an Absorb outcome | — | N/A |
| REQ-0.25.0-30-04 | Exclude rationale explains domain-specificity | Same file § Decision: Exclude + Rationale points 1, 2, 4, 5 | Pass |
| REQ-0.25.0-30-05 | Gate 4 N/A with rationale recorded | Same file § Completion Checklist → Gate 4 | Pass |

Stage 3 Phase 1b will run `gz covers` to verify `@covers` parity. If the parity gate flags REQ-30-* as uncovered, the fix is to add `@covers REQ-0.25.0-30-NN` anchors into the brief's Evidence section (the canonical covers scanner picks up both decorator and docstring forms per #120); this is the same remediation pattern used in prior Exclude briefs in this ADR.

## Execution steps (for Stage 2)

1. Edit the OBPI brief `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-30-references-pattern.md`:
   - Add `## Comparison Evidence` section with a dimension table (airlineops vs gzkit: purpose, inputs, dependencies, domain coupling, consumer surface, absorption cost).
   - Add `## Decision: Exclude` section with the six-point rationale above, grounded in file:line anchors into both repositories.
   - Update `## Completion Checklist (Heavy)` to check Gates 1-4 with inline rationale and leave Gate 5 unchecked.
   - Add `## Evidence` section with concrete Stage 1-3 evidence (brief intent capture, existing test suite remains green, docs validation remains green, mkdocs strict-build remains green, `@covers` parity as required).
   - Replace `## Closing Argument` placeholder with the final decision summary (one paragraph: decision + key reason + consequence).
2. Run baseline Heavy-lane verification (see Verification section).
3. Run REQ parity gate; if uncovered, anchor `@covers` references inside the brief's Evidence section and re-verify.
4. Proceed to Stage 4 ceremony presentation with the mandatory template.

## Risks and mitigations

- **Risk:** `gz covers` parity gate fails because Exclude outcomes produce no test-anchored `@covers` references. **Mitigation:** place `@covers REQ-0.25.0-30-NN` anchors directly in the brief's Evidence section (the scanner is doc-aware per #120), mirroring OBPI-0.25.0-29's approach.
- **Risk:** `mkdocs build --strict` flags a broken cross-ref in the updated brief. **Mitigation:** use only local anchors and existing repo-relative paths; cite `references.py` via plain code spans, not links.
- **Risk:** Reviewer challenges the Exclude decision on the grounds that `pypdf` and APA formatting *could* be useful for ADR narrative generation. **Mitigation:** the rationale already addresses this in point 1 (no consumer surface) and point 3 (dependency weight mismatched to use); Stage 4 ceremony surfaces the evidence for human adjudication.
