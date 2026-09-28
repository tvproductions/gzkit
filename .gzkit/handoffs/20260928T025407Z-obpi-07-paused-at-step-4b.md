---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-28T02:54:07Z'
agent: claude-code
obpi_id: OBPI-0.35.0-07-content-land-orchestrator
session_id: 79c5618c
continues_from: .gzkit/handoffs/20260927T225403Z-windows-sync-recovered-ledger-and-gate-hang-filed.md
---

## Current State Summary

OBPI-0.35.0-07-content-land-orchestrator (ADR-0.35.0, Heavy) is implemented and paused mid Stage 4, Step 4b, at the operator's request ("write a handoff and git-sync, we'll continue the review later"). `gz content land <surface>` is built: preflight (lineage verification, OBPI-14 retention gate on every consumer, attestation resolution), journaled per-file publication with one idempotent `rendition_landed` event, hash-based `--status`, and non-destructive resume (including after a kill mid-staging). Stage 2 is READY: all ten proofs valid (25 of 25 mutations killed on assertion; REQ-09 SUPPORT pass), accepted by spec arb-step-specreview-7c33d579e6404c22981224557428c375 and quality arb-step-qualityreview-f4d2438d928f460491f31b9a1bb4453a, every mapped finding closed. Stage 3 receipts green (arb-ruff-4f4e80dbc54b43d1b09d556ad8b58179, arb-step-typecheck-4ab83c7ed25a431289ede565e3d62682, arb-step-unittest-92545fa88b7244189c1b3d02080b97a0, arb-step-mkdocs-87b2feb3938545c19f4ef3792429a58a, arb-step-behave-6cd45fd061784845ab93f0fab462ab0e) but they predate the final rollback-prose edit and must be re-run. Step 4a packet VERIFIED. Step 4b tier-1 Codex round 2 (arb-step-codexadversary-70151f5432974f658c362e2bfd5fe005) returned NOT-CORROBORATED with three findings (two concurrency counterexamples, one REQ-09 witness gap); its import was REFUSED because its replay records carried abridged test output. Same session also fixed GHI #1143 (gate hang: packaged timeout that kills the process tree) and a `gz arb step` child UTF-8 defect, committed together with the OBPI work as 6e2c7df90.

## Important Context

