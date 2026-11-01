# SPEC: The Session Handoff Picture

**Date:** 2026-10-31
**Status:** Accepted 2026-10-31 (operator, verbatim: *"Accept it"*). Nothing here is built.
**Strengthens:** `gz-session-handoff`, in place
**Holder:** a session-and-handoff outcome in family `SES` (legend letter H), from the handback
**Discharges when built:** the two due-by-a-named-event lines under RO-0 in
`docs/governance/harbor-pilotage-candidate-2026-10-15.md` § List of discrepancies, the three-level
brief and the session-exit half of the unwitnessed edges

## 1. The problem

A handoff exists for context management and continuity. The operator also wants three levels of
picture from it, and today nothing produces them:

> "a good handoff snapshots state but also includes analysis and summary of "what happened" and
> "what comes next." the strategic, operational, and tactical summaries are meant to add to that.
> I, as human, am interested in those three levels of picture."

Four gaps stand behind that:

- The seven sections are written for the resuming agent. None is written for the human.
- A session has no running record of its own. What a handoff knows at the end, it reconstructs.
- A handoff does not land itself. Sync is a separate step, and `gz-how` orders it the opposite way
  from the campaign.
- The exit bookmark is not doing its job. Measured 2026-10-31: 469 of 1,113 handoff files are
  bookmarks, they carry boilerplate, at most 42 of 644 authored handoffs and at most 7 of 262 resume
  rulings refer to one, and a written bookmark leaves no ledger event.

## 2. What was ruled

Each ruling is in `.gzkit/insights/agent-insights.jsonl`, scope `handoff-picture`, with the
operator's words. This spec carries them and does not reopen them.

| Ruling | Operator's words |
|---|---|
| The skill strengthened is the existing one | "yes, we are strengthening "gz-session-handoff"" |
| The called-for handoff stays the main act, nothing automatic | "a called-for explicit handoff is highly valuable" |
| Event-boundary markers are withdrawn | "these event boundary markers seem more of the same" |
| Bookmark files give way to a ledger signal | "Yes, ledger signal" |
| At the pauses, recommend a handoff or add to a log | "we should maybe recommend a handoff and/or augmentation of a running session log" |
| The log does not compete with the ledger | "it shouldn't compete with the ledger, it is more of a flight log - mission, planning, events, logs, summaries" |
| The log runs per session | "Per session" |
| Strategic horizon | "major release" |
| Operational horizon is a proxy, not a boundary | "looser than just next minor release, but that is a decent scope proxy" |
| A mode can span levels | "we are currently locked in drydock, but that has some strategic and operational scope" |
| Sync keeps its sweep | "Keep git add -A" |
| Sync is never gated by a handoff (standing canon) | "handoffs should never, never, never, ever, block git-sync. NEVER." |

## 3. The picture

The handoff gains one section, `## The Picture`, with three subsections, written to the operator in
plain language. A level is defined by the question it answers. Its horizon is a guide to scope.

| Level | The question it answers | Scope guide | Reads from |
|---|---|---|---|
| Strategic | What are we building, and why this way? | next major release, 1.0 today | the campaign plan, `gz status` |
| Operational | How is the work sequenced, and what is in the way? | next release, loosely | the repair orders, until a Release Package exists |
| Tactical | What are we doing now, and what is next? | this session | the session log |

Each level says three things: where we stand, what changed, and what is next or at risk. Tactical is
short. A level that did not move says so in one line and names the handoff that last described it,
because padding an unchanged level hides the change that matters. A mode such as the drydock is
placed by the question, so it may appear at more than one level.

The seven sections keep their reader, the resuming agent. The picture restates none of them; it
interprets them for the operator.

**Delivery.** The operator gets the picture without opening the file:

- CREATE ends by printing the picture in the conversation.
- RESUME leads its report with it, after the Claim Verification Gate. The picture is Layer-1
  narrative, so its claims are tagged like any other.
- `gz handoff resume` returns it, and orientation carries a pointer to it.

**Enforcement.** `gz handoff create` gains `--strategic`, `--operational` and `--tactical`, and
refuses mode `CREATE` without all three. The check sits at the verb. It does not join
`REQUIRED_SECTIONS`, because `handoff-documents` validates the existing corpus and a new required
section would fail all of it (`src/gzkit/handoff_validation.py`, the note on `SETTLED_SECTION`).
Sitting at the verb also leaves the mechanical writers alone, the token-block completion and abandon
paths, which author no picture. `CHECKPOINT` may carry one and need not.

