# OBPI-0.0.19-02 — Scaffold Rendering (Pydantic + Jinja2 + CLI)

## Context

The prior OBPI in this ADR landed the pure library substrate for pre-execution reasoning walkthroughs: `AnchorRef`, `EvidenceBundle`, `resolve_anchor`, `gather_evidence` (attested-complete, 31/31 tests green, REQ parity 100%). Operators cannot yet invoke anything from a terminal — the library has no consumer. OBPI-0.0.19-02 closes that gap by adding:

1. `Walkthrough` / `WalkthroughSection` Pydantic models codifying the 8-section structure the parent ADR mandates.
2. A Jinja2 template rendering a `Walkthrough` to **byte-stable** markdown (YAML frontmatter + 8 H2 sections + evidence/prompt/reasoning blocks, reasoning blocks stubbed as `_[To be filled]_`).
3. A new top-level CLI verb `gz justify <anchor>` wiring `resolve_anchor` → `gather_evidence` → `render_scaffold` → markdown write, with `--save` / `--output` / `--related` / `--draft` / `--draft-slug` flags and the exit-code discipline from `.gzkit/rules/cli.md`.

Scope boundary: validate/round-trip subcommand (OBPI-03), skill authoring (OBPI-04), docs/BDD (OBPI-05). **Heavy lane** because a new CLI verb and a new Jinja template contract are external-consumer-facing; Gate 5 attestation is deferred to ADR-level closeout per lane inheritance.

## Implementation Tasks

TDD discipline per `.gzkit/rules/tests.md` § Red-Green-Refactor: one REQ → one failing test → minimum code → green → next increment. Tests pin REQ-IDs via `@covers`.

### Task 1 — Section constants + `WalkthroughSection` model (REQ-01, REQ-02, REQ-04)

**Files:** `src/gzkit/justify/walkthrough.py` (new), `tests/justify/test_walkthrough.py` (new)

Add module-level constants:

- `SECTION_HEADINGS: list[str]` — fixed 8-entry list in canonical order (mirrors parent ADR § "The 8 Sections"): "What I see (the problem)", "Per-instance severity", "Why this scope", "What it proposes", "Routing decision", "Why this design is right-sized", "What convinces me (evidence)", "Residual uncertainty".
- `SECTION_PROMPTS: dict[int, str]` — ordinal → short prompt text sourced from the parent ADR checklist (short single-sentence framing per section).

Add `WalkthroughSection(BaseModel)`:

- `model_config = ConfigDict(frozen=True, extra="forbid")` (per `.gzkit/rules/models.md`)
- Fields: `ordinal: int = Field(..., ge=1, le=8)`, `heading: str`, `prompt: str`, `evidence_citations: list[str]`, `reasoning: str`
- `@computed_field` or `@property` `is_filled` — returns `True` iff `reasoning.strip()` is non-empty AND `"_[To be filled]_"` is not a substring. (Pydantic frozen models support `@property`; prefer that for simplicity.)

Tests (all decorated `@covers("REQ-0.0.19-02-01")` / `-02` / `-04`):

- `test_section_headings_match_canonical_order` — assert `SECTION_HEADINGS[i] == expected` for i in 0..7 (REQ-04)
- `test_section_is_filled_false_on_placeholder` — `reasoning="_[To be filled]_"` ⇒ False (REQ-02)
- `test_section_is_filled_false_on_empty_whitespace` — `reasoning="   "` ⇒ False (REQ-02)
- `test_section_is_filled_true_on_actual_reasoning` — `reasoning="Because X"` ⇒ True (REQ-02)
- `test_section_rejects_ordinal_out_of_range` — ordinal=0 raises `ValidationError`; ordinal=9 raises (REQ-01)

### Task 2 — `Walkthrough` model + validators + `is_complete` (REQ-01, REQ-03, REQ-04)

**Files:** `src/gzkit/justify/walkthrough.py` (extend), `tests/justify/test_walkthrough.py` (extend)

Add `Walkthrough(BaseModel)`:

