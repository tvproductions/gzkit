# Audit D: were releases, gate results or closeouts accepted through the four gaps?

Date: 2026-09-30. Repo HEAD `c407aa69b`. This was a read-only diagnosis. Nothing in the repo was edited, no ledger rows were written and no issues were filed. Every historical rebuild ran on `git archive` extracts in this evidence directory.

Classification key:
- **EXPLOITED**: a pass or acceptance was recorded (ledger row, ARB receipt, or a push to origin) while the gap was hiding a failure.
- **EXPOSED-CLEAN**: the item depended on the gapped surface, but the evidence shows no failure was hidden.
- **UNDETERMINABLE**: the item was exposed, but the record needed to decide it does not exist. Each such row names what is missing.

Ledger note: `.gzkit/ledger.jsonl` mixes `", "` and `","` JSON spacing, so it was parsed with `json.loads` per line rather than grepped. Event names used: `gate_checked` (gate, status, command), `closeout_initiated` (mode), `attested`, `patch-release`, `obpi_receipt_emitted`, and `audit_receipt_emitted` (`receipt_event` = `validated` / `meta-receipt-bind`), all from `src/gzkit/ledger_events.py`.

---

## GHI #995: `gz validate --json` exited 0 on failure

**Window: 2026-01-19 (`09e510e93`) to 2026-09-13 (`9cc334ee4`).** The GHI's provenance paragraph is wrong. It dates the defect to `b27f42c92` (2026-05-02) because that is where `git log -S 'print(json.dumps(payload, indent=2))'` lands, but that commit added that string to a *different* function, `_render_attestation_result`, which does raise `SystemExit`. The actual aggregate branch, `if as_json: result = {"valid": len(errors) == 0, ...}; print(...); return`, sits ahead of the `raise SystemExit(1)` classification and is already present in the first code commit `09e510e93:src/gzkit/cli.py:508-512`. It moved into `validate_cmd.py` at `6ca086497` (2026-03-24) unchanged. The window is therefore about 8 months, not 4.5. The release notes should not repeat "since 2026-05-02".

**Population.** Every automated caller that could consume the exit status of `gz validate … --json`, plus every ledger acceptance that cites a `gz validate … --json` run as evidence.

**Method.**
1. Ran `git grep` for `validate … --json` in `.github/`, `.pre-commit-config.yaml`, `.gzkit/hooks`, `.claude/hooks`, `src/**/*.py`, `.gzkit/skills`, `.claude/skills`, `.agents/skills` and `features/`. This covered eight snapshots: 2026-02-15, 03-15, 04-15, 05-15, 06-15, 07-15, 08-15 and `9cc334ee4^`.
2. Read how `gz check` calls validate (`src/gzkit/quality.py` at `9cc334ee4^`).
3. Ran a regex over every ledger row in the window for `gz validate [flags] --json`.

| Dependent item | Evidence | Class |
|---|---|---|
| `gz check` steps | `quality.py:815-1064` at `9cc334ee4^` calls `uv run gz validate` and `uv run gz validate --<scope>` in plain mode only. No step passes `--json`. | EXPOSED-CLEAN (never consumed JSON status) |
| pre-commit / pre-push hooks | `.pre-commit-config.yaml:72,133` call `gz validate --bullet-retention …` and `--authorship` in plain mode. No `--json` at any snapshot. | EXPOSED-CLEAN |
| CI (`.github/workflows/`) | No `gz validate … --json` at any of the 8 snapshots. | EXPOSED-CLEAN |
| Skills / behave | The only `validate … --json` hits are `gz arb validate --json` (`features/arb.feature:43`) and `gz justify validate … --json` (gz-justify skill), which are different verbs, plus the parser epilog example `gz validate --briefs --json`. | EXPOSED-CLEAN |
| Test consumer | `tests/commands/test_validate_cmds.py::test_json_output_includes_frontmatter_errors` asserted the defect ("--json doesn't raise SystemExit"). The fix commit flipped it to assert 3. | EXPOSED (a test pinned the bug; no gate result rode on it) |
| OBPI-0.14.0-04 completion, 2026-03-16 (`obpi_receipt_emitted`) | key_proof reads "`uv run gz validate --instructions --json` detects 54 findings". The proof reads the body's findings, not the exit status. | EXPOSED-CLEAN |
| OBPI-0.0.36-03 completion, 2026-05-18 (`obpi_receipt_emitted`) | The evidence pastes `$ uv run gz validate --receipt-shape --json {"valid": true, "errors": []}`. The body reports clean, and the body was never affected by the defect. | EXPOSED-CLEAN |
| OBPI-0.35.0-06 acceptance rows, 2026-09-12 | These are the rows that discovered the defect and routed it to #995. They do not rely on it. | EXPOSED-CLEAN |

**Result: 0 EXPLOITED.** This agrees with the fix commit's caller survey, and it now covers the full 8-month window, not just the tree at the fix.

---

## GHI #1124: `gz tidy` findings never set the exit code; `--check` was a no-op

**Window: 2026-01-19 (`09e510e93`, where `def tidy(check_only, fix)` never reads `check_only` and never raises) to 2026-09-28 (`1a5317c89`).**

