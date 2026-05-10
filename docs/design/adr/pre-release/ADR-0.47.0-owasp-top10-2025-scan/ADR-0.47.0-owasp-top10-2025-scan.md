---
id: ADR-0.47.0-owasp-top10-2025-scan
status: Draft
kind: feature
semver: 0.47.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-10
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.47.0-owasp-top10-2025-scan: OWASP Top 10:2025 Portable Security Scanner

## Persona

`main-session` craftsperson posture. Implementations land complete units —
chore runner with its `proofs/`, CLI verb with its manpage and `--json`
contract, skill with its synthesized SKILL.md and control-surface mirrors —
never partial. Stdlib-first doctrine is load-bearing here: every analyzer
either ships in the standard library (AST), in our existing toolchain
(ruff `S`-rules), or it does not exist as a mechanical analyzer in this
ADR. "Bandit is what everyone reaches for" is the named anti-rationale
this ADR refuses.

## Intent

Add a portable, mechanical OWASP Top 10:2025 security scanner to every
gzkit-governed repository. The scanner runs from any consumer repo via
`gz scan owasp` and produces a structured Pydantic report keyed by OWASP
2025 category (A01–A10), with each category honestly labeled by its
mechanical floor: `mechanical`, `partial-mechanical`, `not-mechanical`, or
`not-applicable`. The scanner uses ruff `S`-rules and stdlib AST visitors
only; it reuses the existing `dependency-currency` and
`exceptions-and-logging-rationalization` chores rather than duplicating
their analyzers. Categories that demand judgment (notably **A06 Insecure
Design**) are not graded by the chore — they route to the synthesizer
skill `gz-owasp-scan` for human-attested review. gzkit dogfoods the
scanner against itself before any consumer adopts it.

## Decision

### CLI surface

- New verb `gz scan owasp` under a new `scan` namespace (future-proofs
  for `gz scan cwe`, `gz scan secrets`, `gz scan license`).
- Default scope mode: `all` (whole repo). Additional scope modes:
  `touched`, `path <PATH>`, `adr <ADR-ID>`, `obpi <OBPI-ID>`.
- `--json` flag emits `OwaspScanReport` to stdout for machine consumers.
- Default exit codes: `0` (no critical/high), `1` (critical or high
  finding present), `2` (config/IO error), `3` (policy breach,
  e.g., heavy-lane gate with unresolved critical/high).
- Manpage at `docs/user/manpages/gz-scan-owasp.md` with EXAMPLES section
  showing real CLI output (Gate 5 runbook-code covenant).

### Analyzer floor (stdlib-first, no third-party security tools)

- **ruff `S`-family** (already in toolchain): `S110`, `S112`, `S301`,
  `S302`, `S303`, `S304`, `S305`, `S306`, `S307`, `S324`, `S501`, `S502`,
  `S503`, `S504`, `S505`, `S506`, `S507`, `S508`, `S509`, `S605`, `S606`,
  `S607`, `S608`, `S609`.
- **Stdlib `ast` visitors** (no third-party): chmod 0o777 literals,
  `verify=False` in requests-style calls, `shell=True` literal,
  `pip install` / package-manager subprocess in source, hardcoded
  cryptographic keys, `random.*` used for security tokens (vs.
  `secrets.*`), f-string interpolation directly into `execute()` /
  `eval()` / `exec()` / `os.system()`, secret-shaped strings in log
  format strings.
- **Reused chores**: `dependency-currency` for A03 (no duplicate
  CVE/dependency analyzer); `exceptions-and-logging-rationalization`
  for A09 (no duplicate logger-policy analyzer) and A10 (no duplicate
  exception-handling analyzer).

### A01–A10 coverage map (OWASP Top 10:2025)