- `model_config = ConfigDict(frozen=True, extra="forbid")`
- Fields: `anchor: AnchorRef`, `evidence: EvidenceBundle`, `generated_at: str`, `sections: list[WalkthroughSection]`, `scaffold_version: str = "1.0"`
- `@model_validator(mode="after")` `_validate_sections` — raises `ValueError` unless `[s.ordinal for s in sections] == [1,2,3,4,5,6,7,8]` AND each `sections[i].heading == SECTION_HEADINGS[i]`. Single validator carries both invariants; error messages cite the mismatch.
- `def is_complete(self) -> bool:` — `return all(s.is_filled for s in self.sections)`. Structural only; NEVER evaluates reasoning quality semantically.

Tests:

- `test_walkthrough_accepts_canonical_8_sections` — happy path (REQ-01)
- `test_walkthrough_rejects_missing_ordinal` — 7 sections ⇒ `ValidationError` (REQ-01)
- `test_walkthrough_rejects_duplicate_ordinal` — two sections at ordinal 3 ⇒ `ValidationError` (REQ-01)
- `test_walkthrough_rejects_permuted_ordinals` — `[1,3,2,4,5,6,7,8]` ⇒ `ValidationError` (REQ-01)
- `test_walkthrough_rejects_heading_drift` — section 1 with heading "Wrong" ⇒ `ValidationError` (REQ-04)
- `test_walkthrough_is_complete_true_all_filled` (REQ-03)
- `test_walkthrough_is_complete_false_any_placeholder` (REQ-03)

### Task 3 — Jinja2 template + internal `render_markdown` helper (REQ-05, REQ-06)

**Files:** `src/gzkit/justify/templates/__init__.py` (new, empty marker), `src/gzkit/justify/templates/walkthrough.md.j2` (new), `src/gzkit/justify/walkthrough.py` (extend), `tests/justify/fixtures/walkthrough_expected.md` (new — golden)

Template (`walkthrough.md.j2`) content shape:

```jinja
---
anchor_id: {{ anchor_id }}
anchor_kind: {{ walkthrough.anchor.kind }}
generated_at: {{ walkthrough.generated_at }}
scaffold_version: {{ walkthrough.scaffold_version }}
---

# Walkthrough: {{ anchor_id }}

{% for section in walkthrough.sections -%}
## {{ section.ordinal }}. {{ section.heading }}

**Prompt:** *{{ section.prompt }}*

**Evidence:**
{% for cite in section.evidence_citations -%}
- {{ cite }}
{% else -%}
- _(no citations for this section)_
{% endfor %}
{{ section.reasoning }}

{% endfor -%}
```

Jinja env: `Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"), trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True, autoescape=False)` — deterministic whitespace, no HTML escaping (markdown output).

`render_markdown(walkthrough: Walkthrough) -> str` — internal module helper (not re-exported). Computes `anchor_id` for frontmatter (derivation: `walkthrough.anchor.identifier` if non-None, else `f"draft-{walkthrough.anchor.draft_slug or 'unnamed'}"`).

Fixture: build `walkthrough_expected.md` by (a) authoring a fixed `Walkthrough` in a helper (`_make_fixture_walkthrough()` with deterministic `generated_at="2026-04-22T00:00:00+00:00"`, known anchor, known citations), (b) running the renderer once locally, (c) committing the exact output. **The fixture is derived from code, but the code's output is the semantic contract** — the test asserts byte-equality, making any silent render drift fail loudly.

Tests:

- `test_rendered_markdown_byte_stable_across_invocations` — render same input twice, `self.assertEqual(output1, output2)` (REQ-06)
- `test_rendered_markdown_matches_golden_fixture` — `self.assertEqual(rendered, fixture_path.read_text(encoding="utf-8"))` (REQ-06)
- `test_rendered_markdown_has_yaml_frontmatter` — parse frontmatter block, assert presence of `anchor_id`/`anchor_kind`/`generated_at`/`scaffold_version` keys (REQ-05)
- `test_rendered_markdown_has_exactly_8_h2_sections` — regex `^## \d\. ` match count == 8 (REQ-05)
- `test_rendered_markdown_each_section_has_evidence_prompt_reasoning` — per-section substring check (REQ-05)

### Task 4 — `render_scaffold` entry point + citation selectors (REQ-07, REQ-13)

