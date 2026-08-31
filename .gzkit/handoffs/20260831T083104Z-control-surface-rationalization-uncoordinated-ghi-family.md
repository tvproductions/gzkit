---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-31T08:31:04Z'
agent: claude-code
session_id: fccd788f-2764-4d8e-a98f-56f695420058
continues_from: .gzkit/handoffs/20260831T013037Z-clean-resume-point-rules-corpus-ownership-open.md
---

## Current State Summary

Tree is clean and synced: HEAD `97cbfede`, `git rev-list --left-right --count origin/main...HEAD` returns `0 0`, `git status --short` empty, `uv run gz obpi lock list` reports no active locks. No pipeline marker, no OBPI scope, no open TASK.

Three commits landed this session, all pushed:
- `e5f60db5` chore(handoffs): record the review session and correct a mis-stated blocker
- `de4efb66` chore(handoffs): land the stranded resume point and book its ruling
- `97cbfede` fix(rules): emit nested CLAUDE.md redirects for Claude/Codex parity (GHI #923)

The substantive delivery was `97cbfede`: 25 generated nested `CLAUDE.md` redirects carrying `@AGENTS.md`, closing a vendor-parity gap where every shared subtree rule reached Codex alone. `uv run gz check` exits 0 on that tree.

Three GHIs were filed: #922 (shape witness under-reads its declared surface family), #923 (the parity gap, now fixed and awaiting close), #924 (Copilot regenerates in adopter projects). None is closed.

THE FRAMING THAT MATTERS MORE THAN ANY SINGLE ITEM, operator verbatim 2026-08-31: much of the agent control surface rationalization/normalization/compression work "is still open and not cohesively planned. this is due to the limitations of long-running agent work. these are all GHIs to the original CMS/corpora/render ADR." Eleven open GHIs form this family. They were filed across many sessions, each locally well-evidenced, and no session has held all of them at once. That is the state to resume into, not a queue to burn down item by item.

## Important Context

THE ADR THIS FAMILY BELONGS TO. Read both; they are not the same artifact. `ADR-0.0.34-agent-control-surface-rendering-substrate` is the ORIGIN of the rendering substrate and is `Validated` 8/8, TERMINAL, so it can own no live work. `ADR-0.35.0-canon-entry-corpus-landing` is the LIVE landing: `Pending`, heavy, closeout BLOCKED. Canon already routed one half there, `.gzkit/handoffs/rulings.jsonl` line 604: "The corpus-ownership half of GHI #921 routes to ADR-0.35.0, extended by the operator." Read the operator's phrase "the original CMS/corpora/render ADR" against both before assuming which is meant.

THE ELEVEN OPEN GHIs IN THE FAMILY, measured 2026-08-31: #924, #923, #922, #921, #907, #878, #874, #873, #863, #836, #815. They divide roughly into corpus integrity (#878, #874, #873, #863), instruction-surface shape and delivery (#921, #922, #815, #836), vendor rendering (#923 fixed, #924 open), and authorship witness (#907). No document plans them as one body of work; that absence is the operator's stated concern.

WHAT `97cbfede` CHANGED BEYOND THE REDIRECTS. Adding one generated filename exposed that `AGENTS.md` was excluded by literal name in EIGHT independent scanners, each a one-member allowlist for a family: the rule loader, `rule_version_markers`, `unscoped_rules`, two test scanners, the handoff-corpus check, the distribution baseline step, and the pre-commit mirror-drift guard. All eight now read `gzkit.rules.NESTED_SURFACE_NAMES`, so a ninth generated surface cannot reopen this eight ways. Expect the same shape wherever a scanner enumerates a directory and excludes one filename.

VERIFIED MECHANISM FOR THE REDIRECT DESIGN, confirmed against the official Claude Code memory documentation rather than assumed. Root `CLAUDE.md` always loads, plus every directory above cwd. Nested `CLAUDE.md` load ON DEMAND, verbatim: "Instead of loading them at launch, they are included when Claude reads files in those subdirectories." A relative import resolves "relative to the file containing the import, not the working directory", so `@AGENTS.md` reaches the SIBLING. Maximum import depth is exactly FOUR hops, not "several" as an earlier turn said. Claude Code does NOT read nested `AGENTS.md`, verbatim: "Claude Code reads CLAUDE.md, not AGENTS.md. If your repository already uses AGENTS.md for other coding agents, create a CLAUDE.md that imports it." The design implements the documented recommendation. Caveat: a nested `CLAUDE.md` loads only if Claude opens a file in that subtree, so parity is real but lazy, which also bounds the context cost to the subtree in play.

`.github` IS MULTI-PURPOSE. Do not treat it as Copilot's tree. Four things there are not Copilot and are scoped OUT of #924: `.github/workflows` (ci, docs, release), `.github/ISSUE_TEMPLATE`, `.github/discovery-index.json` (vendor-neutral, cited by seven live OBPI Discovery Checklists), and `.github/AGENTS.md` (the Codex projection of `gh-cli.md`). Commit `65001830` states the first two untouched and the last two deliberately retained.

A LIVE COUPLING BETWEEN #923 AND #924. `_foreign_vendor_roots` in `src/gzkit/rules/__init__.py` derives the no-Claude-redirect set from declared vendor surface roots. `.github` gets no redirect today precisely BECAUSE it is Copilot's declared root. Removing the Copilot VendorConfig makes `.github` eligible for one. Rule that deliberately; never let it arrive as a side effect of the removal.

ROUTING CANON MIS-STATED THIS SESSION AND NOW CORRECTED. An earlier turn called #924 "OBPI-scale and yours to initiate". Both halves were wrong. `AGENTS.md` line 356 is verbatim: "A GHI-tracked defect repair routes to direct fix (fix(<scope>): <summary> (GHI #N), close citing the commit SHA) regardless of the 'OBPI ceremony required when ANY hold' criteria below; those criteria gate planned ADR work, not defect repair. Never spin up an ADR or OBPI merely to discharge a GHI." Diff size is one of the excluded criteria. Separately, an OBPI is defined by LINEAGE, not size: "There is no such thing as a 'headless' OBPI: every OBPI is ALWAYS attached to a parent ADR." Work with no parent ADR cannot be an OBPI at any scale, and the IRON LAW governs OBPI work rather than reaching a GHI.

INHERITED CAUTIONS THAT STILL BIND. `gz validate --transcribed-adr-counts` refuses a live ADR count transcribed into a handoff; cite `uv run gz adr status <ADR-ID>` instead. Any commit touching `src/**` or `tests/**` needs a `Task:` trailer, slug form for direct-fix work outside OBPI scope. A verifier piped into another process is refused by `.claude/hooks/verifier-pipe-gate.py`; use `set -o pipefail`, or capture to a file and echo the real exit.

## Decisions Made

- [operator-ruled] The control-surface rationalization work is tracked as GHIs against the original CMS/corpora/render ADR, not as fresh ADR work (verbatim: "these are all GHIs to the original CMS/corpora/render ADR"). Its incoherence is attributed to "the limitations of long-running agent work", not to any single GHI being wrong.
- [operator-ruled] Emit nested Claude surfaces for parity (verbatim: "nested AGENTS.md will only be seen by codex. So, we can get better claude performance by symlinking. I want to achieve operational parity in gzkit where either claude or codex can drive").
- [operator-ruled] The mechanism is the generated `@AGENTS.md` redirect, chosen over a symlink from a costed three-option comparison.
- [operator-ruled] Copilot support is ended (verbatim: "I also ended copilot support") and the cleanup is filed as a GHI (verbatim: "we need copilot cleanup as ghi - drop copilot support").
- [operator-ruled] Commit, then push, as separate authorizations (verbatim: "commit, push, then back to questions and GHI work").
- [operator-ruled] The claim about Claude versus Codex nested-instruction loading had to be verified rather than asserted (verbatim: "verify this please"), which corrected the import depth from "several" to four hops.
- [agent-chose] Filed #924 as residue-after-drop rather than as "drop Copilot", after finding commit `65001830` and the booked drop ruling; then re-titled and corrected it once `gz init` was actually run in a probe project.
- [agent-chose] Fixed the eight literal-name scanners by promoting one exported constant rather than adding a second literal in each, per fix-the-family.
- [agent-chose] Did not retarget #922 into #921 and did not start #924; both were left for the operator, since the session closed on the framing question rather than on execution.

## Immediate Next Steps

1. PLAN THE ELEVEN-GHI FAMILY AS ONE BODY OF WORK BEFORE TAKING ANY SINGLE ITEM. This is the operator's stated gap and the reason this handoff exists. The family is #924, #923, #922, #921, #907, #878, #874, #873, #863, #836, #815, and it belongs to the CMS/corpora/render ADR named in Important Context. Sequencing them IS the work; burning one down in isolation is what produced the incoherence.
2. Close #923. The parity fix landed in `97cbfede` and is pushed, but the GHI is still OPEN. Close it citing that SHA, per the direct-fix receipt pattern.
3. Rule on whether #922 retargets into #921. It was filed as a validator-coverage gap, then measurement showed the shape witness audits the adopter bootstrap template and gzkit's Layer-3 only, never gzkit's own Layer-1 corpus, which may make it ADR-0.35.0 work rather than a validator patch.
4. Take #924 when the family plan places it. It is GHI-routed direct repair and agent-workable; the `.github` redirect-eligibility coupling in Important Context must be ruled deliberately as part of it.
5. Hold the two long-standing operator-held items: the design spike, and whether a delivery-cap breach on must-survive canon stays advisory (#815).

## Pending Work / Open Loops

OPEN, and the operator's headline concern: the eleven-GHI control-surface family has no cohesive plan. Individually evidenced, collectively unsequenced.

OPEN, filed this session: #922 (shape witness under-reads its declared family; retarget decision pending) and #924 (`gz init` regenerates 107 files and 796,460 B of Copilot surface in every adopter project). #923 is FIXED AND PUSHED but still OPEN; it needs closing, not working.

OPEN, inherited: #921 (`.gzkit/rules/**` uncorpused; its corpus half is booked to ADR-0.35.0 and corpus onboarding is held for operator discussion), #815 (must-survive canon renders past the codex cap; root AGENTS.md measured 46,876 B against a 32,768 B cap this session), plus #907, #878, #874, #873, #863 and #836.

OPEN, unrouted spike residual, carried unchanged: nested projection shape doctrine. `agents-md-map-doctrine.md` declares paths for AGENTS.md, CLAUDE.md and `.claude/rules/*.md` while `agents_md_map_conformance.py` line 100 pins the rendered path to root AGENTS.md alone. Now partly subsumed by #922.

OPEN, operator-held: the design spike, whose premise no agent assertion can correct.

STRUCK, DO NOT RE-INVESTIGATE. The `surface_content_types` compose blocker was measured false on both halves: the cause is an absent corpus, and the single-entry map is attested design. The retained off-route codex rendition is a deliberately sealed record. `gz validate --brief-reconcile` exiting 0 on a Draft brief is correct by design.

PRE-EXISTING and untouched: `gz check` reports 696 unlinked specs as advisory drift.

## Verification Checklist

Run these before trusting any claim above.

`git rev-list --left-right --count origin/main...HEAD` expects `0 0`. Anything else means work landed after this document was written.

`git status --short` expects empty output.

`git log --oneline -3` expects 97cbfede, de4efb66, e5f60db5 at authoring time.

`uv run gz obpi lock list` expects no active locks.

`uv run gz check` expects exit 0. Pipe it only with `set -o pipefail`, or capture to a file and echo the real exit; the verifier-pipe-gate hook refuses a bare pipe.

`gh issue view 923 --json state` expects OPEN until step 2 closes it. The fix is already in 97cbfede.

`gh issue list --state open --limit 30` re-derives family membership rather than trusting the eleven ids listed above.

`uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` is where lifecycle and landed count are read, never from a figure transcribed in prose.

`uv run gz adr status ADR-0.0.34-agent-control-surface-rendering-substrate` confirms it is still terminal before anyone considers it a home for live work.

`uv run gz handoff rulings --search "corpus"` checks the settled corpus before re-arguing any ownership question.

## Evidence / Artifacts

Surfaces changed and committed this session:
- `src/gzkit/rules/__init__.py` — the nested surface writer, the shared write-set walk, and the NESTED_SURFACE_NAMES authority
- `src/gzkit/validators/rule_version_markers.py` and `src/gzkit/validators/unscoped_rules.py` — two of the eight scanners rewired
- `src/gzkit/hooks/guards.py` — the pre-commit mirror-drift guard, the eighth scanner
- `features/steps/distribution_invariant_steps.py` — the distribution baseline scanner
- `tests/test_rules.py` and `tests/governance/test_handoff_validation.py` — new redirect coverage plus two rewired scanners

Surfaces read for the Copilot finding, unchanged:
- `src/gzkit/commands/init_cmd.py` — the ungated Copilot setup call site
- `src/gzkit/hooks/copilot.py` — imported by init and sync, therefore not dead
- `src/gzkit/config.py` — the surviving Copilot VendorConfig and four path fields
- `data/distribution_baseline_manifest.json` — still ships the Copilot template entry

Handoff chain and Layer-2 records:
- `.gzkit/handoffs/20260831T013037Z-clean-resume-point-rules-corpus-ownership-open.md` — the resumed predecessor, landed in de4efb66
- `.gzkit/ledger.jsonl` — the handoff_resume_decided row booking this session's ruling
- `.gzkit/insights/agent-insights.jsonl` — one improvement record at scope agent-surface-rendering
- `.gzkit/handoffs/rulings.jsonl` — the append-only settled-ruling store

## Settled Rulings

625 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
