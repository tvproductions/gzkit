---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-26T07:50:59Z'
agent: claude-code
session_id: a7415691-3d6e-47eb-b95f-517f613ab40c
continues_from: .gzkit/handoffs/20260926T064148Z-skills-reviewed-sync-preflight-guarded.md
---

## Current State Summary

This part of the session followed the skills-reviewed-sync-preflight-guarded handoff. Four skills were reviewed and two GHIs were filed and fixed, all pushed. origin/main is level with HEAD 640581686. Skill reviews: gz-insights-remember 0.1.1 and gz-init 6.1.0 (8d2c865d6), which also corrected --force wording from 'wipe-and-recreate' to 're-copy from the wheel; deletes nothing'; and gz-adr-emit-receipt 1.1.0 and gz-check-config-paths 0.2.0 (8c8751eb9). The gz-adr-emit-receipt example would have failed closed on heavy lane: the receipt gate reads arb IDs only from attestation_text or scope prose. GHI #1101 (person-name attestor examples in 5 verbs' --help and 3 manpages) was fixed in 1bbd8d7b4: examples show g0, with a guard over every parser. GHI #1036 (configured attestor handle) was fixed in bb4d8d40e. .gzkit.json authorship.attestor_handle now feeds an omitted --attestor on 11 verbs, the 7 human-act verbs keep a typed attestor, gz init --attestor-handle records the handle, and gzkit's own .gzkit.json carries g0. Both GHIs are closed with evidence. The operator course-corrected on settings, recorded as an improvement insight. A GzkitConfig.load encoding defect is recorded as an insight (640581686). No OBPI work was initiated and no lock is held.

## Important Context

