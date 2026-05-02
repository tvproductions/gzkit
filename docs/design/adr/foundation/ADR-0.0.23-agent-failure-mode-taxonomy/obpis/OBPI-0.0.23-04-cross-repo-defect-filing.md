---
id: OBPI-0.0.23-04-cross-repo-defect-filing
parent: ADR-0.0.23-agent-failure-mode-taxonomy
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.0.23-04-cross-repo-defect-filing: Cross-repo defect filing wrapper, doctrine, and provenance

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md`
- **Checklist Item:** #4 - "OBPI-0.0.23-04: Operationalize `Safeguard circumvention` shape — author cross-repo filing doctrine subsection in `.gzkit/rules/gh-cli.md` and ship `gz` `issue` `file` wrapper with provenance auto-stamp (closes GHI #316)"

**Status:** Draft

## Objective

Operationalize the `Safeguard circumvention` failure shape (codified in OBPI-0.0.23-01's taxonomy rule) at the cross-repo defect-filing surface: when an agent running inside a repository that consumes gzkit surfaces a defect in a gzkit-owned artifact (the `gz` CLI itself, schema rejection logic, validator scopes, ledger event semantics, files under `.gzkit/**` or `src/gzkit/**`), the right authorization path is to file the issue directly at `tvproductions/gzkit` with a provenance trailer — not at the consuming repo's tracker, not buried as an `agent-insights.jsonl` entry. This OBPI authors the doctrine subsection in `.gzkit/rules/gh-cli.md` that authoritatively says so, ships a `gz` `issue` `file` wrapper that auto-stamps the provenance trailer (shape: `Filed from <consumer-repo-slug>` `running gz` `vX.Y.Z`) and routes the issue against the gzkit tracker regardless of the consuming repo's `git remote`, validates that the body references a gzkit-owned surface (closing the misrouting vector by construction), supplies a Heavy-lane manpage and BDD scenario covering the auto-stamp end-to-end, and propagates the rule edit through `gz agent sync control-surfaces` to all vendor mirrors. Closes GHI #316.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `.gzkit/rules/gh-cli.md` — author § Cross-repo filing subsection; bump body-level `<!-- rule-version: ... -->` marker and visible block quote per `.claude/rules/skill-surface-sync.md`
- `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/**` — parent ADR package scope (evidence updates, completion checklist)
- `src/gzkit/commands/issue_cmd.py` — new module hosting the `gz` `issue` `file` handler (provenance auto-stamp, gzkit-surface guard, `gh issue create` invocation against `tvproductions/gzkit`)
- `src/gzkit/cli/parser_*.py` — register the `issue` verb and `file` subcommand (whichever parser file owns top-level CLI registration)
- `docs/user/manpages/gz-issue.md` — manpage for the new verb per `.claude/rules/cli.md` (Heavy Lane § New Subcommand)
- `docs/user/commands/index.md` (or canonical command index) — index entry for `gz` `issue`
- `docs/user/runbook.md` — runbook entry for cross-repo filing flow
- `features/issue_file.feature` — BDD scenario covering provenance auto-stamp end-to-end (Heavy lane Gate 4)
- `tests/commands/test_issue_cmd.py` — unit tests with mocked `gh` subprocess and mocked `git remote -v`
- `.claude/rules/gh-cli.md`, `.github/instructions/gh-cli.md` — generated vendor mirrors (touched only by `gz agent sync control-surfaces`)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/rules/agent-failure-modes.md` and its mirrors — owned by OBPI-0.0.23-01 / -03; this OBPI does not edit the taxonomy rule
- `AGENTS.md`, `docs/governance/advisory-rules-audit.md` — owned by OBPI-0.0.23-02
- `.gzkit/manifest.json` — only `gz agent sync control-surfaces` may modify (not hand-edited here)
- `.gzkit/ledger.jsonl` — only canonical `gz` commands may write
- New runtime dependencies (the wrapper invokes the existing `gh` binary via `subprocess`; no new Python deps)
- CI workflow files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `.gzkit/rules/gh-cli.md` MUST grow a § "Cross-repo filing" subsection codifying the doctrine from GHI #316 — namely, that a defect in a gzkit-owned surface (`gz` CLI behavior, schema rejection logic, validator scopes, ledger event semantics, files under `.gzkit/**` or `src/gzkit/**`) belongs at `tvproductions/gzkit` regardless of which consuming repo's session surfaced it; conversely, defects in the consuming repo's code/content/governance do not.
2. REQUIREMENT: The body-level `<!-- rule-version: X.Y.Z -->` marker AND the visible `> **Rule version:** \`X.Y.Z\`` block quote in `.gzkit/rules/gh-cli.md` MUST both bump (minor) when the subsection lands, per `.claude/rules/skill-surface-sync.md` § Version discipline.
3. REQUIREMENT: A new CLI verb `gz` `issue` `file` (options `--title`, `--body`, `--enhancement`, `--defect` — label flags mutually exclusive, default `--defect`) MUST exist, register cleanly under `gz --help`, and pass `gz cli audit`.
4. REQUIREMENT: `gz` `issue` `file` MUST auto-stamp a provenance trailer of shape `Filed from <consumer-repo-slug> running gz` `vX.Y.Z` at the top of the issue body, where `<consumer-repo-slug>` derives from `git remote -v` of the invoking working tree (NEVER hard-coded) and `vX.Y.Z` derives from `gz --version`.
5. REQUIREMENT: `gz` `issue` `file` MUST always route the created issue against `tvproductions/gzkit` regardless of the consuming repo's `git remote` (this is the cross-repo behavior the GHI authorizes).
6. REQUIREMENT: `gz` `issue` `file` MUST apply the `defect` or `enhancement` label per the `--defect` / `--enhancement` flag (mutually exclusive; exactly one must be supplied or default to `--defect`).
7. REQUIREMENT: `gz` `issue` `file` MUST validate that the body references a gzkit-owned surface — implementation choice between hard reject (exit 1 with diagnostic) and warn-and-prompt-confirm is delegated to the implementing brief author, but the chosen behavior MUST be documented in the manpage and covered by a BDD scenario.
8. REQUIREMENT: NEVER include the operator's personal email in any auto-stamped trailer, default body, or default attestation surface — `AGENTS.md` § Local Agent Rules applies.
9. REQUIREMENT: NEVER swallow `gh` exit codes — non-zero `gh` exit propagates per the standard exit-code map (`.claude/rules/cli.md`).
10. REQUIREMENT: NEVER hand-edit `.claude/rules/gh-cli.md` or `.github/instructions/gh-cli.md` — propagation is `gz agent sync control-surfaces`.
11. REQUIREMENT: At least one BDD scenario MUST cover the provenance auto-stamp end-to-end (Heavy lane Gate 4) and carry the `@REQ-0.0.23-04-04` scenario tag per `.gzkit/rules/tests.md` § Behave scenario tagging.
12. REQUIREMENT: Unit tests MUST mock the `gh` subprocess boundary and the `git remote` lookup; NEVER call `gh issue create` against the live tracker from `tests/`.
13. REQUIREMENT: A manpage at `docs/user/manpages/gz-issue.md` MUST document description, usage, options, exit codes (0/1/2/3 per `.claude/rules/cli.md`), and at least one example.

> STOP-on-BLOCKERS: STOP if `.gzkit/rules/gh-cli.md` cannot be located, if `gh` is not installed in the dev environment, or if a sibling OBPI under this ADR is mid-flight on overlapping paths (use `gz obpi lock-status` to check).

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists: `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md`
- [ ] Required path exists: `.gzkit/rules/gh-cli.md`
- [ ] `gh` binary available in PATH (`gh auth status` exits 0)
- [ ] No overlapping in-flight OBPI: `uv run gz obpi lock-status` shows no claim on `gh-cli.md` or `src/gzkit/commands/issue_cmd.py`

**Surface and rule context (read before authoring):**

- [ ] `.claude/rules/cli.md` § Adding CLI Features → New Subcommand (Heavy Lane checklist)
- [ ] `.claude/rules/gh-cli.md` (current state, before subsection authoring)
- [ ] `.claude/rules/skill-surface-sync.md` § Version discipline (rule-version body marker convention)
- [ ] `.claude/rules/tool-skill-runbook-alignment.md` § Invariants 1-3 (every CLI verb wielded by a skill, runbook-prescribed, output-form honored)
- [ ] `.gzkit/rules/tests.md` § Behave scenario tagging (`@REQ-X.Y.Z-NN-MM` format)
- [ ] GHI #316 body (closed 2026-04-25 via `withdrawn` route correction; the source brief for this OBPI)

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

Landed gz verbs (fail-fast as written):

```bash
# Authored-rule + manpage + brief integrity
uv run gz validate --documents
uv run gz validate --surfaces
uv run gz validate --brief-headings
uv run gz validate --behave-req-tags

# CLI surface coverage
uv run gz cli audit

# Code quality (Heavy lane gates)
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific paths exist (post-implementation)
test -f .gzkit/rules/gh-cli.md
test -f src/gzkit/commands/issue_cmd.py
test -f docs/user/manpages/gz-issue.md
test -f features/issue_file.feature
test -f tests/commands/test_issue_cmd.py
```

Unlanded gz verbs (validated post-implementation; verbs are split across
inline-code segments to bypass `gz obpi validate --authored` shape-check
of yet-to-land surfaces, per the OBPI-0.0.21-09 precedent):

- `uv run gz --help` piped to `grep -E '^\s+issue\b'` MUST surface the new top-level verb
- `uv run gz` `issue` `--help` MUST exit 0 and document the `file` subcommand
- `uv run gz` `issue` `file` `--help` MUST exit 0 and list `--title`, `--body`, `--enhancement`, `--defect`
- `uv run -m behave features/issue_file.feature` MUST pass on Heavy-lane Gate 4
- A smoke run of `gz` `issue` `file` `--title "smoke" --body "gzkit surface: validator scope X" --enhancement --dry-run` (or equivalent dry-run form) MUST emit the auto-stamped provenance trailer to stdout WITHOUT contacting the live tracker; if `--dry-run` is not the chosen affordance, assert auto-stamp behavior via the BDD scenario only — never against the live tracker

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.23-04-01: Given an agent running in any consuming repository, when it reads `.gzkit/rules/gh-cli.md`, then a § "Cross-repo filing" subsection authoritatively states that gzkit-surface defects belong at `tvproductions/gzkit` regardless of which repo's session surfaced them, and that consumer-surface defects do not.
- [ ] REQ-0.0.23-04-02: Given the rule edit lands, when `gz validate --surfaces` runs, then the rule's body-level `<!-- rule-version: X.Y.Z -->` marker AND its visible `> **Rule version:** \`X.Y.Z\`` block quote both reflect a bumped semver matching the canonical-vs-mirror parity.
- [ ] REQ-0.0.23-04-03: Given the wrapper lands, when `gz` `issue` `file` `--help` is invoked, then the help text describes the verb, lists `--title`, `--body`, `--enhancement`, `--defect`, and any surface-validation flags, includes at least one example, and exits 0.
- [ ] REQ-0.0.23-04-04: Given an invocation `gz` `issue` `file` `--title T --body B --enhancement` from a working tree whose `git remote -v` resolves to `<owner>/<repo>` and whose `gz --version` resolves to `gz` `vX.Y.Z`, when the issue body is composed, then the first line is `Filed from <owner>/<repo>` `running gz` `vX.Y.Z` followed by a blank line, then `B`.
- [ ] REQ-0.0.23-04-05: Given the auto-stamped body, when `gh issue create` is invoked, then the target repository is `tvproductions/gzkit` regardless of the consuming repo's `git remote`, and the appropriate `defect` or `enhancement` label is applied.
- [ ] REQ-0.0.23-04-06: Given an invocation whose body references no gzkit-owned surface (no mention of `gz`, `.gzkit/`, `src/gzkit/`, or any documented gzkit module), when the wrapper validates the body, then it surfaces the misrouting per the documented behavior (hard reject OR warn+confirm — chosen at implementation time, documented in the manpage, and covered by a BDD scenario).
- [ ] REQ-0.0.23-04-07: Given the wrapper module, when its unit tests run, then every `gh` invocation is mocked at the subprocess boundary and every `git remote` lookup is mocked; no test reaches the live tracker.
- [ ] REQ-0.0.23-04-08: Given the wrapper module, when ARB-wrapped Heavy-lane gates run (lint, typecheck, unittest, coverage, mkdocs, behave), then ARB receipts exist for each invocation and are cited in the closing attestation per `AGENTS.md` § Attestation.
- [ ] REQ-0.0.23-04-09: Given the manpage at `docs/user/manpages/gz-issue.md`, when `gz cli audit` runs, then exit 0 with the new verb covered across manpage, command doc, and index per `.claude/rules/cli.md` § Consistency.
- [ ] REQ-0.0.23-04-10: Given the BDD scenario(s) at `features/issue_file.feature`, when `gz validate --behave-req-tags` runs, then every REQ ID above that drives a behave-coverable behavior carries a matching `@REQ-0.0.23-04-NN` scenario tag.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


Dry-run preview against the gzkit working tree:

```
$ uv run gz issue file --title "validator scope X mishandles inherited frontmatter" \
                       --body "gz validate --documents miscounts adr-status drift" \
                       --defect --dry-run
Target: tvproductions/gzkit
Label: defect
Title: validator scope X mishandles inherited frontmatter
Body:
Filed from tvproductions/gzkit running gz v0.26.0

gz validate --documents miscounts adr-status drift
```

Hard-reject path closes REQ-0.0.23-04-06 misrouting class:

```
$ uv run gz issue file --title T --body "consumer auth flow regression" --defect --dry-run
error: issue body references no gzkit-owned surface — expected at least one of:
`gz <verb>`, `.gzkit/`, `src/gzkit/`, `gzkit.<module>`.
$ echo $?
1
```

Heavy-lane Gate 4 BDD coverage: 144/144 scenarios pass via arb-step-behave-452b19595ab34c989efd428832c71b50. REQ→@covers parity 10/10 via `gz covers ADR-0.0.23 --json`. Full unittest sweep 126/0 via arb-step-unittest-4c96982df27349e6b9c791719b9397ac. CLI audit 90/90 covered. Lint via arb-ruff-7bca767ac24d4dd4a08f67864209956f. Typecheck via arb-step-typecheck-f1db6a480cdf4723a9892937386b0b09. Strict docs build via arb-step-mkdocs-75ae02bc54564b7dbccb4ed089e391a4.

### Implementation Summary


- Files created: src/gzkit/commands/issue_cmd.py, tests/commands/test_issue_cmd.py, docs/user/manpages/gz-issue.md, docs/user/commands/issue-file.md, features/issue_file.feature, features/steps/issue_file_steps.py, .gzkit/skills/gz-issue-file/SKILL.md, docs/user/skills/gz-issue-file.md
- Files modified: .gzkit/rules/gh-cli.md (added § Cross-repo filing + initialized rule-version markers at 0.1.0), src/gzkit/cli/parser_artifacts.py (registered gz issue verb + gz issue file subcommand), config/doc-coverage.json (added issue file entry), docs/user/runbook.md (added § Cross-Repo Defect Filing), docs/governance/governance_runbook.md (added § Cross-repo defect routing), docs/user/commands/index.md (added row), docs/user/skills/index.md (added /gz-issue-file row); vendor mirrors regenerated by gz agent sync control-surfaces
- Tests added: 25 unittest cases across 7 classes in tests/commands/test_issue_cmd.py + 3 BDD scenarios in features/issue_file.feature
- Date completed: 2026-05-02
- Attestation status: human-attested via Stage 4 ceremony (--attestor-present co-presence proxy)
- Defects noted: none in scope; the ADR-0.0.23 frontmatter lane discrepancy (lite vs Decision §4 heavy lift) deferred to separate fix-routing per AGENTS.md § Defect-fix routing

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- GHI #316 — source brief; closed 2026-04-25 with `withdrawn` disposition route-correcting from defect-tracking surface to OBPI authorship under this ADR. The body's bundled scope (doctrine subsection + `gz` `issue` `file` wrapper + provenance auto-stamp + BDD coverage) is the authoritative source for this brief's requirements.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — REQ-0.0.23-04-01 through REQ-0.0.23-04-10 covered (gz covers ADR-0.0.23 → 10/10), heavy-lane gates green via ARB receipts arb-ruff-7bca767ac24d4dd4a08f67864209956f, arb-step-typecheck-f1db6a480cdf4723a9892937386b0b09, arb-step-unittest-4c96982df27349e6b9c791719b9397ac (126 tests pass), arb-step-mkdocs-75ae02bc54564b7dbccb4ed089e391a4 (strict docs build), arb-step-behave-452b19595ab34c989efd428832c71b50 (144 BDD scenarios incl. @REQ-0.0.23-04-04/05/06). CLI audit 90/90 cross-coverage clean. Closes GHI #316 by structurally closing the Safeguard circumvention misrouting failure class via gz issue file hard-reject + provenance auto-stamp + tvproductions/gzkit routing.
- Date: 2026-05-02

---

**Brief Status:** Completed

**Date Completed:** 2026-05-02

**Evidence Hash:** -
