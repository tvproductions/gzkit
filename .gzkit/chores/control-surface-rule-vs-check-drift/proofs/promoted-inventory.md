# Promoted Inventory — Pass C

> Chore: `control-surface-rule-vs-check-drift` (Lite lane, audit-only)
> Run: **2026-08-09**. Supersedes the 2026-08-01 inventory.
> Method: `uv run gz validate --help` cross-referenced against
> `docs/governance/advisory-rules-audit.md` § Scorecard rows scored **Mechanical**
> whose Notes cite a `gz validate --<scope>` flag.

## Counts

| Measure | Value |
|---|---|
| Registered validator scopes | **89** |
| Promoted (rule, scope) pairs | **44** — 35 distinct flags across 33 distinct rows |
| New pairs since baseline `0551bbbd3` | 6 |
| **Registered scopes binding no Mechanical row** | **54 of 89** |

**The last row is this run's structural finding.** The scorecard answers *"is this
rule enforced?"*. The inverse question — *"does this enforcement correspond to a
rule?"* — has no owner, and more than half the mechanical surface is unattributed.
See § Unattributed enforcement.

## Promoted pairs

| Rule file / doctrine home | Scope flag | Scorecard row | Since baseline |
|---|---|---|---|
| `CLAUDE.md` § Architectural Boundaries | `--pool-adr-isolation` | 1, 2 | existing |
| `CLAUDE.md` § Architectural Boundaries | `--reconcile-freshness` | 4 | existing |
| `CLAUDE.md` § Architectural Boundaries | `--frontmatter` | 6 | existing |
| `CLAUDE.md` § Architectural Boundaries | `--event-handlers` | 6 | existing |
| `CLAUDE.md` § Architectural Boundaries | `--validator-fields` | 6 | existing |
| `CLAUDE.md` § Architectural Boundaries | `--taxonomy` | 6a | existing |
| `CLAUDE.md` § Local Agent Rules | `--utf8-prefix` | 9 | existing |
| `CLAUDE.md` § Local Agent Rules | `--version-release` | 11 | existing |
| `.gzkit/rules/governance-core.md` | `--cli-alignment` | 14, **17e** | 17e NEW |
| `.gzkit/rules/governance-core.md` | `--insights-shape` | 17a | existing |
| `.gzkit/rules/governance-core.md` | `--instructions-files-budget` | 17b | existing |
| `.gzkit/rules/governance-core.md` | `--adr-status-fresh` | **17f** | NEW |
| `.gzkit/rules/pythonic.md` | `--class-size` | 21 | existing |
| `.gzkit/rules/pythonic.md` | `--type-ignores` | 24 | existing |
| `.gzkit/rules/models.md` | `--pydantic-models` | 25, 26 | existing |
| `.gzkit/rules/tool-skill-runbook-alignment.md` | `--skill-alignment` | 28 | existing |
| `.gzkit/rules/tests.md` | `--commit-trailers` | 35, **68** | 68 NEW |
| `.gzkit/rules/tests.md` | `--test-tiers` | 37 | existing |
| `.gzkit/rules/tests.md` | `--behave-req-tags` | 39 | existing |
| `.gzkit/rules/tests.md` | `--red-parity` | **67** | NEW |
| `.gzkit/rules/tests.md` § REQ Scope Discipline | `--req-kind-discipline` | 59 | existing |
| `.gzkit/rules/cross-platform.md` | `--utf8-prefix` | 45, 45a | existing |
| `.gzkit/rules/security-sensitivity.md` | `--sensitivity` | 48 | existing |
| `.gzkit/rules/model-selection.md` | `--surfaces` | 52 | existing |
| `.gzkit/rules/complexity-doctrine.md` | `--complexity-doctrine-links` | 50 | existing |
| `.gzkit/rules/complexity-thresholds.{md,json}` | `--complexity-thresholds` | 51 | existing |
| `.gzkit/rules/agents-md-map-doctrine.md` | `--agents-md-map-conformance` | 58 | existing |
| `.gzkit/rules/agents-md-map-doctrine.md` | `--instructions-files-budget` | 58 | existing |
| `.gzkit/rules/task-discovery.md` | `--task-envelope-coherence` | 60, **60b** | 60b NEW |
| `.gzkit/rules/task-discovery.md` | `--commit-trailers` | 60 | existing |
| `.gzkit/rules/changelog-release-notes.md` | `--changelog` | 65 | existing |
| `.gzkit/rules/token-block-discipline.md` | `--lock-exchange-coupling` | **73** | NEW (row and flag) |
| ADR-0.0.20 (no rule file) | `--unscoped-rules`, `--audits` | 47 | existing |
| ADR-0.0.31 / trust-doctrine T0 | `--distribution` | 57 | existing |
| ADR-0.0.37 OBPI-03 / OBPI-05 | `--invariant-coherence`, `--brief-reconcile` | 58, 59 | existing |
| `src/gzkit/schemas/advisor_diagnosis.json` | `--advisor-proof-binding` | 54 | existing |

