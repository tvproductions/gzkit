---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-20T13:30:39Z'
agent: claude-code
session_id: 0b8e20e6-386d-483f-abcf-9f80c0a3962e
continues_from: .gzkit/handoffs/20260920T105946Z-big-picture-altitude-and-ghi-landscape-rnd.md
---

## Current State Summary

Took the measurement the predecessor named as its highest-value open loop, then executed three operator rulings that followed from it. Five commits, `4d011e294..3824802f0`. No OBPI initiated, no ADR activated, no lock claimed; `ADR-0.35.0` remains TOPMOST at 7/13 exactly as it began.

The measurement: is the `doctrine-declared-without-mechanism` family shrinking in share? Answer: **no**, and the apparent 59% -> 25% collapse was reader variance. One reader, one criterion, both cohorts, one day gives 28/37 (75.7%) on 2026-09-02 against 38/56 (67.9%) today — a 7.8-point drift while absolute stock grew 36%, with 10 members closed and 20 filed over the 18 days. Eleven borderline calls were carried and flipped in both directions; under every treatment the family is 57-81% of the queue at both dates. The campaign's sequencing premise is VERIFIED, and stronger than the campaign claimed it.

Its numerator verified; its denominator did not. The queue held 37 at that pass's own measurement instant, not 32, so the claim as written was 19/37 = 51.4%, not 59.4%. Repaired by pointer rather than by correcting the integer.

Then three rulings executed: the campaign's two live sequencing sites now cite the measurement record; the governance-prose case routed to the doctrine box, where it turned out to be an already-enumerated scorecard row; and R&D disposition row 3 was drawn and landed as a chore.

Tree clean at `3824802f0`, 0 ahead 0 behind origin, `gz check` exit 0, open issue queue 57.

## Important Context

Persona: main-session — craftsperson, governance-aware, whole-file reasoning, direct.

**The single most useful thing a successor can inherit from this session: the prior-art discipline paid off twice, and both times it PREVENTED work.** `ghi-author` Step 0 was run deliberately for the governance-prose finding and returned "do not file" — the R&D record already carried it as funded row 3. Later, tracing the same finding into the doctrine box found row `17h` of `docs/governance/advisory-rules-audit.md` already scoring the exact clause as **Promotable**, with a partial arm (`gz validate --transcribed-adr-counts`) already built. Two GHIs were not filed because the routing already existed. Run Step 0 before drafting, not after.

**What the trace found underneath, and what it did NOT find.** `data/transcribed_count_surfaces.json` — the registry for the audit that refuses transcribed counts in the live campaign — names `build-to-1.0-campaign-2026-07-18.md`, which `data/active_campaign.json` lists as superseded. The live campaign has been unscanned for 35 days and the check reports green over an archive. Filed as GHI #1064. **It did not cause the `19 of 32` survival** — that audit's subject is ADR OBPI counts and would never have looked at a GHI family share. Two independent gaps, one trace; the causal story would be convenient and is false.

**Archives are not repaired, only linked.** Every correction this session took the linked-follow-up route: the 2026-09-02 amendment block, `capability-control-review-2026-09-12.md` and both R&D-record citations still read `19 of 32` and are correct as dated records. The same principle decided the chore's central constraint — an issue body writing `#889 (open)` is a dated record of what its author observed, so the chore never rewrites it. `gh issue edit` is also outside `.gzkit/rules/gh-cli.md`'s allowed list, which is the rule agreeing with the principle.

**Two detector lessons, both learned the hard way and both now self-test cases.** A window-based detector for `#N (open)` returned 9 hits for 5 real ones — a 44% false-positive rate — by reading `(open)` from a neighbouring `(closed)` list; binding the annotation to the reference it follows is the correctness condition, not a refinement. And the measurement's own reconciliation assert caught its author classifying GHI #837 differently across the two cohorts, which moved the 2026-09-02 figure from 27 to 28.

