# Promoted Inventory — control-surface-rule-vs-check-drift (Pass C)

Every `gz validate --<scope>` flag that corresponds to a **Mechanical**
scorecard entry under `docs/governance/advisory-rules-audit.md`. Each row is
derived from:

1. `uv run gz validate --help` — the live inventory of scope flags.
2. `docs/governance/advisory-rules-audit.md` — cross-referencing Mechanical
   entries to the flag they landed as.

Scorecard row numbers refer to the `#` column in the tables in that document.

| # | Rule file + § | Promoted scope flag | Scorecard row # | GHI that landed the check |
|---|---|---|---|---|
| 1 | `CLAUDE.md` § Architectural Boundaries (rules 1–2) — pool ADR runtime isolation | `--pool-adr-isolation` | #1, #2 | GHI #208 |
| 2 | `CLAUDE.md` § Architectural Boundaries (rule 4) — reconciliation freshness | `--reconcile-freshness` | #4 | GHI #213 |
| 3 | `CLAUDE.md` § Architectural Boundaries (rule 6) — no derived-view-as-source-of-truth (frontmatter coherence) | `--frontmatter` | #6 | GHI #166 lineage |
| 4 | `CLAUDE.md` § Architectural Boundaries (rule 6) — no derived-view-as-source-of-truth (event handler coverage) | `--event-handlers` | #6 | GHI #193 class |
| 5 | `CLAUDE.md` § Architectural Boundaries (rule 6) — no derived-view-as-source-of-truth (validator field coverage) | `--validator-fields` | #6 | GHI #193 class |
| 6 | `CLAUDE.md` § Architectural Boundaries (rule 6a) — ADR taxonomy kind/semver/id-prefix coherence | `--taxonomy` | #6a | GHI #218 / ADR-0.0.17 |
| 7 | `CLAUDE.md` § Local Agent Rules (rule 9) + `.gzkit/rules/cross-platform.md` § Console Output — no `PYTHONUTF8=1` prefix | `--utf8-prefix` | #9, #45 | GHI #206 |
| 8 | `CLAUDE.md` § Local Agent Rules (rule 11) — every version bump is a release | `--version-release` | #11 | GHI #205 |
| 9 | `.gzkit/rules/governance-core.md` § Proof commands — CLI alignment for operator-doc verbs | `--cli-alignment` | #14 (partial) | GHI #198 |
| 10 | `.gzkit/rules/pythonic.md` § Size Limits — classes ≤300 lines | `--class-size` | #21 | GHI #204 |
| 11 | `.gzkit/rules/pythonic.md` § "Type-check suppression syntax (ty — binding)" | `--type-ignores` | #24 | GHI #197 |
| 12 | `.gzkit/rules/models.md` (rules 25 + 26) — Pydantic BaseModel + ConfigDict discipline | `--pydantic-models` | #25, #26 | GHI #203 |
| 13 | `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 1 — every CLI verb has a wielding skill | `--skill-alignment` | #28 | GHI #202 |
| 14 | `.gzkit/rules/tests.md` § TASK-Driven Workflow — governance-intent commit trailers | `--commit-trailers` | #35 | GHI #201 |
| 15 | `.gzkit/rules/tests.md` § Runner anti-patterns — no third test tier | `--test-tiers` | #37 | GHI #209 |
| 16 | `.gzkit/rules/tests.md` § Behave scenario tagging — `@REQ-X.Y.Z-NN-MM` coverage | `--behave-req-tags` | #39 | GHI #211 |
| 17 | `docs/governance/advisory-rules-audit.md` § Promotion discipline (meta / self-test) | `--advisory-scorecard` | scorecard "meta" row | GHI #212 |
| 18 | `.gzkit/rules/brief-heading-conventions.md` — brief evidence sections must be H3 | `--brief-headings` | new rule 2026-04-21 | GHI #238 |

## Scope flags NOT in this audit

The following flags are live but either (a) not documented as a single-rule
mechanical promotion in the scorecard, or (b) predate the audit architecture
that this chore is built around:

| Flag | Reason for exclusion |
|---|---|
| `--manifest`, `--documents`, `--surfaces`, `--ledger`, `--instructions`, `--briefs`, `--personas`, `--interviews`, `--decomposition`, `--requirements`, `--version` | Baseline schema/artifact validators, pre-dating the scorecard's mechanical-promotion framing. Scorecard does not map any numbered rule to these flags. |
| `--adr`, `--explain`, `--json`, `--quiet`, `--verbose`, `--debug` | Not scopes — output modifiers / scope qualifiers. |

## Waivers visible in the validator source

The validator carries these explicit pass-list dicts (trust doctrine T2 —
explicit waivers beat silent skips):

| Waiver dict | Location | Covers |
|---|---|---|
| `_NO_GRAPH_IMPACT` | `src/gzkit/governance/trust_audits.py:39-61` | Event types intentionally not handled by the graph |
| `_VALIDATOR_FIELD_WAIVERS` | `src/gzkit/governance/trust_audits.py:63` | (empty) |
| `_DOC_PROSE_VERBS` | `src/gzkit/governance/trust_audits.py:65` | (empty frozenset) |
| `_CLASS_SIZE_WAIVERS` | `src/gzkit/governance/trust_audits.py:70-79` | Over-300-line classes with rationale |
| `_DATACLASS_WAIVERS` | `src/gzkit/governance/trust_audits.py:84-89` | `@dataclass` sites where BaseModel is not required |
| `_NO_SKILL_VERBS` | `src/gzkit/governance/trust_audits.py:832-859` | CLI verbs with no wielding skill, each with rationale |
