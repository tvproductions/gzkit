---
id: OBPI-0.0.19-03-validate-subcommand
parent: ADR-0.0.19
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.19-03-validate-subcommand: Validate subcommand (reverse parser)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md`
- **Checklist Item:** #3 — Validate subcommand. `gzkit justify validate <file>` reverse-parses markdown to `Walkthrough`; `is_complete()` structural check; `--json` output; exit codes 0 complete / 1 incomplete / 2 unparseable per CLI doctrine 4-code map.

**Status:** Draft

## Objective

Add the `validate` subcommand that closes the rendering/parsing round-trip. This OBPI ships `src/gzkit/justify/parser.py` — a reverse parser that consumes a filled-in markdown walkthrough (produced by OBPI-02's renderer and subsequently edited by agent or operator to fill `_[To be filled]_` blocks) and reconstructs a `Walkthrough` Pydantic instance. The subcommand `gzkit justify validate <file>` invokes the parser and reports structural completeness via `Walkthrough.is_complete()`. Exit codes follow the CLI doctrine. When this OBPI lands, downstream skills can cite a saved walkthrough and assert it is structurally complete before treating it as evidence.

## Lane

**Heavy** — Adds a new CLI subcommand verb (`validate`) under the `justify` parent, with exit-code semantics that downstream skills will depend on.

> Heavy is reserved for command/API/schema/runtime-contract changes.

## Allowed Paths

- `src/gzkit/justify/parser.py` — reverse parser: markdown + YAML frontmatter → `Walkthrough`
- `src/gzkit/justify/cli.py` — extend the existing subcommand dispatcher with the `validate` subverb
- `src/gzkit/commands/justify_cmd.py` — extend to route `validate` to the new handler
- `src/gzkit/cli/parser_artifacts.py` — register the `validate` subverb (extend, not rewrite)
- `src/gzkit/justify/__init__.py` — re-export `parse_walkthrough`, `ValidateResult`
- `tests/justify/test_parser.py` — reverse parser unit tests
- `tests/commands/test_justify_validate.py` — CLI subverb tests
- `tests/justify/fixtures/walkthrough_complete.md` — a filled, structurally-complete walkthrough fixture
- `tests/justify/fixtures/walkthrough_incomplete.md` — a partially-filled fixture (some sections still `_[To be filled]_`)
- `tests/justify/fixtures/walkthrough_malformed.md` — a malformed fixture (missing section, bad frontmatter)
- `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md` — parent ADR (read-only)

## Denied Paths

- `src/gzkit/justify/anchors.py`, `src/gzkit/justify/evidence.py`, `src/gzkit/justify/models.py` — owned by OBPI-01
- `src/gzkit/justify/walkthrough.py`, `src/gzkit/justify/templates/**` — owned by OBPI-02
- `.gzkit/skills/**` — owned by OBPI-04
- `docs/user/commands/**`, `docs/user/manpages/**`, `features/**`, `docs/user/runbook.md` — owned by OBPI-05
- Any file mutation outside Allowed Paths
- New third-party dependencies (stdlib + existing PyYAML via Jinja2 or existing YAML dependency is sufficient)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `parse_walkthrough(markdown: str) -> Walkthrough` consumes a filled markdown string produced by OBPI-02's renderer and returns a `Walkthrough` Pydantic instance. Parsing order: (a) extract YAML frontmatter delimited by `---` / `---`; (b) walk H2 headings in order; (c) for each section, extract `**Evidence:**` bullet list, `**Prompt:**` line, and reasoning block; (d) construct `WalkthroughSection` instances; (e) construct and return the `Walkthrough` (which auto-validates per OBPI-02's `@model_validator`).
2. REQUIREMENT: The parser is tolerant of trailing whitespace, one or more blank lines between sections, and `#`-style comments. It is STRICT about H2 heading order, YAML frontmatter presence, and the three sub-block markers (`**Evidence:**`, `**Prompt:**`, plus the reasoning block).
3. REQUIREMENT: The parser is the inverse of OBPI-02's renderer for structurally valid inputs. Round-trip property: `parse_walkthrough(render(walkthrough)) == walkthrough` for every `Walkthrough` instance. Verified by a property-based test over representative fixtures.
4. REQUIREMENT: Unparseable input raises `WalkthroughParseError` with a message naming the first failure location (line number and token). Examples: missing frontmatter, H2 heading order violation, missing sub-block marker, section count ≠ 8.
5. REQUIREMENT: The CLI subverb is invoked as `uv run -m gzkit justify validate <file>`. Positional `<file>` is required; absence yields exit 1. `--json` flag emits a structured JSON report to stdout.
6. REQUIREMENT: `ValidateResult` is a Pydantic `BaseModel` with `model_config = ConfigDict(frozen=True, extra="forbid")`. Fields: `file_path: str`, `is_parseable: bool`, `is_complete: bool`, `unfilled_ordinals: list[int]`, `parse_error: str | None`. Emitted as JSON when `--json` is passed.
7. REQUIREMENT: Default (non-`--json`) output is human-readable: "Walkthrough `<file>` is complete" on exit 0; "Walkthrough `<file>` is incomplete. Unfilled sections: 1, 2, 5" on exit 1; "Walkthrough `<file>` could not be parsed: <reason>" on exit 2.
8. REQUIREMENT: Exit codes follow the CLI doctrine 4-code map: `0` parseable AND complete (all 8 sections filled), `1` parseable but incomplete (lists unfilled ordinals), `2` unparseable (system/format error), `3` not used by this subverb.
9. REQUIREMENT: `is_complete` check is strictly structural: a section with `reasoning="I don't know"` passes the check. The docstring for `ValidateResult` and the subverb's `--help` text explicitly state this — callers that want semantic judgment must use other tooling.
10. REQUIREMENT: The parser NEVER calls an LLM, NEVER makes network requests, NEVER mutates the input file. It reads the input once and produces a result.
11. REQUIREMENT: Unit tests cover every REQ. Each test pins a REQ identifier. Fixtures live under `tests/justify/fixtures/` and represent: one complete walkthrough, one incomplete with identified unfilled ordinals, one malformed with an expected parse-error substring.
12. REQUIREMENT: CLI subverb tests invoke `uv run python -m gzkit justify validate <fixture-path>` via subprocess or direct `argparse` harness and assert exit codes + stdout content. Subprocess tests use `tempfile.TemporaryDirectory` for output isolation.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.gzkit/rules/cli.md` — CLI contract doctrine (4-code exit map)
- [ ] `.gzkit/rules/models.md` — Pydantic policy
- [ ] `.gzkit/rules/tests.md` — roundtrip test pattern, fixture isolation
- [ ] Parent ADR — full context

**Context:**

- [ ] OBPI-0.0.19-02 brief + its delivered `Walkthrough` + renderer
- [ ] `src/gzkit/justify/walkthrough.py` (from OBPI-02) — reference model

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01 and OBPI-02 complete and merged
- [ ] `src/gzkit/justify/walkthrough.py` exposes `Walkthrough`, `WalkthroughSection`, `SECTION_HEADINGS`, `render` — the API this OBPI inverts
- [ ] `src/gzkit/cli/parser_artifacts.py` has the parent subcommand registered (from OBPI-02)

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/validate_frontmatter.py` — exemplar for YAML frontmatter parsing
- [ ] `src/gzkit/frontmatter_cmd.py` or similar — existing YAML roundtrip code for inspiration
- [ ] `tests/commands/common.py` — CLI test harness helpers

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief REQ-IDs, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Roundtrip test passes against at least three representative `Walkthrough` fixtures

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] `uv run gz cli audit` exits 0 with the new subverb covered. Manpage + command-doc stub updates land in this OBPI; final text in OBPI-05.

### Gate 4: BDD (Heavy only)

- [ ] No BDD scenarios in this OBPI; deferred to OBPI-05.

### Gate 5: Human (Heavy only)

- [ ] Human attestation deferred to ADR-level closeout per lane inheritance protocol.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest-justify-03 -- uv run -m unittest tests.justify.test_parser tests.commands.test_justify_validate

# Subverb smoke check (no anchor resolution — just argparse)
uv run python -m gzkit justify validate --help

# Exit-code discipline checks against fixtures
uv run python -m gzkit justify validate tests/justify/fixtures/walkthrough_complete.md; test $? -eq 0
uv run python -m gzkit justify validate tests/justify/fixtures/walkthrough_incomplete.md; test $? -eq 1
uv run python -m gzkit justify validate tests/justify/fixtures/walkthrough_malformed.md; test $? -eq 2

# JSON output structure check
uv run python -m gzkit justify validate tests/justify/fixtures/walkthrough_incomplete.md --json | uv run python -c "import json, sys; d = json.loads(sys.stdin.read()); assert set(d) >= {'file_path','is_parseable','is_complete','unfilled_ordinals'}"
```

## Acceptance Criteria

- [ ] REQ-0.0.19-03-01: Given a markdown walkthrough produced by OBPI-02's renderer and subsequently edited to fill every `_[To be filled]_` block, when `parse_walkthrough(markdown)` runs, then a `Walkthrough` instance is returned whose `is_complete()` is `True`.
- [ ] REQ-0.0.19-03-02: Given a `Walkthrough` instance, when rendered and then re-parsed, then the parsed instance equals the original (`parse_walkthrough(render(w)) == w`). Verified across at least three fixtures.
- [ ] REQ-0.0.19-03-03: Given a markdown file missing YAML frontmatter, when `parse_walkthrough` runs, then `WalkthroughParseError` is raised with a message naming the missing frontmatter.
- [ ] REQ-0.0.19-03-04: Given a markdown file with H2 headings out of ordinal order, when `parse_walkthrough` runs, then `WalkthroughParseError` is raised naming the offending heading.
- [ ] REQ-0.0.19-03-05: Given a markdown file with 7 or 9 H2 sections, when `parse_walkthrough` runs, then `WalkthroughParseError` is raised naming the section count mismatch.
- [ ] REQ-0.0.19-03-06: Given `uv run -m gzkit justify validate tests/justify/fixtures/walkthrough_complete.md`, when the command runs, then exit code is 0, stdout contains "is complete", and no error appears on stderr.
- [ ] REQ-0.0.19-03-07: Given `uv run -m gzkit justify validate tests/justify/fixtures/walkthrough_incomplete.md`, when the command runs, then exit code is 1, stdout lists unfilled ordinals matching the fixture's known-unfilled sections, and no exception trace appears.
- [ ] REQ-0.0.19-03-08: Given `uv run -m gzkit justify validate tests/justify/fixtures/walkthrough_malformed.md`, when the command runs, then exit code is 2 and stdout contains the first parse-error message.
- [ ] REQ-0.0.19-03-09: Given the `--json` flag, when `validate` runs on any fixture, then stdout contains a single JSON object matching the `ValidateResult` schema (keys: `file_path`, `is_parseable`, `is_complete`, `unfilled_ordinals`, `parse_error`).
- [ ] REQ-0.0.19-03-10: Given `uv run -m gzkit justify validate --help`, when argparse renders help, then exit-code meanings (0/1/2) are documented in the help text alongside examples.
- [ ] REQ-0.0.19-03-11: Given a section whose reasoning is `"I don't know"`, when the walkthrough is parsed, then `is_filled` on that section is `True` and `is_complete()` at the walkthrough level returns `True` — structural-only semantics explicitly tested.
- [ ] REQ-0.0.19-03-12: Given `uv run gz cli audit`, when it runs after this OBPI lands, then it exits 0 with the new subverb covered across manpage (stub acceptable) and command doc.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from REQ-IDs, roundtrip property verified
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Filled walkthroughs can be validated structurally by downstream tooling
- [ ] **Key Proof:** Output of `validate` against all three fixtures pasted in Evidence with their exit codes
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste `gz cli audit` output
```

### Gate 4 (BDD)

Not applicable at this OBPI; deferred to OBPI-05.

### Gate 5 (Human)

Deferred to ADR-level closeout.

### Value Narrative

**Before:** A filled walkthrough on disk is opaque to tooling — downstream skills that want to cite a walkthrough as evidence cannot assert it is structurally complete without ad-hoc grep.

**After:** `uv run -m gzkit justify validate <file>` returns a typed `ValidateResult` with deterministic exit codes. Downstream skills (e.g. a future integration test or a `gz-adr-evaluate` integration) can cite walkthroughs with confidence.

### Key Proof


$ uv run python -m gzkit justify validate tests/justify/fixtures/walkthrough_complete.md
Walkthrough tests/justify/fixtures/walkthrough_complete.md is complete
# exit 0

$ uv run python -m gzkit justify validate tests/justify/fixtures/walkthrough_incomplete.md
Walkthrough tests/justify/fixtures/walkthrough_incomplete.md is incomplete. Unfilled sections: 2, 5, 8
# exit 1

$ uv run python -m gzkit justify validate tests/justify/fixtures/walkthrough_malformed.md
Walkthrough tests/justify/fixtures/walkthrough_malformed.md could not be parsed: line 10: heading ordinal 2 out of order; expected 1
# exit 2

Receipts: lint arb-ruff-19a0e38bde354f3fb681a0900f8d9af6; types arb-step-typecheck-926e79f68616460aa8fe27fb8376ec8d; tests arb-step-unittest-justify-03-dcec6917f7494b6db188d9d38e172879.

### Implementation Summary


- Files created: src/gzkit/justify/parser.py; tests/justify/test_parser.py; tests/commands/test_justify_validate.py; three fixtures under tests/justify/fixtures/
- Files modified: src/gzkit/justify/__init__.py (re-exports); src/gzkit/justify/cli.py (added handle_validate); src/gzkit/commands/justify_cmd.py (subverb routing); src/gzkit/cli/parser_artifacts.py (registered validate via positional-based dispatch, backward-compatible with gz justify <anchor>)
- Tests added: 36 OBPI-scoped unit + CLI tests (22 parser + 14 CLI); 100% REQ parity (12/12) via gz covers OBPI-0.0.19-03; OBPI-02 regression suite (16/16) still green
- Date completed: 2026-04-22
- Attestation status: OBPI-level self-close under Heavy-lane inheritance; Gate 5 human attestation deferred to ADR-0.0.19 closeout
- Defects noted: Brief Gate 3 bullet (manpage + command-doc stub updates land here) contradicts Denied Paths; honored denied paths — manpage, command doc, runbook, and BDD land in OBPI-05. REQ-12 (gz cli audit) satisfied via existing AST handler resolution; no docs stubs written in this OBPI.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: proceed — Heavy-lane OBPI-level closure under lane inheritance; Gate 5 human attestation deferred to ADR-0.0.19 closeout. Parser + validate subverb land with 100% REQ parity (12/12), 36/36 OBPI-scoped tests pass (22 parser + 14 CLI incl. subprocess smoke + fixture drift guard), Gate 3 cli-audit + mkdocs strict build pass, no regressions in OBPI-02 (16/16). Receipts: lint arb-ruff-19a0e38bde354f3fb681a0900f8d9af6; types arb-step-typecheck-926e79f68616460aa8fe27fb8376ec8d; tests arb-step-unittest-justify-03-dcec6917f7494b6db188d9d38e172879. Flagged: brief Gate 3 bullet conflicts with Denied Paths — docs stubs deferred to OBPI-05 which owns the surface.
- Date: 2026-04-22

---

**Brief Status:** Completed

**Date Completed:** 2026-04-22

**Evidence Hash:** -