- The acceptance input digest covers src/, tests/, features/, data/, rules and schemas: ANY edit there stales every proof and review. Docs and the brief's history sections do not.
- The mutation prover matches raw bytes: write LF only (`newline="\n"` or bytes). Two implementers wrote CRLF this session and eight proofs went invalid until normalized.
- Implementer subagents hit their 25-turn limit almost every dispatch; resume them with SendMessage.
- NEVER let a subagent run `gz content land` with cwd inside this repo. An implementer did (failed `cd` chain): two real landings of AGENTS.md, one with fabricated attestation text. Repaired: renditions restored, both `rendition_landed` rows voided via `gz ledger correct` (cause agent-error).
- Codex tier-1 on this machine: the Windows sandbox needs `~\.codex\.sandbox-bin` owned by Jeff. It was owned by BUILTIN\Administrators (upstream openai/codex #36475/#45734/#46380); renamed to `.sandbox-bin.old`, Codex recreated it and ran. If the companion hangs at phase `starting` with no `codex` child, its shared runtime died: set aside `%TEMP%\codex-companion\<workspace-slug>\broker.json` and retry.
- Step 4b uses the plugin's `task --write --cwd <disposable checkout>` path (per the pipeline skill), not `/codex:adversarial-review` (read-only; its output does not survive import).
- `gz obpi adversary-workspace` prints `.venv\bin\python`; on Windows the interpreter is `.venv\Scripts\python.exe` (insight recorded). The disposable checkout from this session is `C:\Users\Jeff\AppData\Local\Temp\gz-adversary-OBPI-0.35.0-07-content-land-orchestrator-_pw5mo33`; rebuild it after the repair.
- Full-suite `gz test` intermittently deadlocked today (GHI #1143); it now fails with exit 124 after 900 s instead of hanging. The underlying deadlock was not reproduced in three later runs.

## Decisions Made

- [operator-ruled] Land passes the OBPI-14 retention gate with a repeatable `--retention-map` (verbatim option: "Repeatable map (Recommended)").
- [operator-ruled] Build the `rendition_landed` event with `ledger_row(model)`, not `ledger_events.py` (verbatim: "Avoid the surface (Recommended)").
- [operator-ruled] Add `src/gzkit/ontology/corpus.py` and `tests/test_schemas.py` to the allowlist (verbatim: "Add both (Recommended)").
- [operator-ruled] Ratify the brief's Threat Model (verbatim: "Ratify draft (Recommended)").
- [operator-ruled] Allowlist `tests/cli/test_attestor_default.py` and read-only `corpus_store.py` and `retention.py` (verbatim: "Add all three (Recommended)").
- [operator-ruled] Gitignore the landing lock, journal and staging sidecars (verbatim: "Ignore all three (Recommended)").
- [operator-ruled] Restore the accidentally landed renditions and void both ledger rows (verbatim: "Restore + void both (Recommended)").
- [operator-ruled] Run Step 4b tier 1 after installing the Codex plugin (verbatim: "Install plugin, tier 1 (Recommended)").
- [operator-ruled] Rollback is `git restore --source=<rev> --staged --worktree`; amend REQ-09 and Requirement 10 (verbatim: "Name restore, amend REQ (Recommended)").
- [operator-ruled] Fix the Codex sandbox directory rather than fall back to tier 2 (verbatim: "fix it").
- [agent-chose] Reviewed Tasks 2-4 in one combined Stage-2 round because every task edits the one landing module; disclosed in the Change Log.
- [agent-chose] Removed `_provenance_claim` from status as unreachable (the provenance hash already binds landing_id and fingerprint).
- [agent-chose] Committed the OBPI work and both gate fixes in one commit because the `ty` pre-commit hook type-checks the whole tree.

## Immediate Next Steps

1. Present this handoff to the operator and obtain a ruling before acting; the lock on OBPI-0.35.0-07-content-land-orchestrator is still held and the pipeline markers are in place.
2. Repair the two Step-4b concurrency counterexamples in one batch: in `_publish` (shared by land and resume), compare-and-swap at the replacement boundary (replace only if the target still hashes to old_sha256, skip if already new_sha256, otherwise stop with exit 2 and keep the journal); add red-first tests that edit a target during staging and after resume's checks; disclose the residual check-to-replace window. Fold in the recorded one-helper rollback-recipe cleanup only if it does not widen scope.
3. Resolve the REQ-09 witness gap: the post-commit recorder emits `artifact_edited` only for `is_governance_artifact` paths, so no event will ever cite `docs/user/manpages/content.md`; put the choice to the operator (amend the REQ witness to the SUPPORT channel's artifact-exists arm, or produce the event through a governed path).
4. Re-run all ten proofs, run a focused Stage-2 follow-up, re-run the Stage-3 ARB receipts, refresh and re-verify the Step-4a packet, rebuild the adversary workspace, and dispatch a focused tier-1 Step-4b round that requires COMPLETE unittest output (including the `FAILED (failures=N)` line) in every replay record.
5. On a corroborated round, present the Stage-4 packet for Gate 5 attestation, then Stage 5 (precomplete, completion, handoff, lock release, git-sync).

## Pending Work / Open Loops

- Step 4b round-2 findings not yet in the acceptance ledger (import refused): `adv-07-publication-overwrites-concurrent-edit` (REQ-02), `adv-07-resume-overwrites-concurrent-edit` (REQ-07), `adv-07-manpage-edit-witness-absent` (REQ-09). Recorded in the brief's Change Log.
- Round-limit accounting: Step-4b round 1 was an environment failure (sandbox), round 2 was substantive; the pipeline bounds Step 4b at three rounds total, so decide with the operator whether round 1 counts.
- GHI #1143: the timeout fix landed in 6e2c7df90; close the GHI through ghi-close citing that SHA.
- Insights recorded this session (defects): sensitivity parser misses multi-path bullets; ADR-0.39.0-01/-02 fail `--sensitivity` unseen; Ledger.append writes CRLF on Windows; commands.content import cycle; `adversary-workspace` interpreter path on Windows; missing `gz content land` wielding skill; three REQ-09-adjacent observations (seven hand-written rollback strings, untracked sidecars after restore, witness-by-existence).
- ADR-0.35.0's remaining OBPIs: read them from `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` and the parent ADR's § Remaining Delivery Plan, never from a transcribed list.

## Verification Checklist

- `uv run gz obpi lock list` shows OBPI-0.35.0-07-content-land-orchestrator held.
- `uv run gz obpi acceptance OBPI-0.35.0-07-content-land-orchestrator status --stage stage2 --json` reports ready (until any audited-path edit).
- `uv run gz obpi acceptance OBPI-0.35.0-07-content-land-orchestrator status --stage stage4 --json` lists only the missing adversarial approvals.
- `uv run -m unittest tests.content.test_landing tests.commands.test_content_land` exit 0.
- `git status --short .gzkit/renditions/` is empty (no stray landing of real canon).
- `uv run gz ledger corrections` lists both `rendition-landed-landing-20260927T2358...` rows as void.

## Evidence / Artifacts

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-07-content-land-orchestrator.md` (Change Log carries every round and ruling)
- `.claude/plans/content-land-orchestrator-OBPI-0.35.0-07.md`
- `.gzkit/evidence/OBPI-0.35.0-07-content-land-orchestrator.stage4a.md`
- `src/gzkit/content/landing.py`
- `src/gzkit/commands/content/land.py`
- `tests/content/test_landing.py`
- `tests/commands/test_content_land.py`
- `features/content_land.feature`
- `docs/user/manpages/content.md`
- `src/gzkit/quality_command_timeout.json`

## Settled Rulings

1158 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