**Files:** `src/gzkit/justify/walkthrough.py` (extend), `tests/justify/test_walkthrough.py` (extend)

```python
def render_scaffold(
    anchor: AnchorRef,
    evidence: EvidenceBundle,
    now: datetime | None = None,
) -> Walkthrough:
    timestamp = (now or datetime.now(timezone.utc)).isoformat()
    sections = [
        _build_section(ordinal, anchor, evidence)
        for ordinal in range(1, 9)
    ]
    return Walkthrough(
        anchor=anchor,
        evidence=evidence,
        generated_at=timestamp,
        sections=sections,
    )
```

`_build_section(ordinal, anchor, evidence) -> WalkthroughSection` applies section-specific citation selection:

- **Section 1** → `_extract_anchor_body_citations(anchor.body)`. Regex-based extraction over `anchor.body` for identifiers matching `GHI-\d+`, `OBPI-\d+\.\d+\.\d+-\d+(?:-[a-z0-9-]+)?`, `ADR-\d+\.\d+\.\d+` (deduped, first-occurrence order). Empty list if `anchor.body is None`.
- **Section 7** → formatted strings from `evidence.matching_rules` + `evidence.ledger_events` + `evidence.recent_commits` (rule_id, `<event> <id>`, `<sha[:7]> <subject>` respectively).
- **Sections 2–6, 8** → `[]` (the brief only specifies 1 and 7; other sections carry empty citations plus the placeholder reasoning).

All sections receive `reasoning="_[To be filled]_"` and `prompt=SECTION_PROMPTS[ordinal]`.

Tests:

- `test_render_scaffold_builds_8_sections_with_placeholders` (REQ-07)
- `test_render_scaffold_section_1_extracts_anchor_body_citations` — anchor.body containing "See GHI-232 and sibling OBPI refs" yields identifiers as a list for section 1 (REQ-07)
- `test_render_scaffold_section_1_empty_when_body_is_none` (REQ-07)
- `test_render_scaffold_section_7_pulls_all_three_evidence_sources` — fixture bundle with 1 rule + 1 ledger event + 1 commit → section 7 has 3 citations (REQ-07)
- `test_render_scaffold_sections_2_through_6_and_8_have_empty_citations` (REQ-07)
- `test_render_scaffold_generated_at_uses_injected_now` — fixed `now=datetime(2026,1,1,tzinfo=UTC)` yields `"2026-01-01T00:00:00+00:00"` (REQ-07, REQ-13)

### Task 5 — CLI internal dispatch module (REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13)

**Files:** `src/gzkit/justify/cli.py` (new)

Internal pure-function entry point consumed by the command handler. Keeps `commands/justify_cmd.py` a thin wrapper so testing surface is local to `justify/cli.py`.

