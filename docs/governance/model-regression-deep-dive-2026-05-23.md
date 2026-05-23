# gzkit Model Regression Deep Dive - 2026-05-23

## Purpose

This report records a repository-level diagnosis of the operator concern:

> "gzkit is falling apart because newer models do worse with it."

The short diagnosis is sharper than "newer models are worse": gzkit has built a
very large governance harness whose text surfaces correctly predict model
regression modes, but several core ceremonies still depend on prose discipline,
passive presentation, or validator scopes that do not execute the runtime path
that matters. Newer models expose those weak seams more reliably because they
are more literal, more cautious, and more likely to over-weight repeated
instructions. The project is not unsalvageable, but the emergency is real:
gzkit's highest-value ceremonies need the same fail-closed runtime teeth as
`gz-obpi-pipeline`.

Operator update during review: gzkit is now too bloated to reliably get through
a 258K-window Codex run on GPT-5.5-class models. That makes context economics a
primary failure mode, not a secondary usability concern. The project cannot
assume that larger model windows will absorb the governance surface. The harness
must make most doctrine lazy, task-routed, and mechanically checked, with the
per-turn surface reduced to a compact map plus hard invariants.

This file is intended as a discussion packet for a three-model review. It is not
a replacement for GHI #517; it should be read beside:

- GHI #517: `core-ceremonies: 5-alarm structural emergency - 6 pillars unverified`
- GHI #516: `closeout-ceremony: passive-presenter loop lacks REQ-evidence mechanical verification`
- `docs/governance/model-regression-taxonomy.md`
- `docs/governance/harness-engineering-appraisal.md`

## Commands Run

Observed command results from this session:

| Probe | Result |
|---|---|
| `git status --short` | only untracked `.antigravitycli/`; not touched |
| `uv run scripts/session_orientation.py` | passed and printed orientation digest |
| exact Codex hook command via `sh -c 'uv run python "$(git rev-parse --show-toplevel)/scripts/session_orientation.py"'` | failed: `uv` cache initialization at `/Users/jeff/.cache/uv` denied by sandbox |
| `uv run gz validate --instructions-files-budget` | passed |
| `uv run gz validate --orientation-freshness` | passed |
| `uv run gz validate --invariant-coherence` | passed |
| `uv run gz validate --surfaces` | passed |
| `uv run gz cli audit` | passed, 101/101 commands fully covered |
| `uv run ruff check . --output-format=concise` | passed |
| `uv run gz typecheck` | passed with 5 warnings |
| `uv run ty check .` | failed with 41 diagnostics outside the canonical `gz typecheck` scope |
| `uv run gz check` | failed at Preflight |
| `uv run gz preflight` | failed: orphan plan-audit receipt `.plan-audit-receipt-OBPI-0.0.57-01-nominal-id-doctrine.json` |

Repository-scale snapshot from shell probes:

- 760 Python files, 2615 markdown files, 2317 JSON files, 85 YAML files.
- 1257 ADR-like markdown files and 740 OBPI-like markdown files under `docs/design/adr/`.
- 53 canonical skills, mirrored to 53 `.agents`, 53 `.claude`, and 53 `.github` skill surfaces.
- Root `AGENTS.md` is 30,294 bytes; `CLAUDE.md` is 1,378 bytes; all discovered `AGENTS.md` files total 209,554 bytes.
- `gz status --json` reports 235 ADR records: 173 Pending, 60 Validated, 2 Completed; 173 pending attestations; 126 pending pool ADRs.

## What Is Working

The system is not uniformly broken.

- Structural validators for instructions budget, orientation freshness, surface
  drift, invariant coherence, and CLI coverage all passed.
- Ruff passed.
- `gz typecheck` passed under its canonical scope.
- `uv run scripts/session_orientation.py` itself is functional.
- The existing doctrine already names the model-regression shape. In
  `model-regression-taxonomy.md`, the meta-finding says over-cautious governance
  prompts can degrade modern model performance; it also says text-level fixes do
  not close model-level tendencies and must be paired with tests, hooks, receipt
  checks, and contract-anchored output assertions.
