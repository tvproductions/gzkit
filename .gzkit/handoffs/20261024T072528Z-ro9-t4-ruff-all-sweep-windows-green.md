---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-24T07:25:28Z'
agent: claude-code
session_id: d7350098-194b-4239-8f4b-c1634b253a0f
continues_from:
- .gzkit/handoffs/20261023T084205Z-ro9-t4-session-closed-ci-green.md
- .gzkit/handoffs/20261023T085743Z-session-exit-bookmark.md
- .gzkit/handoffs/20261023T090003Z-session-exit-bookmark.md
---

## Current State Summary

RO-9 tranche 4 (drydock, safe mode): Ruff `ALL` with preview now runs under the counted shrink-ratchet baseline `data/ruff_baseline.json`, and every act this session is pushed. CI is green on both legs for `2952a9d54` (run 40072601264). Local main matches origin; the tree is clean.

Acts landed, in order:
- `4d512fbf0`: the complexity-ceiling canary reviewed.
- `e4b46bcb2` and `8989a9dce`: Ruff ALL under the counted baseline (15,044 findings in 4,613 rows), with every lint consumer moved to `gz lint`.
- `d46575235`: `pythonic.md` 0.5.10 writes the import idiom to the 3.14 floor (deferred annotations, no PEP 563 import in new code, `lazy import` recorded as Python 3.15); scorecard row 23b is Promotable.
- `501b5a228` and `c1d8555e8`: act 2, Ruff's safe fixes across the tree. The config is written by rule name (RUF201), and the scorecard reachability check translates names through `ruff rule --all`.
- `c4907e810`: the pre-commit `ruff-check` hook runs `gz lint` and never fixes.
- `b0b50bd8e`: the Windows CI fix. Ruff does not run EXE001 on Windows, so no baseline row may hold EXE001 or EXE002; 32 scripts are now executable and the two IEEE evidence scripts carry a per-file exception.
- `61afa16a5`: the lint canary reviewed.
- `90eea0ad2` and `52a76d7d4`: control S2-080 declares its rewording, so the served stage 2 says `gz lint --fix`; each stage header names its reworded rows.
- `bd49a8838` and the S2-080 passage-log commit: rows for every act, each with its RED receipt.

The baseline now holds 14,417 findings. No canary awaits review.

## Important Context

- Safe mode is open under the MX hangar: every guard outside gate5_invariants is advisory, and orientation reports the debt aging. `gz mx exit` through gz-mx closes it once the tranche is done.
- Ruff's "safe" fixes are not always safe here. Four of them failed other gates, and `gz check --full` caught each:
  - G004 on structlog: structlog does not apply %-format arguments.
  - RET505 pushed a function past the cognitive ceiling.
  - FURB140 `starmap` over a lambda-keyed sort does not type under ty.
  - TC006 quoted casts left imports typing-only.
  Run the full gate after any Ruff fix sweep.
- `gz lint --ratchet` lowers `data/ruff_baseline.json` and never raises or adds a row. The cognitive baseline (`data/cognitive_complexity_baseline.json`) has no ratchet verb; its rows are lowered by hand with the operator's approval.
- The baseline must hold no per-platform rule. `load_baseline` refuses EXE001 and EXE002, and the ratchet deletes such a row.
- The pipeline stage files are rendered from `data/obpi_pipeline_control_inventory.json` and pinned by digest in `src/gzkit/pipeline_procedure.py`. Never hand-edit them: change the inventory (a declared `reworded` row), re-render, and repin.
- The `verifier-pipe-gate` hook reads the word `ruff` in a heredoc commit message as a verifier; write such a message to a file and commit with `-F <file>`.
- A pasted CI diagnosis that names the `NCSurface.md` rendition-lineage line is wrong: that line is the negative-control fixture's own `[advisory]`. Read the failing step's output from `gh run view --log`.
- `features/` is outside the gate's ty scope and carries 14 ty errors; the scope is the open ruling for handoff step 3.

## Decisions Made

