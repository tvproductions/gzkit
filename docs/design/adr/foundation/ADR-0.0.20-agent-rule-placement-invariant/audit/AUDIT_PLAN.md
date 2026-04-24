# Audit Plan — ADR-0.0.20-agent-rule-placement-invariant

## Scope

Verify that ADR-0.0.20 delivered:

1. `uv run gz validate --unscoped-rules` lands as a passing mechanical check
   (Gate 2-level fail-closed on any `paths: "**"` or missing `paths:` rule
   under `.gzkit/rules/`).
2. The three always-on rule files (`agent-contract.md`,
   `attestation-enrichment.md`, `defect-fix-routing.md`) are removed from
   `.gzkit/rules/` and their binding content now lives in AGENTS.md /
   CLAUDE.md addendum / `docs/governance/*`.
3. The manifest allow-list shrinks from 3 transition entries to 0.
4. Vendor mirrors (`.claude/rules/`, `.github/instructions/`,
   `.agents/rules/`) regenerate cleanly without the three deleted rules.
5. Inbound references across live governance/skill/doc surfaces are
   rewritten to point at the new homes; Bucket-3 historical artifacts
   remain untouched.

## Checks

| # | Check | Evidence file |
|---|-------|---------------|
| 1 | `gz adr audit-check ADR-0.0.20` returns PASS with all 5 OBPIs evidenced | `proofs/audit-check.txt` |
| 2 | `gz validate --unscoped-rules` exits 0 with 0 allowlist entries | `proofs/unscoped-rules.txt` |
| 3 | `gz validate --documents` exits 0 | `proofs/validate-documents.txt` |
| 4 | `gz validate --help` lists `--unscoped-rules` and `--allowlist-only` flags | `proofs/validate-help.txt` |
| 5 | Closeout ceremony attestation captured in ledger | ledger (gz state) |

## Risk focus

- **Claim → reality drift:** The ADR claims "target state 0 allowlist entries"
  — verified by `gz validate --unscoped-rules` output "0 allowlisted".
- **Advisory-uncovered REQs:** 25 of 75 REQs carry no `@covers` test decorator.
  These are predominantly closeout/governance REQs (grep sweeps, GHI filings,
  ceremony walkthroughs) whose completion evidence lives in the ceremony
  artifacts and ledger, not in code-level unit tests. Audit-check treats them
  as non-blocking advisory.
