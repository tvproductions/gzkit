# AUDIT_PLAN — ADR-0.0.32 (canonical-surface-packaging)

**Date:** 2026-05-13
**Auditor:** main-session agent (subagent invocation)
**Operator of record:** g0
**Lane / Kind / Sensitivity:** heavy / foundation / (none)
**Prerequisite check:** `gz adr audit-check ADR-0.0.32` → PASS (all 14 linked OBPIs attested_completed; 8 advisory uncovered REQs labelled non-blocking).

## Scope

Verify that ADR-0.0.32 delivered the dual-surface canonical-routing model across skills, rules, personas, templates, and chores; that the T0 distribution invariant (`gz validate --distribution`) enforces wheel-shipping discipline; that `gz init --update` and `gz upgrade` expose adopter-side refresh surfaces; that `gz agent sync control-surfaces` is the unified propagation mechanism.

## Claims extracted from ADR prose

| # | Claim | Source paragraph |
|---|---|---|
| C1 | `.gzkit/<surface>/` is authored canonical source-of-truth; `src/gzkit/<surface>/` is wheel-shipping byte-parity copy; `.[vendor]/<surface>/` is the agent-runtime mirror | § Intent; § Decision |
| C2 | `gz agent sync control-surfaces` propagates `.gzkit/` to BOTH `src/gzkit/` AND `.[vendor]/` in one invocation | § Decision; § Canonical-routing scope |
| C3 | `gz init --update` provides version-aware refresh with IDENTICAL / STALE / EDITED three-state detection | § Decision; OBPI-05 |
| C4 | `gz upgrade` is the adopter-side surface-only refresh, distinct from `gz init --update` | § Decision; OBPI-14 |
| C5 | `gz validate --distribution` enforces T0 fail-closed (exit 3 on drift) — wheel-include drift, baseline drift | § Decision; OBPI-07 |
| C6 | T0 smoke test in `features/distribution_invariant.feature` builds a wheel, installs into a temp venv, runs `gz init`, asserts byte-equivalence against frozen baseline | § Decision; OBPI-06 |
| C7 | Module-to-package conversions for `src/gzkit/skills.py` → `src/gzkit/skills/__init__.py` and `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py` preserve all public-symbol re-exports | § Decision |
| C8 | Byte-parity test fails closed on any drift between `.gzkit/<surface>/` and `src/gzkit/<surface>/` for skills, rules, personas, templates | § Decision; § Consequences |
| C9 | Chores carry mixed file classes (canonical / package_only / runtime_state); byte-parity binds canonical content only | § Named exceptions / Exception 2; OBPI-13 |

## Checks

| Check | Command | Layer | Expected |
|---|---|---|---|
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.32` | L2 | PASS (all OBPIs attested) |
| Distribution invariant (live demo) | `uv run gz validate --distribution` | L1 | exit 0 (clean state) OR exit 3 with categorized errors that the validator caught fail-closed |
| Init refresh demo | `uv run gz init --update --dry-run` | L1 | three-state report (IDENTICAL/STALE/EDITED) |
| Upgrade subcommand | `uv run gz upgrade --help` | L1 | manpage with `--surface`/`--force`/`--dry-run` |
| Sync mechanism | `uv run gz agent sync control-surfaces` | L1 | propagates to vendor mirrors; idempotent |
| Lint clean | `uv run gz lint` | L1 | exit 0 |
| Tests pass | `uv run -m unittest discover -s tests -t .` | L1 | exit 0; 4900+ tests pass |
| Module-to-package APIs | `python -c "from gzkit.skills import CORE_SKILLS, scaffold_core_skills; from gzkit.rules import CORE_RULES, scaffold_core_rules; print('ok')"` | L1 | exit 0 |
| Lifecycle confirmation | `uv run gz adr report ADR-0.0.32` | L1 | Lifecycle Validated (post-receipt) |

## Risk focus

1. **Bidirectional drift risk** — the dual-surface model creates two arrows (`.gzkit/` → `src/gzkit/`, `.gzkit/` → `.[vendor]/`); the T0 validator and the byte-parity tests are the only mechanical guards. Loss of either guard re-opens the original GHI #318 class.
2. **Baseline manifest staleness** — `data/distribution_baseline_manifest.json` is hand-authored under OBPI-06; no regenerator subcommand ships in this ADR. Drift between on-disk and baseline accumulates whenever a new skill/rule/persona/template lands.
3. **Package-only Python files inside canonical surface trees** — when `src/gzkit/rules/` contains both `*.md` (canonical) and `*.py`/`*.json` (package_only), the T0 validator's binary include-or-not-included check breaks down. The chores class-classifier exists in `src/gzkit/chores/__init__.py::_classify_chore_file` but is not yet extended to rules/skills/personas/templates.

## Audit notes

- Layer 2 trust model: ledger PASS allows skipping re-verification of unit tests/mkdocs/gates per skill § "Layer 2 Trust Model". Tests + lint re-run here anyway as defense in depth (cheap, ~45s).
- 8 advisory uncovered REQs reported by `audit-check` (OBPI-01-07, 02-03, 03-04, 03-05, 09-03, 09-04, 11-06, 11-08). Non-blocking per the CLI's labeling. Per skill § Step 2 diagnosis rule, NO cosmetic `@covers` backfill — these are recorded for future remediation under their parent OBPIs, not silenced.
- 13 OBPI checklist items in the ADR prose were left `[ ]` despite the ledger marking them `attested_completed`. Fixed in this audit pass as 1:1-sync-mandate compliance.
- Frontmatter `status: Draft` was stale relative to ledger truth (all 14 OBPIs attested_completed). Updated to `Completed` in this audit pass.
