# Plan: OBPI-0.30.0-02 — OKF Bundle Generator

**OBPI:** OBPI-0.30.0-02-okf-bundle-generator
**Parent ADR:** ADR-0.30.0-okf-documentation-knowledge-structure
**Lane:** Heavy
**Date:** 2026-06-28

## Context

OBPI-0.30.0-01 delivered the `ConceptFrontmatter` Pydantic model and its JSON
schema. This OBPI delivers the **bundle generator** that consumes that model to
emit a small OKF-conformant markdown bundle over the tracer slice into
`.gzkit/governance/knowledge/`:

- Root `index.md` (OKF entry point, lists all concept docs)
- One concept doc per tracer-slice source (state doctrine, trust doctrine,
  agent-contract rationale, active campaign reference) — each with OKF
  frontmatter (`type`, `title`, `description`, `resource`) and a markdown body
  link back to the canonical source (graph edge)
- Directory `index.md` progressive disclosure (root index IS the entry for
  this flat tracer slice)
- Source docs byte-unchanged after generation (read-only)
- Generation idempotent: re-running over unchanged sources yields byte-identical
  bundle (`yaml.dump(sort_keys=True)`, no timestamps in output, deterministic
  slug ordering)

**Tracer slice (fixed):**
- state doctrine — `docs/governance/state-doctrine.md`
- trust doctrine — `docs/governance/trust-doctrine.md`
- agent-contract rationale — `docs/governance/agent-contract-rationale.md`
- active campaign — `docs/governance/build-to-1.0-campaign-2026-06-20.md`

## Files

**Creates:**
- `src/gzkit/knowledge/generate.py` — `generate_bundle()` core function + `if
  __name__ == "__main__":` tracer-slice entry point (runs as
  `python -m gzkit.knowledge.generate`)
