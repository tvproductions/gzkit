# Recommendation — six-source context audit (2026-11-08)

A dated record of steps 1–3 of `instructions-files-diet`, widened by operator
ruling 2026-11-08 ("All six sources") from the chore's three surfaces to every
source that loads into agent context: root `AGENTS.md`, path-scoped rules, auto
memory, hooks, session orientation, and the skill listing. Nothing has been
edited. Every item below waits for an operator ruling (§ 4).

Standard applied: Anthropic's current guidance
(https://code.claude.com/docs/en/memory, https://code.claude.com/docs/en/best-practices,
read 2026-11-08, no last-updated date shown) — "target under 200 lines per
CLAUDE.md file"; "Only write down what Claude can't find by reading the repo";
procedures belong in skills; enforcement belongs in hooks and validators, not
prose; hooks for preferences should be deleted. Path-scoped rules load on
Read/Write/Edit (or `cat`/`head`) of a matching file; `MEMORY.md` loads its
first 200 lines or 25 KB every session.

Per-source tables: `audit-rules-2026-11-08.md`,
`audit-hooks-orientation-skills-2026-11-08.md` (this directory). The auto-memory
table is kept outside the repository because the memory files carry operator
PII; its findings are summarized in § C without names.

## Measured load (bytes)

| Source | Per session | Notes |
|---|---|---|
| Root `AGENTS.md` | 24,906 (248 lines) | over the 200-line target |
| `MEMORY.md` index | 7,798 | imperative rule summaries, not pointers |
| Skill listing | ~6,700 chars + ~1.5 KB overhead | budget 6,000 |
| Session orientation | ~4,000 | at start and after compaction; 20.6 s runtime |
| `CLAUDE.md` (project + user) | 2,798 | |
| MX banner | 359 per prompt | ~18 KB over 50 prompts |
| Rules, first read of a command `.py` | 47,427 (9 rules) | ~18 KB after band B |
| Rules, first read of a test | 33,596 | ~14.5 KB after band B |
| Rules, first read of an OBPI brief | 29,134 (7 rules) | ~4 KB after band B |

A typical coding session loads about 108–132 KB of gzkit instructions before work
starts.

## Step 1–2 findings that bind the rest

1. **The baseline cannot be composed (defect).** `gz content compose AGENTS.md
   --consumer root --candidate …` fails: "Invariant-floor violation: entry
   'corpus-governance-doctrine-surfaces-2026-10-18T07:45:29.432603+00:00' text not
   found verbatim in rendered text." The text is present verbatim at
   `AGENTS.md:239` and `--invariant-coherence` passes, so the composer cannot
   reproduce the committed rendition. Step 1 is blocked until this is fixed.
2. **The chore cannot reach the target on `AGENTS.md` alone.** Live entry bytes:
   invariant/Judgment 15,773; invariant/Mechanical 6,644; invariant/Promotable 459;
   compressible/Judgment 1,224. 98 % is `tier: invariant`, which the composer
   preserves verbatim. Reaching 200 lines needs operator retirement or retiering
   of invariant entries.
3. **The chore's standard differs from Anthropic's.** § 2(a) measures bytes
   against vendor delivery caps (Codex 65,536 B → "40,630 B of headroom").
   Anthropic's standard is adherence (≤200 lines). Under the first the surface
   passes; under the second it fails.
4. **The budget witness already reports the bloat, as advisory only.** 19 of 27
   rules over the 4,000-char per-file budget; rules total 155,521 B against
   60,000; nested `AGENTS.md` 222,649 B against 60,000; personas 24,879 B against
   12,000; skill descriptions 6,736 against 6,000. Agent definitions (10,814 B
   against 6,000) are a false reading: only ~650 B of descriptions reach the main
   session.

## Ranked bands

Ranked by bytes saved per session × how often the source loads, against meaning lost.

### A. Root `AGENTS.md` — operator canon (needs retirement/retiering)

- **A1. Governance doctrine surfaces (3,987 B).** Ten Mechanical entries restate
  "validator X enforces Y". The file already says a failing validator's message
  names its rule. Candidate: retire to `docs/governance/advisory-rules-audit.md`
  behind one pointer. Cost: the agent no longer sees the list before it trips a
  validator.
- **A2. Duplicated with skills.** Operator doctrine (2,674 B) states four rulings
  already carried verbatim by skills. The Gate covenant (2,492 B) restates
  `.gzkit/manifest.json` § verification.
- **A3. Stale line.** "the post-edit ruff hook strips unused imports immediately":
  the hook has run without `--fix` since GHI #239 (`post-edit-ruff.py:9`).

### B. Path-scoped rules — ~100 KB of 156 KB (64 %)

The audit splits the 156 KB into five categories:

| Category | Bytes |
|---|---|
| Binding instructions | 51,001 |
| Rationale, history, pedagogy | 39,621 |
| Procedure that belongs in a skill | 12,244 |
| Duplicated elsewhere | 26,886 |
| Already enforced by a validator, hook or test | 25,769 |

Top items, weighted by how often each rule loads:

| # | Rule | Saving | Action |
|---|---|---|---|
| B1 | `pythonic` (`**/*.py`) | ~5.9 KB | lift the size-limit essay and BLE001/PLC0415 history; file a GHI for the unresolved threshold conflict |
| B2 | `task-discovery` | ~5.5 KB | enforced at commit by hook and `--commit-trailers`; merge the remaining ~600 B into `tests`, delete the rule |
| B3 | `hexagonal-architecture` | ~4.4 KB | compress; narrow the glob to `src/**/*.py`; cite `tests/policy/test_import_boundaries.py` |
| B4 | `tests` | ~4.4 KB | reduce the catalogues to their witness lines |
| B5 | `gh-cli` | ~4 KB, plus 5.2 KB off every ADR read | path rules never load on Bash; move to `ghi-triage`/`ghi-author` |
| B6 | `chores` | ~7 KB | its procedure is `gz-chore-runner` |
| B7 | `token-block-discipline` | ~6.6 KB | drop `.gzkit/handoffs/**` from the glob; the validator enforces most of it |
| B8 | `agents-md-map-doctrine` | ~5.5 KB | fix the glob to canon paths; move the writing levers to `gz-context-diet` |

Also:
- compress `gate5-runbook-code-covenant` and narrow its glob;
- move `mode-contract` into the design skills;
- merge the two complexity rules;
- compress `mx-mode`.

A cross-cutting item needs a doctrine ruling: the rationale sentence in each
"Rule version" banner (~4.9 KB in all) is required by `skill-surface-sync` rule 2.

### C. Auto memory — ungoverned second copy of doctrine

51 topic files (54,959 B) and a 7,798 B index:

| Disposition | Files | Bytes |
|---|---|---|
| Duplicates canon | 27 | 28,788 |
| Stale or contradicted by canon | 16 | 17,874 |
| A real rule not yet in canon | 5 | 5,486 |
| Genuinely personal | 3 | 2,811 |

Index line 35 instructs a real-name attestor, against the `g0` and PII rules.
Several files push against `AGENTS.md`: "never ask questions", "ignore the skill",
"never recommend pruning". The five rules not in canon:

1. descriptive commit messages;
2. a silent skip or drop is a worst-class defect;
3. ceremonies are design occasions;
4. store content as markdown, validate with Pydantic, render as XML at the LLM boundary;
5. Stage 1 checks whether the objective is already met.

Candidate:
- capture the five into canon through the governed route;
- delete the 43 duplicate or stale files;
- cut the index to the 3 personal entries (~412 B).

### D. Hooks, orientation, skill listing

- **D1. Delete `prefer-lsp`.** It is a preference, not a rule. False positives
  were reproduced on `grep -v node_modules`, `git log | grep fix_ci` and any
  underscored token, and a repeat always passes.
- **D2. Retire the other preference hooks.** ghi-triage-chat-silence,
  pipeline-completion-reminder, session-staleness-check, pipeline-router, and the
  claim-grounding half of stop-turn-feedback. Four probably never reach the model
  (stderr, exit 0); confirm by reproduction first.
- **D3. Trim the orientation to ~2.6 KB.** Drop the empty sections, the
  repeats of the banner and `AGENTS.md`, and the "32 overdue" line. Remove the
  PreCompact registration, which saves ~20 s and a duplicate set of state writes.
- **D4. Shorten the MX banner** from 359 to ~110 B. Closing safe mode removes it.
- **D5. Make ~19 skills user-invoked only** (side-effecting ones and thin
  wrappers) and trim the `gz-rnd` description, bringing the listing to ~4.7 K
  chars. Check the skill chains first.

## Defects found in flight (to track)

1. The composer's invariant-floor failure (step 1 above).
2. Hook messages name nonexistent skills `/gz-obpi-audit` and `/prior-art`
   (`obpi-completion-validator.py:367`, `plan-audit-gate.py:311`, and the
   generator templates in `src/gzkit/hooks/scripts/`).
3. `obpi-completion-validator` still branches on Heavy/Foundation lane for human
   attestation; Gate 5 is universal.
4. The orientation hook mutates state on every run: fetch, lock reaping, ledger
   rows.
5. `plan-audit-gate` reads the global `~/.claude/plans/`.
6. `stop-turn-feedback` lints every git-dirty `.py` file, not only this session's.
7. The agent-definition budget measures whole files, not descriptions.
8. `pythonic.md:48–49` has a broken sentence ("`complexity_advise.py` is reads").
9. `pythonic.md` § Size Limits records an unresolved threshold conflict with no GHI.
10. `security-sensitivity` names an unenforced path with no GHI.
11. `models.md` omits its witness, `gz validate --pydantic-models`.
12. `hexagonal-architecture` § Verify cites `gz lint`/`gz typecheck`, which do
    not check import purity.
13. `agents-md-map-doctrine` and `model-selection` are scoped to generated
    mirrors, not canon.
14. `gh-cli`, `task-discovery` and `mx-mode` bind at shell, commit or session
    time, which a path-scoped rule cannot reach.
15. `storage-tiers.md` forbids environment variables in config, while the feature
    flags read `GZKIT_FLAG_*` (`src/gzkit/flags/service.py:93`).
16. Auto-memory index line 35 (real-name attestor).

## Not yet verified

- Whether a loaded rule stays in context after `/compact`. The verbatim docs
  don't say.
- Whether the four stderr/exit-0 hooks reach the model.
- Whether nested `AGENTS.md` files load under this install's "Project
  instructions" setting.
