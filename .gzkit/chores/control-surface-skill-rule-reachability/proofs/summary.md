# Summary — Control Surface Skill ↔ Rule Reachability Audit (Pass B)

**Generated:** 2026-08-01. Supersedes the 2026-05-10 pass in full.
**Scope:** 68 skills (`.gzkit/skills/**`) × 25 rules (`.gzkit/rules/**`). Audit-only; no
edits outside `proofs/`. Vendor mirrors excluded as derivatives.
**Why re-run:** the chore's acceptance was `test -f`, which passes forever once a file
exists. Proofs were frozen at 2026-05-10 while the audited surface moved through
2026-07-29. `acceptance.json` now gates on
`scripts/check_proof_freshness.py` (git-commit-date comparison). GHI #743.

## Headline counts

| Measure | 2026-05-10 | 2026-08-01 | Δ |
|---|---|---|---|
| Skills inventoried | 50 active + 17 archived | **68 active**, 0 archived (delete-on-retire) | +18 |
| Rules inventoried | 20 | **25** (+1 generated subtree map, +1 data file) | +5 |
| Skills citing ≥1 rule | 9 of 50 (18%) | **18 of 68 (26%)** | +9 |
| Skills citing **zero** rules | 41 of 50 (82%) | **50 of 68 (74%)** | +9 abs / −8 pts |
| Rules cited by ≥1 skill | 6 of 20 (30%) | **11 of 25 (44%)** | +5 |
| **Orphaned rules** (no skill routes to them; R3/R3u/R4) | not measured | **12 of 25 (48%)** | new measure |
| **Dangling citations** | not measured | **3 hard + 2 soft** (D1–D4; D5 cleared) | new measure |

## The five findings that matter

### 1. Twelve of 25 rules (48%) are reachable only by `paths:` glob — nothing routes to them

`adr-audit`, `brief-heading-conventions`, `chores`, `cli`, `complexity-thresholds`,
`cross-platform`, `gate5-runbook-code-covenant`, `guardrail-feedback-prose`,
`hexagonal-architecture`, `model-selection`, `models`, `task-discovery`.

A `paths:` match is a *vendor-harness* auto-load behavior against `.claude/rules/*.md`
— the derivative surface. On the canonical surface it is not routing at all. Four of
these rules carry universal globs (`**/*`, `**/*.py`), where the match is trivially
true and carries no signal whatsoever.