- `.gzkit/governance/knowledge/` — generated bundle output root (directory +
  reserved files); generator writes `index.md` + concept docs; MUST NOT clobber
  any pre-existing `content-boundary.md` (OBPI-06's authored node)
- `tests/knowledge/test_bundle_generator.py` — REQ-derived tests

**Modifies:**
- `src/gzkit/knowledge/__init__.py` — export `generate_bundle`, `TRACER_SLICE`,
  `BUNDLE_OUTPUT`

## Steps

### Step 1: Write RED tests (all 4 REQs — before any implementation)

Author `tests/knowledge/test_bundle_generator.py`. All tests must fail with an
assertion error (not import error — create a stub first if needed).

**REQ-0.30.0-02-01** → `test_generator_emits_root_index_and_concept_docs`:
Using a `tempfile.TemporaryDirectory` as `output_dir`, call
`generate_bundle(TRACER_SLICE_FIXTURE, output_dir)`. Assert `index.md` exists;
assert one `.md` file exists per source slug; assert each concept doc's YAML
frontmatter parses via `yaml.safe_load` and `ConceptFrontmatter(**fm)` validates
(non-empty `type`).

**REQ-0.30.0-02-02** → `test_concept_docs_link_to_source_and_have_progressive_disclosure`:
After generation, assert each concept doc has `resource` in its frontmatter (the
graph edge) pointing at the source doc path. Assert the root `index.md` body
contains markdown links to each concept doc slug. Assert `index.md` itself has
OKF frontmatter with `type` set.

**REQ-0.30.0-02-03** → `test_generator_does_not_modify_source_docs`:
For each source in `TRACER_SLICE_FIXTURE`, record `source_path.read_bytes()`.
Call `generate_bundle(...)`. Assert each source doc bytes are unchanged.

**REQ-0.30.0-02-04** → `test_generation_is_idempotent`:
Generate into `output_dir` twice. After each run, collect `{fname: content}` for
every file. Assert the two snapshots are equal (byte-identical content for every
file).

### Step 2: Create stub to reach assertion-level RED

In `src/gzkit/knowledge/generate.py`:
```python
def generate_bundle(sources, output_dir): raise NotImplementedError
```
Run the tests. Each must fail on `NotImplementedError` (assertion-level), not
import error. This is the verified RED.

### Step 3: Implement `generate_bundle`

```python
from __future__ import annotations
from pathlib import Path
import yaml
from gzkit.knowledge.concept_frontmatter import ConceptFrontmatter

SourceEntry = tuple[str, Path]  # (slug, source_path)

def generate_bundle(sources: list[SourceEntry], output_dir: Path | str) -> None:
    """Generate OKF-conformant bundle. Idempotent. Source docs read-only."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    concept_slugs: list[str] = []
    for slug, source_path in sorted(sources, key=lambda s: s[0]):
        fm = ConceptFrontmatter(
            type="doctrine",
            title=slug.replace("-", " ").title(),
            description=f"Knowledge concept: {slug}",
            resource=source_path.as_posix(),
        )
        fm_dict = {k: v for k, v in fm.model_dump().items() if v is not None}
        frontmatter_text = "---\n" + yaml.dump(fm_dict, sort_keys=True,
            default_flow_style=False, allow_unicode=True).rstrip() + "\n---\n"
        body = (
            f"\n# {fm.title}\n\n"
            f"{fm.description}\n\n"
            f"See also: [{source_path.name}]({('../' * (len(out.parts))) + source_path.as_posix()})\n"
        )
        (out / f"{slug}.md").write_text(frontmatter_text + body, encoding="utf-8")
        concept_slugs.append(slug)

    # Root index.md (OKF entry point)
    index_fm = ConceptFrontmatter(type="index", title="Knowledge Index",
        description="OKF bundle index — governance tracer slice")
    index_fm_dict = {k: v for k, v in index_fm.model_dump().items() if v is not None}
    index_front = "---\n" + yaml.dump(index_fm_dict, sort_keys=True,
        default_flow_style=False, allow_unicode=True).rstrip() + "\n---\n"
    links = "\n".join(f"- [{s}](./{s}.md)" for s in concept_slugs)
    (out / "index.md").write_text(
        index_front + f"\n# Knowledge Index\n\n{links}\n", encoding="utf-8"
    )
```

Key idempotency constraints:
- `sorted(sources, key=lambda s: s[0])` — deterministic slug ordering
- `yaml.dump(sort_keys=True)` — deterministic key ordering
- No `datetime.now()` or other non-deterministic values
- No `{k: v for k, v in ... if v is not None}` drops omitted optional fields
  (so the set of keys written is determined by the `ConceptFrontmatter` fields
  we explicitly set, not transient defaults)

### Step 4: Add tracer-slice configuration and `__main__` block

In `src/gzkit/knowledge/generate.py`, add:
```python
TRACER_SLICE: list[SourceEntry] = [
    ("state-doctrine", Path("docs/governance/state-doctrine.md")),
    ("trust-doctrine", Path("docs/governance/trust-doctrine.md")),
    ("agent-contract-rationale", Path("docs/governance/agent-contract-rationale.md")),
    ("active-campaign", Path("docs/governance/build-to-1.0-campaign-2026-06-20.md")),
]
BUNDLE_OUTPUT = Path(".gzkit/governance/knowledge")

if __name__ == "__main__":
    generate_bundle(TRACER_SLICE, BUNDLE_OUTPUT)
    print(f"Bundle generated at {BUNDLE_OUTPUT}")
```

Update `src/gzkit/knowledge/__init__.py` to export `generate_bundle`,
`TRACER_SLICE`, and `BUNDLE_OUTPUT`.

### Step 5: Run tests GREEN (verified assertion pass)

```bash
uv run -m unittest tests.knowledge.test_bundle_generator -v
```
All 4 REQ tests must pass. Record the exact pass count.

### Step 6: Run quality gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run mkdocs build --strict
uv run gz validate --documents
```

### Step 7: Demo verification (idempotency and source-doc integrity)

```bash
uv run python -m gzkit.knowledge.generate
uv run python -m gzkit.knowledge.generate
# Verify byte-identical: second run should show no git diff in bundle dir
git diff -- .gzkit/governance/knowledge/
# Verify source docs untouched
git diff -- docs/governance/state-doctrine.md docs/governance/trust-doctrine.md \
           docs/governance/agent-contract-rationale.md \
           docs/governance/build-to-1.0-campaign-2026-06-20.md
cat .gzkit/governance/knowledge/index.md
cat .gzkit/governance/knowledge/state-doctrine.md
```

### Step 8: Present OBPI Acceptance Ceremony

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.knowledge.test_bundle_generator -v
```

## Notes

- `pyyaml>=6.0.3` is already a runtime dependency — no new dep needed.
- The `.gzkit/governance/knowledge/` directory lives OUTSIDE `docs_dir`; mkdocs
  build is unaffected.
- Generator MUST NOT clobber `content-boundary.md` — that's OBPI-06's authored
  node. The generator only writes `index.md` and the 4 tracer-slice concept docs
  (identified by fixed slugs).
- Tests use `tempfile.TemporaryDirectory` for isolation; the real tracer-slice
  paths are fixtures, not live governance paths, for hermetic test execution.

## Destination-in-mind disclosure (Step 6a)

The approach was formed before writing this plan: a single `generate.py` module
with a pure `generate_bundle(sources, output_dir)` function, a fixed
`TRACER_SLICE` constant, and a `if __name__ == "__main__":` entry point. Tests
use temp dirs and byte-comparison.

**Rejected alternatives:**
1. Jinja2 templates — rejected (no new dependency; f-string markdown suffices).
2. Config file for tracer slice — rejected (fixed, small; hardcoding is simpler
   and avoids a new config surface out of OBPI-02 scope).
3. Timestamps in concept frontmatter — rejected (breaks idempotency REQ-04).
4. `__main__.py` instead of `generate.py` — rejected (Demo shows
   `python -m gzkit.knowledge.generate`; a `generate.py` module satisfies this
   cleanly without ambiguity).