| OWASP 2025 | Source | Coverage | Notes |
|---|---|---|---|
| A01 Broken Access Control | `judgment-only` | not-mechanical | Skill-only governance-access review (OBPI lock claims, Gate 5 attestation gates, ledger-write paths). Web-route auth detection deferred to follow-up ADR. |
| A02 Security Misconfig | `stdlib-ast` (partial) + `judgment-only` (rest) | partial-mechanical | Mech: chmod 0o777, `verify=False`, `shell=True` literal. Judgment: debug flags in production, log policy. |
| A03 Software Supply Chain | reuse `dependency-currency` chore + `stdlib-ast` | partial-mechanical | AST: `pip install` / package-mgr subprocess in source. Reuses dependency-currency outputs verbatim. |
| A04 Cryptographic Failures | `ruff S324,S501,S502,S503,S504,S505,S506,S507,S508,S509` + `stdlib-ast` | mechanical | Weak hash, ssl-no-cert, weak TLS; AST: hardcoded keys, `random.*` for tokens. |
| A05 Injection | `ruff S608,S609,S301,S302,S303,S304,S305,S306,S307,S605,S606,S607` + `stdlib-ast` | mechanical | sql/shell-injection, unsafe pickle/yaml; AST: f-string interpolation into `execute()`. |
| A06 Insecure Design | `judgment-only` | not-mechanical | Synthesizer-skill territory. Chore MUST NOT grade. The honest move is the `not-mechanical` coverage marker. |
| A07 Authentication Failures | `not-applicable` | not-applicable | No auth surface in Python library/CLI; `coverage_note` records the rationale. Web-framework auth detection deferred to follow-up ADR. |
| A08 Software/Data Integrity | `ruff S301,S302,S506` + `stdlib-ast` + `judgment-only` (rest) | partial-mechanical | Mech: unsafe deserialize. Judgment: CI/release artifact integrity, signed-commit policy. |
| A09 Logging/Alerting Failures | reuse `exceptions-and-logging-rationalization` chore + `stdlib-ast` | partial-mechanical | AST: secret-shaped strings in log format strings, missing structured logger. |
| A10 Mishandling of Exceptions | reuse `exceptions-and-logging-rationalization` chore + `ruff S110,S112` | mechanical | `try-except-pass`, `try-except-continue`. |

### Output schema (Pydantic)

`OwaspScanReport`:

- `schema_version: Literal["1.0"]` (anchored — bump on contract change)
- `owasp_year: Literal[2025]`
- `repo: str`, `commit: str` (git SHA at scan time)
- `scope_mode: Literal["all", "touched", "path", "adr", "obpi"]`
- `scanned_paths: list[Path]`
- `findings: list[OwaspFinding]`
- `coverage: dict[str, Literal["mechanical", "partial-mechanical", "not-mechanical", "not-applicable"]]` — keyed by `A01`..`A10`
- `generated_at: datetime`

`OwaspFinding`:

- `category: Literal["A01","A02","A03","A04","A05","A06","A07","A08","A09","A10"]`
- `source: Literal["ruff-S", "stdlib-ast", "chore-reused", "not-mechanical"]`
- `severity: Literal["critical", "high", "medium", "low", "info"]`
- `path: Path`, `line: int`
- `rule_id: str` (e.g., `S324`, `gzkit-ast-chmod-world-writable`)
- `summary: str`
- `evidence: str` (≤200 chars, truncated source span or analyzer output)

**Hard invariant:** No category may report `coverage == "mechanical"`
unless ≥1 named analyzer (ruff `S` rule, stdlib-ast visitor, or reused
chore) produced findings or attested zero findings on the scanned scope.
Categories with `judgment-only` or `not-applicable` source MUST report
`not-mechanical` or `not-applicable` respectively. Validated by schema
test in OBPI-0.47.0-01.

### Routing rules (from finding to action)

| Severity | Route |
|---|---|
| Critical / High | `gh issue create --label security` (1 GHI per finding); blocks heavy-lane gate |
| Medium | In-flight fix if ≤10 SLOC (defect-fix routing per AGENTS.md); else chore |
| Low / Info | Report-only, no GHI |

A06 judgment findings always route through GHI (no auto-fix) — by
design, since the chore does not grade design.

### Triad shape (operator-locked)

- **Mechanical chore** at `.gzkit/chores/owasp-top10-2025-scan/` — runs
  ruff `S`-rules + AST visitors + reused-chore adapters; writes
  `proofs/`; emits ledger receipt.
- **CLI verb** `gz scan owasp` — argparse handler under
  `src/gzkit/cli/scan.py`; resolves scope, invokes chore, formats output
  (table or `--json`).
- **Synthesizer skill** `gz-owasp-scan` at `.gzkit/skills/gz-owasp-scan/`
  — sibling to `gz-tech-debt-review`; renders findings narrative,
  routes critical/high to GHI, names A06 / A01 judgment findings for
  human attention.

## Consequences

### Positive

- Every gzkit-governed repo (gzkit included) gains a portable OWASP Top
  10:2025 floor with no third-party security-tool dependency.
- Stdlib-first doctrine remains intact; new doctrine departures are not
  required for this capability.
- A06 honesty: the chore explicitly refuses to grade Insecure Design,
  surfacing the limit as a `not-mechanical` coverage marker rather than
  pattern-matching from training corpus (anti-vibing binding claim 4).