**Sharpest instance:** `task-discovery.md` makes a `Task:` trailer *mandatory* on every
`src/**`/`tests/**` commit, fail-closed by `gz validate --commit-trailers`. The
`git-sync` skill — which composes and lands every commit — contains **zero** occurrences
of `Task:`, `trailer`, `@advances`, or `TASK-`. Four GHIs (#201, #552, #708, #731) have
been filed and fixed on this contract; every fix landed producer-side. The skill body
was never touched.

### 2. `hexagonal-architecture.md` is orphaned by a filename collision

`.gzkit/rules/hexagonal-architecture.md` and `docs/governance/hexagonal-architecture.md`
both exist. `gz-design:137` and `gz-patch-release:65` cite the **docs** copy. A bare
`grep hexagonal-architecture.md` over the skill corpus returns 2 hits and looks healthy;
the binding rule — the one AGENTS.md calls gzkit's *"primary code-architecture
directive"* — is named by no skill. GHI #559 proves the hazard is live: a defect was
filed and fixed against the docs copy while the rule copy went unexamined.

### 3. Three hard dangling citations

- **D1** — `ghi-close:269` and `:419` cite `tool-skill-runbook-alignment.md §
  Commit-message discipline`. Rule v`0.2.0` **lifted that section out** under GHI #327
  to `docs/governance/tool-skill-runbook-rationale.md:43`. The destination is gone; the
  citation was never swept. A coupled-surface miss (AGENTS.md § DO IT RIGHT 1a).
- **D2** — `gz-content-compose:56` prescribes `gz ledger tail --event
  composition_candidate_emitted` inside a runnable bash block. Observed:
  `gz: error: argument command: invalid choice: 'ledger'`.
- **D3** — `.gzkit/skills/gz-deps-upgrade/SKILL.md:14` is `# gz deps-upgrade`; there is
  no such verb among the 161 registered verb paths, and the skill declares no
  `gz_command:`.

Two soft cases (D4): six `§` citations across four skills resolve to **bold lead-ins or
table cells**, not headings — `tests.md § Tests assert semantics, not strings` (5 sites)
and `agent-failure-modes.md § Safeguard circumvention` (1 site). The prose exists; the
anchor does not.

### 4. `gz validate --cli-alignment` cannot see fenced code blocks — the place operators copy from

D2 and D3 both escape a *passing* gate. Root cause, `src/gzkit/governance/trust_audits/cli.py:28-30`:

```python
_BACKTICKED_INVOCATION = re.compile(r"`gz\s+([a-z][a-z0-9-]*)[^`]*`")
_QUOTED_INVOCATION = re.compile(r'"gz\s+([a-z][a-z0-9-]*)[^"]*"')
_STEP_DEF_FIXTURE = re.compile(r'the gz command\s+"([a-z][a-z0-9-]*)')
```

All three require backticks or quotes. A fenced `bash` code block is neither.
`governance-core.md` § Operator-doc verb resolution declares `.gzkit/skills/**/SKILL.md`
in scope and says *"Exit 3 on any unresolvable reference"* — the rule is right; the
enforcement artifact is blind to the highest-traffic form. **No GHI exists for this.**

### 5. Four of the prior pass's "yes (mechanical)" honors were asserted, not observed

Rows 6/29/31 claimed `gz validate --brief-headings` "runs inside the reconcile
pipeline"; row 17 claimed `--complexity-thresholds` "is invoked by the chore wrapper";
row 27 claimed `--sensitivity`; row 10 claimed `--type-ignores`. **None of those four
strings appears in any skill body.** The observable population is 17 `gz validate
--<scope>` invocations across 13 skills, enumerated in `reachability-matrix.md`. The
prior pass's honored count was inflated by 4 rows — an instance of the failure class the
chore exists to catch, inside the chore's own evidence.

## Routing recommendations

Priority order. Every item is a **correction** under operator doctrine (the surface does
not fulfil its declared intent), not an enhancement.

| # | Finding | Route | Rationale |
|---|---|---|---|
| 1 | D1 dead section pointer in `ghi-close` (2 sites) | **direct fix** — repoint to `docs/governance/tool-skill-runbook-rationale.md § Commit-message discipline for skill-routing changes` | ≤10 lines, 1 file, defect surfaced in flight. Meets every direct-fix threshold. |
| 2 | D2 `gz ledger tail` in `gz-content-compose:56` | **direct fix** — replace with a registered verb or drop the step | 1 line, 1 file, reproducible failing command. |
| 3 | D3 `# gz deps-upgrade` heading | **direct fix** — retitle to the skill name, not a verb | 1 line. |
| 4 | `--cli-alignment` fenced-block blind spot | **file a GHI via `/ghi-author`** | Changes a validator's detection surface across `docs/**`, `features/**`, and 68 SKILL.md files; blast radius unknown until measured. Exceeds direct-fix scope. |
| 5 | `mx-mode.md` marker/blockquote disagreement (`1.0.1` vs `1.0.0`) — **`gz validate --rule-version-markers` is currently red** | **direct fix** | Not a reachability finding but a live failing gate found in-scope. AGENTS.md Prime Directive #2/#5. |
| 6 | 12 orphaned rules; no aging clock for rules | **GHI #691 (already open)** — attach this measurement | #691 asked whether the skills/rules asymmetry has a cost. The cost is 48%, measured here. Do not file a duplicate. |
| 7 | `hexagonal-architecture.md` name collision | **file a GHI** | Requires deciding which file is canonical and sweeping consumers — a doctrine call, not a text fix. |
| 8 | `git-sync` ↛ `task-discovery.md`; `gz-chore-runner` ↛ `chores.md`; `gz-obpi-lock` ↛ `token-block-discipline.md` | **one GHI covering the class** | Filing three is the sibling-cut-duplicate pattern `/ghi-author` Step 0 exists to prevent. The class is *"skills whose subject is a rule's subject do not cite the rule."* |

## What did not move in 83 days

The 2026-05-10 pass ranked five known-blocking gaps and wrote a one-line remedy for
each. **None was routed to a GHI, and none was applied.** All five are re-confirmed
open in this pass. That is the chore's own hollowness — proofs that report findings
into a directory nothing reads, gated by `test -f`. The freshness gate closes the
staleness half; the routing half (a finding must reach a work order) is unclosed and is
the same class GHI #669 names one surface over.

## Gate status

`uv run python scripts/check_proof_freshness.py control-surface-skill-rule-reachability`
compares **git commit dates**, and treats uncommitted proofs as fresh. These artifacts
are rewritten but **not committed** (per run instruction). The gate turns green on
commit; until then it reports against the last committed revision:

```
proof-freshness gate — control-surface-skill-rule-reachability
  audited surfaces:  .gzkit/rules, .gzkit/skills
  surface last moved: 2026-07-29
  ghi-cross-reference.md       2026-06-25  STALE
  reachability-matrix.md       2026-06-25  STALE
  skill-inventory.md           2026-06-25  STALE
  summary.md                   2026-06-25  STALE
EXIT=3
```

**In-scope drift found and not fixed (audit-only lane).** `CHORE.md` § Acceptance
Criteria still lists the four superseded `test -f …` rows, while `acceptance.json`
(both the project-local and the `src/gzkit/chores/` canonical copy) now carries the
single `check_proof_freshness.py` criterion. The two surfaces disagree about what
gates this chore. The human-readable one is the stale side. Route: direct fix — one
table in one file.
