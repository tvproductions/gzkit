# Parity Diff Summary

**Generated:** 2026-05-10
**Scope:** 123 prose assertions vs. 33 in-scope promoted check scopes.
**Source files:** `prose-assertions.md`, `check-behaviors.md`, `parity-diff.md`.

Path renderings use POSIX form.

## Verdict counts

| Class | Count | % of 123 |
|-------|-------|----------|
| `in-parity` (direct or delegated to external mechanical tool) | 73 | 59% |
| `prose-only` (no mechanical check; deliberate Judgment-class) | 26 | 21% |
| `prose-only` (Promotable — could be mechanized) | 11 | 9% |
| `prose-wider` (check narrower than prose) | 9 | 7% |
| `mismatched` (check enforces different invariant than prose) | 1 | 1% |
| `check-only` (check exists, no rule prose) | 3 | 2% |

The chore's primary contribution is the `prose-wider` and `mismatched`
columns: rules that *appear* promoted on the advisory scorecard but
whose underlying check covers a strict subset of the prose. These are
the highest-leverage targets because operators read the scorecard and
assume *parity*, not *partial coverage*.

## Top 5 highest-impact gaps

| # | Gap | Class | Recommendation |
|---|-----|-------|----------------|
| 1 | **Operator PII in repo artifacts** (`AGENTS.md` Local rules, parity row 99) | prose-only (high-impact) | **Promote to mechanical**: a `gz validate --operator-pii` scope that scans commit messages, ledger entries, attestation strings, and rule/doc bodies for the operator's personal email — recovery from a leak is a `git filter-repo` rewrite + force-push (2026-04-19 incident). The cost of one false negative is asymmetric with every other rule in the scorecard. |
| 2 | **Multi-word subcommand resolution** (`.gzkit/rules/governance-core.md:46`, parity row 41) | mismatched | **Fix mismatched check**: `audit_cli_alignment` regex captures only the first token of a `gz <verb>` reference; the rule explicitly says multi-word subcommands count (`gz adr status`, `gz obpi complete`). Extend the regex to capture the next non-flag token and resolve against subparser → subparser chains. Today, a typo in `gz adr <typo>` passes the check while the prose says it should fail. |
| 3 | **ConfigDict `frozen=True, extra="forbid"` content** (`.gzkit/rules/models.md:8`, parity row 8) | prose-wider | **Tighten mechanical check**: `audit_pydantic_models` verifies a `model_config` attribute exists but does not inspect the call expression. Extend the AST inspection to assert `ConfigDict(...)` keyword arguments contain `frozen=True` AND `extra="forbid"` for models declared immutable (or all governance models). Today, a `BaseModel` subclass with `model_config = ConfigDict()` (empty) passes the check while the prose calls it an anti-pattern. |
| 4 | **Advisory scorecard requires *score*, not just *mention*** (parity row 90) | prose-wider | **Tighten mechanical check**: `audit_advisory_scorecard` uses case-folded substring search — a rule's stem appearing in a stray cross-reference passes. The scorecard's own prose says every rule must be **scored** (Mechanical / Promotable / Judgment / Ambiguous). Promote: parse the scorecard's tables and assert the rule stem appears in a row with one of the four valid scores. |
| 5 | **Behavior Rule #11 — course-correction insight record** (parity row 107) | prose-wider | **Promote presence check**: `--insights-shape` validates shape *when* a record is written. The rule says agents *must* append a record on every course-correction. Promotion target: detect course-correction signals in conversation transcripts (or commit messages) and assert a matching insight record exists. Operator-attested signal would be a `Correction:` commit trailer linking to the insight ID. |

## Routing recommendation

- **Promote to mechanical (5 promotions):** rows 99, 41, 8, 90, 107 above.
- **Tighten existing check (2):** rows 41 and 8 are tightenings of existing audits, not new scopes — lowest-effort, highest-immediate-leverage.
- **New `gz validate` scope (3):** rows 99 (`--operator-pii`), 90 (`--advisory-scorecard` rework), 107 (`--course-correction-coverage`).
- **Accept gap (judgment-class):** rows scored Judgment in the advisory scorecard (Prime Directive, DO IT RIGHT 1-9, Operator economy, etc.) are explicitly *not* mechanically enforceable. They appear in the prose-only count but should not be promoted — the existing scorecard treats them correctly.
- **File catch-up rule prose for check-only rows:** rows 120, 121, 122, 123. Each has a working mechanical check but no canonical rule-file prose. Operators looking up "why does `--doc-surface-parity` exist?" today must read the ADR/GHI rather than the rule canon. Short rule-file insertions would close the cycle.

## Files produced

- `.gzkit/chores/control-surface-rule-vs-check-drift/proofs/promoted-inventory.md`
- `.gzkit/chores/control-surface-rule-vs-check-drift/proofs/prose-assertions.md`
- `.gzkit/chores/control-surface-rule-vs-check-drift/proofs/check-behaviors.md`
- `.gzkit/chores/control-surface-rule-vs-check-drift/proofs/parity-diff.md`
- `.gzkit/chores/control-surface-rule-vs-check-drift/proofs/summary.md` (this file)
- `.gzkit/chores/control-surface-rule-vs-check-drift/proofs/validate-help.txt` (evidence)