**Population.** Every gate, hook, CI step, skill or recorded acceptance that consumed `gz tidy`'s exit code.

**Method.**
1. Ran `git grep` for `gz tidy`, `"tidy"` and `tidy(` at 2026-02-15, 04-15, 06-15, 08-15 and `1a5317c89^`, excluding `docs/design` and ledgers.
2. Ran a ledger scan of every non-bookkeeping event for `gz tidy`.
3. Searched ARB receipts and ADR/OBPI docs.
4. Read the gz-tidy skill text at mid-window and just before the fix.

| Dependent item | Evidence | Class |
|---|---|---|
| gz check / pre-commit / pre-push / CI | No `gz tidy` invocation at any snapshot. | EXPOSED-CLEAN (never consumed) |
| Recorded gate results / receipts / attestations | 0 ledger events cite a `gz tidy` run (excluding `artifact_edited`, `obpi_created`, `obpi_parked`, `adr_created`, `agent_sync_completed`, whose matches are the word "tidy" in paths or titles). 0 `artifacts/receipts` files reference it. | EXPOSED-CLEAN (nothing recorded) |
| gz-tidy skill | Mid-window version (2026-06) says "Tidy is the routine check that surfaces it" and routes on the printed report. The `1a5317c89^` version says "The run exits 0 whatever it reports" (line 37) and lists "Reading tidy's exit code instead of its output" as a failure mode (line 127). It never relied on the exit code. | EXPOSED-CLEAN |
| `docs/user/runbook.md` § Verification Checklist (OBPI + ADR), `- uv run gz tidy` (added `329de1ccb`, 2026-03-26) | A human checklist item whose exit code was always 0. Nobody recorded the result anywhere, so there is no way to know whether a human took the 0 as a pass. | UNDETERMINABLE (missing: any record of checklist runs) |
| `docs/governance/governance_runbook.md` ("Run maintenance checks") and `pool-curation.md` ("During `gz tidy` sweeps") | These are process references to reading the report, not to its exit status. | EXPOSED-CLEAN |

**Result: 0 EXPLOITED, 1 UNDETERMINABLE** (the human checklist line).

---

## GHI #803: mkdocs validation downgrade withdrew dead-link enforcement from Gate 3

**Window: 2026-02-14 15:01 -0600 (`1593694e5`, "release: v0.3.1 with govzero parity updates") to 2026-09-29 04:19 -0500 (`d266be9ff`).** `git log -S"not_found: ignore" -- mkdocs.yml` returns exactly those two commits. `1593694e5` added the whole `validation:` block, including `links.not_found: ignore`, in the same change that moved `docs_dir` from `docs/user` to `docs`. The downgrade therefore shipped in the v0.3.1 tag commit itself, and **every one of the 74 tags ever cut (v0.3.1 to v0.34.7) falls inside the window.**

**Dead links at the fix.** Measured on the GHI (2026-09-29, at `817d2e700`): **226** `not_found` warnings once raised to `warn`. Of these, **122 are genuinely dead** (113 inside `docs/`, 9 outside) and **104 point at real files mkdocs cannot serve** (44 inside, 60 outside). The fix commit repaired **167 unique link sites** (56 converted to GitHub URLs, 48 moved from commands/ to manpages/, 19 repointed, 6 moved to a successor skill, 25 removed rows, 13 unlinked) and ended at 0 warnings.

**Method (reconstruction).**
- `build.py` (this directory) runs `git archive <commit> mkdocs.yml docs overrides config hooks`, rewrites only `links.not_found: ignore` to `warn`, runs `.venv/bin/mkdocs build`, and counts `not_found` link warnings. Each warning is then split into "target file absent from `git ls-tree <commit>`" (genuinely dead) and "target exists but is not served".
- **Calibration:** at `817d2e700` it reproduces the GHI's measurement exactly: 226 warnings, split 113/9/44/60.
- **Builds:** 546 builds across the distinct commits needed: every tag, the commit before every in-window `gate_checked` gate-3, `closeout_initiated` and `attested` row, the commit *after* each Gate-3 pass and heavy closeout (the bracket), the commit named by every `arb-step-mkdocs-*` receipt, and the commit before every completion or validation event that cites one.
- **Receipts:** 180 exist. For the 111 whose commit SHA no longer resolves (history rewritten), the commit is mapped by `timestamp_utc`.
- **Result:** every build had at least one `not_found` warning, and `--strict` fails on any warning. **The minimum genuinely-dead count at any bracketing commit is 51; the maximum is 177.**
- **Caveats:**
  - The gate ran on the working tree, which may hold uncommitted edits. 174 of the 180 receipts say `dirty: true`. One witnessed example of that divergence: at `dfa90412b` the committed tree also carried a nav `not_found` warning, and ADR-0.0.11's Gate 3 failed at 11:01Z, then passed at 11:03Z after an uncommitted nav fix.
  - It is not plausible that uncommitted edits removed 51 or more dead links for a single run and then restored them, since the before and after commits both carry them.
  - The **6 receipts with a clean tree and a resolvable SHA are exact**: `arb-step-mkdocs-9e138df2…`, `-6da3ee17…`, `-fae21e4c…`, `-349c3726…`, `-7cd5a4d4…` and `-abd1f4d4…`, at commits `f89520331`, `a04b106ed`, `82f8ab453`, `59dee63c0`, `5982340fc` and `a6cb5e3ee`. Each one is exit 0 with **125 genuinely dead links** in the tree it built.

