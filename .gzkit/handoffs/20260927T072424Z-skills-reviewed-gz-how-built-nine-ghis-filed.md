---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-27T07:24:24Z'
agent: claude-code
session_id: 05eb1eb0-3e7c-40dc-bfcf-d0b15dc22900
continues_from: .gzkit/handoffs/20260926T131431Z-complexity-ghis-fixed-skills-reviewed.md
---

## Current State Summary

This session resumed `20260926T131431Z-complexity-ghis-fixed-skills-reviewed.md` (ruling booked with gz handoff decide) and worked to operator direction throughout. No OBPI work was initiated and no lock is held.

Skill reviews, clearing the 2026-10-23/24 pre-push Skill audit deadline for all six due skills: gz-implement and gz-migrate-semver (ee0da1024), gz-pythonic-pattern-detect and gz-state (9b0fa04a8), gz-validate and gz-obpi-brief-drift (e68d248f0). Each rewrote the skill from its code and corrected the echoing manpages and docs pages.

New meta skills, built directly by operator variance with no ADR: gz-how, the "how do I / what can I" flow guide (hub plus 18 flow files, agent-invocable), and gz-skill-review, the review procedure (12cbc49a3, GHIs #1106 and #1107). gz-skill-router is retired from every surface root. New default-tier scope `gz validate --how-coverage`. AGENTS.md SKILLS FIRST gained the canon line pointing unclear skill selection at gz-how (c6de50d0f).

Defects fixed: #1108 skill references never reached adopters (5918234cd sync, 49959032a gz init scaffold); the validator-reachability ratchet read default-tier scopes as ungated (649faf6f0, baseline 51 to 39); AGENTS.md gate covenant prescribed the deprecated gz gates (f1ab5ee56); #1109 retention sidecar had no trailing newline (2324263c9). GHIs #1106 to #1109 are closed with evidence.

Nine remaining findings filed as GHIs #1110 to #1118; none worked yet. HEAD 2324263c9 was pushed and level with origin/main before this handoff; the uncommitted changes are ledger rows and this handoff.

## Important Context

Workflow fronts source: docs/governance/build-to-1.0-campaign-2026-09-20.md § Workflow fronts. This session touched ghi triage and skill maintenance; it did not touch the adr/obpi front. ADR-0.35.0 is still the lowest open feature ADR (8/14; closeout blocked on OBPIs 07, 08, 10, 11, 12, 13); ADR-0.38.0 is campaign-reserved, so the next free feature id is ADR-0.40.0.

gz-how's catalog is written as `| Intent | Skill |` tables, so router_tables counts gz-how as a router (it covers every skill the retired router did) and the delivery filter drops gzkit-only rows for adopters. Flow files under references/ must never name a project_local skill: the withheld-slug test now scans every delivered .md. A catalog row whose second cell is a backticked non-skill fails router_tables at exit 3, so bare commands in gz-how tables are written with trailing text after the backtick.

Canon change path, as run twice this session: gz content remember, gz content retire for a replaced entry, compose a candidate, gz content advise-rendition, gz content commit with the operator's verbatim words, gz agent sync control-surfaces. A candidate that removes a block needs a retention map: an independent reviewer (a different model, fresh context) extracts the conditions verbatim, the author maps each kept or dropped, the operator rules every dropped id in their own words, and quotes must cover punctuation or the gate refuses.

The verifier-pipe-gate hook refuses a verifier piped or followed by another statement: capture to a file and echo $? in the next statement, or use set -e. gz obpi brief-drift appends a brief_reconciled ledger event on every run, dry runs included. docs/user/skills pages are hand-written echoes of their skills with nothing tying them (#1111).

## Decisions Made

- [operator-ruled] Verbatim: "review gz-implement and gz-migrate-semver" (ee0da1024).
- [operator-ruled] Verbatim: "review gz-pythonic-pattern-detect and gz-state" (9b0fa04a8).
- [operator-ruled] Verbatim: "review gz-validate and gz-obpi-brief-drift" (e68d248f0).
- [operator-ruled] gz-how design, verbatim selections: router fate "Replace it (Recommended)"; freshness "Validator enforces coverage (Recommended)"; answer scope "Skills first, commands as fallback (Recommended)"; boundaries "Yes, as a short section (Recommended)"; name "gz-how (Recommended)"; distribution "Ship it; mark gzkit-only entries (Recommended)"; structure "Hub + one file per flow (Recommended)"; self-selection "gz-how (Recommended)"; steering "Trigger-rich description (Recommended),SKILLS FIRST canon line (Recommended),Session-start pointer (Recommended)".
- [operator-ruled] Verbatim: "no, do not overload rnd".
- [operator-ruled] Verbatim: "fix this oversight: 'First, there's no skill for reviewing a skill,'" (gz-skill-review, 12cbc49a3).
- [operator-ruled] Verbatim: "just make the skill" and "these are "meta" skills about using or reviewing other skills, so I am allowing this variance" (no ADR for gz-how or gz-skill-review; the ADR-0.40.0 booking was abandoned before any file was written).
- [operator-ruled] Verbatim: "approve the canon line" (c6de50d0f).
- [operator-ruled] Verbatim: "fix the gz gates line in AGENTS.md"; drop ruling "Drop C0 and C2 as proposed" (f1ab5ee56).
- [operator-ruled] Verbatim: "fix 1109" (2324263c9).
- [operator-ruled] Verbatim: "file a ghi for each of the remaining findings" (GHIs #1110 to #1118).
- [agent-chose] Fixed #1108 and the reachability ratchet as separate direct-fix commits ahead of gz-how, because gz-how shipping and its default-tier scope depended on both.
- [agent-chose] Did not file the --doc-surface-parity orphan: open GHI #1063 already records it with the same evidence.

## Immediate Next Steps

1. Ask the operator which of GHIs #1110 to #1118 to take up next. #1115 (brief-drift --apply refusal on a sealed brief) and #1111 (three docs pages) are the smallest.
2. For #1112, review the eight template skills with gz-skill-review, two per commit.
3. Ask whether OBPI work on ADR-0.35.0 resumes; only the operator initiates it.
4. Put to the operator the open questions carried from the predecessor handoff: whether the scaffolding-settings layer needs its own ADR, the competitor-radar cadence, and the presenter insight that gz complexity advise prints No crossings detected after an all-attested run.

## Pending Work / Open Loops

Open GHIs from this session: #1110 redundant no-skill waivers, #1111 stale skill docs pages, #1112 eight template skills, #1113 chores run pinned tools through uvx, #1114 shipped chores run scripts adopters lack (sibling of #1034, cross-linked), #1115 brief-drift --apply writes a sealed brief, #1116 brief-drift dry run hides amendments, #1117 validate manpage table unchecked, #1118 21 bare-id renames pending and nothing runs the detector.

The --doc-surface-parity orphan scope is tracked in #1063. Two improvement insights were recorded this session (do not overload gz-rnd; new-skill work routes to direct authoring under a GHI). The predecessor handoff's advised steps 2, 3 and 5 remain unruled.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads 0 0 after the sync.
- `uv run gz check` passes on a fully staged tree.
- `uv run gz validate --how-coverage` and `uv run gz validate --deprecated-verb-prescription` each exit 0.
- `gh issue view <N> --json state` for each of #1110 to #1118 reads OPEN, and for #1106 to #1109 reads CLOSED.
- `uv run gz obpi lock list` shows no locks held by this session.

## Evidence / Artifacts

- `.gzkit/skills/gz-how/SKILL.md` and `.gzkit/skills/gz-how/references/obpi-delivery.md` (the flow guide)
- `.gzkit/skills/gz-skill-review/SKILL.md`
- `src/gzkit/governance/trust_audits/how_coverage.py` and `tests/governance/test_how_coverage.py`
- `src/gzkit/sync_surfaces.py` and `src/gzkit/skills/__init__.py` (#1108)
- `src/gzkit/chores/control-surface-validator-reachability/check_reachability.py` and `data/validator_reachability_grandfather.json`
- `src/gzkit/commands/content/commit.py` (#1109)
- `AGENTS.md` lines 62 and 129, from `.gzkit/corpus/AGENTS.md.jsonl`
- `docs/governance/advisory-rules-audit.md` row 53c

## Settled Rulings

1108 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
