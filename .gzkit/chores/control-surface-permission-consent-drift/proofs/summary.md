# Summary — Pass D run 2026-08-01

Second run of `control-surface-permission-consent-drift`. First run under the git-commit-date
freshness gate (`scripts/check_proof_freshness.py`, GHI #743) that replaced the `test -f`
acceptance — which passed forever once a report existed and could not see that the evidence
described a surface that had since moved.

## Counts

| Severity | This run | 2026-07-16 |
|---|---|---|
| **live** (no deny covers it) | **6** | 0 |
| historical (grant standing, target gone) | 3 | 0 |
| neutralized (a deny rule already wins) | 0 | 0 |
| clean (walked, no allow rule grants the prohibition) | 6 | 6 |
| under-grants (doctrine-mandated read the allowlist withholds) | 2 | not walked |
| **verified gaps invisible to the ledger** (`unwitnessable.md` UW-2) | **8** | 3 |
| context-free prohibitions mapped | 10 | 6 |
| context-dependent prohibitions (unauditable) | 4 | 3 |
| grants inventoried | 216 (180 settings + 36 `_PERMITTED_BASH`) | 180 |

## What changed since 2026-07-16

**The permission surfaces did not move. The doctrine did.** `.claude/settings.local.json` is
byte-identical (180 allow rules, verified by diff against the prior run's inventory);
`.claude/settings.json` is unchanged since `758e33524` (2026-07-16). Meanwhile `.gzkit/rules`
last committed 2026-07-29 (`4b9db7592`). Every new finding traces to that asymmetry:

1. **Four prohibitions were never mapped** by the first run — CF-7 and CF-8
   (`skill-surface-sync.md` rules #4 and #5, on disk since 2026-04-07), CF-10 (Always #11's
   insights-jsonl ban), and CF-9 (`gz gates` retirement, registered 2026-07-21 in
   `322f07473`, i.e. genuinely new). Three of the six live rows come from them.
2. **A second detection test was added** — glob containment for path-shaped prohibitions,
   alongside the command-permission test. It found D-7 (`Edit(src/**)` containing
   `src/gzkit/{skills,rules,personas,templates}/`), which substring matching cannot see.
3. **The audited surface was extended** on the dispatching operator's instruction to cover
   hook allowlists. `_PERMITTED_BASH` (`src/gzkit/handoff_resume_gate.py:96-145`) is the only
   one — none of the 15 `.claude/hooks/*.py` adapters carries an allowlist of its own. It
   produced D-8, D-9, U-1, and confirmed U-2 (GHI #732, still open).
4. **The prior summary's count was internally inconsistent** — its table read `live | 1` while
   its prose read *"`consent-drift.md` reports 0 live rows"* and its routing list read
   *"No `live` drift rows"*. The ledger itself had 0. Retired here; the correct prior-run
   figure is 0.

## The headline

Six live rows, and the two most consequential are not in the local convenience file at all —
they are in **committed, shipped source**:

| Row | Finding |
|---|---|
| **D-8 / D-9** | `_PERMITTED_BASH` grants standing read consent for `gz gates`, and the gate's operator-facing block prose *prescribes* it — a verb `src/gzkit/governance/deprecations.py:41` registers as retired (`successor="gz closeout"`, GHI #705) and which announces its own deprecation at runtime. `gz validate --deprecated-verb-prescription` exists to fail closed on exactly this and passes today, because its surface globs cover `.gzkit/rules/**/*.md`, `.gzkit/skills/**/SKILL.md`, the two runbooks, `AGENTS.md` and `CLAUDE.md` — and no `.py` under `src/gzkit/`. |
| **U-1** | The successor, `gz closeout` — which `.gzkit/rules/governance-core.md` § Required workflow order step 5 now mandates — is **absent** from the same allowlist. The retired verb is permitted; its replacement is refused. |
| **D-1** | `Bash(SKIP=gitleaks uv run gz git-sync --apply --lint --test)` grants standing consent to skip the secret scanner. The committed deny list closes `--no-verify` and `core.hooksPath` — the other two bypass channels — but not `SKIP=`. The hook it disables is the one guarding `AGENTS.md:328`, whose recovery is a filter-repo rewrite and force-push. |

## Known coverage limits (restated verbatim per CHORE.md — required)

1. **Context-dependence — the hard ceiling.** Much of `AGENTS.md` forbids an action *in a context*: "never call `gh issue create` **outside this skill**" (Always #13), "never X directly", "never X without ceremony". Permission rules are context-free string matches. The sanctioned and forbidden invocations are byte-identical. `Bash(gh issue:*)` is **load-bearing, not drift** — `/ghi-author` invokes `gh issue create` at `SKILL.md:199` as its own final step, and denying it would break the only sanctioned path for filing a GHI. Any context-dependent prohibition is **out of scope for a Pass D row** and belongs in `proofs/unwitnessable.md`.
2. **Broad-rule blindness.** A drift row can only be raised against a rule that *mentions* the prohibited token. `Bash(git *)` permits `git checkout -b feature/foo`, contradicting operator canon (verbatim, 2026-06-16: never create feature branches, work directly on main), but contains no matching substring. Broad rules are the more dangerous class and this pass cannot see them. Record known-broad rules in `proofs/unwitnessable.md` rather than silently passing them.
3. **CI-blindness.** The committed `.claude/settings.json` is checkable anywhere; `.claude/settings.local.json` exists only on the operator's machine. This chore is therefore **local-run only** and its findings are not reproducible in CI. Never wire it to a CI gate.
4. **Curated-list drift.** The doctrine→pattern mapping in `proofs/doctrine-map.md` is hand-maintained and can itself drift from `AGENTS.md`, reproducing the drift failure one level up. Step 1 re-derives the map from the corpus each run rather than trusting the prior run's map.

## Routing list

Per operator canon, a GHI-tracked defect repair routes to **direct fix**
(`fix(<scope>): … (GHI #N)`, closed citing the commit SHA) — never an ADR or OBPI. Each item
below is sized against `AGENTS.md` § Defect-fix routing thresholds.

### Repo-side (committed surfaces — GHI-eligible)

| Row | Proposed fix | Diff size | Files | Route |
|---|---|---|---|---|
| **D-8 + D-9 + U-1** | In `src/gzkit/handoff_resume_gate.py`: drop `("gz", "gates")`, add `("gz", "closeout")`, repoint the block prose at `:360` off `gz gates`. Extend `_SURFACE_GLOBS` in `deprecated_verb_prescription.py` to cover `src/gzkit/**/*.py` so the gate that exists for this can see it. | ~10 source lines + covering test | 2 source, 1-2 test | **one GHI, direct fix** — single named surface, in-flight defect, unit-testable without a BDD scenario. The validator-scope half is the class fix (AGENTS.md § DO IT RIGHT 1: *fix the class of failure, not the instance*); shipping only the tuple edit leaves the next retired verb equally invisible. |
| **U-2** | Widen the git read allowlist off enumerate-the-examples (`rev-list`, `blame`, `shortlog`, `describe`, `merge-base`, `cat-file`, `for-each-ref`). | <=10 lines + test | 1 source, 1 test | **already tracked — GHI #732, OPEN.** Do not re-file. Land it with the D-8 fix; same tuple, same test. |
| **UW-5** | Reconcile `AGENTS.md:38` (*"append to `.gzkit/insights/agent-insights.jsonl`"*) with `AGENTS.md:125` / `governance-core.md:50` (*"never hand-append the jsonl"*). | prose | 1-2 rule/contract files | **Pass A finding, not Pass D.** Route to `control-surface-rule-conflicts` or a rule-reconciliation GHI. Not fixable from a permission surface. |

### Operator-side (gitignored `settings.local.json` — no GHI; a GHI cannot carry a diff for an untracked file)

| Rows | Grant to remove | Why |
|---|---|---|
| D-1 | `Bash(SKIP=gitleaks uv run gz git-sync --apply --lint --test)` | Standing consent to skip the secret scanner (`AGENTS.md:145` § Never #10). |
| D-2, D-6 | the two live `cp`-into-a-mirror rules | `skill-surface-sync.md:91`: *"Do not manually copy skill files between surfaces — use the sync command"*. |
| D-3, D-4, D-5 | the three dead `cp` rules | Sources no longer exist; pure fossil. |
| D-7 | narrow `Edit(src/**)` | Contains `src/gzkit/{skills,rules,personas,templates}/`, which `skill-surface-sync.md:31` forbids editing. |

**Durable alternative worth an operator ruling.** Deny takes precedence over allow, and
`.claude/settings.json` **is** committed. Adding deny rules there would neutralize D-1, D-2,
D-6 and D-7 on every machine and every clone, surviving the next "always allow" click — the
same mechanism the existing six `--no-verify` / `hooksPath` denies already use. This run does
not propose specific patterns: writing them is a permission change with real workflow cost and
this chore is audit-only (CHORE.md § Policy and Guardrails: *"This chore does NOT edit
`.claude/settings.json` ... It reads and reports"*).

**Standing operator ruling carried forward (2026-07-16), unchanged.** The UW-2 broad-rule gaps
(`Bash(git *)`, `Bash(uv run *)`, `Bash(sed:*)`, and now `Bash(perl -i -pe ' *)`) are **not**
routed as defects: broad allows are acceptable on a local dev box where the hook chain, the
ledger, and Gate 5 are the actual enforcement. They are recorded as standing known-gaps. Note
that this ruling predates CF-7/CF-8/CF-10 being mapped — it was made against three gaps and
now covers eight. Whether it still holds at that width is an operator call, not an agent's.

**Next run should check:** (a) whether `.claude/settings.json` has accumulated any `allow`
rules (0 for two runs running — deny-only, by design); (b) whether the D-8/U-1 allowlist fix
landed, since the deprecated-verb registry will keep growing and `src/gzkit/**/*.py` is still
outside the validator's scope; (c) whether `.gzkit/rules/**` gained new command- or path-shaped
prohibitions — that is where both of the last two runs' findings actually came from.
