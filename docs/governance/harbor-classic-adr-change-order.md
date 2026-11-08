# Classic ADR change orders of 2026-11-08 — the decision record, on its owning orders

A dated record of the change orders the operator issued on 2026-11-08 to bring the classic
architectural decision record into this drydock. The contract carries the ruling, the change-order
notes on each owning order's row, the list-of-discrepancies lines and the passage-log row
(`harbor-pilotage-candidate-2026-10-15.md`); this page holds the detail they point to. **Owners and
grades in § The change orders were proposed for the operator's review; the operator ruled the owners
by H2 and the grades by H3, both 2026-11-08.**

## Source

The design was settled in a discussion held in another project on 2026-11-07, recorded at
`docs/engineering/proposals/2026-11-07-gz-adr-workflow-discussion.md` in `wtcis-pvecob/cob_projects`,
pinned at commit `74f61ba631fc52ba802f1bfa4b0b680d010dfcbf` (file sha256
`91cc13c1d5d0c39a2cd517c00fa3c48adfff8d97f2af89d2f8d4e4b46f03367f`, 1,621 lines). That repository is
private and this one is public, so the source is summarized here, not copied; the pin keeps it
retrievable by anyone with access. Its research read gzkit at `3f4fc6b7`, 69 commits before this
record; the anchors below are re-read against the tree of this commit.

The source states its own limit: it is *"not adopted policy, an installed skill, or authorization to
change other repositories"*. It holds two audience versions. Only the GZKit version is carried here;
the lightweight version belongs to other projects and nothing in this drydock adopts it.

## The operator's words, in order

Given in this session:

1. *"here is another thing to add for the drydock: docs/engineering/proposals/2026-11-07-gz-adr-workflow-discussion.md"*
2. *"use gh cli"*, with the source URL.
3. By selection, on placement: *"Change orders on anchors (Recommended)"*: one record, a § Rulings
   entry, change-order notes on each owning order's row, discrepancy lines and a passage-log row, with
   the handback inventory held as a contract amendment that waits for the operator's word.

Given in the source discussion on 2026-11-07 and quoted from it (the session that took them was not
this one; they are carried as the source records them):

4. *"I accept Current/Retired with simple revision numbers and a new ADR when the architectural choice materially changes."*
5. *"Yes, I accept the sequential ADR identities and explicit crossover point, with legacy records left intact."*
6. *"I accept ADR-0001-001-title-in-kebab-case.md."*
7. The standing rule the source opens with: a separate, explicit ADR approval checkpoint every time a
   new or superseding decision needs acceptance; spec, plan, implementation or release approval never
   substitutes for it.

## Why change orders, and on which orders

The work scope is frozen at induction, so a finding *"is graded, not added"* and enters *"under its
owning order or a change order the operator issues"* (contract § Repair orders). The source asks for
the same thing in its own terms: the guidance is *"a reconciliation with the existing plan, not a
competing migration program"*, mapped onto anchors that already exist. No new order is opened.

## The settled design, GZKit version

- **What an ADR is.** One architectural choice: its scope, context, credible alternatives, decision
  and rationale, and consequences. A peer of the catalog, as § The general arrangement already draws
  it; not a feature, work or release container.
- **Independent evolution.** Decisions, requirements, feature packages, work packages, orders, tasks,
  instructions, evidence and releases keep separate identities and histories. A link carries
  applicability and constraint, never a synchronized lifecycle, a matching version or an automatic
  cascade. A change calls for checking the links; a linked record is amended only when its own meaning
  changes.
- **Recognition.** A consequential choice about ownership, dependencies, interfaces, persistence,
  recovery, trust or deployment is surfaced as a decision before it is built in. An accepted ADR that
  already covers the work is cited and reused, never re-approved. Routine work and corrections inside
  an accepted decision need no ADR. Justification already on record is recovered before new research is
  commissioned; rationale, alternatives and past approval are never invented.
