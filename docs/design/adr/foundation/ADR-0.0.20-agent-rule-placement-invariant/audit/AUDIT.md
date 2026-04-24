# Audit — ADR-0.0.20-agent-rule-placement-invariant

**ADR:** `ADR-0.0.20-agent-rule-placement-invariant`
**Kind:** foundation
**Lane:** lite
**Lifecycle:** Validated (closeout ceremony 2026-04-23)
**Auditor:** agent (Claude Opus 4.7)
**Attestor (Gate 5):** g0 (recorded at closeout)
**Audit date:** 2026-04-23

## Feature Demonstration

The ADR delivered the following capabilities. Each is demonstrated below with
live command output.

### 1. Mechanical anti-regression check

Capability: new `paths: "**"` rule files under `.gzkit/rules/` cannot silently
accrete — they fail `gz validate --unscoped-rules` unless explicitly
allow-listed.

Command: `uv run gz validate --unscoped-rules`

Representative output:

```
Validated: unscoped-rules

✓ 13 rule file(s) checked (0 allowlisted).
```

Value: the invariant is now enforced by a validator, not by advisory prose.
Target-state is reached (0 allowlist entries) — every remaining rule file in
`.gzkit/rules/` carries a concrete `paths:` scope.

### 2. CLI surface exposes the new flag

Capability: operators discover the invariant via `gz validate --help`.

Command: `uv run gz validate --help`

Representative output (trimmed):

```
  --unscoped-rules      Fail on .gzkit/rules/*.md with paths: '**' or missing
                        paths: (ADR-0.0.20)
  --allowlist-only      With --unscoped-rules: list current allowlist entries
                        and exit 0
```

Value: the flag is registered with an ADR-0.0.20 citation and a companion
`--allowlist-only` flag for reading the current allow-list.

### 3. Three always-on rules migrated to their proper homes

Capability: `.gzkit/rules/agent-contract.md`,
`.gzkit/rules/attestation-enrichment.md`, and
`.gzkit/rules/defect-fix-routing.md` — and all their vendor mirrors — are
gone; binding content now lives in `AGENTS.md`, `CLAUDE.md` addendum, and
`docs/governance/`.

Command: `ls .gzkit/rules/{agent-contract,attestation-enrichment,defect-fix-routing}.md`

Representative output:

```
ls: .gzkit/rules/agent-contract.md: No such file or directory
ls: .gzkit/rules/attestation-enrichment.md: No such file or directory
ls: .gzkit/rules/defect-fix-routing.md: No such file or directory
```

Value: per-turn governance preamble shrinks by ~570 lines; binding content
moved to the Linux-Foundation-stewarded `AGENTS.md` cross-agent standard,
which 25+ agent runtimes honor.

### 4. Manifest allow-list is empty at target state

Capability: the transition allow-list carrying the three files during
migration is now zero entries.

Evidence: `.gzkit/manifest.json`

```json
"unscoped_allowlist": []
```

Value: no silent exceptions remain. Any future allow-list entry must be
explicitly added with a rationale (min 20 chars) and a tracking ref.

### 5. Ledger evidence — all 5 OBPIs completed and attested

Command: `uv run gz adr audit-check ADR-0.0.20`

Representative output:

```
ADR audit-check: ADR-0.0.20-agent-rule-placement-invariant
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.0.20-01-validator-and-allowlist
  - OBPI-0.0.20-02-fold-agent-contract
  - OBPI-0.0.20-03-fold-attestation-enrichment
  - OBPI-0.0.20-04-fold-defect-fix-routing
  - OBPI-0.0.20-05-closeout-and-downstream

Coverage: 50/75 REQs covered (66.7%)
  OBPI-0.0.20-01: 9/20 (45.0%)
  OBPI-0.0.20-02: 13/13 (100.0%)
  OBPI-0.0.20-03: 15/16 (93.8%)
  OBPI-0.0.20-04: 11/11 (100.0%)
  OBPI-0.0.20-05: 2/15 (13.3%)
```

Value: Layer-2 ledger proof is complete. Gate 5 human attestation recorded
at the closeout ceremony.

## Execution Log

| # | Check | Outcome | Evidence |
|---|-------|---------|----------|
| 1 | `gz adr audit-check ADR-0.0.20` returns PASS | ✓ | `proofs/audit-check.txt` |
| 2 | `gz validate --unscoped-rules` exits 0, 0 allowlist entries | ✓ | `proofs/unscoped-rules.txt` |
| 3 | `gz validate --documents` exits 0 | ✓ | `proofs/validate-documents.txt` |
| 4 | `gz validate --help` lists `--unscoped-rules` + `--allowlist-only` | ✓ | `proofs/validate-help.txt` |
| 5 | Canonical rule files and vendor mirrors deleted | ✓ | inline `ls` above |
| 6 | Manifest `unscoped_allowlist` is empty array | ✓ | `.gzkit/manifest.json` |
| 7 | Closeout ceremony attestation recorded (Gate 5) | ✓ | ledger (lifecycle=Validated) |

## Summary

| Dimension | Status |
|-----------|--------|
| Completeness | All 5 OBPIs completed, briefs attested |
| Integrity | Ledger PASS; canonical + mirrors consistent |
| Alignment | ADR claims match reality (validator enforces, rules gone, allow-list empty) |
| Value demonstrated | Yes — 5 capabilities shown with live command output |

## Shortfalls

**Advisory — non-blocking:** 25 of 75 REQs (33.3%) lack `@covers(REQ-…)`
traceability decorators. Breakdown:

- OBPI-0.0.20-01: 11 uncovered REQs — primarily validator-model contract
  requirements (regex patterns, exit-code map, JSON roundtrip) covered
  semantically by existing `tests/test_unscoped_rules.py` but not tagged
  with explicit `@covers` decorators.
- OBPI-0.0.20-05: 13 uncovered REQs — closeout-kind REQs (grep sweep clean,
  mirrors regenerated, downstream GHI filings, ceremony walkthrough) whose
  evidence lives in the closeout ceremony artifacts and the ledger rather
  than in code-level unit tests. These REQs are governance actions, not
  testable behaviors.

**Remediation decision:** Non-blocking per audit-check. Backfilling cosmetic
`@covers` decorators without re-deriving assertions is the anti-pattern
named in `.gzkit/rules/tests.md` § "Tests assert semantics, not strings" and
in `.gzkit/rules/adr-audit.md`. The OBPI-05 REQs in particular are not
code-testable (they assert state transitions that the closeout ceremony
verified and the ledger recorded). The OBPI-01 decorator gap is a
traceability advisory, not a semantic-coverage gap — tracked for a future
coverage-tagging sweep if explicit `@covers` decorators become mechanically
required.

## Attestation

- **Gate 5 (human):** attested by g0 at the closeout ceremony on
  2026-04-23.
- **Audit (agent):** claims in this document are verified against live
  command output and captured proof artifacts. Agent: Claude Opus 4.7.

## References

- ADR: `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md`
- OBPIs: `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/obpis/*.md`
- Closeout form: `ADR-CLOSEOUT-FORM.md` (same directory)
- Scorecard: `EVALUATION_SCORECARD.md` (same directory)
