# Plan: OBPI-0.0.37-23-invariant-tier — Invariant Tier (Verbatim, Never Condense)

**OBPI:** OBPI-0.0.37-23-invariant-tier
**ADR:** ADR-0.0.37-constitutional-invariant-composition (Checklist item #23)
**Lane:** Heavy
**Status:** Ready for implementation

## Context

The corpus model (`CorpusEntry.tier`) already carries `tier: Literal["invariant", "compressible"]`
(OBPI-18, attested-complete). The composer (`src/gzkit/content/composer.py`, OBPI-21) has an
inline invariant-floor check (lines 53-64). This OBPI creates `tier_policy.py` as the
centralized enforcement surface — the single, composer-consumable policy the composer can
import. `composer.py` is in denied paths; this OBPI does NOT re-wire the composer.

**21 ↔ 23 seam:** OBPI-21 landed first with an inline check. OBPI-23 creates the canonical
policy; re-wiring the composer to import from `tier_policy` is a coupled-surface edit that
waits for operator sequencing at brief-reconcile time (see brief § Tracked Defects).

## Files

## Creates These Files

- `src/gzkit/content/tier_policy.py` **CREATE**
- `tests/content/test_tier_policy.py` **CREATE**

**Edits:**
- `docs/governance/agent-control-surface-rendering-substrate.md` — add invariant-tier 0-Kelvin floor subsection
- `data/behave_coverage_waivers.json` — add OBPI-level behave-coverage waiver
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-23-invariant-tier.md` — evidence record

## Steps

### Step 1 — Create `src/gzkit/content/tier_policy.py` (REQ-01, REQ-02, REQ-03)

Implement two functions using stdlib + Pydantic only (no LLM, no network):

```python
def invariant_entries(corpus: Corpus) -> list[CorpusEntry]:
    """Return corpus entries whose tier == 'invariant'."""

def assert_invariant_verbatim(corpus: Corpus, rendered_text: str) -> None:
    """Raise ValueError when any invariant entry's text is absent or altered in rendered_text.
    Returns cleanly when all invariant entries are present verbatim.
    This is the single composer-consumable enforcement surface for the 0-Kelvin floor."""
```

Single module, no class, no LLM dependency. The module docstring names it as the
"single enforcement surface the composer consumes" (REQ-03 centralized-enforcement claim).

### Step 2 — Create `tests/content/test_tier_policy.py` (all REQs)

Four test classes, one per REQ:

**TestInvariantEntries** (REQ-01a):
- `test_returns_only_invariant_entries` — mixed corpus; accessor returns only `tier=="invariant"` rows
- `test_empty_corpus_returns_empty_list` — empty corpus → empty list

**TestAssertInvariantVerbatim** (REQ-01b):
- `test_passes_when_all_invariants_present` — rendered_text includes all invariant entry texts → no raise
- `test_raises_when_invariant_absent` — rendered_text missing one invariant text → `ValueError`
- `test_raises_when_invariant_altered` — rendered_text has rewritten version of invariant → `ValueError`
- `test_passes_with_no_invariant_entries` — corpus with only compressible entries → no raise

**TestInvariantSurvivesLeanestSetpoint** (REQ-02):
- `test_prime_directive_survives_lite` — corpus has PRIME DIRECTIVE as `tier:invariant`;
  rendition at leanest setpoint (`lite`) is constructed to include it; policy passes
- `test_do_it_right_survives_lite` — same pattern for DO IT RIGHT
- `test_never_pytest_survives_lite` — same pattern for NEVER PYTEST
- `test_all_three_survive_lite` — all three named invariants in one corpus; rendition includes
  all three verbatim; policy passes (0-Kelvin floor holds at most aggressive compression)

**TestCentralizedEnforcement** (REQ-03):
- `test_candidate_dropping_invariant_is_rejected` — candidate rendition that drops an invariant-
  tier entry is rejected by `assert_invariant_verbatim`; proves centralized enforcement (the
  composer's compression path calls this exact function, not a duplicated inline check)
- `test_candidate_combining_invariant_is_rejected` — candidate that combines two invariant entries
  into paraphrase is rejected
- `test_candidate_rewriting_invariant_is_rejected` — candidate that rewrites invariant prose is
  rejected

Every test decorated with `@covers("REQ-0.0.37-23-0N")`. Imports: `unittest`, `tempfile` (for
fixture corpus serialization if needed), Pydantic corpus model, `tier_policy`. No pytest.

### Step 3 — Edit substrate doc (REQ-04)

In `docs/governance/agent-control-surface-rendering-substrate.md`, add a narrow subsection
documenting the invariant-tier 0-Kelvin floor as a first-class guarantee. Placement:
after the existing "Binding claim" section. Content: one short paragraph naming the 0-Kelvin
floor, the `tier: invariant` mechanism, and `tier_policy.assert_invariant_verbatim` as the
enforcement surface. Does NOT overlap with OBPI-27's broader mechanism refresh.

### Step 4 — Edit behave coverage waiver (REQ-04 support)

In `data/behave_coverage_waivers.json`, add an OBPI-level entry:
```json
"OBPI-0.0.37-23-invariant-tier": {
  "reason": "No Gherkin-observable CLI surface — this OBPI ships no new verb; REQ-01/02/03 are unit-proven engine behavior; REQ-04 is SUPPORT (doc)."
}
```

### Step 5 — Verify

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.content.test_tier_policy -v
uv run gz covers OBPI-0.0.37-23-invariant-tier --json
uv run gz validate --documents
uv run mkdocs build --strict
uv run gz validate --brief-reconcile
```

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.content.test_tier_policy -v
uv run gz covers OBPI-0.0.37-23-invariant-tier --json
uv run gz validate --documents
uv run mkdocs build --strict
```

## Notes

- `tier_policy.py` is deterministic (stdlib + Pydantic); no LLM or network dependency
- `composer.py` is in denied paths — the 21↔23 wiring seam is not resolved here
- Named invariant texts (PRIME DIRECTIVE, DO IT RIGHT, NEVER PYTEST) in REQ-02 tests are
  the actual canonical text from AGENTS.md; tests reference the contract, not a string literal
- The `req_atomic:` exemption is declared in the brief's frontmatter for all 4 REQs
