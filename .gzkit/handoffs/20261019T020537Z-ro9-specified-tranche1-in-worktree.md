---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-19T02:05:37Z'
agent: claude-code
session_id: 0f093cd5-657a-4ef0-afd7-cbbb192b698a
continues_from: .gzkit/handoffs/20261019T011550Z-ro2-tranche1-seam-landed.md
---

## Current State Summary

Since the last handoff (92815355f): RO-9 was specified and pushed (847cf8d0b, docs/governance/harbor-ro9-astral-toolchain.md; mandate item 7, exit condition 7, the hand-back renumbered to 8). RO-2 tranche 2 landed by its own session (7315311de, 49ee85922, 6f30514c5; CI 39185899740 green), and the tranche 3 session (local_8751db75) was told its precondition is met and is working in this checkout. RO-9 tranche 1 is mid-build and NOT landed: it lives in a detached worktree and as a patch, .gzkit/cache/ro9/tranche1-wip.patch (37 files, applies cleanly to 1eb765ceb). Built so far: the witness gz validate --astral-discipline (src/gzkit/governance/trust_audits/astral_discipline.py, 24 tests in tests/governance/test_astral_discipline.py, real-tree run 1.3 s), its registration on every check surface, catch and admit negative controls, the exception register data/astral_exceptions.json declared in data/config_registry.json; --python-version-pins retired everywhere (module, tests, parser, registry, step, QC binding, controls, grandfathers lowered); Python declared once at 3.14 (requires-python >=3.14, .python-version 3.14.8, classifier; Ruff target and ty python-version deleted; setup-python removed from 4 workflows; uv python install bare in release.yml; Read the Docs 3.14, registered); uv required-version ==0.13.1 with a regenerated uv.lock; setup-uv v10.3.0 pinned by SHA; the gz init scaffold's Ruff target removed; the gz-deps-upgrade skill rewritten to the one-declaration rule (1.4.0); the uv project-norms checklist written as docs/governance/harbor-ro9-uv-project-norms.md. Main itself is clean apart from shared ledger and insights writes.

## Important Context

Safe mode stays open as session e6800367 under docs/governance/harbor-pilotage-candidate-2026-10-15.md; its lease ends near 2026-10-19T16:50Z and its debt is past 40 h. Do not land RO-9 tranche 1 while another session is editing this checkout: it reformats 154 files and would collide with the RO-2 tranche sessions, and `gz git-sync` auto-adds every dirty file. Land it between tranches, or after RO-2 tranche 5. The global uv binary is still 0.12.23 because the RO-2 sessions need it; the worktree used uv 0.13.1 through `uvx --from uv==0.13.1 uv`. At the 3.14 target Ruff's formatter applies PEP 758 (`except A, B:` without parentheses) to 154 files, and Ruff reports 18 UP037; both are mechanical and must be re-run on fresh main at landing, not carried in the patch. Every current Ruff rule (ALL, preview, py314) reports 52,043 findings across 161 rules (.gzkit/cache/ro9/ruff-all-rules-py314.txt); PT009 22,528 and COM812 5,504 conflict with doctrine or the formatter and become curated exceptions in tranche 4. A tree with no data/astral_discipline_baseline.json (an adopter before tranche 7) has its violations announced, not failed; gzkit's own tree must carry the baseline. Measured on 3.14.8: the lock resolves, every runtime dependency imports, and every compiled dependency has 3.14 wheels for Windows, Linux and macOS. The new claims astral-discipline and astral-discipline-baselined need bound guard canaries reviewed by the operator before CI's canary test passes.

## Decisions Made

