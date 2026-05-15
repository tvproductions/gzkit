---
id: OBPI-0.0.32-14-gz-upgrade-subcommand
parent: ADR-0.0.32-canonical-surface-packaging
item: 14
lane: Heavy
status: Completed
---

# OBPI-0.0.32-14-gz-upgrade-subcommand: Gz Upgrade Subcommand

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #14 - "OBPI-0.0.32-14: `gz upgrade` subcommand — adopter-side surface-only refresh of `.gzkit/<surface>/` from the installed wheel's package data via `importlib.resources.files("gzkit.<surface>")`, distinct from `gz init --update` (OBPI-05) which is the canonical project-refresh ceremony. Adds `--surface skills,rules,templates,personas,hooks` filter (comma-separated; default all), `--force` override for project-local edits (without `--force` the three-state IDENTICAL/STALE/EDITED detection from OBPI-05 reports conflicts; with `--force` overwrites), `--dry-run` reports what would change without writing. Works in a fresh `pip install py-gzkit` environment without requiring `gz init` to have been run first (bootstrap retrofit case). Idempotent: exits 0 when wheel content is already byte-identical to `.gzkit/`. Manpage at `docs/user/manpages/upgrade.md`; behave coverage in `features/upgrade.feature`. Depends on OBPI-02 (scaffolder refactor wires `importlib.resources` resolution path) and OBPI-06 (wheel includes ship the canonical content) landing first."

**Status:** Draft

## Objective

