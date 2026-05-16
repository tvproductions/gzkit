---
id: OBPI-0.0.34-05-light-tui-affordances
parent: ADR-0.0.34-agent-control-surface-rendering-substrate
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.34-05-light-tui-affordances: Light Tui Affordances

<!-- gz-validate-skip: brief-demo-section --> <!-- Draft brief; Demo section authored at implementation time per GHI #431 grandfather pattern. -->

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`
- **Checklist Item:** #5 - "OBPI-0.0.34-05: Light TUI affordances — Claude-Code-style status lines, Rich tables, plan-mode-style panels; explicitly NOT a Textual form editor"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Light TUI affordances — Claude-Code-style status lines, Rich tables, plan-mode-style panels; explicitly NOT a Textual form editor.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/content/tui/__init__.py` — TUI affordances public entrypoint
- `src/gzkit/content/tui/status.py` — Claude-Code-style status line for `gz content edit`/`render`
- `src/gzkit/content/tui/tables.py` — Rich table renderer for `gz content list`
- `src/gzkit/content/tui/panels.py` — plan-mode-style panel for `gz content show`
- `src/gzkit/commands/content/edit.py` — wire status-line into edit subcommand (TTY-conditional)
- `src/gzkit/commands/content/render.py` — wire status-line into render subcommand (TTY-conditional)
- `src/gzkit/commands/content/list.py` — wire table renderer into list subcommand (TTY-conditional)
- `src/gzkit/commands/content/show.py` — wire panel renderer into show subcommand (TTY-conditional)
- `tests/content/test_tui_affordances.py` — TTY-on/TTY-off behavior, `--plain` flag, Rich/plain divergence
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-05-light-tui-affordances.md` — this brief

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **Status line, table, and panel affordances only.** Implement Rich-rendered status lines for `gz content edit`/`render`, Rich tables for `gz content list`, and plan-mode-style panels for `gz content show`. NEVER implement an interactive form, a Textual app, or a separate launcher subcommand.
2. REQUIREMENT: **TTY-conditional rendering.** Rich rendering activates only when `sys.stdout.isatty()` returns True. Non-TTY contexts (CI, pipes, redirection) emit plain text. `--plain` flag forces plain text even in TTY contexts.
3. REQUIREMENT: **Zero new top-level commands.** All affordances attach to existing OBPI-04 subcommands. NEVER add `gz content tui`, `gz tui`, or any other launcher verb.
4. REQUIREMENT: **No Textual dependency.** If a candidate solution requires `textual`, the requirement has been mis-read — reject and re-read. Rich is acceptable (already an indirect transitive); NEVER add `textual` as a direct or transitive top-level dependency in this OBPI.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] **Prerequisite OBPI:** OBPI-0.0.34-04 (authoring CLI) — TUI affordances wrap the four subcommands' plain-text output paths. MUST be complete before this OBPI's Gate 2.
- [ ] **Soft co-dependency:** OBPI-0.0.34-02 (rendering pipeline) — status-line on `render` reports byte count and target vendor; reads pipeline return value.
- [ ] No downstream consumers; this is operator-experience polish layered on the authoring surface.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.34-04 complete: `gz content list --help`, `gz content show --help`, `gz content edit --help`, `gz content render --help` each exit 0.
- [ ] `rich` is already an indirect transitive dependency (verify via `uv tree | rg '^rich'`); NEVER add it as a top-level direct dependency in this OBPI.
- [ ] Parent ADR evidence artifacts referenced by this brief are present.

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

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run python -m unittest tests.content.test_tui_affordances -v
uv run gz content list --plain | head -20      # plain text (no ANSI), even on TTY
uv run gz content list | head -20              # Rich table on TTY (ANSI codes acceptable)
uv run gz content list > /tmp/list-pipe.txt    # non-TTY → plain
rg -q $'\x1b\\[' /tmp/list-pipe.txt && exit 1 || true   # no ANSI codes when piped
grep -r "^import textual" src/ tests/          # MUST produce no matches
grep -r "from textual" src/ tests/             # MUST produce no matches
rg -q '^textual' pyproject.toml && exit 1 || true       # MUST not be a top-level dep
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.34-05-01: Given `gz content render <id>` invoked on a TTY, when rendering completes, then a Rich status line summarizing the operation (e.g. `rendered AgentContract → AGENTS.md (2.4 KiB)`) prints to stderr.
- [ ] REQ-0.0.34-05-02: Given `gz content list` invoked on a TTY, when output is produced, then a Rich-rendered table appears; the same command piped to a file produces ANSI-free plain text.
- [ ] REQ-0.0.34-05-03: Given `gz content show <id>` invoked on a TTY, when output is produced, then a Rich panel (plan-mode-style) frames the content; the `--plain` flag suppresses Rich rendering even in TTY contexts.
- [ ] REQ-0.0.34-05-04: Given the project's dependency manifest after this OBPI lands, when grep'd for `textual`, then no top-level dependency entry matches and no `import textual` line exists in `src/` or `tests/`.
- [ ] REQ-0.0.34-05-05: Given `gz content --help`, when invoked, then NO new subcommand has been added by this OBPI (the help output equals OBPI-04's at the subcommand-name level; only output formatting differs).

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

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
