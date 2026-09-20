---
mode: CREATE
adr_id: ADR-0.39.0-gzkit-internal-config-surface
branch: main
timestamp: '2026-09-20T20:22:07Z'
agent: claude-code
session_id: a66b3803-2d38-4c9d-9f10-d4bf849a6fb9
continues_from: .gzkit/handoffs/20260920T160721Z-config-surface-and-magna-carta-edition.md
---

## Current State Summary

Two tracks completed. TRACK 1 (operator-directed): the ADR-0.39.0 interview was finished and the ADR scaffolded. Every interview field is authored, the ADR package exists under docs/design/adr/pre-release/, and one OBPI brief per checklist item is co-created and passes authored-readiness. Verified against Layer 2 at creation: `gz adr status` reported lifecycle Pending with no brief started and closeout BLOCKED; run it rather than trusting this sentence. NO OBPI WORK HAS STARTED and none may start without operator initiation. TRACK 2 (emergent): a sweep of Windows cross-platform defects, all found and fixed this session. Six GHIs closed with shipped commits, one filed and still open, one duplicate withdrawn. Both repositories are clean and synced: gzkit at ade953705, gz-skills at 6633ce3 with v0.4.0 released. `gz check` exits 0.

## Important Context

ORIENTATION, because the session ranged widely and the operator asked for the big picture. The governing campaign is docs/governance/build-to-1.0-campaign-2026-09-20.md, which declares four workflow fronts: handoff system, ghi triage, adr/obpi campaign, and new R&D. TOPMOST is ADR-0.35.0-canon-entry-corpus-landing, NOT the ADR authored this session. ADR-0.39.0 is higher-semver than three unlanded feature ADRs (0.35.0, 0.36.0, 0.37.0). Its AUTHORING was explicitly excepted from ascending ADR order by operator ruling on 2026-09-20; its COMPLETION was explicitly NOT excepted and stays gated behind those four. A successor must not read the existence of fresh briefs as license to work them. THE SESSION STARTED 582 COMMITS BEHIND. That gap explains why the project instruction files differ from any pre-sync copy: AGENTS.md changed across nine of those commits and .claude/rules/governance-core.md was folded into AGENTS.md by 5adb751ee. Nothing in this session edited either. THE WINDOWS DEFECT FAMILY IS THE SESSION THEME. Four separate defects, each invisible on Linux CI, each found by hand rather than by a gate: a CRLF test fixture, a line-endings audit blind to the hazard it names, a settings-backup vault that resolved INSIDE the repository it exists to survive, and a backup nothing ever read. The common shape is a guarantee declared in prose whose witness was never built or never wired.

## Decisions Made

- [operator-ruled] The gzkit-internal config surface lives at .gzkit/config/settings.json, not config/ at repository root (verbatim: "this is config for gzkit, it should live in .gzkit/config, adopters will develop their own approach"). This amended authored Decision item 2.
- [operator-ruled] One flat settings.json; no categorical subdirectories (verbatim: "one mega settings.json file is fine, subdirectories are not needed"). Recorded in the ADR as a deliberate departure from the second of the five airlineops principles adopted verbatim in Decision item 1.
- [operator-ruled] gz init scaffolding of opinionated adopter defaults is DOWNSTREAM work under a named successor ADR, not a checklist item here.
- [operator-ruled] The decomposition scorecard is scored 7 against a computed baseline of 3, with all four Matrix-of-Four overlays scored as violated. Ruled with the disclosure that the agent produced the split mapping AFTER the target was known and that 4 is the formula maximum. That provenance is recorded in the ADR body.
- [operator-ruled] The checklist is ordered core-first: items 1 to 4 close the class, items 5 to 7 are the interruptible tail.
- [operator-ruled] A key-naming discipline is a required checklist deliverable, because the key vocabulary is the one-way door while directory layout is reversible.
- [operator-ruled] Required 2am deliverables are malformed-surface behaviour and a read path reporting the source layer. The gitignore of the local override, and threshold messages naming their key, were noted but declined as deliverables.
- [operator-ruled] Both downstream ADRs are real and recorded: init-scaffolded adopter defaults, and whether GzkitConfig and .gzkit/config converge.
- [operator-ruled] commit-trailers enforcement is wired into the gz check scope rather than a post-commit warning.
- [agent-chose] The ADR slug is gzkit-internal-config-surface, following the gzkit-ontology precedent, because the internal-versus-adopter boundary is what the ADR is about.
- [agent-chose] gzkit does not import the settings-backup hook and the hook does not import gzkit. The hook is deliberately stdlib-only so a backup failure cannot cost a session; the two are held in agreement by a coherence test instead.
- [agent-chose] No fix arm for vault reconciliation. The hook records at the next session boundary, so a second writer would be a parallel system for no gain.

