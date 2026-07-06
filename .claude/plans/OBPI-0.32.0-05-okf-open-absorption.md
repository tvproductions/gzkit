# Plan — OBPI-0.32.0-05-okf-open-absorption

**OBPI:** OBPI-0.32.0-05-okf-open-absorption
**Parent ADR:** ADR-0.32.0-gzkit-ontology
**Lane:** Heavy

## Context

The OKF open-absorption path (`src/gzkit/ontology/okf.py`) reads the generated OKF
orientation bundle (`.gzkit/governance/knowledge/`, ADR-0.30.0) and absorbs each
concept doc into the gzkit ontology's corpus subgraph as a `Doc` node whose
`subtype` echoes the source OKF `type` frontmatter value VERBATIM, with `links_to`
edges built from the concept-doc markdown links. NO subset-validator constrains the
`type` set — a closed-set check would breach OKF Boundary Invariants BI-1 (no OKF
frontmatter/link consumed as enforcement) and BI-3 (unknown `type` values are not
errors) and break shipped OKF v0.30.0.

Parent ADR § Decision clause (verbatim, the contract): *"Docs are absorbed via OKF
open-absorption: Doc subtype = OKF type verbatim, NO subset-validator (a closed-set
check would breach OKF BI-1/BI-3), links_to edges kept."*

### Surfaces consumed (read-only; all on Denied Paths)

- `src/gzkit/ontology/model.py` — `OntologyNode` (frozen, `extra="forbid"`, fields
  `node_id/object_type/ownership/plane`; NO `subtype` field — by OBPI-01 design),
  `OntologyEdge`, `LinkType.LINKS_TO`, `ObjectType.DOC`, `Provenance`,
  `OBJECT_TYPE_REGISTRY` (Doc → `harness`/`process`). CONSUMED, never modified.
- `src/gzkit/knowledge/concept_frontmatter.py` — `ConceptFrontmatter` (required
  free-form `type`); the verbatim `type` mapped to `Doc.subtype`.
- OKF bundle shape (`src/gzkit/knowledge/generate.py`): each `<slug>.md` carries YAML
  frontmatter (`type` required) + a body markdown link `Canonical source: [name](ref)`;
  `index.md` (reserved) carries `- [slug](./slug.md)` links; authored nodes
  (e.g. `content-boundary.md`) carry arbitrary inline `[text](url)` links.

### Design decision — `Doc` is subsumption, not a parallel model (hexagonal rule #8)

`subtype` cannot and must not live on `OntologyNode` (frozen, `extra="forbid"`,
Denied Path). The absorption record `Doc` REUSES `OntologyNode(object_type=DOC)` for
node identity/typing and adds only the OKF-specific enrichment (`subtype`, source
path) — one typed representation, not two. The graph-admission question (how/whether
`subtype` reaches an `OntologyGraph` query surface) belongs to OBPI-0.32.0-03 (the
`gz ontology` interface) — OUT OF SCOPE here; this OBPI's declared surface is the
absorption function returning `(Doc nodes, links_to edges)`, per the brief Demo.

## Destination-in-mind (Step 6a disclosure)

Before writing this plan I had already formed the approach: a small `okf.py` with a
`Doc` Pydantic model (frozen, `extra="forbid"`) carrying a composed `OntologyNode` +
`subtype` + source path, a `doc_from_concept(frontmatter, path)` factory, and an
`absorb_okf_bundle(bundle_dir)` reader returning `(list[Doc], list[OntologyEdge])`.

### Rejected alternatives considered during exploration

1. **Add `subtype` to `OntologyNode`** — REJECTED: violates this brief's Denied Paths
   and OBPI-01's `extra="forbid"` boundary; would be a correction owed to OBPI-01, not
   this OBPI's surface. The brief never asks for it.
2. **Flat `Doc` duplicating `node_id/object_type/ownership/plane`** — REJECTED: that is
   the parallel-model smell hexagonal rule #8 forbids. Compose `OntologyNode`, don't
   re-type it.
