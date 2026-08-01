# GHI Cross-Reference — Control Surface Skill ↔ Rule Reachability Audit (Pass B)

**Generated:** 2026-08-01 (re-run; supersedes the 2026-05-10 pass)
**Source:** `gh issue list --state all --search <term>` and `gh issue view <n>` (read verbs only).
**Open-issue population at scan time:** 25 (`gh issue list --state open --limit 200`).
**Classification:** a gap is **known-blocking** when a GHI documents the same symptom;
**latent** when no GHI names it.

## Part 1 — the meta-finding the queue itself proves

The 2026-05-10 pass produced a ranked list of five known-blocking gaps with a
one-line remedy for each. **None of the five was routed to a GHI.** Searching the
full 743-issue history for the terms in those recommendations returns no issue that
names them:

| 2026-05-10 top-5 recommendation | GHI filed? | Status 83 days later |
|---|---|---|
| Wire `--doc-surface-parity` into pipeline Stage 4 + closeout Step 2 | no | not in any skill body (matrix row 11) |
| Cite `token-block-discipline.md` sub-invariants at `gz-obpi-lock` release step | no | `gz-obpi-lock` still cites nothing (row 24) |
| Add `--chores-layout` / `chores doctor --dry-run` preflight to `gz-chore-runner` | no | no skill invokes `--chores-layout` (row 6) |
| Gate `gz git-sync` on `--commit-trailers` | no | `git-sync` body has 0 trailer mentions (row 22) |
| Cite `tests.md` semantics from `gz-tech-debt-review` | no | still uncited there |

