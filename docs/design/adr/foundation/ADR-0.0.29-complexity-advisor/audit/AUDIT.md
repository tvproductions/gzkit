# Audit: ADR-0.0.29-complexity-advisor

- ADR: `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- Generated: 2026-05-09
- Audit driver: `gz-adr-audit` skill (Layer-2 ledger consumption + Step-3 value demonstration)
- Lifecycle transition: Completed -> Validated (audit_receipt_emitted 2026-05-09T15:42:20Z)

## Feature Demonstration (Step 3 — MANDATORY)

ADR-0.0.29 delivers a trigger-time complexity advisor that replaces opaque numeric verdicts (`CC=14`)
with a doctrinal-frame diagnosis: `(authority, refactor archetype, proof range, recommended move)`. The
demos below exercise the capability against real Python source — not `--help` placeholders. GHI #427
(2026-05-09) explicitly named the `--help`-only walkthrough as the anti-pattern this section refuses to
repeat.

### Capability 1: Clean file produces exit 0 with no crossings (REQ-0.0.29-03-01)

```bash
$ uv run gz complexity advise /tmp/demo_clean.py
No crossings detected. Checked 1 metrics across 2 functions.
EXIT: 0
```

**Why it matters:** Default-path success returns operator attention to the commit flow without noise. A
quiet pass is the load-bearing case — the advisor must not hallucinate diagnoses on healthy code.

Proof: `audit/proofs/demo_01_clean.txt`.

### Capability 2: Warn-band crossing emits doctrinal-frame diagnosis at exit 0 (REQ-0.0.29-03-02)

```bash
$ uv run gz complexity advise /tmp/demo_warn.py
Metric: radon_cc | Band: warn | Value: 8.0 | Archetype: arrowhead
Authority: martin
Citation: Clean Code, ch. 7 — Boundary Conditions
Excerpt: Deeply nested control flow signals missing guard clauses; collapse the
arrowhead with early returns and extracted predicates.
Recommended: When branch count rises, I usually suspect hidden policy logic, mode
handling, or too many cases in one function. First move: extract decision policy or
split paths by responsibility. ...
File: /tmp/demo_warn.py (lines 1-19, FunctionDef)
def classify(x, y, z, mode):
    ...
EXIT: 0
```

**Why it matters:** The operator gets a named archetype (`arrowhead`), the binding authority (`martin`
/ Clean Code ch. 7), the rule excerpt, the recommended move, and the AST proof range — precisely the
trigger-time doctrinal frame the ADR's Decision § Rationale #1 / #5 mandates. This is the canonical
training-corpus failure-mode (number-without-frame) closed at the response layer.

Proof: `audit/proofs/demo_02_warn.txt`.

### Capability 3: Block-band crossing fails closed at exit 3 (REQ-0.0.29-03-03)

```bash
$ uv run gz complexity advise /tmp/demo_block.py
Metric: radon_cc | Band: block | Value: 14.0 | Archetype: arrowhead
Authority: martin
Citation: Clean Code, ch. 7 — Boundary Conditions
...
$ echo "EXIT: $?"
EXIT: 3
```

**Why it matters:** Exit-code 3 is the policy-breach signal in the four-code CLI exit map, propagating
correctly to the auto-chain hook (OBPI-05) and any pre-commit invocation. The pattern lets the gate
fail closed on block-band code without losing the diagnostic surface.

Proof: `audit/proofs/demo_03_block.txt` (exit 3 confirmed via direct invocation: `EXIT: 3`).

### Capability 4: --json mode emits canonical Pydantic serialization (REQ-0.0.29-03-04)

```bash
$ uv run gz complexity advise /tmp/demo_warn.py --json
[
  {
    "archetype": "arrowhead",
    "crossing_band": "warn",
    "crossing_value": 8.0,
    "doctrinal_frame": {
      "authority": "martin",
      "citation": "Clean Code, ch. 7 — Boundary Conditions",
      ...
    },
    "intrinsic_attestation": null,
    "metric": "radon_cc",
    "proof": [
      {"ast_node_kind": "FunctionDef", "end_line": 19, "file_path": "/tmp/demo_warn.py", "start_line": 1},
      ...
    ]
  }
]
```

**Why it matters:** Machine-parseable output is what downstream consumers (xenon-as-gate strengthening,
the future ADR-0.0.30 authoring-guidance integration) need. Every diagnosis carries non-empty `proof:
tuple[ProofRange, ...]` per OBPI-08's verdict-proof binding invariant.

Proof: `audit/proofs/demo_04_json.txt`.

### Capability 5: CLI surface fully wired across manpage, runbook, and index (REQ-0.0.29-03-07)

```bash
$ uv run gz cli audit
Cross-coverage: 93/93 commands fully covered.
EXIT: 0

