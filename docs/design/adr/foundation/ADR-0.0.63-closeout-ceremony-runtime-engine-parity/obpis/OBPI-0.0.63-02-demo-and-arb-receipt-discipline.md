---
id: OBPI-0.0.63-02-demo-and-arb-receipt-discipline
parent: ADR-0.0.63-closeout-ceremony-runtime-engine-parity
item: 2
lane: Heavy
status: Completed
ln:
  - req_id: REQ-0.0.63-02-01
    receipt_ids:
      - arb-step-unittest-a9150e2dfc1447b5a50915c549ac0613
  - req_id: REQ-0.0.63-02-02
    receipt_ids:
      - arb-step-unittest-a9150e2dfc1447b5a50915c549ac0613
  - req_id: REQ-0.0.63-02-03
    receipt_ids:
      - arb-step-unittest-a9150e2dfc1447b5a50915c549ac0613
  - req_id: REQ-0.0.63-02-04
    receipt_ids:
      - arb-step-unittest-a9150e2dfc1447b5a50915c549ac0613
  - req_id: REQ-0.0.63-02-05
    receipt_ids:
      - arb-step-unittest-a9150e2dfc1447b5a50915c549ac0613
---

# OBPI-0.0.63-02-demo-and-arb-receipt-discipline: demo extraction joins multi-line fenced commands, classifies shell-less executability, and binds demo ARB receipts to observed exit code + stdout SHA

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md`
- **Checklist Item:** #2 — "OBPI-0.0.63-02: **demo-and-arb-receipt-discipline** — `src/gzkit/commands/ceremony_data.py`. Demo extraction re-executes the demo command and binds the ARB receipt to observed exit code + stdout SHA. ARB generators accept multi-line command strings as a single quoted argv list."

**Status:** Completed

## Objective

Make the closeout demo surface honest at the *extraction* layer: parse `## Demo` / `## Examples` fenced blocks into cohesive logical commands (joining multi-line `python -c "…"` / backslash-continued / heredoc constructs instead of shredding them per physical line — GHI #539); expose a single shared shell-less-executability classifier (BI-1) that OBPI-07 reuses for the verify stage; and provide a demo re-execution function that binds an ARB receipt to the *observed* exit code + stdout SHA and flags any demo whose observed exit disagrees with its claimed shape (GHI #540). Multi-line command strings handed to ARB generators are quoted as a single argv list, not split on newline (ADR Decision #3).

> **Scope boundary (read before implementing):** This OBPI delivers the pure, unit-testable functions in `ceremony_data.py` + their tests. Wiring the demo-receipt binding into the closeout walkthrough lands in **OBPI-0.0.63-01** (which restructures `closeout_ceremony.py` into the ledger-gated state machine — its natural home). Implementing the wiring here would churn a file OBPI-01 rewrites. The end-to-end closeout behavior is audited at ADR closeout via **BI-1**.

> **Decision#2 vs Non-Goal#1 reconciliation (recorded, not silently picked):** ADR Decision #2 re-executes the *demo command*; ADR Non-Goal #1 preserves presenter posture for *claimed quality receipts* (lint/test evidence). These are not in conflict — **demos ≠ receipts**. A `## Demo` block is a product demonstration that is re-run to bind its own ARB receipt; an already-attested quality receipt is never re-executed (spec-reviewer persona-dispatch retains that role). The current code does *neither* (demos are merely presented), so this OBPI adds demo re-execution as net-new behavior consistent with Decision #2.

## Lane