**Row 4's subject grew during this session and the brief has not caught up.** Row 3's chore concludes that the remedy for decayed annotations is subtractive: amend `ghi-author` to stop transcribing sibling state, because GitHub renders it live. That is a third piece of row-4 work that did not exist when row 4 was written. Separately, Step 0's sibling-cut defense is recorded as having failed in the PREDECESSOR session (#1017 unrecognised as a member of #1063's class) — it did not fail in this one, so the defect is real but intermittent, and a successor should reproduce it before hardening against it.

**A self-reported drift, recorded rather than smoothed over.** `.github/workflows/queue-hygiene.yml` — a new monthly scheduled CI job — was added unilaterally to satisfy `gz validate --gate-callers`. The validator forced *a* caller and forbids grandfathering a newly-authored gate; it did not choose a new workflow file, a monthly cadence, or `0 7 1 * *`. The operator was told after the fact and ruled nothing on it. Leaving it is the standing state.

## Decisions Made

- [operator-ruled] Take the measurement the predecessor handoff named as its highest-value open loop (verbatim, selected from a four-option work picker: "Step 5 — the measurement"). Booked to Layer 2 via `gz handoff decide --decision proceed`.
- [operator-ruled] Repair the campaign's stale family-share figure by pointer rather than by correcting the integer (verbatim: "Pointer, not value"), selected over correcting `32` to `37` in place and over an amendment leaving both live sites as ratified. Reason carried into the amendment: correcting the integer re-creates the same defect one value later with nothing observing it.
- [operator-ruled] Keep R&D disposition row 3 narrow to issue cross-references, with the falsified-premise half demoted to advisory in the chore's own text; route the governance-prose case to the `doctrine-declared-without-mechanism` box instead. Selected over extending row 3 to both surfaces, over recording the prose case without building anything, and over demoting `AGENTS.md:187` to advisory.
- [operator-ruled] Draw row 3 (verbatim: "draw row 3").
- [operator-ruled] Row 4 is the next work to be taken (verbatim: "indicate that row 4 is next"). This handoff records the selection; it does not start it.
- [agent-chose] Did NOT file a GHI for the governance-prose finding. `ghi-author` Step 0 returned it as already routed to funded row 3, and after the operator's re-routing it turned out to be scorecard row `17h`, already enumerated and already **Promotable**. Filing would have shadow-tracked an existing row.
- [agent-chose] Filed GHI #1064 separately rather than folding the superseded-campaign registry into row `17h`. Row 17h scores the general clause; the registry pointing at a retired edition is a specific validator misconfiguration and a different cut.
- [agent-chose] Added the fourth named instance to row `17h` WITHOUT moving its score. Scoring it Mechanical on discharged instances is the laundering the 2026-08-08 ruling forbids, and the row's own argument is that the general form admits no single remedy.
- [agent-chose] Built the row-3 chore at `rung: propose` with no repair verb, and made "never rewrite a body" its central constraint. An annotation was true when authored; editing it falsifies a dated record, and `gh issue edit` is outside the allowed-command list.
- [agent-chose] Registered the chore's baseline shrink-only in `data/waiver_ratchet_registry.json` and proved it with a negative control (a sixth entry exits 3; removing it exits 0). Claiming shrink-only in prose without the registration would have authored a fresh instance of the family this session spent its time measuring.
- [agent-chose] Made the chore `projectLocal: true`, following the `test-consolidation-subtest-sweep` precedent, rather than shipping it canonically in the wheel. Its subject is this repo's own issue-authoring convention, and the canonical surface carries a byte-equivalence validator.
- [agent-chose] Added `.github/workflows/queue-hygiene.yml` as the chore's automatic caller without asking first. Recorded here as drift: `gz validate --gate-callers` forced a caller and forbids grandfathering a newly-authored gate, but did not choose a new workflow file, a monthly cadence, or that cron expression. The operator was told after the fact and has ruled nothing on it.

## Immediate Next Steps

