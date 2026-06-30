# AUDIT (Gate-5) — ADR-0.30.0

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.30.0-okf-documentation-knowledge-structure |
| ADR Title | OKF Documentation Knowledge Structure |
| ADR Dir | docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure |
| Audit Date | 2026-06-29 |
| Auditor(s) | g0 (operator) + Claude (pipeline-orchestrator); spec-reviewer + quality-reviewer dispatched as independent subagents |
| Trust Layer | Layer 2 — consumes ledger proof; bound fidelity gate re-runs the thesis |

## Feature Demonstration (Step 3 — Bound Fidelity Gate)

ADR-0.30.0 makes the CMS emit and maintain an **OKF-conformant semantic map**
over a documentation tracer slice (state doctrine, trust doctrine, agent-contract
rationale, active campaign) so agents can navigate general app-knowledge by typed
frontmatter, descriptions, and links — an **orientation layer, never an authority
layer**. The bound fidelity gate (`gz adr fidelity`) runs the thesis against the
running system.

### Capability 1: Generated bundle is OKF-conformant

```bash
$ uv run gz validate --okf-conformance
Validated: okf_conformance
✓ All validations passed (1 scopes).   # exit 0
```

**Why it matters:** every non-reserved concept doc carries parseable frontmatter
with a non-empty `type`; the validator is generated-bundle-only and never gates
authored source docs (Boundary Invariant 2).

### Capability 2: Idempotent generation over a read-only slice

```bash
$ uv run gz knowledge refresh -q   # run twice
run1=fe204fcc95bcb13fff3d4c0c3ebb3fff8c749854
run2=fe204fcc95bcb13fff3d4c0c3ebb3fff8c749854
IDEMPOTENT ✓
```

**Why it matters:** re-running yields a byte-identical bundle (no timestamps,
sorted keys/slugs); source docs are byte-unchanged. The bundle is a safe,
reproducible derived artifact.

### Capability 3: Navigable progressive-disclosure path

```bash
$ cat .gzkit/governance/knowledge/index.md   # (body)
- [active-campaign](./active-campaign.md)
- [agent-contract-rationale](./agent-contract-rationale.md)
- [content-boundary](./content-boundary.md)
- [state-doctrine](./state-doctrine.md)
- [trust-doctrine](./trust-doctrine.md)

$ grep "Canonical source" .gzkit/governance/knowledge/state-doctrine.md
Canonical source: [state-doctrine.md](../../../docs/governance/state-doctrine.md)   # resolves
```

**Why it matters:** an agent enters at `index.md`, follows a typed link to a
concept doc, then follows the back-edge to the canonical source — every hop
resolves. The OBPI-06 content-boundary doctrine is reachable, not orphaned.
(Both edges corrected during this audit — see Shortfalls.)

### Value Summary

An agent can now orient over gzkit's governance documentation by traversing a
typed, idempotently-generated OKF map instead of reading the whole corpus —
while the load-bearing fence guarantees that map is never read as governance
truth. Truth stays in canon (Layer 1) and the ledger (Layer 2).

## Bound Fidelity Gate (Step 3)

| Claim | Command | Expected | Observed | Result |
|-------|---------|:--------:|:--------:|:------:|
| Generated bundle is conformant | `gz validate --okf-conformance` | 0 | 0 | ✓ |
| Generator refreshes idempotently | `gz knowledge refresh --quiet` | 0 | 0 | ✓ |
| Fidelity block is parseable | `gz adr fidelity … --check` | 0 | 0 | ✓ |

**Summary: 3 pass, 0 fail.** The fidelity block was re-derived during this audit:
it previously carried a planning-time WEAK "not-yet-landed" proxy
(`gz validate --documents`) that no longer matched the now-landed surfaces. The
re-derived assertions exercise the actual OKF validator and generator.

## Execution Log

| Check | Command | Result | Notes |
|-------|---------|:------:|-------|
| Ledger completeness | `gz adr audit-check ADR-0.30.0 --json` | ✓ | passed=true; 6/6 OBPIs complete; 21/25 REQ covered (4 advisory = SUPPORT/STRUCTURAL-FENCE) — `proofs/audit-check.json` |
| Bound fidelity gate | `gz adr fidelity ADR-0.30.0` | ✓ | 3/3 (re-derived) — `proofs/fidelity.txt` |
| OKF conformance | `gz validate --okf-conformance` | ✓ | exit 0 — `proofs/okf-conformance.txt` |
| Bundle idempotency | `gz knowledge refresh` ×2 | ✓ | byte-identical (sha `fe204fc…`) |
| Heavy gates | `gz gates --adr ADR-0.30.0` | ✓ | Gates 1–4 PASS; Gate 5 = this ceremony — `proofs/gates.txt` |
| Governance/CLI audit | `gz cli audit` | ✓ | 114/114 commands covered — `proofs/cli-audit.txt` |
| Docs build | `mkdocs build --strict` | ✓ | clean — `proofs/mkdocs.txt` |
| Full unit suite | `gz arb step --name unittest …` | ✓ | 6660/6660 — receipt `arb-step-unittest-0e9117fa117648718c9daac04be7a3d1` |
| Lint | `gz arb ruff` | ✓ | `arb-ruff-e8e128da72244e54a3a1396d0f8b8891` |
| Typecheck | `gz arb typecheck` | ✓ | `arb-step-typecheck-9f52a1db563a4ef6be3fdee595f992fa` |
| Independent REQ trace | spec-reviewer subagent | ✓ | PASS — 25/25 coverage claims hold; fence verified; see below |
| Independent integration | quality-reviewer subagent | ✓* | CONCERNS → 2 seams found, fixed during audit; see Shortfalls |

