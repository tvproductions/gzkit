---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-24T11:00:59Z'
agent: claude-code
session_id: 46f0c689-58f0-472c-a74b-0478943f960a
continues_from: .gzkit/handoffs/20261024T093055Z-ro9-t4-ty-scope-pep563-banned-witnessed.md
---

## Current State Summary

RO-9 tranche 4 (drydock, safe mode) took the operator's option C for its done condition: the site-by-site reading the tranche promised, the subprocess sites, and the ty overrides, before the tranche closes. Landed and pushed (CI green on 86360ef01): f1e84660c the twelve named sites (F822 and S608 fixed, S701/S506/PLE1141/RUF027 reasoned noqa, a lazy-export test); b93edbddf S404 a standing exception; 04b3641e6 and 7b7ea83cd every spawn resolves its executable through gzkit.executables (absolute PATH entries only, never the current directory), held by the AST fence tests/policy/test_executable_resolution.py over the package, the rendered hooks and the canonical skill and chore scripts, with no S603 or S607 baseline row left; 45c622173 a partial behave stub retires the features/** ty override (660 diagnostics); a85b67ef0, e7d79d689, b7551ab05 and 2eec848d9 shrink the tests/** override from 1,602 hidden diagnostics to 498 and retire unknown-argument, not-subscriptable and possibly-missing-attribute from it. Committed, not yet pushed at writing: 5f5505810 the passage log for seven acts and the RO-9 reading note. 04b3641e6 broke CI on both platforms (a scorecard identity pin and a behave gh mock); 7b7ea83cd repaired it. The tranche is not closed: the tests/** override still ignores invalid-argument-type and unresolved-attribute.

## Important Context

Safe mode is open; every act is one commit with its Task: trailer and a gz arb red --commit witness, and the contract's passage log (docs/governance/harbor-pilotage-candidate-2026-10-15.md) carries before and after counts. shutil.which searches the current directory first on Windows unless NoDefaultCurrentDirectoryInExePath is set, which is why gzkit.executables walks absolute PATH entries and hands each to which as a directory-qualified name. Generated hooks and the ghi-triage skill script cannot import gzkit, so they carry gzkit.executables.standalone_source() verbatim, and the fence holds each copy to the package source. tests/commands/common.py now offers argv_by_tool_name (mocks compare the tool name, since argv[0] is resolved) and subcommand_parser (narrowed argparse walk). Measuring the tests override: a temporary pyproject edit lifting the tests/** block, restored by a trap; never leave it lifted. The pre-commit hook runs gz lint on staged files; plain gz check does not run behave, so a behave-only break shows first in CI (it did once this session). A red witness on a 100-file commit runs well past twenty minutes; it works in its own worktree, so the main tree may be pushed meanwhile.

## Decisions Made

- [operator-ruled] Close RO-9 tranche 4 only after the site-by-site reading, the subprocess sites and the ty overrides (verbatim: "c").
- [operator-ruled] Read the subprocess sites by rule: S404 a standing exception, S607 fixed through a resolver, S603 a reasoned noqa (selection: "Split by rule (Rec.)").
- [operator-ruled] Fix the ty overrides by root cause, one act per class, retiring the override rule by rule (selection: "Fix by root cause (Rec.)").
- [operator-ruled] Fix S607 in the package, the canonical skill scripts and the hook templates, and curate it for tests, features and scripts (selection: "Package fixed, tests curated (Rec.)").
- [operator-ruled] Sync, then keep working (verbatim: "git sync, then continue").
- [operator-ruled] Stop for a handoff that carries the drive-time discussion as work (verbatim: "handoff... include this discussion as something to work on in the handoff").
- [agent-chose] Built the AST fence after 04b3641e6's witness left 104 call-site hunks surviving, rather than recording the survivors as equivalent; its first run found six spawns S607 never saw.
- [agent-chose] Spliced the resolver into hook templates from the package's own source rather than a hand copy, so the two cannot drift.
- [agent-chose] Extended the sealed-evidence per-file exception to S603 and S607, following its C901, banned-api and EXE001 precedent.
- [agent-chose] Rewrote kwargs model constructions in tests as model_validate, and dropped `-> object` helper annotations rather than adding ignores.
- [agent-chose] Typed the complexity test spy as dict[str, Any] rather than add a TypedDict to tests/complexity/__init__.py, which would have grown its held RUF067 findings.

## Immediate Next Steps