The prior run's own artifact says *"Untrackable defect = nonexistent defect"* is the
governing doctrine (AGENTS.md Prime Directive #6). The audit produced findings and
routed none of them. **That is the same class GHI #669 names** — *"the routing is
convention-enforced, not mechanically-enforced"* — applied to chore output: nothing
mechanically discovers that a chore's proof enumerated a defect and no work order
exists for it. It is also why the chore was able to report `All criteria pass` across
five runs (2026-05-10 → 2026-07-31, per `CHORE-LOG.md`) while its evidence went stale —
the exact hollowness GHI #743 is filed against.

## Part 2 — gap-by-gap classification

| Matrix row | Gap | Matching GHI(s) | Class |
|---|---|---|---|
| 1 `adr-audit.md` R3 | `gz-adr-audit` never routes to the audit-sequence rule | **#272** (closed — *"gz-adr-audit Step 2 cites tests.md semantics"*: the fix added the `tests.md` cite and stopped there), **#271** (closed — *"cite defect-fix-routing.md thresholds from gz-plan and gz-design Step 1"*) | **known-blocking**. Both GHIs prove the remedy shape is understood and applied one skill at a time; neither generalized. |
| 4 `brief-heading-conventions.md` R3 | zero cites, zero `--brief-headings` invocations | **#615** (OPEN — *"structured governance docs regex-scraped, not schema-enforced; briefs 597/600 bypass BriefStructure"*) | **known-blocking**. #615 is the mechanical arm of the same gap: the brief structure is neither schema-enforced nor skill-routed. |
| 6 `chores.md` R3 | `gz-chore-runner` ↛ § Layout discipline; `--chores-layout` uninvoked | **#605** (closed — *"CHORE.md proof-paths + manifest still cite legacy ops/chores/"*), **#728** (OPEN — *"sync and init export project-local slugs to adopters"*), **#743** (OPEN — *"acceptance criteria don't gate the chore's own subject"*) | **known-blocking**, three-deep. #743 is the sharpest: the chore surface's failures are *all* failures of gating the subject, and the routing gap is why. |
| 11 `gate5-runbook-code-covenant.md` R3u | no cite, no `--doc-surface-parity` in any skill | **#738** (OPEN — *"closeout-walkthrough: demo discovery cannot surface refusal/negative demos"*), **#673** (closed — *"backtick-wrapped ADR command cells map to opaque observed=-1"*) | **known-blocking**. Prior pass called this "the largest single doctrine-mechanization gap"; #738 shows the covenant surface still failing on the demo arm. |
| 12 `gh-cli.md` / 22 `task-discovery.md` — `git-sync` cites nothing | `git-sync` body has 0 occurrences of `Task:`/trailer | **#201** (closed — *"gz git-sync auto-commits lack Task trailer, always trip gz validate --commit-trailers"*), **#552** (closed — *"TASK governance silently abandoned despite Validated ADR-0.22.0"*), **#708** (closed — *"git-sync: add -A absorbs staged src/tests work into a ceremony chore commit"*), **#731** (OPEN — *"task-envelope Signature (c): layer-drift gate compares 6 of 776 OBPIs"*) | **known-blocking**, highest GHI density in the corpus. Every fix landed producer-side (`gz git-sync`, the prepare-commit-msg hook); **none touched the skill body**. #731 is open and says the auto-stamp's witness status is unruled. |
| 15 `hexagonal-architecture.md` R4 | orphan-by-collision with `docs/governance/hexagonal-architecture.md` | **#559** (closed — *"docs/governance/hexagonal-architecture.md: stale references to demoted ADRs"*), **#490** (closed — *"patch-release qualifier: foundation work undercounted vs hexagonal port/adapter doctrine"*), **#727** (OPEN — *"architecture: tech choices and mechanism objectives are unrecorded"*) | **known-blocking**. #559 is decisive: a defect was filed and fixed against the **docs** copy while the **rule** copy — the binding one — went unexamined. That is the collision hazard realized. |
| 3 `agents-md-map-doctrine.md` one-way link | rule names `gz-context-diet`; skill does not name back | **#533** (OPEN — *"agents-md-budget: 5k recovery target requires ADR-0.0.37 completion"*), **#579** (OPEN — *"instructions-budget: anchor on imperative-density, not char count"*), **#712** (closed — *"agents-md: 560 B from silent Codex truncation, no gate observes it"*) | **known-blocking**. The budget arm is heavily tracked; the routing arm (skill ↛ rule) is not named in any of the three. |
| 24 `token-block-discipline.md` R2 partial | handoff arm mechanical; `gz-obpi-lock` arm unrouted | **#732** (OPEN — *"handoff-resume-gate: git read allowlist omits rev-list (3rd narrow miss)"*), **#696** (closed — *"handoff: decision state is lost across the session boundary"*), **#692** (closed — *"validator passes hollow handoffs — checks section presence, not population"*) | **known-blocking**, but **improved**: `gz-session-handoff:78` now invokes `gz validate --lock-handoff-coupling`, which did not exist at the 2026-05-10 pass. |
| 16 `model-selection.md` R3u | 68/68 declare `model:`; no skill teaches selection | **#409** (closed — *"Enforce model-selection routing in skill frontmatter"*), **#670** (OPEN — *"design skills: opus self-escalation lacks cross-family second opinion"*), **#526** (closed — *"skill bodies: self-escalation directive drives subagent relay chains"*) | **known-blocking**. #409 mechanized presence; #670 and #526 are the residue of never routing *judgment* to the rule. |
| 19 `pythonic.md` R1-mirror | the two Pythonic-pattern skills don't cite the Pythonic rule | none | **latent** |
| 14 `guardrail-feedback-prose.md` R3 | no skill authors or reviews hooks | none (nearest: **#736**, **#732** — both hook-adjacent defects, neither about prose routing) | **latent** |
| 7 `cli.md` · 9 `complexity-thresholds.md` · 10 `cross-platform.md` · 17 `models.md` | uncited, path-bound only | **#234** (closed, cross-platform), **#607** (closed, models: *"models.md + audit_code_contract_mismatches force Pydantic on adopters"*) | **latent** for the routing gap; the rules themselves have defect history. |
| D1 `ghi-close` ↛ relocated § Commit-message discipline | dead section pointer after rule v0.2.0 lift | **#327** (the GHI whose fix performed the lift), **#151** / **#311** (closed — the pair that *created* commit-message discipline and promoted it to a commit-msg hook) | **known-blocking**. The lift under #327 moved the destination; the three skills citing it were not swept. Textbook AGENTS.md § DO IT RIGHT 1a coupled-surface miss. |
| D2 `gz ledger tail` escapes `--cli-alignment` | fenced-code-block blind spot in `_collect_verb_references` | **#156** (closed — *"Ceremony demo discovery emits unregistered CLI verbs (index.md → gz index)"* — the GHI that motivated the check), **#432** (closed — *"Brief command-shape check has no speculative-skip marker"*) | **latent for the blind spot itself.** #156 built the check; nothing since observed that its three regexes all require quoting. **No GHI exists for this.** |
| D3 `gz-deps-upgrade` H1 names a non-verb | same blind spot | none | **latent** |
| D4 `§` citations resolve to bold lead-ins / table cells, not headings | 6 call sites across 4 skills | **#692** (closed — *"validator passes hollow handoffs — checks section presence, not population"*) is the same shape one surface over | **latent** |
| 18 `mx-mode.md` marker/quote disagreement | `gz validate --rule-version-markers` fails: `marker=1.0.1` vs `block quote=1.0.0` | none | **latent — and it is a currently-red gate**, not merely a reachability finding. |

## Part 3 — the aging question (#691)

GHI #691 (OPEN) — *"rules: no aging mechanism — skills have `last_reviewed`, rules have
nothing"* — is the structural explanation for the whole R3/R3u population, and this
re-run supplies the missing measurement.

Skills carry `last_reviewed` + a 90-day `SKA-LAST-REVIEWED-STALE` audit wired to a gate.
Rules carry a `rule-version` marker and nothing time-based. The consequence is
directional and now observable:

- Every skill in the inventory has been reviewed within the last 57 days
  (`last_reviewed` spans 2026-06-05 → 2026-07-29); **39 of 68 within the last 7 days**
  (26 on 2026-07-25, 13 on 2026-07-26). The clock works.
- **Twelve rules (48%) are routed to by nothing**, and there is no clock that would
  ever surface that. A rule can be authored, mirrored, budgeted, and version-bumped
  forever without one skill ever pointing at it.
- The six rules added since the 2026-05-10 pass (`agents-md-map-doctrine`,
  `changelog-release-notes`, `guardrail-feedback-prose`, `hexagonal-architecture`,
  `mx-mode`, `task-discovery`) demonstrate the intake side of the same asymmetry:
  **four of six arrived with zero skill routing and have accrued none.** Only
  `changelog-release-notes` (cited + mechanically enforced by `gz-patch-release`) and
  `mx-mode` (bidirectional with `gz-mx`) landed wired.

#691's own framing — *"a deliberate prior exclusion, not an unfulfilled intent"* — is
what makes this a `enhancement`-class finding rather than a correction. But the
measurement above is the evidence #691 asks for: the exclusion has a 48% cost.

## Part 4 — the mechanical-gap ranking

Ordered by (GHI density × grade severity):

1. **`task-discovery.md` ↛ `git-sync`** — 4 GHIs (#201, #552, #708, #731), one open. Producer-side stamping is doing all the work; the doctrine is unrouted.
2. **`chores.md` ↛ `gz-chore-runner`** — 3 GHIs (#605, #728, #743), two open. The chore surface's own gating failure (#743) is why this audit is being re-run.
3. **`gate5-runbook-code-covenant.md`** — 2 GHIs, one open; named the largest gap in 2026-05-10 and unmoved in 83 days.
4. **D1 — `ghi-close` ↛ relocated section** — hard dead pointer, three call sites, one lift GHI (#327) that never swept its consumers.
5. **D2 — fenced-code-block blind spot in `--cli-alignment`** — no GHI. One reproducible failing command (`gz ledger tail`) that a passing gate declares clean.
