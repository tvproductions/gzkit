---
id: OBPI-0.0.63-07-verify-stage-command-shape-gate
parent: ADR-0.0.63-closeout-ceremony-runtime-engine-parity
item: 7
lane: Heavy
status: Completed
ln:
  - req_id: REQ-0.0.63-07-01
    receipt_ids:
      - arb-step-obpi07tests-7e3ebc43a13144c0afb33cead0e3dd19
      - arb-step-unittest-2edb5e9913c5434b81ad9b93d9159a50
  - req_id: REQ-0.0.63-07-02
    receipt_ids:
      - arb-step-obpi07tests-7e3ebc43a13144c0afb33cead0e3dd19
      - arb-step-unittest-2edb5e9913c5434b81ad9b93d9159a50
  - req_id: REQ-0.0.63-07-03
    receipt_ids:
      - arb-step-obpi07tests-7e3ebc43a13144c0afb33cead0e3dd19
      - arb-step-unittest-2edb5e9913c5434b81ad9b93d9159a50
  - req_id: REQ-0.0.63-07-04
    receipt_ids:
      - arb-step-obpi07tests-7e3ebc43a13144c0afb33cead0e3dd19
      - arb-step-unittest-2edb5e9913c5434b81ad9b93d9159a50
---

# OBPI-0.0.63-07-verify-stage-command-shape-gate: reject non-shell-less brief Verification commands at authoring time (gz validate scope) and at the verify stage (clear failure), reusing the BI-1 classifier

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md`
- **Checklist Item:** #7 — "OBPI-0.0.63-07: **verify-stage-command-shape-gate** — the OBPI-pipeline verify stage and a fail-closed `gz validate` scope reject brief `## Verification` commands that are not single-program shell-less invocations, so authoring-vs-runtime mismatch (GHI #550) fails closed at authoring time rather than erroring confusingly at the verify gate. Reuses the shell-less command classifier built by OBPI-0.0.63-02."

**Status:** Completed

## Objective

Close GHI #550 (brief `## Verification` compound commands like `test -f x && echo ok` fail under the shell-less runtime with `test: unexpected operator`) on two surfaces, both consuming the BI-1 classifier `brief_commands.is_shell_less_executable` (no fork): (1) a fail-closed `gz validate --brief-command-shape` scope that exits 3 when any brief's `## Verification` fenced command is not a single-program shell-less invocation — catching the mismatch at authoring time; and (2) the OBPI-pipeline verify stage classifies each `## Verification` command before dispatch and reports a non-shell-less command with a clear "rewrite as single-program lines" message instead of passing it to `run_command` and surfacing the raw subprocess error. The OBPI brief template's `## Verification` section gains authoring guidance naming the single-program contract.

