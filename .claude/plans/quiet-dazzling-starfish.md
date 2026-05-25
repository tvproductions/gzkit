# Plan — OBPI-0.0.54-03 — `gz validate --agents-md-map-conformance`

## Context

ADR-0.0.54 canonized the **map-not-encyclopedia doctrine** for AGENTS.md: binding bullets + structured tables + canonical links only — no multi-paragraph rationale prose, worked examples, anti-pattern catalogs, or "Why this is canon" coda blocks. OBPI-01 authored the doctrine rule + tightened the budget. OBPI-02 lifted the prose sections out of AGENTS.md to `docs/governance/`. Both are `attested_completed`.

**Problem this OBPI solves:** the doctrine is currently enforced only by `gz validate --instructions-files-budget` (which caps **weight**) and the `/gz-context-diet` skill (which is **reactive**, invoked only on demand). The **shape** is invariant by doctrine but not by mechanism — the lifted AGENTS.md is free to re-accrete prose by the next ADR. The recovery plan (`docs/governance/get-out-of-jail-plan-2026-05-23.md`) names this validator as Move 3's mechanical fail-close.

**Outcome:** a new `gz validate --agents-md-map-conformance` scope that asserts the four shape criteria from ADR-0.0.54 § Decision item 3 against AGENTS.md, joins the `gz check` default pipeline as a fail-closed step, and points failures at `/gz-context-diet` as the operator remediation route. After this lands, prose accretion in AGENTS.md fails at CI time, not at next operator audit.

**Boundary:** this OBPI ships the validator only. Per § Sequencing, AGENTS.md (OBPI-02 territory), the doctrine rule (OBPI-01), and CLAUDE.md + `.claude/rules/*.md` application (OBPI-04) are all out of scope.

**In-flight defects already handled per PRIME DIRECTIVE:**
- ADR-0.0.54 manpage filename typo (`gz-validate.md` → `validate.md`) — **FIXED in-session** at lines 97 + 201 (in Allowed Paths).
- Broader manpage-reference drift across 4 other brief files (9 instances) — **TRACKED in GHI #532** with blocker comment naming three candidate routes.
- ADR-0.0.53 `RemediationPayload` not yet landed — **TRACKED structurally** by ADR-0.0.53-02 (`migrate-validators-remediation-meta`), which will sweep this validator's failure shape when it ships.

---

## Recommended approach

Mirror the `instructions_files_budget` sibling validator exactly. It is the structurally-nearest implementation pattern: same author (the doctrine), same target file (AGENTS.md), same remediation skill (`/gz-context-diet`), same `ValidationError` failure shape, same explicit-scope-plus-quality-runner registration shape.

### Step 1 — Author the validator module

**Create** `src/gzkit/governance/trust_audits/agents_md_map_conformance.py`. Single public entry:

```python
def audit_agents_md_map_conformance(project_root: Path) -> list[ValidationError]:
    ...
```

Internal structure (modeled on `instructions_files_budget.py`):

| Helper | Responsibility |
|---|---|
| `_load_budget_config(project_root)` | reuse pattern at `instructions_files_budget.py:37–42` — load `data/instructions_files_budget.json`, fall back to packaged defaults |
| `_parse_paragraphs(text)` | return list of paragraph dicts: `{lines, start_line, starts_with_marker, in_prohibited_section}`. Paragraph = consecutive non-blank lines. Markers: `- `, `1.` `2.`…, `**`. |
| `_check_paragraph_length(paragraphs, file_label)` | criterion (a) — hard rejection: paragraph > 5 lines AND no binding-marker prefix → `ValidationError(type="agents_md_map_conformance", ...)`. Per § Consequences Negative #7, paragraphs that DO start with a binding marker are exempt from (a) regardless of length. |
| `_check_prohibited_titles(text)` | criterion (b) — hard rejection: subsection title (any heading level) matches `{Worked example, Worked Example, Anti-patterns, Anti-Patterns, Rationale, Why this is canon, Why X is canon (regex), ...}` → `ValidationError`. |
| `_check_link_resolution(text, project_root)` | criterion (c) — hard rejection: every `[…](path)` (relative, no scheme) where path doesn't resolve to an existing file → `ValidationError`. When path has `#anchor`, parse the target file's `## headings` and verify the anchor matches a slugified heading. The match is permissive (case-insensitive, GitHub-style slug). |
| `_check_budget(target, budget)` | criterion (d) — hard rejection: file size > budget → `ValidationError`. Reuse identical char-counting math from `_check_one_file` at `instructions_files_budget.py:45–58`; do NOT call that helper directly (it embeds its own remediation prose for a different scope). |
| `_check_per_bullet_advisory(paragraphs)` | REQ-05 — **soft warning**: bullets in binding-rule sections (PRIME DIRECTIVE, DO IT RIGHT, Behavior Rules) that span >3 lines emit `ValidationError(type="agents_md_map_conformance_advisory", ...)`. The `_advisory` suffix keeps the warning out of the policy-breach set (see Step 2). |

