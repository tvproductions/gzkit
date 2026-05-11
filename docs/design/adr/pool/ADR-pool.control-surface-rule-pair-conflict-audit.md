---
id: ADR-pool.control-surface-rule-pair-conflict-audit
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.control-surface-rule-pair-conflict-audit: Control-Surface Rule-Pair Conflict Audit

## Status

Pool

## Date

2026-05-10

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Codify the methodology and evidence bar for the `control-surface-rule-conflicts`
chore (`.gzkit/chores/control-surface-rule-conflicts/`) so its three proof
artifacts (`rule-inventory.md`, `conflict-matrix.md`, `summary.md`) cannot pass
acceptance with placeholder rows. The chore's stated scope — 21 rule files,
210 unordered pairs — and its CHORE.md prohibition on speculation
("No 'these could maybe conflict' entries") are real, but the acceptance
predicate is purely file-existence (`test -f`). Without a codified evidence
bar this audit is acceptance-passable with thin proofs, which would reproduce
the exact stochastic-vibing failure the anti-vibing mantra exists to close.

This pool ADR is the **design home** for the audit, not its execution vehicle.
The chore is the executable surface; this ADR records the methodology decision
that the chore's `CHORE.md` defers to.

Sibling to `ADR-pool.contract-surface-mechanical-defenses` — that ADR closes
the **accretion** class (doctrine growing without mechanical enforcement); this
ADR closes the **internal consistency** class (rules that disagree mechanically
when composed). Both surface as agent vibing, but the failure mechanisms are
orthogonal and the deliverables don't overlap.

## Decision

### Evidence bar — observed-hit only

A row in `conflict-matrix.md` requires one of:

- A filed GHI (`gh issue view <N>` resolves) where an agent or operator
  surfaced the conflict in the path of work.
- A commit SHA (`git log <SHA>`) where the conflict was reconciled informally
  (the commit's message names both rules and the resolution).
- An entry in `.gzkit/insights/agent-insights.jsonl` (`improvement` record)
  where a course-correction made the conflict explicit.
- An operator-attested session reference (rare; requires the operator's name
  + date + a paraphrased description recoverable from session orientation).

Pairs without observed-hit evidence default to `theoretical` and are
**excluded from the matrix**. The matrix is a registry of named failures,
not a registry of imagined possibilities. This is the anti-vibing mantra
applied to audit methodology: the matrix's authority comes from each row
being grounded in real-world friction, not from comprehensive coverage of
the 210 pair-space.

### Severity classification

`CHORE.md` defines three severities (`blocking`, `episodic`, `theoretical`).
The observed-hit bar collapses these into two operational categories:

| Severity | Evidence shape | Action |
|----------|----------------|--------|
| `blocking` | Two or more observed hits across distinct sessions / ADRs | Spawn direct-fix GHI against the rule pair (the lower-numbered rule wins authorship; reconcile in one rule, split scope, or promote to mechanical check per AGENTS.md § Defect-fix routing) |
| `episodic` | Single observed hit | Document in the matrix; defer reconciliation until a second hit lands or operator judgment escalates |

`theoretical` rows are not authored — they're the empty quadrant. If a
pair earns a hit later, it enters the matrix at `episodic` severity.

### Audit-row schema (mechanical, evidence-resolvable)

Each row in `conflict-matrix.md` has these columns; an audit pass over the
matrix can mechanically verify the evidence column resolves:

| Column | Resolution |
|--------|------------|
| Rule A path + § anchor | `test -f .gzkit/rules/<file>` AND grep for § anchor |
| Rule B path + § anchor | same |
| Worked example | Prose paraphrase, ≤3 sentences, names the artifact type |
| Evidence (observed-hit) | `gh issue view <N>` exits 0, OR `git log -1 <SHA>` exits 0, OR `grep <id> .gzkit/insights/agent-insights.jsonl` returns ≥1 line |
| Mechanical winner today | One of: `<rule A>`, `<rule B>`, `unresolved` |
| Suggested resolution | One of: `reconcile-in-A`, `reconcile-in-B`, `split-scope`, `promote-mechanical-check` |
| Severity | One of: `blocking`, `episodic` |

### Promotion: pool is terminal

This ADR records the methodology, not a deliverable that ships through the
pre-release/foundation series. Pool is the permanent home. Chore execution
happens under the pool umbrella. Blocking rows route to direct-fix GHIs filed
against the *cited rule pair*, never against this ADR.

## Alternatives Considered

**A. Mechanical-validator framing — propose `gz validate --rule-pair-coherence`.**
Rejected. The validator would either parse the matrix file (turning it into
ledger of truth, violating Layer 1 / Layer 2 boundaries per
`docs/governance/state-doctrine.md`) or re-derive conflicts from the rule
files at runtime (the speculation pattern the chore exists to prevent).
Neither is a sharp single-predicate check. If a validator emerges later, it
belongs in `ADR-pool.contract-surface-mechanical-defenses`'s queued-children
space, not here.

**B. Authoring-doctrine framing — codify rule-frontmatter discipline
(scope, mechanical-anchor, conflict-allies).** Rejected. Addresses the
upstream cause but requires retrofitting all 20 rule files plus AGENTS.md +
CLAUDE.md. Worth doing eventually; not the right pool-ADR scope for the chore
that already exists at audit-only Lite lane. Belongs in a separate pool ADR
if the audit matrix surfaces enough conflicts to justify the doctrine work.

**C. Combined umbrella with three children for promotion.** Rejected. Mirrors
`ADR-pool.contract-surface-mechanical-defenses` shape, but the audit
deliverable is a one-shot artifact, not a continuing mechanical defense.
Bundling audit + validator + authoring doctrine into one umbrella conflates
three distinct decisions and inflates the plan-audit surface. Three sibling
pool ADRs (this one for audit, `contract-surface-mechanical-defenses` for
accretion, hypothetical future ADR for authoring doctrine) keep the scopes
sharp.

**D. Single-promotion to a Lite foundation ADR.** Rejected. Promotion to
foundation buys mechanical gates (Gate 2 tests, Gate 3 docs) that don't
match audit-deliverable nature. The audit is a methodology + a one-shot
matrix file; foundation-ADR ceremony is overweight for that. Pool ADRs are
valid terminal homes per ADR-0.0.18 taxonomy doctrine when the design
conversation doesn't need to materialize as a versioned release event.

**E. Concrete-case evidence bar (construct counter-examples, no historical
hit required).** Rejected at the evidence-bar sub-decision. Admits
theoretical-but-real conflicts; matrix grows to 20–40 rows; many rows
become speculative no-hit reconstructions that the anti-vibing mantra
explicitly closes. Observed-hit-only keeps the matrix anchored to friction
the project has actually experienced.

## Notes

Surfaced by GHI #446 (the close action that drove this design dialogue).
The chore at `.gzkit/chores/control-surface-rule-conflicts/` predates this
ADR; the ADR codifies the methodology the chore defers to. Sibling ADR
`ADR-pool.contract-surface-mechanical-defenses` handles the accretion
class of contract-surface failure; this ADR handles the internal-consistency
class. They do not overlap and neither absorbs the other.

The canonical conflict example named in GHI #446 — `tests.md` § "Tests
assert semantics" vs `tool-skill-runbook-alignment.md` § Invariant 3 (pin-
to-string assertions on table markers) — will likely be the first row in
the matrix once the chore executes. It satisfies the observed-hit bar
(surfaced during OBPI-0.0.21 closeout work).

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
This ADR is intended as a permanent pool entry per § Promotion: pool is
terminal; the absence of promotion is the architectural decision, not a
deferral.
