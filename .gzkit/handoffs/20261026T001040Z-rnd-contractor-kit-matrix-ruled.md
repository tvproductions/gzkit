---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-26T00:10:40Z'
agent: claude-code
session_id: 7e48b285-767a-426b-88a0-6967a1e74607
continues_from:
- .gzkit/handoffs/20261025T220051Z-rnd-contractor-kit-deep-dive.md
- .gzkit/handoffs/20261025T221541Z-session-exit-bookmark.md
---

## Current State Summary

Resumed the contractor-kit R&D run (docs/rnd/contractor-kit.md) from the deep-dive handoff; the operator ruled 'proceed with 2, then 3' (booked with gz handoff decide). All four inventories had landed; four independent verifier subagents checked every quote (TUM 419, JFMM V 626, aviation 205, maritime 179): all verbatim and in section, 3 JFMM misquotes, 55 meaning-changing cuts (condition or scope dropped), 9 misstated readings; reports saved verbatim under docs/rnd/contractor-kit/sources/verify-inventory-*.md with host paths made relative. The agent read the gzkit side in full (requirements model, RO-5 spec, Part 0 statement, terms and candidate glossary, safe-mode doctrine, the contract's binding sections and punch list; the passage log in preview only, the superseded record not read) and built the vocabulary matrix docs/rnd/contractor-kit/vocabulary-matrix.md: 34 rows (positions, documents and records, states and acts), every cell quote checked by script (167 of 173) and by hand (6, page breaks and two-column glossary). Published as https://claude.ai/artifact/Eb1Lqig7xdaGy6vBQxHz2U (version 7, private). Question 24 was put again from the matrix and ruled, then all eight contested rows were ruled one at a time; committed at 5661474e3. The run's frontier now moves to the coordinator's authority. RO-5 tranche 1 remains paused with nothing written.

## Important Context

Safe mode is open under docs/governance/harbor-pilotage-candidate-2026-10-15.md and the mx-session lock is held (about 6.5 h of TTL left at writing). The R&D record is the system of record for the run: read it whole before acting; gz-rnd governs (one question at a time with a recommendation; every mapping cites both sides read in full; the hard stop: no row executed without the operator's go on that row). The matrix is a view and holds no authority; the crosswalk becomes canon only through the commissioned row-4 work. The page is rebuilt from the Markdown by a scratchpad generator that is not in the repo; if the page must be updated in a new session, regenerate it and re-check every quote. The PDFs (TUM, JFMM V) stay out of git; re-extract with pdftotext -layout to check a quote. The NAMP full text (COMNAVAIRFORINST 4790.2E Appendix A, Chapters 5 and 7) is still not placed. The operator's correction this session: an amended acceptance is not a bare one; count before raising gz-rnd's recommended-option flag (insight scope gz-rnd:recommended-option-flag).

## Decisions Made

- [operator-ruled] Resume the run with step 2 then step 3 of the deep-dive handoff (verbatim: "proceed with 2, then 3").
- [operator-ruled] A work package is the bundle of its formal work package (initial conditions, procedure as task cards, test and inspection, system restoration) and its objective quality evidence, for both kinds (verbatim: "okay, A. Looking at the matrix, that appears to be the strongest?").
- [operator-ruled] Every gzkit work package is a controlled work package from opening, not at close (verbatim: "yes to your correction").
- [operator-ruled] The change ladder is pen and ink, change order (the operator alone), attachment, supplement; revision stays the REQ's word (verbatim: "B avoids collision and fits").
- [operator-ruled] Two records against the package's own approved spec: the alteration accounted as a configuration change, and the departure from specification for work that cannot meet its spec; the kit's positions must know these details (verbatim: "okay, A is it - make sure the agents/personas/skills are well-versed in these details").
- [operator-ruled] Personas carry their position's expectations and obligations, not the whole matrix (verbatim: "no, the persona/agent doesn't need the whole matrix, but they need to be clear on their expectations and obligations.").
- [operator-ruled] One craftsman persona fills two positions, repair (repair activity side) and restoration (Ship's Force side), separated by the runtime refusing a session that applied a line item from clearing it (verbatim: "A").
- [operator-ruled] The inspector is the Quality Assurance Inspector (verbatim: "A").
- [operator-ruled] The human is the operator and always the commander; no maintenance title for the human (verbatim: "actually, everywhere else, I am the operator and I am assumed to be gov zero (the human). The human, in gzkit, is always the commander").
- [operator-ruled] The punch list becomes the list of discrepancies, graded blocks-return-to-service or due-by-event, with root cause only when blocking or recurring (verbatim: "B′").
- [agent-chose] Verify every matrix cell quote again against the sources rather than trusting the inventories, restoring dropped conditions in the cells.

## Immediate Next Steps

1. Resume the R&D run docs/rnd/contractor-kit.md through gz-rnd: append a decision entry with the operator's words, check the record against git, and recompute the frontier from the subject.
2. Put the coordinator's authority (held provisional since 'Provisionally, I accept A, but let's delve.'), including matrix row A8: who may request a stop from outside the work chain, as JFMM surveillance does (I-9 App. C para 2.d(3)).
3. Put the two subjects the operator opened, one question at a time: a modified pipeline process built from the ruled vocabulary (bounded by question 8, repair first then reuse unchanged, lessons crossing as GHIs), and a maintenance-oriented GHI system (AC 00-71 problem-report states, discrepancies, DFS).
4. Put the remaining frontier: the kit's RO number and place in the register, the vibe-coded audit chore's shape, and disposition rows 1, 5 and 6.
5. Restate the challenge, write docs/rnd/contractor-kit/review.md, and put sign-off: kill or fund.

## Pending Work / Open Loops

Commissioned in the record and not executed (each needs the operator's go on its row, diamond 2): the RO-5 specification amended for the package bundle, the change ladder, alteration and DFS, and every package a controlled work package; the contract's Punch list renamed the list of discrepancies, with the brief and the doctrine; the crosswalk as the single vocabulary home with a witness that persona and skill terms resolve to it; the craftsman persona, the two position procedures, same-session-clearance refusal and the I-13.2.c line-item legibility check; earlier commissions (the eleven pipeline defect repairs, the cwd-escape guard GHI, the persona-witness GHI, the division-of-labor and exit amendments, Part 0's sea trial, Movement E, RO-7's persona number, gz-rnd's both-sides rule). The predecessor's open loops stand. The NAMP text is still requested. RO-5 tranche 1 is paused.

## Verification Checklist

git log origin/main..HEAD is empty after the sync. uv run gz obpi lock list shows mx-session ACTIVE. grep -c '^## decision' docs/rnd/contractor-kit.md counts the run's decisions (it rose this session). The matrix's Rows-the-operator-rules-singly section shows all eight rows struck through. uv run gz handoff rulings --search 'list of discrepancies' returns this session's ruling.

## Evidence / Artifacts

`docs/rnd/contractor-kit.md` `docs/rnd/contractor-kit/vocabulary-matrix.md` `docs/rnd/contractor-kit/sources/verify-inventory-tum.md` `docs/rnd/contractor-kit/sources/verify-inventory-jfmm5.md` `docs/rnd/contractor-kit/sources/verify-inventory-aviation.md` `docs/rnd/contractor-kit/sources/verify-inventory-maritime.md` `docs/rnd/contractor-kit/sources/inventory-navy-tum.md` `docs/rnd/contractor-kit/sources/inventory-navy-jfmm-v5.md` `docs/rnd/contractor-kit/sources/inventory-aviation-civil.md` `docs/rnd/contractor-kit/sources/inventory-maritime.md` `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

1730 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
