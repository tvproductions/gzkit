# Consent Drift Ledger — Pass D run 2026-08-01

Context-free prohibitions (CF-1 … CF-10 from `doctrine-map.md`) walked against **180 allow
rules** across the two settings surfaces plus **36 command prefixes** in the extended
`_PERMITTED_BASH` surface. Deny rules take precedence over allow, so a hit covered by a deny
is `neutralized`, not `live`.

## Detection method (stated so the next run can reproduce or refute it)

Per the prior run's probe-hygiene note, a rule is tested by **whether it permits the forbidden
invocation**, never by substring match against the rule text. Two tests were applied:

1. **Command-permission test** — would this allow rule let the forbidden command run without a
   prompt? (CF-1 … CF-4, CF-6, CF-9)
2. **Glob-containment test** — is the doctrine's forbidden *path* a strict subset of the
   allow rule's glob? (CF-5, CF-7, CF-8, CF-10)

Test 2 is **new this run** and is what surfaced D-7. It is strictly stronger than substring
match and strictly weaker than "does this rule permit any forbidden action" — a rule like
`Bash(sed:*)` names no path at all and remains invisible to it (see `unwitnessable.md` UW-2).
Recording the method change explicitly: a future run that finds fewer rows must first check
whether it applied both tests, not conclude the surface got cleaner.

## Live and historical rows

| ID | Doctrine | Citation | Prohibited | Allow rule (verbatim) | Source | Severity | Neutralizing deny |
|---|---|---|---|---|---|---|---|
| D-1 | CF-2 | `AGENTS.md:145` § Never #10 | commit that skips a configured hook | `Bash(SKIP=gitleaks uv run gz git-sync --apply --lint --test)` | `settings.local.json` | **live** | none — the 6 deny rules close `--no-verify` and `core.hooksPath`, not `SKIP=` |
| D-2 | CF-7 | `.gzkit/rules/skill-surface-sync.md:30`, `:91` | writing a vendor mirror / manual cross-surface copy | `Bash(cp .github/skills/gz-obpi-pipeline/SKILL.md .claude/skills/gz-obpi-pipeline/SKILL.md)` | `settings.local.json` | **live** | none |
| D-3 | CF-7 | same | same | `Bash(cp .github/skills/gz-obpi-pipeline/DISPATCH.md .claude/skills/gz-obpi-pipeline/DISPATCH.md)` | `settings.local.json` | historical | none — source file no longer exists |
| D-4 | CF-7 | same | same | `Bash(cp .github/skills/gz-obpi-pipeline/VERIFICATION.md .claude/skills/gz-obpi-pipeline/VERIFICATION.md)` | `settings.local.json` | historical | none — source file no longer exists |
| D-5 | CF-7 | same | same | `Bash(cp .github/skills/gz-obpi-pipeline/REFERENCE.md .claude/skills/gz-obpi-pipeline/REFERENCE.md)` | `settings.local.json` | historical | none — source file no longer exists |
| D-6 | CF-7 | same | same | `Bash(cp .gzkit/skills/gz-plan-audit/SKILL.md "$mirror/gz-plan-audit/SKILL.md")` | `settings.local.json` | **live** | none |
| D-7 | CF-8 | `.gzkit/rules/skill-surface-sync.md:31` | editing `src/gzkit/{skills,rules,personas,templates}/` | `Edit(src/**)` | `settings.local.json` | **live** | none |
| D-8 | CF-9 | `src/gzkit/governance/deprecations.py:41` | granting/prescribing a retired verb | `("gz", "gates")` — `src/gzkit/handoff_resume_gate.py:102` | `_PERMITTED_BASH` (committed) | **live** | none |
| D-9 | CF-9 | same | same | `"Reading is permitted while unauthorized (gz state / gz gates / gz obpi status, "` — `src/gzkit/handoff_resume_gate.py:360` | block prose (committed) | **live** | none |

## Clean rows (walked, no allow rule grants the prohibition)