- **Approval.** Separate, explicit human approval of an identified edition, before the implementation
  that depends on it. General approval of a design, plan, completion or release does not count, and
  completion's Gate 5 is not relabeled as architectural approval. Approval grants no new authority to
  act.
- **State and revision.** Current or Retired, with no lasting Proposed or Rejected state; drafting is
  preparation, not authority. An integer document revision, independent of any product version. An
  editorial amendment keeps the choice, increments the revision and leaves `approved_revision` on the
  edition actually approved; a materially different choice is a new ADR with its own approval.
  Retirement records date, reason and replacement.
- **Form.** File `ADR-0001-001-title-in-kebab-case.md`: decision number, edition, title. Fields `id`,
  `title`, `revision`, `state`, `decision_date`, `revision_date`, `approved_by` (`g0`),
  `approved_revision`, `approval_ref`, and on retirement `retired_date`, its reason and replacement.
  Body: scope, context, alternatives, decision and rationale, consequences; Confirmation when useful,
  linking evidence rather than holding it. Prior editions live in version history.
- **Crossover.** Legacy version-shaped ADRs and mADRs keep their files, ids, dates and evidence; no
  blanket rename or deprecation. New records take sequential ids from an explicit crossover point.
  Freezing a legacy container does not retire the choices recorded in it; each is reconciled on its
  own.

## The change orders

Each line names the owning order, what the order gains, and a proposed grade.

| # | Owning order | What it gains | Grade (ruled by H3) |
|---|---|---|---|
| CO-1 | RP-6, contradicted canon | The ADR authoring surfaces moved to the decision-only form for new records, legacy records untouched: `.gzkit/templates/adr.md` (still carries `semver`, § Checklist, § Decomposition Scorecard and an attestation table), `src/gzkit/schemas/adr.json` (status enum `Pool` … `Deprecated`, `kind` derived from semver), the skills that author ADRs (`gz-adr-create`, `gz-plan`, `gz-design`) and their manpages, each through its generator. Canon that still states ADR-checklist containment is listed for its owner: root `AGENTS.md` § Gate Covenant (*"ADR Feature Checklist items and OBPI briefs correspond 1:1"*) is cut only by the operator (RP-7 stage 7) | blocks return to service (exit item 5) |
| CO-2 | RP-6, with CO-1 (**ruled 2026-11-08**, H2) | The identity crossover: the resolver seam accepts the sequential decision id and the edition reference (`ADR-0001`, `ADR-0001-001`), new ids never collide with a retained id or alias, and the crossover is the commit that lands CO-1 and CO-2 together (H4). The October identifier program's 1.0 timing and bulk-rename clauses are reconciled explicitly, not silently overridden | blocks return to service (exit items 2 and 11) |
| CO-3 | RP-4, release | Confirmation only: no ADR-derived release, version or closeout survives, and a legacy semver is never read as a document revision | inspected at RP-4's close |
| CO-4 | RP-5, RP-12 and RP-14 | Confirmation only: decomposition, execution, inspection and Gate 5 stay on the work and order surface; no ADR checklist containment returns | inspected at each order's close |
| CO-5 | RP-8, the in-flight work | ADR-0.35.0's freeze does not retire the architectural choices inside it; each is carried as a decision, retired with a reason, or captured afresh with honest provenance | due by RP-8's carry acts at civil rule |
| CO-6 | the existing *design acceptance* discrepancy line (RP-0, holder D) | The architectural-approval producer: the event that books `approved_by`, `approved_revision` and `approval_ref` against the reviewed edition. Today only `adr_created` exists | due by a named event: before the first classic ADR is made Current |
| CO-7 | the contract itself, by amendment only | Exit item 9 gains a decision-reconciliation inventory: decisions retained, missing ones captured with provenance, editorial corrections told apart from changed choices, retirements linked to replacements, and approval gaps put to the operator | **ruled 2026-11-08** (H1): amended into § Exit item 9 |

## Held rulings

Put to the operator one at a time; none is assumed. All six were ruled on 2026-11-08.