Workflow fronts source: docs/governance/build-to-1.0-campaign-2026-09-20.md § Workflow fronts. This part touched the ghi triage front (#1101 and #1036 filed or fixed and closed) and skill maintenance. It did not touch the adr/obpi or new R&D fronts. Settings are three layers, per the operator. gzkit-internal settings belong to ADR-0.39.0 (pending, 7 draft OBPIs; its intent excludes adopter scaffolding). Scaffolding settings are the defaults gzkit ships and gz init writes. Adopter settings are each project's own .gzkit.json. gzkit builds itself, so its repository holds its internal settings and an adopter instance of .gzkit.json, and gz init must never scaffold gzkit's own values: a test pins that a flagless, non-interactive init writes attestor_handle null. The attestor default lives in src/gzkit/cli/helpers/attestor_default.py, where a marker makes --attestor an omitted-sentinel that main() resolves after parse_args. A new verb that takes --attestor must be added to one of the two classes in tests/cli/test_attestor_default.py, or the table test fails. CLI help strings are capped at 80 characters (tests/test_help_text_completeness.py). The pre-push gate runs a tautological-test audit that refuses unit tests which read doc text. The verifier-pipe-gate hook refuses any shell line that chains a statement after ruff, unittest or xenon; run each verifier alone. The next skill-review expiries all fall after 2026-10-23: gz-cli-audit, gz-competitor-radar, gz-complexity-advisor and gz-complexity-guide (last_reviewed 2026-07-25).

## Decisions Made

- [operator-ruled] Verbatim: "review gz-insights-remember and gz-init" (8d2c865d6).
- [operator-ruled] Verbatim: "review gz-adr-emit-receipt and gz-check-config-paths" (8c8751eb9).
- [operator-ruled] Verbatim: "file a ghi for the jane doe examples" (GHI #1101).
- [operator-ruled] Verbatim: "fix 1101" (1bbd8d7b4).
- [operator-ruled] Course-correction, verbatim: "we need to put this in settings - both for here, for development, and downstream, for adopters".
- [operator-ruled] Settings location for the attestor handle, verbatim: "One .gzkit.json field (Recommended)".
- [operator-ruled] GHI #1101 timing, verbatim: "Commit it now (Recommended)".
- [operator-ruled] Settings layering, verbatim: "gzkit has a settings and adopters will too. we need to bear in mind that gzkit is building itself. so, we may beed scaffolding settings and adopter settings".
- [operator-ruled] Verbatim: "fix 1036" (bb4d8d40e).
- [operator-ruled] Attestor default scope, verbatim: "All but the 7 human-act (Recommended)".
- [agent-chose] #1101 used literal g0 in worked examples, following #1031's recorded ruling that g0 is the settled worked-example form.
- [agent-chose] #1036's default is resolved after parsing through a sentinel, so explicit values, including whitespace, are never replaced and the parser tree reads no file.
- [agent-chose] gz init prompts for the handle only when stdin and stdout are both a terminal, so scripted and captured inits never block.

## Immediate Next Steps

1. Ask the operator which work to take up next. In ascending ADR order the lowest open work is ADR-0.35.0, whose closeout was blocked on OBPIs 07, 08, 10, 11, 12 and 13 at this session's start. Only the operator initiates OBPI work.
2. Put to the operator whether the scaffolding-settings layer (the defaults gz init writes for adopters, beyond the attestor handle) needs its own ADR, since ADR-0.39.0's intent excludes adopter scaffolding and the operator named that layer at GHI #1036 [settled].
3. Put the GzkitConfig.load encoding insight (640581686) to the operator for selection as a GHI or direct fix.
4. Before 2026-10-23, review gz-cli-audit, gz-competitor-radar, gz-complexity-advisor and gz-complexity-guide, or the pre-push Skill audit blocks every push.
5. On the first commit that changes an ADR, OBPI, PRD or constitution doc, AGENTS.md or CLAUDE.md outside the Edit tool, confirm the post-commit.legacy recorder prints recorded N (GHI #1092 [settled]'s live witness).

## Pending Work / Open Loops

#1036 [settled]'s close names two paths with no test of their own: the seven content retry lines with a handle configured, which are covered only through attestor_hint, and the interactive gz init prompt. Dry runs of gz init and gz agent sync still skip the sync preflight (#1100 [settled]'s stated limit). The live confirmations from earlier handoffs are still outstanding: one importable reviewer envelope at the next Stage-2 or Step-4b round (GHI #1095 [settled]), and the Demo running in a copy at the next present-evidence run (GHI #1093 [settled]). Open GHIs carried forward: #1091, #1028, #894, #611 and #907. gz-tidy's generic rationalization and red-flag rows still await the operator's ruling on trimming. Earlier discovery insights still await selection: verify-packet replays in the live checkout, and pre-push reports concurrent-session writes as its own modification. OBPI-0.35.0-07's land must call enforce_retention (BI-10).

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
uv run gz skill audit
uv run -m unittest tests.cli.test_attestor_default tests.commands.test_init_attestor_handle tests.cli.test_attestor_examples
gh issue view 1036 --json state
gh issue view 1101 --json state

## Evidence / Artifacts

- `src/gzkit/attestor.py`
- `src/gzkit/cli/helpers/attestor_default.py`
- `src/gzkit/config.py`
- `src/gzkit/commands/init_cmd.py`
- `tests/cli/test_attestor_default.py`
- `tests/commands/test_init_attestor_handle.py`
- `tests/cli/test_attestor_examples.py`
- `.gzkit.json`
- `.gzkit/skills/gz-adr-emit-receipt/SKILL.md`
- `.gzkit/skills/gz-check-config-paths/SKILL.md`
- `.gzkit/skills/gz-insights-remember/SKILL.md`
- `.gzkit/skills/gz-init/SKILL.md`
- `artifacts/receipts/arb-step-unittest-6d1861cecbe94e0d903af18e229c5c74.json`
- `artifacts/receipts/arb-step-behave-53386bf77cf9482095d5fa166d46fa10.json`
- Commits: 8d2c865d6, 8c8751eb9 (skill reviews), 1bbd8d7b4 (GHI #1101), bb4d8d40e (GHI #1036), 640581686 (insight)

## Settled Rulings

1087 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