This witnesses presence only. No check can say a picture is good. Quality rests on the operator
reading it, and the first accuracy signal is Movement D's `handoff_discrepancy`.

`## The Picture` stays out of `PROSPECTIVE_SECTIONS`, since that tuple must be a subset of
`REQUIRED_SECTIONS`. A closed GHI cited in a picture is not annotated `[settled]`.

## 4. The session log

One file per session, authored only, for what the ledger cannot say: why something was done, what
was surprising, what the plan was. It has the shape the operator named: mission, planning, events,
logs, summaries. The handoff is its debrief and cites it under Evidence / Artifacts.

- **Holds:** the mission, the plan and how it changed, an entry at each boundary or surprise, and
  short summaries. An entry cites a ledger event or commit instead of restating it.
- **Does not hold:** tool calls, test output, or anything the ledger already records.
- **Starts** at the first entry. A short session that reaches no boundary has no log, and that is
  normal.
- **Lives at** `.gzkit/handoffs/logs/<session_id>.md` [agent-chose]. `list_handoffs` globs
  `*.md` without recursing, as `archive/` already relies on, so a log is never read as a handoff.
- **Named** session log [agent-chose], because *flight log* (`docs/flighttest/`) and *passage log*
  (safe mode) are taken.
- **Written by** a new subcommand of `gz handoff` [agent-chose], so an entry gets a stamped time and
  the handoff's secrets check, which a hand-written file skips. It is a Heavy-lane contract change
  with the seven obligations of `.gzkit/rules/cli.md`. It adds no depth-1 command.

## 5. Boundaries

The nine processes of § The processes and their edges are pauses, and exits matter more than
entries. The test: **a handoff is warranted when the strategic or operational picture changed.**

At an exit the agent does one of two things, and the operator decides:

| The picture | The agent |
|---|---|
| Changed at the strategic or operational level | Adds a log entry and recommends a handoff, in one sentence saying what changed |
| Changed at the tactical level only, or not at all | Adds a log entry, or nothing if it would say nothing |

A recommendation is never an action. Nothing fires, nothing is written automatically, and no new
ledger event marks a boundary.

**The reach problem.** A skill body loads only when the skill is invoked, and this behaviour must
fire when it is not. So the rule goes in the one part that is always loaded, the skill's
description, and in `.gzkit/skills/gz-how/references/session-end.md`. Proposed description:

> Use to create or resume a session handoff, and at the exit of a process (mode, R&D, design,
> intake, work package, maintenance, chore, release) to log it or recommend a handoff.

This stays advisory, with no mechanical witness. A hook would be the marker the operator withdrew.

## 6. The handoff lands itself

Invoking the handoff is the operator's go-ahead to push. The order for a concluding session:

1. `gz airlock out`.
2. Commit the session's own `src/` and `tests/` work under its own message and `Task:` trailer.
3. Stage any new file the Evidence section cites.
4. `gz handoff create`, which stamps `last_commit_sha`, the HEAD before the sync.
5. `git add` the handoff and the session log.
6. `uv run gz git-sync --apply --json`, unchanged, with `git add -A` kept.
7. Report the handoff path, then one of: pushed, committed but not pushed, or nothing landed, with
   the blocker verbatim.

Every step is forced by the code as it stands:

- **Step 2** comes first because `gz git-sync` refuses the *whole* sync, before staging anything,
  if `src/` or `tests/` is dirty (`_sweep_governed_paths`, `src/gzkit/commands/sync.py`).
