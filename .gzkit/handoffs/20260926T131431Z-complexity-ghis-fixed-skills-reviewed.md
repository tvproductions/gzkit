---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-26T13:14:31Z'
agent: claude-code
session_id: f4d5161a-dae1-43b4-a6ed-9209bccbf4b4
continues_from: .gzkit/handoffs/20260926T075059Z-attestor-handle-configured-skills-reviewed.md
---

## Current State Summary

This session resumed the attestor-handle handoff (booked with gz handoff decide), then fixed two encoding defects, reviewed four skills, filed four GHIs from those reviews and fixed all four. Everything is committed and pushed; HEAD is 07d13ee36 and origin/main is level. The only uncommitted change is one .gzkit/ledger.jsonl row written by the post-commit recorder after 07d13ee36.

Commits, oldest first: 151cb0f89 GzkitConfig.load/save read and write .gzkit.json as UTF-8, and the encoding audit (tests/governance/test_test_fixture_encoding.py) now scans src/gzkit and text-mode open(); 7913f67d5 tempfile-gap insight; f086619c8 the audit also flags text-mode tempfile opens and 30 test sites pass encoding='utf-8'; 6aadee271 review of gz-cli-audit 0.2.0 and gz-competitor-radar 1.1.0 (open-foundation-adr route removed); 0b6e2a22d review of gz-complexity-advisor and gz-complexity-guide, which surfaced four engine defects filed as GHIs #1102-#1105; 3fdab739f GHI #1104 hint and proof ranges span the diagnosed function; c9e1e68fa GHI #1105 the advisor timeout honours advisor_timeout_seconds, the bare install command installs, the hook runs pinned uv run xenon; 80ea34ef5 GHI #1102 both intrinsic-attestation paths suppress a diagnosis in gz complexity advise and the auto-chain hook; 07d13ee36 GHI #1103 an unmatched crossing is RefactorArchetype.UNCLASSIFIED, and attested REQ-0.0.29-02-06 was amended in place by operator ruling. All four GHIs are closed with evidence and ARB receipts. No OBPI work was initiated and no lock is held.

## Important Context

