---
id: ADR-0.0.23-agent-failure-mode-taxonomy
status: Validated
kind: foundation
semver: 0.0.23
lane: lite
parent:
date: 2026-04-25
---

# ADR-0.0.23-agent-failure-mode-taxonomy: Agent Failure-Mode Taxonomy

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
This ADR is rule and doctrine work; the work is the work, not theater for an
unseen reviewer.

## Intent

Codify a six-pattern taxonomy of agent failure modes — drawn from the Claude
Opus 4.7 system card (Anthropic, 2026-04-16, § 2.3.6) and corroborated by the
GPT-5.5 system card (OpenAI, 2026-04-23, § 9.2 Apollo evaluations) — as a
named, citable rule under `.gzkit/rules/`. The taxonomy gives reviewers,
auditors, and rule-authors a shared vocabulary for the recurring failure
shapes the AGENTS.md § DO IT RIGHT invariants are engineered against. Without
a named taxonomy, each new rule re-invents the failure shape it backstops,
and `gz validate --advisory-scorecard` cannot score new rules against a
canonical catalogue.

The six patterns: `Safeguard circumvention`, `Reckless action`, `Fabrication`,
`Skipped cheap verification`, `Correction fails`, `Dishonest when caught`.

## Decision

1. Author `.gzkit/rules/agent-failure-modes.md` enumerating the six patterns
   with: definition, canonical Opus 4.7 / GPT-5.5 citation, the gzkit
   invariant that backstops each pattern (6a / 6c / 6g / 6h / ARB receipts /
   `validate --commit-trailers`), and a worked example from gzkit history
   where available.
2. Cross-link the new rule from `AGENTS.md` § DO IT RIGHT (one-line pointer)
   and from `docs/governance/advisory-rules-audit.md` (scorecard entry).
3. Sync vendor mirrors via `gz agent sync control-surfaces`.
4. Operationalize the `Safeguard circumvention` failure shape (filing
   gzkit-surface defects at the wrong tracker) by authoring a
   cross-repo filing doctrine subsection in `.gzkit/rules/gh-cli.md` and
   shipping a `gz issue file` wrapper with provenance auto-stamp. This
   item lifts the ADR's overall lane from lite to heavy because the
   wrapper introduces a new CLI verb (heavy-lane trigger per
   `.gzkit/rules/cli.md`); brief-level Gate 5 still applies across all
   five items per the foundation-kind × lane matrix.
5. Operationalize the `Skipped cheap verification` failure shape
   (cosmetic `@covers(REQ-...)` decorator backfill that silences
   `gz adr audit-check` without re-deriving the assertion from REQ
   semantics) by adding a temporal heuristic to `gz adr audit-check`:
   flag any `@covers` decorator added in the same commit as (or within
   N commits / D days of) the closing receipt for that REQ. Thresholds
   exposed via `data/audit_thresholds.json`; warning by default, fail-
   closed under `--strict` and on heavy/foundation lanes. The change is
   additive validator scope inside an existing CLI verb, so it lands
   inside the heavy envelope already established by item 4 without a
   further lane lift. Closes GHI #309.

## Consequences

### Positive

- Reviewers gain a shared vocabulary for naming the failure shape of a
  flagged change (e.g., "this is `Skipped cheap verification` shape").
- New rules can be scored against the catalogue rather than re-deriving
  the failure motivation each time.
- External-evidence links keep the rationale anchored to observable model
  behavior, not internal narrative.

### Negative

- One additional always-loaded rule under `.claude/rules/` — small context
  cost. Mitigated by keeping the rule terse (definition + citation + back-
  stop pointer per pattern, no expansion).
- Risk that the taxonomy ossifies as model behavior shifts. Mitigated by
  treating the rule as living: future system cards may rename or extend
  patterns; revisions land under follow-up GHIs.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 0
- Dimension Total: 7
- Baseline Range: 4-5
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.23-01: Author `.gzkit/rules/agent-failure-modes.md` with the six patterns, citations, and backstop pointers
- [ ] OBPI-0.0.23-02: Cross-link from AGENTS.md § DO IT RIGHT and add scorecard entry to `docs/governance/advisory-rules-audit.md`
- [ ] OBPI-0.0.23-03: Sync vendor mirrors and verify the rule loads correctly under each agent harness
- [ ] OBPI-0.0.23-04: Operationalize `Safeguard circumvention` shape — author cross-repo filing doctrine subsection in `.gzkit/rules/gh-cli.md` and ship `gz issue file` wrapper with provenance auto-stamp (closes GHI #316)
- [ ] OBPI-0.0.23-05: Operationalize `Skipped cheap verification` shape — add same-commit-window `@covers` backfill heuristic to `gz adr audit-check` with `data/audit_thresholds.json` thresholds; warn by default, fail-closed under `--strict` and on heavy/foundation lanes (closes GHI #309)

## Q&A Transcript

Authored from a system-card review session (2026-04-25) comparing
GPT-5.5 (OpenAI) and Claude Opus 4.7 (Anthropic). Both cards converge on the
thesis that agent-trust without mechanical backstops is the dominant failure
mode at the current capability frontier, and Opus 4.7 § 2.3.6 supplies the
six-pattern taxonomy this ADR codifies.

## Evidence

- [ ] Rule: `.gzkit/rules/agent-failure-modes.md`
- [ ] Cross-link: `AGENTS.md` § DO IT RIGHT
- [ ] Scorecard: `docs/governance/advisory-rules-audit.md`
- [ ] Mirrors: `.claude/rules/agent-failure-modes.md`, `.github/instructions/agent-failure-modes.md`
- [ ] Doctrine subsection: `.gzkit/rules/gh-cli.md` § Cross-repo filing
- [ ] Wrapper: `gz issue file` CLI verb with provenance auto-stamp + manpage + BDD scenario
- [ ] Validator scope: `gz adr audit-check` same-commit-window `@covers` backfill heuristic
- [ ] Thresholds: `data/audit_thresholds.json` `max_covers_backfill_commits` and `max_covers_backfill_days` keys

## Alternatives Considered

1. **Embed the taxonomy inline in AGENTS.md** — rejected. AGENTS.md is the
   universal contract; adding a six-pattern taxonomy bloats the always-loaded
   surface. A separate rule loads contextually.
2. **Author as a docs-only page under `docs/governance/`** — rejected. Without
   the `.gzkit/rules/` placement, the rule does not get vendor-mirror-synced
   and is invisible to agent harnesses that read from `.claude/rules/` or
   `.github/instructions/`.
3. **Defer until a third independent source exists** — rejected. Two
   independent frontier-lab system cards converging on the same taxonomy is
   sufficient external evidence; deferring loses the immediate value of
   shared review vocabulary.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.23 | Completed | g0 | 2026-05-02 | Completed — six-pattern agent-failure-mode taxonomy codified at .gzkit/rules/agent-failure-modes.md, cross-linked from AGENTS.md, mirrored to .claude/rules and .github/instructions (OBPIs 01-03), cross-repo defect-filing wrapper shipped (OBPI-04, closes GHI #316), and gz adr audit-check covers-backfill temporal heuristic operationalized (OBPI-05, closes GHI #309); evidence: arb-ruff-f088e45f391549bfa3a613107bf4955a, arb-step-typecheck-7fee09e7fa214252a771f6502982ceab, arb-step-unittest-582a9b60dd534981a313e80df9ad4094 (3959 tests, 2 skipped), arb-step-mkdocs-52f743db38524cb38db01249f5ae247b |
