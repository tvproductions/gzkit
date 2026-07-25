---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-25T20:36:57Z'
agent: claude-code
session_id: e6b3da00-82e8-47a5-ab91-7b12feb5e10b
continues_from: .gzkit/handoffs/20260725T110348Z-ghi-615-three-cuts-migration-held.md
---

## Current State Summary

Cut patch release v0.33.2 (17 qualifying GHIs, GitHub release published, tag on 75064bfb), then found and fixed three defects the ceremony exposed. The last of the three is the material one: this clone had NO git hooks installed at all. .git/hooks/ held only the 14 stock .sample files because a local core.hooksPath (set to git's own default, so invisible) makes pre-commit install refuse. Every commit and push in this clone ran with zero enforcement -- ruff, ty, gitleaks, forbid-pytest, xenon, and the gz check pre-push gate never fired -- and gz validate --session-green-gate reported green throughout because it reads .pre-commit-config.yaml and never inspects .git/hooks/. Hooks are now installed and verified firing. Main at 147c46d2, tree clean and level with origin, no active OBPI lock, no in-flight pipeline, 14 GHIs open. A fresh triage of all 14 was rendered this session.

## Important Context

FIRST, the release ceremony is what exposed everything. gz patch release --dry-run surfaced two OPEN GHIs (#533, #615) as release-qualifying, because discovery reads the project-canonical subject form 'fix(scope): summary (GHI #N)' as a closure declaration. AGENTS.md section Defect-fix routing prescribes that exact form as the scope anchor for ANY GHI-tracked repair, including incremental cuts under a deliberately-open tracker, so the marker attributes work rather than declaring closure. SECOND, the v0.33.2 release manifest itself went red: gz patch release renders one row per GHI from that issue's title, and GHI #532's title literally contains docs/user/manpages/gz-validate.md, so #532's own validator flagged the release record documenting #532. Three tests went red the moment the manifest landed. THIRD, that red tree shipped anyway -- which is what led to the hooks. gz git-sync --apply does not run the suite; it defers to pre-commit, whose hooks did not exist. FOURTH, every uvx-entry hook was running a stale ambient tool BELOW the project's declared floor: ruff 0.15.4 against a >=0.15.20 pin, ty 0.0.31 against a >=0.0.52 pin. ty 0.0.31 emitted 13 narrowing false positives that ty 0.0.55 does not; the commit gate and push gate ran different checkers and the commit gate ran the obsolete one. FIFTH, GHI #598 hit this identical core.hooksPath refusal on 2026-06-09 and classified it 'launcher/precondition drift in setup docs, not a runtime bug'. The caveat was documented and the hooks were still never installed, through every commit for the next six weeks. That classification is the correction-vs-enhancement doctrine failing in the wild. SIXTH, an agent claim made in-flight was wrong and was corrected: the first diagnosis of the red tree blamed a missing --test flag on git-sync Step 4c. The CLI help states --test is 'redundant with pre-commit hook'. The cause was asserted without reading the surface; the real cause was zero installed hooks.

## Decisions Made

- [operator-ruled] Book the patch release as the session's work and leave the resumed handoff's five advised steps unauthorized (operator verbatim 2026-07-25: "/gz-patch-release"; booked via gz handoff authorize, session e6b3da00). GHI #615's held migration was NOT authorized and was not worked.
- [operator-ruled] Backfill the runtime label on #532 and #682 only, not on #533 or #710 (Step 1a labeling-recovery). Both landed genuine validator changes under gz validate; #533 is an open tracker with markdown-only commits and #710 was a skill-doc change, so the excluded bucket is correct for them per Step 1a's own guidance.
- [operator-ruled] Describe only what actually landed for the open GHIs in the narrative, omit #533 entirely, and file a GHI against the closure-marker heuristic after the release completed rather than pausing the ceremony.
- [operator-ruled] Approve the drafted release notes as written (operator verbatim: "yes"), triggering the Iron Law run of Steps 4a-4e without pauses.
- [operator-ruled] Fix GHI #714 via Direction 2 -- keep the commit marker authoritative for discovery, consult upstream state one layer down, and downgrade a still-OPEN GHI to a warned bucket the operator adjudicates (operator verbatim: "direction 2"). Directions 1 and 3 were declined.
- [operator-ruled] Deferring a proven defect with a governance-flavored rationale is not acceptable (operator verbatim 2026-07-25: "slop, bullshit, facade, and wank"). The turn-closing "one thing worth your judgment" note on the git-sync gate gap was rejected as rationalized incompleteness; the correction produced the hook-enforcement investigation, its two commits, and GHI #715. Recorded as an improvement insight per Behavior Rule 11.
- [agent-chose] Routed all three fixes as direct fixes with no ADR or OBPI, per operator canon that GHIs are authorized for direct repair, always. 304 fix() commits in the 60-day window against a threshold of 3.
- [agent-chose] Scoped the manpage-alignment audit to skip docs/releases/ rather than sanitizing the quoted GHI title. A manifest row records what an issue was CALLED; rewriting it falsifies the record. This is the sealed-record doctrine that already exempts terminal briefs and that GHI #682 applied to --sensitivity.
- [agent-chose] Made the session-green-gate delivery arm opt-in rather than unconditional. A fresh CI checkout legitimately has no hooks -- CI IS the gate there and does not push -- so defaulting it on would fail every CI run. Wired it into git-sync, the surface that actually pushes.
- [agent-chose] Repointed all five uvx pre-commit entries to uv run rather than fixing the 13 ty diagnostics. The diagnostics were false positives from ty 0.0.31, a version 24 releases below the project's own declared floor; fixing them would have encoded an obsolete checker's bugs into the source.
- [agent-chose] Did NOT pin the hook toolchain before confirming the version direction. The first hypothesis was that uvx pulled a NEWER stricter ty and that pinning would weaken the gate -- which would have been the staging-flag anti-pattern the predecessor handoff named. Checking the actual versions inverted it: uvx was serving a stale cache below the declared floor.
- [agent-chose] Filed #715 rather than reopening #598. #598's named scope (repair two doc surfaces) was genuinely discharged; the runtime half it deferred without naming is a separate cut and needs its own home.

## Immediate Next Steps

1. Rule on the fresh triage's pull order. All 14 open GHIs were read and ranked this session; the ranking is cached at .gzkit/cache/triage/rank.json and was rendered via the ghi-triage script. The top three are ranked blocking. The campaign remains Magna Carta over this ordering -- triage advises, the campaign governs -- so the ordering needs an operator ruling before anything is pulled.
2. Decide whether the session-green-gate delivery arm belongs in the gz check default scope, not only in git-sync. Today an adopter who never runs gz git-sync gets no signal that their hooks are absent. The blocker is the CI question: a fresh checkout has no hooks by design, so wiring it into gz check unconditionally would fail every CI run. This is the first open design question inside GHI #715.
3. Rule on how to close the residual 36 findings on GHI #615. Carried unresolved from the predecessor handoff and NOT authorized this session. Three routes were presented there and none is agent-decidable; the agent recommendation was route (a), a marker convention letting a Discovery row declare itself a deliverable.
4. Decide the campaign line 131 correction. docs/governance/build-to-1.0-campaign-2026-07-18.md records ADR-0.34.0 at 1/5; Layer-2 carries an OBPI-0.34.0-02 attestation with full receipt evidence, so the true count is 2/5. The session-orientation banner quotes that line, so the stale count is re-injected at every session boot. Carried unedited across six handoffs now because campaign amendments are operator-ratified.
5. Adjudicate the scenario-reachability advisory. gz check reports "scenario-reachability: registry absent (ADR-0.0.34)" from two steps. Pre-existing, unadjudicated, and it survived this session's full green run. Diagnose before acting.

## Pending Work / Open Loops

GHI #715 is the live tracker for the unfinished half of the hook work. What landed is DETECTION ONLY, and only in this repo: audit_session_green_gate gained a check_delivery arm that resolves the worktree's effective hooks directory (honoring core.hooksPath) and asserts a pre-commit-shim pre-push hook is present, and _run_sync_prechecks runs that arm before every sync. What did NOT land: gz init still never runs pre-commit install, so every adopter inherits the same scaffolded-but-not-activated condition; the delivery arm is not in the gz check default scope, so an adopter who never syncs gets no signal; and nothing prevents core.hooksPath being re-set later and silently re-disabling everything, since only the next git-sync would notice.

GHI #714 is CLOSED (fixed in baf1d16f) and needs no further work. Its fix demonstrated itself: #714 was still open at verification time and reported open_upstream with the warning, where the old behavior would have read qualified.

CARRIED FROM THE PREDECESSOR HANDOFF, still unresolved and NOT authorized this session: GHI #615's residual 36 findings and its held 154-brief corpus migration, both built and verified and reproducible from the GHI comment thread. The parser-sprawl half of #615 is also untouched -- roughly 14 modules re-parse ADR frontmatter by hand, the dual ReqKind enum collision persists, and brief_reconcile remains absent from the _build_check_steps assembler so the drift it computes never fails the default gate on its own.

FILE CONTENTION TO SEQUENCE. Three ranked GHIs modify src/gzkit/governance/brief_reconcile.py: #615 (held migration), #581 (existence-only checks), and #641 (the reconcile command rename). Whichever lands first forces the other two to re-target. The triage ranking places them in that order but the operator has not ruled it.

STALE-BLOCKER FLAGS the triage script surfaced and the agent adjudicated but did not act on: #533 cites settled #517 and #712; #581 cites settled #519, whose return-to-health posture has lifted; #594 cites settled #585, which shipped the archive pattern it was waiting for; #641 cites settled #618 and #532, and its Movement IV parking was explicitly withdrawn on 2026-07-18. Each is a citation, not a verdict -- the preconditions have moved but the issues' own merits were not re-argued.

OPEN LOOPS NOT TRACKED AS GHIs. The scenario-reachability advisory is unadjudicated and renders from two gz check steps. Campaign line 131 remains stale by one OBPI and is re-injected at every session boot. The spec-test drift advisory stands at 2027 findings. GHI #551 carries a runtime label but landed no src commits -- the inverse of the #532/#682 problem, harmless this cycle but a labeling-discipline signal worth watching.

## Verification Checklist

git log --oneline -6 (expect 147c46d2, 79b775e8, 651abca3, 3ca549e1, baf1d16f, 75064bfb);
git status --short --branch (expect a clean tree level with origin/main);
ls .git/hooks/ (expect pre-commit and pre-push present, NOT only .sample files -- this is the session's central finding and the thing most likely to regress);
git config --local --get core.hooksPath (expect NO output; if it returns a path, pre-commit install will refuse and enforcement is off again);
uv run gz validate --session-green-gate (expect exit 0);
uv run -m unittest -q (expect 7444 or more OK);
uv run gz check (expect exit 0, with the pre-existing scenario-reachability and spec-test-drift advisories);
uv run gz obpi lock list (expect no active locks);
gh issue list --state open (expect 14 open, including #715);
gh release view v0.33.2 (expect published, latest, body containing only the v0.33.2 block);
uv run gz patch release --dry-run (expect latest tag v0.33.2 and #715 reported open_upstream, NOT qualified -- this is the GHI #714 fix observing itself).

To reproduce the hook-delivery finding from scratch on another clone:
git config --local --get core.hooksPath && ls .git/hooks/ | grep -v sample
An empty second result with a set first result is the zero-enforcement condition.

To re-derive the toolchain divergence:
uvx ruff --version; uv run ruff --version; uvx ty --version; uv run ty --version
compared against the ruff and ty floors in pyproject.toml.

## Evidence / Artifacts

Session commits: `75064bfb` (patch release v0.33.2 -- version sync, manifest, RELEASE_NOTES, CHANGELOG), `baf1d16f` (GHI #714 open_upstream bucket), `3ca549e1` (release-manifest exemption from the gz- prefix gate), `651abca3` (git-sync sweep), `79b775e8` (pre-commit toolchain repoint off uvx), `147c46d2` (session-green-gate delivery arm).

Changed surfaces: `src/gzkit/commands/patch_release.py` (GhiStatus open_upstream, GhiRecord.state, _classify_ghi downgrade); `src/gzkit/governance/trust_audits/cli.py` (_manpage_alignment_sources excludes docs/releases/); `src/gzkit/governance/trust_audits/session_green_gate.py` (_effective_hooks_dir, _delivery_errors, check_delivery param); `src/gzkit/commands/sync.py` (_run_sync_prechecks delivery guard); `.pre-commit-config.yaml` (five uvx entries repointed to uv run); `.gzkit/skills/gz-patch-release/SKILL.md` (Step 1b open-upstream adjudication, skill-version 1.9.0, last_reviewed 2026-07-25) and its four mirrors; `tests/adr/test_patch_release.py`; `tests/governance/test_manpage_alignment.py`; `tests/test_session_green_gate_validator.py`; `tests/commands/test_sync_sweep_guard.py`; `RELEASE_NOTES.md`; `CHANGELOG.md`; `docs/releases/PATCH-v0.33.2.md`.

ARB receipts: `arb-ruff-ba51f82e347d4307bb420af59b40a385`, `arb-step-typecheck-e5d922b0e6e447d286ef1db775fd9e76`, `arb-step-unittest-b7f9d3997057463a94d962ab27e57036` (GHI #714 + manifest exemption); `arb-ruff-51e5e914c3c742ee8905e00742f1931d`, `arb-step-typecheck-be353a1106c54f2fb9f800ec1d259d3c`, `arb-step-unittest-1bc3b68f1e5a492981ba0c57a5f8db06` (delivery arm, 7444 tests).

GHIs: #714 filed and closed (fixed, citing baf1d16f); #715 filed and OPEN (adopter hook activation); runtime label backfilled on #532 and #682; cross-link comments posted on #233 (sibling of #714) and #598 (sibling of #715).

Release: v0.33.2 published at https://github.com/tvproductions/gzkit/releases/tag/v0.33.2, tag on 75064bfb, 17 qualifying GHIs.

Insight recorded: `.gzkit/insights/agent-insights.jsonl` -- improvement, scope agent-defect-routing, on surfacing a proven defect as a judgment note instead of routing it.

Triage artifact: `.gzkit/cache/triage/rank.json` (14 of 14 open ranked, fix() precedent 304).

Skills wielded: `.claude/skills/gz-patch-release/SKILL.md`, `.claude/skills/ghi-author/SKILL.md`, `.claude/skills/ghi-triage/SKILL.md`, `.claude/skills/gz-session-handoff/SKILL.md`.

Campaign: `docs/governance/build-to-1.0-campaign-2026-07-18.md`.
Predecessor handoff: `.gzkit/handoffs/20260725T110348Z-ghi-615-three-cuts-migration-held.md`.

## Settled Rulings

- Work the degrading tier starting with #696 (verbatim authorization booked via gz handoff authorize, session 81765765).
- Finish what is on the plate rather than deferring items for later sequencing rulings.
- Do not assert campaign-movement intent without reading it; the claim that Movement C is shrinking the pre-1.0 board was fabricated and is withdrawn. Movement C is Reduce the accretion.
- #696 defect 2 was the buildable cut; defects 3/4 were NOT to be left to an unbuilt ADR.
- Reframe #580 from periphery criticality to truncation survival (operator verbatim 2026-07-25: 'reframe #580 to truncation survival'). The mechanism is unchanged; the warrant and ranking source are replaced. Arrived AFTER the prior handoff was written and was carried by neither its Decisions nor its Settled section.
- #580's survival declaration is ratified with must-survive = ranks 1-11 (operator-doctrine-verbatim-canon first, architectural-boundaries last), cumulative 21582 B, leaving 11186 B of growth headroom. Ranks 12-20 are declared expendable-under-pressure because they are recoverable, not because they are unimportant. Ratified as data only: applying the order to committed AGENTS.md remains a Layer-1 canon change requiring Gate-5 attestation.
- #580's destination is SPLIT, not a single home. The witness half (declaration plus the assertion that every must-survive section begins before the vendor cap, plus fail-closed declaration completeness) lands with GHI #712. The reorder half (permuting the surface) parks to pool post-1.0, because only it is expensive and it pays off only once the cap binds. This supersedes the withdrawn whole-issue pool recommendation, which rested on a false claim about Movement C.
- GHI #607 is UNPARKED. Attested REQ-0.14.0-04-04 asserts a detection capability and is silent on scope, so an adopter-scope predicate that preserves gzkit's own self-enforcement does not falsify it. No repudiation and no amendment are required to work the issue.
- Work advised steps 1 through 4 (verbatim authorization "do 1 to 4", booked via gz handoff authorize, session 8b138d99).
- Mechanize GHI-blocker freshness by extending the bundled triage script rather than adding a gz verb, so the signal lands in the report the operator already reads before pulling work.
- Work GHI #712 (operator verbatim 2026-07-25: 'authorized, proceed with GHI #712'; booked via gz handoff authorize, session bb837938). This authorized the resumed handoff's advised step 1 only; steps 2 through 5 were not authorized and were not worked.
- Fix the gz check advisory-visibility defect, and file it as a GHI first (operator verbatim 2026-07-25: 'yes, fix this defect'). The defect was surfaced for routing rather than fixed unilaterally because it changes a shared renderer's output contract for every step; the operator's ruling converted it into authorized work.
- Fix the gz check advisory-visibility defect, and file it as a GHI first (operator verbatim 2026-07-25: 'yes, fix this defect'). It had been surfaced for routing rather than fixed unilaterally because it changes a shared renderer's output contract for every step.
- Fix the settled-ruling dedup defect, then author a fresh handoff (operator verbatim 2026-07-25: 'fix, then write me a fresh handoff'). It had been surfaced with routing facts rather than fixed, because 'write handoff' is a narrow skill scope and Always #17 forbids launching unrequested implementation work off the back of one.
- Fix the CI failure (operator verbatim 2026-07-25: "fix this:"; booked via gz handoff authorize, session bd43ecd7). This authorized the CI repair only; the resumed handoff's five advised steps were not authorized and were not worked.
- Write the entire triage into a new handoff for context cleanup (operator verbatim 2026-07-25: "write entire triage to new handoff, i want to clean up").
- Work the triage list in its ranked order (operator verbatim 2026-07-25:
- Proceed with GHI #615 cuts 2 and 3 (migration plus strict enforcement)
- Escalation should key on lifecycle rather than on frontmatter shape
- Dimension-aware Draft scoping: a Draft brief does NOT gate on its own