Module-level constants mirror sibling shape:

```python
_REMEDIATION = (
    "Run /gz-context-diet (or `uv run gz chores show instructions-files-diet`) "
    "to lift inline rationale to docs/governance/ behind one-line pointers."
)
_PROHIBITED_TITLES = frozenset({...})
_BINDING_MARKER_PREFIXES = ("- ", "* ", "1.", "2.", ..., "**")
_BINDING_RULE_SECTION_HEADINGS = frozenset({
    "PRIME DIRECTIVE (OWNERSHIP)",
    "DO IT RIGHT (CRAFTSMANSHIP MAXIM)",
    "Behavior Rules",
    ...
})
_TARGET_FILES = ("AGENTS.md",)  # CLAUDE.md / rules application is OBPI-04 scope
```

Embed `/gz-context-diet` in every failure `message` per the sibling's pattern at `instructions_files_budget.py:54–57`. The forward-compat path to ADR-0.0.53 `RemediationPayload` is the message → structured `recovery` field migration that ADR-0.0.53-02 will execute.

### Step 2 — Wire the validator into the registry

`src/gzkit/governance/trust_audits/__init__.py` — re-export `audit_agents_md_map_conformance` alongside the other `audit_*` functions.

**`src/gzkit/commands/validate_cmd.py`:**

| Site | Edit |
|---|---|
| `_collect_errors()` signature (~line 480) | add `check_agents_md_map_conformance: bool = False` parameter (alphabetical position among siblings) |
| `explicit_scopes` dict (lines 499–547) | add `"agents_md_map_conformance": check_agents_md_map_conformance,` near the sibling at line 521 |
| `_explicit_scope_runners()` (lines 591–650) | add `"agents_md_map_conformance": lambda: trust_audits.audit_agents_md_map_conformance(project_root),` near the sibling at line 623–625 |
| `_POLICY_BREACH_ERROR_TYPES` set (~line 1145) | add `"agents_md_map_conformance"` only — NOT the `_advisory` variant. Hard rejections fail-close with exit 3; advisories surface in output but do not change exit code. |

### Step 3 — Add the CLI parser flag

`src/gzkit/cli/parser_maintenance.py` — add immediately after the sibling at lines 464–468:

```python
p_validate.add_argument(
    "--agents-md-map-conformance",
    dest="check_agents_md_map_conformance",
    action="store_true",
    help="AGENTS.md map-not-encyclopedia shape (ADR-0.0.54)",
)
```

### Step 4 — Wire into `gz check` default pipeline

`src/gzkit/commands/quality.py` — mirror the sibling exactly:

| Site | Edit |
|---|---|
| Imports at top of `_build_check_steps` (~line 295) | add `run_agents_md_map_conformance_audit` alongside `run_instructions_files_budget_audit` |
| `_build_check_steps()` step list (~line 325) | add `("AGENTS.md map conformance", run_agents_md_map_conformance_audit)` immediately after the `Instructions files budget` step |
| Define `run_agents_md_map_conformance_audit(project_root)` | as a sibling to `run_instructions_files_budget_audit` — call `trust_audits.audit_agents_md_map_conformance(project_root)`, hand its `list[ValidationError]` to whatever output/exit-translation helper the sibling already uses |

The `gz_check_cmd.steps` test-exposed attribute at lines 460–469 auto-includes the new step because it's a thin re-call of `_build_check_steps()`.

