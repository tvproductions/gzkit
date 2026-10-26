# Census defect review — before filing

> A view over `docs/rnd/contractor-kit.md` and the two census files. It holds no authority. The
> agent prepared it on 2026-10-26 on the operator's ruling *"yes, but let's do one overall review
> before filing."* Each census finding was checked against the code. The verdict and the evidence
> are given for each, and the findings are grouped into proposed GHIs. Nothing is filed until the
> operator rules on this review.

Sources: `sources/census-code-controls.md` § 10d (C1–C15) and `sources/census-model-surfaces.md`
§ Divergences (M1–M8), plus one finding the model-census agent reported about itself (S1).

**Verdicts.**

- **Verified**: the agent read the code and saw the condition.
- **Counted**: the agent re-ran the census's count.
- **Census**: reported with file:line evidence, but not re-checked line by line.
- **By design**: the condition exists, and canon or an operator ruling chose it.
- **Not a defect**: the agent found the finding mistaken.

## Findings

| # | Finding | Verdict | Evidence the agent read |
|---|---|---|---|
| C1 | `.gzkit/mx.json` is tracked, and HEAD says `mode: safe`, so every clone and CI run is demoted | Verified | `git ls-files .gzkit/mx.json`; `git show HEAD:.gzkit/mx.json`; `checkpoint.hangar_demotes` reads only presence and `exiting` |
| C2 | In safe mode no `gz check` runs at push | Verified, **by design** under the safe-mode ruling (alarms off). It conflicts with canon that says the pre-push `gz check` is untouched (`gz-session-handoff` § Trust Model) | `.pre-commit-config.yaml` pre-push entry `gzkit.mx.alarms gz-check-pre-push`; `alarms.main` returns 0 when `alarms_off()` |
| C3 | The step demotion acts only on exit code 3; lint, format, typecheck, tests and the docs build still block | Verified | `quality.py`: `if getattr(result, "returncode", 0) != 3: ... return result` |
| C4 | `gz mx exit` re-runs the change scope, not `--full` | Verified | `mx_cmd.py:380`: `["uv", "run", "gz", "check"]` |
| C5 | 11 solo validator scopes bypass the checkpoint when invoked directly | Census | `validate_cmd.py` `_dispatch_early_return_scopes` exists, and its scopes were not traced one by one |
| C6 | Twin controls disagree: the Claude pipeline gate demotes while its commit-time twin is pinned CRITICAL; the Claude completion validator reads no marker while its twin is a floor member | Verified | `pipeline-gate.py:131-135` (`checkpoint.is_advisory`); `guards.py` `_GUARD_META`: `post-authoring-src-commits` CRITICAL; `obpi-completion-validator.py` has zero marker references |
| C7 | Two readings of *open*: the checkpoint covers both modes and an unreadable marker, and the alarms wrapper covers safe mode only. Neither checks the ledger binding | Verified | `checkpoint.hangar_demotes`; `alarms.alarms_off`; `is_valid` is called only in `contract.py:77`, `mx_cmd.py:484` and `preflight.py:170` |
| C8 | GATE5 floor: `secrets` and `operator-pii` are named but unenforced; gitleaks has no claim; `grader-gaming` has no production caller | Verified. gitleaks sitting **outside the checkpoint is by design** (operator, 2026-10-25), and its missing claim is the gap | `invariants.py:57` `_GATE5_NAMED_NOT_ENFORCED`; `proxy_reality` is referenced only by its own registration and NC |
| C9 | The GATE5 negative controls exercise sibling functions, not the six pre-commit guards | Census | invariants.py comment block (*"BOUND to a genuine gate5 production path"*), with the claim targets not traced |
| C10 | The enforcement floor runs at pre-commit, while its docstring says pre-push | Verified | `.pre-commit-config.yaml:63-66` `stages: [pre-commit]`; `guards.py` `_run_enforcement_floor` docstring *"as a pre-push guard"* |
| C11 | 96 of 134 claims have no canary, and 55 leave `exempts` undeclared | Counted | `production_enforcement_registry()` gives 134 claims and 55 with `exempts is None`; `data/guard_canaries.json` gives 38 |
| C12 | Hook drift: `ceremony-step-gate.py` and `control-surface-sync.py` are on disk but not registered | Verified | Neither appears among the scripts in `.claude/settings.json`. `control-surface-sync` is still named in `src/gzkit/hooks/claude.py` |
| C12b | The README lists `session-start-advisement.py`, which is absent | **Not a defect.** The README marks it *"only without `scripts/session_orientation.py`"*, and gzkit has that script | `.claude/hooks/README.md:40, 79` |
| C13 | Built-in self-tests exist only as 7 chore `--self-test` arms | Not a defect. It is the seed the operator named | census § 8 |
| C14 | 36 of 40 validator scopes outside `gz check` have no negative control | Census | census § 4 |
| C15 | `check-todos-fixmes` can never fail, and pre-commit hides its output on pass, so it surfaces nothing | Verified | `.pre-commit-config.yaml:100-102` (`\|\| true`) |
| M1 | The two safe-mode banners differ. The fallback omits *alarms off* and keeps the PRIME DIRECTIVE, which safe mode relaxes | Verified | `src/gzkit/mx/awareness.py:20-24` against `.claude/hooks/mx-awareness.py:44-51` |
| M2 | Codex gets no per-turn mode banner | Verified | `.codex/hooks.json` wires only `SessionStart` and `PreToolUse` |
| M3 | The Codex verifier pipe ignores safe mode, and its Claude twin honors it | Verified | `.claude/hooks/verifier-pipe-gate.py:31-39` calls `alarms_off()`; `src/gzkit/hooks/codex.py` has no MX reference |
| M4 | `AGENTS.md:167` says the post-edit ruff hook *"strips unused imports immediately"*, while the hook *"Reports lint issues without modifying files"* | Verified | `AGENTS.md:167`; `.claude/hooks/post-edit-ruff.py:8` |
| M5 | The demotion notice is printed to stderr on exit 0, which may never reach the model | Census, from the published hook rule. **Not tested live** | `pipeline-gate.py:135` |
| M6 | `mx-mode.md` loads only for MX code paths, not when the marker is open | Verified | `.gzkit/rules/mx-mode.md` frontmatter `paths: src/gzkit/mx/**, .gzkit/skills/gz-mx/**` |
| M7 | `pipeline-router.py` routes to the OBPI pipeline without reading the marker, while safe mode suspends OBPI initiation | Verified | no marker reference in `.claude/hooks/pipeline-router.py` |
| S1 | Subagents receive no safe-mode banner | Census, observed by the model-census agent of itself while the marker was open. The mechanism is not traced | the agent's report |