```python
ADR_REJECTION_MESSAGE = (
    "justify reasons about change instances (GHIs, OBPIs, drafts), "
    "not governance packages. Invoke on the tracking GHI or an OBPI under the ADR."
)
DRAFT_SLUG_REQUIRED_MESSAGE = (
    "--draft-slug is required when --save is combined with --draft"
)

_ADR_PATTERN = re.compile(r"^ADR-\d+\.\d+\.\d+$", re.IGNORECASE)

def handle_justify(
    *,
    anchor: str | None,
    save: bool,
    output: str | None,
    related: str | None,
    draft: str | None,
    draft_slug: str | None,
    now: datetime | None = None,
    project_root: Path | None = None,
) -> int:
    """Exit-code-returning dispatch for the justify subcommand."""
    # REQ-09: ADR rejection before anything else
    if anchor is not None and _ADR_PATTERN.match(anchor.strip()):
        print(ADR_REJECTION_MESSAGE, file=sys.stderr)
        return 1
    # REQ-10: --draft + --save ⇒ --draft-slug required
    if draft is not None and save and not draft_slug:
        print(DRAFT_SLUG_REQUIRED_MESSAGE, file=sys.stderr)
        return 1
    # REQ-11: --output path conflict check (pre-resolution)
    if output is not None and Path(output).exists():
        print(f"justify: output path already exists: {output}", file=sys.stderr)
        return 1
    # Require either anchor or draft
    if anchor is None and draft is None:
        print("justify: anchor or --draft is required", file=sys.stderr)
        return 1
    try:
        anchor_ref = resolve_anchor(
            anchor if draft is None else None,
            draft_text=draft,
            draft_slug=draft_slug,
            project_root=project_root,
        )
    except ValueError as exc:
        print(f"justify: {exc}", file=sys.stderr)
        return 1
    except AnchorResolutionError as exc:
        print(f"justify: {exc}", file=sys.stderr)
        return 2
    related_list = [r.strip() for r in related.split(",")] if related else None
    evidence = gather_evidence(anchor_ref, related=related_list, project_root=project_root)
    walkthrough = render_scaffold(anchor_ref, evidence, now=now)
    markdown = render_markdown(walkthrough)
    # Output routing — REQ-11
    if output is not None:
        try:
            Path(output).write_text(markdown, encoding="utf-8")
        except OSError as exc:
            print(f"justify: failed to write {output}: {exc}", file=sys.stderr)
            return 2
        return 0
    if save:
        slug = (draft_slug or anchor_ref.identifier or "draft").strip("/")
        stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
        target = (project_root or Path.cwd()) / "artifacts" / "justify" / f"{slug}-{stamp}.md"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(markdown, encoding="utf-8")
        except OSError as exc:
            print(f"justify: failed to write {target}: {exc}", file=sys.stderr)
            return 2
        return 0
    print(markdown)
    return 0
```

REQ-13 satisfied by construction: `handle_justify` accepts `now` as an injectable parameter; no direct LLM call anywhere.

### Task 6 — CLI command handler + tests (REQ-08 through REQ-13)

**Files:** `src/gzkit/commands/justify_cmd.py` (new), `tests/commands/test_justify_cmd.py` (new)

```python
def justify_cmd(
    *,
    anchor: str | None,
    save: bool = False,
    output: str | None = None,
    related: str | None = None,
    draft: str | None = None,
    draft_slug: str | None = None,
) -> int:
    """Produce a pre-execution reasoning scaffold for <anchor> or a draft."""
    return handle_justify(
        anchor=anchor, save=save, output=output,
        related=related, draft=draft, draft_slug=draft_slug,
    )
```

Tests (patch targets: `gzkit.justify.cli.resolve_anchor`, `gzkit.justify.cli.gather_evidence` — same mocking shape as OBPI-01 tests):

- `test_cli_adr_rejection_exit_1_and_exact_stderr` — run with `anchor="ADR-0.0.19"`, capture stderr, assert exact REQ-09 message (REQ-09)
- `test_cli_draft_with_save_missing_slug_exit_1` (REQ-10)
- `test_cli_output_path_exists_exit_1` — pre-create file in tempdir, pass `--output=<path>` (REQ-11)
- `test_cli_default_emits_scaffold_to_stdout` — mocked anchor+evidence, `capsys` check (REQ-08, REQ-11)
- `test_cli_save_writes_auto_path_under_artifacts_justify` — assert file exists at `artifacts/justify/GHI-232-<ts>.md` under temp `project_root` (REQ-11)
- `test_cli_explicit_output_writes_path` — `--output=<new path>` writes, exit 0 (REQ-11)
- `test_cli_related_passed_through_as_list` — inspect mocked `gather_evidence` call args (REQ-08)
- `test_cli_help_lists_anchor_and_all_flags` — parser help text includes `anchor`, `--save`, `--output`, `--related`, `--draft`, `--draft-slug`, at least one example, exit-code reference (REQ-11)
- `test_cli_deterministic_given_fixed_now` — two calls with same inputs + same `now` produce same output (REQ-13)
- `test_cli_exit_codes_follow_doctrine` — table-driven: ADR → 1, draft-slug missing → 1, AnchorResolutionError → 2, happy → 0 (REQ-12)

Tests use the canonical `unittest.mock.patch` pattern per `.gzkit/rules/tests.md` and `tempfile.TemporaryDirectory` for paths.

### Task 7 — Parser registration (extension only) (REQ-08, REQ-11, REQ-12)