**Heavy** — changes a runtime-contract surface (closeout demo extraction + ARB receipt binding semantics).

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md` — parent ADR for intent and scope (read-only reference)
- `src/gzkit/brief_commands.py` — **NEW shared module** (BI-1 spine): quote-aware fenced-command extraction, the shell-less-executability classifier, demo re-execution → receipt, and multi-line ARB command quoting. Lives standalone (not inside `ceremony_data.py`) because (a) `ceremony_data.py` is at 544/600 lines and these additions breach the pythonic module cap, and (b) BI-1 requires *one shared* classifier that OBPI-0.0.63-07's verify stage imports — a shared lib, not a ceremony-private helper.
- `src/gzkit/commands/ceremony_data.py` — refactor `_commands_from_demo_sections` (current lines 309-343) to delegate per-block parsing to `brief_commands.extract_fenced_commands`, preserving the registered-`gz`-verb validation
- `tests/test_brief_commands.py` — **NEW**; unit tests for the shared module (extraction join, classifier, re-execution receipt, ARB quoting)
- `tests/test_ceremony_demo_discovery.py` — currently empty (0 lines); RED-first home for the `_commands_from_demo_sections` delegation regression (multi-line construct → one command)
- `tests/test_ceremony_data_extraction.py` — existing extraction tests; extend only if a regression assertion belongs alongside current cases

> **Scope amendment (in-flight, recorded — GHI #190 ground-truth discipline):** the original brief named only `ceremony_data.py`. Implementation discovery (the 600-line module cap + BI-1's shared-classifier mandate) required a new standalone module `src/gzkit/brief_commands.py` and its test file. This is the OBPI-0.0.16-03 precedent: Allowed Paths amended to on-disk reality before code is written, not after.

## Denied Paths

- `src/gzkit/commands/closeout_ceremony.py` — the walkthrough wiring + state machine is **OBPI-0.0.63-01's** surface; do not touch it here
- `src/gzkit/commands/obpi_stages.py`, `src/gzkit/quality.py` — verify-stage surface is **OBPI-0.0.63-07**; the classifier is *defined* here and *consumed* there, but those files are edited in OBPI-07
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. ALWAYS: Quote the parent ADR § Decision item this OBPI implements into the Implementation Summary before any code is written (Decision items #2 and #3).
2. NEVER: Split a multi-line quoted/continued construct inside a fenced block into more than one logical command. A `python -c "…"` heredoc spanning N physical lines is exactly one command.
3. ALWAYS: Treat a logical command containing an unbalanced shell operator (`&&`, `||`, `|`, `;`, `$(...)`, `<`, `>`) as **not shell-less-executable** — the classifier returns a negative verdict; it never silently rewrites the command.
4. ALWAYS: Bind a demo re-execution receipt to the *observed* `returncode` and a SHA-256 of observed stdout — never to a prose claim of expected behavior.
5. NEVER: Re-execute an already-attested *quality receipt* (lint/test/etc.); presenter posture for receipts is preserved (ADR Non-Goal #1). Only `## Demo` / `## Examples` product demonstrations are re-executed.
6. ALWAYS: Keep changes inside Allowed Paths; the closeout walkthrough wiring is OBPI-01's surface.

> STOP-on-BLOCKERS: if `tests/test_ceremony_demo_discovery.py` is not empty or the extraction surface has moved off `_commands_from_demo_sections`, print a BLOCKERS list and re-anchor before proceeding.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision items #2 and #3** — quote verbatim into Implementation Summary:
  - "**Add demo-extraction re-execution preflight.** Before emitting an ARB receipt from extracted demo content, re-execute the demo command and bind the receipt to the *observed* exit code and stdout SHA, not the T1 prose claim."
  - "**Quote multi-line ARB commands.** ARB receipt generators must accept multi-line command strings as a single quoted argv list, not split-on-newline."
- [ ] Parent ADR § Intent — closeout-runtime parity with `gz obpi pipeline`'s state machine.
- [ ] Parent ADR § Boundary Invariants — **BI-1** (shell-less brief-command executability) is the fence this OBPI's classifier anchors.
- [ ] Parent ADR § Non-Goals #1 — presenter posture for *receipts* (the demos≠receipts reconciliation above).

> **STOP:** If you cannot quote Decision items #2 and #3, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/cross-platform.md` § Subprocess — list form, no `shell=True` (the classifier encodes this contract; GHI #415)
- [ ] `.gzkit/rules/tests.md` § "Tests assert semantics, not strings" — REQ-derived assertions

**Context:**

