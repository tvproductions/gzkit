# Renewing vows — the plan, for the operator's review

> **What this is.** One readable account of R&D run `renewing-vows`, rewritten once on
> 2026-10-10 after the operator closed frontier item 22 and ruled the joined statement of
> command. It is a view over the run record [`../renewing-vows.md`](../renewing-vows.md) and
> has no authority of its own. Where the two differ the record governs and this page is
> corrected. Figures are dated observations; re-run the command before relying on one.
>
> **What it is for.** You reopened the run on 2026-10-07 to review the plan before sign-off.
> Read this, correct it, then rule on § 9. Nothing below has been built on this run's
> authority, and no row has your go. Two direct fixes under GHI #1181 and GHI #1185 were
> built on your separate rulings of 2026-10-10 and are held local, unpushed.

## 1. The problem, as it stands today

You asked on 2026-10-05 for a mid-stream reconceptualisation of gzkit to be converged, in a
military and aviation frame, with ultimate names and an honest account of how much of the
remedy was already planned. The run's first answer was a missing document: a concept of
operations above the PRD. That answer was superseded on 2026-10-08 when the run read
`docs/governance/GovZero/command-doctrine.md`, ratified by you on 2026-06-10, and you ruled
one doctrine, not two: "incorporate and merge/subsume, I am in search of binding/bounding
doctrine for gzkit to hold me and agents to account."

The problem since then, in your words of 2026-10-09: **"canon that disagrees with itself."**
Three acts of 2026-06-09 and 2026-06-10 (the scorecard freeze, the campaign's ratification,
the command doctrine) disagree in seven places and were never reconciled; the doctrine's
worklist was left outside the plan that selects work; and five obligations canon says are
met have no position that owes them (the lapses). The military frame did not create that
problem. It is the instrument you chose to fix it, by giving every obligation a position.

## 2. What you have ruled, in order

| Date | Ruling | Where it lives |
|---|---|---|
| 2026-10-05 | The frame: full military and aviation; combat register at full strength. Green keeps local cleanup. Chase and damage assessment are two roles. Constraints are a Design act. Weaponeering by requirement kind. Model and effort by echelon and role. The tasking order is a ledger event. The artifact ladder's names; migration at 1.0. General orders exist and are tiny. | record, decisions of 2026-10-05 |
| 2026-10-07 | Integrity level as a second axis beside lane. Chore runs are ledger events; findings are not. A rhythm with two slower tiers due on a signal. IOC a waypoint before 1.0; 1.0 is full operational capability with nothing removed. The public texts supplied before their rows are drafted. The run reopened for your review. | record, decisions of 2026-10-07 |
| 2026-10-08 | One binding doctrine, merged. Both frames shape each other, forwards and backwards. The core model: six phases as the process, eight roles as the crew; constraints are flown. Position, role and crew defined. Article 3's title to be amended: an agent is crew. You are commander and captain, not crew; the session is crew. The session's four statements stand; you abide by doctrine and policy and may override and change policy. | record, decisions of 2026-10-08 |
| 2026-10-09 | Phases, stages and positions: "a good start." The June work is discrepancy. A force has doctrine, assets and abilities; a campaign focuses them. The two concepts of command are brought together. The freeze is about assets. The lapses addressed on your go; chores after the run; a patch release soon. | record, decisions of 2026-10-09 |
| 2026-10-10 | **Item 22: gzkit is built with a released gzkit** ('C'). **The joined statement of command stands, in seven lines.** The scope gate and the airlock exit as direct fixes under #1181 and #1185. | record, decisions of 2026-10-10 |

## 3. The doctrine's spine, as ruled

The seven lines are yours as of 2026-10-10 ('it stands, add the seventh'):

1. One human commands. As commander that human shapes intent and decides what the force is
   tasked to do. As captain the same human signs for what ships and can override anything.
   It is one standing and does not divide.
2. Command reaches the work only as orders the harness carries: standing orders for every
   position, a tasking order for one work package. The order is what carries a role's
   auspices.
3. Every obligation has a position, and every position leaves a record. Crew fill positions
   and command nothing. Every obligation has a position is the lapses' remedy.
4. The commander holds positions too, and is bound by doctrine and policy until changing
   them on the record.
5. The campaign says what the force does next and when. Doctrine sets no dates and carries
   no worklist.
