# Plan: OBPI-0.30.0-05-progressive-disclosure-path-docs

**OBPI:** OBPI-0.30.0-05-progressive-disclosure-path-docs
**Parent ADR:** ADR-0.30.0-okf-documentation-knowledge-structure
**Lane:** Heavy

## Context

The generated OKF bundle exists at `.gzkit/governance/knowledge/` with four tracer-slice
concept docs (active-campaign, agent-contract-rationale, state-doctrine, trust-doctrine),
each carrying `resource:` frontmatter pointing to canonical source docs. The bundle root
`index.md` links to all four concept docs. The operator runbook already has a brief
`gz knowledge generate/refresh` entry but no documented progressive-disclosure
navigation path and no control-surface pointer naming the bundle root as the entry point.

## Objective

Close the tracer bullet: wire ONE documented progressive-disclosure path (control surface
→ bundle root → concept → canonical source) by authoring three doc-layer artifacts and
one test that mechanically verifies the link graph is reachable end-to-end.

## Files

**Create:**
- `docs/user/concepts/okf-navigation.md` — the control surface; names
  `.gzkit/governance/knowledge/index.md` as entry point; describes 3-step nav path;
  orientation-only framing
- `tests/knowledge/test_progressive_disclosure_path.py` — walks link graph from
  bundle root to each concept doc and its canonical source; also verifies the concept
  doc pointer

**Modify:**
- `docs/user/runbook.md` — add progressive-disclosure section pointing agents to
  the bundle root and concept doc
- `docs/governance/governance_runbook.md` — expand OKF section with nav path and
  maintainer guidance

## Steps

### Step 1: TDD RED — write reachability test (do NOT implement yet)

Write `tests/knowledge/test_progressive_disclosure_path.py`:
- `TestBundleRootReachability.test_all_tracer_slice_concepts_reachable` — parses
  `index.md` links, reads each concept doc, asserts all 4 tracer-slice names found
- `TestConceptDocPointer.test_concept_doc_names_bundle_root` — reads
  `docs/user/concepts/okf-navigation.md` (does NOT yet exist), asserts it contains
  the string `.gzkit/governance/knowledge/index.md`

Run tests and confirm:
- `test_all_tracer_slice_concepts_reachable` PASSES (bundle already exists)
- `test_concept_doc_names_bundle_root` FAILS with `FileNotFoundError` (concept doc
  does not exist yet) — verified red

REQ coverage: `@covers REQ-0.30.0-05-01` on the reachability test, `@covers
REQ-0.30.0-05-03` on the pointer test.

### Step 2: GREEN — create concept doc control surface

Author `docs/user/concepts/okf-navigation.md`:
- H1: "OKF Knowledge Navigation"
- Names `.gzkit/governance/knowledge/index.md` as the navigation entry point
  (satisfies REQ-0.30.0-05-03 and the pointer test)
- Describes the 3-step progressive-disclosure path:
  1. Start at `.gzkit/governance/knowledge/index.md` (bundle root)
  2. Follow a concept link → read the concept doc (type, description, resource)
  3. Follow the `resource:` link to the canonical source doc
- MUST frame the bundle as ORIENTATION ONLY: "The OKF bundle is an orientation aid.
  Cite the canonical source doc (the `resource:` target), not the OKF concept doc,
  as evidence."
- Short, clear, no invented CLI verbs

Run pointer test → GREEN.

### Step 3: Update operator runbook

In `docs/user/runbook.md`, update the `gz knowledge generate/refresh` paragraph to
add a "Navigating the OKF bundle" subsection:
- Points agents to `.gzkit/governance/knowledge/index.md` as the bundle root
- References `docs/user/concepts/okf-navigation.md` for the full path description
- Orientation-only framing (do not cite OKF content as authority)

No new `gz <verb>` strings beyond already-registered ones.

### Step 4: Update governance runbook

In `docs/governance/governance_runbook.md`, expand the `gz knowledge` entry:
- Add a note that the generated bundle at `.gzkit/governance/knowledge/` follows the
  progressive-disclosure path documented in `docs/user/concepts/okf-navigation.md`
- Orientation-only framing
- Reference `uv run gz knowledge refresh` as the maintenance command

### Step 5: Verify full suite

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run gz validate --cli-alignment
uv run mkdocs build --strict
```

## Verification

```bash
uv run gz validate --documents
uv run gz validate --cli-alignment
uv run gz lint
uv run -m unittest tests.knowledge.test_progressive_disclosure_path -v
uv run mkdocs build --strict
```

## Notes

- The concept doc is intentionally minimal — it documents the path, it does not
  restate the bundle content. Per Boundary Invariant 1, the concept doc MUST NOT
  present OKF frontmatter as evidence.
- The runbook and governance runbook already have `gz knowledge generate/refresh`
  mentions; this plan adds the navigation pointer, not a duplicate CLI entry.
- Scope collisions with sibling ADR docs/user/runbook.md and
  docs/governance/governance_runbook.md are advisory (those OBPIs are Completed);
  this OBPI makes additive, non-conflicting edits.
