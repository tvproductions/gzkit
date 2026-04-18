# Plan — OBPI-0.0.16-05: Canonical Status-Vocabulary Mapping

## Context

ADR-0.0.16 landed the frontmatter-ledger coherence guard (OBPI-01). OBPI-01's
dogfood run surfaces 315 drift entries across the repo; inspection shows ten
distinct frontmatter `status:` terms in circulation (`Draft`, `Proposed`,
`Pending`, `Validated`, `Completed`, `Accepted`, `archived`,
`Pending-Attestation`, `Pool`, `Promoted`, `Superseded`). Downstream consumers
— OBPI-02 (gate error output) and OBPI-03 (chore canonicalization rewrite) —
both need a *single* authoritative mapping from observed-frontmatter term to
ledger-state-machine canonical term. OBPI-05 exists so those two can run in
parallel after OBPI-01 landed, instead of serializing through a bundled
OBPI-02.

This OBPI is **data-only**. It exports the typed constant and documents the
mapping. No consumers are updated. No frontmatter is mutated. No chore is
registered. No gate is wired.

## Canonical terms (from ADR-0.0.9 / `src/gzkit/ledger.py`)

- **OBPI runtime states** (`OBPI_RUNTIME_STATES` at `src/gzkit/ledger.py:23-31`):
  `pending`, `in_progress`, `completed`, `attested_completed`, `validated`,
  `drift`, `withdrawn`.
- **ADR lifecycle states** (`Ledger.derive_adr_semantics` at
  `src/gzkit/ledger.py:536-559`): `Pending`, `Validated`, `Completed`,
  `Abandoned` (capitalized at the ADR layer; compared case-insensitively by
  the validator at `src/gzkit/commands/validate_frontmatter.py:106`).

The mapping normalizes canonical targets to **lowercase** so a single vocabulary
covers both layers. Consumers that need display casing can title-case at the
presentation boundary. The union of canonical targets is:
`{pending, in_progress, completed, attested_completed, validated, drift,
withdrawn, abandoned}`.

## Proposed mapping

| Frontmatter term     | Canonical ledger term | Rationale |
|----------------------|-----------------------|-----------|
| Draft                | pending               | Authoring state — no ledger events yet |
| Proposed             | pending               | ADR authored but not validated |
| Pool                 | pending               | Backlog item — no lifecycle events |
| Promoted             | pending               | Just promoted from pool — no events yet |
| Pending              | pending               | Direct mirror |
| Accepted             | validated             | Historical term — Gate 1 validated |
| Validated            | validated             | Direct mirror |
| Pending-Attestation  | completed             | Work done, awaiting human attestation |
| Completed            | completed            | Direct mirror (may lag `attested_completed` post-ceremony) |
| Superseded           | abandoned             | Replaced by later decision |
| archived             | abandoned             | Retired — no longer active |

All eleven observed terms covered; every canonical target ∈ the canonical
union above, satisfying REQ-05-03.

## Files to create / modify

| # | Path | Action |
|---|------|--------|
| 1 | `src/gzkit/governance/__init__.py` | **Create** (empty or minimal) — package marker for the new sub-package. Needed so `from gzkit.governance.status_vocab import ...` resolves. |
| 2 | `src/gzkit/governance/status_vocab.py` | **Create** — exports `STATUS_VOCAB_MAPPING`, `CANONICAL_LEDGER_TERMS`, and helper `canonicalize_status(term: str) -> str \| None`. |
| 3 | `tests/governance/__init__.py` | **Create** (if not present) — test package marker. |
| 4 | `tests/governance/test_status_vocab.py` | **Create** — unit tests covering REQ-01..05 and REQ-08. |
| 5 | `docs/governance/state-doctrine.md` | **Modify** — append "Canonical status vocabulary (ADR-0.0.16 addendum)" section. |

Note: `src/gzkit/governance/__init__.py` and `tests/governance/__init__.py`
are implicit scope expansion beyond the brief's literal Allowed Paths —
they are the package-marker minimum needed to make the brief-allowed
`status_vocab.py` and `test_status_vocab.py` imports resolve. This is the
"Complete all work fully — including adjacent files" invariant, not scope
creep.

## Module contract (`src/gzkit/governance/status_vocab.py`)

