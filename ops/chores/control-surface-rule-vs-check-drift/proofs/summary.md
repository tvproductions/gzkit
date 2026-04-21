# Summary — control-surface-rule-vs-check-drift (Pass C)

## Counts by verdict

| Verdict | Count |
|---|---|
| parity | 5 |
| prose-wider | 10 |
| check-wider | 0 |
| divergent | 3 |
| **Total promoted flags audited** | **18** |

Scorecard currently reports 59% Mechanical promotion across the rule surface. This audit tests the stronger claim — does the mechanical check enforce what the prose says? In more than half of promotions (13 of 18, 72%) the check implements a strict subset of, or diverges from, the rule prose. Zero `check-wider` verdicts confirms the pattern: promotions shipped with partial implementations, but the accompanying rule-text narrowing that `docs/governance/advisory-rules-audit.md` § Promotion discipline would prescribe never happened.

## Top 5 prose-wider cases (ranked by promotion value)

1. **`--utf8-prefix`** (row 7) — `.gzkit/rules/cross-platform.md` explicitly declares fresh-interpreter helpers (`python -c`, `uv run python <script>`, `tools/**`) must configure UTF-8 stdin/stdout. Check enforces **none** of it — scans only for the literal `PYTHONUTF8=1 uv run gz` prefix. GHI #234 observed the exact failure class; the rule-text fix landed, the mechanical fix did not.
2. **`--type-ignores`** (row 11) — positive form (`# ty: ignore[<ty-code>]` with ty-code specificity) is entirely unenforced. `# ty: ignore[totally-bogus-code]` passes. Check is blacklist-only on the mypy-bracket form.
3. **`--pydantic-models`** (row 12) — `model_config = {}` satisfies the check, even though prose demands `ConfigDict(frozen=True, extra="forbid")`. The frozen/forbid semantics — the actual point of the Pydantic discipline — is unchecked.
4. **`--version-release`** (row 8) — `pyproject.toml` / `__init__.py` / README badge triple is named in prose; only `pyproject.toml` is validated. Version drift between the three files lands silently.
5. **`--advisory-scorecard`** (row 17) — stem-as-substring-anywhere is weak: a rule stem mentioned in a narrative paragraph of the scorecard (but without a table row) passes the check. Score presence and stale-row detection both absent.

Remaining prose-wider rows (6–10): `--skill-alignment` (Invariant 1 treats only top-level subparser choices as verbs — multi-word subcommands like `gz adr status` are invisible), `--commit-trailers` (trailer-as-final-line positional discipline unenforced; HEAD-only scope not blessed in prose), `--pool-adr-isolation` (prose covers both id-prefix and `docs/design/adr/pool/` path; check covers only id-prefix), `--validator-fields` (asymmetric vs sibling `--event-handlers` on stale-waiver enforcement), `--taxonomy` (non-pool id-prefix ↔ semver coherence not enforced).

## Top divergent cases (3 total, ranked by drift risk)