- [operator-ruled] Review the complexity-ceiling canary now and track the unmutated cognitive leg as a GHI (verbatim: "A"; GHI #1266).
- [operator-ruled] Hold the Ruff ALL findings in a keyed shrink-ratchet baseline (verbatim: "b"), counted and run by gzkit ("Counted, gz-run (Rec.)"), in its own file ("Own file (Rec.)"), with RUF105 as a standing exception ("RUF105 exception (Rec.)").
- [operator-ruled] Move idiomatic Python to the 3.14 standard (verbatim: "I want to make sure that we move our idiomatic python TO the 3.14 standard").
- [operator-ruled] Witness the safe-fix sweep with the full unit tier and canary sweep passing, the baseline falling, and the RED verdict recorded as equivalent by construction (verbatim: "3 as recommended").
- [operator-ruled] Let Ruff apply its fixes, RUF201 included (verbatim: "let ruff be our guide and let ruff do the fixes").
- [operator-ruled] Lower the four cognitive rows to their measured scores, give the dated evidence scripts a per-file exception instead of a mode change, and make the pre-commit hook check-only (verbatim: "do all three"; the hook confirmed by "do 1").
- [operator-ruled] Git sync, then fix Windows CI (verbatim: "git sync then windows CI").
- [operator-ruled] Record the lint canary review and draft the S2-080 amendment (verbatim: "do 1 and 2"), then land S2-080 as a ruled correction under safe mode (verbatim: "A land it").
- [agent-chose] Fixed EXE001 with the executable bit, not by removing shebangs, because removing them exposes INP001, which Ruff waives for a script.
- [agent-chose] The ratchet deletes a per-platform row rather than the fence blocking it, since deleting is a lowering.
- [agent-chose] Excluded dated evidence from the fix sweep as records.

## Immediate Next Steps

1. Ask the operator to rule whether `features/` comes into ty's scope; it has 14 ty errors today. Then land `[tool.ty]` with the warn rules raised, as handoff step 3 of the prior chain advised.
2. Land TID251, including a banned-api entry for `__future__.annotations` with the existing sites held in the baseline and a control that plants one, which moves scorecard row 23b to Mechanical. Then land `ruff analyze graph` behind the import-boundary checks.
3. Read RO-9 tranche 4's done condition ("No lint or type row remains") against `data/astral_discipline_baseline.json`, and add the tranche's closing passage-log row when it holds.
4. Before tranche 6, present the plan for the 411 PEP 563 imports and the held PLC0415 sites, read file by file against 3.14 semantics.

## Pending Work / Open Loops

- The attestation that completes OBPI-0.35.0-20 must name S2-080 (Requirement 4 of OBPI-0.35.0-17 and -20); the row is a declared rewording landed under safe mode.
- GHI #1266: the complexity-ceiling canary's mutant covers the cyclomatic leg only.
- RO-9 tranche 4, still open: the site-by-site reads of the held S506, S608, S701, S603, S607 and S404 findings, and row 23's property-level control (a planted lazy import that `gz lint` must refuse).
- Tranche 6: remove `from __future__ import annotations` from the 411 files that carry it and read the held PLC0415 sites (172 in `src/gzkit`), file by file, since removing the import changes runtime annotation semantics.
- Mirror creation may not preserve the executable bit. A mirror newly written for an executable canonical script would surface as EXE001 locally, and `gz lint` would catch it.
- The MX hangar stays open until the tranche closes (`gz mx exit` through gz-mx).
- Supersedes the session-exit bookmarks 20261023T085743Z and 20261023T090003Z, which carried no live state.

## Verification Checklist

- `uv run gz lint`: passes, with 14,417 findings held.
- `uv run gz check`: passes. `uv run gz check --full` passed on the S2-080 tree.
- `gh run view 40072601264`: success on windows-latest and ubuntu-latest.
- `uv run gz validate --complexity-ceiling`: passes.
- `git rev-list --left-right --count HEAD...origin/main`: 0 0.
- `uv run -m unittest tests.test_ruff_baseline tests.test_lint_cli tests.governance.test_pipeline_procedure_render`: OK.

## Evidence / Artifacts

- `src/gzkit/ruff_baseline.py`: the baseline judge, `ruff_rule_codes`, the per-platform fence and the ratchet.
- `data/ruff_baseline.json`: the counted baseline.
- `data/cognitive_complexity_baseline.json`: four rows lowered.
- `src/gzkit/governance/trust_audits/release.py`: rule names translated to codes.
- `.pre-commit-config.yaml`: the check-only `ruff-check` hook.
- `data/obpi_pipeline_control_inventory.json`: S2-080 reworded.
- `src/gzkit/governance/pipeline_procedure_render.py` and `.gzkit/skills/gz-obpi-pipeline/references/stage-2-implement.md`: the renderer and the re-rendered stage 2.
- `.gzkit/rules/pythonic.md`: 0.5.10.
- `docs/governance/advisory-rules-audit.md`: row 23b.
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`: the passage-log rows with RED receipts.
- RED receipts: arb-red-commit-d46575235744-4df9a9ca7260456baba20bdb2ea4e17f, arb-red-commit-501b5a228c6b-7c97abd57bf14975b892b4b8542bb9c8, arb-red-commit-c4907e810497-1edda5b09c1044c9b712d44e5a8ecac0, arb-red-commit-b0b50bd8e662-c32f81370a3a4088b830e3eecb5bf545, arb-red-commit-90eea0ad21d7-d661f41a06d441f3a576db33a7c260b7.

## Settled Rulings

1676 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