- [ ] OBPI-0.0.63-07 (verify-stage gate) — the downstream consumer of the BI-1 classifier; keep the classifier's signature reusable
- [ ] OBPI-0.0.63-01 (state machine) — the home of the closeout walkthrough wiring this OBPI's functions feed

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/ceremony_data.py` exists; `_commands_from_demo_sections` present (re-anchor line numbers against current file — ADR's cited lines are from 2026-05-26 and have drifted)
- [ ] `tests/test_ceremony_demo_discovery.py` exists and is empty (RED-first target)

**Existing Code (understand current state):**

- [ ] `_commands_from_demo_sections` (ceremony_data.py): toggles `in_code` on fence boundaries, appends each non-empty/non-comment **physical line** — the per-line shred is the #539 root
- [ ] `_extract_gz_verb_chain` + `_collect_registered_invocations`: registered-verb validation that must keep working after the join (a joined multi-line command is validated as one unit)
- [ ] `discover_demo_commands` (ceremony_data.py:262-303): the strategy chain that returns demo command strings — the producer the new receipt function pairs with

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision items #2 and #3 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from REQ acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated (closeout demo-extraction behavior)

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
uv run -m unittest tests.test_ceremony_demo_discovery -v
```

## Demo

```bash
uv run python -c "from pathlib import Path; from gzkit.commands.ceremony_data import _commands_from_demo_sections; cmds = _commands_from_demo_sections([Path('tests/fixtures/ceremony_demos/multiline_demo.md')]); print(len(cmds), 'logical command(s)'); print(cmds[0])"
```

## Acceptance Criteria

- [ ] REQ-0.0.63-02-01 [BEHAVIOR]: Given a `## Demo`/`## Examples` fenced block containing a multi-line `python -c "…"` construct, when `_commands_from_demo_sections` extracts it, then the construct is returned as exactly one logical command string (not one per physical line) — fixes GHI #539.
- [ ] REQ-0.0.63-02-02 [BEHAVIOR]: Given a logical command string, when the shared shell-less classifier inspects it, then it returns a negative verdict for any command containing `&&`, `||`, `|`, `;`, `$(...)`, or a redirect, and a positive verdict for a `shlex.split`-parseable single-program invocation.
- [ ] REQ-0.0.63-02-03 [BEHAVIOR]: Given a harvested demo command, when it is re-executed, then the resulting receipt carries the observed `returncode` and a SHA-256 of observed stdout, and a demo whose observed exit code disagrees with its claimed shape is reported as a mismatch — fixes GHI #540.
- [ ] REQ-0.0.63-02-04 [BEHAVIOR]: Given a multi-line command string, when it is prepared for an ARB receipt, then it is carried as a single quoted argv list (no split-on-newline truncation) — ADR Decision #3.
- [ ] REQ-0.0.63-02-05 [STRUCTURAL-FENCE]: The shell-less-executability classifier defined here is the single shared classifier consumed by OBPI-0.0.63-07's verify-stage gate — BI-1 in the parent ADR's `## Boundary Invariants` (audited at ADR closeout).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from REQ, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
$ uv run -m unittest tests.test_brief_commands tests.test_ceremony_demo_discovery
..............
Ran 14 tests in 0.012s
OK
# RED first: 14 tests authored against REQ-01..04 failed (module missing +
# per-line shred: '4 != 2'); GREEN after brief_commands.py + delegation.
# No regression: tests.test_ceremony_data_extraction (25 tests) still OK.
```

### Code Quality

```text
$ uv run ruff check src/gzkit/brief_commands.py src/gzkit/commands/ceremony_data.py tests/test_brief_commands.py tests/test_ceremony_demo_discovery.py
All checks passed!
$ uvx ty check src/gzkit/brief_commands.py
All checks passed!
# Full verify stage (gz obpi pipeline --from=verify): PASS arb ruff, arb
# typecheck, arb unittest, validate --documents, lint, test, mkdocs --strict.
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

