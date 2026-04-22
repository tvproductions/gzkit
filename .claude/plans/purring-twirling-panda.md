# OBPI-0.0.19-03 — `gz justify validate` reverse parser

## Context

ADR-0.0.19 ships a three-stage pipeline for pre-execution reasoning walkthroughs: **OBPI-01** delivered the anchor/evidence library substrate; **OBPI-02** delivered the 8-section `Walkthrough` Pydantic model and Jinja2-backed deterministic renderer (`render_markdown`). Operators can now scaffold a walkthrough (`gz justify GHI-232 --save`) and edit its `_[To be filled]_` blocks.

**OBPI-03** closes the round-trip. It adds `src/gzkit/justify/parser.py` (reverse parser: markdown → `Walkthrough`) and the new subverb `gz justify validate <file>` so downstream skills can mechanically assert a filled walkthrough is structurally complete before treating it as evidence. Exit codes are 4-code doctrine: `0` complete, `1` parseable-but-incomplete, `2` unparseable.

## Key design decisions

### 1. Restructure `gz justify` into a subverb group

`parser_artifacts.py` currently registers `gz justify` as a flat command with a single optional positional `anchor`. OBPI-03's brief says "register the `validate` subverb (extend, not rewrite)" and the allowed paths include `parser_artifacts.py`. The minimum-invasive restructure:

- `gz justify` becomes a group with subparsers (`scaffold`, `validate`).
- `gz justify scaffold [anchor] [--save] [--output] [--related] [--draft] [--draft-slug]` — preserves every current scaffold flag verbatim.
- `gz justify validate <file> [--json]` — new subverb.
- A top-level `anchor` positional on the `justify` parser is retained with a shim: when no subverb is given and `anchor` is present (or `--draft` is present), it dispatches to the scaffold handler. This keeps `gz justify GHI-232` and `gz justify --draft "..."` working as they do today.

This is safe because `docs/user/commands/**` and `docs/user/manpages/**` for `justify` are owned by OBPI-05 (denied here), so no operator-facing doc currently pins the flat form. Internal callers that pass through `justify_cmd` remain API-compatible — `justify_cmd` is extended with an optional `subverb` keyword that defaults to `None` (= scaffold).

### 2. Reverse parser (`parse_walkthrough`)

New module `src/gzkit/justify/parser.py`:

- `WalkthroughParseError(Exception)` — raised with a message naming the first failure location (line number + offending token), per REQ-04.
- `parse_walkthrough(markdown: str) -> Walkthrough` — strict parser with the order:
  1. Split leading YAML frontmatter (`---` / `---`). Missing frontmatter → `WalkthroughParseError`.
  2. Parse frontmatter (PyYAML, already in the dep tree via Jinja2/pydantic wiring — verify with `uv pip list`). Extract `anchor_id`, `anchor_kind`, `generated_at`, `scaffold_version`.
  3. Walk H2 headings in body in order. Assert exactly 8 sections; assert ordinals `[1..8]`; assert headings match `SECTION_HEADINGS`. Any violation → `WalkthroughParseError` with location.
  4. Per section, extract: `**Prompt:** *<prompt>*`, `**Evidence:**` block (bullets `- <cite>` OR the sentinel `- _(no citations for this section)_` = empty list), and the reasoning block (remaining non-whitespace text before the next H2 or EOF).
  5. Construct `WalkthroughSection` and `Walkthrough` instances — the existing Pydantic `@model_validator` fires as a second-line defense.

