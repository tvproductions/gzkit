---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-22T09:42:37Z'
agent: claude-code
session_id: 5e8561bb-318e-49d4-9bbe-8a00887ec188
continues_from: .gzkit/handoffs/20261022T082525Z-ro3-tranches-2-to-4-landed-check-demotion-baseline-drain-prd.md
---

## Current State Summary

Resumed from the 08:25Z handoff on the operator's "do next steps" (booked with gz handoff decide, proceed). Worked the advised steps in order:

1. RO-3 closed on the operator's word, its specification carrying the after-figures (5 catalog files, 11 families, 0 outcomes/REQs/externals, 9 delivery event types, 1,340 events naming a REQ, 0 delivery events after the cutover); the requirements-catalog-forward-rule canary review booked (reviewed_by g0). Commit 4423ae5eb.
2. GHI #1259 fixed and closed: gz interview obpi renders through gz specify's builder, now `obpi_template_vars` in specify_cmd.py, answers overriding the inferred sections. Commits a991b05d7, 83302c4c6.
3. RO-9 tranche 3 landed: uv_build (wheel payload unchanged, 880 files); `wheel_shipped_files` predicts the wheel for --distribution and --wheel-path-literals; release.yml builds in `dist` (uv build --no-sources, smoke test of both distributions) and publishes in `pypi` (the only job with id-token, astral-sh/attest-action v0.0.6, uv publish, skipping a version PyPI already holds); `uv version <v> --no-sync` writes pyproject.toml and uv.lock with __init__.py and the README badge following. Commits c9be1203e, e1ae92299, 41eed90bb, 8af73091b, d81128baa. Full unit tier 12540 OK; gz check exit 0; pushed, origin/main level.

Stopped before RO-9 tranche 4 to ask the operator whether to specify it first; no answer yet.

## Important Context

