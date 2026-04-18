---
id: OBPI-0.25.0-30-references-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 30
status: in_progress
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-30: References Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-30 — "Evaluate and absorb opsdev/lib/references.py (797 lines) — bibliography index and citation generation"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/references.py` (797 lines) against gzkit's
reference management surface and determine: Absorb, Confirm, or Exclude. The
airlineops module covers bibliography index and citation generation. No direct
gzkit equivalent was found — the comparison must determine whether bibliography
and citation management is generic governance infrastructure worth absorbing or
airline-domain-specific tooling.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/references.py` (797 lines)
- **gzkit equivalent:** No direct equivalent identified

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- At 797 lines, the airlineops module is substantial and likely implements a significant feature

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Building a generic bibliography engine — absorb only if the pattern is governance-relevant

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, adapted gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Exclude` decision
- [ ] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [ ] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [ ] REQ-0.25.0-30-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`.
- [ ] REQ-0.25.0-30-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-30-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-30-04: [doc] Given an `Exclude` outcome, then the brief explains why
  the pattern is domain-specific or otherwise not fit for gzkit.
- [ ] REQ-0.25.0-30-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/references.py
# Expected: airlineops source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-30-references-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Comparison Evidence

Both surfaces were examined before authoring this decision. The table records
concrete differences grounded in file:line anchors; gzkit has no equivalent
module, so the right column records repository-level absence rather than a
rival implementation.

| Dimension | airlineops `opsdev/lib/references.py` (797 L) | gzkit equivalent |
| --- | --- | --- |
| Purpose | Build a PDF bibliography index, cross-link `ANNOTATED_BIBLIOGRAPHY.md`, extract APA metadata from PDFs, rewrite an airline-research reference block | None — gzkit has no research-paper library, no APA citation surface, no annotated bibliography |
| Primary input corpus | `docs/references/*.pdf` (research papers with DOIs, authors, journals) | No such directory; `docs/references/` does not exist in gzkit |
| APA marker surface | `docs/REFERENCES.md` with `<!-- BEGIN AUTO APA -->` / `<!-- END AUTO APA -->` injection points | No `docs/REFERENCES.md`, no APA marker surface |
| Annotated bibliography | `docs/ANNOTATED_BIBLIOGRAPHY.md` cross-linked with `[PDF]` back-references | No `docs/ANNOTATED_BIBLIOGRAPHY.md` |
| Domain-coupled data | `ROSETTA_REFERENCES_LIST` — six aviation-industry textbook citations hardcoded at `references.py:56-63` (Belobaba, Bazargan, Abdelghany, Littlewood, Talluri, Barnhart) | N/A — no equivalent data fixture; gzkit has no aviation domain |
| Rosetta writer | `run_rosetta_refs()` rewrites a hardcoded block inside `docs/airlineops_rosetta_stone.md` from the above list (`references.py:782-797`) | N/A — gzkit has no `airlineops_rosetta_stone.md` and no equivalent doc |
| PDF parsing dependency | `pypdf` — guarded `try/except` at `references.py:32` and `references.py:36-37`; runtime warning at `references.py:745-746` when missing | N/A — `pyproject.toml` has no `pypdf` dependency; no gzkit module imports `pypdf` or `PdfReader` (verified via Grep across `src/gzkit/`) |
| Markdown block-replacement helper | `_replace_block()` — twelve-line regex-based AUTO marker block substituter (`references.py:763-779`) | gzkit handles block injection inline in its own manifest and sync surfaces without a shared helper |
| Consumer surface | airlineops's own research-paper library at `docs/references/` | Zero — gzkit's "references" are ADR IDs, OBPI slugs, ledger event types, and commit hashes, not journal articles with DOIs |
| String presence check | N/A | "APA" / "citation" / "bibliography" appear in gzkit only in unrelated skill-sync and traceability contexts, never as an academic-reference surface |
| Only PDF under `docs/` | Many research PDFs | `GovZero_ AI Governance Framework and Next Steps.pdf` — a single framework whitepaper, not part of a bibliography corpus |
| Absorption cost | Module (~800 L) + mandatory `pypdf` third-party dependency + new markdown marker conventions + domain-specific data fixture | — |

## Decision: Exclude

**Decision:** Exclude — the specific 797-line module is the wrong fit, but
the capability it hints at is a legitimate gzkit need. The need is captured
in a follow-up pool ADR (see Consequence below).