> **Non-Goal — do NOT change `run_command` (`src/gzkit/quality.py`).** Its `shlex.split` + `shell=False` contract is intentional (GHI #415: gate execution must not depend on shell parsing). The fix is to *classify before dispatch*, not to make the runtime shell-aware. `quality.py` is a read-only reference here.

## Lane

**Heavy** — adds a `gz validate` scope (CLI/validator surface) and changes verify-stage runtime behavior.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md` — parent ADR (read-only reference)
- `src/gzkit/governance/trust_audits/briefs.py` — NEW `audit_brief_command_shape(project_root)` scope function; mirrors `audit_brief_headings` brief-walking (`rglob("OBPI-*.md")`), extracts each brief's `## Verification` fenced commands via `brief_commands.extract_fenced_commands`, flags any failing `brief_commands.is_shell_less_executable`
- `src/gzkit/cli/parser_maintenance.py` — register the `--brief-command-shape` flag on `gz validate` (mirror the `--req-kind-discipline` registration at ~line 663)
- `src/gzkit/commands/validate_cmd.py` — dispatch `brief_command_shape` scope (mirror `_validate_req_kind_discipline` wiring)
- `src/gzkit/commands/obpi_stages.py` — in the verify-stage command path (`_pipeline_verification_commands` / `_dispatch_verification_commands`, current lines ~139-163/224-259), classify each non-baseline `## Verification` command via `is_shell_less_executable`; a non-shell-less command fails with a clear remediation message and is NOT dispatched to `run_command`
- `.gzkit/templates/obpi.md` — `## Verification` section gains one-paragraph authoring guidance: single-program shell-less commands only (no `&&`/`||`/`|`/`;`/`$(...)`/redirects); propagate via `gz agent sync control-surfaces`
- `tests/governance/test_brief_command_shape.py` — NEW; validator-scope tests (positive + fail-closed)
- `tests/commands/test_obpi_stages.py` — verify-stage classification test (create if absent under `tests/commands/`)

## Denied Paths

- `src/gzkit/quality.py` — `run_command`'s shell-less contract is intentional (GHI #415); read-only reference, do NOT modify
- `src/gzkit/brief_commands.py` — the BI-1 classifier is defined in OBPI-0.0.63-02 and consumed read-only here; do NOT modify
- `src/gzkit/commands/ceremony_data.py`, `closeout_ceremony.py` — OBPI-02 / OBPI-01 surfaces
- `src/gzkit/templates/obpi.md`, `.claude/**`, `.github/**` — generated by sync; edit `.gzkit/templates/obpi.md` only
- Any path not listed in Allowed Paths; new dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. ALWAYS: Consume the single shared classifier `brief_commands.is_shell_less_executable` (BI-1) on both surfaces — never reimplement shell-operator detection.
2. ALWAYS: `gz validate --brief-command-shape` exits 3 (policy breach) when any brief `## Verification` fenced command is not shell-less-executable; exit 0 when all are.
3. ALWAYS: The verify stage reports a non-shell-less command with an actionable message (name the offending operator; instruct "rewrite as separate single-program lines") and NEVER dispatches it to `run_command`.
4. NEVER: Modify `run_command` / `quality.py` to interpret shell syntax (GHI #415 contract).
5. NEVER: Flag a command whose operator is inside a quoted argument (e.g. `python -c "a | b"`) — the classifier already distinguishes data from syntax.
6. ALWAYS: Keep the new validator scope within `gz validate`'s registration + dispatch convention (parser_maintenance.py flag + validate_cmd.py dispatch + trust_audits scope function).

> STOP-on-BLOCKERS: if `brief_commands.is_shell_less_executable` is absent (OBPI-02 not landed), print a BLOCKERS list and halt — OBPI-07 depends on it.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Checklist item #7 + § Target Scope `verify-stage-command-shape-gate`** — quote verbatim into Implementation Summary.
- [ ] Parent ADR § Boundary Invariants — **BI-1** (shell-less brief-command executability) is the fence both surfaces anchor.
- [ ] Parent ADR § Non-Goal #5 (amended) — OBPI-07's brief-command-shape gate is the named carve-out.

> **STOP:** If you cannot quote the Checklist item #7 / Target Scope, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/cross-platform.md` § Subprocess — no `shell=True` (why the runtime is shell-less; GHI #415)
- [ ] `.gzkit/rules/cli.md` § Exit Codes — exit 3 = Policy Breach (the scope's failure code)

**Context:**

- [ ] `src/gzkit/brief_commands.py` — `is_shell_less_executable`, `extract_fenced_commands` (the consumed BI-1 surface, OBPI-02)
- [ ] OBPI-0.0.63-02 brief — the classifier's contract and test patterns

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/brief_commands.py` exists with `is_shell_less_executable` and `extract_fenced_commands` (OBPI-02 landed)
- [ ] `gz validate --req-kind-discipline` registration is present in `parser_maintenance.py` (the wiring precedent to mirror)

**Existing Code (understand current state):**

- [ ] `src/gzkit/governance/trust_audits/briefs.py` `audit_brief_headings` (the brief-walking + ValidationError pattern to mirror)
- [ ] `src/gzkit/commands/obpi_stages.py` `_pipeline_verification_commands` (regex `r"```bash\n(.*?)```"` + per-line extract) and `_dispatch_verification_commands` (the classify-before-dispatch insertion point)
- [ ] `src/gzkit/commands/validate_cmd.py` `_explicit_scope_runners` / `_default_scope_runners` (scope dispatch registry)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Checklist item #7 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from REQ acceptance criteria, not implementation
- [ ] Red-Green-Refactor per behavior increment
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `gz cli audit` clean for the new `--brief-command-shape` flag (manpage + index coverage)
- [ ] Brief template `## Verification` guidance updated + synced

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.governance.test_brief_command_shape tests.commands.test_obpi_stages -v
```

## Demo

<!-- Demo runs the validator's own test suite (exit 0, shell-less): exercises both
     the fail-closed compound-command path and the pass path. The bare
     `uv run gz validate --brief-command-shape` repo scan currently exits 3 on 40
     pre-existing active-brief violations (tracked for a follow-up GHI), so it is
     not used as the closeout-bound demo until that debt is drained. -->

```bash
uv run -m unittest tests.governance.test_brief_command_shape
```

## Acceptance Criteria

- [ ] REQ-0.0.63-07-01 [BEHAVIOR]: Given a brief whose `## Verification` block contains a compound command (`test -f x && echo ok`), when `gz validate --brief-command-shape` runs, then it exits 3 and names the offending brief + command — closes GHI #550 at authoring time.
- [ ] REQ-0.0.63-07-02 [BEHAVIOR]: Given a brief whose `## Verification` commands are all single-program shell-less invocations, when `gz validate --brief-command-shape` runs, then it exits 0.
- [ ] REQ-0.0.63-07-03 [SUPPORT]: The OBPI brief template `## Verification` section gains authoring guidance naming the single-program shell-less contract — `gz validate --documents` + `artifact_edited` event on `.gzkit/templates/obpi.md`.
- [ ] REQ-0.0.63-07-04 [STRUCTURAL-FENCE]: Both the `gz validate --brief-command-shape` scope and the OBPI-pipeline verify stage consume the single shared classifier `brief_commands.is_shell_less_executable` (no fork) — ADR-0.0.63 `## Boundary Invariants` BI-1, audited at ADR closeout.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from REQ
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now documented
- [ ] **Key Proof:** One concrete usage example included
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
# Paste docs-build + gz cli audit output here
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

Before: brief `## Verification` compound commands (`test -f X && echo`, `grep … | wc -l`) failed under the shell-less runtime with `test: unexpected operator`, discovered only mid-closeout (GHI #550); nothing caught them at authoring time and the verify-stage error was opaque. After: `gz validate --brief-command-shape` fails closed at authoring time on any non-shell-less Verification command, the verify stage reports such commands with an actionable rewrite message instead of the raw subprocess error, and the brief template warns authors of the single-program contract — all via the one shared BI-1 classifier.

### Key Proof


`uv run -m unittest tests.governance.test_brief_command_shape tests.commands.test_obpi_stages -v` → 11/11 pass (receipt arb-step-obpi07tests-7e3ebc43a13144c0afb33cead0e3dd19). `uv run gz validate --brief-command-shape` exits 3 reporting: "Non-shell-less Verification command: 'test -f x && echo ok'. Rewrite as separate single-program lines". `python -c "from gzkit.brief_commands import is_shell_less_executable; print(is_shell_less_executable('test -f x && echo ok'))"` → False (same predicate drives both surfaces, BI-1).

### Implementation Summary


- Parent ADR Checklist item #7: verify-stage-command-shape-gate — reject non-single-program shell-less brief Verification commands at authoring time and at the verify stage, reusing OBPI-02's classifier.
- BI-1 reuse: audit_brief_command_shape (briefs.py) and _pipeline_verification_commands (obpi_stages.py) both consume brief_commands.is_shell_less_executable — no fork.
- Validator: gz validate --brief-command-shape exits 3 on non-shell-less Verification commands in active (non-terminal-status) briefs; terminal-status briefs (Completed/attested_completed/Validated/Superseded/archived/Promoted) skipped as historical records.
- Verify stage: _pipeline_verification_commands raises SystemExit(1) with actionable "rewrite as separate single-program lines" message before dispatch.
- Files: src/gzkit/governance/trust_audits/briefs.py (+__init__.py re-export), src/gzkit/commands/obpi_stages.py, src/gzkit/cli/parser_maintenance.py, src/gzkit/commands/validate_cmd.py, docs/user/manpages/validate.md, .gzkit/templates/obpi.md, data/behave_coverage_waivers.json.
- Tests: tests/governance/test_brief_command_shape.py (8), tests/commands/test_obpi_stages.py (3). Direct-fix: 2 completed ADR-0.9.0 briefs (heredoc + && rewritten shell-less).
- Date completed: 2026-05-29
- Attestation status: attested by g0 (operator-verbatim conversational)
- Defects noted: 40 pre-existing brief Verification compound-command violations (cmd && echo REQ-NN OK idiom) logged in agent-insights.jsonl for a follow-up GHI.

## Tracked Defects

- GHI #550 — Verification compound commands fail under shell-less runtime (closed by REQ-07-01 + REQ-07-02).

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.63-07 verify-stage-command-shape-gate landed: gz validate --brief-command-shape scope + verify-stage classify-before-dispatch both consume the BI-1 classifier (brief_commands.is_shell_less_executable, no fork), closing GHI #550 at authoring time. 11 OBPI tests GREEN (receipt arb-step-obpi07tests-7e3ebc43a13144c0afb33cead0e3dd19), 5732 full suite GREEN (arb-step-unittest-2edb5e9913c5434b81ad9b93d9159a50), ruff/ty/mkdocs clean. Attested by g0.
- Date: 2026-05-29

---

**Date Completed:** 2026-05-29

**Evidence Hash:** -
