---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-20T10:59:46Z'
agent: claude-code
session_id: 93064b1c-aab9-498b-8aae-52071fa3b70f
continues_from: .gzkit/handoffs/20260920T013912Z-big-picture-baseline-and-report-scope-repair.md
---

## Current State Summary

Two big-picture reports published and one R&D run closed. No OBPI initiated, no ADR activated, no lock claimed.

The session began by reviewing the 2026-09-19 baseline report, then made three changes to how that report is produced and one change to what the project enforces about its own control surfaces.

`gz-big-picture` went 0.1.1 to 0.2.0 (design and capability coverage), produced `docs/reports/big-picture/2026-09-20.md`, and then went 0.2.0 to 0.3.0 after the operator course-corrected it away from defect-chasing and back to altitude. The enforced AGENTS.md budget moved 50000 to 20000 chars, making the doctrine ceiling mechanical for the first time.

Routing the 2026-09-20 report's findings to the tracker through `ghi-author` Step 0 overturned one of them. That produced `docs/reports/big-picture/2026-09-20-correction.md`, a linked correction under a new id because a published report is immutable.

`gz-rnd` went 0.2.0 to 0.3.0 to claim an existing defect population as a legitimate R&D subject, and the first such run closed as funded at `docs/rnd/ghi-landscape-reorganization.md`.

Tree clean at `d986ebf0b`, 0 ahead 0 behind origin, `gz check` exit 0, open issue queue 56.

## Important Context

Persona: main-session — craftsperson, governance-aware, whole-file reasoning, direct.

The non-obvious constraint a successor most needs: a published report is immutable. `publish_report` refuses a same-id republish with different bytes and `_history()` re-verifies the sha256 of every retained report on every subsequent publish. Correcting a published assessment means a linked follow-up under a new id, never an edit. This session did exactly that.

Workflow-front deltas:

- **new R&D** — `gz-rnd` now carries two subjects. The second (a population the project already carries) was added this session and exercised once. Its boundary against `ghi-triage` is stated in the skill: triage ranks, R&D asks why the class produces.
- **ghi triage** — one issue filed (#1063), one closed (#815). Queue 57 to 56. No queue-wide triage run. The R&D run concluded AGAINST a triage spree on evidence.
- **adr/obpi campaign** — untouched. `ADR-0.35.0` remains topmost at 7/13. The operator ruled `ADR-0.37.0` is not started now, so the airlock findings stay tracked and unselected.
- **handoff system** — this successor records the above; predecessor lineage preserved via `continues_from`.

Two verification habits earned their keep and should be carried forward. First, re-measuring delegated findings before use: a delegated pass concluded Gate 5 had lapsed, and checking the receipts showed `attested` is an ADR-closeout event while OBPI attestation lives inside the completion receipt — all 7 completions since 2026-07-31 carry `attestor: g0`. Relaying that would have been a false claim about the project's central invariant. Second, `ghi-author` Step 0: it overturned a published report finding and revealed that live Draft briefs own the airlock surface.

The `verifier-pipe-gate` hook refused eight shell commands across the session, every refusal correct. Four were verifiers piped into filters; the rest were verifiers followed by another statement, where the shell would report the later statement's exit.

## Decisions Made

- [operator-ruled] Set the enforced AGENTS.md budget to 20000 chars (verbatim: "make agents budget 20k"). Read as the enforced value rather than the doctrine destination, because the same day's second ruling had already moved the destination and closed with "Nothing mechanical reads the range yet".
- [operator-ruled] Amend `gz-big-picture` to cover design and features (verbatim: "the big picture skill needs to say more about gzkit's design and features in addition to its current aspects").
- [operator-ruled] File the narrowed class GHI and publish the correcting follow-up report in the same session, rather than deferring either.
- [operator-ruled] `ADR-0.37.0` is not started now (verbatim: "we are not going to start 0.37.0 now"), so the airlock findings remain tracked and unselected.
- [operator-ruled] Scope the R&D run to one question — why the residue exists — and let the answer determine whether any reorganization is warranted, rather than designing a reorganization first.
- [operator-ruled] Fund disposition rows 1, 2, 3 and 4 of the R&D run; row 1 as propose-only.
- [operator-ruled] Hold `gz-big-picture` at altitude (verbatim: "I don't want big picture to over-chase defects, I just want it to see things from up high and offer deficiencies as a valid output - not only SWOT, but what does the design look like, what is it trying to look like, where is it misaligned, where is blind, etc. it is still a big picture view - what is, what is not, what could be, what maybe shouldn't be").
- [operator-ruled] Fold the twelve-family taxonomy into the closed R&D record as evidence.
- [agent-chose] Authored two content commits for the budget change rather than letting `git add -A` sweep them into one chore commit, because the budget history file itself records that failure at `219d23fd6` and calls the indistinguishability the defect.
- [agent-chose] Disposition `withdrawn` rather than `fixed` for #815, because the cap premise was itself wrong — `e702060e7` restored the cap to 65536 on the doctrine that gzkit sets it — so the contradicting rule changed rather than a fix landing.
- [agent-chose] Left the second row of #815's cause table deliberately empty. Order-independence is not established by today's measurement, since a smaller surface in the same order still renders the must-survive section last.
- [agent-chose] Left #1063 open with a blocker rather than authoring a pool ADR, because the skill's architectural-absence route collides with Architectural Boundary 2, and named the disagreement instead of picking.
- [agent-chose] Re-measured every delegated figure before use, and refuted one outright rather than relaying it.

## Immediate Next Steps

1. Present this state and await the operator's work selection. Nothing here authorizes execution.
2. If the operator resumes R&D disposition row 2: close GHI #1039 using GHI #1051 [settled] as its landed template — same import-cycle mechanism, #1051 [settled] closed fourteen minutes after #1039 was filed, and neither issue cites the other. Re-derive that claim before acting on it.
3. If the operator resumes row 2 for GHI #943: only the control-surface half landed; the paired behavioral evaluation fixtures the body demands have not. Confirm whether the operator considers the remaining half in scope before closing anything.
4. Rows 1, 3 and 4 are funded and unstarted. Row 4 has two concrete pieces: a family and staleness pass for `ghi-triage`, and hardening `ghi-author` Step 0's sibling-cut defense, which failed in this session.
5. Before trusting campaign sequencing on the `doctrine-declared-without-mechanism` family, take the measurement this session named and did not take.

## Pending Work / Open Loops

- **The unmeasured question.** The campaign records the `doctrine-declared-without-mechanism` family at 19 of 32 open issues on 2026-09-02; a full-body pass counted 14 of 57 today. Different readers, different dates, no shared method. If the direction holds, the family the campaign ranks as its dominant producer is shrinking in share while the queue grows, and the sequencing rests on the older figure. This is the single highest-value open loop.
- **R&D disposition rows 1, 3 and 4** are operator-funded and unstarted. Row 1 is propose-only: draft the ADR route for the pool-ADR fence and the homeless-corrective collision and put it in front of the operator. Row 3 is a queue-staleness chore. Row 4 is the two skill hardenings.
- **Row 2 remainder:** GHI #1039 and the open half of GHI #943.
- **GHI #1063** is open with a blocker. Its next concrete operator action is naming whether the enrollment witness is a checklist item under an existing active ADR, a chore-class promotion, or deferred until the campaign can accept it.
- **The airlock surface** is owned by three live Draft briefs under `ADR-0.37.0`, which the operator ruled is not started now. GHI #807 carries the evidence; nothing routes there.
- **Thirteen overlap candidates** are recorded in the R&D record with evidence and acted on by nothing. The sharpest: #1014 and #1015 filed 44 seconds apart with identical probe output, and #1012 and #1013 filed 51 seconds apart on the same three surfaces.
- **Queue decay**, measured not repaired: eleven open bodies cite now-closed siblings as open. GHI #969's argument rests on #889 [settled] being open; #889 [settled] is closed.
- Previously tracked and still unselected, carried from the predecessor: the `scripts/check_proof_freshness.py` stdout-capture behavior, and skill-support-delivery packaging omitting separate skill reference assets.

## Verification Checklist

VERIFIED this session, with the command that produced each figure. Re-measure before asserting current health — these are dated observations, not a claim that all checks were rerun for this handoff.

- `uv run gz test` — 10,541 tests pass, 4 skipped, 91.5s.
- `uv run gz check` — exit 0, 62 steps, run six times across the session on a fully staged tree.
- `uv run gz covers` — REQ coverage 1,794/2,728 = 65.8%.
- `uv run gz validate --cli-alignment` — passes with both new reports in the tree; the retained-record enrollment from the predecessor session held.
- `uv run gz validate --instructions-files-budget` — passes at the new 20000-char budget; AGENTS.md measures 19,787 chars, so live headroom is 213 chars.
- `uv run gz skill audit` — no findings for `gz-big-picture` or `gz-rnd`.
- `uv run gz agent sync control-surfaces` — all four copies of each amended skill byte-identical.
- Ledger-derived, re-measured directly: 16,973 events; airlock 71 in / 29 out with all 53 proceeds on an empty seam-map; `gate_checked` 943 and `attested` 103 both last fired 2026-07-31; OBPI completions 659, last 2026-09-12.
- All 7 OBPI completions since 2026-07-31 carry `attestor: g0` and `obpi_completion: attested_completed`. This refutes a delegated claim that Gate 5 had lapsed.
- `git rev-list --left-right --count origin/main...HEAD` — 0 0, tree clean at `d986ebf0b`.
- Report publication: `report_published` ledger events `2026-09-20` (sha256 `8ba5a0b2054340173`) and `2026-09-20-correction` (sha256 `5aa220f106bd6e181`).

## Evidence / Artifacts

- `docs/reports/big-picture/2026-09-20.md` — the design-and-capability assessment; immutable, witnessed.
- `docs/reports/big-picture/2026-09-20-correction.md` — the linked correction; immutable, witnessed.
- `docs/rnd/ghi-landscape-reorganization.md` — the R&D record, closed as funded, carrying the twelve-family taxonomy.
- `data/instructions_files_budget.json` — the enforced budget, now 20000 for AGENTS.md.
- `docs/governance/instructions-files-budget-history.md` — dated rationale entry for that change.
- `docs/governance/agents-md-doctrine.md` — coupled repair to the Budget targets section.
- `.gzkit/skills/gz-big-picture/SKILL.md` — version 0.3.0.
- `.gzkit/skills/gz-rnd/SKILL.md` — version 0.3.0.
- `.gzkit/insights/agent-insights.jsonl` — the improvement record for the altitude course-correction.
- Commits: `789807374`, `524ac80f9`, `9f1849d75`, `21ad6b4b5`, `6f6071db4`, `d986ebf0b`.
- GitHub: GHI #1063 filed and open with a blocker; GHI #815 closed withdrawn; cross-links posted on #807 and #1017.

## Settled Rulings

973 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
