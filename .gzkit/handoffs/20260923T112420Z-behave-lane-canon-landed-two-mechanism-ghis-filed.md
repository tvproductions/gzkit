---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-23T11:24:20Z'
agent: g0
session_id: 50c10551-c5db-4777-ba56-743196d233bd
continues_from: .gzkit/handoffs/20260923T094701Z-three-citation-ghis-closed-touched-vs-discussed-filed.md
---

## Current State Summary

Five GHIs touched, one measurement executed, one canon change landed. GHI #1084 CLOSED by relabelling the git-sync anchor trailer to 'Governance anchors referenced:' (43d63da8d) -- the cheaper of the two routes the issue recorded, chosen because path-derivation would encode one reading of an unsettled question. Measurement M-F EXECUTED, the first program item an agent ran alone, and piece 03 authored in the IEEE register (6f36c4f4f). GHI #1085 FILED and open. The operator then ruled on behave lane scope, producing three invariant-tier gate-covenant corpus entries (45e82992b); landing them required repairing a blocking test under GHI #1086, CLOSED (b454f3ff2). GHI #1087 FILED and open. main is at 45e82992b, level with origin, tree clean, uv run gz check exit 0 with AGENTS.md knowingly over its char budget and warning rather than blocking.

## Important Context

WORKFLOW FRONTS (campaign docs/governance/build-to-1.0-campaign-2026-09-20.md, section Workflow fronts): ghi triage advanced -- two closes, three files, net +2 open; new R&D advanced via M-F, which is investigation rather than an R&D run and writes to docs/governance/ieee/ rather than docs/rnd/; handoff system and adr/obpi campaign untouched. ADR-0.35.0 remains campaign TOPMOST with closeout BLOCKED under GHI #930.

THE THREE FILINGS ARE ONE FAMILY and are worth reading together: each is a declared discipline with no mechanism. #1084 (closed) -- a trailer label claiming 'touched' on evidence that only witnesses mention. #1085 -- behave.ini promises a @wip block carries a tracking reference; nothing reads it, so brief_reconcile.feature's deferral outlived the two Completed OBPIs it names. #1087 -- a booked ruling records THAT it was made, never WHERE it binds, so its application is an unverifiable manual sweep. The family locus is the Close the doctrine-declared-without-mechanism family box in Movement C; four members are visible in a single 20-title skim, which is why the family is named rather than the siblings cross-linked.

M-F IS DELIBERATELY ONE-SIDED and must not be read as settling D-08. It measures line reach, and Astra's challenge is about assertions over shared lines, which coverage structurally cannot see. D-08 keeps MISSING EVIDENCE.

READ-PATH TRAP in the M-F evidence: coverage json reports 25366 executed statements where CoverageData.lines reports 40491 raw line records for the same run. Every ratio is identical. The script uses the reporting basis and is the authority; a reader re-deriving by the other path has not found a discrepancy.

TWO STANDING CAUTIONS carried unchanged: D-01 (F-006) and D-05 (F-021) are UNRESOLVED disagreements on load-bearing findings; and an OPEN finding row is settled under Q-14 but NOT confirmed.

## Decisions Made

- [operator-ruled] Proceed on the resumed handoff, relabelling GHI #1084's trailer first and then running M-F (verbatim: "relabel the trailer, then M-F - are we returning to the ieee phases soon?"). Booked via gz handoff decide.
- [operator-ruled] File the @wip finding as a GHI (verbatim: "file it"), which became #1085. The finding NARROWED during authoring: behave.ini excludes @wip deliberately and documents why, so the defect is not that the gate passes while skipping a feature but that the tracking-reference half of that contract is prose nothing reads.
- [operator-ruled] Accept the Gate 4 / Gate 5 correction and the lite lane reading (verbatim: "I accept the gate 4 and gate 5 correction" and "Yes to your correction on lite: [1,2]"). The operator's framing had Gate 4 as a general precursor to Gate 5, which inverts the intent because Gate 5 is universal.
- [operator-ruled] The lane distinction is whether the external contract changes, and most but not all OBPI work is heavy (verbatim: "The distinction is whether the external contract is changed by the OBPI").
- [operator-ruled] Write all three drafted corpus entries (verbatim: "write all three entries").
- [operator-ruled] Repair the blocking budget test rather than trim canon, raise the budget, or revert the entries (verbatim: "go with A"), chosen from a four-option picker. The alternatives declined were raising the budget value, compressing invariant canon, and retiring the three entries.
- [operator-ruled] File the budget-limit sweep as a GHI (verbatim: "file the budget-limit sweep as a GHI"), which became #1087. The finding INVERTED during authoring: the sweep came back clean, so the issue is the absence of a mechanism rather than the presence of more arms.
- [agent-chose] Relabelling over path-derivation for #1084, on the issue's own argument that the cheaper route be weighed first and because what 'touched' means is unsettled -- a commit implementing an OBPI's REQ touches that OBPI's subject while touching none of its files.
- [agent-chose] Kept the GHI #519 Codex silent-truncation assertion HARD while removing the per-file budget ceiling beside it, on the ground that a 32768 B delivery cap is a correctness invariant rather than a configured budget. Mutation-checked rather than asserted.
- [agent-chose] Left "most but not all OBPI work is heavy" OUT of the corpus entries, because the covenant already states kind and lane are independent and a frequency claim invites a reader to treat "most" as a threshold. Surfaced to the operator rather than decided silently.
- [agent-chose] Did NOT trim canon when the diet chore was invoked. Its own section 2(c) stops at a gap exceeding the compressible budget, and the required delta was 1569 chars against 105 B.