- `gz-obpi-pipeline` is the local gold standard: staged runtime, explicit verify
  stage, human gate, guarded sync/accounting, and fail-closed boundaries.

This matters because the right response is not "throw away gzkit." It is "stop
treating prose-rich ceremonies as equivalent to mechanically enforced runtime
pipelines."

## Critical Findings

### 1. The SessionStart hook can fail while orientation validators pass

Evidence:

- `.codex/hooks.json` uses:
  `["sh", "-c", "uv run python \"$(git rev-parse --show-toplevel)/scripts/session_orientation.py\""]`
- Running that exact shape failed in this session because `uv` attempted to
  initialize `/Users/jeff/.cache/uv` and the sandbox denied access.
- `uv run scripts/session_orientation.py` and `uv run gz validate --orientation-freshness` both passed.

Interpretation:

The validator checks that the hook mentions the script and that the script
contains expected AST structure. It does not execute the hook under Codex's
actual harness/sandbox semantics. That is a T2/T3 gap: authored wiring looks
right, but runtime execution fails.

This directly matches ADR-0.44.0's warning that Codex parity is not achieved by
copying mirrors. ADR-0.44.0 says Codex needs generated config, hook policy,
roles, runtime path abstraction, validation, and instruction-budget evidence
before it is first-class.

Recommended outcome:

Codex hook validation needs an execution probe, not only a wiring probe. The
probe should run the generated hook command in the same execution class Codex
will use, with cache/write paths pinned inside the workspace or with a
stdlib-only wrapper that does not depend on `uv` cache initialization.

Follow-up applied in the same session: keep the hook in the project-scoped
`.codex/hooks.json` surface and keep the uv runtime, but pin uv's mutable cache
to `.gzkit/cache/uv` via `uv run --cache-dir "$(git rev-parse
--show-toplevel)/.gzkit/cache/uv" ...`. The orientation freshness validator now
rejects Codex SessionStart hooks that depend on the user-level uv cache.

### 2. `gz check` is red, and its output is hard to triage

Evidence:

- `uv run gz check` failed only at Preflight.
- `uv run gz preflight` shows one actionable issue: an orphan plan-audit receipt
  for `OBPI-0.0.57-01-nominal-id-doctrine`.
- The same `gz check` output emitted a huge advisory spec/test drift list with
  2773 advisory findings.

Interpretation:

This is a presentation and sensor-health problem. The actual blocking issue is
small, but it is buried inside very large advisory noise. That is exactly the
"sensor-health aggregator" gap named in `harness-engineering-appraisal.md`.

Recommended outcome:

`gz check` should render fail-closed blockers first in a compact table, then
advisories behind a count and drilldown command. The operator should not have to
scan thousands of advisory rows to identify the single exit-code cause.

### 3. The typecheck sensor scope is inconsistent

Evidence:

- `uv run gz typecheck` runs `uv run ty check src` and passes with 5 warnings.
- `uv run ty check .` fails with 41 diagnostics, mostly in mirrored executable
  skill scripts (`.gzkit/skills`, `.agents/skills`, `.claude/skills`,
  `.github/skills`) and BDD step glue.
- The duplicate skill diagnostics are one source defect multiplied across four
  mirrored surfaces.

Interpretation:

This is not merely "type errors exist." The deeper issue is that executable
agent-surface scripts are not within the canonical typecheck gate, while a raw
whole-repo typecheck over-reports mirror duplicates. Generated mirrors amplify
signal instead of collapsing it to canonical source.

Recommended outcome:

Add a canonical-source-only typecheck profile for executable governance
surfaces, for example `.gzkit/skills/**/scripts/*.py` plus `features/steps/**/*.py`,
then explicitly exclude generated mirrors or de-duplicate diagnostics by
canonical origin.

### 4. The core emergency is ceremony mechanization, not just model behavior