3. **Admit Doc nodes directly into the corpus `OntologyGraph` here** — REJECTED: graph
   integration is OBPI-03's surface; `corpus.py`/`graph.py` are on Denied Paths. The
   brief Demo returns raw `(nodes, edges)`, not a mutated graph.

## Files

- `src/gzkit/ontology/okf.py` — **CREATE**: the Doc absorption path.
- `tests/test_ontology_okf.py` — **CREATE**: `@covers`-decorated REQ tests.
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/obpis/OBPI-0.32.0-05-okf-open-absorption.md`
  — evidence writeback only.

## Steps (Red-Green-Refactor, one behavior per cycle)

1. **Skeleton (import-clean stub, negative-control enabler).** Define in `okf.py`:
   `Doc` (frozen `BaseModel`, `extra="forbid"`) with a composed `OntologyNode` +
   `subtype: str` + `path: str`; `doc_from_concept(frontmatter: dict, path: str) -> Doc`
   as a no-op-ish stub; `absorb_okf_bundle(bundle_dir: str | Path) -> tuple[list[Doc],
   list[OntologyEdge]]` stub. Purpose: tests import cleanly so each REQ test reds on its
   OWN assertion, not a `ModuleNotFoundError` (false red).

2. **REQ-01 (verbatim subtype) — RED→GREEN.** Test: `doc_from_concept({'type': 'doctrine'},
   'p.md').subtype == 'doctrine'` byte-for-byte; also a mixed-case/spaced `type` carried
   with no normalization. Implement `subtype = frontmatter['type']` verbatim.

3. **REQ-02 (unknown-type tolerance) — RED→GREEN.** Test: an arbitrary never-registered
   `type` (`'never-registered-type'`) yields a `Doc` and raises nothing; `subtype`
   carried verbatim. Implement: no closed-set membership check anywhere.

4. **REQ-03 (links_to edges) — RED→GREEN.** Test: `absorb_okf_bundle` over a temp bundle
   dir whose concept doc carries a known markdown link emits a `links_to`
   `OntologyEdge` (source = Doc node id, target = link ref, `link_type == LINKS_TO`).
   Implement: parse frontmatter `type` + body markdown links (`[text](ref)` via a
   focused regex on the doc body), build one `OntologyEdge(link_type=LINKS_TO,
   provenance=INTENT)` per link. Read bundle files READ-ONLY (REQ-05 item 5). Skip
   reserved `index.md`/`log.md`? — include index links too (they are `links_to` edges);
   pin exact inclusion in the test.

5. **REQ-04 / REQ-05 (structural fences) — proof by absence.** No new validator, no
   `gz validate` scope, no closed-set check exists in the diff. Anchored to parent ADR
   `## Boundary Invariants` #5 (already authored by OBPI-04). Add a test asserting the
   module holds no closed OKF `type` set (e.g. no module-level frozenset/enum of types)
   only if it can be expressed as a real structural assertion; otherwise the fence is
   discharged by the ADR anchor + code review (STRUCTURAL-FENCE channel, not `@covers`).

6. **REQ-06 (support) — Implementation Summary quote.** Write the parent ADR § Decision
   OKF clause verbatim into the brief's `### Implementation Summary` at completion;
   proven by `gz validate --documents` + the `artifact_edited` ledger event.

7. **Refactor** to keep `okf.py` within size limits (functions ≤50 lines), stdlib +
   Pydantic only (no third-party import — networkx stays behind the graph adapter,
   untouched here).

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_ontology_okf -v
```

## Notes / downstream observations (not this OBPI's scope)

- Whether `Doc.subtype` should be queryable from the corpus `OntologyGraph` (i.e.
  survive graph admission) is an OBPI-0.32.0-03 (gz ontology interface) concern — the
  absorption here returns raw `(nodes, edges)`. Noted, not expanded (surgical scope).
- `links_to` edge `provenance`: concept-doc markdown links are authored → `INTENT`
  vein; advisory-ness derives from the `Doc` source endpoint type (auto-honors OKF
  BI-1 per `model.py` Provenance doc). Final value pinned in the REQ-03 test.