```python
"""Canonical status-vocabulary mapping (ADR-0.0.16 OBPI-05).

Frontmatter status terms observed in circulation → ledger state-machine
canonical terms (from ADR-0.0.9 / gzkit.ledger). Consumers (OBPI-02 gate
output, OBPI-03 chore canonicalization) import STATUS_VOCAB_MAPPING; they
do NOT inline duplicates.
"""

from types import MappingProxyType

# Union of canonical ledger terms (lowercase, from OBPI_RUNTIME_STATES and
# derive_adr_semantics lifecycle_status).
CANONICAL_LEDGER_TERMS: frozenset[str] = frozenset({
    "pending",
    "in_progress",
    "completed",
    "attested_completed",
    "validated",
    "drift",
    "withdrawn",
    "abandoned",
})

_RAW_MAPPING: dict[str, str] = {
    "Draft": "pending",
    "Proposed": "pending",
    "Pool": "pending",
    "Promoted": "pending",
    "Pending": "pending",
    "Accepted": "validated",
    "Validated": "validated",
    "Pending-Attestation": "completed",
    "Completed": "completed",
    "Superseded": "abandoned",
    "archived": "abandoned",
}

# Immutable at runtime. Consumers iterate but never mutate.
STATUS_VOCAB_MAPPING: MappingProxyType[str, str] = MappingProxyType(_RAW_MAPPING)


def canonicalize_status(term: str) -> str | None:
    """Return the canonical ledger term for a frontmatter status term.

    Case-insensitive lookup. Returns None if `term` is not in the mapping;
    consumers MUST BLOCK with a clear error naming the unmapped term
    (REQ-0.0.16-05-06).
    """
    if not term:
        return None
    lowered = term.lower()
    for key, value in STATUS_VOCAB_MAPPING.items():
        if key.lower() == lowered:
            return value
    return None
```

**Design choices:**

- Use `types.MappingProxyType` (not Pydantic `BaseModel`) because the
  artifact is a **mapping**, not a record. `MappingProxyType` gives exactly
  the immutability semantics REQ-05 asks for (mutation raises `TypeError`)
  without the ceremony of modeling a single-field Pydantic class. The
  repository's models policy (`.claude/rules/models.md`) applies to *data
  records*, not lookup tables — precedent at `src/gzkit/ledger.py:23`
  (`OBPI_RUNTIME_STATES = {...}` is a module-level frozen set, not a
  Pydantic model).
- The raw dict `_RAW_MAPPING` is private (leading underscore) so the only
  public surface is the read-only proxy.
- Case-insensitive `canonicalize_status` helper mirrors the validator's
  comparison semantics (`src/gzkit/commands/validate_frontmatter.py:106`).

## Test plan (`tests/governance/test_status_vocab.py`)

Every test carries a `@covers("REQ-0.0.16-05-NN")` decorator so the
Stage 3 Phase 1b parity gate passes. Use stdlib `unittest`.

| Test method | REQ covered | Mechanism |
|-------------|-------------|-----------|
| `test_mapping_importable_without_side_effects` | REQ-01 | Importing the module binds a non-empty `STATUS_VOCAB_MAPPING`; no I/O occurs (assert via `importlib.reload` + no file handles). |
| `test_mapping_includes_brief_five_terms` | REQ-02 | Assert `{"Draft","Proposed","Pending","Validated","Completed"} <= set(STATUS_VOCAB_MAPPING)`. |
| `test_mapping_includes_all_observed_drift_terms` | REQ-02 (extended) | Assert `{"Accepted","archived","Pending-Attestation","Pool","Promoted","Superseded"} <= set(STATUS_VOCAB_MAPPING)`. |
| `test_every_canonical_value_is_in_ledger_set` | REQ-03 | For each value in `STATUS_VOCAB_MAPPING.values()`, assert value ∈ `CANONICAL_LEDGER_TERMS` AND value ∈ the ledger-authored set (import `OBPI_RUNTIME_STATES` from `gzkit.ledger` and `{"pending","validated","completed","abandoned"}` for ADR terms; the union must include every mapped value). |
| `test_mapping_is_immutable` | REQ-05 | Assert `STATUS_VOCAB_MAPPING["Draft"] = "x"` raises `TypeError`. |
| `test_canonicalize_status_case_insensitive` | REQ-01 (helper) | Assert `canonicalize_status("draft") == "pending"` and `canonicalize_status("DRAFT") == "pending"`. |
| `test_canonicalize_status_unknown_returns_none` | REQ-06 (consumer contract) | Assert `canonicalize_status("XYZ") is None` — consumer tests (OBPI-02/03) verify the BLOCK-on-None semantics; this OBPI only exports the helper. |

Tests use the canonical `uv run -m unittest` runner, no pytest.

## State-doctrine addendum (`docs/governance/state-doctrine.md`)

