# Reachability Matrix — Control Surface Skill ↔ Rule Audit (Pass B)

**Generated:** 2026-08-01 (re-run; supersedes the 2026-05-10 pass)
**Population:** 68 skills under `.gzkit/skills/**` × 25 rules under `.gzkit/rules/**`.
**Orientation:** rule-centric. The 2026-05-10 pass was skill-centric and enumerated
50 hand-picked (skill, rule) pairs, which cannot answer *"is this rule reachable at
all?"* — the question the chore's Overview actually poses. Every rule now gets a row.

## Reachability grades

| Grade | Meaning | Test |
|---|---|---|
| **R1 — cited** | A skill body names the rule file. An agent following the skill will read the rule. | `grep -E '(^\|[^a-z0-9-])<rule>\.md' .gzkit/skills/*/SKILL.md` |
| **R2 — mechanical** | A skill invokes a validator/verb that enforces the rule's invariant, without naming the rule. | `grep -oE 'gz validate --[a-z-]+' .gzkit/skills/*/SKILL.md` |
| **R3 — path-bound only** | The rule's `paths:` glob fires on a surface some skill touches, so a `paths:`-aware harness *may* auto-load it. Nothing in any skill routes to it. | glob ∩ skill working surface |
| **R3u — path-bound, universal glob** | Same, but the glob is `**/*` or `**/*.py`. The match is trivially true and carries no routing signal. | — |
| **R4 — unreachable** | Neither cited, nor mechanically enforced by a skill, nor path-bound. | — |

R3/R3u is **not** a honors verdict. Rule loading by `paths:` is a *vendor harness*
behavior (`.claude/rules/*.md` frontmatter), and `.gzkit/rules/*.md` is the canonical
surface, not the loaded one. A rule reachable only at R3 depends on a mirror the
chore's own scope declares a derivative.

## Matrix — all 25 rules

