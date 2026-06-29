# Plan: OBPI-0.30.0-06-content-boundary-doctrine

## Context

OBPI-0.30.0-06 under ADR-0.30.0 (OKF documentation-knowledge structure). Authors
the `.gzkit/` vs `docs/` content-boundary doctrine doc and wires runbook pointers.
Heavy lane. Authoring-only — no production code change, no content migration.

The doctrine doc homes under `.gzkit/governance/knowledge/` (the OKF bundle
created by OBPI-0.30.0-02) with OKF `type: doctrine` frontmatter. The migration
IS declared, NOT performed.

## Files

- CREATE: `.gzkit/governance/knowledge/content-boundary.md` — the doctrine doc
- MODIFY: `docs/user/runbook.md` — add pointer to content-boundary doctrine
- MODIFY: `docs/governance/governance_runbook.md` — add pointer to content-boundary doctrine
- CREATE: `tests/knowledge/test_content_boundary_doctrine.py` — REQ-derived unittest cases

## Steps

### Step 1: Write failing tests (RED)

Author `tests/knowledge/test_content_boundary_doctrine.py` with four REQ-derived
test cases:

- `TestContentBoundaryDoctrine.test_doctrine_file_exists` — REQ-0.30.0-06-01:
  asserts `.gzkit/governance/knowledge/content-boundary.md` exists.
- `TestContentBoundaryDoctrine.test_doctrine_states_boundary` — REQ-0.30.0-06-01:
  reads the file and asserts it states the three boundary elements (gzkit-core under
  `.gzkit/`; `docs/` = adopter space; OKF bundles domain-named).
- `TestContentBoundaryDoctrine.test_doctrine_declares_phased_migration` — REQ-0.30.0-06-02:
  asserts the doc declares the docs/→`.gzkit/` relocation as phased AND states migration
  not performed under ADR-0.30.0.
- `TestContentBoundaryDoctrine.test_no_docs_canon_relocated` — REQ-0.30.0-06-03:
  asserts a representative set of docs/ core-canon files (state-doctrine.md,
  trust-doctrine.md, agent-contract-rationale.md) still exists at their original paths.

Run: `uv run -m unittest tests.knowledge.test_content_boundary_doctrine -v`
Expected: FAIL on test_doctrine_file_exists (file missing).

### Step 2: Author the doctrine doc (GREEN)

Create `.gzkit/governance/knowledge/content-boundary.md` with:
- OKF YAML frontmatter: `type: doctrine`, `title`, `description`, `tags`, `resource`
- H1 heading: the boundary statement
- Three boundary rules stated explicitly
- Phased migration declared with explicit "migration NOT performed under ADR-0.30.0"
- Linked to the parent ADR

Run tests: REQ-01, REQ-02, REQ-03 should pass.

### Step 3: Add runbook pointers (SUPPORT REQ-04)

Add a brief pointer sentence to:
- `docs/user/runbook.md` — in the appropriate section, pointing to
  `.gzkit/governance/knowledge/content-boundary.md`
- `docs/governance/governance_runbook.md` — same pointer

No `gz <verb>` references in the runbook text (pointer is a path reference, not a
CLI incantation — no cli-alignment issue).

Run: `uv run gz validate --documents && uv run gz validate --cli-alignment`
Expected: exit 0.

### Step 4: Verify

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run -m unittest tests.knowledge.test_content_boundary_doctrine -v
uv run gz validate --documents
uv run gz validate --cli-alignment
uv run mkdocs build --strict
```

## Verification

See Step 4 above. All commands must exit 0.

## Notes

- OBPI-0.30.0-02 already created `.gzkit/governance/knowledge/`; content-boundary.md
  is a new concept node in the existing bundle.
- The `type: doctrine` frontmatter makes the doc OKF-conformant alongside the bundle's
  existing concept docs.
- REQ-04 is SUPPORT kind: the structural proof is `gz validate --documents` + `gz
  validate --cli-alignment` passing; the ledger proof (`artifact_edited` events) is
  emitted by `gz obpi complete` at Stage 5.
- No `req_atomic:` exemption needed — each REQ has distinct labor (one test class per REQ).