## Proposed grouping into GHIs

The groups put one defect class in each issue (DO IT RIGHT #1, *"Fix the class of failure, not the
instance"*). `ghi-author`'s prior-art step runs on each before filing, and any group already
carried by an open issue joins it.

1. **[#1271]** **`gz mx exit` does not re-run every guard at full strength** — C4. Fix ruled by the operator.
2. **[#1272]** **Safe-mode demotion acts only on exit code 3** — C3. Fix ruled by the operator.
3. **[#1273]** **The MX signal is read inconsistently** — C1, C2, C5 and C7: the tracked marker, the two
   readings of *open*, the missing ledger-binding check, the solo-scope bypass, and pre-push
   against canon. This is the operator's *"review the entire mx system"*. It is filed as the
   review's work order, and its fixes are decided there.
4. **[#1274]** **Twin controls disagree across harnesses and stages** — C6 and M3.
5. **[#1275]** **The mode does not reach the model** — M1, M2, M5, M6, M7 and S1: the banners differ, Codex
   gets no banner, the notice goes to stderr, the binding rule is scoped to code paths, the router
   ignores the marker, and subagents get no banner.
6. **[#1276]** **The GATE5 floor is partly unenforced** — C8 and C9.
7. **[#1277]** **Enforcement coverage gaps** — C10, C11 and C14: the floor's stage against its docstring,
   claims without canaries or `exempts`, and validators without negative controls.
8. **[#1278]** **Hook inventory drift** — C12: two unregistered hooks on disk.
9. **[#1279]** **A control that cannot fail** — C15.
10. **[#1280]** **`AGENTS.md` misstates the post-edit ruff hook** — M4. The fix runs through the content skills,
    because `AGENTS.md` is a generated rendition.

Not filed: C12b (not a defect), C13 (the seed of the built-in self-test).

**Filed 2026-10-26** through `ghi-author`, on the operator's *"yes, let's go with those"*: #1271 to #1280, numbered against the groups above. Prior art: #1263 already carried finding C1's CI side, so #1273 names it as a sibling, and a cross-link comment was posted on #1263. The coverage group (#1277) names the per-step witness family #1230 to #1241 and #1155 once, rather than cross-linking each.
