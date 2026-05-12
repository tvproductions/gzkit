---
id: ADR-pool.agentic-security-review
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: anthropic-agentic-coding-trends-2026
---

# ADR-pool.agentic-security-review: Agentic Security Review Pipeline

## Status

Pool

## Date

2026-03-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add automated security scanning to gzkit's gate verification pipeline so that
agent-generated code is checked for common vulnerability patterns before human
attestation. AI coding agents produce code at high velocity, which amplifies
both productivity and the risk of introducing security issues — hardcoded
secrets, SQL injection, path traversal, insecure deserialization, and overly
permissive file operations. Currently, gzkit's gates verify intent alignment,
test coverage, and documentation but have no security dimension.

---

## Target Scope

- Integrate static security analysis (bandit for Python, semgrep for polyglot) as a gate check in `gz check`.
- Define a security findings schema for the `.gzkit/` ledger (finding ID, severity, file, line, rule, suppression status).
- Add `gz security [--fix] [--baseline]` CLI surface for running scans, reviewing findings, and managing baseline suppressions.
- Define severity thresholds: critical/high findings block gate passage; medium/low are advisory.
- Add a `security-review` chore template for periodic full-codebase scans beyond per-commit checks.
- Integrate with pre-commit hooks for incremental scanning on changed files only.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No runtime security monitoring (this is static analysis only).
- No dependency vulnerability scanning (that is a separate concern — consider `pip-audit` or similar).
- No custom rule authoring in v1 — use upstream rulesets.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.release-hardening (security scanning is a release gate), ADR-pool.audit-system (security findings feed audit)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Scanner toolchain is accepted (bandit, semgrep, or alternatives).
3. Severity threshold and suppression model are agreed upon.

---

## Inspired By

[Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) — Trend 8: Security Dual-Use.
The report highlights that AI agents are both a security asset (finding
vulnerabilities faster) and a security risk (generating vulnerable code at
scale). Organizations that integrate security scanning into their agent
workflows catch issues earlier. GovZero's gate model is the natural integration
point — security becomes a gate dimension alongside intent, tests, and docs.

---

## Notes

- AirlineOps has `ruff` for style and `ty` for types but no security scanner in the pre-commit chain.
- bandit is stdlib-friendly and Python-native; semgrep adds polyglot rules but requires a registry.
- Key design tension: scan speed vs. coverage. Pre-commit needs to be fast; full scans can be periodic chores.
- Consider: should security findings have their own ledger file or share `agent-insights.jsonl`?
- Consider: integration with GitHub Advanced Security for projects hosted on GitHub.

### Promotion-time design tension: canonical-surface migration catch-22 (GHI #455)

Surfaced during OBPI-0.0.32-03-rules-physical-migration Stage 5 (2026-05-11).
When a foundation OBPI migrates the on-disk location of source code listed in
`data/security_surfaces.json`, the registry becomes stale relative to the
post-migration tree. Once the auto-detect security floor (GHI #413) is active
and the security-scan canonical slot is filled by this ADR's promotion, the
following four-step catch-22 fires on the migrating brief itself:

1. `detect_brief_security_floor` matches the pre-migration glob against the
   brief's `## Allowed Paths` (necessarily — the migrating file is in scope)
   → `effective_sensitivity = security`.
2. `_run_security_gate` requires the security-scan canonical slot to be
   filled → fail-closed until this pool ADR is promoted and slot wired.
3. The registry edit that would resolve (1) requires `sensitivity: security`
   on the editing brief per `.gzkit/rules/security-sensitivity.md`
   § Registry contract.
4. Declaring `sensitivity: security` on the editing brief re-triggers (2).

Operator resolution in flight: AGENTS.md § 1a coupled-surface coherence —
the registry edit was treated as coherent with the migration and applied
inline; `src/gzkit/rules.py` was removed from
`data/security_surfaces.json` `deserialization_user_input` in commit
`b1bb69ae`. The class-of-failure pattern is recorded here for the
promotion ADR to design against. Promotion must choose one of:

- **(a) Self-migrating-path exemption**: when a brief's only registry
  overlap is a path the brief itself migrates, the auto-detect floor
  treats the overlap as transient (exempt).
- **(b) Coupled registry-edit allowance**: a migrating brief may edit the
  registry to track its own move without inheriting `sensitivity: security`,
  bounded to paths the brief touches.
- **(c) Slot-first ordering**: the security-scan canonical slot is filled
  before any sensitive-surface migration becomes possible, eliminating
  fail-closed step (2) at the cost of pushing pool promotion ahead of
  any further canonical-surface OBPIs.

This is a Stage-2 promotion-criteria design question, not a v1 implementation
detail. Recorded here so the promotion-time author has the prior art.