- **Tolerance (REQ-02):** blank lines between sections, trailing whitespace, and full-line `#`-style comments (e.g. `# note`) are skipped.
- **Strictness (REQ-02):** H2 ordinal order, frontmatter presence, and the three per-section sub-block markers (`**Prompt:**`, `**Evidence:**`, reasoning block) are mandatory.
- **Anchor/evidence reconstruction.** The template only serializes section content; the full `EvidenceBundle` is not recoverable from markdown. The parser reconstructs a minimal but valid `AnchorRef` (from `anchor_kind`, `anchor_id`) and a minimal `EvidenceBundle` (empty tuples for `matching_rules`, `ledger_events`, `recent_commits`, `related_anchors`, `warnings`; canonical `taxonomy_reference` constant). Round-trip fixtures (REQ-03) are authored with minimal evidence so `parse(render(w)) == w` holds exactly. This is consistent with the brief's test-fixture framing (three representative fixtures, not arbitrary Walkthroughs) and keeps `walkthrough.py`/templates untouched per the denied-paths list.
- **Side-effect discipline (REQ-10):** no network, no LLM, no file mutation — reads input once, returns result.

### 3. `ValidateResult` and CLI handler

New model in `parser.py`:

```python
class ValidateResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    file_path: str
    is_parseable: bool
    is_complete: bool
    unfilled_ordinals: list[int]
    parse_error: str | None
```

New handler in `src/gzkit/justify/cli.py`:

```python
def handle_validate(*, file: str, json_output: bool) -> int:
    ...
```

- Reads `file` as UTF-8; on `OSError` → exit 2 with "could not be parsed: <reason>".
- Calls `parse_walkthrough(text)`:
  - Success + `is_complete()` True → exit 0, stdout `Walkthrough <file> is complete`.
  - Success + not complete → exit 1, stdout `Walkthrough <file> is incomplete. Unfilled sections: N, N, N` (sorted ordinals).
  - `WalkthroughParseError` → exit 2, stdout `Walkthrough <file> could not be parsed: <message>`.
- `--json` flag emits a single serialized `ValidateResult` JSON object to stdout (no prose).
- Exit codes follow CLI doctrine: 0 / 1 / 2 (no 3).

### 4. Integration & re-exports

- `src/gzkit/justify/__init__.py` — re-export `parse_walkthrough`, `WalkthroughParseError`, `ValidateResult`.
- `src/gzkit/commands/justify_cmd.py` — accept `subverb: str | None = None` plus `file: str | None = None`, `json_output: bool = False`; dispatch to `handle_validate` when `subverb == "validate"`, else to `handle_justify` (existing behavior).
- `src/gzkit/cli/parser_artifacts.py` — the restructure described in § 1.

## Tests (TDD, one REQ at a time — RED → GREEN → next)

### `tests/justify/test_parser.py` (unit tier, REQs 01–04, 09–11)

- `@covers("REQ-0.0.19-03-01")` — filled walkthrough parses; `is_complete()` True.
- `@covers("REQ-0.0.19-03-02")` — round-trip over 3 fixtures (complete / one-unfilled / anchor-draft-kind).
- `@covers("REQ-0.0.19-03-03")` — missing frontmatter → `WalkthroughParseError` naming the line.
- `@covers("REQ-0.0.19-03-04")` — H2 out-of-order → `WalkthroughParseError` naming the heading.
- `@covers("REQ-0.0.19-03-05")` — wrong section count (7 or 9) → `WalkthroughParseError`.
- `@covers("REQ-0.0.19-03-09")` — `ValidateResult` Pydantic contract (frozen, extra="forbid", required fields).
- `@covers("REQ-0.0.19-03-11")` — section with reasoning `"I don't know"` is structurally complete.
- Tolerance tests: blank lines / trailing whitespace / `#` comment lines accepted.

### `tests/commands/test_justify_validate.py` (CLI tier, REQs 05–10, 12)

- `@covers("REQ-0.0.19-03-05")` — missing `<file>` positional → exit 1.
- `@covers("REQ-0.0.19-03-06")` — exit 0 + "is complete" on the complete fixture.
- `@covers("REQ-0.0.19-03-07")` — exit 1 + lists unfilled ordinals on the incomplete fixture.
- `@covers("REQ-0.0.19-03-08")` — exit 2 + parse error on the malformed fixture.
- `@covers("REQ-0.0.19-03-09")` — `--json` stdout parses; keys match `ValidateResult`.
- `@covers("REQ-0.0.19-03-10")` — `--help` lists exit codes 0/1/2 and an example.
- `@covers("REQ-0.0.19-03-12")` — `uv run gz cli audit` exits 0 (run in verification, not a unit test — asserted in brief-level verification).