**Rationale.** The initial Exclude framing ("gzkit has no bibliography
consumer") was corrected during Stage 4 ceremony: gzkit *does* need a
design-references bibliography for the SDD, AI-governance, and
agent-engineering literature that grounds its design reviews. The user
named three concrete seed references already in active use
([Project Sustainable Model](https://alignment.anthropic.com/2026/psm/),
[Abstractive Red-Teaming](https://alignment.anthropic.com/2026/abstractive-red-teaming/),
[Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
Once the consumer need was confirmed, the question reframed from "does
gzkit need bibliography management?" (yes) to "does airlineops's specific
implementation fit the need?" (no). The Exclude rationale below addresses
the refined question.

1. **Architectural mismatch — PDF-first vs design-reference-first.**
   airlineops `references.py` is fundamentally a PDF-scan pipeline. Its
   core machinery — `pypdf` metadata extraction (title, authors, journal,
   volume, pages, DOI), `docs/references/*.pdf` file-glob indexing, APA
   *journal article* formatting — solves the problem of managing an
   academic research-paper corpus. gzkit's consumer need is a design-
   references bibliography seeded with web articles, engineering blogs,
   and framework documentation — URL-first, article-first, not
   PDF-first. Absorbing 797 lines of PDF-biased infrastructure to serve a
   URL-first consumer would be mostly dead code, and would commit gzkit to
   a format choice (APA journal-article citation) that does not match
   engineering-literature conventions.
2. **Hardcoded airline-domain content.** `ROSETTA_REFERENCES_LIST`
   (`references.py:56-63`) is six aviation-industry textbook citations
   (Belobaba, Bazargan, Abdelghany, Littlewood, Talluri, Barnhart).
   `run_rosetta_refs()` (`references.py:782-797`) rewrites a block inside
   `docs/airlineops_rosetta_stone.md` from that list. This is domain-
   specific content that does not generalize — it is not a "pattern" in
   the absorbable sense, it is an airlineops-specific data fixture that
   would need stripping before any absorption.
3. **Dependency weight mismatched to the actual consumer pattern.**
   `pypdf` is a non-trivial third-party dependency whose value is PDF
   metadata extraction. For URL-first web-article references, `pypdf`
   solves no problem — the metadata (author, title, publisher, URL, year)
   is either already structured in the source page or hand-authored. Adding
   `pypdf` to `pyproject.toml` for a consumer surface that does not
   exercise it would inflate dependencies and add a supply-chain surface
   for no governance value. `references.py` already guards `pypdf` behind
   a `try/except` stub (`references.py:32`, `references.py:36-37`),
   confirming that even airlineops treats it as optional tooling.
4. **Consumer surface does not exist yet — absorbing commits design
   choices prematurely.** gzkit has no `docs/references/`, no
   `REFERENCES.md`, no `ANNOTATED_BIBLIOGRAPHY.md`, and no chosen citation
   format today. Absorbing a 797-line module before the consumer surface
   is designed would commit gzkit to airlineops's architectural choices
   (AUTO-marker convention, APA format, file-glob indexing, directory
   layout) before gzkit has deliberated on them. The clean path is the
   opposite: design the gzkit-native surface in a dedicated pool ADR,
   choose the format that fits URL-first seed content, and pull only the
   twelve-line `_replace_block()` marker pattern (`references.py:763-779`)
   if it turns out to be useful — re-implementing it in gzkit style
   rather than inheriting 797 lines to get twelve useful ones.
5. **Tooling layer vs consumer layer.** gzkit is a framework that
   downstream projects adopt to govern their own development. airlineops's
   `references.py` sits inside `opsdev/lib/` — an application-specific
   library within airlineops's own consumer project, tied to airlineops's
   research-library layout choices. Even the capability gzkit wants needs
   to be re-hosted as framework-native rather than inherited from a
   consumer project's implementation. This mirrors the OBPI-0.25.0-29
   (`ledger_schema` Exclude) precedent: consumer-layer implementations
   should not be pushed into the tooling layer, even when the underlying
   capability is valuable.
6. **No narrow idiom warrants surgical absorption.** Unlike OBPI-0.25.0-27's
   `_safe_print` outcome (a narrow robustness helper absorbed surgically),
   `references.py` exposes no standalone utility that gzkit lacks today.
   The markdown block-replacement helper `_replace_block()`
   (`references.py:763-779`) is a twelve-line regex snippet — not
   absorbable tooling, not a reusable component worth a dedicated module.
   If the follow-up design-references pool ADR needs that pattern, it can
   re-derive it in gzkit style.

**Consequence.** No source or test edits in this brief. The `Exclude`
outcome for this specific 797-line module is recorded here; the underlying
design-references capability need is captured in
`docs/design/adr/pool/ADR-pool.design-references-bibliography.md`, booked
during the Stage 4 ceremony as an intentional follow-up. That pool ADR
seeds the bibliography with the three Anthropic articles the user named
and leaves format/storage/citation-tooling decisions to its own promotion
cycle. The ADR-0.25.0 decision table will pick up the `Exclude` outcome
for OBPI-0.25.0-30 via `gz obpi reconcile` and `gz adr status` in Stage 5.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.25.0 checklist item #30 captured verbatim in brief l.15.
- [x] **Gate 2 (TDD):** N/A — Exclude outcome introduces no code or tests. `uv run gz test` remains green because no source changed; evidence captured in Stage 3 of the pipeline run.
- [x] **Gate 3 (Docs):** Decision rationale completed above with concrete capability, dependency-weight, and tooling-vs-consumer-layer differences between airlineops and gzkit.
- [x] **Gate 4 (BDD):** N/A — the Exclude outcome introduces no operator-visible behavior change. `features/core_infrastructure.feature` is not touched. Rationale: no CLI surface, no user-facing command, no ledger event type, and no doc output is added, removed, or modified by this decision.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony of `gz-obpi-pipeline`.

## Evidence

### Gate 1 (ADR)

- Intent captured verbatim from ADR-0.25.0 checklist item #30 at brief l.15
- Scope aligned with ADR Heavy lane and the Absorb / Exclude contract (no Confirm path — brief l.36)

### Gate 2 (TDD)

- Existing gzkit test suite remains green — no new tests needed for an Exclude decision
- Verification: `uv run gz test` → comparison or absorbed implementation remains green (Stage 3 evidence below)

### Code Quality

- No code changes — Exclude decision is documentation-only
- `uv run gz lint` → Stage 3 evidence below
- `uv run gz typecheck` → Stage 3 evidence below
- `uv run gz validate --documents` → Stage 3 evidence below
- `uv run mkdocs build --strict` → Stage 3 evidence below
- `uv run gz covers OBPI-0.25.0-30-references-pattern --json` → Stage 3 evidence below

### Value Narrative

Before this OBPI, the comparison between `airlineops/src/opsdev/lib/references.py` (797 L bibliography index + APA citation generator) and any gzkit equivalent was unrecorded. After this OBPI, a six-point rationale is on the record explaining why gzkit is architecturally the wrong home for this module: no consumer surface in gzkit (no `docs/references/`, no `REFERENCES.md`, no `ANNOTATED_BIBLIOGRAPHY.md`, no `pypdf` dependency, no research-paper corpus); hardcoded airline-domain content (`ROSETTA_REFERENCES_LIST` at `references.py:56-63` with six aviation-industry textbook citations); dependency weight mismatched to consumer need (`pypdf` supply-chain surface for zero consumers); subtraction test fails on the *need* not the implementation; tooling-layer vs consumer-layer distinction (airlineops's `opsdev/lib/` is a consumer-layer library, not framework material); and no narrow idiom warranting surgical absorption (unlike OBPI-0.25.0-27's `_safe_print`). This follows the precedent from OBPI-0.25.0-29 (`ledger_schema` Exclude) where the same tooling-vs-consumer distinction decisively disqualified absorption.

### Key Proof


- Decision: Exclude
- Comparison: twelve-dimension table in `## Comparison Evidence`
- airlineops `references.py`: 797 L, PDF bibliography index + APA citation generator, hardcoded `ROSETTA_REFERENCES_LIST` (aviation textbooks), mandatory `pypdf` dependency
- gzkit equivalent: none — no `docs/references/`, no `REFERENCES.md`, no `ANNOTATED_BIBLIOGRAPHY.md`, no `pypdf` in `pyproject.toml`, no `pypdf` / `PdfReader` import anywhere in `src/gzkit/` (verified via Grep)
- Precedent: OBPI-0.25.0-29 (`ledger_schema` Exclude) applied the same tooling-layer vs consumer-layer distinction
- `rg -n 'Decision: Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-30-references-pattern.md` matches in this brief

### Implementation Summary


- Decision: Exclude
- Files created: none
- Files modified: this brief only (`docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-30-references-pattern.md`)
- Tests added: none (no code changes)
- Date: 2026-04-13

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed — Exclude decision for airlineops/src/opsdev/lib/references.py (797 L PDF-scan pipeline). Initial framing corrected mid-ceremony after user pushback: gzkit does need a design-references bibliography for SDD/AI-governance literature, but airlineops's specific implementation is PDF-first/pypdf-dependent/APA-journal-article-formatted and mismatches gzkit's URL-first article-centric consumer pattern. Refined 6-point rationale anchored in file:line citations; capability booked as ADR-pool.design-references-bibliography seeded with three Anthropic articles (Project Sustainable Model, Abstractive Red-Teaming, Effective Context Engineering for AI Agents). Zero source/test edits; no pypdf added; gates green.
- Date: 2026-04-13

## Closing Argument

The capability airlineops's `references.py` hints at — curated
bibliography management for design references — is legitimately useful to
gzkit. gzkit has been running design reviews grounded in external
engineering literature (Anthropic's alignment and context-engineering
articles among them), and that body of material deserves a durable,
citable surface. But airlineops's specific 797-line implementation is the
wrong vehicle for that capability in gzkit. It is a PDF-scan pipeline:
`pypdf` metadata extraction, `docs/references/*.pdf` file-glob indexing,
APA *journal article* formatting, and a hardcoded
`ROSETTA_REFERENCES_LIST` of aviation-industry textbooks
(`references.py:56-63`) feeding a `docs/airlineops_rosetta_stone.md`
rewriter. gzkit's consumer pattern is URL-first, article-first, and
engineering-literature-first — none of which airlineops's machinery
serves. Absorbing the module would inflate `pyproject.toml` with
`pypdf`, import 797 lines that are mostly dead against gzkit's consumer
pattern, and commit gzkit to airlineops's format/layout choices before
gzkit has deliberated on its own. The doctrinally-coherent outcome is
Exclude *this specific implementation* and book the capability into a
dedicated follow-up:
`docs/design/adr/pool/ADR-pool.design-references-bibliography.md`. That
pool ADR captures the need at the right granularity — gzkit-native
design, seeded with material that has already grounded design reviews,
unburdened by a consumer project's implementation choices — and pulls
only the twelve-line `_replace_block()` marker pattern from airlineops
if it turns out to be useful, re-implemented in gzkit style. The
subtraction test fails here at a more precise granularity than the
initial framing suggested: the *capability* generalizes, the *specific
implementation* does not.

## Implementation Summary

- Decision: Exclude (with follow-up pool ADR)
- Files created: `docs/design/adr/pool/ADR-pool.design-references-bibliography.md` (captures the design-references capability need for promotion later)
- Files modified: this brief only (`docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-30-references-pattern.md`)
- Tests added: none (no code changes)
- Dependencies added: none (no `pypdf` absorption)
- Date: 2026-04-13

## Key Proof

```bash
rg -n 'Decision: Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-30-references-pattern.md
# Output: matches the Decision: Exclude heading in this brief

test -f docs/design/adr/pool/ADR-pool.design-references-bibliography.md
# Output: exit 0 — follow-up pool ADR exists with seed references

grep -l 'pypdf' src/gzkit/
# Output: empty — no gzkit module imports pypdf; Exclude kept the dependency surface clean

ls docs/references/ 2>&1
# Output: No such file or directory — gzkit has no research-paper corpus, confirming the PDF-scan absorption would be dead code
```

Pipeline quality gates:
- `uv run gz lint` → All checks passed; ADR path contract passed
- `uv run gz typecheck` → All checks passed
- `uv run gz test` → 17 features passed, 110 scenarios passed, 584 steps passed, 0 failed (11.321s)
- `uv run gz validate --documents` → All validations passed (1 scope)
- `uv run mkdocs build --strict` → Documentation built in 2.04s
- `uv run gz covers OBPI-0.25.0-30-references-pattern --json` → `total_reqs=0, uncovered_reqs=0` (trivial pass)