- Reused chores avoid analyzer duplication and keep the maintenance
  surface small.
- The `scan` CLI namespace establishes future-proof shape for `gz scan
  cwe`, `gz scan secrets`, `gz scan license`.
- gzkit dogfoods before any external consumer adopts; baseline report
  becomes evidence in OBPI-0.47.0-05.

### Negative

- `judgment-only` categories (A01, A06, parts of A02 / A08) require
  human review to be meaningful; the chore alone is incomplete for
  those categories. Operators must understand `coverage` markers to
  interpret reports correctly.
- Adding a new CLI namespace (`scan`) increases the verb surface; manpage
  and runbook must stay aligned (`tool-skill-runbook-alignment.md`).
- Heavy-lane Gate 5 attestation is required for the foundational scanner
  release — the dogfood pass and baseline report are gated on operator
  witness, not auto-completable.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1

<!-- Score notes (advisory only; scorecard parser requires bare integers above):
     Data/State 2 — Pydantic models + JSON-schema'd mapping.json + Literal-typed
       coverage map with hard invariant; non-trivial schema surface.
     Logic/Engine 2 — analyzer composition: ruff `S`-rules + AST visitors +
       chore-reuse adapters.
     Interface 2 — new CLI namespace (`scan`) + `--json` contract + manpage.
     Observability 2 — `proofs/` + ledger receipt + JSON output contract;
       the JSON contract is a first-class observability surface for
       downstream consumers and CI gates.
     Lineage 1 — cross-references chores; reuses `dependency-currency` and
       `exceptions-and-logging-rationalization`. -->

- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps.
     Per AGENTS.md § OBPI Decomposition Mandate, this checklist is in
     1:1 sync with the brief files under obpis/. -->

- [ ] OBPI-0.47.0-01-owasp-data-model-and-mapping-schema: `mapping.json` data + `OwaspScanReport` Pydantic models + schema tests
- [ ] OBPI-0.47.0-02-owasp-chore-runner: Chore runner — ruff-`S` invocation + AST visitors + chore-reuse adapters
- [ ] OBPI-0.47.0-03-gz-scan-owasp-cli-verb: CLI verb `gz scan owasp` — argparse, scope resolution, `--json`, manpage
- [ ] OBPI-0.47.0-04-gz-owasp-scan-skill: Skill `gz-owasp-scan` — SKILL.md, control-surface sync, skill-trigger tests
- [ ] OBPI-0.47.0-05-gzkit-dogfood-and-gate5-attestation: gzkit dogfood pass + Gate-5 attestation; baseline report; reference pool ADR

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.47.0-01 | `mapping.json` + `OwaspScanReport`/`OwaspFinding` Pydantic models + schema-invariant tests | Heavy | Pending |
| 2 | OBPI-0.47.0-02 | Chore runner: ruff-`S` invocation, stdlib-AST visitors, reused-chore adapters, `proofs/` writer | Heavy | Pending |
| 3 | OBPI-0.47.0-03 | `gz scan owasp` argparse handler, scope resolution, `--json`, exit codes, manpage | Heavy | Pending |
| 4 | OBPI-0.47.0-04 | `gz-owasp-scan` skill SKILL.md, vendor-mirror sync, skill-trigger tests | Heavy | Pending |
| 5 | OBPI-0.47.0-05 | gzkit dogfood scan + baseline report + Gate-5 attestation + pool ADR cross-reference | Heavy | Pending |

**Lane inheritance:** All 5 OBPIs are heavy by inheritance from the
parent ADR's `lane: heavy`, per AGENTS.md § Lane & Kind & Sensitivity
Attestation Matrix. Each OBPI requires Gate-5 human attestation at
brief level.

## Q&A Transcript