## Immediate Next Steps

Nothing is REQUIRED next. Everything below is available without entering Phase 4.
1. Rule on GHI #1087's shape before anything is built. The issue argues two cheaper alternatives should be weighed ahead of a rulings-to-sites registry -- a resolvable ruling-id citation convention, or accepting manual sweeps recorded as dated censuses -- and records that the answer may legitimately be none. Adding machinery is the failure mode piece 01 section 12 names for this repository.
2. Rule on GHI #1085's remedy. Two legitimate routes: delete the 35 @wip scenarios, since M-F shows they prove nothing not already @covers-ed, or author the steps, since the CLI verb they target now exists. Measuring redundancy is not an argument for deletion.
3. Escalate REQ-0.0.54-01-03, which literally asserts the AGENTS.md budget is 15000, CLAUDE.md 4000 and per-rule-file 16000 against live values of 20000, 15000 and 30000. An attested REQ asserting retired values is an operator act under section OBPI Acceptance Protocol, not an agent repair. Carried on GHI #1086 [settled] and unrouted.
4. Reconcile .gzkit/rules/tests.md section Two runners, which still reads "Both tiers must pass for gz check" against the corpus entries landed this session. This is the natural follow-on to the canon change and was named as such when the entries were drafted.
5. Run a further measurement item from M-A to M-G. Six outstanding after M-F. M-A feeds Phase 4 directly and M-E depends on it; M-B settles D-03; M-C bears on D-01; M-G settles D-04. M-D must NOT be started until its own method problem is settled.
6. Phase 4 requires EXPLICIT OPERATOR AUTHORISATION and the full triad when it opens. Nothing this session moved it.

## Pending Work / Open Loops

GHI #1085 and GHI #1087 are OPEN, eligible and unselected -- authored only, per the ghi-author invocation boundary.

RESIDUE RECORDED, NOT FIXED: fenced blocks are still not distinguished from prose in the commit-anchor scanner, deferred from GHI #1081 [settled] and not subsumed by the relabelling; path-derivation for the anchor trailer remains available if what 'touched' means is ever settled; a cited path:line that resolves to the WRONG lines is still unchecked.

REGISTER QUESTIONS the operator has not ruled on: whether a finding should be authored for D-08 now that M-F has run, and whether to lift PROVISIONAL from consequence-bands.md, which rests partly on the DISPUTED F-021.

A BUDGET CONDITION now stands deliberately: AGENTS.md is 21569 chars against a 20000 budget, warning and not blocking. That is what the 2026-08-17 stay asks for. The diet chore is the management valve and only the operator or the chore may trim; an ordinary session may not.

D-01 and D-05 remain UNRESOLVED standing conditions, not open tasks. ADR-0.35.0 closeout is BLOCKED under GHI #930. The version_sync kind guard is GHI-sized and unblocked, untouched this session.

## Verification Checklist

uv run gz check exits 0 on the current tree -- verified by reading REAL EXIT immediately after the verifier, never a notification's exit code, and re-run after every landing. ARB receipt arb-step-unittest-7632979ef346411db1d8da539685ced4 exit_status=0, 10737 tests OK with 4 skipped. uv run mkdocs build --strict exit 0 over the register changes.

Working tree clean and main level with origin at 45e82992b, verified with git ls-remote rather than a sync's exit status.

uv run gz validate --instructions-files-budget exits 0 and WARNS that AGENTS.md is 21569 chars over a 20000 budget. That warning is the correct state, not a defect: re-running it and finding silence would mean the stay had stopped measuring.

M-F figures are re-derivable rather than transcribed: uv run python docs/governance/ieee/03-gate4-gate2-duplication-evidence/measure.py for the structural census in seconds, --coverage for the line comparison in roughly seven minutes. The script carries no literals from today.

FINDINGS.md still holds 35 rows: 2 CONFIRMED, 15 QUALIFIED, 2 DISPUTED, 14 OPEN, 2 REJECTED -- unchanged by M-F, which authored no finding. Re-derive any figure rather than trusting one transcribed here.

## Evidence / Artifacts

Commits: 43d63da8d (GHI #1084 anchor trailer relabelled); 6f36c4f4f (M-F executed, piece 03); b454f3ff2 (GHI #1086 budget test repaired); 45e82992b (three gate-covenant corpus entries).

Issues: #1084 and #1086 CLOSED with evidence; #1085 and #1087 OPEN.

Register: `docs/governance/ieee/03-gate4-gate2-duplication-2026-09-23.md` and its re-runnable script `docs/governance/ieee/03-gate4-gate2-duplication-evidence/measure.py`; `docs/governance/ieee/README.md` and `docs/governance/ieee/DISAGREEMENTS.md` both amended for M-F.

Canon: `.gzkit/corpus/AGENTS.md.jsonl` carries the three gate-covenant entries; `.gzkit/renditions/AGENTS.md/root.md` is the attested rendition at fingerprint 8bcc41852e77 over 375 entries; `AGENTS.md` is its playback.

Chore: `.gzkit/chores/instructions-files-diet/proofs/CHORE-LOG.md` records the stop-and-ask finding, nothing trimmed.

Code: `src/gzkit/commands/sync.py` and `tests/commands/test_sync_cmds.py` for the relabelling; `tests/governance/test_agents_md_map_doctrine.py` for the budget repair.

ARB receipts live under artifacts/, which is gitignored -- F-022's durability finding, which is why they are resolved on disk before quoting rather than trusted.

## Settled Rulings

1035 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