- [operator-ruled] Toolchain direction, verbatim: "I want strict https://docs.astral.sh/uv/concepts/projects/ compliance for gzkit and all of its adopters."; "I want tight compliance - even gzkit itself might need to change."; "this includes maximal use of astral tools themselves - MAX, EXTENSIVE, THOROUGH."
- [operator-ruled] Versions, verbatim: "using a new version mandates updating to new features of the version - max stdlib with select ad curated exceptions."; "i want to keep up with the idioms of new releases - newer statements replace the older rule."
- [operator-ruled] On the eleven restatements of the Python version, verbatim: "this is insane slop"; "this is proof positive that we need the astral project discipline".
- [operator-ruled] RO-9 rulings, verbatim: "1. 3.14"; "2. yes, MAXX astral... MAXX" (preview allowed); "3. yes, MAXX astral... MAXX" (uv_build); "4. A we are in dry dock" (route as RO-9).
- [operator-ruled] Currency and scope, verbatim: "also, keep all astral tools up to date"; "all ruff rules up to date (ty too)"; "even `gz init` should look carefully at `uv init`".
- [operator-ruled] Sequencing, verbatim: "Yes: once RO-2 tranche 2 is on main, start RO-9 tranche 1 here (witness, uv current, Python declared once at 3.14)."
- [agent-chose] Pinned the exact patch 3.14.8 in .python-version, keeping gzkit's patch-pin practice for reproducible CI.
- [agent-chose] Retired --python-version-pins inside tranche 1, since the witness's version-restated rule replaces it; two checks of one fact is the duplication RO-9 removes.
- [agent-chose] Registered only the curated exceptions the RO-9 spec names (with reasons); jinja2, jsonschema, pyyaml, rich and structlog stay baseline violations for tranche 6's stdlib re-read, and bandit, detect-secrets, pygount, vulture, xenon, radon and interrogate for removal in tranches 2 and 4.
- [agent-chose] Built tranche 1 in a detached, never-pushed worktree with uv 0.13.1 side by side, to avoid touching the global uv binary or sweeping another session's edits.

## Immediate Next Steps

1. Wait for the RO-2 tranche 3 session (local_8751db75) to land; tranches 4 and 5 (local_5806c6b6, local_595d5dcd) run after it, one at a time, on main.
2. Resume RO-9 tranche 1 on fresh main when no other session is editing: `git apply --binary .gzkit/cache/ro9/tranche1-wip.patch`; `uv self update` to 0.13.1; set ruff>=0.17.1 and ty>=0.0.89 in the dev group and `uv lock`; `uv run ruff format .` and `uv run ruff check --fix .` (PEP 758, UP037); add the --astral-discipline manpage section, synopsis and table row; `uv run gz agent sync control-surfaces` for the skill mirrors; seed data/astral_discipline_baseline.json with its waiver_ratchet_registry entry and identity-baseline identities.
3. Fold into the RO-9 spec: the three late rulings (keep Astral current, every Ruff and ty rule, gz init on uv init), the resolved uncertainties (3.14 wheels, PEP 758 reformat), the adopter advisory behaviour, the --python-version-pins retirement, and a link to harbor-ro9-uv-project-norms.md; append the passage-log row.
4. Run `uv run gz check --full` on 3.14, commit with `Task: TASK-ro9-version-once`, run `uv run gz arb red --commit HEAD` and drive any undriven hunk, bind the two astral-discipline canaries and kill them live, get the operator's review via `gz canary review`, push and read CI on both platforms.
5. Then propose RO-9 tranches 2 to 7 as sessions, one at a time; specify RO-3; put the RO-2/RO-3 compatibility path to the operator; decide the hangar's lease with the operator.

## Pending Work / Open Loops

RO-9 tranche 1 is unlanded (the patch above). RO-2 tranches 3 to 5 are open in their sessions. The Windows CI investigation (session local_32c92ea3) reported read-only: the Test step is 1.7x slower on Windows with 3.9x more subprocess and temp-tree work per test, and the Handoff validator spawns 449 git processes per run; no fix is authorized. Carried: correction_mining.DEFAULT_RECURRENCE_THRESHOLD duplicating the maxim-13 threshold under ADR-0.0.70's fence; commands/task.py's short-id resolution without project_root (RO-2 tranche 3 owns it); the first contract pin naming rewritten commit 640629757; gz mx and gz context have no tagged scenarios; the session orientation is over its 4000-byte budget; thirty chores are overdue; the handback amendment waits for the drydock's exit conditions. The Astral tool map left three docs unread past a point (the uv CLI reference after uv build, the last part of Ruff's rule list, ty's rules after useless-overload-body); read them before tranche 4.

## Verification Checklist

git log --oneline -6 (expect 1eb765ceb and 847cf8d0b on top); gh run list --limit 3; git apply --check --binary .gzkit/cache/ro9/tranche1-wip.patch exits 0 on main; uv run gz handoff rulings --search 'MAXX astral' returns the RO-9 rulings; uv run gz insights remember entries with scopes toolchain-alignment and drydock-ro9 exist in .gzkit/insights/agent-insights.jsonl.

## Evidence / Artifacts

- `docs/governance/harbor-ro9-astral-toolchain.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `.gzkit/cache/ro9/tranche1-wip.patch`
- `.gzkit/cache/ro9/ruff-all-rules-py314.txt`
- `docs/governance/harbor-ro2-identity-seam.md`

## Settled Rulings

1626 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
