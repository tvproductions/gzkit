# R&D run — ghi-batch-closure

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-09-27T20:45Z.

**Challenge.** Operator, verbatim: *"The GHI queue grows faster than it drains (140 opened
vs 113 closed, 2026-09-13→27). Can parallel subagents raise the closure rate — fan out
ghi-close's Read phase across a batch, one writer lands fixes on main, local worktrees
permitted — and should that become a ghi-batch skill? Measure first what share of the open
queue is direct repair versus waiting on operator rulings, and reconcile with
ADR-pool.worktree-parallel-agents, ADR-pool.ledger-concurrency-substrate and
ADR-pool.ghi-triage-closeout."*

Subject class: **a population the project already carries** (the open GHI queue).

---

## source · the rate figures, re-derived

`gh issue list` queries, run 2026-09-27T20:50Z

> opened `created:2026-09-13..2026-09-27` → **140**; closed `closed:2026-09-13..2026-09-27` → **113**; open now → **76**

The operator's figures reproduce exactly. Net growth is +27 over 15 days (about 1.8 a day).
For scale, the prior run measured the open queue at 57 on 2026-09-20. It is 76 seven days later.

## source · ghi-triage's mechanical route cannot answer the measurement question

`uv run python .gzkit/skills/ghi-triage/scripts/triage.py --format json`, run 2026-09-27

> `76 direct-fix` (route); `72 defect`, `2 enhancement`, `2 investigation` (klass); 21 issues carry a `blockers` entry; `precedent_60d: 557`

Every open issue routes `direct-fix`, because the script applies `AGENTS.md` § Defect-fix routing,
*"A GHI authorizes direct defect repair"*. That is **authority**, not **readiness**. The
direct-repair-versus-operator-ruling split the operator asked for is not recorded in any field
and has to be read from bodies and comments. That is a finding in itself: the tool that ranks
the queue cannot tell the fan-out which members are safe to draw.

## source · the prior run on this population

`docs/rnd/ghi-landscape-reorganization.md` § decision · the residue is defined by what an issue needs in order to end · read 2026-09-27

> Counting from the 57 bodies: **8 are explicitly blocked on sequence** (ADR order, an
> unpromoted pool ADR, an operator-held campaign box); **at least 14 name an unresolved design
> question or an operator ruling as their next concrete action**; **19 are class-members whose
> remedy is a class-level witness that does not exist**. The categories overlap, but their
> union is most of the queue. What they share is that **none of them can be ended by writing
> code** — and the fast path only knows how to end things by writing code.

> **Consequence for the challenge.** A triage spree would not drain this queue, because
> ranking does not supply a closure route. The queue is not disorganised; it is an accurate
> record of decisions that only the operator can make, plus a thin layer of genuine decay.

and from § source · the label signature inverts:

> **30 of 30 closed citing a commit SHA, 0 superseded into an ADR or OBPI, 0 closed as
> duplicate**, and 15 of the 30 discharged on just **three** commits. The fast path is not
> thirty repairs; it is a few sweeps each discharging a batch of findings that arrived with
> their fix already specified.

This is the hypothesis the present run must test first. If it still holds at 76, a parallel
Read phase speeds up the part of the pipeline that is not the bottleneck.

## source · the chunking discussion this run inherits

`.gzkit/handoffs/20260927T165044Z-parallel-agents-chunking-discussion.md` § Important Context · read 2026-09-27

> **The pattern: fan out to read, funnel to write.**
> 1. Parallel agents only investigate. [...] They write nothing to the repo.
> 2. The main session verifies each result before relying on it. This session showed why: one of two research subagents invented a Claude Code `skillsDir` setting that does not exist.
> 3. One writer, the main session, applies the changes one after another on main, through the normal commit hooks and the pre-push `gz check`.

> **The case against doing much of this.** The bottleneck is operator attention (rulings, Gate 5 on every OBPI completion), not agent speed.

> If agents ever write in parallel, GHIs need a claim or lock mechanism like `gz obpi lock`; not designed.