### Population and verdicts

| Population (in window) | Count | Dead links at bracketing commits | Class |
|---|---|---|---|
| `gate_checked` gate 3, `uv run mkdocs build --strict`, status pass (2026-02-15 to 2026-07-31) | 148 (66 ADRs) | 51-177 | **EXPLOITED** (all 148) |
| `gate_checked` gate 3 mkdocs, status fail | 2 (ADR-0.8.0 2026-03-07; ADR-0.0.11 2026-04-02) | n/a | not a false pass; each was re-run to pass minutes later, and those re-runs are counted above |
| `closeout_initiated` mode heavy | 107 events / 59 ADRs | 51-177 | **EXPLOITED** (all 59 ADRs have a recorded Gate-3 mkdocs pass above) |
| `attested` (ADR, 97 completed + 3 partial) | 100 events / 82 ADRs | 51-177 | **EXPLOITED** for 75 events / 61 ADRs that have a recorded Gate-3 mkdocs pass. EXPOSED for 25 events / 21 ADRs (14 lite, 7 lane unrecorded) with no Gate-3 row, although several of them (for example ADR-0.0.23, 0.0.35 and 0.0.70) appear in the `validated` row below |
| `arb-step-mkdocs-*` receipts, exit 0 (2026-04-15 to 2026-09-28) | 179 (6 exact, 173 reconstructed) | 51-227 link warnings; 51-125 dead | **EXPLOITED** |
| `arb-step-mkdocs-*` receipt, exit 1 (`a77360fc…`, 2026-05-01) | 1 | n/a | not a false pass |
| `obpi_receipt_emitted` completions citing an `arb-step-mkdocs-*` receipt as Gate-3 evidence | 220 OBPIs (209 heavy-lane rows, 12 lite) | 51-125 | **EXPLOITED** |
| `audit_receipt_emitted` `validated` (ADR validation) citing a mkdocs receipt | 24 ADRs | 51-120 | **EXPLOITED** |
| `audit_receipt_emitted` `meta-receipt-bind` citing a mkdocs receipt | 38 subjects (2026-05-02 to 2026-09-28) | 51-125 | **EXPLOITED** |
| Git tags v0.3.1 to v0.34.7 | 74 | 64-183 warnings; 51-177 dead (table below) | shipped with dead links. Releases v0.34.0 to v0.34.7 went out after `368367ca0` (2026-07-26) put `mkdocs build --strict` in `gz check`, so their pre-push gate ran the blinded build. That pre-push pass is not recorded anywhere, so these are **UNDETERMINABLE** as recorded acceptances (missing: a pre-push log). The 66 earlier tags had no docs step in their release path, so the gap did not carry their acceptance; they are EXPOSED, not exploited. The ADR closeouts that produced the minor tags are EXPLOITED above. |
| `patch-release` ledger events | 33 (v0.24.3 to v0.34.7) | same as their tags | the event records no gate results; same split as the tags (v0.34.1 to v0.34.7 UNDETERMINABLE, rest EXPOSED) |

These rows overlap. A heavy ADR's closeout, its Gate-3 row, its OBPIs' receipt citations and its attestation are all one acceptance chain. Counted by **accepted subject**: **66 ADRs with a recorded Gate-3 mkdocs pass** (all 59 heavy-closeout ADRs among them; 61 of them attested), **220 OBPI completions** and **24 ADR validations**, all accepted on a docs gate that could not see dead links.

### Per-ADR Gate-3 / closeout table