**Row 73 cites the module (`lock_exchange_coupling.py`) and the `gz check` runner,
never the flag string** — the pair is real but the citation form differs from every
other row, which is why it reads as unattributed to a naive flag-string scan.

## Unattributed enforcement — 54 registered scopes binding no Mechanical row

Not a defect list. A scope may legitimately enforce an ADR decision, a schema, or a
doctrine doc rather than a `.gzkit/rules/**` file. It is recorded because the
scorecard cannot see it, so nothing tells a reader which of these is deliberate.

`--manifest` · `--documents` · `--ledger` · `--instructions` · `--briefs` ·
`--personas` · `--interviews` · `--decomposition` · `--requirements` · `--version` ·
`--event-schemas` · `--authorship` · `--line-endings` · `--pool-interview` ·
`--obpi-lifecycle-coherence` · `--adversarial-validation` · `--session-green-gate` ·
`--orientation-freshness` · `--chores-layout` · `--rule-version-markers` ·
`--invariant-witness` · `--doc-surface-parity` · `--absorption-duplicates` ·
`--orphaned-implementation` · `--evaluation-justify-binding` ·
`--intrinsic-attestation` · `--qc-binding` · `--fidelity-presence` ·
`--waiver-ratchet` · `--closeout-proof` · `--transcribed-adr-counts` ·
`--deprecated-verb-prescription` · `--okf-conformance` · `--router-tables` ·
`--brief-structure` · `--bullet-retention` · `--surface-weight` ·
`--pointer-anchors` · `--surface-fidelity` · `--vendor-manifest` ·
`--setpoint-coherence` · `--rendition-freshness` · `--rendition-floor-coherence` ·
`--kind-invariance` · `--persona-witness` · `--receipt-shape` ·
`--status-writer-coverage` · `--ontology-purity` · `--brief-command-shape` ·
`--advisory-scorecard` · `--tautological-test-audit` · `--brief-headings` ·
`--brief-cross-references` · `--brief-demo-section`

**All five scopes registered since baseline landed with zero flag-string citations
in the scorecard:** `--pool-interview` (GHI #719), `--invariant-witness` (GHI #746),
`--transcribed-adr-counts` (GHI #768), `--status-writer-coverage` (GHI #669), and
the renamed `--lock-exchange-coupling` (GHI #763). Four of the five shipped in
v0.34.2. A validator can be built, registered, wired into `gz check`, and released
without any surface recording which rule it enforces.

## Orphan citations — scorecard cites a flag that is not registered

| Row | Flag cited | Citing text |
|---|---|---|
| 49 (`agent-failure-modes.md`) | `--failure-mode-coverage` | *"Promotion candidate `gz validate --failure-mode-coverage` … tracked under follow-up GHIs #308–#312"* |
| § Summary prose (not a row) | `--failure-mode-coverage` | *"(mechanical promotion `gz validate --failure-mode-coverage` tracked under follow-up GHIs #308–#312)"* |
| 62 (`mx-mode.md`) | `--mx-marker-coherence` | *"a proposed `--mx-marker-coherence` scope"* |

All three are explicitly **proposed**, not asserted as existing, so none is a false
Mechanical claim. Recorded so a future flag-resolution scan does not read them as
dead pointers.