## Immediate Next Steps

1. Present this handoff and await an operator ruling before executing anything. Book it with `gz handoff decide`.
2. Do NOT start ADR-0.39.0 OBPI work. Completion is gated behind four unlanded feature ADRs and only the operator initiates OBPI work. If the operator does initiate, the head of the chain is OBPI-0.39.0-01-entry-point-and-key-grammar, run through the gz-obpi-pipeline skill with Stage 2 dispatched rather than inline.
3. Rule on GHI #1069, the only gzkit issue this session left open. The line-endings audit names the write_text hazard in its own error message and its scope cannot reach it, so the gate read green for all five instances of that family. The AST machinery to build the arm already exists in the same module.
4. Rule on gz-skills#1 [settled]. The portable catalog now declares a discovery floor across the board, so that issue body is partly stale and needs re-reading against the v0.4.0 release before any action.
5. If the operator wants campaign work rather than this session residue, the front to read is adr/obpi campaign and the item is ADR-0.35.0-canon-entry-corpus-landing, which remains TOPMOST.

## Pending Work / Open Loops

OPEN AND UNRULED. GHI #1069, the line-endings gate that cannot see its own named hazard. gz-skills#1 [settled], the discovery-contract issue, now partly discharged by the v0.4.0 release and needing a re-read rather than immediate action. UNREPAIRABLE RESIDUE. Commit 84ea8e435 touches src and tests and carries no Task trailer. It is published, so repairing it needs a force-push, which repository policy forbids. It stands as the second recorded instance behind the one GHI #1017 [settled] was filed on, and the gate that would now catch it is wired in. MEASURED BUT NOT ROUTED. GHI #1063 counts 51 validator scopes never invoked. This session closed one of them, commit_trailers, which had been rostered in uncalled_gate_grandfather.json as known-inert. Whether the other 50 are the same class or merely unrouted is unmeasured, and that measurement is the obvious next thread. A SECOND OPERATOR ASK, PARTLY DONE. Vault reconciliation reports four states through gz tidy, but nothing prunes or restores; restore is a manual copy named in the message text. NOT A DEFECT, A LIMIT. The gz-skills floor checker witnesses that a floor is DECLARED, never that the rung it names is genuinely universal. Every floor was authored this session and a future author could satisfy the checker with a template.

## Verification Checklist

Run `uv run gz check` and expect exit 0. Run `uv run gz adr status ADR-0.39.0-gzkit-internal-config-surface` and read the OBPI table as the authority; no count is transcribed here deliberately. Expect lifecycle Pending and every brief in state pending. A brief in any other state means OBPI work began without operator initiation and must be investigated before anything else proceeds. Run `uv run gz obpi validate --adr ADR-0.39.0-gzkit-internal-config-surface --authored` and expect every brief to PASS. Run `uv run gz validate --commit-trailers` and expect exit 0; it is now inside gz check, so a failure means the HEAD commit lacks a Task trailer. Run `uv run gz tidy --check` and expect no Settings vault warning, which confirms the backup vault is current and sits outside the repository. Confirm `git rev-list --left-right --count origin/main...HEAD` returns 0 0 in gzkit and in the gz-skills clone at C:/Users/Jeff/source/repos/agents/gz-skills. Confirm `gh issue list --state open` shows none of #1068, #1070, #1071, #1072, #1073 or #1017, and that #1069 is the only one this session left open.

## Evidence / Artifacts

docs/design/adr/pre-release/ADR-0.39.0-gzkit-internal-config-surface/ADR-0.39.0-gzkit-internal-config-surface.md
docs/design/adr/pre-release/ADR-0.39.0-gzkit-internal-config-surface/ADR-0.39.0-config-surface-interview.json
src/gzkit/settings_vault.py
tests/governance/test_settings_vault_awareness.py
tests/governance/test_settings_local_vault_outside_repo.py
tests/governance/test_commit_trailers_is_gated.py
scripts/settings_local_backup.py
src/gzkit/commands/validate_cmd.py
tests/cli/test_validate_registry_parity.py
data/check_scope_membership.json
docs/governance/config-derivation-census-2026-09-20.md
docs/governance/build-to-1.0-campaign-2026-09-20.md

## Settled Rulings

1000 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
