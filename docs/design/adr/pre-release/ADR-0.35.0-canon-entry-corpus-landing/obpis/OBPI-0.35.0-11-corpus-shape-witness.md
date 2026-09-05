---
id: OBPI-0.35.0-11-corpus-shape-witness
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 11
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/governance/trust_audits/agents_md_map_conformance.py
  - src/gzkit/governance/trust_audits/_qc_negative_controls.py
  - tests/governance/test_agents_md_map_conformance.py
  - tests/governance/test_agents_md_map_doctrine_application.py
  - features/agents_md_map_conformance.feature
  - features/steps/agents_md_map_conformance_steps.py
  - docs/user/manpages/validate.md
  - docs/governance/governance_runbook.md
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-11-corpus-shape-witness.md
reqs:
  - REQ-0.35.0-11-01
  - REQ-0.35.0-11-02
  - REQ-0.35.0-11-03
  - REQ-0.35.0-11-04
  - REQ-0.35.0-11-05
  - REQ-0.35.0-11-06
verification:
  - uv run -m unittest tests.governance.test_agents_md_map_conformance tests.governance.test_agents_md_map_doctrine_application
  - uv run -m behave features/agents_md_map_conformance.feature
  - uv run gz validate --agents-md-map-conformance
  - uv run gz validate --documents --req-kind-discipline
  - uv run gz lint
  - uv run gz typecheck
  - uv run mkdocs build --strict
---

# OBPI-0.35.0-11-corpus-shape-witness: Corpus Shape Witness

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #11 — "Corpus shape witness over Layer 1 -- `agents-md-map-conformance` shape criteria evaluated against the corpus effective view for the surface, not against `src/gzkit/templates/agents.md`; the template keeps its own adopter-bootstrap check, and the Layer-1 corpus gains the shape witness it has never had (GHI #922)"

## Objective

Extend the existing map-conformance scope to check each effective AGENTS.md corpus entry
for the existing paragraph, prohibited-title and link criteria, with entry-addressed
diagnostics. Retain independent template bootstrap checks and the advisory rendered budget.
A clean template must no longer hide invalid source entries.

**Dependencies:** OBPI-01's effective fold is required and attested. This source check
does not wait for 04/05/06/07: it checks entry text before rendition generation and makes
no claim about assembled section shape or lineage coverage. Rule-family migration is 12;
root render order is 13. The broader original GHI #922 is not wholly discharged by this item.

## Lane

**Heavy** — changes what the existing public validator rejects. Gates 1–5 apply.

## Allowed Paths

- `src/gzkit/governance/trust_audits/agents_md_map_conformance.py`
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py`
- `tests/governance/test_agents_md_map_conformance.py`
- `tests/governance/test_agents_md_map_doctrine_application.py`
- `features/agents_md_map_conformance.feature`
- `features/steps/agents_md_map_conformance_steps.py` — **CREATE**; adjacent feature steps establish the convention.
- `docs/user/manpages/validate.md`
- `docs/governance/governance_runbook.md`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-11-corpus-shape-witness.md`

The negative-control registry gains a corpus-specific violation fixture; its existing
template control remains. No new CLI scope or parser flag is needed.

## Denied Paths

- `src/gzkit/content/models/corpus.py`, `src/gzkit/content/corpus_store.py`, `src/gzkit/content/vendors.py` — read-only fold, store and routing contracts.
- `.gzkit/corpus/AGENTS.md.jsonl`, `AGENTS.md`, `src/gzkit/templates/agents.md` — subjects, never rewritten to pass the audit.
- `data/vendor-manifest.json`, `data/instructions_files_budget.json` — no cap or budget change.
- Paths not listed in Allowed Paths; new dependencies, CI files and lockfiles.

## Requirements (FAIL-CLOSED)

1. ALWAYS run the existing shape criteria over effective entry text, regardless of tier,
   without substituting the template or a committed rendition for that source.
2. ALWAYS preserve each entry boundary and identify corpus path, entry id, logical surface
   and offending entry-local line. Never concatenate entries so unrelated paragraphs
   merge or a fence in one entry suppresses findings in another.
3. ALWAYS use the shipped fold. Pure tombstones contribute no text; superseded and retired
   content is excluded according to the existing algebra. No second liveness algorithm.
4. ALWAYS resolve relative links against the logical AGENTS.md location, then the existing
   project-root fallback. The JSONL storage directory is never a link base.
5. ALWAYS distinguish absent-store bootstrap from a malformed or unreadable present store.
   The former retains the template audit; the latter reports a hard source failure.
6. NEVER change the existing shape criteria or turn budget/bullet advisories into errors.
   The template arm stays independently effective; retained off-route renditions and
   candidate files cannot affect the source verdict.
7. ALWAYS register a live corpus negative control with clean template/rendered fixtures,
   so the registered claim proves the new source arm actually ran.

> STOP-on-BLOCKERS: report missing prerequisites before implementation; do not weaken the source check.

## Discovery Checklist

**Parent ADR (read first):**