Workflow fronts source: docs/governance/build-to-1.0-campaign-2026-09-20.md § Workflow fronts. This session touched the ghi triage front (#1102-#1105 filed and fixed) and skill maintenance; it did not touch the adr/obpi or new R&D fronts. The complexity-advisor surfaces (ADR-0.0.29 and ADR-0.0.30, both Validated) are now coherent: gz complexity advise and the auto-chain hook share find_attestation in src/gzkit/complexity/advisor/intrinsic.py; the guide deliberately ignores attestation (ADR-0.0.30: hints precede attestation). RefactorArchetype has eleven values; the rule-table schema deliberately lacks unclassified. ADR-0.0.29 routes archetype amendments through ADR-pool.doctrine-amendment-protocol, which is unbuilt, so the operator ruling recorded on GHI #1103 is that amendment's witness. docs/governance/attested-req-subject-retirement.md now records Worked example 3, the first attested REQ that literally asserted a retired claim; it states one ruling, not a procedure. The auto-chain hook is still not installed here; uv run python -m gzkit.hooks.install_complexity_advisor now installs it. data/module_constant_grandfather.json is shrink-only and its stale-entry test fails when a rostered constant is removed without removing its entry. The post-commit recorder printed recorded 1 on 07d13ee36, the live witness GHI #1092 asked for. The verifier-pipe-gate hook refuses a verifier followed by another statement; capture to a file and read the exit status immediately.

## Decisions Made

- [operator-ruled] Verbatim: "fix the encoding defect directly" (151cb0f89).
- [operator-ruled] Verbatim: "fix the tempfile gap too" (f086619c8).
- [operator-ruled] Verbatim: "review gz-cli-audit and gz-competitor-radar" (6aadee271).
- [operator-ruled] Verbatim: "review gz-complexity-advisor and gz-complexity-guide" (0b6e2a22d).
- [operator-ruled] Verbatim: "file a ghi for each" (GHIs #1102, #1103, #1104, #1105).
- [operator-ruled] Verbatim: "fix 1104" (3fdab739f).
- [operator-ruled] Verbatim: "fix 1105" (c9e1e68fa).
- [operator-ruled] Verbatim: "fix 1102" (80ea34ef5).
- [operator-ruled] Verbatim: "fix 1103 with an explicit unclassified archetype" (07d13ee36).
- [operator-ruled] REQ-0.0.29-02-06 record reconciliation, verbatim: "Amend in place (Recommended)" (dated amendment note on the REQ line; @covers kept).
- [agent-chose] #1105's timeout precedence (explicit timeout wins, config supplies the default) was read from REQ-0.0.29-09-04's wording, not chosen.
- [agent-chose] #1102 reads the decorator from the parsed AST and honours only non-empty string-literal arguments, so no file is ever imported and an empty decorator is no escape hatch.
- [agent-chose] #1105's bare install command was made to install, rather than rewording REQ-0.0.29-05, because that attested requirement names the bare command.

## Immediate Next Steps

1. Ask the operator which work to take up next. In ascending ADR order the lowest open work is ADR-0.35.0, whose closeout is blocked on OBPIs 07, 08, 10, 11, 12 and 13. Only the operator initiates OBPI work.
2. Put to the operator whether the scaffolding-settings layer needs its own ADR, since ADR-0.39.0's intent excludes adopter scaffolding.
3. Put to the operator the competitor-radar cadence: run a scan now, schedule one, or leave it on demand; the only scan is 2026-05 and its six moves await the grill.
4. Before 2026-10-23, review gz-implement, gz-migrate-semver, gz-pythonic-pattern-detect, gz-state and gz-validate, and gz-obpi-brief-drift by 2026-10-24, or the pre-push Skill audit blocks every push.
5. Put the presenter discovery insight to the operator for selection: gz complexity advise prints No crossings detected after an all-attested run.

## Pending Work / Open Loops

OBPI-0.35.0-08 reports Runtime State IN PROGRESS with no lock held (gz obpi status, observed at this session's start); unexplained and untouched. The predecessor handoff's skill-expiry step named four skills; five more expire the same day, recorded in step 4. At resume this session booked gz handoff decide with --set-aside for the predecessor's step 1, which the operator had not declined; the record overstates the ruling and was disclosed, not corrected. Whether a ledger intrinsic attestation should lapse when the function changes is undecided (#1102 [settled]'s close). Open GHIs carried forward: #1091, #1028, #894, #611, #907 and #1063. Earlier carried loops remain: #1036 [settled]'s two untested paths, the dry-run sync-preflight limit, the live confirmations for #1095 [settled] and #1093 [settled], gz-tidy's rationalization rows, and OBPI-0.35.0-07's land calling enforce_retention (BI-10).

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD
git status --short
uv run gz obpi lock list
uv run gz obpi status OBPI-0.35.0-08-remember-post-append-advisory
uv run gz skill audit
uv run gz complexity guide src/gzkit/ --json
gh issue view 1102 --json state
gh issue view 1103 --json state

## Evidence / Artifacts

- `src/gzkit/config.py`
- `tests/governance/test_test_fixture_encoding.py`
- `src/gzkit/complexity/advisor/intrinsic.py`
- `src/gzkit/complexity/advisor/engine.py`
- `src/gzkit/complexity/advisor/diagnosis.py`
- `src/gzkit/complexity/advisor/timeout.py`
- `src/gzkit/hooks/install_complexity_advisor.py`
- `src/gzkit/commands/complexity_advise.py`
- `.gzkit/hooks/pre-commit-complexity-advisor`
- `features/intrinsic_complexity_attestation.feature`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-02-diagnosis-engine.md`
- `docs/governance/attested-req-subject-retirement.md`
- `docs/user/runbook.md`
- `.gzkit/skills/gz-cli-audit/SKILL.md`
- `.gzkit/skills/gz-competitor-radar/SKILL.md`
- `.gzkit/skills/gz-complexity-advisor/SKILL.md`
- `.gzkit/skills/gz-complexity-guide/SKILL.md`
- `artifacts/receipts/arb-step-unittest-a0c02c40463f45fb87a1d61fc7f90876.json`
- `artifacts/receipts/arb-step-behave-b2b8a3dda7134ca383530395abd0d430.json`
- Commits: 151cb0f89, 7913f67d5, f086619c8, 6aadee271, 0b6e2a22d, 3fdab739f, c9e1e68fa, 80ea34ef5, 07d13ee36

## Settled Rulings

1097 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