**Files:** `src/gzkit/cli/parser_artifacts.py` (extend)

Append to `_LAZY_HANDLERS`:

```python
"justify_cmd": "gzkit.commands.justify_cmd",
```

Add a top-level `justify` subcommand registration (argparse subparser, same pattern as the `obpi precomplete` block at `parser_artifacts.py:512-532`):

```python
p_justify = commands.add_parser(
    "justify",
    help="Produce a pre-execution reasoning scaffold (8 sections) for an anchor",
    description="Scaffold reasoning for a GHI, OBPI, or draft anchor...",
    epilog=build_epilog([
        "Examples:",
        "  uv run gz justify GHI-232",
        "  uv run gz justify GHI-232 --save",
        "  uv run gz justify --draft 'proposal text' --save --draft-slug my-idea",
        "",
        "Exit codes: 0 success; 1 user/config error; 2 system/IO error.",
    ]),
)
p_justify.add_argument("anchor", nargs="?", default=None,
                      help="Anchor identifier (GHI-<N>, #<N>, OBPI-X.Y.Z-NN); omit with --draft")
p_justify.add_argument("--save", action="store_true",
                      help="Write scaffold to artifacts/justify/<slug>-<timestamp>.md")
p_justify.add_argument("--output", default=None,
                      help="Write scaffold to explicit path (must not exist)")
p_justify.add_argument("--related", default=None,
                      help="Comma-separated list of related anchors for evidence context")
p_justify.add_argument("--draft", default=None,
                      help="Literal draft text in place of a resolvable anchor")
p_justify.add_argument("--draft-slug", default=None,
                      help="Slug used to name the output file when --draft + --save are combined")
p_justify.set_defaults(func=lambda a: _lazy("justify_cmd")(
    anchor=a.anchor, save=a.save, output=a.output,
    related=a.related, draft=a.draft, draft_slug=a.draft_slug,
))
```

Registration is additive — no rewrite of `parser_artifacts.py` structure. Placement: top-level (not nested under `adr`/`obpi`). Parser constructed once via the existing `_get_parser()` cache.

### Task 8 — Package re-exports (REQ-07 exposure surface)

**Files:** `src/gzkit/justify/__init__.py` (extend)

Extend existing `__all__` from 6 to 9 names. Add import line for the three new names:

```python
from gzkit.justify.walkthrough import Walkthrough, WalkthroughSection, render_scaffold

__all__ = [
    "AnchorKind", "AnchorRef", "AnchorResolutionError",
    "EvidenceBundle", "resolve_anchor", "gather_evidence",
    "Walkthrough", "WalkthroughSection", "render_scaffold",
]
```

Per the local agent rule "When adding imports in an Edit call, always include the code that uses them in the same edit" — the `__init__.py` change ships in one Edit with both the import line and `__all__` extension.

### Task 9 — CLI audit stubs (Gate 3 unblock)

**Files:** `config/doc-coverage.json` (extend), `docs/user/commands/justify.md` (new stub), `docs/user/commands/index.md` (extend), `docs/user/manpages/justify.md` (new stub)

Minimum viable stubs — OBPI-05 supplies final text.

`config/doc-coverage.json` — add entry (key style matches existing flattened verbs):

```json
"justify": {
  "surfaces": {
    "manpage": true,
    "index_entry": true,
    "operator_runbook": false,
    "governance_runbook": false,
    "docstring": true
  },
  "governance_relevant": false
}
```

(If the existing audit also requires `operator_runbook: true`, fall back to that — OBPI-05 will flip it to populated runbook references. Set it false initially so the stub passes without touching the runbook, which is a Denied Path for this OBPI.)

`docs/user/commands/justify.md` — stub:

```markdown
# gz justify

Produce a pre-execution reasoning scaffold (8 sections) for a GHI, OBPI, or
draft anchor. See parent ADR-0.0.19 for the walkthrough protocol. Final
operator guidance ships in a later OBPI under this ADR.

## Usage

    uv run gz justify <anchor> [--save | --output PATH] [--related A,B] \
                      [--draft TEXT --draft-slug SLUG]

## Exit Codes

- 0 — scaffold produced successfully
- 1 — user/config error (bad anchor, ADR, missing --draft-slug, output exists)
- 2 — system/IO error (resolver failure, filesystem write failure)
```