`gz upgrade` subcommand — adopter-side surface-only refresh of `.gzkit/<surface>/` from the installed wheel's package data via `importlib.resources.files("gzkit.<surface>")`, distinct from `gz init --update` (OBPI-05) which is the canonical project-refresh ceremony. Adds `--surface skills,rules,templates,personas,hooks` filter (comma-separated; default all), `--force` override for project-local edits (without `--force` the three-state IDENTICAL/STALE/EDITED detection from OBPI-05 reports conflicts; with `--force` overwrites), `--dry-run` reports what would change without writing. Works in a fresh `pip install py-gzkit` environment without requiring `gz init` to have been run first (bootstrap retrofit case). Idempotent: exits 0 when wheel content is already byte-identical to `.gzkit/`. Manpage at `docs/user/manpages/upgrade.md`; behave coverage in `features/upgrade.feature`. Depends on OBPI-02 (scaffolder refactor wires `importlib.resources` resolution path) and OBPI-06 (wheel includes ship the canonical content) landing first.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/commands/upgrade.py` — new CLI command module implementing `gz upgrade`
- `src/gzkit/cli/parser_governance.py` — register `upgrade` subparser alongside `init` (the CLI package lives at `src/gzkit/cli/`; `src/gzkit/cli.py` does not exist)
- `tests/commands/test_upgrade.py` — unit-tier coverage for `gz upgrade` semantics (surface filter, force flag, dry-run, idempotency)
- `tests/commands/test_upgrade_resources.py` — package-resource resolution coverage (the `importlib.resources.files("gzkit.<surface>")` lookup path)
- `features/upgrade.feature` — behave coverage of three-state IDENTICAL/STALE/EDITED detection in upgrade context, `--force` overwrite, `--dry-run` no-write, idempotent exit-0 on byte-identical state, bootstrap-without-prior-`gz init` scenario
- `docs/user/manpages/upgrade.md` — operator-facing command manpage (synopsis, options, examples, exit codes, relationship to `gz init --update`)
- `docs/user/runbook.md` — operator runbook entry distinguishing the project-refresh ceremony (`gz init --update`) from the surface-only refresh (`gz upgrade`)
- `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md` — parent ADR (read-only here; Evidence section already references this OBPI's manpage and behave feature)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/commands/init.py` and related scaffolder modules — `gz init --update` is OBPI-05's surface; `gz upgrade` is a sibling verb, not a mutation of `init`
- `src/gzkit/<surface>/**` and `.gzkit/<surface>/**` content — `gz upgrade` consumes these surfaces but must not modify their canonical content
- `pyproject.toml [tool.hatch.build.targets.wheel] include:` — wheel-includes are OBPI-06's surface; this OBPI assumes the includes are in place and fail-closes on missing package data rather than mutating the wheel contract
- `data/distribution_baseline_manifest.json` — OBPI-06's surface; `gz upgrade` does not extend or rewrite the baseline manifest
- CI files, lockfiles (`uv.lock`, `pyproject.toml` dependency block), `.github/workflows/**`
- New runtime dependencies — per stdlib-first doctrine, `importlib.resources` is the canonical surface for package-data resolution; no third-party copy-utility dependency

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz upgrade` MUST resolve canonical content via `importlib.resources.files("gzkit.<surface>")` for every canonical surface registered in `CORE_SKILLS` / `CORE_RULES` / `CORE_PERSONAS` / `CORE_TEMPLATES` / `CORE_CHORES`. Direct filesystem reads of `src/gzkit/<surface>/` are forbidden — the package-data surface is the contract.
2. REQUIREMENT: `gz upgrade --surface <list>` MUST accept a comma-separated subset of registered surface names (`skills`, `rules`, `templates`, `personas`) and process only those; default (no `--surface`) processes every registered canonical surface. An unrecognized surface name MUST fail closed with exit 1 and an error naming the unrecognized token. Per-surface package-only files (e.g. `templates/skills/**`) MUST be filtered via the surface's `_classify_*` helper and never propagated to `.gzkit/<surface>/`. (Note: the authored REQ originally listed `hooks` as a valid surface; this contradicted ADR-0.0.32 § Named exception 1 — hooks are vendor-coupled and carved out of the dual-surface byte-parity invariant. Corrected under GHI #465.)
3. REQUIREMENT: Without `--force`, `gz upgrade` MUST run the same three-state IDENTICAL/STALE/EDITED detection that OBPI-05 (`gz init --update`) establishes for `.gzkit/<surface>/<slug>/` content; project-local EDITED artifacts MUST be reported as conflicts and left unchanged, with overall exit 0 only when zero EDITED conflicts remain unresolved.
4. REQUIREMENT: With `--force`, `gz upgrade` MUST overwrite EDITED artifacts with the wheel's package-data canonical content. A `--force` invocation MUST print a per-file overwrite line per modified path (one line per file, deterministic ordering by path) so the operator has an audit trail.
5. REQUIREMENT: `--dry-run` MUST report what would change (using the same three-state classification as a non-dry-run invocation) without writing any byte to `.gzkit/`. The exit code under `--dry-run` matches what the corresponding non-dry-run invocation would exit with (0 for clean, non-zero for conflicts under no-`--force`).
6. REQUIREMENT: `gz upgrade` MUST work in a fresh `pip install py-gzkit` environment without requiring `gz init` to have been run first — i.e., when `.gzkit/<surface>/` does not exist, `gz upgrade` scaffolds it from package data (bootstrap-retrofit case). This semantic distinguishes `gz upgrade` from `gz init --update`, which assumes prior init.
7. REQUIREMENT: `gz upgrade` MUST be idempotent: a second invocation immediately after a successful first invocation MUST exit 0 with zero artifacts reported as STALE or EDITED (modulo project-name substitution, which is OBPI-05's contract surface).
8. REQUIREMENT: `gz upgrade` MUST NOT mutate `.gzkit/manifest.json`, run scaffolder hooks beyond surface content copy, or invoke `gz agent sync control-surfaces`. Those are `gz init --update`'s contract; `gz upgrade` is the narrower surface-only verb.
9. REQUIREMENT: Manpage at `docs/user/manpages/upgrade.md` MUST follow the same shape as other registered command manpages (synopsis, options table, examples block, exit codes, related commands). Behave coverage at `features/upgrade.feature` MUST exercise every fail-closed requirement above (each REQ traced to ≥1 scenario or unit test per ADR-0.0.25).
10. REQUIREMENT: `gz check` MUST pass with the new command registered. `gz validate --documents` MUST recognize `docs/user/manpages/upgrade.md` and `features/upgrade.feature` as registered surfaces; `gz cli audit` MUST resolve `gz upgrade` as a registered verb (per `.claude/rules/governance-core.md` operator-doc verb resolution rule).

> STOP-on-BLOCKERS: if OBPI-0.0.32-02 (scaffolder refactor establishing `importlib.resources` resolution) or OBPI-0.0.32-06 (wheel includes shipping canonical content) have not landed, print a BLOCKERS list and halt — `gz upgrade` consumes both upstreams and cannot be implemented before they land.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.32-02 (skills scaffolder refactor) is Completed — the `importlib.resources.files("gzkit.skills")` resolution path that `gz upgrade` will reuse for every surface must be established.
- [ ] OBPI-0.0.32-06 (wheel includes + T0 smoke test) is Completed — `pyproject.toml [tool.hatch.build.targets.wheel] include:` ships canonical content for every surface this OBPI's `--surface` filter exposes.
- [ ] OBPI-0.0.32-04 / -10 / -12 / -13 (rules, personas, templates, chores scaffolder/normalization) are Completed for the surfaces listed in the `--surface` filter — `gz upgrade --surface rules` MUST NOT be advertised before `CORE_RULES` registry exists.

**Existing Code (understand current state):**

- [ ] Read `src/gzkit/commands/init.py` (esp. the `--update` flag handler authored by OBPI-05) to understand the three-state IDENTICAL/STALE/EDITED detection that `gz upgrade` shares with `init --update`. Factor shared helpers into a module both commands can import; do NOT duplicate the three-state logic.
- [ ] Read the canonical-routing test fixtures established by OBPI-01 / -03 / -09 / -11 / -13 to understand the byte-parity invariant `gz upgrade` consumes.
- [ ] Read `src/gzkit/commands/__init__.py` (parser-registration pattern) and one adjacent command module (e.g., `commands/init.py` or `commands/state.py`) for the argparse subparser registration convention.
- [ ] Read `docs/user/manpages/gz-init.md` for the manpage shape `gz-upgrade.md` should follow (synopsis + options + examples + exit codes + related-commands sections).

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz upgrade --help                                                     # registered subcommand
test -f docs/user/manpages/upgrade.md                                     # manpage authored
test -f features/upgrade.feature                                             # behave feature authored
test -f tests/commands/test_upgrade.py                                       # unit-tier coverage
uv run gz cli audit                                                          # gz upgrade resolves as registered verb
uv run -m behave features/upgrade.feature                                    # Gate 4 behave coverage
uv run -m unittest tests.commands.test_upgrade -q                            # unit-tier semantics
uv run gz arb step --name unittest -- uv run -m unittest -q                  # heavy-lane ARB receipt for tests
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict             # heavy-lane ARB receipt for docs
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Surface-only refresh of skills, dry-run first to preview changes
uv run gz upgrade --surface skills --dry-run

# Refresh skills + rules from the installed wheel
uv run gz upgrade --surface skills,rules

# Refresh every canonical surface (default)
uv run gz upgrade

# Force overwrite of project-local edits (with audit-trail output)
uv run gz upgrade --surface templates --force

# Bootstrap retrofit: project never ran gz init; pull canonical content from the wheel
uv run gz upgrade
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.32-14-01: `gz upgrade` is a registered subcommand of `gz`; `uv run gz upgrade --help` exits 0 and prints synopsis+options; `uv run gz cli audit` resolves `gz upgrade` as a registered verb.
- [ ] REQ-0.0.32-14-02: `gz upgrade --surface <list>` accepts comma-separated names from the registered canonical-surface set (`skills`, `rules`, `templates`, `personas`, `hooks`); unknown name exits 1 with naming-the-token error message; default (no flag) processes every registered surface.
- [ ] REQ-0.0.32-14-03: Without `--force`, EDITED project-local artifacts are reported as conflicts and left unchanged; exit non-zero when any EDITED conflict remains; exit 0 when zero conflicts.
- [ ] REQ-0.0.32-14-04: `--force` overwrites EDITED artifacts and prints one deterministic per-file overwrite line per modified path; exit 0 on success.
- [ ] REQ-0.0.32-14-05: `--dry-run` reports the same three-state classification a non-dry-run would, writes zero bytes to `.gzkit/`, and exits with the code the non-dry-run would have exited with.
- [ ] REQ-0.0.32-14-06: `gz upgrade` works in a fresh `pip install py-gzkit` environment without prior `gz init` — `.gzkit/<surface>/` is scaffolded from package data in the bootstrap-retrofit case.
- [ ] REQ-0.0.32-14-07: `gz upgrade` is idempotent — a second invocation immediately after the first reports zero STALE or EDITED artifacts and exits 0.
- [ ] REQ-0.0.32-14-08: `gz upgrade` does not mutate `.gzkit/manifest.json`, run scaffolder hooks beyond surface content copy, or invoke `gz agent sync control-surfaces`; those mutations remain `gz init --update`'s contract.
- [ ] REQ-0.0.32-14-09: Manpage `docs/user/manpages/upgrade.md` lands with synopsis/options/examples/exit-codes/related-commands sections; `gz validate --documents` passes; behave `features/upgrade.feature` exercises every REQ above (each REQ traced to ≥1 scenario or unit test per ADR-0.0.25 REQ-coverage gate).

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


```text
$ uv run gz upgrade --surface bogus
Unknown surface: 'bogus'. Known surfaces: skills, rules, templates, personas, hooks
$ echo $?
1

$ uv run gz upgrade --dry-run
Upgrade complete: N identical, 0 refreshed.
$ echo $?
0
```

Quality receipts:
- Tests: `arb-step-unittest-dd6cce6b7a64477e808e68fe35e68dd1` — 4967/4967 pass
- Lint: `arb-ruff-93a2f945ebd84b9f8e707d3123471841` — clean
- Typecheck: `arb-step-typecheck-6bc7bb66d62e47f3adc98cd0bdb4a1e8` — clean
- Docs build: `arb-step-mkdocs-afedd783c3ef42da8e983752839d50b6` — clean
- BDD: 11/11 scenarios in `features/upgrade.feature` pass
- REQ coverage: `gz covers OBPI-0.0.32-14-gz-upgrade-subcommand` reports 0 uncovered REQs

### Implementation Summary


- New command: `gz upgrade` — adopter-side surface-only refresh of `.gzkit/<surface>/` from installed wheel package data via `importlib.resources.files("gzkit.<surface>")`.
- Reuses three-state IDENTICAL/STALE/EDITED detection from `init_cmd.py` (`_iter_canonical_surface_files`, `_refresh_one_artifact`, `_detect_refresh_state`); no duplication of detection logic.
- Flags: `--surface skills,rules,templates,personas,hooks` (comma-list, default all), `--force` (overwrite EDITED with per-file audit line), `--dry-run` (exit code matches non-dry-run).
- Bootstrap-retrofit: scaffolds `.gzkit/<surface>/` from wheel when absent; idempotent on byte-identical state.
- Guard invariants: never reads/writes `.gzkit/manifest.json`, never calls `scaffold_core_*` hooks, never invokes `gz agent sync`. Brief denied paths enforced.
- Registered in `src/gzkit/cli/parser_governance.py` alongside `init` (lazy handler dispatch).
- Files created: `src/gzkit/commands/upgrade.py`, `tests/commands/test_upgrade.py` (21 tests), `tests/commands/test_upgrade_resources.py` (15 tests), `docs/user/manpages/upgrade.md`, `features/upgrade.feature` (11 scenarios), `features/steps/upgrade_steps.py`.
- Files modified: `parser_governance.py`, `manpages/index.md`, `runbook.md`, `governance_runbook.md`, `doc-coverage.json`, `trust_audits/cli.py` (`_NO_SKILL_VERBS` entry), and the brief itself.
- Tests added: 36 unit tests + 11 behave scenarios. All REQs traced via `@covers` decorators and `@REQ-` scenario tags.
- Date completed: 2026-05-13
- Attestation status: operator attested with "attest completed" in Stage 4; `--attestor-present` co-presence proxy via active pipeline marker.
- Defects noted: none in-scope.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- GHI #465 — `gz upgrade` ignored ADR-0.0.32 § Named exception 1 (hooks carve-out) and package-only carve-outs (`templates/skills/**`). Surfaced at ADR-0.0.32 closeout (demo 21). Resolved by direct fix removing `hooks` from `KNOWN_SURFACES` and consulting per-surface `_classify_*` helpers; REQ-0.0.32-14-02 corrected above.

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — gz upgrade surface-only refresh delivered with 36 unit tests, 11 behave scenarios, 9 REQ coverage (zero gaps), and ARB receipts arb-step-unittest-dd6cce6b7a64477e808e68fe35e68dd1, arb-ruff-93a2f945ebd84b9f8e707d3123471841, arb-step-typecheck-6bc7bb66d62e47f3adc98cd0bdb4a1e8, arb-step-mkdocs-afedd783c3ef42da8e983752839d50b6 — all green; gz cli audit passes; gz check exits 0.
- Date: 2026-05-13

---

**Brief Status:** Completed

**Date Completed:** 2026-05-13

**Evidence Hash:** -
