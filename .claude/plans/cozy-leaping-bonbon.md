# Plan: OBPI-0.0.57-01 — Nominal ID Doctrine

## Context

ADR-0.0.57 Decision item 1 declares the third component of foundation ADR IDs (0.0.x) a **nominal integer** — a unique identifier, not a sequence position. OBPI-0.0.57-01 records this doctrine change by amending the two Validated ADRs that govern taxonomy mechanics (ADR-0.0.17) and doctrine guidance (ADR-0.0.18), narrowing the AGENTS.md ordering rule to feature ADRs only, auditing the taxonomy validator for sequence-position assumptions (none exist), and adding a test that explicitly asserts the validator accepts sparse/gapped foundation IDs.

## Path Discrepancy

The brief's allowed paths list `src/gzkit/trust_audits.py` as **CREATE**. The actual taxonomy validator lives at `src/gzkit/governance/trust_audits/taxonomy.py`. The audit annotation goes into the actual module; no spurious top-level `trust_audits.py` shim will be created. The plan satisfies REQ-03 against the real validator location.

---

## Step 1 — Amend ADR-0.0.17

**File:** `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`

Insert the following H2 block **before** the `## Attestation Block` line (currently at line 150), preserving all pre-amendment body content unchanged:

```markdown
## Amendment 2026-05-23 — ADR-0.0.57

ADR-0.0.57 (Foundation ADR Nominal ID Semantics and Priority Triage, 2026-05-22) extends this ADR's taxonomy by declaring (Decision item 1, verbatim):

> "The third component of foundation ADR IDs (0.0.x) is a nominal integer: a unique identifier, not a sequence position. gz-adr-create's minor-version odometer becomes a next-free-integer nominal allocator."

**Impact on ADR-0.0.17 mechanical enforcement:** The `gz validate --taxonomy` validator enforces format and kind coherence (0.0.x pattern, kind: foundation / feature, pool id-prefix). It has never enforced consecutive ordering of foundation integers — the amendment documents that as intentional nominal-identifier semantics, not an oversight. Sparse foundation trees (e.g. 0.0.54 present, 0.0.55 absent, 0.0.56 present) correctly return no taxonomy errors.

No existing foundation ADR directories or files are renamed or renumbered by this amendment. Recorded digits are preserved; the doctrine shift is semantic only (ADR-0.0.57 § Anti-pattern).
```

Then emit the ledger receipt:
```bash
uv run gz adr emit-receipt ADR-0.0.17 \
  --event amendment \
  --attestor "g0" \
  --evidence-json '{"source":"ADR-0.0.57","amendment_path":"docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md"}'
```

---

## Step 2 — Amend ADR-0.0.18

**File:** `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`

Insert the following H2 block **before** the `## Attestation Block` line (currently at line 117):

```markdown
## Amendment 2026-05-23 — ADR-0.0.57

ADR-0.0.57 (Foundation ADR Nominal ID Semantics and Priority Triage, 2026-05-22) adds operator guidance that companions this ADR's foundation/feature/pool taxonomy guidance (Decision items 1 and 3, verbatim):

> "The third component of foundation ADR IDs (0.0.x) is a nominal integer: a unique identifier, not a sequence position."
> "The CLAUDE.md 'order versioned identifiers semantically' rule scope shrinks to feature ADRs only — nominal foundation IDs have no semantic ordering."

**Nominal vs. semver guidance for operators (additive — preserves existing guidance):**

- Foundation ADRs (kind: foundation, semver 0.0.x): the 0.0.x component is a **nominal integer** — uniquely identifies the ADR but carries no ordering signal. Agents and operators MUST NOT infer work order, precedence, or relative importance from foundation ID sequence. Priority of foundation work is determined by the `gz-foundation-triage` skill (ADR-0.0.57 Decision item 2), not by ID number.
- Feature ADRs (kind: feature, semver 0.y.z and up): retain genuine semver semantics — ordering, comparison, and precedence all apply as before.
- The existing pool/foundation/feature taxonomy guidance, kind constraints, and semver format rules in this ADR remain fully in force.
```

Then emit the ledger receipt:
```bash
uv run gz adr emit-receipt ADR-0.0.18 \
  --event amendment \
  --attestor "g0" \
  --evidence-json '{"source":"ADR-0.0.57","amendment_path":"docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md"}'
```

---

## Step 3 — Narrow AGENTS.md ordering rule

**File:** `AGENTS.md` (Local Agent Rules section, lines 322-323)