| ADR | Gate-3 mkdocs passes (first..last) | dead links at those commits (min-max) | heavy closeouts | attested | Class |
|---|---|---|---|---|---|
| ADR-0.3.0 | 1 (2026-02-15..2026-02-15) | 72-72 | 1 | 1 (2026-02-15) | EXPLOITED |
| ADR-0.2.0 | 1 (2026-02-17..2026-02-17) | 72-72 | 0 | 0 | EXPLOITED |
| ADR-0.4.0-skill-capability-mirroring | 1 (2026-02-21..2026-02-21) | 71-72 | 3 | 3 (2026-03-01) | EXPLOITED |
| ADR-0.6.0-pool-promotion-protocol | 3 (2026-02-21..2026-03-21) | 71-72 | 2 | 2 (2026-03-06) | EXPLOITED |
| ADR-0.5.0-skill-lifecycle-governance | 1 (2026-03-01..2026-03-01) | 71-71 | 1 | 1 (2026-03-01) | EXPLOITED |
| ADR-0.7.0-obpi-first-operations | 2 (2026-03-07..2026-03-21) | 71-72 | 1 | 1 (2026-03-07) | EXPLOITED |
| ADR-0.8.0-gz-chores-system | 2 (2026-03-07..2026-03-07) | 71-71 | 1 | 1 (2026-03-07) | EXPLOITED |
| ADR-0.10.0-obpi-runtime-surface | 1 (2026-03-10..2026-03-10) | 71-72 | 1 | 1 (2026-03-10) | EXPLOITED |
| ADR-0.11.0-airlineops-obpi-completion-pipeline-parity | 1 (2026-03-12..2026-03-12) | 72-72 | 1 | 1 (2026-03-12) | EXPLOITED |
| ADR-0.12.0-obpi-pipeline-enforcement-parity | 1 (2026-03-13..2026-03-13) | 72-72 | 1 | 1 (2026-03-13) | EXPLOITED |
| ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir | 2 (2026-03-20..2026-03-21) | 72-72 | 0 | 2 (2026-03-20) | EXPLOITED |
| ADR-0.14.0-multi-agent-instruction-architecture-unification | 1 (2026-03-17..2026-03-17) | 72-72 | 1 | 1 (2026-03-17) | EXPLOITED |
| ADR-0.13.0-obpi-pipeline-runtime-surface | 2 (2026-03-18..2026-03-21) | 72-72 | 1 | 1 (2026-03-18) | EXPLOITED |
| ADR-0.15.0-pydantic-schema-enforcement | 1 (2026-03-18..2026-03-18) | 72-72 | 1 | 1 (2026-03-18) | EXPLOITED |
| ADR-0.16.0-cms-architecture-formalization | 1 (2026-03-19..2026-03-19) | 72-72 | 1 | 3 (2026-03-20) | EXPLOITED |
| ADR-0.18.0-subagent-driven-pipeline-execution | 1 (2026-03-21..2026-03-21) | 72-72 | 1 | 1 (2026-03-21) | EXPLOITED |
| ADR-0.0.3-hexagonal-architecture-tune-up | 2 (2026-03-24..2026-03-29) | 72-177 | 2 | 1 (2026-03-24) | EXPLOITED |
| ADR-0.0.4-cli-standards-presentation-foundation | 1 (2026-03-25..2026-03-25) | 72-177 | 1 | 1 (2026-03-25) | EXPLOITED |
| ADR-0.0.6-documentation-cross-coverage-enforcement | 2 (2026-03-27..2026-03-27) | 72-72 | 2 | 2 (2026-03-27) | EXPLOITED |
| ADR-0.1.0 | 1 (2026-03-27..2026-03-27) | 72-72 | 0 | 0 | EXPLOITED |
| ADR-0.20.0-spec-triangle-sync | 2 (2026-03-27..2026-03-27) | 72-72 | 2 | 2 (2026-03-27) | EXPLOITED |
| ADR-0.21.0-tests-for-spec | 1 (2026-03-27..2026-03-27) | 72-72 | 0 | 1 (2026-03-27) | EXPLOITED |
| ADR-0.22.0-task-level-governance | 1 (2026-03-28..2026-03-28) | 72-72 | 0 | 1 (2026-03-28) | EXPLOITED |
| ADR-0.23.0-agent-burden-of-proof | 5 (2026-03-28..2026-03-29) | 72-177 | 2 | 1 (2026-03-28) | EXPLOITED |
| ADR-0.0.8-feature-toggle-system | 5 (2026-03-31..2026-03-31) | 174-174 | 5 | 1 (2026-03-31) | EXPLOITED |
| ADR-0.0.11-persona-driven-agent-identity-frames | 5 (2026-04-02..2026-04-02) | 174-174 | 4 | 1 (2026-04-02) | EXPLOITED |
| ADR-0.0.14-deterministic-obpi-commands | 8 (2026-04-06..2026-04-07) | 174-174 | 7 | 4 (2026-04-06) | EXPLOITED |
| ADR-0.25.0-core-infrastructure-pattern-absorption | 2 (2026-04-16..2026-04-16) | 108-108 | 2 | 1 (2026-04-16) | EXPLOITED |
| ADR-0.0.16 | 3 (2026-04-18..2026-04-18) | 108-108 | 4 | 1 (2026-04-18) | EXPLOITED |
| ADR-0.0.16-frontmatter-ledger-coherence-guard | 1 (2026-04-18..2026-04-18) | 108-108 | 0 | 0 | EXPLOITED |
| ADR-0.0.17-adr-taxonomy-mechanical | 8 (2026-04-19..2026-04-21) | 108-108 | 8 | 1 (2026-04-20) | EXPLOITED |
| ADR-0.0.19-pre-execution-reasoning-walkthrough | 3 (2026-04-22..2026-04-22) | 108-108 | 3 | 2 (2026-04-22) | EXPLOITED |
| ADR-0.0.21-chores-as-gzkit-surface | 4 (2026-04-28..2026-04-28) | 51-51 | 2 | 0 | EXPLOITED |
| ADR-0.0.22-security-sensitivity-doctrine | 1 (2026-04-29..2026-04-29) | 51-51 | 1 | 1 (2026-04-29) | EXPLOITED |
| ADR-0.26.0-governance-library-module-absorption | 9 (2026-05-02..2026-05-02) | 51-51 | 1 | 1 (2026-05-02) | EXPLOITED |
| ADR-0.0.24-attestation-receipt-binding | 1 (2026-05-02..2026-05-02) | 51-51 | 1 | 1 (2026-05-02) | EXPLOITED |
| ADR-0.0.25-obpi-completion-req-coverage-gate | 2 (2026-05-03..2026-05-03) | 51-51 | 5 | 1 (2026-05-03) | EXPLOITED |
| ADR-0.0.26-evaluation-feedback-loop-doctrine | 7 (2026-05-03..2026-05-04) | 51-51 | 2 | 1 (2026-05-04) | EXPLOITED |
| ADR-0.0.27-exemplar-corpus-doctrine | 1 (2026-05-05..2026-05-05) | 55-55 | 0 | 0 | EXPLOITED |
| ADR-0.0.28-complexity-threshold-doctrine | 4 (2026-05-06..2026-05-06) | 56-56 | 2 | 2 (2026-05-06) | EXPLOITED |
| ADR-0.0.29-complexity-advisor | 2 (2026-05-09..2026-05-09) | 111-112 | 3 | 2 (2026-05-09) | EXPLOITED |
| ADR-0.0.30-complexity-authoring-guidance | 1 (2026-05-10..2026-05-10) | 113-113 | 1 | 1 (2026-05-10) | EXPLOITED |
| ADR-0.0.32-canonical-surface-packaging | 1 (2026-05-15..2026-05-15) | 114-114 | 1 | 1 (2026-05-15) | EXPLOITED |
| ADR-0.0.33-agent-control-surface-fidelity | 1 (2026-05-16..2026-05-16) | 114-114 | 1 | 1 (2026-05-16) | EXPLOITED |
| ADR-0.0.34-agent-control-surface-rendering-substrate | 3 (2026-05-17..2026-05-17) | 114-114 | 4 | 1 (2026-05-17) | EXPLOITED |
| ADR-0.0.36-universal-obpi-attestation | 1 (2026-05-18..2026-05-18) | 114-114 | 1 | 1 (2026-05-18) | EXPLOITED |
| ADR-0.0.57-foundation-adr-nominal-id-triage | 3 (2026-05-23..2026-05-23) | 114-114 | 3 | 1 (2026-05-23) | EXPLOITED |
| ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine | 1 (2026-05-27..2026-05-27) | 115-115 | 1 | 1 (2026-05-27) | EXPLOITED |
| ADR-0.0.63-closeout-ceremony-runtime-engine-parity | 1 (2026-05-30..2026-05-30) | 115-115 | 1 | 1 (2026-05-30) | EXPLOITED |
| ADR-0.0.67-tool-skill-invariant1-enforcement | 2 (2026-06-09..2026-06-09) | 115-115 | 2 | 1 (2026-06-09) | EXPLOITED |
| ADR-0.0.68-green-between-sessions-gate | 1 (2026-06-09..2026-06-09) | 115-115 | 1 | 1 (2026-06-09) | EXPLOITED |
| ADR-0.0.69-channels-first-closeout-proof | 1 (2026-06-11..2026-06-11) | 115-115 | 1 | 1 (2026-06-11) | EXPLOITED |
| ADR-0.0.41-token-block-lock-discipline | 1 (2026-06-12..2026-06-12) | 117-117 | 1 | 1 (2026-06-12) | EXPLOITED |
| ADR-0.0.71-completion-repudiation | 1 (2026-06-13..2026-06-13) | 117-117 | 1 | 1 (2026-06-13) | EXPLOITED |
| ADR-0.0.73-verification-layer-binding-audit | 3 (2026-06-19..2026-06-19) | 117-117 | 1 | 1 (2026-06-19) | EXPLOITED |
| ADR-0.0.74-mx-mode-maintenance-hangar | 1 (2026-06-27..2026-06-27) | 119-119 | 1 | 1 (2026-06-27) | EXPLOITED |
| ADR-0.30.0-okf-documentation-knowledge-structure | 2 (2026-06-30..2026-06-30) | 119-119 | 1 | 1 (2026-06-30) | EXPLOITED |
| ADR-0.31.0-obpi-state-machine | 1 (2026-07-04..2026-07-04) | 119-119 | 1 | 1 (2026-07-04) | EXPLOITED |
| ADR-0.32.0-gzkit-ontology | 1 (2026-07-07..2026-07-07) | 119-119 | 1 | 1 (2026-07-07) | EXPLOITED |
| ADR-0.33.0-airlock-membrane | 2 (2026-07-12..2026-07-12) | 119-119 | 1 | 1 (2026-07-12) | EXPLOITED |
| ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine | 1 (2026-07-12..2026-07-12) | 120-120 | 1 | 1 (2026-07-12) | EXPLOITED |
| ADR-0.0.64-task-envelope-and-planning-decomposition | 1 (2026-07-13..2026-07-13) | 120-120 | 1 | 1 (2026-07-13) | EXPLOITED |
| ADR-0.0.72-meta-governance-coherence | 2 (2026-07-14..2026-07-14) | 120-120 | 1 | 1 (2026-07-14) | EXPLOITED |
| ADR-0.0.65-handoff-system-consolidation | 2 (2026-07-15..2026-07-15) | 120-120 | 1 | 1 (2026-07-15) | EXPLOITED |
| ADR-0.0.37-constitutional-invariant-composition | 3 (2026-07-17..2026-07-18) | 120-120 | 1 | 1 (2026-07-18) | EXPLOITED |
| ADR-0.34.0-foundation-sunset | 8 (2026-07-19..2026-07-31) | 117-123 | 1 | 1 (2026-07-31) | EXPLOITED |

