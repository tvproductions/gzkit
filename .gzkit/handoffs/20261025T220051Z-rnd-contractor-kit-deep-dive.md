---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-25T22:00:51Z'
agent: claude-code
session_id: 3b70eb44-a1f0-49f2-9044-cc8a4960a60e
continues_from: .gzkit/handoffs/20261025T152405Z-drydock-specified-contractor-brief.md
---

## Current State Summary

The operator resumed the drydock handoff and started the drydock contractor (RO-5 tranche 1), then stopped it before any code was written: the contractor brief was a prose prompt with no persona, skill or tools ("extreme vibe coding"). gz-rnd was changed so the agent starts an R&D run when the operator calls for it and offers one when the signals fit (commit 3c32d8f07). An R&D run, docs/rnd/contractor-kit.md, has defined the contractor kit through 23 ruled questions, grounded in 14 CFR 43/121, AC 120-16G, 29 CFR 1915.89, DFARS 252.217, and the operator-placed NAVSEA Tag-Out User's Manual Rev 08 and JFMM Vol V Rev D Chg 5. The frontier-model-card-currency chore was widened to review every model-level assignment (9649d0eb0). The record was committed at 7e048d9af and again in this sync. The operator then stopped the run again ("if you are not carefully reading this stuff, then we are flying in circles") and ordered a deep dive: four verbatim-inventory research tracks were launched and were still running when this handoff was written; question 24 is withdrawn and will be put again from the rebuilt matrix. RO-5 tranche 1 is paused with nothing written.

## Important Context