| # | Rule (`rule-version`) | Grade | Routing evidence | Gap statement |
|---|---|---|---|---|
| 1 | `adr-audit.md` (0.2.0) | **R3** | 18 skills reference `docs/design/adr/…`; none names the rule | No skill routes to the audit-sequence rule. `gz-adr-audit` — the skill whose entire subject is the audit — cites `tests.md` and never `adr-audit.md`. Unchanged from the 2026-05-10 row 2. |
| 2 | `agent-failure-modes.md` (0.4.0) | **R1** (1/68) | `gz-issue-file:82` — "`.gzkit/rules/agent-failure-modes.md` § Safeguard circumvention". Also embedded verbatim in the generated `.gzkit/rules/AGENTS.md` subtree map. | 67 of 68 skills never name the six-pattern taxonomy AGENTS.md § DO IT RIGHT points at. |
| 3 | `agents-md-map-doctrine.md` (0.3.0) | **R2** | `gz-context-diet:39` invokes `gz validate --instructions-files-budget` — the budget arm of the rule | **One-way link.** The rule's § Related names `.gzkit/skills/gz-context-diet/SKILL.md` as *"the operator-facing procedure this rule makes the mechanical default"*; `gz-context-diet` never names the rule back. The skill also does not invoke `--agents-md-map-conformance` (the shape arm). |
| 4 | `brief-heading-conventions.md` (0.1.0) | **R3** | 8 skills touch `docs/design/adr/**/obpis/**` (`gz-adr-create`, `gz-adr-evaluate`, `gz-adr-promote`, `gz-context`, `gz-obpi-simplify`, `gz-obpi-specify`, `gz-obpi-pipeline`, `gz-plan-audit`) | Zero cites and **zero skills invoke `gz validate --brief-headings`**. The 2026-05-10 pass graded rows 6/29/31 "yes (mechanical)" on the premise that the validator runs inside reconcile; no skill body carries that invocation today. The mechanical honor claimed then is not present now. |
| 5 | `changelog-release-notes.md` (1.1.0) | **R1 + R2** | `gz-patch-release` names the rule and invokes `gz validate --changelog` at :310 and :316 | None. Strongest reachability in the corpus alongside `tests.md`. |
| 6 | `chores.md` (0.3.0) | **R3** | `gz-chore-runner`, `gz-context-diet`, `gz-obpi-pipeline`, `gz-obpi-specify`, `gz-pythonic-pattern-{detect,apply}` touch `.gzkit/chores/**` | **Unchanged from the 2026-05-10 row 14.** The rule's § Layout discipline names `gz validate --chores-layout` as its fail-close; **no skill invokes it**, and `gz-chore-runner` — the rule's own § Related target — still does not cite the rule. The prior pass's remedy ("add §0 preflight") was never applied. |
| 7 | `cli.md` (0.3.0) | **R3** | 7 skills reference `src/gzkit/commands/…` | No skill routes an agent authoring a CLI verb to the exit-code map / help-text contract. Unchanged from row 5. |
| 8 | `complexity-doctrine.md` (0.3.1) | **R1** | `gz-complexity-distill` cites it (and is the rule's declared wielder) | None. |
| 9 | `complexity-thresholds.md` (0.4.0) | **R3** | 11 complexity-touching skills | Zero cites; no skill invokes `gz validate --complexity-thresholds`. The 2026-05-10 row 17 graded this "yes (mechanical) — invoked by the chore wrapper"; that invocation does not appear in any skill body. |
| 10 | `cross-platform.md` (0.5.0) | **R3** | `ghi-close`, `gz-obpi-simplify` are the only skills mentioning Windows / `as_posix` | Unchanged from row 12. `gz-check` runs ruff; no ruff rule enforces `.as_posix()`, and no skill names the invariant. |
| 11 | `gate5-runbook-code-covenant.md` (0.2.0) | **R3u** | `paths: docs/**, src/gzkit/**` — fires on nearly every skill | **Unchanged from rows 3, 18, 26.** Zero cites; no skill invokes `gz validate --doc-surface-parity`. The prior pass named this "the largest single doctrine-mechanization gap"; nothing moved in 83 days. |
| 12 | `gh-cli.md` (0.3.0) | **R1** (4/68) | `ghi-author`, `ghi-close`, `ghi-triage`, `gz-issue-file` | `git-sync` — the skill that pushes — still cites nothing. Unchanged from row 50. |
| 13 | `governance-core.md` (0.7.0) | **R1-mirror** | `gz-adr-create` cites **`.claude/rules/governance-core.md`** — the vendor mirror | Only skill naming the `paths: "**/*"` rule, and it names the derivative path. See § Mirror-path citations. |
| 14 | `guardrail-feedback-prose.md` (0.1.0) | **R3** | `ghi-triage:126`, `gz-tidy:30/38/67`, `gz-session-handoff:63/332`, `gz-plan-audit:295/296` reference `.claude/hooks/**` | Zero cites. The rule governs how guardrails phrase refusals to agents; **no skill in the catalog is about authoring or reviewing a hook**, so nothing routes an author to it. Weakest-reachability new rule. |
| 15 | `hexagonal-architecture.md` (0.2.0) | **R4 (orphan-by-collision)** | — | Zero skills cite the rule. Two skills cite a **same-named non-rule file**: `gz-design:137` and `gz-patch-release:65` both point at `docs/governance/hexagonal-architecture.md`. See § Name-collision hazard. AGENTS.md calls ports/adapters gzkit's *"primary code-architecture directive"*; no skill routes to the rule stating it. |
| 16 | `model-selection.md` (0.3.0) | **R3u + R2** | `paths: .gzkit/skills/**/SKILL.md` — every skill *is* the surface; 68/68 declare `model:` | No skill teaches model selection. Honored only as a frontmatter fact, never as a decision an author is routed through. |
| 17 | `models.md` (0.1.0) | **R3u** | `paths: src/**/*.py` | Zero cites. Unchanged from row 20: `gz-deps-upgrade` still walks the whole dependency-bump flow without routing to the stdlib-first / Pydantic-departure attestation. |
| 18 | `mx-mode.md` (1.0.1) | **R1** | `gz-mx` cites it; the rule's `paths:` names `.gzkit/skills/gz-mx/**` | None — bidirectional link. **Rule-internal defect:** `uv run gz validate --rule-version-markers` fails on this file (`marker=1.0.1 disagrees with block quote=1.0.0`). |
| 19 | `pythonic.md` (0.2.0) | **R1-mirror** | `gz-tech-debt-review:196` cites `.claude/rules/pythonic.md` | Mirror path. `gz-pythonic-pattern-{detect,apply}` — the two skills whose entire subject is Pythonic pattern application — cite `tests.md` but **not** `pythonic.md`. Unchanged from rows 36, 38. |
| 20 | `security-sensitivity.md` (0.5.1) | **R1** | `ghi-author` cites it | `gz-obpi-specify` (the brief-authoring skill) still does not route to the registry; unchanged from row 32. No skill invokes `gz validate --sensitivity`. |
| 21 | `skill-surface-sync.md` (0.10.0) | **R1** | `gz-complexity-distill`, `gz-obpi-sync` | `gz-agent-sync` — the rule's own mechanical wielder — does not name it. |
| 22 | `task-discovery.md` (0.5.0) | **R3u** | `paths: src/gzkit/**, docs/design/adr/**, .gzkit/**` | **New rule, worst routing gap.** The rule's § Invariant makes a `Task:` trailer **mandatory** on every `src/**` or `tests/**` commit. Exactly one skill (`gz-obpi-pipeline`) mentions TASK at all. `git-sync` — the skill that composes and lands commits — contains **zero** occurrences of `Task:`, `trailer`, `@advances`, or `TASK-`. See the § Named worked example below. |
| 23 | `tests.md` (0.13.0) | **R1** (5/68) | `gz-adr-audit`, `ghi-close`, `gz-check`, `gz-pythonic-pattern-{detect,apply}` | Best-cited rule. But every one of those cites is `§ Tests assert semantics, not strings` — see § Dangling section citations. |
| 24 | `token-block-discipline.md` (0.3.0) | **R2** | `gz-session-handoff:78` invokes `gz validate --lock-handoff-coupling` | **Partially closed since 2026-05-10.** The prior rows 24/39 were pure gaps; the handoff side is now mechanically enforced. `gz-obpi-lock` still neither cites the rule nor invokes the validator, so the lock-release side of the coupling remains unrouted. |
| 25 | `tool-skill-runbook-alignment.md` (0.2.0) | **R1** (2/68) + **R2** | `ghi-close`, `gz-complexity-distill`; `gz-tech-debt-review:94/156` invokes `gz validate --cli-alignment` | Both `ghi-close` citations point at a **section that no longer exists** — see § Dangling section citations. |

### Grade distribution

| Grade | Rules | Count | Share |
|---|---|---|---|
| R1 (cited by ≥1 skill, canonical path) | 2, 5, 8, 18, 20, 21, 23, 25 | 8 | 32% |
| R1-mirror (cited only via `.claude/rules/…`) | 13, 19 | 2 | 8% |
| R2-only (mechanical, never named) | 3, 24 | 2 | 8% |
| R3 / R3u (path-bound only — no routing) | 1, 4, 6, 7, 9, 10, 11, 14, 16, 17, 22 | 11 | 44% |
| R4 (unreachable) | 15 | 1 | 4% |

**Orphaned rules — no skill routes to them (R3 + R3u + R4): 12 of 25 (48%).**

## Dangling citations

Five distinct defects. Each is a skill pointing at something that is not there.

### D1 — `tool-skill-runbook-alignment.md § Commit-message discipline` (HARD)

`ghi-close:269` and `ghi-close:419` both cite:

> `.claude/rules/tool-skill-runbook-alignment.md` § Commit-message discipline (observed-output evidence)

The rule has five headings: `## Invariants`, `### Invariant 1/2/3`, `## When to apply`.
There is no *Commit-message discipline* section, and no bold lead-in of that name.
Rule version `0.2.0` **lifted it out** ("lifted pedagogy, canonical violations, and
enforcement details to rationale doc under GHI #327"); it now lives at
`docs/governance/tool-skill-runbook-rationale.md:43` § *Commit-message discipline for
skill-routing changes*. The rule file's only remaining trace is a `> See […]` pointer
on its last line. An agent following `ghi-close` step 7e opens the rule and finds nothing.

### D2 — `gz ledger tail` is not a registered verb (HARD)

`gz-content-compose:56`, inside a runnable ```` ```bash ```` block in step 6
("Confirm the output"):

```
gz ledger tail --event composition_candidate_emitted
```

Observed: `gz: error: argument command: invalid choice: 'ledger'`.

**`uv run gz validate --cli-alignment` passes anyway.** Root cause is mechanical and
citable: `_collect_verb_references` (`src/gzkit/governance/trust_audits/cli.py:121`)
scans only three patterns —

```python
_BACKTICKED_INVOCATION = re.compile(r"`gz\s+([a-z][a-z0-9-]*)[^`]*`")
_QUOTED_INVOCATION = re.compile(r'"gz\s+([a-z][a-z0-9-]*)[^"]*"')
_STEP_DEF_FIXTURE = re.compile(r'the gz command\s+"([a-z][a-z0-9-]*)')
```

— all of which require backticks or quotes. **A `gz` invocation inside a fenced code
block is unquoted and unbackticked, so it escapes the gate entirely.** That is the
exact place operators copy commands from. This is a blind spot in the enforcement of
`governance-core.md` § Operator-doc verb resolution, whose scope text explicitly
includes `.gzkit/skills/**/SKILL.md`.

### D3 — `gz-deps-upgrade` H1 advertises a CLI verb that does not exist (SOFT)

`.gzkit/skills/gz-deps-upgrade/SKILL.md:14` is `# gz deps-upgrade`. There is no
`deps-upgrade` verb (161 registered verb paths; the skill declares no `gz_command:`
and drives `uv`/`uvx` directly). It escapes `--cli-alignment` for the same reason as
D2 — a markdown heading is not backticked. Violates
`tool-skill-runbook-alignment.md` Invariant 2 in spirit: the skill's advertised
operator moment names a tool that is not there.

### D4 — `tests.md § Tests assert semantics, not strings` resolves to a bold lead-in, not a section (SOFT)

Cited as a `§` by five call sites across three skills (`ghi-close:265`, `:421`;
`gz-pythonic-pattern-apply:47`, `:138`; `gz-pythonic-pattern-detect:126`). The target
is `tests.md:65`, a `**bold lead-in.**` under `## Red-Green-Refactor (TDD Discipline
— binding)` — not a heading, therefore not anchor-addressable. Same shape for
`agent-failure-modes.md § Safeguard circumvention` (`gz-issue-file:82`), which
resolves to a **table cell** at `agent-failure-modes.md:20`; that rule has exactly one
heading in the whole file. The citations resolve by prose search, not by structure.

Note the same convention has already drifted inside `tests.md` itself: its `0.11.0`
version note claims to add "§ Unit-test purpose, § The discriminator, § Prefer
structured assertion targets" — all three are bold lead-ins, none is a heading.

### D5 — `.claude/rules/arb.md` (NOT a defect — recorded to close the question)

`ghi-close:313` contains the string `.claude/rules/arb.md`, which exists in neither
`.gzkit/rules/` nor `.claude/rules/`. It is **not** a live citation: it is the quoted
title of GHI #291 inside a worked example ("GHI #291 (*OBPI-0.36.0-08 premise broken:
`.claude/rules/arb.md` absorbed twice*)"). Sealed historical record. No action.

## Mirror-path citations

Four skills route agents at `.claude/rules/…` — a surface `skill-surface-sync.md`
§ Non-negotiable rules #4 calls a *generated output* and #1 subordinates to
`.gzkit/rules/`:

| Skill | Line(s) | Cited mirror path |
|---|---|---|
| `ghi-close` | 253, 269, 419 | `tool-skill-runbook-alignment.md` |
| `ghi-close` | 418 | `gh-cli.md` |
| `ghi-triage` | — | `gh-cli.md` |
| `gz-adr-create` | — | `governance-core.md` |
| `gz-tech-debt-review` | 196 | `pythonic.md` |

`ghi-close` is the sharpest case: line 253 cites `.gzkit/rules/tests.md` (canonical)
and the *same sentence* cites `.claude/rules/tool-skill-runbook-alignment.md` (mirror).
For `governance-core.md` and `pythonic.md` this is the **only** citation the rule has —
both rules' sole routing path runs through a derivative.

## Name-collision hazard

Two canonical rule filenames are duplicated under `docs/governance/`:

```
.gzkit/rules/AGENTS.md                    <->  docs/governance/AGENTS.md
.gzkit/rules/hexagonal-architecture.md    <->  docs/governance/hexagonal-architecture.md
```

The second is load-bearing. `gz-design:137` and `gz-patch-release:65` both cite
`docs/governance/hexagonal-architecture.md` — plausibly deliberate (that file carries
Cockburn's source and the port/adapter mapping), but the effect is that the **rule**
version, which is the binding surface and carries `paths: "**/*.py"`, is named by no
skill at all. A bare-filename search for `hexagonal-architecture.md` reports 2 hits and
looks reachable; it is not.

## Named worked example — `git-sync` ↛ `task-discovery.md`

The chore's Honors test asks for a concrete procedure-vs-rule tension. This is the
sharpest one in the current corpus, and it is new since 2026-05-10 (the rule did not
exist then).

`task-discovery.md` § Invariant (rule-version `0.5.0`):

> **Every unit of labor traceable to a TASK MUST surface that attribution through at
> least one of four discovery channels — with a floor: any commit touching `src/**`
> or `tests/**` MUST additionally carry a `Task:` trailer.**

`gz validate --commit-trailers` fail-closes on that scope. `tests.md` v`0.7.0` records
the producer side: *"`gz git-sync` now stamps `Task: TASK-gz-git-sync` (previously only
`Ceremony:`, which #552 stopped accepting on src/tests scope — leaving every sync
commit silently non-compliant)"*.

Observed on the skill that lands every commit:

```
$ grep -cniE "task:|trailer|@advances|TASK-" .gzkit/skills/git-sync/SKILL.md
0
```

An agent driving `git-sync` sees no mention of the mandatory trailer, no mention of the
validator that fails closed on it, and no pointer to the rule. The stamping is entirely
producer-side (`gz git-sync` + `.gzkit/hooks/prepare-commit-msg-task-trailers`), so
today it works — but the skill body carries **zero** description of the contract it
depends on, and GHI #731 records that the auto-stamp's witness status is unruled. That
is the definition of a rule reachable at R3u only: correct by accident of tooling,
unrouted by doctrine.

## What the 2026-05-10 pass claimed that does not hold today

| 2026-05-10 claim | 2026-08-01 observation |
|---|---|
| Rows 6, 29, 31: `brief-heading-conventions.md` "yes (mechanical) — `gz validate --brief-headings` runs inside the reconcile pipeline" | No skill body contains `--brief-headings`. Grade R3. |
| Row 17: `complexity-thresholds.md` "`gz validate --complexity-thresholds` is invoked by the chore wrapper" | No skill body contains `--complexity-thresholds`. Grade R3. |
| Row 27: `security-sensitivity.md` "locked by `--sensitivity` validator" in the pipeline | No skill body contains `--sensitivity`. |
| Row 10: `pythonic.md` "`gz validate --type-ignores` which the wrapper invokes in heavy lanes" | No skill body contains `--type-ignores`. |
| "50 active, 17 archived" skills | 68 active; archived directories deleted (delete-on-retire, `skill-surface-sync.md` § Retirement policy). The 17-row archived table has no successor. |
| "20 canonical rules" | 25 rules + 1 generated subtree map. Six rules added. |

Four of the prior pass's "yes (mechanical)" honors were asserted against validator
invocations that are not in any skill body. They inflated the honored count by 4 rows.
This re-run grades mechanically-honored only where the invocation string is
observable — the 17 `gz validate --<scope>` occurrences enumerated above.
