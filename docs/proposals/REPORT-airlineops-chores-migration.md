# Report: AirlineOps Chores Migration to gzkit

Date: 2026-01-26
Author: Codex (draft)

## Scope

- Source list: `../airlineops/config/opsdev.chores.json` (24 chores)
- Supporting context: `../airlineops/docs/design/briefs/chores/README.md` and `../airlineops/src/opsdev/commands/chores_tools/**`
- gzkit context: current CLI, quality commands, and design corpus

## Findings

1) **gzkit has no chore registry or runner** today. There is no equivalent to `opsdev chores` or a chores config in gzkit.
2) **airlineops chore system is config-first** (JSON), lane-aware, and evidence/log driven. It assumes a runner that can plan, run, audit, and log each chore.
3) **There is drift between the config list and chore briefs** in AirlineOps. The config contains 24 chores, while the `docs/design/briefs/chores/` folder contains additional briefs not represented in the config.
4) **Several chores are domain-specific** to AirlineOps (warehouse, SQL hygiene, manpage system), while many are generic hygiene practices portable to gzkit.
5) **gzkit already exposes quality commands** (`lint`, `format`, `test`, `typecheck`, `check`) that could seed a chore runner but lacks lane/evidence/logging semantics.

## Recommendations (Priority Order)

1) **Establish a single source of truth** for chores in gzkit (registry + briefs). Avoid the AirlineOps drift by enforcing one canonical registry and auto-syncing any secondary views.
2) **Introduce a minimal gzkit chore system** that can list, plan, run, and audit chores using a config-first registry and per-chore logs. This should be the landing zone for portable chores.
3) **Port a first tranche of portable chores** once the gzkit chore system exists. Start with generic quality and hygiene chores; defer domain-specific ones.
4) **Defer or mark N/A for domain-specific chores** until gzkit has equivalent surfaces (SQL/warehouse, manpages, opsdev tooling).
5) **Create an explicit migration matrix** that is reviewed alongside each gzkit release until parity is reached.

## Migration Matrix (Draft)

Legend:
- **Portable**: Can land in gzkit once chore system exists.
- **Adapt**: Likely portable, but needs gzkit-specific tweaks or prerequisites.
- **Blocked**: Requires missing gzkit surface (SQL, manpages, ops tooling).
- **N/A**: AirlineOps-only domain.

| Chore (slug) | Lane | Classification | Notes / gzkit prerequisite |
| --- | --- | --- | --- |
| pep257-docstring-compliance | Lite | Portable | Map to gzkit docstring coverage + ruff pydocstyle if adopted. |
| docstring-and-dev-docs-enforcement | Lite | Portable | Align with gzkit docs structure and any docstring policy. |
| sql-hygiene-query-normalization | Heavy | Blocked | No SQL/warehouse layer in gzkit. |
| test-isolation-tempdbmixin-compliance | Lite | Adapt | Only relevant if gzkit adds DB tests; define temp DB policy first. |
| cross-platform-test-cleanup | Medium | Portable | Applies to gzkit tests and temp file handling. |
| test-quality-analysis | Lite | Adapt | Needs a gzkit-specific test inventory baseline. |
| exceptions-and-logging-rationalization | Lite | Portable | Applies to gzkit logging/CLI error patterns. |
| schema-and-config-drift-audit | Lite | Adapt | gzkit has JSON schemas; define drift checks. |
| repository-structure-normalization | Lite | Portable | Aligns with gzkit canonical layout rules. |
| complexity-reduction-xenon | Lite | Portable | Reuse xenon thresholds for gzkit code. |
| config-paths-remediation | Lite | Portable | Apply to `.gzkit.json` path usage and docs references. |
| coverage-40pct | Lite | Portable | Use gzkit test suite coverage baseline. |
| module-sloc-cap-radon | Lite | Portable | Apply SLOC cap for gzkit modules. |
| pythonic-refactoring | Lite | Portable | General hygiene chore for code quality. |
| warehouse-naming-drift-remediation | Lite | N/A | AirlineOps warehouse domain only. |
| warehouse-core-architecture | Lite | N/A | AirlineOps warehouse domain only. |
| cli-contract-governance | Heavy | Adapt | Use for gzkit CLI once command surface stabilizes. |
| orchestration-tools-opsdev-parity | Lite | Blocked | No opsdev tooling in gzkit yet. |
| validate-manpages | Lite | Blocked | gzkit does not ship manpages today. |
| test-manpage-examples | Heavy | Blocked | Depends on manpage system. |
| sync-manpage-docstrings | Lite | Blocked | Depends on manpage/docstring sync tooling. |
| skill-manifest-sync | Lite | Adapt | gzkit has skills; define manifest expectations. |
| insight-extract | Lite | Adapt | Depends on transcript/log sources; can use `.gzkit/transcripts`. |
| insight-report | Lite | Adapt | Same prerequisites as insight-extract. |

## Next Actions

- Approve the proposed ADR + OBPI for a gzkit chores system.
- Once approved, scaffold a gzkit chores registry and CLI (list/plan/run/audit).
- Add a first portable chore set and validate the logging flow.