"Dead links" is the count of link targets absent from `git ls-tree` at the commit before each event and the commit after it. "Class" applies to the ADR's recorded Gate-3 pass(es).

### ADR `validated` receipts that cite a mkdocs receipt

| ADR | validated receipt ts | commit at ts | dead links |
|---|---|---|---|
| ADR-0.0.22-security-sensitivity-doctrine | 2026-04-30T01:09:10 | 72e306452 | 51 |
| ADR-0.0.23-agent-failure-mode-taxonomy | 2026-05-02T23:29:27 | 737d412aa | 51 |
| ADR-0.0.26-evaluation-feedback-loop-doctrine | 2026-05-04T00:33:51 | 0cbc5b35f | 51 |
| ADR-0.0.27-exemplar-corpus-doctrine | 2026-05-05T12:38:14 | a926a8751 | 55 |
| ADR-0.0.28-complexity-threshold-doctrine | 2026-05-06T01:18:01 | c3deb6937 | 56 |
| ADR-0.0.30-complexity-authoring-guidance | 2026-05-10T08:29:17 | 5fc01daa0 | 113 |
| ADR-0.0.33-agent-control-surface-fidelity | 2026-05-16T02:56:02 | b8c7b4305 | 114 |
| ADR-0.0.34-agent-control-surface-rendering-substrate | 2026-05-17T09:29:18 | 4e00e2742 | 114 |
| ADR-0.0.35-foundation-feature-invariance-test | 2026-05-17T21:59:37 | 1797fb859 | 114 |
| ADR-0.0.36-universal-obpi-attestation | 2026-05-18T11:14:25 | ece2d6a2a | 114 |
| ADR-0.0.57-foundation-adr-nominal-id-triage | 2026-05-23T16:21:19 | 497ec477c | 114 |
| ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine | 2026-05-27T09:27:27 | efd75d35d | 115 |
| ADR-0.0.63-closeout-ceremony-runtime-engine-parity | 2026-05-30T12:15:41 | 8095806ca | 115 |
| ADR-0.0.67-tool-skill-invariant1-enforcement | 2026-06-09T08:01:48 | 72b5d06ad | 115 |
| ADR-0.0.68-green-between-sessions-gate | 2026-06-09T23:11:48 | cc96766d8 | 115 |
| ADR-0.0.69-channels-first-closeout-proof | 2026-06-11T21:07:51 | 9f14bafb1 | 115 |
| ADR-0.0.70-turn-end-feedback-and-correction-mining | 2026-06-13T22:25:12 | da27a75c6 | 117 |
| ADR-0.32.0-gzkit-ontology | 2026-07-07T09:55:41 | 24352b8aa | 119 |
| ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine | 2026-07-12T23:41:05 | 79de42826 | 120 |
| ADR-0.0.64-task-envelope-and-planning-decomposition | 2026-07-13T00:21:05 | fe058ae11 | 120 |
| ADR-0.0.72-meta-governance-coherence | 2026-07-14T11:21:36 | 97ea3d1d5 | 120 |
| ADR-0.0.65-handoff-system-consolidation | 2026-07-15T23:54:10 | c55c810e7 | 120 |
| ADR-0.0.37-constitutional-invariant-composition | 2026-07-18T23:49:24 | 285408acb | 120 |
| ADR-0.34.0-foundation-sunset | 2026-07-31T12:26:25 | 4f6a0d579 | 117 |