- [ ] Read § Decision SOURCE-OF-TRUTH DIRECTION and quote it in Implementation Summary.
- [ ] Read § Intent, then checklist item 11 and the 2026-09-01 scope amendment.
- [ ] Read parent: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`.

> STOP: if the parent Decision grounding cannot be quoted, re-read it before implementation.

**Governance:**

- [ ] Read AGENTS.md and `.gzkit/rules/agents-md-map-doctrine.md`; preserve advisory budget posture.
- [ ] Read `.gzkit/rules/tests.md` for semantic tests and proof channels.

**Prerequisites:**

- [ ] Verify completed OBPI-01 and the available `effective_corpus` API.
- [ ] Confirm the existing public scope is wired through validate_cmd.py and parser_maintenance.py.
- [ ] Read the corpus and classify current source findings; no fixed entry count is a completion criterion.

**Existing Code:**

- [ ] Read the whole `agents_md_map_conformance.py` audit and its paragraph/title/link helpers.
- [ ] Read `corpus_store.load_corpus` absent-store behavior and effective-fold tests.
- [ ] Read `_qc_negative_controls.py` template fixture; it cannot witness this new corpus arm.
- [ ] Read the two named governance test modules and the existing map-conformance feature.

## Quality Gates

### Gate 1: ADR

- [ ] Parent checklist and this brief remain in 1:1 correspondence.

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Each BEHAVIOR REQ has a semantic failing test before implementation and passing evidence afterward.
- [ ] Negative controls exercise the production command path, not a substituted helper.
- [ ] Full tests pass with canonical ARB receipts before completion.

### Gate 3: Docs

- [ ] User documentation carries observed output and strict MkDocs build passes.

### Gate 4: BDD

- [ ] The named feature scenarios prove the delivered behavior through the CLI.

### Gate 5: Human

- [ ] Present concrete evidence and obtain explicit human completion attestation.
- [ ] Record the operator's words verbatim, with evidence enrichment, before completion.

## Verification

```bash
uv run -m unittest tests.governance.test_agents_md_map_conformance tests.governance.test_agents_md_map_doctrine_application
uv run -m behave features/agents_md_map_conformance.feature
uv run gz validate --agents-md-map-conformance
uv run gz validate --documents --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
```

## Demo

Run against the actual corpus after implementation; the unit/BDD fixtures supply the
known-bad and repaired counterparts without mutating repository canon.

```bash
uv run gz validate --agents-md-map-conformance
uv run gz validate --agents-md-map-conformance --json
uv run -m behave features/agents_md_map_conformance.feature
```

## Acceptance Criteria

- [ ] REQ-0.35.0-11-01 [BEHAVIOR]: Given clean template and rendered files but an effective corpus entry violating an existing paragraph or prohibited-title criterion, the public scope exits 3 with corpus path, entry id and entry-local line; a conforming counterpart exits 0. The registered corpus-specific QC negative control invokes this production scope and proves that the corpus violation is detected with otherwise clean fixtures.
- [ ] REQ-0.35.0-11-02 [BEHAVIOR]: Given the same violating text first live, then retired or superseded, only its effective live state contributes a finding; retiring a pure retirement tombstone restores the finding according to the shipped fold.
- [ ] REQ-0.35.0-11-03 [BEHAVIOR]: Given an entry with a relative link and file anchor, valid logical-surface-relative targets pass and missing files or invalid anchors fail with entry attribution; placing a decoy target under .gzkit/corpus cannot make an invalid logical link pass.
- [ ] REQ-0.35.0-11-04 [BEHAVIOR]: Given no corpus store, the independent template audit still detects a template violation; a malformed or unreadable present corpus produces a hard corpus finding rather than a template fallback, and corpus violations are detected even without a template.
- [ ] REQ-0.35.0-11-05 [BEHAVIOR]: Given unchanged corpus entries, adding retained off-route renditions or candidates leaves source findings unchanged; template violations remain independently detectable while budget and binding-bullet advisories alone do not make the scope fail.
- [ ] REQ-0.35.0-11-06 [SUPPORT]: Validator documentation describes the effective-corpus arm, retained template arm, entry diagnostics and logical link base, witnessed by an artifact_edited event citing docs/user/manpages/validate.md and by gz validate --documents.

## Tracked Defects

- GHI #922 — this brief implements the parent-ratified corpus-source slice; the issue's wider nested-budget questions are not silently declared solved.

## Completion Checklist

- [ ] Gate 1 intent and scope recorded.
- [ ] Gate 2 semantic tests and negative controls verified.
- [ ] Lint, type checks, docs and BDD verified.
- [ ] Value narrative and key proof show the delivered capability.
- [ ] Human attestation recorded through the governed completion command.

## Evidence

### Gate 1 (ADR)

Authored on 2026-09-05 at the operator's request to rectify the thirteen-item decomposition.
This is authoring authorization, not an implementation draw or completion attestation.

### Gate 2 (TDD — Red-Green-Refactor)

No implementation test result claimed at authoring.

### Code Quality

Execution receipts will be recorded when this OBPI is implemented.

### Gate 3 (Docs)

Implementation documentation and observed command output remain to be delivered.

### Gate 4 (BDD)

No implementation scenario result claimed at authoring.

### Gate 5 (Human)

No completion attestation recorded.

### Value Narrative

The Objective states the missing capability. Record the measured before/after at implementation.

### Key Proof

Run the Demo after implementation and preserve its observed output with negative-control evidence.

### Implementation Summary

Parent Decision grounding, verbatim:

> SOURCE-OF-TRUTH DIRECTION (operator-ruled this session, stated explicitly rather than inherited): the corpus is the SOURCE that AGENTS.md is generated from.

The specific deliverable is the linked checklist item quoted above. No source implementation
was performed while authoring this brief.

## Human Attestation

- Attestor: pending
- Attestation: pending explicit human completion attestation
- Date: pending