| Doctrine | Citation | Prohibited | Result |
|---|---|---|---|
| CF-1 | `AGENTS.md:249` § Execution Rules | bare `python` / `python3` | clean — no allow rule names either; the `Bash(python3:*)` rule that motivated GHI #690 stays removed |
| CF-3 | `AGENTS.md:94` § STDLIB-FIRST | `pytest` | clean by this test — but see UW-2, `Bash(uv run *)` permits it unnamed |
| CF-4 | `AGENTS.md:324` § Local Agent Rules | `PYTHONUTF8=1 uv run gz` | clean |
| CF-5 | `AGENTS.md:137` § Never #2 | write to `.gzkit/ledger.jsonl` | clean on the `Edit(...)` path (no glob reaches it) — but see UW-2, `Bash(sed:*)` and `Bash(perl -i -pe ' *)` reopen it through the shell |
| CF-6 | `AGENTS.md:344` § Operator Doctrine | `git checkout -b` / `git switch -c` | clean by this test — but see UW-2, `Bash(git *)` permits it unnamed |
| CF-10 | `AGENTS.md:125` § Always #11 | hand-append `.gzkit/insights/agent-insights.jsonl` | clean on the `Edit(...)` path — same shell reopening as CF-5 |

## Adjudications (the part that is not a permission list)

**D-1 — is `SKIP=gitleaks` actually forbidden?** Never #10's first sentence names only
`--no-verify`. Its second sentence is categorical: *"All commits and pushes must run through
the configured hooks and quality gates."* `gitleaks` is a configured hook
(`.pre-commit-config.yaml:90-95`, `entry: gitleaks protect --staged --redact`,
`stages: [pre-commit]`), and `SKIP=` is pre-commit's own per-hook bypass — so the grant
permits a commit that does not run through a configured gate. The verdict rests on the second
sentence, and it is the sharper reading here because the deny list already treats *channel*
as the thing being closed: it spends four of six rules on `--no-verify` and `git commit -n`
variants and two on `core.hooksPath`, i.e. it enumerates bypass channels. `SKIP=` is the third
channel and the only one with a standing allow. It is also the highest-consequence one to
leave open: gitleaks is the secret scanner backing `AGENTS.md:328` § Local Agent Rules
(*"never include the operator's personal email in any repo-bound artifact … A leak needs a
filter-repo rewrite + force-push to recover (2026-04-19 incident)"*). This grant pre-disables
the scanner that guards the one prohibition whose recovery is a history rewrite.

**D-2 / D-6 — why `cp` counts as "editing a mirror".** `skill-surface-sync.md:91` § Do Not
does not say "do not edit"; it says *"Do not manually copy skill files between surfaces — use
the sync command"*. These five rules are that sentence, verbatim, converted into standing
consent. D-2 is mirror-to-mirror (`.github/skills/` → `.claude/skills/`), so it violates rule
#4 on both ends. D-6 copies canonical → mirror, bypassing `gz agent sync control-surfaces`,
which rule #3 requires *"after every edit"* because *"sync also updates manifests,
registrations, and vendor-specific rendering"* (`:92`) — a `cp` moves bytes and nothing else.

**D-7 — `Edit(src/**)` vs a per-surface prohibition.** The forbidden paths
(`src/gzkit/skills/`, `src/gzkit/rules/`, `src/gzkit/personas/`, `src/gzkit/templates/`) are a
strict subset of the granted glob `src/**`. This is not the broad-rule blindness of UW-2:
containment here is decidable, and the grant is one level of specificity away from being
correct (`Edit(src/**)` with a matching deny, or narrower allows, would close it). The
countervailing fact, recorded rather than argued away: rule #5's violation is *detectable
after the fact* by `gz agent sync control-surfaces` / `gz validate --distribution` byte-parity.
That is T2 recovery, not T1 prevention — and this chore exists precisely because the
permission prompt is the only *interposition* point, per CHORE.md § Overview: *"the one
mechanical interposition point (the permission prompt) is pre-disabled for a prohibited
action."*

**D-8 / D-9 — a permission allowlist grandfathering a retired verb.** `gz gates` is registered
at `src/gzkit/governance/deprecations.py:41` as `DeprecatedVerb(verb="gates",
successor="gz closeout", ghi="#705")` and announces itself at runtime — observed this run:

```
$ uv run gz gates
⚠ Deprecated: `gz gates` will be removed in a future release. Use `gz closeout` instead.
```

`gz validate --deprecated-verb-prescription` exists to fail closed on exactly this, and it
passes today (`✓ All validations passed (1 scopes)`) — because its `_SURFACE_GLOBS` /
`_SURFACE_FILES` (`src/gzkit/governance/trust_audits/deprecated_verb_prescription.py:48-62`)
cover `.gzkit/rules/**/*.md`, `.gzkit/skills/**/SKILL.md`, `src/gzkit/rules/**/*.md`,
`src/gzkit/skills/**/SKILL.md`, the two runbooks, `AGENTS.md` and `CLAUDE.md` — **and no
`.py` under `src/gzkit/`**. So the retired verb survives in two places the gate cannot see:
the allowlist tuple, and the operator-facing block prose that tells a blocked agent which
reads are available. D-9 is the more consequential half — that prose is a *prescription*, and
it is the exact shape GHI #705 recorded (a governed surface routing an agent onto a retired
verb with no signal that the correct move is a different verb).