Before: the closeout demo extractor split multi-line `python -c "…"` heredocs per physical line, producing ~65% walkthrough noise (GHI #539), and harvested demo commands were never executed — a brief could claim a REQ demonstration that never ran (GHI #540). After: fenced blocks parse into cohesive logical commands; a shared shell-less classifier names what is and isn't runnable under the `shell=False` runtime (BI-1, reused by OBPI-07); and demo re-execution binds receipts to observed exit code + stdout SHA so a demo that lies fails closed.

### Key Proof


```text
# GHI #539 — multi-line demo now extracts as ONE logical command (was 5 fragments):
$ _commands_from_demo_sections([multiline_demo.md])
  [1] 'uv run gz status --json'
  [2] 'uv run python -c "\nfrom pathlib import Path\nprint(...)\n"'   # joined, not shredded

# GHI #550 / BI-1 — the shared classifier names shell-less executability:
  is_shell_less_executable('test -f x && echo ok')  -> False  (rejected)
  is_shell_less_executable('grep -q . file.md')      -> True   (accepted)
  is_shell_less_executable('python -c "a | b"')      -> True   (operator inside quote is data)
```

### Implementation Summary


- Parent ADR § Decision item (quoted):
  - #2: "Add demo-extraction re-execution preflight. Before emitting an ARB receipt from extracted demo content, re-execute the demo command and bind the receipt to the observed exit code and stdout SHA, not the T1 prose claim."
  - #3: "Quote multi-line ARB commands. ARB receipt generators must accept multi-line command strings as a single quoted argv list, not split-on-newline."
- Files created/modified:
  - NEW `src/gzkit/brief_commands.py` — BI-1 shared spine: `extract_fenced_commands`, `is_shell_less_executable`, `reexecute_demo`/`DemoReceipt`, `command_argv`
  - `src/gzkit/commands/ceremony_data.py` — `_commands_from_demo_sections` delegates per-block parsing to the shared extractor
  - NEW `tests/test_brief_commands.py`, `tests/test_ceremony_demo_discovery.py`, `tests/fixtures/ceremony_demos/multiline_demo.md`
- Tests added: 14 (REQ-01..04; REQ-05 STRUCTURAL-FENCE → BI-1)
- Date completed: 2026-05-29 (pending Gate 5 attestation)
- Attestation status: awaiting human Gate 5
- Defects noted: `_extract_gz_verb_chain` positional-capture demo-loss (tracked in agent-insights.jsonl; out of scope, distinct from #539/#540)
- Scope amendment: new shared module `brief_commands.py` (600-line cap + BI-1 shared-classifier mandate); closeout *wiring* deferred to OBPI-0.0.63-01

## Tracked Defects

- GHI #539 — multi-line demo split per-line (closed by REQ-02-01 + closeout wiring in OBPI-01)
- GHI #540 — demos hand-authored, never executed (closed by REQ-02-03 + closeout wiring in OBPI-01)

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.63-02-demo-and-arb-receipt-discipline: shipped src/gzkit/brief_commands.py (BI-1 shared spine: quote-aware fenced extraction, shell-less-executability classifier, demo re-execution receipt binding observed exit code + stdout SHA + mismatch, single-argv multiline) and refactored ceremony_data._commands_from_demo_sections to delegate. 14/14 OBPI tests pass (arb-step-unittest-a9150e2dfc1447b5a50915c549ac0613); ruff clean (arb-ruff-086f7ceb710f446abba75ed4fbb59d0c), ty clean (arb-step-typecheck-aaee91f17f5649078e761d732fd063df), mkdocs --strict clean (arb-step-mkdocs-c951620292824ec0a748908b703131f9); no regression in 25 existing ceremony tests. Closes GHI #539 (multi-line demo split) and #540 (demos never executed); builds the BI-1 classifier OBPI-0.0.63-07 reuses for #550. REQ-05 STRUCTURAL-FENCE accepted-uncovered (proof channel = ADR-0.0.63 Boundary Invariants BI-1, audited at ADR closeout).
- Date: 2026-05-29

---

**Date Completed:** 2026-05-29

**Evidence Hash:** -