Safe mode is open (drydock contract docs/governance/harbor-pilotage-candidate-2026-10-15.md); the mx-session lock is held. The R&D record docs/rnd/contractor-kit.md is the system of record for the run: read it whole before acting; its rulings are verbatim with their questions. The gz-rnd skill governs the run: one question at a time with a recommendation; sources before decisions; and, new this session, every mapping question cites both sides, each read in full (insight scope gz-rnd:both-sides-read) - the operator caught the agent twice building mappings from partial reads. Four background research agents were writing docs/rnd/contractor-kit/sources/inventory-navy-tum.md, inventory-navy-jfmm-v5.md, inventory-aviation-civil.md and inventory-maritime.md; they may have landed after this handoff, uncommitted. Every quote in them must be verified against the source before use (model-selection.md: a subagent's claim is not evidence). Text extractions of the PDFs are in the previous session's scratchpad and are reproducible with pdftotext. The operator-placed PDFs (TUM, JFMM Vol V, the NAMP release letter) are kept out of git by docs/rnd/contractor-kit/sources/.gitignore; the NAMP full text (COMNAVAIRFORINST 4790.2E Appendix A, Chapters 5, 7) is still missing and was requested. Pipeline: no run since 2026-10-13; eleven open defects in the parts the kit reuses must be repaired before reuse.

## Decisions Made

- [operator-ruled] Specify the contractor kit before any contractor launches (verbatim: "A and we had better talk about it THOROUGHLY").
- [operator-ruled] The agent starts an R&D run when the operator calls for it and offers one when the signals fit (verbatim: "if I say we need it, then we need it and you start it"; "maybe the skill offers, do you want to start an rnd session for that?"; "OR, when I call for it").
- [operator-ruled] A vibe-coded and underbaked audit chore is commissioned (verbatim: "We had better get a "vibe coded" and underbaked bullshit chore soon").
- [operator-ruled] A contractor is a runtime-driven session that dispatches each act (verbatim: "c").
- [operator-ruled] Four distinct positions - coordinator, repairer, inspector, restorer - the repair performer never performs the restoration (verbatim: "repairer, inspector, restorer"; "that's why I don't want the same agent/persona for the two sides of the work").
- [operator-ruled] The repairer resists bias toward the present shape; the runtime holds documentation-first (verbatim: "C. both").
- [operator-ruled] One inspector judging against the job order and the record, routed around the coordinator through the runtime (verbatim: "A"; "A. yes, I did recommend an inspector").
- [operator-ruled] The coordinator is a new orchestration role; the runtime keeps the log; the operator attests; the coordinator's authority is tactical and operational, provisionally (verbatim: "Provisionally, I accept A, but let's delve.").
- [operator-ruled] Repair the pipeline first, then reuse its parts unchanged; every open defect in a reused part is repaired before reuse (verbatim: "A"; "A for sure.").
- [operator-ruled] The tasking spec is a job order changed only by the operator's change order (verbatim: "A").
- [operator-ruled] The operator and a working session build the bootstrap under the kit's discipline (verbatim: "we'll improvise and innovate until we have a pattern to build from. A.").
- [operator-ruled] A dock trial per job order; the sea trial gates exit in two approved forms, best a fresh project, better an increment of real work in the hangar (verbatim: "Make the two an OR"; "A").
- [operator-ruled] Persona budgets cap each file, not the total (verbatim: "caping each personal file directly is the best approach").
- [operator-ruled] Roles reuse the pipeline's model routing, kept current by the widened model-card chore (verbatim: "A is fine, but with those provisos"; "that chore must be udpated with this expanded scope").
- [operator-ruled] One tag-out per surface; parallel repairers only on disjoint surfaces (verbatim: "don't do multiples for the sake of it").
- [operator-ruled] Three records - tag-out log, maintenance record, punch list (verbatim: "A. and that matters because mx/drydock [elided] DOES require that lockout concept").
- [operator-ruled] A scoped vocabulary register: maintenance terms inside the hangar, Part 0 for the force (verbatim: "D, yes.").
- [operator-ruled] The isolation is the Navy's tag-out with Danger and Caution tags (verbatim: "A").
- [operator-ruled] Rebuild the vocabulary matrix from a deep read favoring formal naval and aviation terms before ruling another term (verbatim: "do a deep dive, and come up with a matrix that favors the more formal naval/aviation terms").
- [agent-chose] Keep the operator-placed PDFs out of git and commit their verbatim extracts; reversible on the operator's word.

## Immediate Next Steps

1. Continue the R&D run docs/rnd/contractor-kit.md through gz-rnd: check whether the four inventories landed under docs/rnd/contractor-kit/sources/; re-run any track that did not land.
2. Verify every quote in the inventories against its source, then read the gzkit side in full (docs/governance/ieee/requirements-model.md, docs/governance/harbor-ro5-work-packages.md, Part 0 in docs/rnd/renewing-vows/doctrine-merge.md, docs/governance/safe-mode-doctrine.md, the contract).
3. Build the vocabulary matrix favoring formal naval and aviation terms, every cell quoted and every liberty marked, and present it to the operator, ideally as a published page.
4. Put question 24 again from the matrix: the work package as formal work package plus controlled record, change orders, and what a work package bundles (RO-5 ruling 1, the retired work order, the Release Package).
5. Ask again for the NAMP full text (COMNAVAIRFORINST 4790.2E Appendix A, Chapters 5 and 7) if not yet placed.

## Pending Work / Open Loops

The R&D run is open: frontier remaining after the matrix - the coordinator's authority (provisional), the kit's RO number and place in the register, the audit chore's shape, disposition rows 1, 5, 6, then the review at docs/rnd/contractor-kit/review.md and sign-off. Commissioned and not yet executed: direct repair of the eleven pipeline defects (#1200, #1206, #1208, #1198, #1203, #1205, #1194, #1209, #1185, a cwd-escape guard GHI to file, #1028's boundary); a GHI on the persona witness; amendments to the contract (division of labor, cheaper sessions, exit conditions, the punch list split into three records), the doctrine (Seaworthy, Handback), Part 0's sea trial and the campaign's Movement E (each needs operator ratification); RO-7's persona exit number; gz-rnd's both-sides rule. RO-5 tranche 1 is paused. The predecessor's open loops still stand (GHI #1268 and #1269 [settled]'s rerun as RO-0 restoration lines, GHI #1252's flight, GHI #1188's chore, the T/O/S thread, the PLC0415 plan). Pre-existing advisories seen: nested AGENTS.md and personas over budget (RO-7), gz-tech-debt-review body oversize, one low Dependabot alert on main.

## Verification Checklist

git status shows only ledger rows and any late inventory files; git log origin/main..HEAD is empty. ls docs/rnd/contractor-kit/sources/ shows the four inventory files if the tracks landed. uv run gz obpi lock list shows mx-session ACTIVE. grep -c "^## decision" docs/rnd/contractor-kit.md counts the run's decisions. uv run gz handoff rulings --search "tag-out" returns this session's rulings.

## Evidence / Artifacts

`docs/rnd/contractor-kit.md` `docs/rnd/contractor-kit/sources/14cfr43.md` `docs/rnd/contractor-kit/sources/14cfr121-371.md` `docs/rnd/contractor-kit/sources/faa-rii-return-to-service.md` `docs/rnd/contractor-kit/sources/ship-repair.md` `docs/rnd/contractor-kit/sources/dfars-252-217-7003-changes.md` `docs/rnd/contractor-kit/sources/pipeline-regressions-2026-10-25.md` `docs/rnd/contractor-kit/sources/navy-tum-rev08.md` `docs/rnd/contractor-kit/sources/navy-jfmm-vol5-glossary.md` `.gzkit/skills/gz-rnd/SKILL.md` `docs/governance/rnd-discipline.md` `.gzkit/chores/frontier-model-card-currency/CHORE.md`

## Settled Rulings

1720 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