- Safe mode is open (MX session 57346836, advisory debt over 120 h); every act is one commit with its Task trailer and a `gz arb red --commit` witness, and the passage log in docs/governance/harbor-pilotage-candidate-2026-10-15.md gains a row per tranche.
- RO-9 tranche 4 is large: Ruff `ALL` with preview reported 52,043 findings across 161 rules when measured at tranche 1; PT009 and COM812 already conflict with doctrine; xenon, radon and interrogate retire for Ruff, complexipy and Lizard (GHI #1183) with the C/C/C contract re-derived and changed verdicts reviewed. Per-rule exceptions and complexity verdicts are the operator's to rule.
- The new release.yml has not run yet; the first tag push after this is its first live test. The publish skip guard asks https://pypi.org/pypi/py-gzkit/<v>/json (200 skip, 404 publish, anything else fails), because uv publish refuses a rebuilt file PyPI holds where the retired action's skip-existing passed it.
- `wheel_shipped_files` refuses an anchored exclude (exit 2): on uv 0.13.1 an anchored wheel-exclude removed nothing. Excludes are matched unanchored at any depth, children included, as uv documents.
- `gz check` (per-change) does not run the full unit tier: this session's first full run found five failures the gate never selected. Run `uv run gz test` before recording a tranche.
- The verifier-pipe-gate hook reads verifier names inside commit-message heredocs; write messages to a file and commit with -F.

## Decisions Made

- [operator-ruled] Proceed on the handoff's steps (verbatim: "do next steps"), booked with gz handoff decide.
- [operator-ruled] RO-3 is closed (selection: "RO-3 closed (Rec.)").
- [operator-ruled] The requirements-catalog-forward-rule canary mutant is accepted (selection: "Approve (Rec.)").
- [operator-ruled] REQ-0.0.21-03-06, which names Hatchling-native include syntax, is amended in place (selection: "Amend in place (Rec.)").
- [operator-ruled] REQ-0.0.32-15-09, whose Given is the hatch include block, is amended in place (selection: "Amend in place (Rec.)").
- [operator-ruled] REQ-0.0.32-06-02, which names the hatch include block, is amended in place (selection: "Amend in place (Rec.)").
- [agent-chose] GHI #1259: the interview door shares gz specify's builder rather than supplying author prompts; it also validates the parent ADR item through `_validate_parent_adr`.
- [agent-chose] REQ-0.0.32-03-06, -09-05 and -01-06 record that an OBPI left pyproject.toml untouched; their tests were repaired at the surface without escalation, since the move leaves those statements true.
- [agent-chose] astral-sh/attest-action pinned to v0.0.6 by SHA (f589a42a); v0.0.7 was published the day before.
- [agent-chose] __version__ in __init__.py stays a literal written from uv's version, not read from importlib.metadata, because the PyInstaller binary ships no package metadata.
- [agent-chose] The astral-discipline witness drops full-line YAML comments only; inline # also opens SHA pin comments and appears in shell strings.

## Immediate Next Steps

1. Ask the operator whether to specify RO-9 tranche 4 (lint and type to the maximum, GHI #1183) before building it: measure Ruff ALL with preview on the current tree, draft the per-rule exception list and the complexity contract re-derivation, and bring them for rulings.
2. Then RO-9 tranches 4 to 7 from docs/governance/harbor-ro9-astral-toolchain.md, in order.
3. At the next release, watch the first live run of .github/workflows/release.yml (the dist and pypi jobs, the PyPI skip guard, the attestations) and record its run id.
4. When the operator chooses: GHI #1264 (the API reference; which modules count is the operator's call), GHI #1262 (debt reading), GHI #1263 (parked); renew the hangar lease or exit it when the orientation announces it, on the operator's word.

## Pending Work / Open Loops

- RO-9 tranches 4 to 7 open; RO-9 closes when data/astral_discipline_baseline.json is empty (11 rows remain).
- The MX hangar (session 57346836) carries advisory debt; its exit runs every guard at full strength and needs the operator.
- GHI #1120 (the interview door's PRD id canonicalization) is open in the same family as #1259 [settled] and was not touched.
- Two RO-9 known uncertainties remain unread: whether Read the Docs builds through uv with a locked group, and which of uv check, uv format and uv audit are preview on the pinned uv (tranche 4 and 5 read them).

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads 0 0.
- `uv run gz validate --distribution --wheel-path-literals --astral-discipline` exits 0.
- `uv run gz test` reports 12540 or more tests OK.
- `gh issue view 1259 --json state` reads CLOSED.
- `uv run gz obpi status` is not needed: no OBPI is in flight; `uv run gz obpi lock list` shows only the mx-session claim.

## Evidence / Artifacts

- `docs/governance/harbor-ro9-astral-toolchain.md` (status: tranche 3 landed; two uncertainties read)
- `docs/governance/harbor-ro3-requirements-store.md` (RO-3 closed, after-figures)
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (passage-log rows for RO-3 closed and RO-9 tranche 3)
- `src/gzkit/governance/trust_audits/distribution.py` (`wheel_shipped_files`, `unshipped_reason`)
- `src/gzkit/commands/version_sync.py` (`uv_set_project_version`)
- `src/gzkit/commands/interview_cmd.py`, `src/gzkit/commands/specify_cmd.py` (`obpi_template_vars`)
- `.github/workflows/release.yml`
- `tests/commands/test_interview_render.py`, `tests/governance/test_distribution_audit.py`, `tests/governance/test_release_pypi_dispatch.py`, `tests/test_version_sync.py`
- Red receipts: arb-red-commit-a991b05d75f6-ceb0c2b21ce943f789efb1491098c3cc, arb-red-commit-83302c4c6cec-e5386581935b4672a67efa8ce4a6c48f, arb-red-commit-c9be1203e5d2-f8a630d08bb34fe3a58324eb2b739a38, arb-red-commit-e1ae92299588-d03b9ef7a5b644039be057c914155640, arb-red-commit-41eed90bbeba-3cef46a415e74e5190f44236134eb132, arb-red-commit-8af73091bbe3-e92553e614024daca8a14acc6dfc0cee, arb-red-commit-d81128baa1a3-6b48c612e9444794b9934f1f1a0d8923

## Settled Rulings

1659 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
