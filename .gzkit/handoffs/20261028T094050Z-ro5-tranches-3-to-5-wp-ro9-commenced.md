---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-28T09:40:50Z'
agent: claude-code
session_id: 2e2e493b-472b-4c61-addf-78ede287b7bf
continues_from: .gzkit/handoffs/20261028T073030Z-ro5-tranche-2-landed-tranche-3-next.md
---

## Current State Summary

RO-5 tranches 3 and 4 landed and tranche 5 is in flight. Tranche 3 (33ccaea12): gz wp new and attach label each added issue repair and comment the package id on GitHub between the store check and the write; gz wp resolve books work_package_issue_closed; ghi-close step 9a calls it. Tranche 4 (f3331166a): the catalog forward rule is fail-closed with OBPI/ADR-named events passing as frozen legacy; work_package_lane derives a package lane, shown by gz wp show and recorded on the closed event; the checklist-count step retired at gz specify, gz validate --decomposition and the ADR document check; the decomposition matrix rekeyed; lane removed from release_package.md. Tranche 5: the correction gz wp evidence (7f61ab1ae) records OQE; RO-9 flew as WP-01-astral-toolchain (a6840df77), created with the repair label and comments on #1183 and #1184, initiated, #1183 resolved, frozen and commenced. GHI #1183 was reopened by independent review, repaired in 5de0f9a5d, 7109e6120 and 989215394, confirmed by a third reviewer and closed again with evidence. RO-9 gained its list-of-discrepancies lines and a corrected status line (088fd76c3). Commits through 989215394 are pushed; a6840df77 is local.

## Important Context

Safe mode stays open under docs/governance/harbor-pilotage-candidate-2026-10-15.md; every act is one commit with its Task trailer, and the commit hook leaves one mx_contract_amended ledger line unstaged each time, picked up by gz git-sync. Shift turnover: no tag hung (the tag-out log is RO-12's); no finding awaits buy-back; one commenced package, WP-01-astral-toolchain (RO-9), held by this session and handed to the relieving session by name; the mx-session OBPI claim is held. The forward rule now refuses a post-cutover delivery event naming no REQ, outcome or work package unless it names an OBPI or ADR id. A guard canary is bound to names_req_or_outcome in catalog_forward.py: editing that function voids the operator's canary review, so new naming lives in sibling functions. The full guard canary sweep (40 killed) runs only under gz check --full. Subagent spec-reviewers stop at about 15 turns; scope them tightly and SendMessage to collect a report.

## Decisions Made

- [operator-ruled] Tranche 3 attach order (verbatim choice: "Check, GitHub, write (Recommended)").
- [operator-ruled] Tranche 3 repair label (verbatim choice: "Verb ensures it (Recommended)").
- [operator-ruled] Tranche 3 issue close record (verbatim choice: "New event + gz wp verb (Recommended)").
- [operator-ruled] Tranche 4 forward rule (verbatim choice: "Fail-closed, legacy exempt (Recommended)").
- [operator-ruled] Tranche 4 lane reader (verbatim choice: "Reader + show + close (Recommended)").
- [operator-ruled] Tranche 4 brief-lane validators (verbatim choice: "Leave them connected (Recommended)").
- [operator-ruled] Tranche 5 flight scope (verbatim choice: "Fly to commenced now (Recommended)").
- [operator-ruled] Tranche 5 OQE verb (verbatim choice: "gz wp evidence (Recommended)").
- [operator-ruled] WP RO-9 initiation words (verbatim: "do: tranche 5 (witness)").
- [operator-ruled] GHI #1183 after failed review (verbatim choice: "Reopen, repair, re-review (Recommended)").
- [operator-ruled] RO-9 system restoration (verbatim choice: "Add RO-9's lines (Recommended)").
- [agent-chose] Retired the checklist-count step at all three enforcing sites, not only the specify site the spec named, as one class.
- [agent-chose] Kept names_req_or_outcome byte-identical so its reviewed guard canary keeps its binding.

## Immediate Next Steps

1. Run gz git-sync to push a6840df77 and the hook's ledger line.
2. Ask the operator which work to pull next: RO-9 tranches 5 to 7 under WP-01-astral-toolchain (supply chain, the 3.14 idioms of GHI #1184, adopter scaffold), recording OQE with gz wp evidence as each lands.
3. Have the operator review the requirements-catalog-work-packages guard canary through gz canary review.
4. Repair the RO-12 pre-kit GHIs (1200, 1206, 1208, 1028, 1273, 1198, 1203, 1205, 1194, 1209, 1185 and the cwd-escape guard), each confirmed by a reviewer subagent before close.

## Pending Work / Open Loops

- WP-01-astral-toolchain: accept, gz wp resolve for GHI 1184 and the Gate 5 close (the operator's attestation) once RO-9 tranches 5 to 7 land; tranche 5 of RO-5 closes with it.
- RO-5's own list-of-discrepancies lines stay open for the restoration contractor: the brief-lane validators (restored), the checklist-count step (retired), the forward rule (reconnected), new work's briefs replaced by work packages.
- RO-9's six new retired and replaced lines stay open for the restoration contractor.
- The MX hangar's advisory debt keeps aging; close it through the gz-mx skill when the drydock work is done.

## Verification Checklist

- git log --oneline -12 shows a6840df77, 989215394, 7109e6120, 088fd76c3, 5de0f9a5d, 7f61ab1ae, f3331166a and 33ccaea12.
- uv run gz wp show WP-01-astral-toolchain reports commenced with #1183 closed.
- uv run gz validate --catalog passes.
- gh issue view 1183 --json state reports CLOSED; gh issue view 1184 --json labels includes repair.

## Evidence / Artifacts

- `docs/governance/harbor-ro5-work-packages.md` — tranches 3 and 4 landed, tranche 5 in flight.
- `data/catalog/work_packages.json` — WP-01-astral-toolchain.
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` — the § RO-5 and § RO-9 lines and the passage log.
- `docs/governance/GovZero/obpi-decomposition-matrix.md` — the rekeyed matrix.
- `src/gzkit/work_package_github.py` — the one gh adapter.
- `docs/user/manpages/wp-evidence.md` — the OQE verb.

## Settled Rulings

1798 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
