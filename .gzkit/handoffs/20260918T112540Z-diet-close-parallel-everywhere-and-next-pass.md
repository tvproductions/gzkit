---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-18T11:25:40Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260918T091028Z-control-surface-diet-landed-and-card-refresh.md
---

## Current State Summary

Continuation of the 2026-09-18 control-surface diet session (GHI #921), same day, second handoff. The first handoff's four advised steps were all ruled and worked. State at writing: `main` level with `origin/main`, tree clean, no OBPI locks, no pipeline, no open TASK, no pending Gate 5.

Landed since the predecessor, every commit behind a full `uv run gz check` exit 0 on a fully staged tree:

- `38e47df50` serial full-suite unittest retired from 22 chore criteria, four rules, six skills and the ARB examples; 16 chore ceilings 120 to 180 s. Measured first: serial 238 s, `uv run gz test` 91 s.
- `3d8722e3b` GHI #856 (reopened, then fixed): pipeline Stage 3 `BASELINE_VERIFICATION` and `gz arb` help derive the unittest argv from `CANONICAL_STEP_COMMANDS`; dispatch prompts name `uv run gz test`.
- `1c2dac56a` GHI #1021: nested generated `CLAUDE.md` importers removed (24 files); Claude gets subtree rules from `.claude/rules` only; Codex keeps 28 nested `AGENTS.md`.
- `44db91a4b` GHI #1026: ARB schemas caught up with their writers; `gz arb validate --limit 300` went from 39 invalid to 1 (a genuine catch).
- `2e44b60de` GHI #1022 adopter template gate rows; `e1fa4c4cd` GHI #1024 `governance-core.md` citations in `src/`.
- `9611e5e83` GHI #1027: coverage canonical moved to the parallel runner (493 s to 307 s, identical totals); `gz arb coverage` with no arguments is the canonical run.
- `f4d88882a` GHI #1025: Stage 1 to 2 gate renamed Justification Gate and fires on three observable conditions; two attested REQs on ADR-0.0.19 handled under an operator ruling.

Closed this session: #856, #1020 (superseded against OBPI-0.35.0-10), #1021, #1022, #1024, #1025, #1026, #1027. The `instructions-files-diet` chore run now passes all six criteria.

TWO ITEMS THE OPERATOR ASKED THIS HANDOFF TO CARRY WITH CARE

Item 1. Root `AGENTS.md` is 19,872 B against the 15,000 destination in `data/instructions_files_budget.json`; 4,872 B over. Agent-side trimming is exhausted. The binding constraint is `gz validate --bullet-retention`: ten Mechanical or Promotable scorecard rows (47, 50, 53, 54, 55, 57, 58, 59, 17e, 17f) must appear verbatim on a per-turn surface, and `_resolve_tier` reads the first corpus row containing the text, retired rows included, so a retired invariant entry pins its bullet permanently and re-capturing it as compressible is unreachable. Rehearsal showed about 2,400 B is recoverable from § Governance doctrine surfaces once those rows are free; about 700 B was taken by compressing around the anchors. Two routes exist and both are the operator's: (a) OBPI-0.35.0-10 (`status: Draft`, under TOPMOST ADR-0.35.0), whose REQ-01 reads classification from the live `CorpusEntry` and whose notes rule out the first-substring-hit lookup by name; (b) an ADR-level ruling on ADR-0.0.33 Invariant 1: whether a rule that already has a mechanical witness must still render verbatim on the every-turn surface. Route (b) is the faster one and needs no code; it would let the ten rows become pointers. Even with all ten freed the file lands near 17.4 KB, so reaching 15,000 also needs a second look at § Operator Doctrine (verbatim canon, operator-owned wording) and § Gate Covenant.

Item 2. Unaudited material, measured at writing. Rules: `.gzkit/rules/*.md` total 145,695 B across 24 rules; seven were trimmed this run; every rule at or under 8 KB was NOT audited part by part: pythonic 8,137, chores 6,990, hexagonal-architecture 6,851, complexity-doctrine 6,527, tool-skill-runbook-alignment 6,103, complexity-thresholds 5,608, adr-audit 5,521, cross-platform 5,492, security-sensitivity 5,487, mx-mode 5,287, gh-cli 4,892, model-selection 4,760, guardrail-feedback-prose 4,572, changelog-release-notes 3,876, gate5-runbook-code-covenant 3,388, brief-heading-conventions 2,465, models 1,971. `pythonic.md` loads on every Python edit and carries a long unreconciled-thresholds blockquote and a 138-violation narrative: the best first target. Skill bodies: 72 skills, 690,894 B total, none audited; only descriptions were trimmed. `gz-obpi-pipeline` is 122,302 B and 1,671 lines, roughly a sixth of the whole catalog, and loads in full on every OBPI run. Next largest: ghi-close 46,465, gz-session-handoff 42,238, ghi-author 31,152, gz-adr-closeout-ceremony 27,240, gz-tech-debt-review 21,422, gz-adr-audit 19,665, gz-patch-release 19,272, gz-adr-create 19,027, gz-health-audit 18,790. Most of that bulk is dated incident narrative and canonical-regression stories, the same material the rule pass lifted to rationale docs.

## Important Context

- Working mode for diet work stays "you propose, I rule, you land": full before and after per surface, operator rules A/B/C, then land. Tests that pin surface wording are invalid and get re-derived; `src/**` moves only under a GHI.
- A skill-body pass is NOT a rule pass. Skills carry procedure the pipeline executes; several are bound by attested REQs on Completed ADRs (ADR-0.0.19 bound two this session). Before trimming any skill, grep `tests/skills/` and `tests/cli/` for the skill name and read every `@covers` REQ literally. If a REQ literally asserts text being removed, that is operator escalation under `docs/governance/attested-req-subject-retirement.md` § The discriminator, not an edit. GHI #1025 is the first recorded instance; that doc still says there is none.
- `gz-obpi-pipeline` may only be edited, never run, by the agent: only the operator initiates OBPI work. A trim of it must keep every stage, dispatch and review step; lift narrative to a rationale doc, keep procedure.
- Each skill edit needs `metadata.skill-version` and `last_reviewed` bumps (some `last_reviewed` values are quoted strings and a test reads them as strings) and `uv run gz agent sync control-surfaces`. Each rule edit needs the version marker, the blockquote, the Coverage Ledger row in `docs/governance/advisory-rules-audit.md`, and a history lift.
- The verifier-pipe-gate hook refuses any verifier that is piped or not the last statement. Pattern that works: `cmd > log 2>&1; echo "REAL EXIT: $?"`. `ruff`, `coverage` and `gz arb` count as verifiers.
- Bullet-retention binds rule trims too: every Mechanical or Promotable scorecard row for a rule must stay a normalized substring of the rule. Verify anchors by script before presenting a trim.
- Full-suite timings on this machine (10 cores): `uv run gz test` about 91 s; `uv run gz check` several minutes; `uv run gz arb coverage` about 327 s.
- Workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts). Handoff system: this document; nothing else observed. GHI triage: eight issues closed and one filed-and-closed chain this session; #1019, #1023, #943, #921 remain open from this thread; queue not otherwise inspected. ADR/OBPI campaign: ADR-0.35.0 TOPMOST and Draft, unstarted, no locks; this session's diet blocker routes into OBPI-0.35.0-10; not freshly inspected with `gz adr status`. New R&D: untouched.