### Tags

| Tag | Date | links not_found at tag | genuinely dead (target file absent) |
|---|---|---|---|
| v0.3.1 | 2026-02-14 | 77 | 72 |
| v0.4.0 | 2026-03-01 | 77 | 71 |
| v0.5.0 | 2026-03-04 | 77 | 71 |
| v0.6.0 | 2026-03-04 | 77 | 71 |
| v0.7.0 | 2026-03-06 | 77 | 71 |
| v0.8.0 | 2026-03-07 | 77 | 71 |
| v0.9.0 | 2026-03-09 | 77 | 71 |
| v0.10.0 | 2026-03-10 | 78 | 72 |
| v0.11.0 | 2026-03-12 | 78 | 72 |
| v0.12.0 | 2026-03-13 | 78 | 72 |
| v0.14.0 | 2026-03-17 | 78 | 72 |
| v0.15.0 | 2026-03-18 | 78 | 72 |
| v0.16.0 | 2026-03-19 | 78 | 72 |
| v0.17.0 | 2026-03-20 | 78 | 72 |
| v0.18.0 | 2026-03-21 | 78 | 72 |
| v0.18.1 | 2026-03-21 | 78 | 72 |
| v0.19.0 | 2026-03-22 | 78 | 72 |
| v0.20.0 | 2026-03-27 | 78 | 72 |
| v0.21.0 | 2026-03-27 | 78 | 72 |
| v0.22.0 | 2026-03-28 | 78 | 72 |
| v0.23.0 | 2026-03-28 | 78 | 72 |
| v0.24.0 | 2026-03-29 | 183 | 177 |
| v0.24.1 | 2026-04-01 | 180 | 174 |
| v0.24.2 | 2026-04-05 | 180 | 174 |
| v0.24.3 | 2026-04-08 | 180 | 174 |
| v0.25.0 | 2026-04-15 | 114 | 108 |
| v0.25.1 | 2026-04-15 | 114 | 108 |
| v0.25.2 | 2026-04-16 | 114 | 108 |
| v0.25.3 | 2026-04-16 | 114 | 108 |
| v0.25.4 | 2026-04-16 | 114 | 108 |
| v0.25.5 | 2026-04-16 | 114 | 108 |
| v0.25.6 | 2026-04-16 | 114 | 108 |
| v0.25.7 | 2026-04-16 | 114 | 108 |
| v0.25.8 | 2026-04-16 | 114 | 108 |
| v0.25.9 | 2026-04-17 | 114 | 108 |
| v0.25.10 | 2026-04-18 | 114 | 108 |
| v0.25.11 | 2026-04-18 | 114 | 108 |
| v0.25.12 | 2026-04-19 | 114 | 108 |
| v0.25.13 | 2026-04-19 | 114 | 108 |
| v0.25.14 | 2026-04-21 | 114 | 108 |
| v0.25.15 | 2026-04-23 | 120 | 108 |
| v0.25.16 | 2026-04-25 | 64 | 51 |
| v0.25.17 | 2026-04-26 | 64 | 51 |
| v0.25.18 | 2026-04-26 | 67 | 51 |
| v0.25.19 | 2026-04-30 | 67 | 51 |
| v0.26.0 | 2026-05-01 | 67 | 51 |
| v0.26.1 | 2026-05-05 | 73 | 55 |
| v0.26.2 | 2026-05-10 | 134 | 113 |
| v0.26.3 | 2026-05-15 | 136 | 114 |
| v0.26.4 | 2026-05-16 | 136 | 114 |
| v0.26.5 | 2026-05-17 | 136 | 114 |
| v0.26.6 | 2026-05-22 | 136 | 114 |
| v0.27.0 | 2026-05-24 | 138 | 115 |
| v0.27.1 | 2026-05-24 | 138 | 115 |
| v0.28.0 | 2026-05-24 | 138 | 115 |
| v0.28.1 | 2026-06-12 | 140 | 117 |
| v0.29.0 | 2026-06-27 | 142 | 119 |
| v0.30.0 | 2026-06-29 | 142 | 119 |
| v0.30.1 | 2026-07-01 | 142 | 119 |
| v0.30.2 | 2026-07-01 | 142 | 119 |
| v0.31.0 | 2026-07-04 | 142 | 119 |
| v0.32.0 | 2026-07-07 | 145 | 119 |
| v0.33.0 | 2026-07-12 | 145 | 119 |
| v0.33.1 | 2026-07-23 | 150 | 123 |
| v0.33.2 | 2026-07-25 | 146 | 119 |
| v0.33.3 | 2026-07-25 | 146 | 119 |
| v0.34.0 | 2026-07-31 | 144 | 117 |
| v0.34.1 | 2026-08-04 | 147 | 118 |
| v0.34.2 | 2026-08-08 | 149 | 118 |
| v0.34.3 | 2026-08-12 | 150 | 118 |
| v0.34.4 | 2026-08-18 | 152 | 118 |
| v0.34.5 | 2026-08-23 | 152 | 118 |
| v0.34.6 | 2026-08-29 | 153 | 119 |
| v0.34.7 | 2026-08-29 | 153 | 119 |