### Step 5 — Tests

**Create** `tests/governance/test_agents_md_map_conformance.py`. Mirror `tests/governance/test_audit_instructions_files_budget.py`:

- `unittest.TestCase` base class
- `tempfile.TemporaryDirectory()` per-test fixtures with a synthetic project root containing `data/instructions_files_budget.json` + a synthetic `AGENTS.md`
- Helper `_write_agents_md(root, content)` writes the fixture
- One test class per criterion; each test asserts on `errors[i].type` and `errors[i].artifact` (semantic), and confirms `"gz-context-diet" in errors[i].message` (recovery-semantics, allowed)

Test matrix (one test per row; REQ tag in docstring per `.gzkit/rules/tests.md`):

| Test | Fixture shape | Expected |
|---|---|---|
| `test_paragraph_over_5_lines_without_marker_rejects` (REQ-01a) | AGENTS.md with a 7-line prose paragraph and no leading `- `/`1.`/`**` | one error, type `agents_md_map_conformance` |
| `test_paragraph_with_binding_marker_passes_at_any_length` (REQ-01a, REQ-05 corner) | AGENTS.md with a 12-line binding-bullet paragraph (starts with `- `) | zero errors of type `agents_md_map_conformance` |
| `test_prohibited_subsection_title_rejects` (REQ-01b) | AGENTS.md with `## Worked example`, `## Anti-patterns`, `## Rationale` subsections — one per fixture for each variant | one error per fixture, all type `agents_md_map_conformance` |
| `test_dangling_link_rejects` (REQ-01c) | AGENTS.md with `See [Foo](docs/governance/nonexistent.md)` | one error |
| `test_dangling_anchor_rejects` (REQ-01c) | link path exists; `#missing-anchor` does not match any heading in the target | one error |
| `test_resolving_link_passes` (REQ-01c) | link path + anchor both resolve | zero errors |
| `test_file_size_within_budget_passes` (REQ-01d) | minimal AGENTS.md well under budget | zero errors |
| `test_file_size_over_budget_rejects` (REQ-01d) | AGENTS.md padded over the budget value | one error |
| `test_happy_path_against_lifted_agents_md` (REQ-02) | copies the real lifted `AGENTS.md` from the project root into the temp fixture | zero hard-rejection errors |
| `test_advisory_warning_for_long_binding_bullet` (REQ-05) | AGENTS.md with a 5-line binding bullet inside `## Behavior Rules` | one error of type `agents_md_map_conformance_advisory` — verifies it does NOT also surface as `agents_md_map_conformance` |
| `test_remediation_message_points_at_gz_context_diet` (REQ-03 forward-compat) | any failing fixture | `"/gz-context-diet" in errors[0].message` |

No new test fixtures beyond inline string-built AGENTS.md content. No external dependencies. No `@covers` decorators (sibling test does not use them; per Explore agent confirmation).

### Step 6 — Manpage

`docs/user/manpages/validate.md` — add a new H3 subsection after the existing `--instructions-files-budget` section, mirroring the format the Explore agent identified at the `--chores-layout` section (lines 203–230). Include:

- One-paragraph description naming ADR-0.0.54 and the four criteria
- Exit code table (3 = policy breach; reuse the standard 4-code map per `.claude/rules/cli.md`)
- A real EXAMPLES code block showing (1) green case `uv run gz validate --agents-md-map-conformance` and (2) a synthetic prohibited-title violation with the actual error format

The EXAMPLES output must be **observed** from the implemented validator (per `.gzkit/rules/cli.md` § Adding CLI Features), not invented.

### Step 7 — Re-audit and ceremony

After implementation lands:
1. Re-run `uv run gz plan audit OBPI-0.0.54-03` against the new plan; receipt must PASS.
2. Enter the `gz-obpi-pipeline` for OBPI-0.0.54-03 — registered hook will route on the PASS receipt.

---

## Files