## Decisions Made

- [operator-ruled] Chore timeout ceiling (verbatim: "And, raise to 180"). Landed for the 16 chores at 120 s that carry the full-suite criterion.
- [operator-ruled] Serial unittest is retired everywhere it is a full-suite run (verbatim: "we shouldn't retain serial unittests, why not use parallel everywhere?" and "We want parallel everywhere unless you can give me a good reason why we can't."). Single-target runs, the pipe-gate fixtures and one negative control stay serial, with reasons recorded on GHI #856.
- [operator-ruled] GHI #1020 closes superseded against OBPI-0.35.0-10 rather than a narrow direct fix (verbatim: "A, A", first A).
- [operator-ruled] The retired 90 percent framing in skill bodies goes through a GHI, not under #921 (verbatim: "A, A", second A). Filed as #1025.
- [operator-ruled] Stage 1 to 2 gate stays conditional and fires on three named conditions instead of a confidence figure (verbatim: "A, then fix #1027").
- [operator-ruled] Attested REQs that literally assert a retired doctrine (REQ-0.0.19-04-06, REQ-0.0.19-05-04): treat each as a dated before/after assertion true on its date; repair the covering tests to assert what survives, keep the `@covers` bindings, record the amendment in the docstring and commit, and let the surfaces cite invariant 11 as the trigger they supersede (verbatim: "A, then write the successor handoff"). First ruling on the literal-assertion case.
- [operator-ruled] Direct repairs authorized by name: "fix #856", "fix #1021, then #1026", "do 4, then 5, then 1", "fix #1027".
- [agent-chose] GHI #1021: removed the nested `CLAUDE.md` importers entirely rather than emptying their bodies. This reverses the remedy ruled under GHI #923 (2026-08-31), whose premise that Claude never saw subtree rules was false; the close comment says so plainly.
- [agent-chose] GHI #1026: lint and step receipt `exit_status` accepts any integer, recording a signal death as it happened rather than normalizing to 128 plus N. One-line reversal if the operator prefers normalizing.
- [agent-chose] GHI #1027: `gz arb coverage` with no arguments runs the canonical argv, mirroring `gz arb typecheck`; arguments still forward to coverage.py. Chore ceiling for `coverage-40pct` 300 to 600 s.
- [agent-chose] GHI #856 was reopened rather than a fresh issue filed, because its close claimed exhaustive coverage of receipt-bearing spellings and missed one.