- **Step 3** comes before create because Evidence paths must be tracked, and a new file not yet
  staged refuses the handoff (`validate_referenced_files`). This is probably why `session-end.md`
  syncs first. Its order still disagrees with the campaign (Movement D: "Then `git-sync`,
  unobstructed"), and it would leave the handoff itself unsynced. It takes the order above.
- **Step 5** comes before the sync because a refused sync must not lose the handoff. Staged counts
  as durable (operator ruling 2026-08-05, on the exit bookmark): a staged file rides the next commit.
- **Step 4's stamp** exists because a handoff cannot name the commit that carries it. The next
  session confirms what reached `origin`.

`CHECKPOINT` stops at step 5 and does not sync [agent-chose]. It is a pause, not a departure.

**A blocked sync never fails the handoff.** The skill reports and stops, and it resolves nothing.
This is a normal result when a second agent shares the checkout.

| What happens | State left behind | Who clears it |
|---|---|---|
| `src/` or `tests/` dirty, this session's | nothing committed, handoff staged | this session, by step 2, then re-run |
| `src/` or `tests/` dirty, another agent's | nothing committed, handoff staged | that agent's commit, then a later sync |
| Commit hook refuses, or a stranded `COMMIT_EDITMSG` | nothing committed, handoff staged | the blocker's own recovery text |
| Another agent dirties a tracked file during the sync | committed, not pushed | a later sync; git refuses the rebase |
| Rebase conflict | **stopped mid-rebase** | the operator; the sync does not abort it |
| Push refused, or offline | committed, not pushed | a later sync |

The mid-rebase row is the serious one. `_pull_if_needed` records the failure and leaves the rebase
in progress, so the checkout is left stopped on a conflict for the next session or the other agent.
Observed in a scratch repository, along with the dirty-tree refusal, on 2026-10-31. The session
that hits it says so first, and RESUME checks for it. The known trap, the post-commit recorder
appending rows while commits replay (insight `2026-10-31T09:10:20`, scope `mx-1273`), is still
unfiled and feeds this row.

Every other path in `git add -A` is swept into the handoff's commit, including another agent's
docs, skills or half-written files. The operator ruled this knowingly. Provenance stays readable
because the sync commit lists its anchors and ledger events.

## 7. The exit bookmark gives way to a ledger signal

Every session exit appends one ledger event, proposed `session_exit_recorded`, and writes no file:

| Field | Meaning |
|---|---|
| `session_id` | from the harness payload |
| `exit_reason` | from the harness payload |
| `handoff_path` | the authored handoff this session wrote, or null |
| `head_sha` | HEAD at exit, so a reader can see what came after the handoff |
| `transcript_name` | file name only, through `_portable_transcript_reference`'s rule (GHI #951) |

Coverage changes meaning. `_covering_handoff` asks a repository-wide question: is the newest
authored handoff unfollowed by any commit, on a clean tree? With two agents that answer is wrong
both ways, since another agent's handoff can cover this session and its dirty tree can uncover it.
The signal asks only whether *this session* wrote a handoff, matched on `session_id`, so the skill
always passes `--session-id`. The frontmatter field exists and is optional today.

The signal must earn its keep where the bookmark did not: orientation reports the last exit that
carried no handoff, by session and transcript name, replacing its "Exit bookmarks since" line.

The beat still books and never blocks ("DO NOT BLOCK HERE"). The other half of that ruling, to
"Observe, contextualize, update status, develop suggestions, pose questions", is what the shipped
bookmark never did, and it now belongs to the authored handoff.

**Coupled surfaces.** The writer: `src/gzkit/session_exit.py`, `src/gzkit/hooks/scripts/session_exit.py`,
`src/gzkit/hooks/claude.py`. The vocabulary: `src/gzkit/events.py`, `src/gzkit/ledger_events.py`,
`src/gzkit/governance/trust_audits/events.py`, `src/gzkit/ontology/corpus.py`. The reader:
`scripts/session_orientation.py`. Six test modules name the bookmark.

**Kept as record.** The 469 files stay; `archive` ages them. `is_floor_bookmark` and its readers stay
for as long as those files exist. `session_exit_bookmark_skipped` stays in the vocabulary for its
212 rows, with no new writer.

This witnesses the session's exit edge, row 1 of the edges table.

## 8. Movement D

Measured 2026-10-31, against `docs/governance/build-to-1.0-campaign-2026-09-20.md`:

| Beat | State |
|---|---|
| Exit verification | Partial. CREATE annotates settled citations. No general re-resolution, no turnover timestamp |
| Preview | Landed in part. Orientation runs, and delivers the handoff with it |
| Readiness call | Not landed |
| Briefing against a Position Relief Checklist, with abnormal items | Not landed. No artifact, no schema |
| Assumption | Landed, `gz handoff decide` |
| Deferred review, `handoff_discrepancy` | Not landed. No event |

This spec delivers the human half of the briefing and the unobstructed sync. It leaves the rest with
Movement D: the checklist, the readiness call, `handoff_discrepancy`, and `ruling_issued`. Its two
binding constraints hold here: advisory, never authorizing, and `gz git-sync` never gated.

Also out of scope: `gz-big-picture`, a published report on the whole project, which this does not
replace. The rewrite named for it on 2026-10-29 stays open.

## 9. Mode contract

Stated here per `.gzkit/rules/mode-contract.md`, since its declaration shapes await RO-13.

| Control | Operational | Hangar | Drydock |
|---|---|---|---|
| Picture check at `gz handoff create` | on | on | on |
| Boundary recommendation | advisory | advisory | advisory |
| Session log | on | on | on |
| Sync after handoff | on | on | on, with the change below |
| Exit signal | on | on | on |

**The drydock difference.** Every act there is one commit with a `Task:` trailer naming the repair
order (`docs/governance/safe-mode-doctrine.md`, item 5). The sweep commit carries
`Task: TASK-gz-git-sync`, which names none. So while `mode: safe` is open, the skill commits the
handoff and log itself, as `chore(handoff): <summary>` with the repair order's trailer, as recent
handoffs do, and `gz git-sync --apply` then pushes it. In the hangar the sweep stands.

**MEL.** Nothing here gates, so the standby state of each is the same. The picture check has no
bypass and needs none, because a refused create writes nothing and blocks no sync. (O) if the exit
signal cannot write, the session still leaves, and the limitation is a session with no exit record.
Self-test: their unit tests at the usual interval. The restore condition is any later working run.

`GATE5_INVARIANTS` is not touched.

## 10. Changes by surface

**`gz-session-handoff`.**

- CREATE: the three levels, the sync sequence, the blocked-sync report, always `--session-id`.
- RESUME: lead with the picture, confirm the handoff reached `origin`, check for a stopped rebase.
- Description as in § 5.
- `model: opus`, from `sonnet`: the picture is operator-facing narrative synthesis
  (`.gzkit/rules/model-selection.md`, routing matrix).
- Correct step 4's `write_completion_handoff`, a function no module under `src/gzkit/` defines now.
- Minor version bump, `last_reviewed`, `gz agent sync control-surfaces`.

**Size.** The body measures 491 lines against a ceiling of 497 in
`src/gzkit/skill_body_grandfather.json`, a record of 2026-10-31, and the ceiling may only shrink.
So compression comes first. To lift into a new `docs/governance/session-handoff-rationale.md`:
the gate retirement story in § Operator Authorization, the ruling-store history in step 4 and
the rationalization rows that name no observed failure. The commit says what was compressed.

**Others.**

- `assets/handoff-template.md`: the new section.
- `.gzkit/skills/gz-how/references/session-end.md`: the order of § 6.
- `docs/user/manpages/handoff-create.md`, the new subcommand's manpage and both runbooks.
- The harbor contract's edges table, row 1, when the exit signal lands. The revisit the four-edges
  line named was done on acceptance (contract § Rulings of 2026-10-31).

## 11. Acceptance

| # | Holds when | Proof |
|---|---|---|
| 1 | `gz handoff create --mode CREATE` missing any level is refused, and writes nothing | unit test |
| 2 | `CHECKPOINT` and the mechanical writers succeed with no picture | unit test |
| 3 | The existing corpus still passes `handoff-documents` | `gz check` |
| 4 | `gz handoff resume` returns the picture | unit test |
| 5 | A log entry is stamped, refused on a secret, and never listed as a handoff | unit test |
| 6 | Every session exit appends one event and writes no handoff file | unit test |
| 7 | Coverage follows `session_id`: another agent's handoff does not cover this session | unit test |
| 8 | Orientation reports the last uncovered exit | unit test |
| 9 | A refused sync leaves the handoff staged and the handoff create successful | unit test |
| 10 | The picture reads well to the operator | the operator, on the first real handoffs |

Row 10 is the real test, and no mechanism replaces it.

## 12. Build order

Four independent pieces:

1. **Skill and documents.** The order, the boundary rule, the blocked-sync report, the model and the
   compression. No code. The picture rule waits for piece 2 to be enforced, but the session can
   write it from day one in `--summary` and print it. Lite.
2. **The picture.** Flags, resume and orientation. Heavy.
3. **The session log.** The subcommand and its obligations. Heavy.
4. **The exit signal.** Heavy.

**Route: already ruled.** On 2026-10-30 the operator chose *"A"* for this finding: due by a named
event, held by a session-and-handoff outcome from the handback. Working it by change order under
RO-0 or RO-12 were options B and C, and neither was chosen (harbor contract § Rulings of 2026-10-30).
So the build follows the handback, as the `SES` outcome. The line requires this to be specified
before the first civil-rule work package, which it now is. It does not require it built by then.