Append a new top-level section at the end of the file:

```markdown
---

## Canonical Status Vocabulary (ADR-0.0.16 addendum)

**Source:** [ADR-0.0.16 — Frontmatter-Ledger Coherence Guard](../design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md)

**Canonical constant:** `gzkit.governance.status_vocab.STATUS_VOCAB_MAPPING`

Frontmatter `status:` terms in circulation across gzkit (as of ADR-0.0.16
authoring) do not all match the ledger state-machine terms defined in
ADR-0.0.9. This addendum records the canonical mapping that downstream
surfaces — `gz gates` error output (OBPI-0.0.16-02) and the
`frontmatter-ledger-coherence` chore (OBPI-0.0.16-03) — consume. There is
exactly one canonical mapping; consumers import the constant and never
inline duplicates.

| Frontmatter term     | Canonical ledger term | Rationale |
|----------------------|-----------------------|-----------|
| Draft                | pending               | Authoring state; no ledger events yet |
| Proposed             | pending               | ADR authored but not validated |
| Pool                 | pending               | Backlog item; no lifecycle events |
| Promoted             | pending               | Recently promoted from pool; no events yet |
| Pending              | pending               | Direct mirror |
| Accepted             | validated             | Historical term for Gate-1 validated |
| Validated            | validated             | Direct mirror |
| Pending-Attestation  | completed             | Work done, awaiting human attestation |
| Completed            | completed             | Direct mirror (may lag `attested_completed` post-ceremony) |
| Superseded           | abandoned             | Replaced by later decision |
| archived             | abandoned             | Retired; no longer active |

Canonical targets are drawn from `OBPI_RUNTIME_STATES` (at
`src/gzkit/ledger.py`) and ADR lifecycle states
(`pending`/`validated`/`completed`/`abandoned`). Lookups are
case-insensitive; consumers that encounter a frontmatter term not in
this mapping MUST block with a clear error naming the unmapped term —
they never silently skip.
```

## Implementation ordering (TDD)

Per `.claude/rules/tests.md`, Red-Green-Refactor per behavior increment:

1. **Red** — create `tests/governance/__init__.py` (empty) and
   `tests/governance/test_status_vocab.py` with the first test
   (`test_mapping_importable_without_side_effects`). Run
   `uv run -m unittest tests.governance.test_status_vocab -v` — fails
   (module does not exist).
2. **Green** — create `src/gzkit/governance/__init__.py` and
   `src/gzkit/governance/status_vocab.py` with the minimum `STATUS_VOCAB_MAPPING`
   needed to pass that first test.
3. **Refactor** — tidy the module (docstrings, imports, type annotations).
4. Repeat Red-Green-Refactor for each subsequent test in the table above,
   growing the mapping and the helper until all seven tests pass.
5. Append the state-doctrine addendum (docs change — no TDD required;
   covered by `mkdocs build --strict` at Stage 3).
6. Run the full Stage 3 gate battery (`uv run gz lint`, `uv run gz typecheck`,
   `uv run gz test --obpi OBPI-0.0.16-05-status-vocab-mapping`,
   `uv run gz covers OBPI-0.0.16-05-status-vocab-mapping --json`,
   `uv run gz validate --documents`, `uv run mkdocs build --strict`).

## Verification (Stage 3 commands)

```bash
# Baseline quality (always)
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.16-05-status-vocab-mapping

# Heavy-lane doc and parity gates
uv run gz validate --documents
uv run mkdocs build --strict
uv run gz covers OBPI-0.0.16-05-status-vocab-mapping --json

# Brief-specific spot checks
python -c "from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING; print(len(STATUS_VOCAB_MAPPING))"
python -c "from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING; STATUS_VOCAB_MAPPING['Draft']='x'"  # expect TypeError
```

## Key proof (for Stage 4 ceremony)

```python
>>> from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING, canonicalize_status
>>> STATUS_VOCAB_MAPPING["Draft"]
'pending'
>>> canonicalize_status("Pending-Attestation")
'completed'
>>> STATUS_VOCAB_MAPPING["Draft"] = "x"
Traceback (most recent call last):
  ...
TypeError: 'mappingproxy' object does not support item assignment
```

## Out of scope (BLOCKER tripwire)

- Wiring `STATUS_VOCAB_MAPPING` into `gz gates` error output → OBPI-02
- Registering the frontmatter-ledger-coherence chore → OBPI-03
- Mutating any ADR/OBPI frontmatter to clear the 315 drift entries → OBPI-04
- Adding/modifying the validator itself → OBPI-01 (complete)