## Immediate Next Steps

1. Present these steps to the operator and wait for a ruling; none is authorized by this document.
2. Ask the operator to rule on the `AGENTS.md` destination (item 1 above): initiate OBPI-0.35.0-10, or give the ADR-0.0.33 Invariant 1 ruling that lets mechanically witnessed rows become pointers. Offer the measured figures: 19,872 B now, about 2,400 B recoverable from the ten pinned rows, 15,000 B destination.
3. If the operator draws diet pass two, start with `gz-obpi-pipeline` (122,302 B): read the whole file, grep tests for REQ bindings first, propose a lift of dated narrative to a rationale doc with full before and after, and land only on a ruling. Then `ghi-close`, `gz-session-handoff`, `ghi-author`.
4. For rules at or under 8 KB, start with `pythonic.md` (loads on every Python edit), same before/after rhythm, anchors verified by script.
5. Re-measure per-turn and on-edit loads after GHI #1021 [settled] and write a new proof beside `post-trim-2026-09-18.txt`; the on-edit figures in that file still include the double delivery.

## Pending Work / Open Loops

- GHI #921 stays open as the umbrella for the diet; the chore run itself is complete and passing.
- GHI #943: the paired Opus and Fable behavioral evaluation set is still owed; it needs a design conversation about what the pairs test.
- GHI #1019: GPT-6 Astra card registered unconsumed; run the `frontier-model-card-currency` chore when convenient.
- GHI #1023: a `gz` verb for BDD; filed, unselected.
- `docs/governance/attested-req-subject-retirement.md` says there is no known instance of a REQ literally asserting retired doctrine. GHI #1025 [settled] is one. Adding it as a worked example is doctrine text and wants the operator's wording.
- `gz arb coverage report` emits a receipt labelled `coverage` with a non-canonical command, so `gz arb validate` flags it. Predates this session; recorded on GHI #1027 [settled], not filed separately.
- `tests/` still carries five comment-level mentions of `governance-core.md` (recorded on GHI #1024 [settled]).
- Not run: whether the receipt-binding gate in `gz obpi complete` schema-validates a cited `arb-step-judge` receipt; the `coverage-40pct` chore end to end after its criterion changed (its three commands were each run individually).
- Class questions left with the operator, each named on its issue: derive the adopter template gate table from `manifest.json` (#1022 [settled]); a validator arm resolving rule-path citations in source (#1024 [settled]); a witness holding skill-body quotations of root-contract text to the live contract (#1025 [settled]).
- 36 chores show overdue on the staleness board; staleness gates nothing.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` prints `0	0` and `git status --short` prints nothing.
- `wc -c AGENTS.md` prints 19872.
- `find . -name CLAUDE.md -not -path "./.git/*" -not -path "./.venv/*"` prints only `./CLAUDE.md`.
- `uv run gz arb validate --limit 300 > out.log 2>&1; echo "REAL EXIT: $?"` exits 1 with exactly one error, the serial-unittest receipt `arb-step-unittest-7161a74d315047abb72483d9463fa8da`; any other error is new.
- `uv run gz chores run instructions-files-diet > out.log 2>&1; echo "REAL EXIT: $?"` exits 0.
- `gh issue list --state open --search "921 OR 943 OR 1019 OR 1023"` shows those four open.
- `uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"` exits 0 on a clean tree.

## Evidence / Artifacts

- `.gzkit/chores/instructions-files-diet/proofs/CHORE-LOG.md` (every ruling of the diet run verbatim, including the serial-criterion entry)
- `.gzkit/chores/instructions-files-diet/proofs/post-trim-2026-09-18.txt` and `.gzkit/chores/instructions-files-diet/proofs/baseline-2026-09-17.txt`
- `data/instructions_files_budget.json` (the enforced budgets) and `docs/governance/instructions-files-budget-history.md`
- `src/gzkit/governance/trust_audits/bullet_retention.py` (the lookup that pins the ten rows)
- `docs/governance/attested-req-subject-retirement.md`
- `tests/arb/test_unittest_runner_lockstep.py`, `tests/arb/test_coverage_runner_lockstep.py`, `tests/arb/test_writer_validator_lockstep.py`
- `tests/skills/test_skill_surface_sync_justify.py` and `tests/cli/test_justify_manpage.py` (the amended attested-REQ tests)
- `data/schemas/arb_advisor_verdict.schema.json`
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (122,302 B, the first target of a skill-body pass)
- Receipts: `arb-step-unittest-f2f093be40314ddb8f75940b86abd6fd`, `arb-step-coverage-f4548fc28b8543bfb80625c7cd5c8005`

## Settled Rulings

918 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