## Under-grants (the inverse direction — recorded, not counted as drift)

A permission surface can be wrong in two directions. These are grants doctrine *requires* and
the surface withholds. They are not "standing consent for a prohibited action", so they are
not drift rows; they are logged because the same allowlist produced both.

| ID | Doctrine that mandates the read | Absent from | Status |
|---|---|---|---|
| U-1 | `.gzkit/rules/governance-core.md` § Required workflow order step 5 — `uv run gz closeout ADR-<X.Y.Z> --dry-run` | `_PERMITTED_BASH` has no `("gz", "closeout")` entry | **live** — the deprecated predecessor `gz gates` IS allowlisted (D-8) while its successor is refused. The repoint at `governance-core.md` `0.6.0` moved the rule; the allowlist did not follow. |
| U-2 | `.gzkit/rules/token-block-discipline.md` § Binding Sub-Invariant 2 item 4 — handoff-time branch-state verification | `_PERMITTED_BASH` has `("git", "rev-parse")` but no `("git", "rev-list")` | **live, already tracked** — GHI #732 (OPEN), *"git read allowlist omits rev-list (3rd narrow miss)"*. Not re-filed. |

U-1 and U-2 share a root the module's own docstring predicts
(`src/gzkit/handoff_resume_gate.py:78-83`): *"Enumerate-the-examples always under-covers the
rule it serves."* U-1 shows the same enumeration also *over*-covers — it keeps entries the
rules have retired. GHI #732 names the under-coverage class; the over-coverage class (D-8)
has no tracker.

## Counts

- **live**: **6** (D-1, D-2, D-6, D-7, D-8, D-9)
- **historical**: 3 (D-3, D-4, D-5)
- **neutralized**: 0
- clean (walked, no allow rule grants the prohibition): 6 (CF-1, CF-3, CF-4, CF-5, CF-6, CF-10)
- under-grants (inverse direction, not drift): 2 (U-1, U-2)
- rows total: 9 drift + 6 clean + 2 under-grant
- allow rules walked: 180 settings (180 local + 0 shared) + 36 `_PERMITTED_BASH` prefixes
- deny rules consulted: 6

Prior run (2026-07-16): 0 live, 6 clean, 6 rules mapped.

## Reading this ledger

A drift ledger is **not** a coverage report. Four of fourteen command-shaped prohibitions in
the contract are structurally invisible to this pass, and broad allow rules are invisible
regardless of doctrine. See `unwitnessable.md` — it is a required acceptance artifact for
exactly this reason, and the three verified-but-invisible gaps it records are still open.