Evidence:

- GHI #516 records closeout defects: stale demo anchors, unit-test housekeeping
  in product-demo slots, multi-line command fragment splitting, REQ AND-clause
  coverage gaps, and Gate 5 bypass via `--next`.
- GHI #517 elevates this to six-pillar diagnosis: ADR authoring, OBPI authoring,
  ADR authoring evaluation, OBPI execution, ADR closeout, ADR audit.
- `gz-adr-closeout-ceremony` explicitly says the skill "Does NOT re-verify:
  Evidence (trusts Layer 1 proof)" while also making the walkthrough the human
  verification surface.
- `gz-obpi-pipeline` has a separate verify stage and stronger stage boundaries.

Interpretation:

Newer models worsen the situation by following the authored ceremony too
literally. But the root issue is that some ceremonies are still passive
presenters over Layer-1-authored shell/prose, while claiming governance-grade
verification. That creates false confidence: the operator becomes the real
validator at the worst possible moment.

Recommended outcome:

Use GHI #517 as the anchor. Score all six pillars against the seven dimensions
already written there. Do not implement a fix until the rubric identifies which
pillar failures are shared and which are local to closeout.

### 5. The model-regression taxonomy predicted the current shape

Evidence from `model-regression-taxonomy.md`:

- Over-cautious governance prompts can degrade modern model performance.
- Text-level remediation does not close skipped verification or confident
  guessing; closure requires mechanical gates.
- F4 names over-ceremony coupled to root-cause thinking.
- F9 names repetition for emphasis.
- F10 names implicit cross-file context dependencies.

Interpretation:

The current problem is not a surprise external shock. It is a known risk class
that has not yet been converted into enough runtime checks across the highest
value ceremonies.

Recommended outcome:

Treat the taxonomy as diagnostic vocabulary, not as the remediation itself.
Each F-category involved in a core ceremony should be paired with a mechanical
counterpart or explicitly left as human judgment.

### 6. Surface scale is now a first-order risk

Evidence:

- 53 skills mirrored into four skill surfaces.
- 20 canonical rule files mirrored across Claude and Copilot instruction
  surfaces.
- 235 ADR records and 126 pending pool ADRs.
- Root AGENTS is under its 40k budget but still large, and all AGENTS files
  total over 200k bytes.
- Operator reports that gzkit cannot reliably complete a 258K-window Codex run
  on GPT-5.5-class models.

Interpretation:

The current budget validators answer "is this below a cap?" They do not answer
"which instructions are still load-bearing for this task?" The harness appraisal
already names this as unmeasured: guides-vs-sensors balance has never been
tested, and harness fitness is unmeasured.

The 258K-window failure is the strongest evidence that "below cap" is the wrong
metric. A governance system that consumes the full run budget before the agent
can diagnose, modify, verify, and report has failed its operator-economy goal
even if every individual file passes a character budget validator.

Recommended outcome:

Promote "AGENTS.md as map, not encyclopedia" immediately, but do not confuse
dieting with truth. The emergency package needs two coupled tracks:

1. Context collapse: reduce the always-loaded surface to hard invariants,
   routing pointers, and task entrypoints.
2. Ceremony hardening: move verification out of prose and into observed runtime
   checks so removed prose is replaced by sensors, not by wishful memory.

## Outcomes To Discuss

1. Treat #517 as the emergency anchor. Do not create parallel umbrella GHIs
   unless a finding is outside #517's six-pillar scope.
2. First repair target should probably be closeout ceremony, because #516 has
   concrete reproducible failures. But do not assume it is the only broken
   pillar; run the #517 rubric first.
3. Add hook execution validation for Codex. The present orientation freshness
   check validates script presence and AST wiring, not harness execution.
4. Add a canonical-source-only typecheck profile for executable skill scripts
   and BDD step glue. Avoid mirror-duplicate diagnostics.
5. Redesign `gz check` output so the blocking reason is visible before advisory
   bulk output.