1. Present this state and await the operator's confirmation. Nothing here authorizes execution.
2. **Row 4 is the operator's declared next work** and has THREE pieces, not the two the R&D record lists. (a) Give `ghi-triage` a family and staleness pass beside its ranking. (b) Harden `ghi-author` Step 0's sibling-cut defense. (c) NEW, produced by row 3's chore: amend `ghi-author` to stop transcribing sibling state into issue bodies, since GitHub renders it live — the subtraction GHI #768 [settled] ruled for ADR counts, applied one surface over.
3. Before hardening Step 0 (row 4b), reproduce its failure. It is recorded as having failed in the PREDECESSOR session (#1017 unrecognised as a member of #1063's class); it did not fail in this session, where two deliberate runs both returned correct "already routed" verdicts. Harden against a reproduced instance, not a remembered one.
4. Row 4c has a ready-made template: `data/transcribed_count_surfaces.json` plus `src/gzkit/governance/trust_audits/transcribed_counts.py` are the shape a sibling-state subtraction fence would take. Read GHI #1064 first — that same registry is currently pointed at a superseded campaign edition.
5. GHI #1064 is open, unselected, and drawable at position (c) of the drawn-work order because it closes a named validator-side arm of the NEXT-IN-PRIORITY box. It ranks below the chore estate.

## Pending Work / Open Loops

- **R&D disposition rows 1, 2 and 4 remain funded and unstarted.** Row 3 is complete and landed. Row 1 is propose-only: draft the ADR route for the pool-ADR fence and the homeless-corrective collision and put it in front of the operator. Row 2 is GHI #1039 plus the open half of GHI #943.
- **Row 2's rationale was corrected this session and the correction must not be lost.** The predecessor advised closing #1039 using #1051 [settled] as a landed template on three supporting facts; two are false. #1051 [settled] closed 6h43m after #1039 was filed, not fourteen minutes — the fourteen minutes is #1051 [settled]'s own open-to-close duration — and #1051 [settled] **does** cite #1039. The same-class claim survives (both are implementation/compat-export import cycles, different modules), so #1051 [settled] remains a usable fix template. The near-simultaneous-duplicate framing is not to be relayed.
- **The "thirteen overlap candidates acted on by nothing" open loop is overstated** and should not be carried forward as a merge backlog. Measured: body similarity 2-16%, and in four of five pairs the younger issue cites the older, several explicitly pre-arguing non-duplication. One sub-claim survives — #1014/#1015 share one byte-identical probe block, but it is the evidence-gathering command, not the finding.
- **GHI #1064 is open**: `data/transcribed_count_surfaces.json` scans a superseded campaign edition, so the live plan has gone unscanned for 35 days.
- **Row `17h` of the advisory scorecard remains Promotable** — the general form of "a value in a Markdown doc is illustrative" is still unwitnessed, now with four named instances. Its promotion path is the narrow allowlist shape, not a general grader.
- **One load-bearing decayed cross-reference is surfaced and unresolved**: GHI #969 argues its named remedy is compromised BECAUSE #889 [settled] reports a defect in it, and #889 [settled] closed 2026-09-14. Re-reading #969 against what #889 [settled] landed is judgment work the chore deliberately does not perform. Disclosed in `data/ghi_cross_reference_baseline.json` with that reason.
- **`.github/workflows/queue-hygiene.yml` awaits no ruling but has had none.** It runs monthly from now on. The operator may want to change the cadence, fold it elsewhere, or drop it.
- **Six dependabot advisories were patched; GitHub had not rescanned at session end.** GitPython 3.1.58 -> 3.1.62 (transitive, dev-only via `pygount` and `wily`) and mkdocs-material 9.7.1 -> 9.7.7 in `requirements-docs.txt`, which had drifted from `pyproject.toml`'s already-patched 9.7.7.
- Previously tracked and still unselected, carried from the predecessor: the airlock surface owned by three live Draft briefs under `ADR-0.37.0` (operator ruled it not started), GHI #1063's blocker, `scripts/check_proof_freshness.py` stdout-capture behavior, and skill-support-delivery packaging omitting separate skill reference assets.

## Verification Checklist

VERIFIED this session, with the command that produced each figure. These are dated observations, not a claim that all checks were rerun for this handoff — re-measure before asserting current health.

- `uv run gz check` — exit 0, run five times across the session on a fully staged tree; last run before `3824802f0`.
- `uv run gz validate --waiver-ratchet` — exit 0. Negative control run the same day: a sixth baseline entry exits **3**, removing it returns exit 0.
- `uv run gz validate --gate-callers` — exit 0; 47 gates inventoried, 7 with an automatic caller, 40 accepted as uncalled.
- `uv run gz validate --advisory-scorecard` — exit 0 after the row `17h` edit; the fenced Summary table was not disturbed because the score did not move.
- `uv run gz validate --cli-alignment` — exit 0 with the new chore's docs in the tree.
- `uv run gz chores advise ghi-cross-reference-staleness` — both criteria PASS (self-test 0.0s, gate 6.6s).
- `check_cross_reference_staleness.py --report` — 10 transcribed sibling-state annotations, 5 decayed, 50% rate.
- `check_cross_reference_staleness.py --self-test` — exit 0, after correcting an assertion that was itself wrong (asserted 4 countable annotations, not the 5 first written).
- `uv run mkdocs build --strict` — exit 0 after the mkdocs-material pin change.
- `uv run python -c "import git; print(git.__version__)"` — GitPython 3.1.62.
- The measurement, re-runnable: `docs/governance/f1-family-share-2026-09-20-evidence/measure.py` over a fresh `gh issue list --state all` dump. 2026-09-02 28/37 = 75.7%; 2026-09-20 38/56 = 67.9%; sensitivity 57-81% under every borderline flip; flow 10 closed, 20 filed.
- Denominator correction: the open queue held **37** at the 2026-09-02 pass's own measurement instant (pinned to `#933`'s creation, `2026-09-02T05:00:45Z`), never 32 on that date; it passed through 32 around 2026-08-25/26.
- `uv run gz obpi lock list` — no active locks. `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` — Pending, `pre_closeout`, 7/13, closeout BLOCKED. Both unchanged from session start.
- `git rev-list --left-right --count origin/main...HEAD` — 0 0, tree clean at `3824802f0`.