| File | Action | Reuse |
|---|---|---|
| `src/gzkit/governance/trust_audits/agents_md_map_conformance.py` | **create** | shape from `instructions_files_budget.py` |
| `src/gzkit/governance/trust_audits/__init__.py` | edit (re-export) | existing pattern |
| `src/gzkit/commands/validate_cmd.py` | edit (~4 sites) | sibling registration at lines 521, 623–625 |
| `src/gzkit/cli/parser_maintenance.py` | edit (1 site) | sibling parser at lines 464–468 |
| `src/gzkit/commands/quality.py` | edit (2 sites) | sibling step at line 325 |
| `tests/governance/test_agents_md_map_conformance.py` | **create** | shape from `test_audit_instructions_files_budget.py` |
| `docs/user/manpages/validate.md` | edit (add H3 subsection) | sibling section at lines 203–230 |

**Not edited (Denied Paths per brief):**
- `AGENTS.md` (OBPI-02)
- `.gzkit/rules/agents-md-map-doctrine.md` (OBPI-01)
- `data/instructions_files_budget.json` (OBPI-01/04)
- `CLAUDE.md`, `.claude/rules/*.md` (OBPI-04)
- Lock-handoff coupling, ledger format, schema files

---

## Verification

Acceptance per brief § Verification:

```bash
uv run gz validate --agents-md-map-conformance
uv run gz arb step --name unittest -- uv run -m unittest -q tests.governance.test_agents_md_map_conformance
uv run gz check
uv run gz validate --documents --surfaces
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

End-to-end behavioral checks:

1. **Green path:** `uv run gz validate --agents-md-map-conformance` exits 0 against the currently-lifted `AGENTS.md`.
2. **Hard rejection path:** create a throwaway `AGENTS.md.test` (NOT committed) with a `## Worked example` subsection; temporarily point the validator at it (via a test helper, not by editing the real file); observe exit 3 + `RemediationPayload`-shaped message embedding `/gz-context-diet`.
3. **Advisory path:** AGENTS.md fixture with a 5-line binding bullet under `## Behavior Rules` surfaces an `agents_md_map_conformance_advisory` finding in `gz check` output without changing the exit code.
4. **Pipeline integration:** `uv run gz check` includes the step `AGENTS.md map conformance` in its output table and the step contributes to its overall exit status.
5. **CLI audit clean:** `uv run gz cli audit` exits 0 — the new flag has manpage + index coverage per `.claude/rules/cli.md`.
6. **No regression:** the full `uv run -m unittest -q` suite remains green; `uv run gz check` overall exits 0.

ARB receipts produced (per brief § Gate 2 / § Code Quality / § Gate 3):

