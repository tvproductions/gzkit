# AUDIT_PLAN — ADR-0.0.34-agent-control-surface-rendering-substrate

**Audit driver:** pipeline-orchestrator persona (per `.claude/skills/gz-adr-audit/SKILL.md`).
**Date opened:** 2026-05-17.
**Trust model:** Layer 2 — consume `gz adr audit-check` ledger proof; re-verify only on staleness.
**Goal:** COMPLETED → VALIDATED lifecycle promotion for ADR-0.0.34.

## Scope

ADR-0.0.34 canonizes the headless-CMS substrate that every per-turn agent control surface renders from. Eight OBPIs, all `attested_completed`. Heavy lane, foundation kind. Lifecycle currently `Completed`; this audit, plus operator verbal `accept audit`, promotes to `Validated`.

## Claims extracted from ADR prose

| # | Claim | Source line | OBPI |
|---|-------|-------------|------|
| C1 | Eight canonical content models registered (`AgentContract`, `Rule`, `Skill`, `Chore`, `Persona`, `Handoff`, `Scenario`, `Bullet`) with `frozen=True, extra="forbid"` | ADR §Decision, OBPI-01 | 01 |
| C2 | Jinja2 templates per (content type × vendor) replace file-copy logic; render is deterministic and byte-stable | ADR §Decision, OBPI-02 | 02 |
| C3 | Round-trip fidelity contract: `model == parse(render(model))` AND `render(parse(render(m))) == render(m)` | ADR §Decision, OBPI-03 | 03 |
| C4 | Authoring CLI: `gz content list / show / render / edit / import` with prose output (never raw JSON in operator review surface by default) | ADR §Decision, OBPI-04 | 04 |
| C5 | Light TUI affordances via Rich tables + plan-mode panels; explicitly NO Textual form editor | ADR §Decision, OBPI-05 | 05 |
| C6 | Validation hooks fire ADR-0.0.33 fidelity validators on every render and every save; failure does not land | ADR §Decision, OBPI-06 | 06 |
| C7 | Migration layer: Pydantic `schema_version` stamping + typed migration registry; v1 baseline byte-identical | ADR §Decision, OBPI-07 | 07 |
| C8 | Vendor manifest is canonical declaration of routing; `gz validate --vendor-manifest` is fail-closed | ADR §Decision, OBPI-08 | 08 |
| C9 | Eight-component delivery is coherent and integrated — not eight disjoint patches | ADR §Decision sequencing note | all |

## Checks per claim

| Check | Type | Command | Proof file |
|-------|------|---------|------------|
| Ledger proof complete (Layer-2 trust foundation) | L2 | `uv run gz adr audit-check ADR-0.0.34` | `proofs/audit_check.txt` |
| ADR lifecycle + OBPI roll-up | L1 | `uv run gz adr report ADR-0.0.34` | `proofs/adr_report.txt` |
| Content registry live (C1) | L1 | `uv run python -c "from gzkit.content.models import CONTENT_MODELS; …"` | `proofs/content_registry.txt` |
| `gz content` CLI surface live (C4) | L1 | `uv run gz content --help` | `proofs/content_help.txt` |
| `gz content list` table renders (C4, C5) | L1 | `uv run gz content list --plain` | `proofs/content_list.txt` |
| Round-trip fidelity for Rule (C2, C3) | L1 | round-trip exercise (parse/render/parse/render) | `proofs/round_trip_fidelity.txt` |
| Vendor manifest validator green (C8) | L1 | `uv run gz validate --vendor-manifest` | `proofs/vendor_manifest_validate.txt` |
| Vendor manifest content readable (C8) | L1 | inspect `data/vendor-manifest.json` | `proofs/vendor_manifest.txt` |
| Validation hooks wired at render time (C6) | L1 | import check + source inspection | `proofs/validation_hooks.txt` |
| TUI affordances import Rich (C5) | L1 | import check on `gzkit.commands.content.{list,show}` | `proofs/tui_affordances.txt` |
| Migration registry live (C7) | L1 | import + `Rule.schema_version` default check | `proofs/migration_registry.txt` |
| Content test suite GREEN (cross-cutting integration) | L1 | `uv run -m unittest tests.content.test_round_trip_rule tests.content.test_byte_stability tests.content.test_validation_hooks tests.content.test_vendor_manifest tests.content.test_migration_layer -q` | `proofs/content_suite_unittest.txt` |
| Governance validators green | L1 | `uv run gz validate --documents --surfaces` | `proofs/gz_validate.txt` |
| CLI verb coverage 100% | L1 | `uv run gz cli audit` | `proofs/cli_audit.txt` |

## Risk focus

1. **Layer-2 trust dependence.** The audit trusts ledger proof from `gz adr audit-check`. Mitigation: confirmed `passed=true, total_reqs=39, covered_reqs=39, complete_obpis=8/8` in JSON output before skipping re-verification of every REQ.
2. **Coverage-shape drift risk.** None observed — `coverage_findings`, `coverage_blocking`, `coverage_advisory`, `covers_backfill_findings`, `covers_backfill_unresolvable` all empty arrays in audit-check JSON.
3. **Value demonstration risk.** Foundation ADRs are tempting to audit mechanically; this run executes live `gz content` CLI commands and demonstrates the canonical-model substrate operating, not just "tests pass".
4. **Drift between attested-OBPI completion (2026-05-16) and audit (2026-05-17).** 1-day delta is well within the 7-day staleness threshold; no re-verification triggered.

## Persona dispatch

Per `.claude/skills/gz-adr-audit/SKILL.md` Persona Dispatch table:

- **spec-reviewer** — Steps 1–2 (independent requirement-tracing against ledger proof).
- **quality-reviewer** — between Step 2 and Step 3 (structural-coherence assessment).
- **narrator** — Step 3 Value Demonstration framing.

Independent assessments are recorded in `AUDIT.md` § Subagent Independent Assessments.