1. Push 5f5505810 with gz git-sync, then confirm CI with gh run list.
2. Rerun `uv run gz arb red --commit 7b7ea83cd` if its verdict is not on record (this session's background run may have died with the session), and add its passage-log row between the 04b3641e6 and 45c622173 rows.
3. Ask the operator to route the drive-time discussion's first thread (tactical/operational/strategic orientation on handoff write and read, below): a GHI through ghi-author, or a direct patch to gz-session-handoff and gz handoff.
4. Continue the ty tail: with the tests/** block lifted, 498 diagnostics (invalid-argument-type and unresolved-attribute) across 132 files, the densest tests/cli/test_validate_solo_scope_refusal.py (40); retire each rule from the block when it reaches zero, then the tranche's closing passage-log row.
5. Before tranche 6, present the plan for the held PLC0415 sites read against the pythonic.md carve-outs; before any gz mx exit, read the contract's § Exit and the repair-order register.

## Pending Work / Open Loops

- The drive-time discussion (operator-pasted reconstruction, 2026-10-24, "a standalone, manually reconstructed transcript"; the operator's words: "include this discussion as something to work on"). Four threads, to be read in full from the operator, not re-derived:
  (1) Enhance the handoff skill with tactical, operational and strategic orientation. At handoff read (session start) the agent states tactical (what we are doing now and how we know it worked), operational (how it advances the work package, its dependencies and consequences) and strategic (why it matters, how it fits the architecture and the long arc), plus a brief course assessment, reasoned from the system of record (ledger, handoff, campaign) so it shows it consulted the record. At handoff write, or release candidacy, the same three levels assess what was achieved. The operator framed it as an improvement to the existing gz-session-handoff skill and gz handoff tool pairing, not a new ledger, memory layer or approval ceremony; inspect the existing mechanisms before prescribing. Suggested title: "Enhance handoff skill with tactical/operational/strategic orientation". The operator may file the GHI and may route it as a patch. Side checks the operator named: whether the session-start handoff trigger is wired beyond Claude, and that git sync accompanies a handoff.
  (2) One narrow handoff experiment: give a fresh agent a half-finished work package (one trusted, one messy) with the repository and official records only, no chat history, and compare the state that survives the handoff with the state that dies in someone's head; the aim is the minimum sufficient state that survives an agent transition, which then licenses simplifying rules.
  (3) The economics of intervention: which interdictions pay for themselves in first-pass acceptance or reduced rework, and which burn capacity; read recent work packages end to end, and ask whether constraints have been removed as often as added.
  (4) Reasoning effort as a conscious work-package property: higher effort for direction-setting, unexpected failures and adversarial review, lower for well-shaped execution (the operator reported a likely subscription overage from leaving a high reasoning setting on).
- The tests/** ty override: 498 diagnostics remain; the block in pyproject.toml records each retirement with its count.
- Scorecard row 45e stays Promotable until the executable-resolution scan is enrolled as an @enforces claim with a control.
- Stale gzkit-red-* worktree entries (prunable) are residue from witness runs killed before cleanup; `git worktree prune` clears them, and red_witness already removes its worktree in a finally.
- Inherited: GHI #1267 (hexagonal direction) and GHI #956; docs/examples/tutorial-rhea-bootstrap.md still shows the PEP 563 import in an adopter example; adopter projects get no behave stub until tranche 7's scaffold.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads 0 0 after the sync.
- `uv run gz check` passes; `uv run ty check .` passes.
- `uv run python -m unittest tests.policy.test_executable_resolution tests.test_executables` passes.
- `uv run ruff check --select S603,S607 --preview .` reports nothing but S404 (a standing exception the explicit select overrides).
- `uv run -m behave features/` passes (plain gz check does not run it).
- The passage log carries rows for f1e84660c, b93edbddf, 04b3641e6, 45c622173, a85b67ef0, e7d79d689, b7551ab05 and 2eec848d9; 7b7ea83cd's row is the one outstanding.

## Evidence / Artifacts

- `src/gzkit/executables.py`
- `tests/test_executables.py`
- `tests/policy/test_executable_resolution.py`
- `tests/cli/test_lazy_exports_declared.py`
- `tests/commands/common.py`
- `typings/behave-stubs/__init__.pyi`
- `pyproject.toml`
- `data/ruff_baseline.json`
- `data/advisory_scorecard_identities.json`
- `.gzkit/rules/cross-platform.md`
- `docs/governance/advisory-rules-audit.md`
- `docs/governance/rule-version-history.md`
- `docs/governance/harbor-ro9-astral-toolchain.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `.gzkit/skills/ghi-triage/scripts/triage.py`

## Settled Rulings

1688 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