Since then the operator has ratified local worktrees (AGENTS.md § Operator Doctrine, 2026-09-27:
*"local worktrees are fine"*), which answers that handoff's second open question.

## source · ghi-close's Read phase and its batch prohibition

`.gzkit/skills/ghi-close/SKILL.md` v2.9.0 · read 2026-09-27

> Four-phase protocol: **read**, **execute**, **verify**, **close**.

> 1a. **Re-derive every stated precondition against the current tree before accepting it.**

> 3a. **Establish the bounded closure contract** above before Phase 2.

> - **Never batch-close GHIs.** One GHI, one disposition, one comment.

> | "Multiple GHIs resolve together; let me close them all with one comment" | Each GHI has its own disposition. Batching conflates them. |

Phase 1 (load, re-derive preconditions, classify shape, check prior commits, write the closure
contract) writes nothing to the repo. It can be parallelized without touching the batch
prohibition, which concerns *closing*. A batch skill that fanned out Phase 1 and funnelled
Phases 2 to 4 through one writer, one issue at a time, would not violate it.

## source · the three pool ADRs

`docs/design/adr/pool/ADR-pool.worktree-parallel-agents.md` (2026-07-26) · read 2026-09-27

> 4. **Write-heavy modes (deferred, dependent):** parallel OBPI implementation
>    under one ADR; parallel independent GHI fixes; parallel ADR pipelines. Each
>    depends on ADR-pool.ledger-concurrency-substrate (single-writer-by-construction)

> **Blocked by**: an operator-ratified doctrine carve-out permitting ephemeral
>   worktrees (amends *"Never create feature branches — work directly on main"*).

`docs/design/adr/pool/ADR-pool.ledger-concurrency-substrate.md` (2026-07-26) · read 2026-09-27

> 1. Parallel/worktree agents write **zero** Layer-2 ledger events during their
>    parallel phase. Their output is code, findings, and worktree-local artifacts only.
> 2. The only surface that appends to `.gzkit/ledger.jsonl` is the **serialized
>    merge-to-main step**.

`docs/design/adr/pool/ADR-pool.ghi-triage-closeout.md` (2026-03-29, amended 2026-04-19) · read 2026-09-27

> 3. For TRIVIAL items, optionally dispatch `gz-ghi-fix` per issue (subagent fan-out or sequential)

> **What it does NOT do.** No pre-decision on whether `gz-ghi-fix` should fan-out via subagents or run sequentially (promotion-time decision).

Reconciliation, first pass. The worktree ADR's promotion blocker (the carve-out) was **ratified
today** as operator doctrine, though no ADR text records it. The ledger ADR's *decision* ("only
the merge lane writes Layer-2") is exactly "one writer lands fixes on main", and a GHI direct fix
emits few or no ledger events anyway. The ghi-triage-closeout ADR proposes `gz-ghi-fix` and
`gz-ghi-triage`; both have since shipped as the `ghi-close` and `ghi-triage` skills, without the
proposed `ghi` CLI verb group. Its open question ("fan-out via subagents or sequential") is **the operator's
question in this run**, and it was deliberately left to promotion time.

## source · how the 113 closures actually happened

`gh issue list --state closed --search "closed:2026-09-13..2026-09-27"`, analysed 2026-09-27

> n 113 · median age 1.7 h · closed ≤24 h: 95 · open >7 d before closing: 11 · stateReason COMPLETED 111, NOT_PLANNED 2
> closed items filed inside the window: **100** · filed before it: **13**
> per day: 09-19 **28**, 09-27 14, 09-26 12, 09-20 10; every other day ≤ 8