`docs/user/manpages/justify.md` — stub with similar shape.

`docs/user/commands/index.md` — insert row under Governance table:

```markdown
| [`gz justify`](justify.md) | Produce a pre-execution reasoning scaffold |
```

### Task 10 — Verification (Stage 3 baseline + parity gate)

Run in this order:

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest-justify-02 -- \
    uv run -m unittest tests.justify.test_walkthrough tests.commands.test_justify_cmd
uv run python -m gzkit justify --help                 # REQ-11 help surface
uv run python -m gzkit justify ADR-0.0.19             # REQ-09 — expect exit 1
uv run python -m gzkit justify --draft "t" --save     # REQ-10 — expect exit 1
uv run gz cli audit                                   # Gate 3 — expect exit 0
uv run gz covers OBPI-0.0.19-02-scaffold-rendering --json   # @covers parity gate
```

All ARB receipts feed Stage 4 evidence per `.gzkit/rules/attestation-enrichment.md` canonical invocations.

## Files Touched (summary for scope contract)

**Created:**

- `src/gzkit/justify/walkthrough.py`
- `src/gzkit/justify/templates/__init__.py`
- `src/gzkit/justify/templates/walkthrough.md.j2`
- `src/gzkit/justify/cli.py`
- `src/gzkit/commands/justify_cmd.py`
- `tests/justify/test_walkthrough.py`
- `tests/justify/fixtures/walkthrough_expected.md`
- `tests/commands/test_justify_cmd.py`
- `docs/user/commands/justify.md`
- `docs/user/manpages/justify.md`

**Modified (additive only):**

- `src/gzkit/cli/parser_artifacts.py` — `_LAZY_HANDLERS` entry + new `justify` subparser block
- `src/gzkit/justify/__init__.py` — `__all__` extended by 3 names + one import line
- `config/doc-coverage.json` — new `"justify"` entry
- `docs/user/commands/index.md` — single row in the Governance table

All paths are within the brief's Allowed Paths list except the two stub doc paths (`docs/user/manpages/justify.md` and `docs/user/commands/index.md`) and `config/doc-coverage.json`. These three are Gate-3 audit prerequisites for Heavy lane — the brief marks `docs/user/commands/**`, `docs/user/manpages/**`, `features/**` as Denied under a narrow reading. Gate 3 explicitly states "A stub manpage + command doc are produced in this OBPI to unblock audit," which licenses the minimum stub set; `config/doc-coverage.json` is the mechanical manifest those stubs feed. **If the brief allowlist is read strictly, I will surface the tension to the operator before writing those files** — the alternative is to make CLI audit fail (`gz cli audit` non-zero on unknown verb), which violates Gate 3. Planned resolution: proceed with stubs + Gate-3-unblock justification; if the operator prefers tighter allowlist discipline, I will expand the brief allowlist first.

## Verification Plan (End-to-End)

1. **Unit level** — `uv run -m unittest tests.justify.test_walkthrough tests.commands.test_justify_cmd -v` — every REQ decorated with `@covers`.
2. **Parity gate** — `uv run gz covers OBPI-0.0.19-02-scaffold-rendering --json` shows `uncovered_reqs == 0`.
3. **Smoke — help & exit codes** — three CLI smoke invocations above, inspect stderr and `$?`.
4. **Smoke — rendered output** — mock-free invocation against a real local GHI the operator picks (e.g. `uv run gz justify GHI-288`) produces an 8-section scaffold written to stdout; visually inspect the first 30 lines as Key Proof.
5. **Audit** — `uv run gz cli audit` exits 0 with `justify` reported as covered.
6. **Golden fixture** — any future render drift fails `test_rendered_markdown_matches_golden_fixture`; byte-level stability enforced.

## Out of Scope (Explicit Reminder)

- Reverse parser (markdown → `Walkthrough`) — later OBPI
- Skill authoring for `gz-justify` skill — later OBPI
- Runbook entries + BDD scenarios + final manpage prose — later OBPI
- LLM integration — forbidden by REQ-13
