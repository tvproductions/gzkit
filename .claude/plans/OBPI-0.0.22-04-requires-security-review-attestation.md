# Plan: OBPI-0.0.22-04 — `_requires_security_review_attestation` audit OR

**OBPI:** OBPI-0.0.22-04-requires-security-review-attestation
**Parent ADR:** ADR-0.0.22-security-sensitivity-doctrine
**Lane:** Heavy
**Depends on:** OBPI-0.0.22-01 (Completed — adds `sensitivity` to brief schema)

## Context

OBPI-0.0.22-01 has landed: the schema (`src/gzkit/schemas/obpi.json`,
`src/gzkit/schemas/adr.json`) now allows a `sensitivity: "security"`
frontmatter field on briefs, and OBPI-0.0.22-02/03 ship the registry +
auto-detect validator. What is still missing — and is this brief's only
contribution — is the **runtime gate** that fires when a brief carries
`sensitivity: security`: today, a `lite + feature + sensitivity:security`
brief is still self-closeable because `_requires_human_obpi_attestation`
ignores the third axis.

The current predicate at `src/gzkit/commands/adr_audit.py:262-273` reads:

```python
def _requires_human_obpi_attestation(parent_adr: str | None, parent_lane: str) -> bool:
    if not isinstance(parent_adr, str) or not parent_adr:
        return False
    if _is_foundation_adr(parent_adr):
        return True
    return parent_lane == "heavy"
```

The TTY + `ATTEST` gate at `_enforce_human_attestation_authenticity`
(lines 310-396) is reused as-is — REQ-04 is explicit: the OR alone is
sufficient; no new TTY-gating code lands in this OBPI.

Brief content is available at every call site:

- `src/gzkit/commands/obpi_complete.py:91` already has `original_content`
  and is the canonical OBPI-completion entry point.
- `src/gzkit/commands/adr_audit.py:494` (in `_validate_obpi_completion_evidence`)
  receives the obpi_content and forwards it.

The new predicate therefore takes the brief frontmatter (or the
brief content) as its third argument and ORs into the existing
predicate.

AGENTS.md § "Lane & Kind Attestation Matrix" (line 291) becomes
"Lane & Kind & Sensitivity Attestation Matrix" — a third-axis successor
enumerating every (kind × lane × sensitivity) cell, with `security` rows
marking attestation as Required regardless of lane or kind, and citing
`_requires_human_obpi_attestation` as the source-of-truth function.
The same edit lands in the template at
`src/gzkit/templates/agents.md:267`.

## Files

**Source (predicate + composition):**

- `src/gzkit/commands/adr_audit.py` — add `_requires_security_review_attestation(brief_frontmatter)`; OR into `_requires_human_obpi_attestation`; thread brief content/frontmatter through call sites.

**Source (call sites that pass brief frontmatter to the predicate):**

- `src/gzkit/commands/obpi_complete.py` — pass parsed brief frontmatter into the predicate at the existing call (line 91).
- (No other call site needs updating: the ADR-emit-receipt path is ADR-level, not brief-level.)

**Tests:**

- `tests/test_obpi_complete_cmd.py` — add behavioral tests for the four-quadrant matrix (REQ-02..04) using existing patterns.
- `tests/commands/test_adr_audit.py` *(or new `tests/test_adr_audit_predicates.py`)* — direct unit tests for `_requires_security_review_attestation` (REQ-01) and the OR composition, plus the no-regression cases.
- `tests/test_obpi_complete_cmd.py` (existing TTY-gate class) — add a `lite + feature + sensitivity:security` headless-refusal case (REQ-05).

**Documentation / matrix update:**

- `AGENTS.md` — replace § "Lane & Kind Attestation Matrix" with § "Lane & Kind & Sensitivity Attestation Matrix"; enumerate every cell; cite the predicate as source-of-truth (REQ-06).
- `src/gzkit/templates/agents.md` — same edit as AGENTS.md (template mirror per `.claude/rules/skill-surface-sync.md`).

**No edits to:**

- Schema files (OBPI-01 territory)
- `data/security_surfaces.json` or `src/gzkit/governance/trust_audits.py` sensitivity-binding code (OBPI-02/03 territory)
- `_enforce_human_attestation_authenticity` (REQ-04 explicitly forbids new TTY-gating code)
- ARB canonical command slot (OBPI-05) or rule file (OBPI-06)

## Steps

### Step 1 — RED tests for `_requires_security_review_attestation` (REQ-01)

Add direct unit tests in `tests/test_adr_audit_predicates.py` (new file) that:

- Pass a frontmatter dict with `sensitivity: "security"` → returns `True`.
- Pass a frontmatter dict with no `sensitivity` key → returns `False`.
- Pass a frontmatter dict with `sensitivity: ""` or any other string → returns `False` (only `"security"` triggers).
- Decorate each test `@covers(REQ-0.0.22-04-01)`.

Run the tests; confirm they fail because the function does not exist yet.

### Step 2 — GREEN: implement `_requires_security_review_attestation`

Add the function in `src/gzkit/commands/adr_audit.py` directly above
`_requires_human_obpi_attestation`:

```python
def _requires_security_review_attestation(brief_frontmatter: Mapping[str, Any] | None) -> bool:
    """Return True when a brief carries sensitivity: security (ADR-0.0.22)."""
    if not isinstance(brief_frontmatter, Mapping):
        return False
    return brief_frontmatter.get("sensitivity") == "security"
```

Run unit tests; confirm Step-1 tests are GREEN.

### Step 3 — RED tests for the OR composition (REQ-02..04)

Add tests for the updated `_requires_human_obpi_attestation` signature
(now accepts a third frontmatter argument; default `None` preserves the
two-argument call shape used by ADR-level callers):

- `lite + feature + sensitivity:security` → True (REQ-02)
- `lite + feature + sensitivity:null` → False (REQ-03)
- `heavy + feature + sensitivity:null` → True (REQ-04, no regression)
- `lite + foundation + sensitivity:null` → True (REQ-04, no regression)
- `lite + feature` (frontmatter argument omitted) → False (call-site-compat)

Decorate each with the appropriate `@covers(REQ-0.0.22-04-NN)`.

Confirm REQ-02 fails (still self-closeable); the others pass (existing
behavior).

### Step 4 — GREEN: thread frontmatter into `_requires_human_obpi_attestation`

Update the function signature to:

```python
def _requires_human_obpi_attestation(
    parent_adr: str | None,
    parent_lane: str,
    brief_frontmatter: Mapping[str, Any] | None = None,
) -> bool:
```

Add the OR branch:

```python
    if _requires_security_review_attestation(brief_frontmatter):
        return True
```

Default-`None` preserves backward compatibility with the ADR-level call
in `adr_emit_receipt_cmd` and tests that exercise the two-argument form.

Update `obpi_complete._resolve_and_validate` to parse the brief
frontmatter from `original_content` and pass it as the third argument.
Use the existing `parse_frontmatter_value` helper from `gzkit.ledger`
or a small local YAML-block parser — preferred form is reading the
already-loaded frontmatter via the brief schema validator helpers if
available; otherwise add a private `_parse_obpi_frontmatter(content)`
helper that walks the `---` block.

Run unit tests; confirm REQ-02..04 cases are now GREEN.

### Step 5 — RED test for headless refusal under `sensitivity: security` (REQ-05)

Add a behavioral test in `tests/test_obpi_complete_cmd.py` modelled on
the existing GHI #290 TTY-gate tests (~line 838 onwards): set up a
`lite + feature` parent ADR, brief frontmatter `sensitivity: security`,
run `obpi_complete_cmd` with `_is_human_attestation_tty_available`
patched to return `False` and no `attestor_present` flag. Assert the
call raises `GzCliError` (or exits non-zero) with the GHI-#290
authenticity-gate message, mirroring the heavy-lane case.

Decorate `@covers(REQ-0.0.22-04-05)`.

Confirm RED — the path currently bypasses the gate because the predicate
returns False without the OR.

### Step 6 — GREEN: confirm OR triggers the existing gate (no new TTY code)

The OR added in Step 4 should already make REQ-05 pass, because once
`_requires_human_obpi_attestation` returns True, the existing
`_enforce_human_attestation_authenticity` is invoked at the existing
call site. Run the test; confirm GREEN.

If the call site does not reach the gate for OBPI-completion (only ADR
emit-receipt currently calls it explicitly — see `obpi_complete.py:91`
vs `adr_audit.py:599-614`), audit the OBPI completion path. If the gate
needs to be wired into `obpi_complete` (separately from REQ-04's
"no new TTY-gating code"), this is a missing-wire defect that pre-dates
this OBPI; surface as a flag, file a GHI if needed, and fix in scope
(the wiring is *use* of an existing gate, not new gate code).

### Step 7 — Update AGENTS.md matrix to third axis (REQ-06)

Replace § "Lane & Kind Attestation Matrix" in `AGENTS.md` (line 291) with
§ "Lane & Kind & Sensitivity Attestation Matrix" enumerating every
(kind × lane × sensitivity) cell:

| Parent Kind | Parent Lane | Sensitivity | Brief-level Human Attestation | Source of truth |
|-------------|-------------|-------------|-------------------------------|-----------------|
| `foundation` | `lite`  | absent     | **Required** | foundation branch |
| `foundation` | `lite`  | `security` | **Required** | foundation OR security |
| `foundation` | `heavy` | absent     | **Required** | foundation OR lane |
| `foundation` | `heavy` | `security` | **Required** | three-way OR |
| `feature`    | `lite`  | absent     | Self-closeable after evidence | — |
| `feature`    | `lite`  | `security` | **Required** | security branch |
| `feature`    | `heavy` | absent     | **Required** | lane branch |
| `feature`    | `heavy` | `security` | **Required** | lane OR security |

Add the disclaimer: "*Matrix is a readable projection of
`_requires_human_obpi_attestation` at `src/gzkit/commands/adr_audit.py`.
If the matrix and the code disagree, the code is source of truth; the
matrix is the defect.*" (Same wording shape as the existing kind/lane
disclaimer at line 306.)

Apply the identical edit to `src/gzkit/templates/agents.md` (line 267).

Run `uv run gz agent sync control-surfaces` afterward — even if AGENTS.md
is hand-maintained, the template should match (`.claude/rules/skill-surface-sync.md`).

### Step 8 — Verification sweep

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.22-04 --json   # parity gate
```

REQ → `@covers` parity must be clean before Stage 4. All baseline gates
(lint, typecheck, unittest, mkdocs, behave if applicable) must pass.

## Verification

| Check | Command | Expected |
|-------|---------|----------|
| Predicate unit tests | `uv run -m unittest tests.test_adr_audit_predicates -v` | All REQ-01..04 cases pass |
| OBPI-completion behavioral test | `uv run -m unittest tests.test_obpi_complete_cmd -v -k security` | REQ-05 case passes; existing tests unchanged |
| REQ → `@covers` parity | `uv run gz covers OBPI-0.0.22-04 --json` | `summary.uncovered_reqs == 0` |
| Lint | `uv run gz arb ruff` | clean |
| Typecheck | `uv run gz arb typecheck` | clean |
| Full unittest | `uv run gz arb step --name unittest -- uv run -m unittest -q` | OK |
| Docs build | `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` | clean |
| Documents validation | `uv run gz validate --documents` | clean |

## Notes — Destination-in-mind / Rejected alternatives

**Destination-in-mind:** Before authoring this plan, the conclusion already
forming was: "add a small `_requires_security_review_attestation` predicate,
OR it into the existing two-argument predicate by extending the signature
with an optional brief-frontmatter argument, and update the matrix to a
third axis. The TTY gate is reused — no new authentication code." That is
the approach this plan proposes.

**Rejected alternatives:**

1. **Mutate `_requires_human_obpi_attestation` in place without a new
   predicate.** Rejected: REQ-01 explicitly names the predicate as a
   testable, separately-mockable function — a single fused branch
   sacrifices the unit-test surface and the AGENTS.md citation target.
2. **Pass the *whole brief content* (string) to the predicate, parse
   inside.** Rejected: parsing is the call site's job, not the
   predicate's. The predicate operates on a parsed frontmatter mapping
   so unit tests can construct synthetic dicts trivially. Aligns with
   `.claude/rules/pythonic.md` § "Separation of concerns."
3. **Make the brief-frontmatter argument required (positional).**
   Rejected: breaks the ADR-level call at
   `adr_audit.py:494` and the ADR-emit-receipt path that does not have
   per-brief frontmatter. Default-`None` preserves the existing
   ADR-level call shape and makes the third axis additive.
4. **Add a new TTY gate specifically for security briefs.** Explicitly
   forbidden by REQ-04: "the ORing alone reuses the existing gate."
   Rejected on doctrine.
5. **Skip the AGENTS.md matrix edit ("the code is source of truth
   anyway").** Rejected: REQ-06 is explicit. Doctrine drift is invariant
   drift; the readable projection is the operator's surface.

The two-runner test boundary (`.claude/rules/tests.md`) keeps unit tests
under `tests/` and any required BDD scenarios under `features/`. The
behavioral tests for the OR composition do not need to spawn `git` or
`uv sync`, so they belong in `tests/`. Heavy-lane Gate 4 BDD coverage —
if any new feature-level scenarios are required — is added in `features/`
under a `@REQ-0.0.22-04-NN` tag; otherwise the existing security-
sensitivity feature coverage is sufficient (verify via the brief's
`Acceptance Criteria` after Step 6).
