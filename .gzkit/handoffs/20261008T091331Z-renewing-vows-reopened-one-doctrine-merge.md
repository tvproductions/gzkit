---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-08T09:13:31Z'
agent: claude-code
session_id: 8c72a519-2957-4d5e-9ed6-e7139f3c3b99
continues_from: .gzkit/handoffs/20261007T065152Z-debt-drained-three-ghis-closed-1028-measured.md
---

## Current State Summary

This document covers one session, 2026-10-07 09:10Z to 2026-10-08, on the R&D run renewing-vows, which the operator re-entered by invoking the gz-rnd skill on `docs/rnd/renewing-vows.md`. It continues the 06:51Z handoff of 2026-10-07 and supersedes the two exit bookmarks written after it.

The run is OPEN. It was signed off as funded on 2026-10-07 and reopened the same day on the operator's word, because the sign-off was taken before the operator had reviewed the plan. The sign-off is recorded as set aside. No disposition row has a go. No OBPI was initiated, no lock was claimed and none is held. No ledger event was emitted for the run.

What the session did, in order. It put seven frontier questions and recorded the rulings. It wrote a readable review of the plan. It landed sixteen source files from texts the operator supplied or that an open host served, and corrected the record where the texts contradicted it. It amended the gz-rnd skill to version 0.5.0 on the operator's direction and synced the mirrors. It built a core model for how one work package is flown. It then found that gzkit already has a ratified command doctrine the run had never read, and on the operator's ruling merged that doctrine and the run's model into one working file.

One sync was pushed during the session, commit a735a6011. Everything after it is staged and goes out with the sync that carries this handoff. The per-change gate has not been run on that staged tree; the pre-push hook runs it.

## Important Context

The largest finding. `docs/governance/GovZero/command-doctrine.md` is canonical, ratified 2026-06-10: ten articles on authority, accountability and automation, to which every gate and procedure must trace. No session of the run had read it. It is named by the GovZero charter, by one pool ADR and by two evaluation records, and by nothing an agent loads each turn. The corpus entry that carried it into AGENTS.md was dropped; the compression sweep of 2026-09-24 records that as row S31. Any work on gzkit's purpose or shape should read that file and the rest of `docs/governance/GovZero/` first.

How the doctrine is to be made. The operator assembles it and directs each part; the agent drafts what is directed and nothing ahead of it. `docs/rnd/renewing-vows/doctrine-merge.md` is a quarry for that work, not a first draft awaiting approval. Its June sections are copied byte for byte and marked RATIFIED; its new parts are marked DRAFT. It applies the doctrine's Article 2 to itself: of eighteen draft policies, two are enforced in full, nine in part and seven by nothing in the harness. The canonical doctrine file is unchanged.

Two agents write the run record. The operator is working with a second agent that finds sources through the desktop app's browser. It wrote five source entries and five source files into the run. The division this session adopted: the other agent lands sources; this session holds decisions, the model, the disposition map and the review. Read the record fresh before every write. One edit failed when the two overlapped.

The gz-rnd skill is operator-invoked only. A later session continues this run only when the operator invokes the skill on the record. If a handoff or the operator points at the run and the skill was not invoked, say so before the first record edit.

Lessons the operator drew out, each on the insights file. Names and a model were written down before any source was read, and research was sent to confirm them. The agent asked for texts the operator already held. The agent took sign-off after a run of recommended-option selections and no review. The agent read a message as an instruction to draft when it was not. Hosts that refuse automated retrieval were not worked around; the operator supplied files instead.

Source standing. The combat register is cited to JP 3-60 dated 28 September 2018, which supersedes the 2013 edition also on file. RTCA DO-178C and A4A MSG-3 are not bought, by ruling; rows that needed them drop the clause number 11.17, any count of objectives, and letter check as anything but the operator's own practice.

Workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-09-20.md`, Workflow fronts section). Handoff system: this document authored; the resumed 06:51Z handoff was not ruled on in this session, because the operator invoked the R&D skill directly. GHI triage: not run; no issue filed, fixed or closed. ADR and OBPI campaign: untouched; ADR-0.35.0 was not inspected this session. New R&D: all of the session's work; the run is open.

## Decisions Made

- [operator-ruled] The consequence bands become a second axis beside lane, proposed only; lane keeps its external-contract criterion (selection: "Second axis, propose only (Recommended)"). The axis is named integrity level (selection: "Integrity level (Recommended)").
- [operator-ruled] A chore run becomes a ledger event and a chore finding does not (selection: "Runs yes, findings no (Recommended)").
- [operator-ruled] The rhythm keeps the session tier of 2026-07-18 and gains two slower tiers that come due on a signal and never on a calendar (selection: "Two slower tiers, signal-triggered (Recommended)").
- [operator-ruled] IOC is a waypoint before 1.0, and 1.0 is full operational capability with its ten gates untouched (selection: "A waypoint before 1.0 (Recommended)").
- [operator-ruled] The five public texts are supplied by the operator before the rows they carry are drafted (verbatim: "b").
- [operator-ruled] The run is reopened for review and its sign-off is set aside (verbatim: "reopen"). The earlier sign-off selection was "Fund (Recommended)".
- [operator-ruled] The gz-rnd skill is improved and the core model is built first (verbatim: "step 1, and improve rnd skill").
- [operator-ruled] The core model is both: the six phases of the joint targeting cycle as the process and the operator's eight roles as the crew (verbatim: "i want both").
- [operator-ruled] Both kinds of planning exist, the plan for the whole and the unit's own (verbatim: "moth are valid, what does our guidance say?").
- [operator-ruled] RTCA DO-178C and A4A MSG-3 are not bought unless a library holds them (verbatim: "these are too expensive unless we think they are availablre in a library:").
- [operator-ruled] A second agent works on the run to find sources (verbatim: "1. yes, I am working with another agent to find the resources you've requested here.").
- [operator-ruled] The command doctrine and the run's model become one doctrine (verbatim: "2. incorporate and merge/subsume, I am in search of binding/bounding doctrine for gzkit to hold me and agents to account.").
- [operator-ruled] They are merged into one file, and the materials assist the operator's doctrine (verbatim: "merge them, they assist in creating my doctrine").
- [operator-ruled] The operator assembles the doctrine and directs; the agent drafts (verbatim: "no, i want to assemble the doctrine. i direct, you draft. for now, we need a handoff and git sync").
- [operator-ruled] The four FAA circulars are entered in the run record (verbatim: "Yes, use these:").
- [agent-chose] Two rulings of 2026-10-07 are recorded as superseded by the one-doctrine ruling, because they were put without the command doctrine in view: the placement of a separate concept of operations (selection at the time: "Under constitution, above PRD (Recommended)") and the content of a constitution draft (selection at the time: "Draft it small, with row 4 (Recommended)").
- [agent-chose] The identifier migration stays timed to 1.0. It was ruled at IOC when IOC meant 1.0; this was carried forward and not put as a new question.
- [agent-chose] Did not use a browser to pass hosts that refuse automated retrieval; asked the operator for files.
- [agent-chose] Held edits to the run record once a second writer was seen, until the operator said how to proceed.
- [agent-chose] Left the canonical command doctrine untouched and built the merge as a separate file, so that ratified text changes only by the operator's ratification.
- [agent-chose] Changed disposition row 6 from commissioned to not pursued, so that the issue-authoring prior-art check treats its ideas as rejected.

## Immediate Next Steps

1. Tell the operator this run resumes only on their invocation of the gz-rnd skill on `docs/rnd/renewing-vows.md`, and confirm against live state: no lock is held, main is in sync with origin, and the sync that carried this handoff passed its gate.
2. Ask the operator where they want to begin assembling the doctrine. The operator directs and the agent drafts. Do not offer a draft ahead of direction. `docs/rnd/renewing-vows/doctrine-merge.md` is the material to draw from.
3. When the operator reaches them, the open questions listed at the end of the merge file are theirs: whether the merged document is the constitution; whether any agent role may be called a pilot against Article 3; that the handoff policy traces to no article; and what to do with the seven policies nothing in the harness enforces.
4. Put the unrouted defects to the operator for routing, one at a time: the command doctrine does not reach agents (sweep row S31); the campaign plan sets five phrases in quotation marks that occur in neither FAA order; both published charters scope Gate 5 to the heavy lane; the gz-rnd offer rule is seated nowhere and the handoff skill does not name the invocation for an open run.
5. Before any write to the run record, check whether the second agent is still working on it, and read the file fresh.

## Pending Work / Open Loops

The R&D run renewing-vows is open. Its frontier, in the record's Close section, holds: the questions under the one-doctrine ruling; the divisions inside the core model (how ordnance delivery and BDA divide, who owns the two assessment outputs nothing produces, the names for the two kinds of planning); the operator's review of the plan; and the names the supplied texts put in doubt (battle rhythm, watch, duty officer, letter check, the prioritised target list as a name for an absolute order, hazard log, gates as objectives, and the ladder names). Sign-off is not put again before the operator has reviewed.

`docs/rnd/renewing-vows/review.md` was written before the one-doctrine ruling. Its sections 5 and 9 carry notes on that ruling, and the rest still describes a separate concept of operations. It needs bringing into line with the merge before the operator relies on it.

The run record's disposition row 4 was updated for the one-doctrine ruling by a guarded edit that may not have applied; its text should be read and corrected if it still names a separate concept of operations.

Sources still unread that carry a row or a proposal: JP 5-0 Joint Planning (two official hosts returned 403); FAA AC 120-51 on crew resource management training; FAA Order 8900.1 and the International MRB/MTB Process Standard for the maintenance review board procedure.

Insights recorded this session and unrouted: both charters scope Gate 5 to the heavy lane; the campaign plan's position-relief quotations; the command doctrine unread by the run; names before sources; sign-off before review; asking for texts already held. Earlier and still unrouted: the gz-rnd offer and resume gap.

The gz-rnd skill amendment at version 0.5.0 is the agent's drafting on the operator's direction; the operator has not read its four rules line by line. `docs/governance/rnd-discipline.md` carries the same amendment.

Still standing from the 06:51Z handoff and not worked this session: its advised steps 4 and 5; the tautological debt ceiling that steps down on 2026-10-14 UTC; GHI #1028 open under its hold; ADR-0.35.0 with ten items outstanding.

## Verification Checklist

The ahead and behind count of main against origin: expect 0 0 after the sync. The OBPI lock list: expect no active locks. The canonical doctrine: `git log -1 --format=%h -- docs/governance/GovZero/command-doctrine.md` should still name a commit of 2026-09-17 or earlier, showing this session did not change it. The merge file: its header should give the canonical file's SHA-256 beginning ad96345626d6. The run record: its Close section should read that the sign-off is set aside. The skill: `uv run gz skill audit` should exit 0 with nothing against gz-rnd, and the skill frontmatter should read version 0.5.0. The sources directory under the run should hold 44 files. A rulings search for "merge them" should return this handoff's ruling.

## Evidence / Artifacts

The run: `docs/rnd/renewing-vows.md`, `docs/rnd/renewing-vows/review.md`, `docs/rnd/renewing-vows/doctrine-merge.md`.

The doctrine it merges, unchanged: `docs/governance/GovZero/command-doctrine.md`, with its worklist at `docs/design/adr/pool/ADR-pool.command-doctrine-internalization.md`.

Source indexes: `docs/rnd/renewing-vows/sources/README-us-gov.md`, `docs/rnd/renewing-vows/sources/README-standards.md`.

Source files written by this session: `docs/rnd/renewing-vows/sources/us-gov-jp-3-60-2018.md`, `docs/rnd/renewing-vows/sources/us-gov-jp-3-60.md`, `docs/rnd/renewing-vows/sources/us-gov-jp-3-30.md`, `docs/rnd/renewing-vows/sources/us-gov-faa-jo-7110-65-position-relief.md`, `docs/rnd/renewing-vows/sources/us-gov-faa-ac-121-22-mrb.md`, `docs/rnd/renewing-vows/sources/us-gov-faa-ac-120-71b-sop-pm.md`, `docs/rnd/renewing-vows/sources/us-gov-faa-ac-120-16g-maintenance-programs.md`, `docs/rnd/renewing-vows/sources/us-gov-faa-ac-20-115d-do-178c.md`, `docs/rnd/renewing-vows/sources/us-gov-faa-ac-00-71-open-problem-reports.md`, `docs/rnd/renewing-vows/sources/us-gov-faa-ac-20-189-open-problem-reports.md`, `docs/rnd/renewing-vows/sources/us-gov-dsca-esamm-glossary-ioc.md`, `docs/rnd/renewing-vows/sources/us-gov-far-part-2-definitions.md`, `docs/rnd/renewing-vows/sources/src-nasa-jacklin-2012-do-178c.md`, `docs/rnd/renewing-vows/sources/src-parasoft-do-178c-overview.md`.

Skill and doctrine record amended: `.gzkit/skills/gz-rnd/SKILL.md`, `.gzkit/skills/gz-rnd/assets/rnd-record-template.md`, `docs/governance/rnd-discipline.md`.

Insights: `.gzkit/insights/agent-insights.jsonl`.

Commit pushed during the session: a735a6011. Predecessor: `.gzkit/handoffs/20261007T065152Z-debt-drained-three-ghis-closed-1028-measured.md`. Exit bookmarks superseded: `.gzkit/handoffs/20261007T090930Z-session-exit-bookmark.md`, `.gzkit/handoffs/20261007T183507Z-session-exit-bookmark.md`.

## Settled Rulings

1433 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