Current:
```
- Order versioned identifiers semantically, never lexicographically. Example: `ADR-0.9.0` comes before `ADR-0.10.0`.
- Apply semantic-version ordering in ADR summaries, comparisons, and any operator-facing status narration.
```

Replace with:
```
- Order **feature ADR** versioned identifiers semantically, never lexicographically. Example: `ADR-0.9.0` comes before `ADR-0.10.0`. Applies to non-`0.0.x` identifiers only — foundation IDs are nominal; see counter-rule below.
- Apply semantic-version ordering in feature ADR summaries, comparisons, and any operator-facing status narration.
- **Foundation ADR IDs (0.0.x) are nominal — NEVER order or sequence them.** ADR-0.0.57 declares the third component a unique identifier with no sequence-position semantics. No ordering, comparison, or work-order inference is permitted for 0.0.x IDs.
```

---

## Step 4 — Annotate taxonomy validator (audit finding)

**File:** `src/gzkit/governance/trust_audits/taxonomy.py`

Audit finding: the module contains zero sequence-position assumptions. The `audit_adr_taxonomy` function iterates `sorted(adr_root.rglob(...))` for deterministic error ordering only — no max-N, no consecutive-integer check, no gap detection. The `_FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")` matches any `0.0.<digits>` pattern without enforcing sequence.

Add a one-line annotation comment to the module docstring (end of the existing docstring) and to `_FOUNDATION_SEMVER_RE`:

```python
# audit-exempt: regression-invariant-overlay ADR-0.0.57: no sequence-position assumptions; nominal-ID doctrine confirmed
_FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")
```

And at the module docstring, add one line:
```
* Audit (ADR-0.0.57 OBPI-01): no sequence-position assumptions present — nominal-ID semantics are correctly implicit.
```

---

## Step 5 — Create tests/test_taxonomy_validator_nominal.py

**File:** `tests/test_taxonomy_validator_nominal.py` (new)

Import pattern from existing tests:
```python
from gzkit.governance.trust_audits import audit_adr_taxonomy
from gzkit.traceability import covers
```

Three test methods in `TestNominalIdTaxonomyValidator(unittest.TestCase)`:

1. `test_sparse_foundation_ids_produce_no_taxonomy_errors` — `@covers("REQ-0.0.57-01-04")` — temp tree with 0.0.54, gap at 0.0.55, 0.0.56 → `audit_adr_taxonomy(root) == []`
2. `test_nonconsecutive_foundation_ids_produce_no_taxonomy_errors` — `@covers("REQ-0.0.57-01-04")` — temp tree with 0.0.1, 0.0.5, 0.0.10 → returns []
3. `test_plan_allocator_is_unchanged` — `@covers("REQ-0.0.57-01-05")` — imports `gzkit.commands.plan._next_available_foundation_semver` and asserts it still uses the max+1 pattern (via a temp dir with 0.0.3 → expects "0.0.4"), confirming commands/plan.py was not modified by this OBPI

Each test creates minimal ADR frontmatter packages in a `tempfile.TemporaryDirectory`:
```
docs/design/adr/foundation/ADR-0.0.54-slug-a/ADR-0.0.54-slug-a.md
```
with frontmatter: `id:`, `status: Draft`, `kind: foundation`, `semver: 0.0.<N>`.

---

## Files Modified

| File | Change |
|------|--------|
| `docs/design/adr/foundation/ADR-0.0.17-.../ADR-0.0.17-....md` | Amendment block prepended before Attestation Block |
| `docs/design/adr/foundation/ADR-0.0.18-.../ADR-0.0.18-....md` | Amendment block prepended before Attestation Block |
| `AGENTS.md` | Lines 322-323 narrowed to feature ADRs; foundation counter-rule added |
| `src/gzkit/governance/trust_audits/taxonomy.py` | Audit-exempt annotation added (module docstring + `_FOUNDATION_SEMVER_RE`) |

## Creates these files

| File | Content |
|------|---------|
| `tests/test_taxonomy_validator_nominal.py` **CREATE** | 3 REQ-derived tests; imports `audit_adr_taxonomy`, `covers` |

## Verification

```bash
# Nominal-ID specific tests (OBPI scope)
uv run gz arb step --name unittest -- uv run -m unittest tests.test_taxonomy_validator_nominal -v

# Full suite
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb ruff
uv run gz arb typecheck

# Docs build (heavy lane)
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# Validate taxonomy still passes on live tree (sparse gap assertion)
uv run gz validate --taxonomy

# Surface checks (Demo section)
grep -q "nominal" docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md
grep -q "nominal" docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md
grep -E "Foundation ADR IDs.*nominal" AGENTS.md
```