---

## GHI #1017: the mandatory `Task:` commit trailer had no automated witness

**Fix commits** (from `git log --all -E --grep="#1017([^0-9]|$)"`):
- `ade953705` (2026-09-20) re-tiered `commit_trailers` from `explicit` to `default`, so `gz check` reaches it at pre-push. It still read HEAD only.
- `98bec10c1` (2026-09-27) widened it to `@{upstream}..HEAD`.
- `1e03fbe3c` is a brief note, and the other matches are sync commits.

**Window.** The obligation began at `289d35a7e` (2026-05-27, GHI #552 strict mode: "src/tests commits MUST carry a `Task:` trailer … Enforced by `gz validate --commit-trailers`"). At that commit `commit_trailers` sits in `explicit_scopes` (`validate_cmd.py` `explicit_scopes` dict). No hook, workflow or `quality.py` step names it at `289d35a7e`, at 2026-07-15 or at `ade953705^`. So:
- Phase A, `289d35a7e` to `ade953705^` (2026-05-27 to 2026-09-20): no witness at all.
- Phase B, `ade953705` to `98bec10c1` (2026-09-20 to 2026-09-27): a HEAD-only witness.

**Did the GHI measure it?** No. The body says "How many commits already in history violate the invariant is **unmeasured**", and the close comment says "Not claimed: … a retroactive sweep". I measured it here.

**Method.** For every commit in `289d35a7e^..98bec10c1` (2402 commits, 0 merges), I applied the validator's own predicate: it touches a path starting `src/` or `tests/` and `has_task_trailer(message)` is False. The predicate was run once with the `98bec10c1` version of `tasks.py` and once with the current one; they gave identical verdicts. Push boundaries come from `git reflog show origin/main`, which has 509 "update by push" entries in this clone.

| Phase | Commits | Code commits | Code commits with no valid `Task:` trailer | Class |
|---|---|---|---|---|
| A: unwired (2026-05-27 to 2026-09-20) | 2245 | 1061 | **277** (25 are `gz git-sync` chore commits that swept src/tests files; 252 are authored commits). By month: May 25, Jun 21, Jul 17, Aug 120, Sep 94 | Invariant violated with no gate consulted. This is not a false pass by a gate, because no gate claimed to check it, but three surfaces claimed that `gz validate --commit-trailers` enforced it. The GHI names two instances: `872edb5` (2026-09-17, caught by hand; it is not an ancestor of `main`, so it was amended before push) and `84ea8e435` (published). **EXPLOITED (the documented claim "Enforced by gz validate --commit-trailers" was false for all 277)** |
| B: HEAD-only (2026-09-20 to 2026-09-27) | 157 | 74 | **3**: `1841c53d9`, `d98b520f3`, `d9c099add` | **EXPLOITED** (details below) |

Phase B details:
- **`d9c099add`** was pushed under the non-code `96cc65a75` with every gate green. The GHI reopen comment pastes `gz validate --commit-trailers` giving exit 0 at that tip.
- **`1841c53d9`** was never a pushed tip: origin moved past it with `ed034d6a4` and `64e712057` on top. This is the same HEAD-only blind spot.
- **`d98b520f3` is a new finding.** The reflog shows `d98b520f3 refs/remotes/origin/main@{2026-09-21 03:41:14 -0500}: update by push`, so it was the tip of its push after `ade953705` had wired the scope. HEAD-only reading cannot explain that escape. See the next section.

### New finding: the pre-push trailer witness is skipped by `--reuse-verified` (still live after `98bec10c1`)

- The pre-push hook is `uv run gz check --reuse-verified` (`.pre-commit-config.yaml`, `gz-check-pre-push`).
- `src/gzkit/check_fingerprint.py` keys the reuse on the **index tree** (`git write-tree`), "deliberately neither HEAD nor the working tree" (GHI #835, `4b5430527`, 2026-08-22).
- `commit_trailers` judges **commit messages and the pushed range**, neither of which is in that key.
- The mandated workflow is `git add -A` → `gz check` → commit → push. It records the fingerprint *before* the commit exists, while HEAD is still the previous commit. The pre-push run then prints "skipped — this exact tree … already passed" and the trailer scope never evaluates the new commit.
- Four code commits without a valid trailer reached origin **after** the `98bec10c1` fix:
  - `61eb84194`: carries `Task: TASK-deps-upgrade-ty-0.0.84`, which the validator's grammar rejects. Pushed as tip at 2026-09-27 18:48:14.
  - `d85a36ca3`: no trailer, pushed as tip at 21:32:07.
  - `4cb8cedbc`: no trailer, pushed as tip at 21:36:50.
  - `57a94bd58`: no trailer (2026-09-30, "test: drive the three guards…"). It is on origin under `c407aa69b`, inside the range the widened validator reads.
- An unskipped pre-push `gz check` would have exited non-zero on each of them. The skip is the one mechanism in the hook path that explains all five tip escapes. That is an inference: pre-push output is not recorded, so the skip line itself was not witnessed.
- I found no GHI for this. A search is not proof; it should go through `/ghi-author`, whose prior-art lookup is authoritative. Until it is fixed, "#1017 closed" does not mean the obligation binds.

---

## What the release notes can truthfully say

- **#803 (docs gate):** From v0.3.1 (2026-02-14), whose release commit introduced `links.not_found: ignore`, until the fix on 2026-09-29, `mkdocs build --strict` could not see dead links. Every release from v0.3.1 to v0.34.7 shipped docs with dead links: between 51 and 177 at each tag, and 122 at the fix, of 226 unresolvable link warnings. In that window the ledger records 148 Gate-3 docs passes, 107 heavy-lane closeouts across 59 ADRs, 75 ADR attestations (61 ADRs), 24 ADR validations and 220 OBPI completions whose Gate-3 evidence was a docs build that would have failed at the restored level. Their other gates are unaffected. Their Gate-3 docs evidence did not hold for dead links, though it did hold for nav integrity.
- **#995 (`validate --json`):** The defect dates from the first commit (2026-01-19), not 2026-05-02. No hook, CI job, `gz check` step or recorded acceptance read `--json`'s exit status in that window, so no gate result was accepted through it.
- **#1124 (`gz tidy`):** No gate, hook or recorded acceptance read tidy's exit code. The only exposure was one human checklist line in the runbook.
- **#1017 (`Task:` trailer):** From 2026-05-27 to 2026-09-27, 280 commits touching `src/` or `tests/` reached `main` without the trailer the rule made mandatory. For most of that period no automated check ran it, although three surfaces said one did. The notes should not claim the obligation is now enforced at push: the pre-push gate's `--reuse-verified` skip bypasses it in the standard verify-then-commit workflow, and four more such commits have landed since the fix.
