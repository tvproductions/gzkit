---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-28T05:17:18Z'
agent: claude-code
continues_from:
- .gzkit/handoffs/20261028T010731Z-rnd-contractor-kit-at-signoff.md
- .gzkit/handoffs/20261028T010848Z-session-exit-bookmark.md
---

## Current State Summary

The ty-backed LSP route for Python symbol lookups was audited and repaired on the GHI triage front. The ty LSP works in Claude Code; the first call can fail with 'server is starting', and a retry works. Four GHIs were filed through ghi-author: #1285, #1286, #1287 and #1288. A third member was added to #1278 by comment. Fixes landed and pushed on main:
- 4f9b1d519: sync hook ownership reads exec-form args (#1285).
- 951c37c33: the prefer-LSP hook is delivered by the generator as prefer-lsp.py under uv run python (#1278).
- a23c1496c and ae4e8e8d8: the hook reads every search in a command line and routes only Python-shaped names; 11 tests (#1286).
- eb6033388: every pipeline role and the four .claude/agents definitions are granted LSP (#1287).
- ea16d805a: a fence asserts the hooks README documents every registered hook; it fixed the mx-awareness and ghi-triage omissions (#1278).
- 39b8268e1: stage 2 names the reviewers' LSP grant through inventory control S2-064 reworded and repinned (#1287).
#1285, #1286 and #1287 are closed fixed with cause-to-test tables and resolved arb-red receipts; post-close corrections are on #1285 and #1286. #1278 and #1288 stay open. The predecessor's step 3, pushing on the operator's go, is done. Its steps 1, 2 and 4 were not touched.

## Important Context

Safe mode is still open: one commit per act with a Task: trailer, lint and fast static checks on, gz check --full not run per act. The mx-session lock lease is expired, booked and never evicted; this session did not touch it.
- The hook now lives at .claude/hooks/prefer-lsp.py, rendered from src/gzkit/hooks/scripts/lsp.py. Never hand-edit the delivered file. The sync's ruff format turns the template's parenthesized except tuples back into the 3.14 form, which is expected.
- The stage files under .gzkit/skills/gz-obpi-pipeline/references are rendered from data/obpi_pipeline_control_inventory.json and pinned in src/gzkit/pipeline_procedure.py. Change one through a reworded control row, then render_stage, then repin, as S2-080 and S2-064 did. That path is owned by the live Draft briefs OBPI-0.35.0-17 and -20.
- The .claude/agents frontmatter is preserved across sync, not generated. tests/test_roles.py fences it to src/gzkit/roles.py.
- gz arb red counts the generated hook mirror as production (#1268), so commits touching the hook template read undriven for mirror hunks.
- In zsh, $RANDOM inside $(...) repeats, so probe loops must use distinct session ids.
- The hook's residue: snake_case filenames still look like symbols until the search is repeated, which is the designed escape.

## Decisions Made

- [operator-ruled] Fix every item of the LSP augmentation list (verbatim: "fix all").
- [operator-ruled] Push the unpushed commits, correct the stage-2 reviewer-grant line owned by OBPI-0.35.0-17/-20, and defer #1288 (verbatim: "1. yes; 2. fix; 3. defer").
- [agent-chose] Commented on #1278 instead of filing a duplicate, because its three-set invariant already covers a registered-but-ungenerated hook.
- [agent-chose] Dropped the gz-airlock and gz-ontology LSP suggestion: those skills read the governance graph, not Python symbols.
- [agent-chose] Delivered the hook through the generator under uv run python rather than parenthesizing excepts in a hand-wired file; ruff's py314 target would undo that, and generator delivery fixes the adopter gap too.
- [agent-chose] Granted LSP to all four roles, Planner included, since every role consumes code or codebase state.
- [agent-chose] Left ceremony-step-gate.py and control-surface-sync.py, the other two #1278 members, for their own read of history.

## Immediate Next Steps

1. The operator rules the contractor-kit sign-off, kill or fund, from docs/rnd/contractor-kit/review.md. This is the carried predecessor step 1; read the record's last four decision entries first.
2. On fund, the operator gives the row-level gos for row 2 and row 4. This is the carried predecessor step 2.
3. Optionally restore the AGENTS.md anti-vibing section order. This is the carried predecessor step 4 and is a second canon act.
4. When #1278 is pulled, read the history of ceremony-step-gate.py and control-surface-sync.py, wire or retire each, and build the three-set check its closure contract names.

## Pending Work / Open Loops

- GHI #1278 is open for ceremony-step-gate.py and control-surface-sync.py, and for the registered/generated/on-disk hook check it names. The README-vs-registered fence covers one pair only.
- GHI #1288 is open, deferred by operator ruling. Next action: the operator picks route (a) an MCP LSP bridge for Codex, (b) .github/lsp.json for Copilot, or (c) none, per harness. The Codex and Copilot rows are subagent leads; only the ty CLI and the Codex hook file were re-verified.
- GHI #1268 explains the undriven mirror hunks in the a23c1496c red run.
- Requirement 4: the attestation that completes OBPI-0.35.0-20 must name S2-064 as well as S2-080 (commit 39b8268e1).
- Safe-mode punch list: nothing this session broke. The gz check --full failures from the 2026-10-27 insight still stand.
- Session-exit bookmark 20261028T010848Z-session-exit-bookmark.md is folded here.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD should read 0 0 after the closing sync.
- gh issue view 1285, 1286 and 1287 should be CLOSED; 1278 and 1288 should be OPEN.
- uv run python -m unittest tests.hooks.test_prefer_lsp tests.test_hooks tests.test_roles tests.test_pipeline_procedure tests.governance.test_pipeline_procedure_render should pass.
- Send {"tool_name":"Bash","session_id":"verify-1","tool_input":{"command":"cd x && grep -rn AdvisorDiagnosis ."}} to uv run python .claude/hooks/prefer-lsp.py; it should print a deny decision.
- grep -n '^tools' .claude/agents/*.md should show LSP in four files.
- uv run gz agent sync control-surfaces should leave the tree unchanged.

## Evidence / Artifacts

- `src/gzkit/hooks/scripts/lsp.py`
- `.claude/hooks/prefer-lsp.py`
- `src/gzkit/hooks/claude.py`
- `tests/hooks/test_prefer_lsp.py`
- `tests/test_hooks.py`
- `src/gzkit/roles.py`
- `tests/test_roles.py`
- `.claude/agents/implementer.md`
- `data/obpi_pipeline_control_inventory.json`
- `src/gzkit/pipeline_procedure.py`
- `.gzkit/skills/gz-obpi-pipeline/references/stage-2-implement.md`
- `artifacts/receipts/arb-red-commit-4f9b1d5191cd-9a36a7de5fe141cd82d83a22f53d08dc.json`
- `artifacts/receipts/arb-red-commit-a23c1496c1c2-ceeed55bdb2f4142b3f7577311d6cd6f.json`
- `artifacts/receipts/arb-red-commit-eb60333880ee-fa7a63a5ce404b8e87b96932c822471c.json`
- `artifacts/receipts/arb-red-commit-ea16d805a8ec-0f1204c2d4424ce1a36632f44dd075bd.json`
- `artifacts/receipts/arb-red-commit-39b8268e18cd-1aa09419ce234e85ad64ccbf9e7a8675.json`
- Commits: 4f9b1d519, 951c37c33, a23c1496c, ae4e8e8d8, eb6033388, ea16d805a, 39b8268e1

## Settled Rulings

1772 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
