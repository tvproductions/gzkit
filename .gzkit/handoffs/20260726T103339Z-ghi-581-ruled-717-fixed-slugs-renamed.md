---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-26T10:33:39Z'
agent: claude-code
session_id: 2b04eebf-d90b-4e6c-bc08-872f6fc5c590
continues_from: 20260726T094159Z-ghi-615-641-landed-authorized-queue-clear.md
---

## Current State Summary

Three commits on main, pushed, ending at 26f3473b7; tree clean and level with origin/main. Resumed 20260726T094159Z under operator authorization booked verbatim as 'i want to continue ghi work: 1, 3, 4, and 5' (session 2b04eebf). Of those four authorized buckets: bucket 1 (GHI #581) is DISCHARGED — one item landed, one measured as already-satisfied, one ruled by the operator; bucket 3 (skill slugs) LANDED; bucket 4 (chain-less handoff) LANDED as GHI #717, filed and closed in-session. Bucket 5 (GHI #615's untouched half) is AUTHORIZED AND NOT STARTED — it is the one carried item. 12 GHIs open (#717 filed and closed within the session, so the count is unchanged).

## Important Context

FIRST, the recurring shape from the predecessor held again and is now three-for-three across sessions: a checker reading one surface while ignoring the adjacent surface that already answers its question. audit_event_schemas held the factory/model-to-schema coupling from the day it landed but was reachable only from a unittest, so GHI #581 proposed a ~4,775-line six-registry collapse to build protection that already existed. A guard nobody can find is a guard that gets re-litigated. Expect more of this family; the cheap probe is 'who calls this, and would an operator find it where they would look?'

SECOND, DO NOT TRUST THE SCOPING PASS'S MEASUREMENTS ON #581 — two of its three claims did not survive re-measurement. Its 'schema - typed_models = adr-evaluation, intrinsic-complexity-attestation, patch-release' is now empty (all three carry event: Literal[...] models at events.py:224, :357, :442). Its claim that ledger_events.json's only references are historical .claude/plans/ and terminal ADR-0.0.37 is FALSE: three Draft briefs declare it as an extension target with unchecked REQs. Re-measure before acting on any remaining claim in that comment.

THIRD, a skill rename has a FIVE-root blast radius, not the four AGENTS.md lists. skill-surface-sync.md § Retirement policy names src/gzkit/skills/ — the wheel-shipping copy — alongside .gzkit, .claude, .agents, .github. Missing it does not fail skill audit; it fails gz validate --distribution, and the recovery is gz validate --distribution --regenerate.

FOURTH, a blanket sed on a rename is a trap when the target name has history. gz-obpi-sync was ALSO the name of a Layer-3 table-sync skill retired INTO this one at ADR-0.0.36, so the rename produced a SKILL.md claiming to absorb itself, and left GovZero/layered-trust.md and ledger-schema.md describing a different tool under the same string. Those two docs now carry dated disambiguating notes rather than rewrites.

FIFTH, mkdocs build --strict was ALREADY BROKEN before this session's work, by a stale nav entry pointing at a manpage renamed in an earlier pass. Nothing in gz check caught it — the strict docs build is not in the default scope. Worth knowing before trusting a green gz check as proof the docs build.

## Decisions Made

[operator-ruled] Work GHI buckets 1, 3, 4, and 5; decline bucket 2 (the Movement A campaign work).
[operator-ruled] Retire .gzkit/schemas/ledger_events.json by forward supersession and keep the file.
[agent-chose] Registered event_schemas as an EXPLICIT validate scope rather than adding it to the --audits bundle (whose help text names four trust-doctrine audits) or promoting it to the default tier — the existing test-tier run inside gz check is unchanged, so this adds a discovery surface, not a second execution.
[agent-chose] Did NOT auto-link continues_from to the newest handoff when fixing GHI #717. handoff_api.py:603-606 already rejected that as asserting a continuity that may not exist, and that reasoning stands; only the author knows the lineage, so the fix asks rather than defaults.
[agent-chose] Made the #717 warning ADVISORY, not a fail-closed gz validate scope. An unlinked handoff can be a genuine chain root; the silence was the defect, not the shape.
[agent-chose] Left GovZero/layered-trust.md and ledger-schema.md describing the pre-ADR-0.0.36 architecture, adding dated disambiguating notes rather than rewriting a legacy architecture doc inside a slug-rename sweep.
[agent-chose] Did NOT resolve #581 item 1 unilaterally — surfaced the operator-doctrine conflict and the three-Draft-brief blocker per Always #9. The operator ruled; the ruling is the disposition.

## Immediate Next Steps

1. GHI #615's untouched half is AUTHORIZED AND NOT STARTED — the only carried item. Roughly 14 hand-rolled ADR frontmatter parsers, the dual ReqKind enum collision, the REQ-ID grammar divergence, and the escalation-keying gap where validate_brief_reconcile still escalates on structural shape rather than lifecycle. It wants a scoping pass before any code; do not open with a diff.
2. Two follow-ups the rename surfaced and deliberately did not fix. .gzkit/skills/gz-obpi-sync/README.md still documents a two-invocation pre-consolidation workflow that no longer matches its own SKILL.md. And docs/user/skills/index.md plus gz-skill-router carry no routed entry for gz-obpi-brief-drift. Both are pre-existing, neither introduced by the rename.
3. mkdocs build --strict is not in the default gz check scope, which is how it stayed broken. Worth deciding whether it should be.
4. GHI #581 stays open on its ORIGINAL observation only — brief-reconcile's existence-only checks. All three scoped items from the scoping pass are now discharged (landed / already-satisfied / ruled). The issue is no longer a tracker for the registry collapse.
5. NOTHING BEYOND ITEM 1 IS AUTHORIZED. Items 2 through 4 need an operator ruling before execution.

## Pending Work / Open Loops

GHI #615's untouched half is the single carried-and-unstarted item, authorized but not begun.

THE SCOPING-PASS MEASUREMENTS ON #581 ARE PARTLY STALE and two claims were falsified this session. Any future work citing that comment must re-measure first.

THE #717 FIX IS ADVISORY BY DESIGN. A chain-root handoff still writes successfully; the operator or agent must read the warning. If silent chain roots recur despite it, the escalation is the gz validate scope named as remedy 2 in #717's body — deliberately not built, because it would fail-close on a legitimate shape.

THE SPEC-TEST DRIFT ADVISORY stands at 2031 findings (2020 unlinked specs, 10 orphan tests, 1 unjustified code change), unchanged in character by this session.

AN UNRELATED INSIGHT from a concurrent session (adr-authoring scope, timestamped 2026-07-26T10:14:06Z, about authoring pool ADRs through gz-adr-create) rode along in 86583cdf7. It was not authored by this session; it is schema-valid and appended through the governed verb, so it was committed rather than dropped.

## Verification Checklist

git log --oneline -3 (expect 26f3473b7, 86583cdf7, 9b409921e);
git status -sb (expect a clean tree level with origin/main);
uv run gz validate --event-schemas (expect exit 0, 'Validated: event_schemas');
uv run gz skill audit (expect passed, 68 canonical skills across 4 roots, blocking 0);
uv run gz validate --distribution (expect exit 0 — regenerated to 114 files this session);
uv run gz cli audit (expect 131/131 commands fully covered);
uv run mkdocs build --strict (expect exit 0 — it did NOT pass before 86583cdf7);
uv run -m unittest -q (expect 7479 or more OK);
gh issue view 717 (expect CLOSED, completed);
gh issue list --state open (expect 12 open, #581 still open on its original observation);
ls .gzkit/schemas/ledger_events.json (expect PRESENT — the operator ruled it kept).

## Evidence / Artifacts

Session commits, all on main and pushed: 9b409921e (fix(validate): promote the event-schema coupling to a validator scope, GHI #581), 86583cdf7 (refactor(skills): rename two slugs onto the verbs they wield), 26f3473b7 (fix(handoff): speak up when a create silently drops the ruling chain, GHI #717).

Runtime surfaces changed: src/gzkit/commands/validate_cmd.py, src/gzkit/cli/parser_maintenance.py, src/gzkit/commands/handoff.py, src/gzkit/governance/trust_audits/cli.py.

Tests changed: tests/governance/test_ledger_event_schema_coverage.py, tests/cli/test_validate_registry_parity.py, tests/test_handoff_cli.py.

Docs changed: docs/user/manpages/validate.md, docs/user/manpages/handoff-create.md, mkdocs.yml, README.md, docs/user/index.md, docs/user/skills/**, docs/governance/skills-catalog.md, docs/governance/governance_runbook.md, docs/governance/GovZero/layered-trust.md, docs/governance/GovZero/ledger-schema.md, docs/governance/work-phases-and-airlock.md, docs/flighttest/manifest.md.

Skills renamed: gz-brief-reconcile to gz-obpi-brief-drift (0.4.0 to 0.5.0), gz-obpi-reconcile to gz-obpi-sync (3.2.0 to 3.3.0), deleted from all five roots. Seven wielding skills bumped: ghi-close 2.6.0, gz-adr-audit 6.13.0, gz-governance 0.7.0, gz-obpi-lock 6.2.0, gz-obpi-simplify 6.1.0, gz-plan-audit 6.4.0, gz-skill-router 6.3.0.

ARB receipts, event-schemas run: arb-ruff-a6fac7b20557402d9257f9fc8b9d537b, arb-step-typecheck-ca51412dca6d45a7b4f3e076430caf47, arb-step-unittest-608df9f3aea84c778aeae6ed56ff7002 (7476 tests OK). GHI #717 run: arb-ruff-1afc0cb3a8714d3b9e4910f57afa8387, arb-step-typecheck-3d30118a97444d968d7d0ef128704475, arb-step-unittest-c024b1fea12843839562025bc3ec1cc0 (7479 tests OK).

Issue activity: GHI #717 FILED and CLOSED with evidence; GHI #709 cross-link comment; GHI #581 two comments (working-pass findings, then the operator ruling on item 1).

Predecessor: .gzkit/handoffs/20260726T094159Z-ghi-615-641-landed-authorized-queue-clear.md. Campaign: docs/governance/build-to-1.0-campaign-2026-07-18.md.

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
- Book the patch release as the session's work and leave the resumed handoff's five advised steps unauthorized (operator verbatim 2026-07-25: "/gz-patch-release"; booked via gz handoff authorize, session e6b3da00). GHI #615's held migration was NOT authorized and was not worked.
- Backfill the runtime label on #532 and #682 only, not on #533 or #710 (Step 1a labeling-recovery). Both landed genuine validator changes under gz validate; #533 is an open tracker with markdown-only commits and #710 was a skill-doc change, so the excluded bucket is correct for them per Step 1a's own guidance.
- Describe only what actually landed for the open GHIs in the narrative, omit #533 entirely, and file a GHI against the closure-marker heuristic after the release completed rather than pausing the ceremony.
- Approve the drafted release notes as written (operator verbatim: "yes"), triggering the Iron Law run of Steps 4a-4e without pauses.
- Fix GHI #714 via Direction 2 -- keep the commit marker authoritative for discovery, consult upstream state one layer down, and downgrade a still-OPEN GHI to a warned bucket the operator adjudicates (operator verbatim: "direction 2"). Directions 1 and 3 were declined.
- Deferring a proven defect with a governance-flavored rationale is not acceptable (operator verbatim 2026-07-25: "slop, bullshit, facade, and wank"). The turn-closing "one thing worth your judgment" note on the git-sync gate gap was rejected as rationalized incompleteness; the correction produced the hook-enforcement investigation, its two commits, and GHI #715. Recorded as an improvement insight per Behavior Rule 11.
- Work GHI #715 and correct campaign line 131 (operator verbatim 2026-07-25: "#715 + campaign line 131"; booked via `gz handoff authorize`, session e4c56baa). This authorized the resumed handoff's advised steps 1 and 2 only; steps 3, 4, and 5 were not authorized at that point.
- Route GHI #615's residual findings by mechanical re-triage into three classes, file a GHI for the scenario-reachability advisory, and confirm the brief_reconcile landing order (operator verbatim 2026-07-25: "Mechanical re-triage into 3 classes; File a GHI; #615 -> #581 -> #641"; booked via `gz handoff authorize`). Routes (i), (ii), and (iii) were declined; building the scenario registry now and accepting Era-1 as permanent were declined; landing #641 first was declined.
- Book the patch release as this session's work and leave the resumed handoff's five advised steps unauthorized (operator verbatim 2026-07-25: "/gz-patch-release"; booked via `gz handoff authorize`, session bfc3ccad). GHI #716, #615 cuts 2 and 3, #581, and #641 were NOT authorized and were not worked.
- Fix the CI failure, diagnosed by the operator from the job log as blocking skill-audit staleness rather than a code runtime defect (operator verbatim 2026-07-25: "fix:"). This authorized the skill-audit repair only.
- Approve the v0.33.3 release narrative as drafted and execute it (operator verbatim 2026-07-25: "yes, appprove the patch release narrative - do the work"), triggering the Iron Law run of Steps 4a through 4e without pauses.
- Decline the near-edge staleness sweep and record it in a handoff instead (operator verbatim 2026-07-25: "no, but place it into a handoff and then git-sync the handoff").
- Authorize the git-sync only, before any handoff steps were worked (operator verbatim 2026-07-25: "authorized, git-sync only"; booked via `gz handoff authorize`, session a76662eb). The stale-pinned handoff's five advised steps were NOT authorized at that point and were not worked.
- Work advised steps 1 through 5 of the current handoff (operator verbatim 2026-07-25: "do these:" followed by the five steps; booked via `gz handoff authorize`). Steps 1 through 3 were completed; 4 and 5 were not started.
- Resolve the skill-version pin collision by asserting the increment rather than the literal, chosen over updating the four frozen constants and over reverting the stamps. The equality pins contradicted REQ-0.0.35-02-04's own wording.
- Add a fixed 75-day non-blocking warn band, chosen over deriving the band from the ceiling and over leaving the gate binary.
- Retire ADR-0.0.33 Invariant 4 rather than build the scenario registry; GHI #716 closed withdrawn against the retirement commit.
- Fix the handoff evidence check's category error when the pre-push gate blocked the retirement, chosen over annotating the two sealed handoffs and over reverting the retirement.
- Work all four authorized buckets (operator verbatim 2026-07-26, booked via `gz handoff authorize`, session 7dd80db9): "GHI #615 cuts 2 and 3, Then #581, then #641, Steps 3 and 4 (the two cheap judgments), Fix the two handoff-surface defects".
- Fix the engine first, then repair genuine drift — chosen over rewriting 22 briefs to satisfy the scrapers as written, and over landing the extractor fixes as a separate prior commit.
- Seal the 8 pre-frontmatter ADR-0.0.1 briefs as `archived` rather than `Completed` — an honest claim that they are no longer a live authoring surface, without asserting a ledger completion they do not carry.
- Scope GHI #581 first and do NOT build — chosen over executing the 6-registry collapse, over building the 6th validator dimension, and over closing the issue unexamined.
- Take GHI #641's own strawman naming: `gz brief reconcile` becomes `gz obpi brief-drift`, `gz obpi reconcile` becomes `gz obpi sync`, and the single-verb `brief` namespace goes away.
- Fix the engine first, then repair genuine drift — chosen over rewriting 22 briefs to satisfy the scrapers as written.
- Seal the 8 pre-frontmatter ADR-0.0.1 briefs as `archived` rather than `Completed` — no ledger completion is asserted.
- Scope GHI #581 first and do NOT build — chosen over executing the collapse, over building the 6th validator dimension, and over closing it unexamined.
- Take GHI #641's own strawman naming, then execute it (operator verbatim 2026-07-26: "refresh it" followed the landing; the rename itself was authorized by the strawman ruling and the follow-up "okay, so what about 641?").
- Work GHI buckets 1, 3, 4, and 5 of the resumed handoff's advised steps (operator verbatim 2026-07-26: 'i want to continue ghi work: 1, 3, 4, and 5'; booked via gz handoff authorize, session 2b04eebf). Advised step 2 — the Movement A campaign work — was NOT authorized and was not worked.
- Retire .gzkit/schemas/ledger_events.json by FORWARD SUPERSESSION and KEEP the file (operator verbatim 2026-07-26: 'forward supersession, keep the file'). Re-affirms the 2026-06-05 doctrine note against the later scoping pass's unqualified 'retire'. GHI #581 item 1 is closed as RULED, not as built — the correct disposition was a ruling, not a diff. No file deleted; the three Draft briefs declaring it as an extension target keep their Allowed Paths.
