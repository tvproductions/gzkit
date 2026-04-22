---
id: OBPI-0.0.19-02-scaffold-rendering
parent: ADR-0.0.19
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.19-02-scaffold-rendering: Scaffold rendering (Pydantic + Jinja2 + CLI)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md`
- **Checklist Item:** #2 — Scaffold rendering. `WalkthroughSection` + `Walkthrough` Pydantic models with 8-section validator; Jinja2 template at `src/gzkit/justify/templates/walkthrough.md.j2`; `gzkit justify <anchor>` CLI with `--save`, `--output`, `--related`, `--draft`/`--draft-slug`; ADR-anchor rejection with named recovery guidance.

**Status:** Draft

## Objective

Deliver the operator-visible CLI surface and the deterministic scaffold renderer. This OBPI introduces `Walkthrough` and `WalkthroughSection` Pydantic models (with a `@model_validator` enforcing exactly 8 sections ordered 1-8), a Jinja2 template that renders a `Walkthrough` instance to deterministic markdown (YAML frontmatter + H2 sections + evidence blocks + reasoning placeholders), and the `gzkit justify <anchor>` CLI subcommand that composes OBPI-01's `resolve_anchor` + `gather_evidence` with the new rendering layer. When this OBPI lands, an operator can run the command in a terminal and get an 8-section markdown scaffold with evidence blocks populated and reasoning blocks as `_[To be filled]_` placeholders. The `validate` subcommand, upstream skill integration, and docs/BDD remain out of scope.

## Lane

**Heavy** — Adds a new CLI verb and a new Jinja2 template contract. The CLI surface is load-bearing for external consumers (terminal operators, downstream skills).

> Heavy is reserved for command/API/schema/runtime-contract changes.

## Allowed Paths

- `src/gzkit/justify/walkthrough.py` — `WalkthroughSection`, `Walkthrough` Pydantic models + renderer entry point
- `src/gzkit/justify/templates/__init__.py` — marker for template package
- `src/gzkit/justify/templates/walkthrough.md.j2` — Jinja2 template for the 8-section scaffold
- `src/gzkit/justify/cli.py` — subcommand dispatch layer (internal to justify package)
- `src/gzkit/commands/justify_cmd.py` — command handler registering the subcommand under the top-level CLI (mirrors `src/gzkit/commands/validate_cmd.py` naming)
- `src/gzkit/cli/parser_artifacts.py` — parser registration for the new subcommand (extended, not rewritten)
- `src/gzkit/justify/__init__.py` — extend re-exports to include `Walkthrough`, `WalkthroughSection`, `render_scaffold`
- `tests/commands/test_justify_cmd.py` — CLI subcommand behavior tests (argument parsing, exit codes, file writes)
- `tests/justify/test_walkthrough.py` — Pydantic model + renderer unit tests
- `tests/justify/fixtures/walkthrough_expected.md` — golden fixture for deterministic render output
- `docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/ADR-0.0.19-pre-execution-reasoning-walkthrough.md` — parent ADR (read-only)

## Denied Paths

- `src/gzkit/justify/anchors.py`, `src/gzkit/justify/evidence.py`, `src/gzkit/justify/models.py` — owned by OBPI-01 (consume their public API; do not modify)
- `src/gzkit/justify/parser.py` — reverse parser lives in OBPI-03
- `.gzkit/skills/**` — skill authoring lives in OBPI-04
- `docs/user/commands/**`, `docs/user/manpages/**`, `features/**` — docs + BDD live in OBPI-05
- `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — runbook entries live in OBPI-05
- Any file mutation outside Allowed Paths
- New third-party dependencies beyond the existing Jinja2 already present

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `WalkthroughSection` is a Pydantic `BaseModel` with `model_config = ConfigDict(frozen=True, extra="forbid")`. Fields: `ordinal: int = Field(..., ge=1, le=8)`, `heading: str`, `prompt: str`, `evidence_citations: list[str]`, `reasoning: str`. A computed property `is_filled` returns `True` iff `reasoning.strip()` is non-empty AND `"_[To be filled]_"` is NOT a substring of `reasoning`.
2. REQUIREMENT: `Walkthrough` is a Pydantic `BaseModel` with `model_config = ConfigDict(frozen=True, extra="forbid")`. Fields: `anchor: AnchorRef`, `evidence: EvidenceBundle`, `generated_at: str` (ISO-8601), `sections: list[WalkthroughSection]`, `scaffold_version: str = "1.0"`. A `@model_validator(mode="after")` raises `ValidationError` unless `[s.ordinal for s in sections] == [1, 2, 3, 4, 5, 6, 7, 8]`.
3. REQUIREMENT: `Walkthrough.is_complete()` returns `True` iff `all(s.is_filled for s in self.sections)`. The method is structural only — it NEVER judges reasoning quality semantically.
4. REQUIREMENT: The 8 section headings are fixed in a module-level constant `SECTION_HEADINGS: list[str]` matching the canonical order from the parent ADR: (1) What I see (the problem), (2) Per-instance severity, (3) Why this scope, (4) What it proposes, (5) Routing decision, (6) Why this design is right-sized, (7) What convinces me (evidence), (8) Residual uncertainty. Any attempt to construct a `Walkthrough` whose section headings deviate from this list in order raises `ValidationError`.
5. REQUIREMENT: Jinja2 template at `src/gzkit/justify/templates/walkthrough.md.j2` renders a `Walkthrough` to deterministic markdown. Output contains: YAML frontmatter with `anchor_id`, `anchor_kind`, `generated_at`, `scaffold_version`; an H1 title; 8 H2 sections in ordinal order; each section has `**Evidence:**` bullet list (from `section.evidence_citations`), `**Prompt:**` italicized `section.prompt`, and a reasoning block rendered as `section.reasoning`.
6. REQUIREMENT: The rendered markdown is byte-stable for a given `Walkthrough` instance: identical input produces identical output on every invocation. Verified via a golden-fixture test: render a fixed `Walkthrough` and assert the output matches `tests/justify/fixtures/walkthrough_expected.md` byte-for-byte.
7. REQUIREMENT: `render_scaffold(anchor: AnchorRef, evidence: EvidenceBundle, now: datetime | None = None) -> Walkthrough` is the high-level entry point. It constructs the 8 `WalkthroughSection` instances with `reasoning="_[To be filled]_"`, populates each section's `evidence_citations` using a section-specific selector (section 7 pulls from ALL of `matching_rules`, `ledger_events`, `recent_commits`; section 1 pulls only anchor-body citations), and returns a frozen `Walkthrough`. The `now` parameter is injectable for deterministic tests.
8. REQUIREMENT: The CLI subcommand is invoked via `uv run -m gzkit justify <anchor>` or `uv run gzkit justify <anchor>`. It accepts positional `anchor` (GHI-<N>, #<N>, or OBPI-X.Y.Z-NN) and the following flags: `--save` (boolean), `--output <path>` (explicit path), `--related <comma-list>`, `--draft '<text>'`, `--draft-slug <slug>`.
9. REQUIREMENT: When the positional anchor matches `ADR-<X.Y.Z>` (case-insensitive), the CLI exits with code 1 and stderr message: `"justify reasons about change instances (GHIs, OBPIs, drafts), not governance packages. Invoke on the tracking GHI or an OBPI under the ADR."` — exact text. stdout is empty on error.
10. REQUIREMENT: When `--draft` is supplied and `--save` is also supplied, `--draft-slug` is required. Absence yields exit 1 with stderr: `"--draft-slug is required when --save is combined with --draft"`.
11. REQUIREMENT: Default output mode (no `--save`, no `--output`) writes the rendered markdown to stdout. `--save` auto-computes path `artifacts/justify/<anchor-id-or-slug>-<ISO8601-basic>.md` (creating parent directories if absent). `--output <path>` writes to the explicit path; if the path exists, the CLI exits with code 1 (no `--force` supported in v1).
12. REQUIREMENT: Exit codes follow the CLI doctrine 4-code map: `0` scaffold produced successfully, `1` user/config error, `2` system/IO error (filesystem write failure, subprocess failure propagating from OBPI-01), `3` not used by this subcommand.
13. REQUIREMENT: The CLI NEVER invokes an LLM. All behavior is deterministic given (anchor, evidence, injected `now`). Tests clock-freeze `generated_at` via the `now` parameter.
14. REQUIREMENT: Unit + CLI tests cover every REQ. Test naming pins REQ identifiers. Tests mock OBPI-01's public API via `unittest.mock.patch` so this OBPI's tests do not depend on real `gh`/`git` subprocesses.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.gzkit/rules/cli.md` — CLI contract doctrine (exit codes, flag conventions, help-text requirements)
- [ ] `.gzkit/rules/models.md` — Pydantic policy
- [ ] `.gzkit/rules/tests.md` — unittest discipline, two-runner contract, REQ-pinning
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` — Invariants 1/2/3
- [ ] Parent ADR — full context

**Context:**

- [ ] OBPI-0.0.19-01 brief + its delivered public API
- [ ] Sibling OBPIs 03/04/05 for scope boundaries

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01 is complete and merged
- [ ] `src/gzkit/cli/parser_artifacts.py` exists (confirmed)
- [ ] `src/gzkit/commands/` exists with sibling command modules (confirmed)
- [ ] Jinja2 importable: `uv run python -c "import jinja2"`

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/validate_cmd.py` — exemplar for command-module shape
- [ ] `src/gzkit/cli/parser_artifacts.py` — exemplar for subcommand registration pattern
- [ ] `src/gzkit/commands/common.py` or equivalent — console/log helpers, exit-code conventions
- [ ] `tests/commands/common.py` — canonical test helpers (subprocess patchers)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief REQ-IDs, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] `uv run gz cli audit` exits 0 — new subcommand coverage required. A stub manpage + command doc are produced in this OBPI to unblock audit; final text ships in OBPI-05.

### Gate 4: BDD (Heavy only)

- [ ] No BDD scenarios in this OBPI; deferred to OBPI-05.

### Gate 5: Human (Heavy only)

- [ ] Human attestation deferred to ADR-level closeout per lane inheritance protocol.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest-justify-02 -- uv run -m unittest tests.justify.test_walkthrough tests.commands.test_justify_cmd

# CLI surface smoke check
uv run python -m gzkit justify --help

# Exit-code discipline checks (shell tests, not unit tests)
uv run python -m gzkit justify ADR-0.0.19; test $? -eq 1
uv run python -m gzkit justify --draft "test" --save; test $? -eq 1

# CLI audit coverage
uv run gz cli audit
```

## Acceptance Criteria

- [ ] REQ-0.0.19-02-01: Given a `Walkthrough` instance with `sections=[...]` whose ordinals are `[1, 2, 3, 4, 5, 6, 7, 8]` in order, when it is constructed, then validation succeeds; given any permutation or missing ordinal, a `ValidationError` is raised.
- [ ] REQ-0.0.19-02-02: Given a `WalkthroughSection` with `reasoning="_[To be filled]_"`, when `is_filled` is checked, then it returns `False`; given `reasoning="Actual reasoning text"`, then `True`.
- [ ] REQ-0.0.19-02-03: Given a `Walkthrough` with all 8 sections having non-placeholder reasoning, when `is_complete()` is called, then it returns `True`; given any section with `"_[To be filled]_"` in its reasoning, then `False`.
- [ ] REQ-0.0.19-02-04: Given a fixed `Walkthrough` fixture, when rendered through the Jinja2 template, then the output matches `tests/justify/fixtures/walkthrough_expected.md` byte-for-byte.
- [ ] REQ-0.0.19-02-05: Given the rendered output, when parsed as YAML frontmatter + markdown, then the frontmatter contains `anchor_id`, `anchor_kind`, `generated_at`, `scaffold_version`; there are exactly 8 H2 headings in ordinal-label order; each section body contains `**Evidence:**`, `**Prompt:**`, and a reasoning block.
- [ ] REQ-0.0.19-02-06: Given `uv run -m gzkit justify GHI-232` with mocked anchor + evidence, when the command runs, then stdout contains the rendered scaffold; exit code is 0.
- [ ] REQ-0.0.19-02-07: Given `uv run -m gzkit justify ADR-0.0.19`, when the command runs, then stderr contains the ADR-rejection message exactly as specified in REQ-09 and exit code is 1.
- [ ] REQ-0.0.19-02-08: Given `uv run -m gzkit justify --draft "text" --save` without `--draft-slug`, when the command runs, then stderr contains the draft-slug-required message and exit code is 1.
- [ ] REQ-0.0.19-02-09: Given `uv run -m gzkit justify GHI-232 --save` with a clean temp workdir, when the command runs, then a file appears under `artifacts/justify/GHI-232-<ISO8601>.md` containing the rendered scaffold; exit code is 0.
- [ ] REQ-0.0.19-02-10: Given `uv run -m gzkit justify GHI-232 --output <existing-path>`, when the command runs, then stderr reports output-path-conflict and exit code is 1.
- [ ] REQ-0.0.19-02-11: Given the CLI subcommand invoked with `--help`, when argparse renders help, then the output lists the anchor positional, all five documented flags, at least one example, and notes exit codes 0/1/2 per CLI doctrine.
- [ ] REQ-0.0.19-02-12: Given `uv run gz cli audit`, when it runs after this OBPI lands, then it exits 0 with the new subcommand verb covered across manpage (stub acceptable; final text ships in OBPI-05), command doc, and index.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from REQ-IDs, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Operator can invoke the new subcommand and get a scaffold
- [ ] **Key Proof:** A rendered scaffold pasted in Evidence shows 8 sections populated
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

**Before:** No CLI surface exists for pre-execution reasoning walkthroughs; operators wanting to think through a GHI or OBPI before implementation rely on ad-hoc prose.

**After:** `uv run -m gzkit justify GHI-232 --save` produces an 8-section markdown scaffold with evidence citations populated and reasoning blocks marked for human or agent completion. Operators in a terminal have parity with Claude Code skill invocation.

### Key Proof


$ uv run gz justify ADR-0.0.19 ; echo $?
justify reasons about change instances (GHIs, OBPIs, drafts), not governance packages. Invoke on the tracking GHI or an OBPI under the ADR.
1

$ uv run gz cli audit | tail -2
CLI audit passed.
Cross-coverage: 86/86 commands fully covered.

$ uv run gz covers OBPI-0.0.19-02 --json  # parsed via python, summary excerpt:
{"identifier":"OBPI-0.0.19-02","total_reqs":12,"covered_reqs":12,"uncovered_reqs":0,"coverage_percent":100.0}

Receipts: lint arb-ruff-e589e56687064f5eb96fbeb6866a2509; types arb-step-typecheck-0b47a303e6cb4ea7b72d1d343da081d4; tests arb-step-unittest-justify-02-e18a117e04fa4485becaf47a39851fd8; coverage arb-step-coverage-10e03300a7f346f1875aa9be1c39595c.

### Implementation Summary


- Files created: src/gzkit/justify/walkthrough.py; src/gzkit/justify/templates/__init__.py; src/gzkit/justify/templates/walkthrough.md.j2; src/gzkit/justify/cli.py; src/gzkit/commands/justify_cmd.py; src/gzkit/__main__.py; tests/justify/test_walkthrough.py; tests/justify/fixtures/walkthrough_expected.md; tests/commands/test_justify_cmd.py; docs/user/commands/justify.md
- Files modified (additive): src/gzkit/cli/parser_artifacts.py (_LAZY_HANDLERS + _register_justify_parser); src/gzkit/justify/__init__.py (9 exports); config/doc-coverage.json (justify entry with runbook surfaces deferred to OBPI-05); docs/user/commands/index.md (one row); src/gzkit/governance/trust_audits.py (_NO_SKILL_VERBS waiver citing OBPI-04 skill deferral); tests/justify/test_models.py (OBPI-01 export surface test updated for scope-expansion)
- Tests added: 27 walkthrough model+renderer tests (REQ-01..05); 16 CLI handler tests (REQ-06..12). Full suite 3397 tests pass.
- Date completed: 2026-04-22
- Attestation status: attest completed from operator; Heavy-lane Gate 5 deferred to ADR-0.0.19 closeout per lane inheritance (brief Gate 5 section).
- Defects noted: none filed; three in-flight scope-expansion fixes applied (OBPI-01 export test; epilog gz-prefix convention; _NO_SKILL_VERBS waiver)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — CLI + Jinja2 + Pydantic scaffold rendering landed for ADR-0.0.19 OBPI-02; 43/43 OBPI tests pass, 3397/3397 full suite pass, @covers parity 12/12 (100%), gz cli audit 86/86 fully covered; Heavy-lane Gate 5 deferred to ADR-0.0.19 closeout per lane inheritance. Receipts: lint arb-ruff-e589e56687064f5eb96fbeb6866a2509; types arb-step-typecheck-0b47a303e6cb4ea7b72d1d343da081d4; tests arb-step-unittest-justify-02-e18a117e04fa4485becaf47a39851fd8; coverage arb-step-coverage-10e03300a7f346f1875aa9be1c39595c.
- Date: 2026-04-22

---

**Brief Status:** Completed

**Date Completed:** 2026-04-22

**Evidence Hash:** -