## Independent Review (dispatched personas)

**spec-reviewer — VERDICT: PASS.** Traced all 25 REQs against briefs + covering
test bodies. No string-pinning / cosmetic-`@covers` drift on any BEHAVIOR REQ.
The 4 advisory-uncovered REQs (01-04, 03-04, 05-02 SUPPORT; 03-05
STRUCTURAL-FENCE) each carry a legitimate non-BEHAVIOR kind — none is a
mislabeled BEHAVIOR dodging a test. Independently verified the load-bearing
Boundary-Invariant-1 fence holds: no enforcement surface consumes OKF data as
evidence. Minor non-blocking observations: a few content-presence REQs in
OBPI-05/06 are over-labeled BEHAVIOR (adds proof, no gap); REQ-05-03 is a weak
substring test; one REQ-05-04 unit test shells a real subprocess (slow tier).

**quality-reviewer — VERDICT: CONCERNS (resolved).** Confirmed the
STRUCTURAL-FENCE is real (only the generator + CLI import `gzkit.knowledge`; the
conformance audit reads `type` solely for the bundle's own well-formedness) and
the `--okf-conformance` scope is correctly bounded (explicit tier, scans only
`.gzkit/`, recognizes by reserved files + `type`, never folder name). Found two
MAJOR navigation-graph seams (below). Code-quality baseline clean (sizes within
limits; the `frozen=True, extra="allow"` Pydantic departure is ADR-mandated and
documented; specific exception handling; cross-platform pathlib throughout).

## Shortfalls & Remediation

| # | Severity | Finding | Resolution |
|---|----------|---------|------------|
| 1 | Stale | Fidelity block carried a planning-time WEAK proxy not exercising the landed thesis | Re-derived to 3 assertions over the real OKF validator + generator. Fixed in audit (ADR doc). |
| 2 | Major | Concept-doc markdown back-edge was repo-root-relative (`docs/governance/…`) — dead from a file 3 levels deep in the bundle. Masked by a string-containment test (fixture used absolute paths). | Generator now emits a bundle-relative link via `os.path.relpath`; test re-derived to assert resolvability + portability. Fixed `b2214ece`. |
| 3 | Major | OBPI-06 `content-boundary.md` preserved in the bundle but orphaned — `index.md` linked only tracer slugs; progressive disclosure never reached it. | Index now links by discovery over every non-reserved typed node; REQ-05-01 walk follows `resource` only when present (authored leaves are valid terminals, Invariant 1a). Fixed `b2214ece`. |

**Operator decision (2026-06-29):** the two navigation-graph seams were treated
as **blocking** the ADR's declared "one working progressive-disclosure path"
thesis and fixed in-flight (operator selected "Hold — fix both first") rather
than deferred to a GHI. Routed as direct defect repair (`fix(knowledge): …`,
`Task: TASK-okf-bundle-navigation-graph`) per operator correction-vs-enhancement
doctrine. TDD: 2 RED → GREEN; full suite 6660/6660.

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ 6/6 OBPIs complete; thesis surfaces all landed |
| Ledger / REQ Integrity | ✓ passed; 21/25 covered, 4 advisory by kind |
| Navigation-graph Fidelity | ✓ resolved (seams 2 & 3 fixed in audit) |
| Fence Integrity (orientation ≠ authority) | ✓ zero enforcement consumers (independently verified) |
| Documentation Alignment | ✓ mkdocs --strict clean; CLI audit 114/114 |
| Risk Items Resolved | ✓ all 3 shortfalls remediated |

## Evidence Index

- `audit/proofs/audit-check.json` — ledger completeness (passed=true)
- `audit/proofs/fidelity.txt` — bound fidelity gate (3 pass)
- `audit/proofs/okf-conformance.txt` — validator exit 0
- `audit/proofs/gates.txt` — heavy gates 1–4 PASS
- `audit/proofs/cli-audit.txt` — 114/114 covered
- `audit/proofs/mkdocs.txt` — docs build clean
- ARB receipts: `arb-step-unittest-0e9117fa117648718c9daac04be7a3d1`, `arb-ruff-e8e128da72244e54a3a1396d0f8b8891`, `arb-step-typecheck-9f52a1db563a4ef6be3fdee595f992fa`
- Fix commit: `b2214ece` (navigation-graph corrections)

## Attestation

Agent (pipeline-orchestrator) attests: ADR-0.30.0 is implemented as intended,
all evidence is reproducible, the bound fidelity gate runs green against the
live OKF surfaces, two independent reviewers were dispatched, and all three
shortfalls surfaced during this audit are resolved. The brief-level human
attestation occurred at each OBPI completion; the ADR-level audit-validation
attestation is recorded via the audit-begin/audit-end ceremony below.

Agent-signed: pipeline-orchestrator — 2026-06-29
Operator audit-validation: _pending verbal `accept audit` / `verify audit`_