## Evidence / Artifacts

- `docs/governance/f1-family-share-measurement-2026-09-20.md` — the measurement record, method stated, marked as a dated record.
- `docs/governance/f1-family-share-2026-09-20-evidence/measure.py` — read-only, three fail-closed asserts; one caught the author's own cross-pass inconsistency.
- `docs/governance/f1-family-share-2026-09-20-evidence/README.md` — re-run instructions.
- `docs/governance/build-to-1.0-campaign-2026-08-16.md` — two live sequencing sites now cite the measurement record; § Amendments 2026-09-20 added; archives untouched.
- `docs/governance/advisory-rules-audit.md` — row `17h` carries the fourth named instance; score unmoved.
- `.gzkit/chores/ghi-cross-reference-staleness/CHORE.md` — the chore definition, carrying the never-rewrite-a-body constraint and the advisory demotion.
- `.gzkit/chores/ghi-cross-reference-staleness/check_cross_reference_staleness.py` — the detector and its self-test.
- `.gzkit/chores/ghi-cross-reference-staleness/acceptance.json` — the two criteria.
- `.gzkit/chores/ghi-cross-reference-staleness/README.md` — the human-facing summary.
- `.gzkit/chores/ghi-cross-reference-staleness/proofs/cross-reference-staleness.md` — first-run proof.
- `.gzkit/chores/registry.json` — the chore registered, `projectLocal`, `coherence`/`propose`.
- `data/ghi_cross_reference_baseline.json` — five disclosed dated records, one flagged load-bearing.
- `data/waiver_ratchet_registry.json` — the baseline registered shrink-only.
- `.github/workflows/queue-hygiene.yml` — the monthly automatic caller (added unilaterally; see Decisions Made).
- `requirements-docs.txt` and `uv.lock` — the six dependabot advisories patched.
- `.gzkit/insights/agent-insights.jsonl` — three records: the overlap-claim correction, the refuted #1039/#1051 facts, and the GHI #1064 discovery.
- `docs/rnd/ghi-landscape-reorganization.md` — the R&D record whose row 3 was drawn; unmodified, correct as a closed record.
- Commits: `4a26f55c9`, `ae947ecdf`, `0dacff7f0`, `56e684a89`, `3824802f0`.
- GitHub: GHI #1064 filed and open.

## Settled Rulings

981 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