Of the 140 filed, 100 closed inside the window, almost all within hours of filing. The fast
path is **not** the bottleneck, and it is already bursty: one day accounts for a quarter of all
closures. The growth comes from **40 of the 140 that did not take the fast path** and from a
drain on the older residue of just **13 in 15 days**. Of those 13, twelve closed `fixed` and one
`withdrawn` (#815, premise falsified). None was superseded into an ADR or OBPI.

The operator's framing, "grows faster than it drains", is therefore two rates, not one:
**in-flight findings close at about 100/140 within hours, and residue drains at under one a day.**
Parallelism can only raise the second rate, and only for the residue members an agent is
permitted to end.

## source · the residue can absorb work without ending

`git log --since=2026-09-13 --format=%s | grep -oE 'GHI #[0-9]+' | sort | uniq -c`, 2026-09-27

> 40 GHI #921 · 6 GHI #1112 · 5 GHI #1053 · 4 GHI #1091 · 3 GHI #1077

#921 has 40 trailered commits in the window and is still open. At least one residue member is
an **epic in GHI clothing**: it takes commit throughput and never reaches a terminal state.
Parallel landing aimed at an issue like that would raise commit count, not closure count.

## source · the ledger is already cross-process safe in one checkout, and tracked in git

`src/gzkit/ledger.py:560`, landed `be75c6b22` 2026-09-06 · `git ls-files` · read 2026-09-27

> `with exclusive_file_lock(self.path):` — *"make append one transaction across writers and across a crash"*

> `.gzkit/ledger.jsonl` → TRACKED · `fix(...)` commits since 2026-09-13 touching it: **64 of 124**

`ADR-pool.ledger-concurrency-substrate` (2026-07-26) opens on *"`.gzkit/ledger.jsonl` is an
append-only file written on the single-writer assumption"*. That premise is **stale for a single
checkout**: since 2026-09-06 two processes appending to one ledger file are serialized by an OS
lock. It remains **true across worktrees**. Each worktree carries its own tracked copy, so two
worktrees that each append would produce divergent tails that git can only reconcile as a merge
conflict at end of file. About half of all direct fixes touch the ledger. The ADR's *decision*,
that only the merge lane writes Layer 2, still stands. The reason it holds has changed: the risk
is no longer interleaved bytes but forked history.

## source · readiness of the open queue, read in full

`docs/rnd/ghi-batch-closure/sources/readiness-2026-09-27.json` (76 rows), produced under
`docs/rnd/ghi-batch-closure/sources/rubric.md` by four parallel read-only agents, 2026-09-27.
**76 of 76 open bodies and all their comments read.** Each reader re-derived stated
preconditions against the live tree.

> R1-ready **35** · R2-ruling **28** · R3-sequence **4** · R4-design **9**

| Filed | n | R1 ready | R2 ruling | R3 sequence | R4 design |
|---|---:|---:|---:|---:|---:|
| before 2026-09-13 | 36 | 6 | 21 | 3 | 6 |
| 2026-09-13..20 | 19 | 12 | 5 | 1 | 1 |
| 2026-09-21..27 | 21 | 17 | 2 | 0 | 2 |

16 of the 35 ready issues were filed **today** (#1110, #1113, #1119–#1121, #1125–#1130,
#1132, #1133, #1135–#1137): one audit sweep's output, fix-specified at filing.

File overlap among the 35 ready issues (estimated from bodies, coupled surfaces such as skill
mirrors not counted): **21 disjoint components, 15 singletons.** Clusters: {804, 810, 813, 907,
1062}, {1126, 1128, 1129, 1130}, {1015, 1032, 1125}, {1119, 1120, 1135}, {1127, 1136, 1137},
{1012, 1013}.

**Verification of the fan-out, by the main session.** Five verdicts spot-checked. #1091:
the reader relied on a brief's `status:` (a derived view); `gz obpi status OBPI-0.35.0-14`
reads *"Runtime State: ATTESTED COMPLETED"* from the ledger, so the verdict holds. #907: the
reader wrote that #611's limit *"has since landed"*, but **#611 is open**. The verdict survives
on the body's own terms (*"this witness can only ever be a **ratchet** ... until GHI #611
lands"*), so the arm is buildable as a ratchet now. #1129, #1124 and #922 are consistent with
the quoted evidence. **One factual error in five; no verdict flipped.**

**Cost of the Read phase, observed.** Wall-clock per 19-issue chunk: 4 min (newest), 8, 12,
21 (oldest dense threads: #921's 12 comments, #978's five closure passes). About 21 minutes
wall-clock against roughly 45 serial. The readers found **stale preconditions on at least nine
issues** (#1091, #1028, #832, #907, #927, #943, #969, #983, #1136): blockers that no longer
hold and that nothing had re-derived.

**Limitation.** Readiness is a single reader's judgment per issue. The readers flagged
R2/R3/R4 boundaries as their least certain (#978/#983, #1003, #1131/#1134). The R1 count is
the more robust number, because R1 needs positive evidence of a derivable fix.

## decision · the queue is two populations, and parallel Read serves only one directly

Reading the measurement against the closure data:

- **Fresh, fix-specified findings** close in hours by the fast path (median 1.7 h, 100 of 140).
  Today's audit batch of 16 is the same kind; it is open because it was filed today.
  Parallel Read gives this population real but modest help. Its fixes are already specified,
  and landing, not reading, is what serializes.
- **The residue proper** (36 issues filed before the window) is **30 of 36 operator-bound or
  undesigned** (21 R2, 3 R3, 6 R4). This re-confirms the 2026-09-20 run at a larger n: that
  run found the residue to be *"an accurate record of decisions that only the operator can
  make"*. No number of agents drains R2. Only rulings do.

So the answer to *"can parallel subagents raise the closure rate"* is **yes for R1 and no for
R2, and R2 is where the residue lives.** The largest thing the fan-out actually produced in
this run was not faster fixes. It was a **per-issue readiness verdict with re-derived
preconditions**, which is exactly the input a ruling session needs and which no current
surface supplies (`ghi-triage` routes all 76 `direct-fix`).

This moves the design question. A batch capability that only fans out `ghi-close` Phase 1
into a landing queue attacks the smaller, faster-draining population. The lever on the residue
is a **ruling docket**: the same fan-out, emitting for each R2 issue the decision it needs,
its options and a recommended answer, so the operator can rule on many in one sitting under
AGENTS.md § Operator Economy of Effort. Whether to build that is the operator's call, and it is
the first frontier question.

## decision · Q1 — the batch capability targets both populations from one fan-out

Operator ruling, 2026-09-27, selecting the recommended option verbatim: *"Both, one fan-out
(Recommended)"*. One parallel Read pass produces two outputs: a **landing queue** of R1 issues
for the single writer (`ghi-close` Phases 2–4, one issue at a time), and a **ruling docket** of
R2 issues (the decision needed, its options, a recommended answer) for the operator to rule on
in one sitting.

Reasoning: the measurement shows the residue is ruling-bound (30 of 36), so a closer-only design
attacks the population that already drains fast. The docket reuses the same Read output and
needs no new write path.

## decision · Q2 — the capability lives in ghi-triage, not a new ghi-batch skill

Operator ruling, 2026-09-27, selecting verbatim: *"Extend ghi-triage (Recommended)"*.
`ghi-triage` already reads every open body, so the parallel Read belongs there. It gains a
readiness verdict (R1–R4, preconditions re-derived) and two renderings, a landing queue and a
ruling docket. The writer then runs `ghi-close` on each R1 issue in order, and `ghi-close` stays
unchanged, including *"Never batch-close GHIs"*. Authority: `.claude/rules/skill-authoring.md`
§ Parsimony 2, *"One home per meaning."* Consequence: the answer to the challenge's *"should that
become a ghi-batch skill?"* is **no**. The `ghi-triage` body must pass a compress-and-merge pass
before it grows (§ Parsimony 6).

## decision · Q3 — the fan-out stops at Read; the single writer executes

Operator ruling, 2026-09-27, selecting verbatim: *"No — Read only for now (Recommended)"*.
Parallel agents read and classify. The single writer executes, verifies and closes each R1
issue on main. Reasoning: the ledger rows `fix(...)` commits actually add are emitted during
execution (`agent_sync_completed` 21, `task_started` 8, `red_receipt_emitted` 7 in the last
40 fixes, plus corpus events). A RED receipt must witness failure on the pre-fix tree, so it
cannot be replayed by the writer after a worktree drafted the fix. That replay is
`ADR-pool.ledger-concurrency-substrate` promotion criterion 2, and it is unsolved.
**Revisit condition:** landing, not Read, becomes the measured bottleneck of the landing queue.

## decision · Q4 — the three pool-ADR drifts go to one GHI, repaired as dated amendments

Operator ruling, 2026-09-27, selecting verbatim: *"One GHI, three amendments (Recommended)"*.
One GHI filed through `ghi-author` names the three drifts with this record's evidence;
`ghi-close` lands a dated `## Amendments` entry in each pool ADR. No promotion, and no decision
changed beyond the facts:

- `ADR-pool.worktree-parallel-agents`: Decision 1 lands work *"via fast-forward/squash at merge"*,
  against AGENTS.md § Operator Doctrine (2026-09-27), *"its result lands on main through the single
  writer, never by merging a branch"*. Its promotion blocker (the carve-out) is now met.
- `ADR-pool.ledger-concurrency-substrate`: its Intent premise has been false in one checkout since
  `be75c6b22`. The live risk is forked tracked history across worktrees; the decision stands.
- `ADR-pool.ghi-triage-closeout`: its `gz-ghi-fix`/`gz-ghi-triage` skills shipped as
  `ghi-close`/`ghi-triage`. Its open question (*"fan-out via subagents or sequential"*) is
  answered by Q1–Q3: fan out the Read, land sequentially. The proposed `ghi` CLI verb group and
  patch-release scope remain.

**commissions:** disposition 2, one GHI.

## decision · disposition 1 fails the admission question

Canon settles this; nothing was put to the operator. Extending `ghi-triage` is a reversible skill
edit, so it fails *"hard to reverse"*. The trade-offs were real, but all three admission
conditions must hold. The skill route goes to row 4. Phase-2 fan-out, the one part that would
warrant an ADR, is held behind `ADR-pool.ledger-concurrency-substrate` under Q3's revisit condition.

## decision · this run's terms are held until the DDD run names the glossary's home

The skill routes terms to `GLOSSARY.md` at the repo root, and that file does not exist. The
design-amendment run found canon declaring two glossary homes, the root file and PRD § 2.1,
and ruled (its Q8, operator verbatim *"We need option A to make up for this lapse"*) that terms
wait for the DDD run to name the home. That ruling is carried forward here, not re-asked.
Held terms, each with its rejected synonym:

- **readiness** — whether an open GHI can be ended by an agent now: R1 ready, R2 ruling,
  R3 sequence, R4 design. _Avoid_: *route* (which `ghi-triage` already uses for authority).
- **landing queue** — the R1 issues, in the order the single writer lands them. _Avoid_:
  *batch* (implies batch-closing, which `ghi-close` forbids).
- **ruling docket** — the R2 issues, each with the decision it needs, its options and a
  recommended answer, for the operator to rule on in one sitting. _Avoid_: *backlog*, *punch list*.

## source · ghi-triage's rank input is structural-only by ruling (re-entry, after sign-off)

`.gzkit/skills/ghi-triage/SKILL.md` v5.3.0 § Step 2 · read 2026-09-27, while starting row 4

> | any other field | **rejected** — the script returns exit 1 if a `rankings[*]` entry contains keys other than `number` and `severity` |

> The schema is structural-only by design: prose fields in the rank input
> duplicated the renderer's output in the operator's chat surface, and only
> removing them from the schema made that impossible (GHI #424).

Row 4 as funded specifies the ruling docket as *"the decision it needs, its options and a
recommended answer"*, which is per-issue prose. The run's frontier was declared empty without
reading `ghi-triage`'s rendering boundary, so this conflict was missed. Per `gz-rnd`, a
signed-off run reopens when later findings send it back. The run reopens for one question
(Q5) before row 4 executes.

## decision · Q5 — readiness is one structural enum; the docket's prose is asked live

Operator ruling, 2026-09-27, selecting verbatim: *"Enum in input; rulings asked live
(Recommended)"*. The rank input gains one structural enum, `readiness`. The renderer groups its
deliverable into a landing queue (ready) and a ruling docket (ruling), still structural (number,
title, severity). The docket's prose (decision needed, options, recommendation) goes into a live
ruling session, one question per R2 issue, the surface AGENTS.md § Operator Economy of Effort
prescribes. GHI #424 holds unchanged: no prose in the input, no duplicate render. Row 4's *What*
is read under this ruling.

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | **not pursued** | No ADR for the `ghi-triage` extension; Phase-2 fan-out not promoted. | The skill edit is reversible, so it fails the admission question. Phase-2 fan-out needs `ADR-pool.ledger-concurrency-substrate` criterion 2 (merge-lane accounting, RED-receipt replay). **Revisit** when landing, not Read, is the measured bottleneck of the landing queue (Q3). |
| 2 | GHI / direct fix | **commissioned** | One GHI via `ghi-author`: three pool-ADR drifts (worktree landing by merge vs. single writer; ledger premise stale since `be75c6b22`; ghi-triage-closeout's shipped skills and answered fan-out question). Repaired as dated `## Amendments` entries. **Filed #1139; fixed at `3db5f97c9` and closed 2026-09-27.** Cross-linked to sibling #837 (same class). | Q4 ruling. Drift is a defect (PRIME DIRECTIVE 5), and it must be trackable (6). Awaits the operator's go on this row. |
| 3 | chore | **not pursued** | No new chore. | `ghi-cross-reference-staleness` already covers closed-GHI references. OBPI- and code-state preconditions are caught by the readiness pass in row 4. **Revisit** if stale preconditions recur between triage runs. |
| 4 | control surface, rule, doc, skill, hook | **commissioned** | Extend `ghi-triage`: compress-and-merge pass first (Parsimony 6), then a readiness verdict R1–R4 with re-derived preconditions, an optional parallel read-only fan-out, a main-session spot-check step, and two renderings (landing queue and ruling docket). `ghi-close` unchanged. | Q1, Q2, Q3 and Q5 rulings. **No new `ghi-batch` skill** (Parsimony 2). **Landed at `ead445895`** (`ghi-triage` 5.4.0; readiness enum in `triage.py`; 8 new tests). Awaits the operator's go on this row. |
| 5 | one-shot refactoring | **not pursued** | — | The six R1 file-overlap clusters (e.g. {1126, 1128, 1129, 1130}, {1012, 1013}) are landing-order facts for the writer, not a refactoring program. |
| 6 | no action | **commissioned** | Do not build worktree-parallel fix execution now, and do not reorganise the residue. | The residue is 30 of 36 operator-bound. Only rulings drain it, and the docket (row 4) is the lever. **Revisit** if the residue share that is R1 rises above today's 6 of 36. |

## Close

**Challenge restated.** The queue does not grow because agents close slowly: 100 of 140
new findings closed with a median age of 1.7 hours. It grows because a residue drains at under
one a day, and 30 of the 36 older members are waiting on operator rulings, sequence or design,
which no number of agents can supply. The question is therefore not "how do we parallelize
closing" but **"how do we put each open GHI in front of the one who can end it, in a form they
can act on at once"**. For the agent, that is a landing queue; for the operator, a ruling docket.
Both come from one parallel read-only pass inside `ghi-triage`, with a single writer landing
fixes on main.

**Frontier.** Empty. Q1–Q4 are ruled; disposition 1 is settled by canon; the glossary home is
carried by the DDD run under design-amendment Q8, and moves no disposition here.

**Sign-off.** Operator, 2026-09-27, verbatim: *"Fund, go on rows 2 and 4"* — **fund**. The row-level
go was given on rows 2 and 4 in the same words.

## What this record does not license

- No ADR, OBPI or chore was started. No pool ADR was promoted or edited.
- Rows 2 and 4 received the operator's go at sign-off. Each executes through its own governed route (`ghi-author`/`ghi-close`; a skill edit under `skill-surface-sync.md`), not on this record's authority.
- The readiness verdicts in `sources/readiness-2026-09-27.json` are one reader's judgment per
  issue. They do not route, close or re-label any GHI, and the 35 R1 issues are not thereby
  drawn. Drawing them is `ghi-close` work under its own contract.