CLI tests call `handle_validate()` directly (argparse harness pattern from `tests/commands/common.py`) for speed; one end-to-end `subprocess.run([..., "gz", "justify", "validate", ...])` smoke test per test file for the subverb registration.

### Fixtures (in-repo, allowed by brief)

- `tests/justify/fixtures/walkthrough_complete.md` — rendered via `render_markdown` from a Python-constructed `Walkthrough` with every reasoning block filled with deterministic prose.
- `tests/justify/fixtures/walkthrough_incomplete.md` — same, but sections 2, 5, 8 left as `_[To be filled]_`.
- `tests/justify/fixtures/walkthrough_malformed.md` — a hand-authored file with the 5th and 6th H2 swapped (ordinal order violation) — triggers REQ-04 path deterministically.

## Files to modify / create

**Create:**
- `src/gzkit/justify/parser.py`
- `tests/justify/test_parser.py`
- `tests/commands/test_justify_validate.py`
- `tests/justify/fixtures/walkthrough_complete.md`
- `tests/justify/fixtures/walkthrough_incomplete.md`
- `tests/justify/fixtures/walkthrough_malformed.md`

**Modify (extend, not rewrite):**
- `src/gzkit/justify/__init__.py` — add re-exports.
- `src/gzkit/justify/cli.py` — add `handle_validate`; keep `handle_justify` unchanged.
- `src/gzkit/commands/justify_cmd.py` — add `subverb` routing.
- `src/gzkit/cli/parser_artifacts.py` — restructure `_register_justify_parser` into a subparser group (scaffold + validate).

**Read-only reference:**
- `src/gzkit/justify/walkthrough.py` — `Walkthrough`, `WalkthroughSection`, `SECTION_HEADINGS`, `SECTION_PROMPTS`, `render_markdown` (the API the parser inverts).
- `src/gzkit/justify/templates/walkthrough.md.j2` — the rendering shape the parser matches.

## Verification (matches brief § Verification)

```bash
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest-justify-03 -- uv run -m unittest tests.justify.test_parser tests.commands.test_justify_validate
uv run gz test --obpi OBPI-0.0.19-03-validate-subcommand
uv run python -m gzkit justify validate --help

# Exit-code discipline (run against fixtures produced by the tests)
uv run python -m gzkit justify validate tests/justify/fixtures/walkthrough_complete.md;   test $? -eq 0
uv run python -m gzkit justify validate tests/justify/fixtures/walkthrough_incomplete.md; test $? -eq 1
uv run python -m gzkit justify validate tests/justify/fixtures/walkthrough_malformed.md;  test $? -eq 2

# REQ → @covers parity
uv run gz covers OBPI-0.0.19-03-validate-subcommand --json

# Gate 3 (Heavy-lane)
uv run gz cli audit
```

## Risk / non-obvious notes

- **`gz justify GHI-232` backward compatibility.** The subverb restructure keeps the bare anchor form working via a dispatch shim; covered by extending existing scaffold tests (if any) or authoring a thin test in `tests/commands/test_justify_cmd.py` — but that file is under OBPI-02's scope. The shim will live inside the `set_defaults(func=...)` lambda of the top-level `justify` parser: if `a.subverb is None and (a.anchor or a.draft)`, call the scaffold path. No OBPI-02-owned file is modified.
- **`taxonomy_reference` reconstruction.** The canonical constant used by the parser must match what OBPI-01's `gather_evidence` writes. Read `src/gzkit/justify/evidence.py` at implementation time and cache the exact string; any mismatch breaks round-trip equality.
- **Fixtures are generated at test setup, not committed as hand-authored markdown, where possible.** The complete/incomplete fixtures are produced by `render_markdown` at `setUpClass` to avoid drift with the template — committed files under `tests/justify/fixtures/` are written once and re-asserted by a byte-equality check (catches template drift early). The malformed fixture is hand-authored because its shape is intentionally invalid.