- **H1. Ruled 2026-11-08.** Amend Exit item 9 with the decision-reconciliation inventory (CO-7)? The
  contract changes only by its own amendment (§ Records, B1). Operator, by selection: *"Amend item 9
  as drafted (Recommended)"*. The text, put to the operator before the ruling, now stands in § Exit
  item 9 of the contract. Scope at the ruling: about 74 version-shaped legacy ADRs (44 foundation
  `0.0.x`, 30 feature) under `docs/design/adr/`, counted by filename on 2026-11-08; the 204 pool
  entries are excluded.
- **H2. Ruled 2026-11-08.** RP-2 closed on 2026-10-19 with no identifier changes, and its grammar is
  legacy-shaped. Put to the operator: A, RP-6 with CO-1, after the precedent of 2026-10-30 that put
  the capability records on RO-11, their first writer, rather than reopen the closed RO-3; B, RP-14
  as first drafted; C, reopen RP-2. Operator, by selection: *"RP-6, with CO-1 (Recommended)"*. The
  new form and its id land in one order; RP-6 takes code in the resolver seam.
- **H3. Ruled 2026-11-08.** The grades in § The change orders. Put to the operator: A, as proposed;
  B, CO-6 blocking too, so the sea trial could run a real classic-ADR approval; C, CO-1 and CO-2 due
  before the first classic ADR is authored, short of exit item 5. Operator, by selection: *"Accept as
  proposed (Recommended)"*.
- **H4. Ruled 2026-11-08.** The crossover point. Put to the operator: A, the RP-6 commit landing CO-1
  and CO-2 together; B, the handback ratification; C, the 1.0 release, keeping the identifier
  program's freeze. Operator, by selection: *"The RP-6 landing commit (Recommended)"*. From that
  commit authoring refuses a new legacy-shaped ADR, and its SHA is recorded in the contract's passage
  log and here when it lands. The ruling supersedes the identifier program's *"no artifact takes a new
  prefix before 1.0"* for ADRs only. No `ADR-<4 digits>` id existed in the tree on 2026-11-08
  (`git grep`), so the sequence starts at 0001; the first sequential record is the first decision the
  operator approves after the crossover, none pre-assigned.
- **H5. Ruled 2026-11-08.** The final id grammar. Put to the operator: A, minimum widths with the
  seam's slug; B, exact widths refused at overflow with a stricter, capped slug; C, minimum widths
  with a stricter slug for classic ADRs only. Operator, by selection: *"Minimum widths, seam slug
  (Recommended)"*. The id is `ADR-[0-9]{4,}` alone; the edition file is
  `ADR-[0-9]{4,}-[0-9]{3,}-<slug>.md`, zero-padded to at least four and three digits, so nothing is
  renamed past 9999 or 999. The slug is the seam's `SLUG_BODY`, `[a-z0-9-]+`
  (`src/gzkit/core/models.py:29`), which legacy ADR, pool ADR and OBPI ids already share. The
  filename changes with each revision; the id does not. Correction disclosed: the question put to the
  operator also said work packages use that slug body; they do not reference it (LSP references,
  2026-11-08). The ruling does not rest on that clause.
- **H6. Ruled 2026-11-08.** Whether § The general arrangement states the classic ADR design, by
  contract amendment. Put to the operator: A, the ADR row amended and the independent-evolution
  invariant stated once in § How work moves; B, both in the ADR row; C, no amendment, short of exit
  item 11. Operator, by selection: *"Row, plus invariant in How work moves (Recommended)"*. Both texts,
  put to the operator before the ruling, now stand in the contract.

Every held ruling is ruled. What remains is the work itself, under its owning orders.

## Not carried

- The lightweight audience version and every cross-project binding (gz-skills, the starter,
  Superpowers workflows and Backplane): the source assigns them elsewhere and authorizes no rollout.
- The source's invented sample ADR and its COB-specific examples: illustrative, not gzkit canon.