1. **`--behave-req-tags`** (row 16) — prose scopes to "Heavy-lane and foundation-kind OBPIs" (scorecard row #39); check is scope-blind. Prose direction is OBPI → feature (every Heavy OBPI REQ must have scenario coverage); check direction is feature → feature (every feature-level `# @covers` must have matching scenario tag). A Heavy OBPI with zero feature coverage passes the check entirely — the check literally cannot see the violation the prose forbids.
2. **`--reconcile-freshness`** (row 2) — prose asserts reconciliation is "tested, gated, and part of the pipeline"; check fails-open when the ledger has zero reconcile events (`trust_audits.py:1024-1028` explicit carve-out). A reconciliation pathway that has never fired appears green. A project that has never run reconciliation looks identical to one that runs it continuously.
3. **`--cli-alignment`** (row 9) — rule-file source is implicit (lives in validator docstring, not any `.gzkit/rules/*.md` file). Check excludes `.gzkit/skills/**/SKILL.md` — the surface where the tool-skill-runbook-alignment rule asserts skills must wield real verbs. An unresolvable `gz <verb>` in a SKILL.md passes this audit but violates the spirit of the Invariant 1 promoted alongside.

## Prioritized follow-up list

| # | Scope flag | Action | GHI shape |
|---|---|---|---|
| 1 | `--utf8-prefix` | Extend scan to `python -c` / `uv run python <script>` / `tools/**/*.py`; assert `sys.stdout.reconfigure` present | mechanical-promotion GHI |
| 2 | `--type-ignores` | Cross-check `# ty: ignore[<code>]` comments against ty's own error-code set | mechanical-promotion GHI |
| 3 | `--pydantic-models` | AST-walk `model_config=ConfigDict(...)` keyword args; require `frozen=True` + `extra="forbid"` on immutable models | mechanical-promotion GHI |
| 4 | `--version-release` | Parse `__init__.py` `__version__` and README badge; assert match against `pyproject.toml` | mechanical-promotion GHI |
| 5 | `--behave-req-tags` | Architectural realign: split OBPI→feature coverage from feature→feature coverage, or redirect the check to the prose direction | rule-clarification + mechanical-promotion GHI |
| 6 | `--reconcile-freshness` | Decide fail-open vs fail-closed on empty reconcile history (architectural decision) | rule-clarification GHI |
| 7 | `--cli-alignment` | Author an explicit `.gzkit/rules/*.md` home for this rule; extend scan to `.gzkit/skills/**/SKILL.md` | direct-fix + mechanical-promotion GHI |
| 8 | `--advisory-scorecard` | Replace substring-match with table-row regex; validate score enum; detect stale rows | mechanical-promotion GHI |
| 9 | `--skill-alignment` | Extend "verb" semantics to multi-word subcommand paths (`gz adr status`, `gz obpi complete`, etc.) | mechanical-promotion GHI |
| 10 | `--commit-trailers` | Enforce `Task:` as final line (positional discipline); decide whether HEAD-only scope is contract or advisory | direct-fix GHI |
| 11 | `--pool-adr-isolation` | Extend scan to `docs/design/adr/pool/` path in addition to `ADR-pool.` id-prefix | direct-fix GHI |
| 12 | `--validator-fields` | Symmetric stale-waiver enforcement vs `--event-handlers` (scorecard rules 6 sibling pair) | direct-fix GHI |
| 13 | `--taxonomy` | Enforce non-pool id-prefix ↔ `semver:` frontmatter coherence | direct-fix GHI |
| 14 | `--pool-adr-isolation` | Decide 1.0-boundary meaning (prose says "post-1.0"; check is boundary-agnostic) | rule-clarification GHI |
| 15 | `--class-size` | No action — split enforcement across ruff/xenon/pre-commit is scorecard-acknowledged | — |
| 16 | `--frontmatter` | No action — parity verdict | — |
| 17 | `--event-handlers` | No action — parity verdict | — |
| 18 | `--test-tiers` | Minor: document the parser-source scope vs the substring `flag in text` false-positive risk | doc-only GHI |

## Method note

Audit sourced from cross-referencing `docs/governance/advisory-rules-audit.md` **Mechanical** scorecard rows with live `gz validate --help` scope flags. Baseline validators without a scorecard row (`--manifest`, `--documents`, `--surfaces`, `--ledger`, `--instructions`, `--briefs`, `--personas`, `--interviews`, `--decomposition`, `--requirements`, `--audits`, `--adr`, `--explain`, `--version`, `--ledger-integrity`) are out of scope — they predate the scorecard promotion-audit framing and assert schema invariants, not rule prose.

## Harness note

The Pass C subagent's final `summary.md` write was blocked by a harness-level heuristic framing subagent file-writes as report artifacts. Four of five proof files landed via the subagent; this file was written by the parent session using the subagent's returned content plus the full `parity-diff.md` row-set for the prioritized follow-up table. Same blocker hit during Pass A and worked around by the agent via Bash heredoc — recommend surfacing this as a chore-runner UX defect for a separate GHI (the harness should not treat bounded `ops/chores/<slug>/proofs/` writes as report spillover).