6. Defer new governance ambitions until the core ceremony audit finishes.
   Pending pool volume is already high enough that more doctrine can become
   another layer of unread pressure.

## Questions For The Three-Model Review

Ask each model to answer these with file/line evidence and to mark each answer
as `confirmed`, `contradicted`, or `unclear`.

1. Is the main failure "newer models are worse," or "gzkit has under-mechanized
   ceremonies that newer models expose more reliably"?
2. Which of the six #517 pillars currently have runtime fail-close boundaries
   comparable to `gz-obpi-pipeline`, and which are prose/skill-driven?
3. Does `gz-adr-closeout-ceremony` have any mechanical verification step that
   would catch empty demo stdout, stale anchors, or multi-line command
   fragmentation before human walkthrough?
4. Is the Gate 5 bypass via `--next` a local bug in closeout state transition,
   or evidence of a broader ceremony-state-machine pattern?
5. Does ADR-0.44.0 already cover the Codex SessionStart hook failure class, or
   is a narrower direct-fix/GHI needed for hook execution validation?
6. Which validator scopes currently validate authored configuration only, and
   which validate observed runtime behavior?
7. Is the massive advisory spec/test drift output useful, or does it degrade
   operator response by burying fail-closed blockers?
8. Which instructions in `AGENTS.md` are still load-bearing because no sensor
   exists, and which are redundant with existing validators?
9. Should REQs containing explicit `AND` clauses be rejected at brief authoring
   time, decomposed automatically, or supported by conjunct-level coverage
   checks?
10. Which always-loaded surfaces can be converted into routeable skill docs,
    command-discovered state, or validator-owned doctrine without weakening
    safety?
11. What is the smallest remediation package that restores trust in the heart
    of gzkit without adding another large prose layer?

## Recommended Analyst Split

Use #517's role split as canonical. If only three models are available, use:

| Analyst | Scope |
|---|---|
| Model A - lead architect | Integrate this report with #517; produce the 7x6 rubric and remediation order |
| Model B - codebase specialist | Read source and skills for all six pillars; produce evidence packets with function/file references |
| Model C - adversarial reviewer | Attack the diagnosis: list claims not proven by evidence, likely false positives, and missing failure modes |

Do not let any model produce only narrative. Require file paths, commands, and
observed outputs.

## Immediate Risk Register

| Risk | Severity | Evidence | Route |
|---|---|---|---|
| Codex SessionStart hook fails under sandbox while validator passes | High, patched in-session | exact hook command failed; orientation validator passed; replacement command passes with project-local uv cache | direct fix anchored to GHI #510 follow-up |
| Closeout ceremony passive presenter lacks REQ/evidence verification | Critical | GHI #516, #517 | #517 diagnosis, then pool ADR(s) |
| 258K-window Codex run cannot reliably carry gzkit through work | Critical | operator report during this review | immediate context-collapse track coupled to #517 |
| `gz check` hid one blocking preflight issue behind advisory bulk | High, orphan cleaned in-session | `gz check` failed Preflight; `gz preflight` showed one orphan receipt; `gz preflight --apply` cleaned it | output-design fix remains separate |
| Executable governance scripts outside `gz typecheck` scope | Medium/High | `gz typecheck` passes; `ty check .` fails with 41 diagnostics | typecheck-scope design |
| Large pending governance queue creates selection pressure and context load | Medium | 173 pending ADRs, 126 pending pool ADRs | pool triage / foundation triage |

## Bottom Line

The right frame is not "make prompts harsher" or "tell models to try harder."
The correct direction is to move the six core ceremonies from prose/skill
discipline toward observed runtime checks, with `gz-obpi-pipeline` as the
comparison target. Newer models are exposing the gap; they are not the only
cause of the gap.

After the operator's 258K-window report, the immediate bottom line is stricter:
gzkit must stop treating context as abundant. A governance rule that must be
read every turn is a runtime dependency. Keep only the hard invariants in that
dependency set; everything else must be routed, queried, or mechanically
enforced.