6. Work is assessed from records by someone who did not do it. Release is the captain's.
7. The orders that bind construction are the last release's. Doctrine under construction is
   product until released, and is proven on another project before it binds its own making.

Beneath them, your terms: a **position** is an obligation and a role to fulfil it; the
**role** has bounds and auspices; **crew** is the actor within them. A **force** has
doctrine, assets (table of organization and equipment) and abilities; a **campaign** focuses
those abilities for specified goals. The Magna Carta is that campaign. The ten ratified
articles are the force's doctrine; the military process is how the commander employs the
force. They are three kinds of thing and not rivals, on one condition you have already set:
no agent is a subordinate commander.

Line 7 has consequences the record states and nothing more: a repair to a rule, skill or
validator governs only once released; the first step is a release from a tree 200 commits
past `v0.34.8`, and your coming patch release is the vehicle; the surfaces a session loads
from the tree would have to be pinned to the release too, which is unsized; doctrine from
this run is proven on another project (`ADR-0.38.0`'s first sortie) before it binds gzkit's
own making.

## 4. How one work package is flown

The six phases are the process and your eight roles are the crew (ruled 2026-10-08). The
phases are the joint targeting cycle's, JP 3-60 (28 September 2018), which the publication
calls "not time-constrained nor rigidly sequential". The five pipeline stages are the part of
that life the pipeline runs; a stage is a span with its witnesses, a position is an
obligation and a role inside it, and one stage can hold several positions ("a good start",
2026-10-09). The staffing is my drawing of your ruling:

| Phase | Who | What they hand on |
|---|---|---|
| 1. Objectives, guidance and intent | command: you and the order's author | intent, requirements, measures |
| 2. Target development | **target planning** | what changes, what is protected, what is restricted |
| 3. Capabilities analysis | **mission constraints**; the runtime applies the weaponeering rule | contracts, the collateral estimate, the sortie set |
| 4. Commander's decision | command: you initiate | the tasking order |
| 5. Mission planning and execution | **mission planning**, **infiltration**, **ordnance delivery**, **exfiltration**, **decontamination** | plan; entry; red then green; exit; cleanup reported |
| 6. Assessment | **BDA** | damage in three phases, munitions effectiveness, collateral, reattack |

Three of the eight roles (infiltration, exfiltration, decontamination) are the airlock's and
gzkit's own. The airlock is measured as not biting: entries on every launch with a `hold`
that stops nothing; three exits ever for a work package, all in July. GHI #1185 and the
direct fix of 2026-10-10 give the exit its comparison of changed files with Allowed Paths.

**Open seams (frontier item 14):** where mission planning sits (first in your list, fifth in
the cycle); how ordnance delivery and BDA divide; who owns munitions effectiveness. The
collateral output had an owner, the scope report, which lapsed on 2026-06-19 and is restored
locally under #1181.

## 5. What exists, what is queued, what is new

| The remedy needs | Carried by | State |
|---|---|---|
| A runtime that holds a run's position, next command, stage procedure, dispatch outcome and lock continuity | `ADR-0.35.0` briefs 15 to 20 | ADR at 10 of 20; next in the ruled order |
| A second opinion at the convergence moment | `ADR-0.36.0` | 0 of 9 |
| An airlock that bites | `ADR-0.37.0`, Movement B | 0 of 6; exit comparison now a direct fix under #1185 |
| A flight test on someone else's substrate | `ADR-0.38.0` | 0 of 6 sorties ever flown; where line 7's proof is taken |
| The scope report on completion | `OBPI-0.11.0-03`, lapsed; GHI #1181 | report restored on receipts (`85d55a627`); refusal built, held local |
| **New:** the crew split with the sortie matrix | proposed engineering order | row 1 |
| **New:** integrity level as a second axis | proposed engineering order | row 1, conditional on lifting PROVISIONAL |
| **New:** a ledger event per chore run | proposed engineering order | row 1 |
| **New:** an owner for munitions effectiveness | proposed | row 1, after item 14 |
| **New:** pinning session-loaded surfaces to a release | proposed, unsized | row 1, from item 22 |

Your question of 2026-10-05, whether to stop using gzkit to build gzkit, is now answered by
item 22: neither stay nor abandon, but build with a released gzkit.

## 6. The names

The full row-by-row table with sources is the record's nomenclature decision. What changed
since the last review: the Fielding rows are verified from the DAU Glossary ("some" against
"all"); JP 3-60 is cited in its 2018 edition; "handoff → position relief briefing" rests on
JO 7110.65BB Appendix A and JO 7210.3EE paragraph 2-2-4; "challenge-and-response" and the
pilot flying and pilot monitoring split rest on AC 120-71B (read 2026-10-08: the monitor
works at the same time as the flyer, and "assessor" and "briefer" occur nowhere) and on Degani
and Wiener (1990) for the method and the 1990 role names; "work package" and "task card" are
verified maintenance terms and "engineering order" a term only (AC 120-16G); problem reports
have four states and four classes (AC 00-71 and AC 20-189, read 2026-10-08); coverage per level
rests on Hayhurst et al. (2001) for DO-178B; the maintenance planning document is a reference
document beside the MRB report (EASA checklist); 14764 has five maintenance types.

Still contradicted or unsourced, for your ruling at item 13: "watch" and "duty officer" (no
text carries them); "letter check" (operator practice, no regulatory text); the prioritised
target list as the name for an order that is absolute; the hazard-log row; "gates →
objectives" against your five-gate constraint; "change proposal" and "block" in no landed
source; "pilot" for any agent role against Article 3.

## 7. The June discrepancy and the lapses

| Pair | One text | The other |
|---|---|---|
| 1 | Freeze: subtraction now has equal standing | Campaign, a day later: every reductive move deferred past 1.0 |
| 2 | Campaign: reduction deferred | Article 10: accumulated ritual "retires now" |
| 3 | Freeze: too much mechanism; new checks only on observed drift | Article 2: six new mechanisms, one "a gate precondition, not advice" |
| 4 | Campaign supersedes all prior plans | The doctrine's worklist landed after it and is named by no campaign edition |
| 5 to 7 | The freeze's "measure the residual"; "the third state is empty"; the Article 10 audit | No measurement; contradicted in the same file; no run found |

Your readings: the freeze is a statement about assets; the doctrine carried a plan and
"retires now" is the campaign's to time; a doctrine is not a plan, so the campaign did not
subsume it. The lapses, under your go of 2026-10-09: the scorecard's text corrected, five
readings done, the scope report filed and its first part repaired, the coherence audit's
lapse awaiting a campaign amendment. The reconciliation itself is row 4's, inside the merged
doctrine.

## 8. What each row would produce

| Row | What it would produce | Who starts it |
|---|---|---|
| 1 ADR / OBPI | Proposals only, after briefs 15 to 20: the crew split with the sortie matrix; the integrity-level axis; the chore-run event; an owner for munitions effectiveness; the pinning of session surfaces to a release. | You initiate each, or not. |
| 2 GHI / direct fix | Eleven tracked defects, (a) to (k) in the record's map; #1181 and #1185 built and held; the rest filed on your go. | Your go, plus routing picks. |
| 3 chore | Advice only; the board waits until this run closes (your ruling). | You direct admission. |
| 4 docs and rules | The merged doctrine, built on the ten articles with the seven-line statement of command, the three terms, the five terms, the reconciliation of June, Article 3's amended title, the rhythm, and line 7's governor; the campaign plan republished naming it and carrying the IOC waypoint; the PRD repairs; the weaponeering rule; the model-and-effort correction; the names. | Your go. You assemble; I draft each part on your direction. |
| 5 one-shot refactoring | The identifier migration, aliases first, timed to 1.0. | You select its route. |
| 6 no action | The rejected ideas, kept as prior art. | — |

## 9. What I need you to rule, in order

1. **Item 14, the seams**: where mission planning sits; how ordnance delivery and BDA
   divide; who owns munitions effectiveness.
2. **Item 15**: what the constitution is relative to the merged doctrine; whether Article
   3's body, not only its title, gains the position and the role; an article for relief of
   position; Article 6's sizing against the frame's.
3. **Item 13**: the names in § 6 still contradicted or unsourced: keep as stated
   departures, rename, or drop.
4. **The four unanswered statements**: what a policy is (lines 1 to 3); the reading of the
   June pairs under your five terms; whether changing an article differs from changing a
   policy, and what "encourage" consists of.
5. **Does § 1 state the problem you meant?** The restatement at the close is drafted from
   your answer.
6. Then: kill or fund; and the go on each row.
