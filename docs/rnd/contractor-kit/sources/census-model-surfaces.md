# Census of model-oriented control surfaces

**Date:** 2026-10-26. **Record:** `docs/rnd/contractor-kit.md`, the decision *"the census covers
every control in place, by kind"*. This is a source for that run. It holds facts only and makes no
design recommendation. The companion census of executable code controls (hooks as code,
validators, `gz check` steps, CI) is a separate track. A hook appears here only as the injector of
text into model context.

## Method

- **Canonical sets enumerated by listing:** `.gzkit/skills/*/` (73 directories), `uv run gz skill
  list` (73 active, the same names), `.gzkit/rules/*.md`, `.gzkit/personas/*.md`, `.gzkit/agents/`,
  `.claude/agents/*.md`, `.codex/agents/*.toml`, `.agents/`, `.gzkit/templates/*.md`,
  `.gzkit/chores/registry.json` and every `CHORE.md`, every `AGENTS.md` under the tree (excluding
  `.venv`), `CLAUDE.md`, `.claude/settings.json`, `.codex/hooks.json`.
- **Mirrors were compared** with `cmp` or `diff` against canon, and counted once as canon.
- **Mode-awareness was searched** case-insensitively across all of the above with the pattern
  `hangar|safe[ -]mode|drydock|mx\.json|gz mx|\bMX\b|standby|sea trial|harbor`. **Every hit was
  read in context** and classified as *conditions* (the text tells the model to act differently
  when the marker is open), *routes* (sends the model to `gz-mx`), *mentions* (cross-reference or
  provenance only), or a false positive.
- **Self-check / freshness:** frontmatter keys extracted per file; `gz validate --help` read for
  every scope that names a model surface; `src/gzkit/skills_audit.py` read for `last_reviewed`.

**Read in full:** the last fourteen entries of `docs/rnd/contractor-kit.md` (from line 2098);
`.gzkit/rules/mx-mode.md`; `.gzkit/personas/main-session.md`; `.claude/hooks/mx-awareness.py`;
`src/gzkit/mx/awareness.py` lines 1–74; `.claude/settings.json`; `.codex/hooks.json`;
`src/gzkit/hooks/codex.py` lines 100–150; `scripts/session_orientation.py` lines 55–100, 1166–1200
and 1330–1469; the MX branch of `.claude/hooks/pipeline-gate.py` (122–140) and
`.claude/hooks/verifier-pipe-gate.py` (25–48); the docstrings of every wired Claude hook.

**Sampled, not read in full:** skills (frontmatter and description for all 73; body text only
where the mode search hit, plus `gz-mx/SKILL.md` headings); rules other than `mx-mode.md`
(frontmatter, headings and mode-search hits); agent definitions (frontmatter for all; the body of
`implementer.md` lines 1–40); the other six personas (frontmatter keys only); templates (mode search
and consumer search only); chores (registry fields for all 40; `CHORE.md` bodies only where the mode
search hit).

**Role assignments for skills and rules are this census's judgment** from description, headings
and category. They are not a field the repo declares, so they are a reading and can be challenged.

**Gaps.**

- How a hook's text reaches the model depends on the harness's hook semantics. This census applies
  Claude Code's published rule (exit 0: stdout reaches context only for `SessionStart` and
  `UserPromptSubmit`; exit 2: stderr is fed back to the model). It did not observe it live. Rows
  whose reach depends on that rule are marked *reach unverified*.
- This subagent session received no MX banner, although `.gzkit/mx.json` is open (`"mode": "safe"`).
  So the banner did not reach this subagent's context. Whether any subagent receives
  `UserPromptSubmit` output was not tested further.
- CLI output that steers the model (guardrail prose, `gz` diagnostics, prompts built in code such
  as `src/gzkit/templates/author_prompts.py` and the dispatch frames in
  `src/gzkit/pipeline_dispatch.py`) is model-facing text produced by code. It is named under
  delivery channels but not inventoried row by row. It belongs on the boundary with the code census.
- Doctrine documents under `docs/governance/` that skills and rules point to (for example
  `docs/governance/safe-mode-doctrine.md`) are read on demand. They are not inventoried here.
- The harness skill list that `disable-model-invocation` controls was observed in this session only.

## 1. Skills (kind: skill)

**Canon:** `.gzkit/skills/<name>/SKILL.md`, 73 skills, matching `uv run gz skill list` (73).
**Mirrors, not counted:** `.claude/skills/` (73), `.agents/skills/` (73), and `src/gzkit/skills/`
(71, the wheel copy). The wheel copy omits `airlineops-parity-scan` and `gz-competitor-radar`, the
two skills carrying `project_local`. Three canonical skill directories carry their own `AGENTS.md`:
`.gzkit/skills/AGENTS.md`, `gz-mx/AGENTS.md` and `gz-obpi-pipeline/AGENTS.md`. These are generated
rule projections (§ 3b), not skill text.

**Self-check on every skill:** a `last_reviewed` frontmatter date (73/73). `gz skill audit`
(`src/gzkit/skills_audit.py`) emits `SKA-LAST-REVIEWED-AGING` (non-blocking) and
`SKA-LAST-REVIEWED-STALE` (blocking) against `DEFAULT_WARN_REVIEW_AGE_DAYS` and
`DEFAULT_MAX_REVIEW_AGE_DAYS` in that file. Catalogue-level witnesses: `gz validate
--how-coverage` (*"The gz-how guide catalogues every live skill and names only real ones"*),
`--router-tables` (*"Router slugs resolve; concrete skills are router-reachable"*),
`--skill-alignment` (*"Every CLI verb has a wielding skill"*), and `--cli-alignment` over skill
text. Skill directories also carry `metadata.skill-version`. The `persona:` key appears on 41 of
73 skills.

**Delivery:** 63 skills are model-invocable: their description appears in the harness skill list,
and the body loads on invocation. 10 carry `disable-model-invocation: true` and load only on an
operator `/` invocation: `git-sync`, `gz-big-picture`, `gz-chores`, `gz-context`, `gz-governance`,
`gz-health-audit`, `gz-manage`, `gz-project`, `gz-quality`, `gz-workflow`. In this session's skill
list, those 10 are absent and the other 63 are present.