$ uv run gz validate --advisor-proof-binding
Validated: advisor_proof_binding
✓ All validations passed (1 scopes).
EXIT: 0

$ uv run gz covers OBPI-0.0.29-03 --json
... "covered_reqs": 7, "uncovered_reqs": 0, "coverage_percent": 100.0 ...
```

**Why it matters:** The ADR's Heavy-lane subcommand discipline (manpage + runbook + index parity per
`.claude/rules/cli.md`) is mechanically enforced, not narrated. The proof-binding validator (OBPI-08)
backstops the model-layer + engine-layer guarantees with a third defense at gate time. REQ coverage
parity is 7/7 with REQ-derived tests — no cosmetic backfill.

Proof: `audit/proofs/demo_06_cli_audit.txt`, `demo_07_proof_binding.txt`, `demo_08_req_coverage.txt`.

### Value Summary

Before ADR-0.0.29: when xenon flagged a function the operator received `CC=14` and had to reach for
training-memory pattern-matching (the named anti-vibing failure mode) to act. After ADR-0.0.29: the
same crossing produces `(arrowhead, martin / Clean Code ch. 7, AST lines 1-19, "extract decision
policy or split paths by responsibility")` — a structured doctrinal frame that the operator can audit
at trigger time. The advisor is auto-chainable from xenon-as-gate failure (OBPI-05), operator-
invocable ad-hoc for preview (OBPI-06), and never blocks indefinitely (OBPI-09's 30s timeout fail-
open). The verdict-proof binding (OBPI-08) closes "plausible-looking advice without traceable
evidence" — the same training-corpus failure mode AGENTS.md § Attestation forbids at the receipt
layer, applied at the diagnosis layer.

---

## Attestation Record
- Attestor: g0
- Status: completed
- Timestamp: 2026-05-09T15:31:00.888024+00:00

## Gate Results (from ledger)
| Gate | Status | Command | Return Code |
|------|--------|---------|-------------|
| 2 | fail | `uv run gz test` | 1 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `uv run gz lint` | 0 |
| 2 | pass | `uv run gz typecheck` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `uv run gz lint` | 0 |
| 2 | pass | `uv run gz typecheck` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |

## OBPI Completion Summary
| OBPI | Receipt Event | Completed |
|------|---------------|-----------|
| OBPI-0.0.29-01-advisor-diagnosis-schema | completed | Yes |
| OBPI-0.0.29-02-diagnosis-engine | completed | Yes |
| OBPI-0.0.29-03-complexity-advise-cli | completed | Yes |
| OBPI-0.0.29-04-complexity-advisor-skill | completed | Yes |
| OBPI-0.0.29-05-auto-chain-hook | completed | Yes |
| OBPI-0.0.29-06-ad-hoc-path | completed | Yes |
| OBPI-0.0.29-07-intrinsic-complexity-attestation | completed | Yes |
| OBPI-0.0.29-08-verdict-proof-binding | completed | Yes |
| OBPI-0.0.29-09-advisor-timeout-fallback | completed | Yes |

## Verification Results
- **test**: PASS (`uv run gz test`) -> `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/audit/proofs/test.txt`
- **lint**: PASS (`uv run gz lint`) -> `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/audit/proofs/lint.txt`
- **typecheck**: PASS (`uv run gz typecheck`) -> `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/audit/proofs/docs.txt`
- **demo (clean file)**: PASS (`uv run gz complexity advise /tmp/demo_clean.py`, exit 0) -> `audit/proofs/demo_01_clean.txt`
- **demo (warn-band crossing)**: PASS (`uv run gz complexity advise /tmp/demo_warn.py`, exit 0 + diagnosis) -> `audit/proofs/demo_02_warn.txt`
- **demo (block-band crossing)**: PASS (`uv run gz complexity advise /tmp/demo_block.py`, exit 3) -> `audit/proofs/demo_03_block.txt`
- **demo (--json mode)**: PASS (`uv run gz complexity advise /tmp/demo_warn.py --json`) -> `audit/proofs/demo_04_json.txt`
- **demo (--help)**: PASS (`uv run gz complexity advise --help`, exit 0) -> `audit/proofs/demo_05_help.txt`
- **demo (cli audit parity)**: PASS (93/93 commands covered) -> `audit/proofs/demo_06_cli_audit.txt`
- **demo (proof-binding validator)**: PASS (1 scope clean) -> `audit/proofs/demo_07_proof_binding.txt`
- **demo (REQ coverage parity)**: PASS (7/7 REQs covered for OBPI-0.0.29-03) -> `audit/proofs/demo_08_req_coverage.txt`

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | PASS — 9/9 OBPIs attested_completed; 55/55 REQs covered |
| Doctrinal-Frame Binding (OBPI-02) | PASS — diagnosis emits archetype + authority + citation + recommendation on warn/block crossings |
| Verdict-Proof Binding (OBPI-08) | PASS — every diagnosis carries non-empty `proof: tuple[ProofRange, ...]`; validator clean |
| Exit-Code Map (OBPI-03) | PASS — exit 0 (no crossings or warn), exit 3 (block-band) verified end-to-end |
| --json Serialization (OBPI-03) | PASS — Pydantic round-trip; schema-valid output |
| CLI Surface Wiring (OBPI-03) | PASS — `gz cli audit` 93/93 covered (manpage + runbook + index) |
| Documentation Alignment | PASS — `mkdocs build --strict` clean; manpage authored; runbook entry present |
| Cosmetic-Backfill Discipline | PASS (post-remediation) — 3 covers-backfill findings removed; audit-check zero-flag |
| Risk Items Resolved | PASS — GHI #427 (closed) ceremony walkthrough fix landed; no outstanding tracked defects on this ADR |

## Shortfalls & Remediation

| # | Finding | Severity | Remediation | State |
|---|---------|----------|-------------|-------|
| 1 | `gz adr audit-check ADR-0.0.29` initially reported 3 covers-backfill findings on `tests/test_ceremony_demo_discovery.py:308`, `:335`, `:366` — all decorated with `@covers("REQ-0.0.29-03-01")`. The tests assert `_commands_from_demo_sections` semantics (closeout ceremony walkthrough discovery) under GHI #427's class-of-fix, NOT REQ-0.0.29-03-01's clean-file-exit-zero semantics. This is the cosmetic-backfill anti-pattern named in `.claude/rules/tests.md` § Invariant 6f and the audit SKILL.md Step 2: backfilling `@covers` to silence audit-check while leaving the semantic gap intact. | Blocking | Removed the three cosmetic decorators (tests retain their GHI #427 docstring binding; legitimate REQ-0.0.29-03-01 coverage remains at `tests/commands/test_complexity_advise.py:220` + `:318` + behave scenario). Re-ran `gz audit ADR-0.0.29` → ledger refreshed; `gz adr audit-check` → PASS clean (55/55 REQs covered; zero covers-backfill findings). | Resolved |

## Evidence Links
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-01-advisor-diagnosis-schema.md`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-02-diagnosis-engine.md`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-03-complexity-advise-cli.md`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-04-complexity-advisor-skill.md`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-05-auto-chain-hook.md`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-06-ad-hoc-path.md`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-07-intrinsic-complexity-attestation.md`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-08-verdict-proof-binding.md`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-09-advisor-timeout-fallback.md`