Design captured via the `gz-design` skill on 2026-05-10. Operator
locked the triad shape ("we always do C: all chores are SKILL + tool"),
the analyzer floor (stdlib-first, no bandit/semgrep), the default scope
mode (`all`), and the routing of `ADR-pool.agentic-security-review`
(stays live as backlog; this ADR implements one slice).

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/scan/test_owasp_models.py`, `tests/scan/test_owasp_chore_runner.py`, `tests/scan/test_gz_scan_owasp_cli.py`, `tests/skills/test_gz_owasp_scan_skill.py`
- [ ] Docs: `docs/user/manpages/gz-scan-owasp.md`, `docs/user/runbook.md` (scan section), `docs/governance/governance_runbook.md` (scan-as-gate section)
- [ ] Chore: `.gzkit/chores/owasp-top10-2025-scan/CHORE.md`, `.gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05-10.json`
- [ ] Skill: `.gzkit/skills/gz-owasp-scan/SKILL.md` (canonical) + vendor mirrors via `gz agent sync control-surfaces`
- [ ] Receipt: `arb-step-` receipts for unittest + ruff + typecheck + mkdocs; `gz adr emit-receipt` for completed/validated events
- [ ] Pool ADR: `docs/design/adr/pool/ADR-pool.agentic-security-review.md` remains live (not closed, not superseded); ADR-0.47.0 cross-references it as parent intent

## Rationale

The parent intent is captured in the live pool ADR
[`ADR-pool.agentic-security-review`](../../pool/ADR-pool.agentic-security-review.md),
which calls out that AI-coding agents amplify both productivity and
security risk and that gzkit's gate model is the natural integration
point for a security dimension. ADR-0.47.0 implements one concrete
slice of that pool intent — an OWASP Top 10:2025 mechanical floor with
stdlib-first analyzers — without consuming the pool ADR. The pool ADR
remains the backlog home for the broader agentic-security-review vision
(CWE Top 25, NIST SSDF mappings, secrets scanning, license posture,
runtime monitoring, custom rule authoring), and the `scan` CLI
namespace is shaped so each future slice ships as `gz scan <kind>`
without restructuring.

The doctrine-fit story: stdlib-first
([AGENTS.md § Stdlib-First doctrine](../../../../AGENTS.md))
forbids reaching for bandit/semgrep without articulated rationale. The
ruff `S`-family already covers bandit's checks within our existing
toolchain; stdlib `ast` covers the gzkit-specific patterns (governance
state writes, OBPI lock claims, ledger format strings) that no
third-party scanner could understand without custom rule authoring
anyway. The pool ADR's promotion criterion 2 ("scanner toolchain is
accepted") was stated as `bandit / semgrep / alternatives` in 2026-03;
under the stdlib-first lock the right resolution is to leave the pool
ADR live with that criterion **structurally unsatisfiable** and ship
this ADR as a doctrine-correct slice. That choice is itself the
rejected-alternative #4 below.

The triad shape ("chore + CLI + skill, always") is project doctrine.
Mechanical analysis without a chore would produce no `proofs/` evidence
and no ledger receipt — exactly the Layer-3-as-source-of-truth pattern
Architectural Boundary 6 prohibits. CLI-only without a skill leaves
operators without a synthesized narrative for judgment categories
(A06, A01); skill-only without a chore leaves the mechanical floor
unattested.

The honest treatment of A06 Insecure Design is itself the doctrine
proof. Pattern-matching "insecure design" from training corpus is the
exact named failure class in
[anti-vibing binding claim 4](../../../../AGENTS.md). The
chore must NOT grade A06; the report must mark `coverage["A06"] ==
"not-mechanical"` and route every A06 finding through the synthesizer
skill for human attestation. Forcing this honesty in the schema
(`coverage` Literal type validated by test) prevents future drift.

### Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| **Direct bandit integration** | Violates stdlib-first doctrine. Ruff `S`-family already covers bandit's checks; adding bandit duplicates coverage and adds a third-party security-tool dependency without articulated rationale per AGENTS.md § Stdlib-First binding claims 1–2. "Bandit is what everyone reaches for" is the named anti-rationale. |
| **Skill-only (no chore)** | Violates project doctrine "all chores are SKILL + tool". Mechanical analysis without a chore = no `proofs/` evidence trail, no ledger receipt — exactly the Layer-3-as-source-of-truth pattern Architectural Boundary 6 prohibits. |
| **Mechanically grade A06 Insecure Design** | Anti-vibing doctrine binding claim 4. Pattern-matching "insecure design" from training corpus is the named failure class. The honest move is the `not-mechanical` coverage marker; A06 is synthesizer-skill territory by construction. |
| **Promote `ADR-pool.agentic-security-review` as-is** | Pool ADR's promotion criterion 2 ("scanner toolchain accepted") is unsatisfiable under stdlib-first lock — its bandit/semgrep premise is wrong-by-doctrine, not just dated. Resolution: pool ADR stays live as backlog; ADR-0.47.0 implements one slice with correct toolchain. |
| **Single-word CLI verb (`gz owasp-scan`)** | Orphans the verb when CWE Top 25 / NIST SSDF / secrets-scanning / license-scanning land. Two-word `gz scan owasp` matches existing `obpi pipeline`, `adr audit-check`, `agent sync` shape and establishes a `scan` noun-namespace for future siblings. |

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.47.0 | Pending | | | |