| Skill | Role | `persona:` | `model:` | How it reaches the model | MX / safe mode today | Freshness witness | Other files in dir |
|---|---|---|---|---|---|---|---|
| `airlineops-parity-scan` | guidance — analysis or report | main-session | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `ghi-author` | guidance — governed authoring | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | references |
| `ghi-close` | guidance — reconcile, sync or repair | main-session | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | references |
| `ghi-triage` | guidance — analysis or report | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-24` | scripts |
| `git-sync` | gate procedure — gate, ceremony, receipt, lock or mode transition | main-session | haiku | operator `/` invocation only (`disable-model-invocation: true`) | no | `last_reviewed: 2026-10-23` | — |
| `gz-adr-audit` | gate procedure — gate, ceremony, receipt, lock or mode transition | pipeline-orchestrator | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | assets |
| `gz-adr-closeout-ceremony` | gate procedure — gate, ceremony, receipt, lock or mode transition | pipeline-orchestrator | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | references |
| `gz-adr-create` | guidance — governed authoring | main-session | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | references |
| `gz-adr-emit-receipt` | gate procedure — gate, ceremony, receipt, lock or mode transition | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-adr-evaluate` | guidance — analysis or report | pipeline-orchestrator | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | assets |
| `gz-adr-map` | guidance — analysis or report | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-adr-promote` | guidance — governed authoring | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-adr-status` | guidance — analysis or report | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-adr-sync` | guidance — reconcile, sync or repair | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-advisor-qc` | gate procedure — gate, ceremony, receipt, lock or mode transition | — | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-agent-sync` | guidance — reconcile, sync or repair | main-session | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-airlock` | gate procedure — gate, ceremony, receipt, lock or mode transition | main-session | haiku | skill invocation (description in the harness skill list) | mentions — SKILL.md:57–58, the mx door calls the airlock | `last_reviewed: 2026-10-17` | — |
| `gz-arb` | gate procedure — gate, ceremony, receipt, lock or mode transition | main-session | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-24` | — |
| `gz-big-picture` | guidance — analysis or report | main-session | opus | operator `/` invocation only (`disable-model-invocation: true`) | no | `last_reviewed: 2026-09-19` | — |
| `gz-check` | gate procedure — gate, ceremony, receipt, lock or mode transition | main-session | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-check-config-paths` | guidance — reconcile, sync or repair | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-chore-runner` | guidance — reconcile, sync or repair | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-24` | — |
| `gz-chores` | routing — namespace router | — | haiku | operator `/` invocation only (`disable-model-invocation: true`) | no | `last_reviewed: 2026-09-18` | — |
| `gz-cli-audit` | guidance — analysis or report | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-competitor-radar` | guidance — analysis or report | — | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | references, scripts |
| `gz-complexity-advisor` | guidance — analysis or report | — | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-22` | — |
| `gz-complexity-distill` | guidance — reconcile, sync or repair | — | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-complexity-guide` | guidance — analysis or report | — | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-22` | — |
| `gz-constitute` | guidance — governed authoring | — | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-content-compose` | gate procedure — gate, ceremony, receipt, lock or mode transition | — | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-content-remember` | guidance — governed authoring | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-context` | routing — namespace router | — | haiku | operator `/` invocation only (`disable-model-invocation: true`) | no | `last_reviewed: 2026-09-18` | — |
| `gz-context-diet` | guidance — reconcile, sync or repair | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-deps-upgrade` | guidance — reconcile, sync or repair | main-session | haiku | skill invocation (description in the harness skill list) | mentions — SKILL.md:63, provenance *"(drydock RO-9)"* | `last_reviewed: 2026-10-19` | — |
| `gz-design` | guidance — governed authoring | main-session | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-flighttest` | gate procedure — gate, ceremony, receipt, lock or mode transition | flight-test-engineer | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-foundation-triage` | guidance — analysis or report | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | scripts |
| `gz-governance` | routing — namespace router | — | haiku | operator `/` invocation only (`disable-model-invocation: true`) | no | `last_reviewed: 2026-09-18` | — |
| `gz-health-audit` | routing — namespace router | spec-reviewer | sonnet | operator `/` invocation only (`disable-model-invocation: true`) | no | `last_reviewed: 2026-09-19` | references |
| `gz-how` | routing — skill selector | main-session | sonnet | skill invocation (description in the harness skill list) + orientation note (*"consult `gz-how` first"*) | routes — SKILL.md:188 *"enter or leave the maintenance hangar \| `gz-mx`"*; references/repair.md:9 | `last_reviewed: 2026-10-17` | references |
| `gz-implement` | gate procedure — gate, ceremony, receipt, lock or mode transition | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-init` | guidance — governed authoring | — | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-insights-remember` | guidance — governed authoring | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-18` | — |
| `gz-intent-trace` | guidance — analysis or report | spec-reviewer | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-issue-file` | guidance — governed authoring | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-justify` | guidance — governed authoring | main-session | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-18` | — |
| `gz-manage` | routing — namespace router | — | haiku | operator `/` invocation only (`disable-model-invocation: true`) | routes — SKILL.md:26 *"mx hangar \| `gz-mx`"* | `last_reviewed: 2026-09-18` | — |
| `gz-migrate-semver` | guidance — governed authoring | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-mx` | gate procedure — gate, ceremony, receipt, lock or mode transition | main-session | haiku | skill invocation (description in the harness skill list) | conditions — the mode's own operator; SKILL.md:4 *"Use to open or exit the MX hangar or safe mode, or to check which mode is open."* | `last_reviewed: 2026-10-20` | AGENTS.md |
| `gz-obpi-brief-drift` | guidance — reconcile, sync or repair | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-obpi-lock` | gate procedure — gate, ceremony, receipt, lock or mode transition | main-session | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-obpi-pipeline` | gate procedure — gate, ceremony, receipt, lock or mode transition | pipeline-orchestrator | sonnet | skill invocation (description in the harness skill list) + hook (`pipeline-router.py` routes to `gz obpi pipeline`) | no | `last_reviewed: 2026-10-24` | references, AGENTS.md |
| `gz-obpi-simplify` | guidance — analysis or report | quality-reviewer | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-23` | — |
| `gz-obpi-specify` | guidance — governed authoring | main-session | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents, assets |
| `gz-obpi-sync` | guidance — reconcile, sync or repair | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-ontology` | guidance — analysis or report | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-patch-release` | gate procedure — gate, ceremony, receipt, lock or mode transition | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-22` | — |
| `gz-plan` | guidance — governed authoring | — | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-plan-audit` | gate procedure — gate, ceremony, receipt, lock or mode transition | main-session | sonnet | skill invocation (description in the harness skill list) + hook (`plan-audit-gate.py` self-runs `gz plan audit`) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-prd` | guidance — governed authoring | — | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-project` | routing — namespace router | — | haiku | operator `/` invocation only (`disable-model-invocation: true`) | no | `last_reviewed: 2026-09-19` | — |
| `gz-pythonic-pattern-apply` | guidance — reconcile, sync or repair | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-23` | — |
| `gz-pythonic-pattern-detect` | guidance — analysis or report | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-22` | — |
| `gz-quality` | routing — namespace router | — | haiku | operator `/` invocation only (`disable-model-invocation: true`) | no | `last_reviewed: 2026-09-18` | — |
| `gz-rnd` | guidance — governed authoring | main-session | opus | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-25` | assets |
| `gz-session-handoff` | guidance — governed authoring | main-session | sonnet | skill invocation (description in the harness skill list) | mentions — SKILL.md:245, provenance *"(drydock RO-1 act a, 2026-10-17)"* | `last_reviewed: 2026-10-17` | assets |
| `gz-skill-review` | guidance — reconcile, sync or repair | main-session | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | — |
| `gz-state` | guidance — analysis or report | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-status` | guidance — analysis or report | — | haiku | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-17` | agents |
| `gz-tech-debt-review` | guidance — analysis or report | quality-reviewer | sonnet | skill invocation (description in the harness skill list) | no | `last_reviewed: 2026-10-23` | — |
| `gz-tidy` | guidance — reconcile, sync or repair | main-session | haiku | skill invocation (description in the harness skill list) | no (SKILL.md:124 *"safe mode"* is a phrase about `--check`, not the mode) | `last_reviewed: 2026-10-17` | agents |
| `gz-validate` | gate procedure — gate, ceremony, receipt, lock or mode transition | — | haiku | skill invocation (description in the harness skill list) | conditions — SKILL.md:30 *"In an open MX hangar (`gz mx`), ERROR-level scopes report without failing;"* | `last_reviewed: 2026-10-17` | agents |
| `gz-workflow` | routing — namespace router | — | haiku | operator `/` invocation only (`disable-model-invocation: true`) | no | `last_reviewed: 2026-09-18` | — |

## 2. Rules (kind: rule)

**Canon:** `.gzkit/rules/*.md`, 26 rules. (`.gzkit/rules/AGENTS.md` is a generated projection;
`complexity-thresholds.json` is data.) **Mirrors, not counted:** `.claude/rules/*.md` (26,
generated, with the header *"Generated by gz agent sync — do not edit"*; frontmatter reduced to
`paths:`) and `src/gzkit/rules/*.md` (26, byte-identical to canon, the wheel copy).

**Self-check on every rule:** a `rule-version` marker, witnessed by `gz validate
--rule-version-markers` (*"Fail on .gzkit/rules/*.md missing or drifting the rule-version
marker"*). Also `--unscoped-rules` (no `paths: "**"` or missing `paths:`), `--advisory-scorecard`
(*"Every .gzkit/rules file appears in advisory-rules-audit scorecard"*),
`--instructions-files-budget` (the char budget for `.claude/rules/*.md`) and `--cli-alignment`.
No rule carries `last_reviewed`.

**Delivery:** every rule is path-scoped by its `paths:` list. On Claude, the `.claude/rules` mirror
loads when a matching file is touched. On harnesses that read nested `AGENTS.md`, the same body is
projected into the `AGENTS.md` of each matching subtree (§ 3b).

| Rule | Role | `paths:` scope (abridged) | MX / safe mode today | Version |
|---|---|---|---|---|
| `adr-audit.md` | gate procedure — the ADR audit sequence | `docs/design/adr/**` | no | 0.3.3 |
| `agent-failure-modes.md` | guidance — nine-pattern failure taxonomy | `AGENTS.md`, `.gzkit/rules/**`, `docs/governance/**` | no | 0.8.3 |
| `agents-md-map-doctrine.md` | guidance — shape and budget of per-turn instruction files | `AGENTS.md`, `CLAUDE.md`, `.claude/rules/*.md` | no | 0.13.1 |
| `brief-heading-conventions.md` | guidance — brief evidence headings (H3) | `docs/design/adr/**/obpis/**` | no | 0.2.1 |
| `changelog-release-notes.md` | guidance — release-doc authoring | `CHANGELOG.md`, `RELEASE_NOTES.md` | no | 1.2.2 |
| `chores.md` | guidance — chore workflow; *"Suppression is not a repair"* | `src/gzkit/chores/**`, `.gzkit/chores/**` | no | 0.6.4 |
| `cli.md` | guidance — CLI contract | `src/gzkit/commands/**` | no | 0.9.2 |
| `complexity-doctrine.md` | guidance — exemplar-corpus doctrine | complexity docs, data and code | no | 0.4.1 |
| `complexity-thresholds.md` | guidance — points to the threshold data file | the rule, its JSON, `thresholds.py`, schema | no | 0.6.0 |
| `cross-platform.md` | guidance — cross-platform coding | `src/**/*.py`, `src/gzkit/**/*.md`, `tests/**/*.py` | no | 0.8.1 |
| `gate5-runbook-code-covenant.md` | gate procedure — Gate 5 doc–code covenant | `docs/**`, `src/gzkit/**` | no | 0.3.2 |
| `gh-cli.md` | tripwire-by-instruction — *"route through `/ghi-author`, never `gh issue create`"*; prohibited commands | `.github/**`, `docs/design/adr/**`, `issue_cmd.py` | no | 0.7.1 |
| `guardrail-feedback-prose.md` | guidance — the form of guardrail output | `src/gzkit/hooks/**`, `src/gzkit/governance/**`, `.claude/hooks/**` | no | 0.3.1 |
| `hexagonal-architecture.md` | guidance — ports and adapters | `**/*.py` | no | 0.3.1 |
| `model-selection.md` | routing — model routing across skills and subagents | `pipeline_runtime.py`, `.gzkit/skills/**/SKILL.md`, `.claude/agents/**` | no | 0.7.2 |
| `models.md` | guidance — Pydantic policy | `src/**/*.py` | no | 0.2.1 |
| `mx-mode.md` | tripwire-by-instruction — honor the marker; do not shell `gz mx`; do not exit with defects | `src/gzkit/mx/**`, `.gzkit/skills/gz-mx/**`, `.claude/hooks/mx-awareness.py`, `src/gzkit/mx/awareness.py`, `src/gzkit/hooks/guards.py` | **conditions** — :23 *"Honor the marker: when `.gzkit/mx.json` exists, most guards drop to advisory"*; :25 *"Before every action in a session where `.gzkit/mx.json` exists, confirm the hangar is open."*; :122 *"Safe mode differs (ruling 2026-10-25)"*; :136 *"agents do not shell out to `gz mx enter` or `gz mx exit` directly"* | 1.13.0 |
| `pythonic.md` | guidance — Pythonic standards | `**/*.py` | no | 0.5.12 |
| `security-sensitivity.md` | gate procedure — security rigor at Gate 5 | `docs/design/adr/**/obpis/**`, `data/security_surfaces.json` | **conditions** — :29 *"The floor demotes to advisory inside the MX hangar — say so out loud. When `.gzkit/mx.json` exists, … `sensitivity` is **not** a member of that set"* | 0.6.1 |
| `skill-authoring.md` | guidance — how a skill is written | `.gzkit/skills/**` | no | 0.2.1 |
| `skill-surface-sync.md` | tripwire-by-instruction — edit canon, never the generated mirrors | `.claude/**`, `.agents/**`, `.gzkit/skills/**`, `.gzkit/rules/**` | no | 0.13.1 |
| `task-discovery.md` | guidance — TASK attribution channels | `src/gzkit/**`, briefs, `.gzkit/hooks/**` | no | 0.10.1 |
| `tests.md` | guidance — test policy (binding) | `tests/**` | no | 0.27.3 |
| `token-block-discipline.md` | tripwire-by-instruction — lock release coupled to a register entry | `lock_manager.py`, `obpi_lock` command, … | mentions — :48 *"applied to the token block as to the hangar"* (analogy) | 0.10.0 |
| `tool-skill-runbook-alignment.md` | guidance — CLI / skill / runbook invariants | `src/gzkit/commands/**`, `src/gzkit/cli/**`, `.gzkit/skills/**` | no | 0.5.3 |
| `weaponeering.md` | guidance — requirement kind fixes the sorties | `pipeline_dispatch.py`, `pipeline_runtime.py`, `gz-obpi-pipeline/**`, briefs | no | 0.1.1 |

**Fact on reach:** `mx-mode.md` is the binding rule for an open marker. Its `paths:` names only MX
code and the `gz-mx` skill. On a path-scoped harness it therefore loads only when one of those
paths is touched. An open marker does not load it.

## 3. Contract files (kind: contract-file)

### 3a. Authored

| File | Role | How it reaches the model | MX / safe mode today | Freshness / self-check witness |
|---|---|---|---|---|
| `AGENTS.md` (248 lines) | guidance + tripwire-by-instruction + gate procedure (Gate Covenant, PRIME DIRECTIVE, Behavior Rules) | always loaded: root contract for every harness; on Claude through `CLAUDE.md`'s `@AGENTS.md`. It is a playback of the `root` rendition from `.gzkit/corpus/AGENTS.md.jsonl` (`.gzkit/renditions/AGENTS.md/root.md`) | mentions — :237 *"Safe mode is the regime for a crisis the ordinary ceremony cannot govern: entered and left only through the gz-mx skill under a written contract, one exceptional period through harbor, drydock and sea trial, exit at seaworthiness."* | `gz validate --invariant-coherence`, `--rendition-freshness`, `--agents-md-map-conformance`, `--instructions-files-budget`, `--cli-alignment` |
| `CLAUDE.md` (26 lines) | guidance — Claude-only addenda (Invariant 10a, model tuning, compact instructions) | always loaded on Claude | no | `--instructions-files-budget`; template `.gzkit/templates/claude.md` |

A candidate rendition (`.gzkit/renditions/AGENTS.md/root.candidate.md:239`) words the same line as
*"Safe mode (martial law) is the regime …"*. It is not delivered.

### 3b. Generated nested `AGENTS.md` (rule projections)

Written by `gzkit.rules` (`_shared_subtree_rules`, `nested_agents_md_paths` in
`src/gzkit/rules/__init__.py`). Each holds the bodies of the rules whose `paths:` fall under that
subtree, with the header *"Generated by gzkit — do not edit manually"*. The sync-parity check
covers them (`src/gzkit/validate_pkg/sync_parity.py`, `_nested_agents_md`). **Delivery:**
directory-scoped, for harnesses that read nested `AGENTS.md`. 23 canonical locations exist. A
further 8 copies sit inside the skill mirrors (`.claude/skills/`, `.agents/skills/`,
`src/gzkit/skills/`: the `AGENTS.md` at the root of each, and in `gz-mx/` and `gz-obpi-pipeline/`).
These rows add no body that the rules in § 2 do not already hold.

| Location | Rules projected | MX / safe mode today |
|---|---|---|
| `.github/AGENTS.md` | gh-cli | no |
| `.gzkit/chores/AGENTS.md` | chores | no |
| `.gzkit/handoffs/AGENTS.md` | token-block-discipline | mentions (:43, analogy) |
| `.gzkit/hooks/AGENTS.md` | task-discovery | no |
| `.gzkit/locks/exchange/AGENTS.md` | token-block-discipline | mentions (:43, analogy) |
| `.gzkit/rules/AGENTS.md` | agent-failure-modes, skill-surface-sync | no |
| `.gzkit/skills/AGENTS.md` | model-selection, skill-authoring, skill-surface-sync, tool-skill-runbook-alignment | no |
| `.gzkit/skills/gz-mx/AGENTS.md` | mx-mode | **conditions** (:18 *"Honor the marker: when `.gzkit/mx.json` exists, most guards drop to advisory"*) |
| `.gzkit/skills/gz-obpi-pipeline/AGENTS.md` | weaponeering | no |
| `docs/AGENTS.md` | gate5-runbook-code-covenant | no |
| `docs/design/adr/AGENTS.md` | adr-audit, brief-heading-conventions, gh-cli, security-sensitivity, task-discovery, weaponeering | **conditions** (:203, the security-sensitivity clause) |
| `docs/governance/AGENTS.md` | agent-failure-modes | no |
| `docs/governance/complexity/AGENTS.md` | complexity-doctrine, complexity-thresholds | no |
| `src/AGENTS.md` | cross-platform, models | no |
| `src/gzkit/AGENTS.md` | cross-platform, gate5-runbook-code-covenant, task-discovery | no |
| `src/gzkit/chores/AGENTS.md` | chores | no |
| `src/gzkit/cli/AGENTS.md` | tool-skill-runbook-alignment | no |
| `src/gzkit/commands/AGENTS.md` | cli, tool-skill-runbook-alignment | no |
| `src/gzkit/complexity/AGENTS.md` | complexity-doctrine | no |
| `src/gzkit/governance/AGENTS.md` | guardrail-feedback-prose | no |
| `src/gzkit/hooks/AGENTS.md` | guardrail-feedback-prose | no |
| `src/gzkit/mx/AGENTS.md` | mx-mode | **conditions** (:18, as above) |
| `tests/AGENTS.md` | cross-platform, tests | no |

Four rules appear in no nested `AGENTS.md`: `hexagonal-architecture` and `pythonic` (`paths: **/*.py`),
`agents-md-map-doctrine` (root files and `.claude/rules/*.md`) and `changelog-release-notes` (root files).

## 4. Personas (kind: persona)

**Canon:** `.gzkit/personas/*.md`, 7. **Rendition, not counted:** `.agents/personas/*.md` (7, body
without frontmatter). Frontmatter keys on all 7: `name`, `traits`, `anti-traits`, `grounding`. No
`last_reviewed`. **Witnesses:** `gz validate --personas` (*"Validate persona files in
.gzkit/personas/"*); `gz personas drift` (*"Report persona trait adherence from behavioral
proxies"*). (`--persona-witness` checks that each ADR has a Persona section, not persona files.)

**Delivery (all 7):** on demand: `AGENTS.md` § Persona says *"Read the applicable definition in
`.gzkit/personas/` when assigning a role"*. Code-composed: `src/gzkit/pipeline_dispatch.py`
`_persona_frame` loads the persona body into the Implementer and Reviewer dispatch prompts.
Declarative: the `persona:` key on 41 skills names one of these.

| Persona | Role | Named by `persona:` on skills | MX / safe mode today |
|---|---|---|---|
| `main-session.md` | persona obligation — primary session | yes | no |
| `pipeline-orchestrator.md` | persona obligation — pipeline controller | yes | no |
| `implementer.md` | persona obligation — dispatched implementer (code-composed frame) | — | no |
| `spec-reviewer.md` | persona obligation — spec review (code-composed frame) | yes | no |
| `quality-reviewer.md` | persona obligation — quality review (code-composed frame) | yes | no |
| `narrator.md` | persona obligation — ceremony evidence | — | no |
| `flight-test-engineer.md` | persona obligation — flight test sortie | yes (`gz-flighttest`) | no |

## 5. Agent definitions (kind: agent-def)

**Five roles, three delivery copies each.** `.gzkit/agents/*.md` holds the canonical role
**bodies** for Codex. Per `.gzkit/agents/README.md`, they were *"captured verbatim, excluding YAML
frontmatter, from the shipped Claude definitions on 2026-09-12"*, with `roles.json`. Two copies are
generated or delivered from them. `.claude/agents/*.md` carries frontmatter plus body; all five
differ from `.gzkit/agents` by byte comparison, since they include frontmatter. `.codex/agents/*.toml`
is rendered by `gzkit.codex_roles.sync_codex_roles`. **Witness:** the coherence test named in the
README. No `last_reviewed`. **Delivery:** harness subagent dispatch (Claude `subagent_type`; Codex
roles), and pipeline dispatch for implementer and reviewers.

| Role | Role class | Claude frontmatter (keys) | MX / safe mode today |
|---|---|---|---|
| `git-sync-repo` | gate procedure — guarded sync | name, description, model, color | no |
| `implementer` | guidance — TDD per task, result contract | name, description, tools, model, permissionMode, maxTurns | no |
| `narrator` | guidance — ceremony evidence | name, description, tools, model, maxTurns | no |
| `quality-reviewer` | gate procedure — review stage (read-only tools) | name, description, tools, model, maxTurns | no |
| `spec-reviewer` | gate procedure — review stage (read-only tools) | name, description, tools, model, maxTurns | no |
| `.agents/verifier.md` (standalone) | guidance — citation and source verification | name, description, tools (`web_search, fetch_content, …`), model `anthropic/claude-sonnet-4`, thinking, output | no |

`.agents/verifier.md` has no canon under `.gzkit/` and no counterpart in `.claude/agents` or
`.codex/agents`. The harness that consumes its frontmatter dialect was not identified.

## 6. Chores (kind: chore)

**Registry:** `.gzkit/chores/registry.json`, 40 chores, each with `.gzkit/chores/<slug>/CHORE.md`
(40). The wheel copy `src/gzkit/chores/` ships 31 of them. It omits the five
`control-surface-*` chores, `frontier-model-card-currency`, `ghi-cross-reference-staleness`,
`ledger-vocabulary-inertness` and `test-consolidation-subtest-sweep`.
`.gzkit/chores/owasp-top10-2025-scan/` holds only `mapping.json` and its schema. It is not a
registered chore (commit `2a63a5d53`, the data contract for OBPI-0.47.0-01).

**Role (all 40):** a maintenance procedure the model executes on demand, through `gz-chore-runner`
or `gz chores show/plan/advise`. The registry's `rung` sets its authority. **Self-check:** every
entry has a `staleness` block (signal and period). `gz chores status` computes due bands, and the
SessionStart orientation renders *"Chores due or overdue"* when any is due. `gz validate
--chores-layout` constrains the layout. Each entry carries a `version` and a `nonAuthority` line.

| Chore | Class / rung | Lane | Staleness signal | Governing rule | MX / safe mode today |
|---|---|---|---|---|---|
| `arb-pattern-extraction` | mining / propose | lite | elapsed-time / 30d | — | no |
| `cli-contract-governance` | conformance / operator-only-repair | heavy | content-delta | `.gzkit/rules/cli.md` | no |
| `complexity-reduction-xenon` | conformance / repair | lite | content-delta | `.gzkit/rules/pythonic.md § Size Limits & Refactoring` | no |
| `config-paths-remediation` | conformance / repair | lite | content-delta | — | no |
| `control-surface-permission-consent-drift` | conformance / operator-only-repair | lite | elapsed-time / 30d | — | no |
| `control-surface-rule-conflicts` | coherence / propose | lite | content-delta | — | no |
| `control-surface-rule-vs-check-drift` | coherence / propose | lite | content-delta | — | no |
| `control-surface-skill-rule-reachability` | coherence / propose | lite | content-delta | — | no |
| `control-surface-validator-reachability` | coherence / propose | lite | content-delta | — | no |
| `coverage-40pct` | conformance / repair | lite | content-delta | `.gzkit/rules/tests.md § Coverage Floor (binding)` | no |
| `cross-platform-test-cleanup` | conformance / repair | lite | content-delta | `.gzkit/rules/cross-platform.md § Quick Reference` | no |
| `decommission-tautological-tests` | conformance / repair | heavy | accumulated-work | `.gzkit/rules/tests.md § Red-Green-Refactor (TDD Discipline — binding)` | no |
| `dependency-currency` | currency / propose | lite | elapsed-time / 30d | — | no |
| `doc-coverage` | conformance / repair | heavy | content-delta | `.gzkit/rules/gate5-runbook-code-covenant.md` | no |
| `eval-feedback-cluster` | mining / propose | lite | elapsed-time / 30d | — | no |
| `evidence-integrity-audit` | conformance / propose | lite | content-delta | `.gzkit/rules/adr-audit.md § Rules` | no |
| `exceptions-and-logging-rationalization` | conformance / repair | lite | content-delta | `.gzkit/rules/pythonic.md § Error Handling` | no |
| `failure-class-index` | mining / propose | lite | elapsed-time / 30d | — | no |
| `frontier-model-card-currency` | currency / operator-only-repair | lite | elapsed-time / 30d | `.gzkit/rules/agent-failure-modes.md` | mentions — CHORE.md:147 *"the drydock contractor kit adds once it lands"* |
| `frontmatter-ledger-coherence` | conformance / repair | heavy | content-delta | — | no |
| `ghi-cross-reference-staleness` | coherence / propose | lite | elapsed-time / 30d | — | no |
| `hardcoded-root-eradication` | conformance / repair | lite | content-delta | — | no |
| `instructions-files-diet` | curation / operator-only-repair | lite | accumulated-work | `.gzkit/rules/agents-md-map-doctrine.md § Budget` | no |
| `ledger-vocabulary-inertness` | coherence / propose | lite | content-delta | — | mentions — CHORE.md:28 *"The **MX Maintenance Hangar** ships a CLI (`gz mx`), a skill, and a hook"* |
| `memory-hygiene` | curation / operator-only-repair | lite | content-delta | — | no |
| `module-sloc-cap-radon` | conformance / repair | lite | content-delta | `.gzkit/rules/complexity-thresholds.md § Invariant` | no |
| `pep257-docstring-compliance` | conformance / repair | lite | content-delta | — | no |
| `pool-triage` | curation / propose | lite | accumulated-work | — | no |
| `pythonic-design-pattern-application` | conformance / repair | lite | content-delta | `.gzkit/rules/pythonic.md § Core Principles` | no |
| `pythonic-design-pattern-detection` | conformance / propose | lite | content-delta | `.gzkit/rules/pythonic.md § Core Principles` | no |
| `pythonic-refactoring` | conformance / repair | lite | content-delta | `.gzkit/rules/pythonic.md § Core Principles` | no |
| `quality-check` | conformance / propose | heavy | content-delta | — | no |
| `repository-structure-normalization` | conformance / repair | lite | content-delta | — | no |
| `session-correction-mining` | mining / propose | lite | elapsed-time / 30d | — | no |
| `skill-authoring-quality` | conformance / propose | lite | content-delta | `.gzkit/rules/skill-authoring.md` | no |
| `skill-command-doc-parity` | conformance / operator-only-repair | heavy | content-delta | `.gzkit/rules/gate5-runbook-code-covenant.md` | no |
| `skill-trigger-testing` | conformance / propose | lite | content-delta | — | no |
| `test-consolidation-subtest-sweep` | conformance / repair | lite | content-delta | `.gzkit/rules/tests.md § General Rules (binding)` | no |
| `test-isolation-compliance` | conformance / repair | lite | content-delta | `.gzkit/rules/tests.md § General Rules (binding)` | no |
| `test-manpage-examples` | conformance / repair | heavy | content-delta | `.gzkit/rules/gate5-runbook-code-covenant.md` | no |

## 7. Text injected into model context by hooks (kind: injected-text)

Wiring read from `.claude/settings.json` (Claude) and `.codex/hooks.json` (Codex). For the
reach rule applied, see *Gaps*.

| Injecting hook (event, matcher) | Text source | Channel and reach | Role | MX / safe mode today |
|---|---|---|---|---|
| `scripts/session_orientation.py` (Claude `SessionStart *` and `PreCompact *`; Codex `SessionStart startup\|resume\|clear\|compact`, `additionalContextLimit: 6000`) | rendered by the script: handoff account, exit bookmarks, campaign, git remote, most-recent handoff (with *"A handoff ADVISES; it does not authorize"*), session-handoff GHIs, OBPI claims, ADR pipeline state, conditional chores-due, conditional *"MX hangar"*, conditional guard canaries, *"Skill-awareness re-injection"* (`POST_COMPACTION_NOTE`, `SKILL_SELECTION_NOTE`) | stdout to context, both harnesses | guidance + routing (to `gz-how`) | **conditions, narrowly** — `_render_mx_hangar` (:1166) renders only *"when an MX hardening guard found something"* (:62), from `gz validate --mx-hardening` findings. The script carries no banner by design, :1458 *"No MX banner here: the per-turn mx-awareness hook prints it on every prompt"* |
| `.claude/hooks/mx-awareness.py` (Claude `UserPromptSubmit *`) | `gzkit.mx.awareness.get_banner` → `MX_BANNER` or `safe_mode_banner(contract)`; stdlib fallback `_banner_stdlib` in the hook | stdout to context every turn, Claude only | tripwire-by-instruction (mode placard) | **conditions** — awareness.py:20–24 *"SAFE MODE ACTIVE — OBPI initiation and brief ceremony are suspended under {contract}; most guards advisory; alarms off; gate5_invariants, the ledger through gz verbs and operator PII still bind; every act is one commit with its trailer; what it breaks goes on the punch list"*; awareness.py:13–14 *"MX MODE ACTIVE — most guards advisory; gate5_invariants and the PRIME DIRECTIVE still bind"* |
| `.claude/hooks/plan-audit-gate.py` (Claude `PreToolUse ExitPlanMode`) | prose in the hook; self-runs `gz plan audit` | stderr, exit 2 → model | gate procedure | no direct marker read |
| `.claude/hooks/verifier-pipe-gate.py` (Claude `PreToolUse Bash`) | `gzkit.verifier_pipe_gate.decide(...).reason` | stderr, exit 2 → model | tripwire | **conditions by silence** — :38–39 `if alarms_off(): sys.exit(0)  # safe mode: alarms are off until gz mx exit` |
| `python -m gzkit.hooks.codex` (Codex `PreToolUse Bash`) | same `decide(...).reason`, as `permissionDecisionReason` | JSON deny → model, Codex only | tripwire | **no** — `hook_output` (codex.py:114–136) calls `decide` with no `alarms_off` check |
| `.claude/hooks/ghi-triage-chat-silence.py` (Claude `PreToolUse Bash`) | stderr naming GHI #424 and the tokens | stderr, exit 2 → model | tripwire | no |
| `.claude/hooks/pipeline-gate.py` (Claude `PreToolUse Write\|Edit\|NotebookEdit`) | `pipeline_gate_message`; under the marker, `gzkit.mx.checkpoint.demote_notice` | refusal: stderr, exit 2 → model. Demotion notice: stderr, **exit 0** (*reach unverified*) | tripwire | **conditions** — :127–136; checkpoint.py:90–92 *"[MX advisory] guard 'pipeline-gate' reported a violation and was demoted to advisory by the open Maintenance Hangar marker (.gzkit/mx.json). It is NOT waived -- `gz mx exit` re-runs every guard at full strength."* |
| `.claude/hooks/obpi-completion-validator.py` (Claude `PreToolUse Write\|Edit\|NotebookEdit`) | lane and evidence refusals | stderr, exit 2 → model | gate procedure | no direct marker read |
| `.claude/hooks/stop-turn-feedback.py` (Claude `Stop *`) | lint findings and claim-grounding block messages | stderr, exit 2 → model | tripwire | no direct marker read |
| `.claude/hooks/pipeline-router.py` (Claude `PostToolUse ExitPlanMode`) | `pipeline_router_message(obpi_id)`, routing to `gz obpi pipeline` | stdout, exit 0 (*reach unverified*) | routing | no |
| `.claude/hooks/pipeline-completion-reminder.py` (Claude `PreToolUse Bash`) | reminder before `git commit`/`push` | stderr, exit 0 (*reach unverified*) | guidance | no |
| `.claude/hooks/session-staleness-check.py` (Claude `PreToolUse Write\|Edit\|NotebookEdit`) | stale-artifact warnings | stdout/stderr, exit 0 (*reach unverified*) | guidance | no |
| `.claude/hooks/post-edit-ruff.py` (Claude `PostToolUse Edit\|Write`) | ruff findings, *"so the agent sees the warning in the same turn"* (:11) | stderr, exit 0 (*reach unverified*) | guidance | no |

Wired but not model-facing: `scripts/settings_local_backup.py` (`SessionStart`, `Stop`; stderr
only on failure), `.claude/hooks/ledger-writer.py` (`PostToolUse`; exit 1),
`.claude/hooks/session-exit-bookmark.py` (`SessionEnd`). Present on disk and **not wired** in
`.claude/settings.json`: `ceremony-step-gate.py` and `control-surface-sync.py`.
`.claude/hooks/README.md:40,79` lists `session-start-advisement.py`, and
`gz-session-handoff/SKILL.md:245` names it, but the file is not in this repo. It is the adopter-side
fallback for projects without the orientation script.

**Witnesses:** `gz validate --orientation-freshness` (*"SessionStart orientation hook + script must
remain wired"*); the orientation measures its own size against `injected_hook_text.max_bytes` in
`data/instructions_files_budget.json` (`check_session_start_budget`); `check_hook_liveness` in
`src/gzkit/mx/awareness.py` checks that the banner hook is registered; `tests/hooks/test_mx_awareness.py`.

## 8. Templates (kind: template)

**Canon:** `.gzkit/templates/*.md`, 14. **Mirror, not counted:** `src/gzkit/templates/*.md` (the
wheel copy, plus `author_prompts.py` and `skills/`). **Delivery:** on demand. A `gz` verb renders
them, or a skill reads them. No `last_reviewed`. The witnesses are indirect: `--agents-md-map-conformance`
covers the AGENTS template shape, and `--distribution` covers the wheel copies.

| Template | Role (what it steers) | Consumer found by search | MX / safe mode today |
|---|---|---|---|
| `adr.md` | guidance — ADR scaffold | `gz plan` and sync code | no |
| `adr_pool.md` | guidance — pool ADR scaffold | `src/gzkit/commands/plan.py`, `gz-plan` | no |
| `obpi.md` | guidance — OBPI brief scaffold | `tasks.py`, `interview.py`, sync | no |
| `prd.md` | guidance — PRD scaffold | sync, `interview.py` | no |
| `constitution.md` | guidance — constitution scaffold | sync, registry | no |
| `agents.md` | guidance — adopter `AGENTS.md` scaffold | `sync_surfaces.py` | no |
| `claude.md` | guidance — adopter `CLAUDE.md` scaffold | `sync_surfaces.py` | no |
| `audit.md`, `audit_plan.md` | gate procedure — audit scaffolds | `audit_cmd.py` | no |
| `closeout.md` | gate procedure — closeout scaffold | `audit_cmd.py`, `version_sync.py` | no |
| `changelog.md` | guidance — changelog form | `validate_pkg/changelog.py` | no |
| `release_notes.md` | guidance — release-notes form | `gz-patch-release` | no |
| `release_package.md` | guidance — release package | `canonical_history.json` only | mentions — :21 *"Doctrine: `docs/governance/safe-mode-doctrine.md` § The Release Package."* |
| `safe_mode_contract.md` | gate procedure — the safe-mode entry contract | `gz-mx` skill, `mx-mode.md` | **conditions (mode-native)** — :4 *"The `gz-mx` skill reads this document before entry and refuses when a required section is"* …; :47 *"the alarms are off in safe mode (`gzkit.mx.alarms`)"* |

## 9. Other model-facing text found

| Path | Kind | Role | Delivery | MX / safe mode |
|---|---|---|---|---|
| `.gzkit/prompts/claude-alignment-tidy.md` | prompt | guidance — a reusable operator prompt | operator pastes; referenced only by `docs/evals/three-pillars-remedy-2026-09-19/corpus.json` | no |
| `.gzkit/gzkit-companion-adr-prompt.md` | prompt | guidance — an agent prompt for opsdev retirement | operator pastes; referenced by `docs/governance/storage-tiers.md` and the same eval corpus | no |
| `.gzkit/invariants/*.json` (4) | data read by code | — | rendered into `AGENTS.md` through the invariant registry (`--invariant-coherence`) | no |

## Counts

### Per kind (canon counted once)

| Kind | Canonical count | Mirror / rendition copies (not counted) |
|---|---|---|
| skill | 73 | 73 `.claude/skills`, 73 `.agents/skills`, 71 `src/gzkit/skills` |
| rule | 26 | 26 `.claude/rules`, 26 `src/gzkit/rules` |
| contract-file, authored | 2 (`AGENTS.md`, `CLAUDE.md`) | `.gzkit/renditions/AGENTS.md/` |
| contract-file, generated projection | 23 nested `AGENTS.md` | 8 more inside skill mirrors |
| persona | 7 | 7 `.agents/personas` |
| agent-def | 6 (5 roles + `.agents/verifier.md`) | 5 `.claude/agents`, 5 `.codex/agents` |
| chore | 40 | 31 `src/gzkit/chores` |
| injected-text (hook entries that reach or may reach the model) | 13 (9 reach by the published rule; 4 only *reach unverified*; `pipeline-gate`'s demotion notice is a fifth unverified output) | — |
| template | 14 | 14 `src/gzkit/templates` |
| other prompts | 2 | — |
| **Total** | **206** (183 excluding the 23 generated projections) | |

### Per role

| Role | skill | rule | contract | persona | agent-def | chore | injected | template | prompt | Σ |
|---|---|---|---|---|---|---|---|---|---|---|
| guidance | 47 | 18 | 1 (`CLAUDE.md`) | — | 3 | 40 | 4 | 10 | 2 | 125 |
| tripwire-by-instruction | — | 4 | — | — | — | — | 6 | — | — | 10 |
| gate procedure | 17 | 3 | — | — | 3 | — | 2 | 4 | — | 29 |
| routing | 9 | 1 | — | — | — | — | 1 | — | — | 11 |
| persona obligation | — | — | — | 7 | — | — | — | — | — | 7 |
| mixed | — | — | 1 (`AGENTS.md`) | — | — | — | — | — | — | 1 |

Notes. Injected *tripwire* here counts the mx-awareness banner and the five exit-2 refusals or
blocks (verifier-pipe Claude, verifier-pipe Codex, ghi-triage, pipeline-gate, stop-turn-feedback).
The orientation is counted as guidance, and it also routes to `gz-how`. The 23 nested `AGENTS.md`
inherit the roles of the rules they project and are left out of this table. Chores split by
registry `rung` as propose 17, repair 17 and operator-only-repair 6, and by `class` as conformance
25, coherence 6, mining 4, curation 3 and currency 2.

## Mode-awareness today

**Conditions on the mode, in text the model receives (8 canonical surfaces):**

1. Skill `gz-mx`: the mode's operator (*"Use to open or exit the MX hangar or safe mode, or to
   check which mode is open."*, SKILL.md:4).
2. Skill `gz-validate`: SKILL.md:30 *"In an open MX hangar (`gz mx`), ERROR-level scopes report
   without failing; CRITICAL-level scopes still fail."*
3. Rule `mx-mode.md`, with its two projections: :25 *"Before every action in a session where
   `.gzkit/mx.json` exists, confirm the hangar is open."*
4. Rule `security-sensitivity.md`, with its projection in `docs/design/adr/AGENTS.md`: :29 *"The
   floor demotes to advisory inside the MX hangar — say so out loud."*
5. Template `safe_mode_contract.md`: mode-native.
6. Injected: the per-turn banner (`mx-awareness.py` → `gzkit.mx.awareness`). Claude only.
7. Injected: the `pipeline-gate.py` demotion notice (exit 0, *reach unverified*).
8. Injected: the orientation's conditional *"MX hangar"* section. It is keyed to hardening findings,
   not to the marker being open.

In addition, `verifier-pipe-gate.py` conditions on the mode by **withholding** its refusal text
when alarms are off. Its Codex counterpart does not.

**Routes to the mode skill (2):** `gz-how` (SKILL.md:188, :249; references/repair.md:9–11) and
`gz-manage` (SKILL.md:26).

**Mentions only (8):** skills `gz-airlock`, `gz-deps-upgrade`, `gz-session-handoff`; rule
`token-block-discipline.md` (analogy); root `AGENTS.md:237`; template `release_package.md:21`;
chores `ledger-vocabulary-inertness` (CHORE.md:28) and `frontier-model-card-currency`
(CHORE.md:147). One false positive: `gz-tidy` SKILL.md:124.

**Silent on the mode:** 66 of 73 skills, 23 of 26 rules, `CLAUDE.md`, 7 of 7 personas, 6 of 6 agent
definitions, 38 of 40 chores, 12 of 14 templates, both loose prompts, and 9 of 13 injected-text
hooks. Among the silent skills are the ones whose ceremony safe mode suspends: `gz-obpi-pipeline`,
`gz-obpi-specify`, `gz-obpi-lock`, `gz-adr-create`, `gz-plan`. The banner says *"OBPI initiation
and brief ceremony are suspended"*. No text in those skills reads or names the marker.

**No surface reports its own suitability for function** (the outbound channel the record names).
The only self-report-shaped artifacts are external freshness witnesses: `last_reviewed` with
`gz skill audit`, `rule-version` markers, chore `staleness` blocks, and `check_hook_liveness`.

## Delivery channels

| Channel | Surfaces (canonical) | Harness |
|---|---|---|
| Always loaded at session start | 2 (`AGENTS.md`, `CLAUDE.md`); Codex loads `AGENTS.md` | both |
| Path-scoped rule load (`.claude/rules` `paths:`) | 26 | Claude |
| Directory-scoped nested `AGENTS.md` | 23 locations projecting 22 of 26 rules | harnesses that read nested `AGENTS.md` |
| Skill invocation, model-selectable from the description list | 63 | both (mirrors) |
| Skill invocation, operator `/` only | 10 | both |
| Hook injection, session start / pre-compact (stdout) | 1 (orientation) | Claude and Codex |
| Hook injection, every prompt (stdout) | 1 (MX banner) | Claude only |
| Hook injection, exit-2 refusal or block (stderr / JSON deny) | 6 (plan-audit-gate, verifier-pipe ×2, ghi-triage, pipeline-gate, obpi-completion-validator) + 1 Stop (stop-turn-feedback) = 7 | Claude 6, Codex 1 |
| Hook output on exit 0 (*reach unverified*) | 5 (pipeline-router, pipeline-completion-reminder, session-staleness-check, post-edit-ruff, pipeline-gate demotion notice) | Claude |
| Code-composed dispatch prompt | personas via `pipeline_dispatch._persona_frame` (implementer, reviewers); 5 agent roles via harness subagent dispatch | both |
| On demand (a skill, verb or contract line tells the model to read it) | 7 personas, 40 chores, 14 templates, 2 prompts, `.agents/verifier.md` | both |

## Divergences found in passing

These are recorded as facts. This census edits nothing.

1. **Two banner texts for safe mode.** `src/gzkit/mx/awareness.py:20–24` says *"… alarms off;
   gate5_invariants, the ledger through gz verbs and operator PII still bind; … what it breaks goes
   on the punch list"*. The stdlib fallback in `.claude/hooks/mx-awareness.py:44–51` says *"…
   gate5_invariants, the ledger through gz verbs, operator PII and the PRIME DIRECTIVE still bind;
   every act is one commit with its trailer and its witness"*. The fallback omits *alarms off* and
   keeps the PRIME DIRECTIVE, which `mx-mode.md:122` (*"Safe mode differs (ruling 2026-10-25)"*)
   relaxes for safe mode.
2. **The mode is not injected on Codex per turn.** `.codex/hooks.json` wires only `SessionStart`
   (orientation) and `PreToolUse` (verifier adapter). The orientation omits the banner by design
   (:1458). So a Codex session in an open marker sees the mode only if a hardening finding fires,
   or if it touches a path where `mx-mode.md` is projected.
3. **The verifier-pipe refusal is honored differently.** On Claude it goes silent under
   `alarms_off()`. On Codex (`gzkit.hooks.codex.hook_output`) it does not check.
4. **`AGENTS.md:167` contradicts `post-edit-ruff.py:8–9`.** The contract says *"the post-edit ruff
   hook strips unused imports immediately"*. The hook says it *"Reports lint issues without
   modifying files — avoids the import-removal problem where --fix deletes an import"*.
5. **Announced demotion may not reach the model.** `checkpoint.demote_notice` (*"Demotion is
   announced, never silent"*, checkpoint.py:85) is printed by `pipeline-gate.py` to stderr with exit
   0. Under the published hook rule, that reaches the user transcript, not the model.
6. **`mx-mode.md` is scoped to MX code paths**, not to the open marker (§ 2).
7. **`pipeline-router.py` routes to `gz obpi pipeline` with no marker read.** It does so although
   the safe-mode banner says OBPI initiation is suspended.
8. **Unwired hooks** (`ceremony-step-gate.py`, `control-surface-sync.py`) and a README entry for a
   hook absent from the repo (`session-start-advisement.py`).