- `arb-step-unittest-*` (test suite)
- `arb-ruff-*` (lint)
- `arb-step-typecheck-*` (ty)
- `arb-step-mkdocs-*` (docs build)
- `arb-step-agents-md-map-conformance-*` (the new scope's own ARB step)

Receipt IDs land in the brief's `### Implementation Summary` at completion. Gate 5 attestation is universal per ADR-0.0.36; foundation-kind brief requires explicit human attestor.

---

## Open question (operator-decision after this plan, NOT a blocker)

REQ-01 criterion (c) wording diverges slightly between the ADR and the doctrine rule:

- **ADR Decision item 3:** "every `See [text](path)` link resolves to an existing file with the named anchor"
- **`.gzkit/rules/agents-md-map-doctrine.md`:** "Every `See [text](path)` link resolves to an existing file"

The ADR is more strict (anchor verification). This plan implements the **stricter** ADR phrasing — anchors are verified when present. This is the safer default: a permissive validator that silently passes broken anchors is the failure shape ADR-0.0.54 § Consequences Negative #3 warns about. If the operator prefers the rule's softer phrasing, the anchor-check can be made best-effort (warn-not-reject) under a one-line REQ-05 extension.

---

## R1+expansion amendment (2026-05-25)

**Operator course-correction surfaced mid-pipeline:** the validator was authored against the rendered Layer-3 AGENTS.md without verifying the construction pipeline. AGENTS.md is template-constructed via `gz governance render`. The doctrine's edit surface is `src/gzkit/templates/agents.md` (23,248 chars) + `.gzkit/invariants/*.json` (3 entries, ADR-0.0.37 work-in-progress). Composition is half-built; the rule corpus has not migrated to the registry; the template carries the prose inline.

OBPI-02 was attested `Completed` but did not deliver doctrine-conformant template — the validator's first run against rendered AGENTS.md surfaces 7 hard findings traceable to template-side prose (1 budget overrun 31387/15000, 2 prohibited subsection titles at lines 113 + 278, 4 long paragraphs at lines 19/188/266/288).

The 5k recovery-plan target is post-ADR-0.0.37; the today-achievable target is 15k (the ADR-0.0.54 doctrine number). 5k dependency tracked in **GHI #533**.

**Operator decision: R1 + scope expansion.** Ship the validator AND absorb the lift OBPI-02 didn't finish, both in this OBPI. Brief amended: Allowed Paths gains template + `agent-contract-rationale.md`; REQ-01 reframed against template (primary) + registry (secondary) + rendered (budget only); REQ-10 added for the lift work. STOP-on-BLOCKERS clause revised to acknowledge OBPI-02's incomplete-but-attested state.

### Amended task structure (replaces original Steps 1–7)

| Task | Action | Files | Subagent model |
|---|---|---|---|
| 1 (DONE) | RED tests + validator stub | `agents_md_map_conformance.py` + `test_agents_md_map_conformance.py` | sonnet |
| 2 (DONE_WITH_CONCERNS) | Validator logic (made 10/11 tests GREEN; keystone fails — by design: surfaces template-side lift gap) | `agents_md_map_conformance.py` | opus |
| **2.5 (NEW)** | **Retarget validator at template (primary) + registry (secondary) + rendered (budget criterion only).** Update target-file logic to scan `src/gzkit/templates/agents.md` for shape criteria (a)/(b)/(c); keep budget criterion (d) against rendered AGENTS.md. Update the test fixtures to write template + budget config (or point at real template for keystone), assert validator output mapped to the new layer split. | `agents_md_map_conformance.py`, `test_agents_md_map_conformance.py` | sonnet |
| **2.6 (NEW)** | **Template lift pass.** Lift the 2 prohibited subsection titles + 4 long paragraphs from `src/gzkit/templates/agents.md` to `docs/governance/agent-contract-rationale.md` verbatim under named anchors; replace each with a one-line `See [...]` link preserving the binding-bullet text. Tighten where binding-bullet shape is achievable without semantic loss. Target: template ≤ 15k post-lift; rendered AGENTS.md ≤ 15k post-render. | `src/gzkit/templates/agents.md`, `docs/governance/agent-contract-rationale.md` | opus |
| **2.7 (NEW)** | **Re-render AGENTS.md.** `uv run gz governance render --target agents-md`. Verify byte-equivalence to expected output. Validator passes against template + rendered. | (CLI invocation; rendered AGENTS.md write is mechanical) | (inline, no dispatch) |
| 3 | Wire validator into `validate_cmd.py` + `parser_maintenance.py` + `quality.py` | as in original plan | sonnet |
| 4 | Manpage entry with observed CLI output | `docs/user/manpages/validate.md` | haiku |
| 5 | Present OBPI Acceptance Ceremony | (Stage 4) | narrator |

### Verification additions (post-amendment)

End-to-end checks add:

1. **Template-side conformance:** `uv run gz validate --agents-md-map-conformance` against the post-lift template emits zero hard findings.
2. **Rendered conformance:** `uv run gz governance render --target agents-md --check` exits 0 (byte-parity with committed AGENTS.md); `uv run gz validate --agents-md-map-conformance` against the rendered file emits zero hard findings within the 15k budget.
3. **Lift verbatim-preservation:** the lifted paragraphs in `agent-contract-rationale.md` are byte-equivalent to their original template positions (no compression-by-summarization, per ADR-0.0.54 § Decision item 2).
4. **Existing `--invariant-coherence` still green:** the template + registry + rendered chain remains coherent.

### Documents to NOT touch

Same as original plan, plus explicit clarification:
- The rendered `AGENTS.md` at project root is NEVER hand-edited; all fixes flow through template + render.
- `.gzkit/invariants/*.json` registry entries are ADR-0.0.37 territory; do not author new entries here.
- Budget JSON stays at 15k; the 5k destination is GHI #533.

### Insight record

Per Behavior Rule 11, an `improvement` record was appended to `.gzkit/insights/agent-insights.jsonl` (2026-05-25T17:30:00Z) capturing the course correction before completing the corrected work.
