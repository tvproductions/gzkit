---
id: OBPI-0.47.0-05-gzkit-dogfood-and-gate5-attestation
parent: ADR-0.47.0-owasp-top10-2025-scan
item: 5
lane: Heavy
sensitivity: security
status: Draft
---

# OBPI-0.47.0-05-gzkit-dogfood-and-gate5-attestation: gzkit dogfood pass + Gate-5 attestation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/ADR-0.47.0-owasp-top10-2025-scan.md`
- **Checklist Item:** #5 — `OBPI-0.47.0-05-gzkit-dogfood-and-gate5-attestation: gzkit dogfood pass + Gate-5 attestation; baseline report; reference pool ADR`

**Status:** Draft

## Objective

Run `gz scan owasp --scope all` against gzkit itself (the dogfood pass), capture the baseline report at `.gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json`, route any Critical/High findings as GHIs (via `gz issue file`; do NOT auto-fix here — auto-fix is separate work that may spawn follow-up ADRs), document the baseline in the parent ADR's Closeout section, and complete Gate-5 human attestation ceremony for ADR-0.47.0. The brief also confirms `ADR-pool.agentic-security-review` remains live as backlog (kept-live, not closed) and is cross-referenced from the ADR Closeout text.

This is the closure brief: it proves the triad (schema + chore + CLI + skill) lands by exercising it end-to-end on gzkit's own source tree, and binds the ADR to human attestation.

## Lane

**Heavy** — closes a heavy-lane ADR. Gate-5 ceremony, BDD scenario for the end-to-end flow, baseline-report durability, and pool-ADR cross-reference all happen here.

> Sensitivity: `security`. The brief operates the security scanner
> against the project source, files security GHIs, and updates
> `data/security_surfaces.json` if dogfood findings warrant registering
> new gzkit modules. Sensitivity escalation per
> `.gzkit/rules/security-sensitivity.md` § Invariant; the heightened
> Gate-5 walkthrough fires at brief completion.

## Allowed Paths

- `.gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json` — durable baseline report (renamed at capture; the chore's per-run proof in `proofs/` is preserved alongside)
- `docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/ADR-0.47.0-owasp-top10-2025-scan.md` — parent ADR Closeout section + Attestation Block update (one section append + one row update)
- `docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/CLOSEOUT.md` — closeout artifact (if convention requires; align with sibling ADRs)
- `docs/governance/governance_runbook.md` — append a brief note that the dogfood baseline exists at `.gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json` and how to re-run
- `data/security_surfaces.json` — register any newly-identified gzkit security surfaces flagged by dogfood (only if dogfood findings warrant)
- `tests/scan/test_gzkit_dogfood_baseline.py` — regression test that ensures `baseline-2026-05.json` validates against `OwaspScanReport` and that gzkit does not regress below the baseline's clean-floor on subsequent runs
- `features/owasp_scan.feature` — BDD scenarios for end-to-end `gz scan owasp` flow (Gate 4)
- `tests/features/steps/owasp_scan_steps.py` — BDD step implementations
- GHI bodies (filed via `gz issue file` with `--label security`) — one per Critical/High dogfood finding; this brief authors the bodies, not the GitHub responses

## Denied Paths

- `src/gzkit/scan/**` — schema is OBPI-01; CLI handler is OBPI-03; this brief does not add code there
- `.gzkit/chores/owasp-top10-2025-scan/runner.py`, `visitors.py`, `adapters.py` — chore runner is OBPI-02
- `.gzkit/skills/gz-owasp-scan/**` — skill is OBPI-04
- Any source file flagged by dogfood as having a Critical/High finding — auto-fix is forbidden in this brief; findings route to GHIs, fixes happen in follow-up work
- `docs/design/adr/pool/ADR-pool.agentic-security-review.md` — pool ADR stays live; this brief MUST NOT close, supersede, or edit its body
- Other pre-release ADRs (`ADR-0.27.0-arb-receipt-system-absorption`, etc.) — out of scope per hard-gate
- `pyproject.toml`, `uv.lock` — no new deps

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `uv run gz scan owasp --scope all --json > .gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json` MUST run cleanly (exit 0 or 1; exit 2/3 is a chore/CLI defect, not a baseline).
2. ALWAYS: The captured `baseline-2026-05.json` MUST validate via `OwaspScanReport.model_validate_json(...)`; failure is a fail-closed defect blocking attestation.
3. ALWAYS: Each Critical or High finding in the baseline MUST be filed as a `gz issue file` GHI with label `security`, body referencing the finding's `category`, `rule_id`, `path`, `line`, and `evidence`. Auto-fix MUST NOT happen in this brief.
4. NEVER: This brief MUST NOT edit `docs/design/adr/pool/ADR-pool.agentic-security-review.md` body; the pool ADR stays live as backlog.
5. ALWAYS: The parent ADR's Closeout section MUST cross-reference `ADR-pool.agentic-security-review` with rationale "kept-live as backlog; ADR-0.47.0 implements the OWASP slice; pool ADR remains the home for CWE Top 25, NIST SSDF mappings, secrets scanning, license posture, runtime monitoring, custom-rule authoring per its rationale paragraph."
6. ALWAYS: BDD scenarios in `features/owasp_scan.feature` MUST cover (a) clean-repo run exits 0; (b) fixture-with-critical-finding exits 1; (c) `--json` output validates as `OwaspScanReport`.
7. REQUIREMENT: Gate-5 attestation text MUST follow the canonical attestation pattern from AGENTS.md § Attestation: `<operator's verbatim words> — <concrete characterization grounded in session evidence>`, with named receipt IDs (`arb-ruff-*`, `arb-step-typecheck-*`, `arb-step-unittest-*`, `arb-step-coverage-*`, `arb-step-mkdocs-*`, `arb-step-security-scan-*`).
8. ALWAYS: `uv run gz adr emit-receipt ADR-0.47.0 --event validated --attestor "<Operator Name>" --evidence-json '{...}'` MUST run cleanly at closeout, and the receipt MUST appear in `.gzkit/ledger.jsonl`.
9. REQUIREMENT: `tests/scan/test_gzkit_dogfood_baseline.py::test_baseline_validates` MUST pass; `test_no_regression_below_baseline` MUST pass on subsequent CI runs (regression guard).
10. ALWAYS: Operator PII discipline (CLAUDE.md § Local Agent Rules) — no personal email in any artifact, ledger entry, GHI body, attestation text, or commit message; use the operator's name only or the GitHub noreply form.

> STOP-on-BLOCKERS: if `gz scan owasp` is not executable, halt and report. If `ADR-pool.agentic-security-review.md` does not exist, halt and report.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote verbatim into Implementation Summary:** "gzkit dogfoods before any external consumer adopts; baseline report becomes evidence in OBPI-0.47.0-05." Plus § Rationale paragraph 1 explaining `ADR-pool.agentic-security-review` cross-reference (kept-live as backlog).
- [ ] Parent ADR § Consequences § Negative — heavy-lane Gate 5 attestation is required for the foundational scanner release.
- [ ] Parent ADR § Evidence — pool-ADR cross-reference checklist item.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Attestation — canonical attestation pattern + canonical receipt-name prefixes.
- [ ] `AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix — heavy + security force human attestation independently.
- [ ] `.gzkit/rules/adr-audit.md` — Gate-5 audit sequence + receipt emission.
- [ ] `.gzkit/rules/security-sensitivity.md` — heightened walkthrough requirements.
- [ ] `.gzkit/rules/gh-cli.md` — `gz issue file` is the canonical defect-filing wrapper.
- [ ] CLAUDE.md § Local Agent Rules — operator PII discipline (no personal email in any artifact).

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.47.0-01, -02, -03, -04 have all landed and passed.
- [ ] `gz scan owasp` is callable.
- [ ] `gz issue file` is callable.
- [ ] `.gzkit/skills/gz-owasp-scan/SKILL.md` is the canonical skill (mirror sync confirmed).
- [ ] `docs/design/adr/pool/ADR-pool.agentic-security-review.md` exists and is in `Active` (or equivalent live) state.

**Existing Code (understand current state):**

- [ ] One sibling closeout (e.g., `docs/design/adr/pre-release/ADR-0.43.0-ghi-triage-closeout/CLOSEOUT.md` if present) for shape.
- [ ] `features/` directory for existing BDD precedents (any `.feature` file) for step-definition shape.
- [ ] `.gzkit/ledger.jsonl` — review one prior `validated` event for shape.

## Quality Gates

### Gate 1: ADR

- [ ] Decision quote present in Implementation Summary
- [ ] Closeout section appended to parent ADR with baseline path + pool-ADR cross-reference
- [ ] Attestation Block row updated for term `0.47.0`

### Gate 2: TDD (Red-Green-Refactor)

- [ ] `tests/scan/test_gzkit_dogfood_baseline.py` lands RED → GREEN
- [ ] `uv run gz arb step --name unittest -- uv run -m unittest -q tests/scan/test_gzkit_dogfood_baseline.py` passes

### Code Quality

- [ ] `uv run gz arb ruff` clean
- [ ] `uv run gz arb typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
- [ ] Governance runbook updated with re-run instructions
- [ ] `gz validate --documents` exit 0
- [ ] `gz validate --cli-alignment` exit 0

### Gate 4: BDD (Heavy)

- [ ] `features/owasp_scan.feature` covers the three named scenarios
- [ ] `uv run -m behave features/owasp_scan.feature` passes

### Gate 5: Human (Heavy + Security)

- [ ] Heightened walkthrough completed; `arb-step-security-scan-*` receipt confirmed
- [ ] Operator attestation captured per AGENTS.md § Attestation pattern (verbatim words + concrete characterization)
- [ ] `uv run gz adr emit-receipt ADR-0.47.0 --event validated ...` runs cleanly
- [ ] Ledger entry visible in `.gzkit/ledger.jsonl`

## Verification

```bash
uv run gz validate --documents
uv run gz validate --briefs
uv run gz validate --cli-alignment
uv run gz validate --skills
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests/scan
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run -m behave features/owasp_scan.feature

# Gate-5 specific
uv run gz adr audit-check ADR-0.47.0
uv run gz closeout ADR-0.47.0 --dry-run
uv run gz attest ADR-0.47.0 --status completed
uv run gz audit ADR-0.47.0
uv run gz adr emit-receipt ADR-0.47.0 --event validated --attestor "<Operator Name>" --evidence-json '{"scope":"ADR-0.47.0","date":"2026-05-10","baseline":".gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json"}'

# Specific verification
test -f .gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json
uv run python -c "
from gzkit.scan.models import OwaspScanReport
r = OwaspScanReport.model_validate_json(open('.gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json').read())
print(f'baseline findings: {len(r.findings)}; critical/high: {sum(1 for f in r.findings if f.severity in (\"critical\",\"high\"))}')
"
```

## Demo

```bash
# End-to-end dogfood
uv run gz scan owasp --scope all
echo "exit: $?"

# Capture durable baseline
uv run gz scan owasp --scope all --json > .gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json

# File any critical/high findings as GHIs (one per finding)
uv run python -c "
from gzkit.scan.models import OwaspScanReport
r = OwaspScanReport.model_validate_json(open('.gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json').read())
for f in r.findings:
    if f.severity in ('critical','high'):
        print(f'gz issue file --label security --title \"OWASP {f.category} ({f.rule_id}): {f.path}:{f.line}\" --body ...')
"
```

## Acceptance Criteria

- [ ] REQ-0.47.0-05-01: Given `gz scan owasp --scope all --json`, when run against gzkit, then exit code is `0` or `1` (never `2`/`3`) and stdout validates as `OwaspScanReport`; `tests/scan/test_gzkit_dogfood_baseline.py::test_dogfood_run_clean_or_findings_only` covers.
- [ ] REQ-0.47.0-05-02: Given `.gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json`, when read, then it validates via `OwaspScanReport.model_validate_json` and contains `coverage["A06"] == "not-mechanical"` and `coverage["A07"] == "not-applicable"`; `tests/scan/test_gzkit_dogfood_baseline.py::test_baseline_validates` covers.
- [ ] REQ-0.47.0-05-03: Given subsequent runs of `gz scan owasp --scope all` after baseline capture, when finding count is compared to baseline, then no new Critical or High finding appears that is not already filed as a GHI; `tests/scan/test_gzkit_dogfood_baseline.py::test_no_unfiled_critical_high_regression` covers.
- [ ] REQ-0.47.0-05-04: Given the parent ADR's Closeout section, when read, then it cross-references `ADR-pool.agentic-security-review` with the kept-live rationale; `tests/scan/test_gzkit_dogfood_baseline.py::test_pool_adr_crossreference_present` covers (file-content assertion).
- [ ] REQ-0.47.0-05-05: Given `docs/design/adr/pool/ADR-pool.agentic-security-review.md`, when read, then its body and frontmatter are unchanged from pre-OBPI-05 state; `tests/scan/test_gzkit_dogfood_baseline.py::test_pool_adr_body_unchanged` covers (sha256 against snapshot taken at brief authoring time).
- [ ] REQ-0.47.0-05-06: Given `.gzkit/ledger.jsonl`, when filtered for events with `adr_id == "ADR-0.47.0"` and `event == "validated"`, then exactly one entry exists with the operator's name (not personal email); `tests/scan/test_gzkit_dogfood_baseline.py::test_ledger_validated_event_clean` covers.
- [ ] REQ-0.47.0-05-07: Given `features/owasp_scan.feature`, when `behave` runs, then all three scenarios (clean-repo, fixture-with-finding, JSON-shape) pass; the run is captured as Gate-4 evidence.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Closeout section appended; pool-ADR cross-reference present; Attestation Block updated
- [ ] **Gate 2 (TDD):** Seven REQ-derived tests pass
- [ ] **Code Quality:** `arb-ruff-*`, `arb-step-typecheck-*` receipts captured
- [ ] **Gate 3 (Docs):** mkdocs strict; runbook updated; cli-alignment 0
- [ ] **Gate 4 (BDD):** `behave` scenarios pass
- [ ] **Gate 5 (Human + Security):** Heightened walkthrough completed; `gz adr emit-receipt validated` succeeded; ledger entry present; operator PII clean
- [ ] **Value Narrative:** gzkit dogfooded its own scanner before any consumer adopts
- [ ] **Key Proof:** Baseline JSON exists, validates, and is the durable evidence anchor
- [ ] **OBPI Acceptance:** Human attestation recorded with verbatim-words pattern

## Evidence

### Gate 1 (ADR)

- [ ] Closeout section + pool-ADR cross-reference + Attestation Block update

### Gate 2 (TDD — Red-Green-Refactor)

```text
# arb-step-unittest-<sha>     (uv run -m unittest -q tests/scan/test_gzkit_dogfood_baseline.py)
# arb-step-coverage-<sha>     (coverage discover -s tests/scan)
```

### Code Quality

```text
# arb-ruff-<sha>
# arb-step-typecheck-<sha>
```

### Gate 3 (Docs)

```text
# arb-step-mkdocs-<sha>
# gz validate --documents exit 0
# gz validate --cli-alignment exit 0
```

### Gate 4 (BDD)

```text
# behave output: 3 scenarios passed, 0 failed
```

### Gate 5 (Human + Security)

```text
# arb-step-security-scan-<sha>  (heightened walkthrough)
# Attestation:
#   "<operator verbatim words> — gzkit dogfood scan against ADR-0.47.0 produced
#    baseline at .gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json
#    validating against OwaspScanReport schema (commit <sha>); receipts:
#    arb-ruff-<sha>, arb-step-typecheck-<sha>, arb-step-unittest-<sha>,
#    arb-step-coverage-<sha>, arb-step-mkdocs-<sha>, arb-step-security-scan-<sha>;
#    Critical/High findings filed as GHI #<n>..#<m> per Routing rules; pool ADR
#    ADR-pool.agentic-security-review remains live as backlog."
# Receipt:
#   uv run gz adr emit-receipt ADR-0.47.0 --event validated \
#     --attestor "<Operator Name>" \
#     --evidence-json '{"scope":"ADR-0.47.0","date":"2026-05-10","baseline":".gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json"}'
```

### Value Narrative

Before this OBPI: ADR-0.47.0 had a chore + CLI + skill but no exercised proof that the triad actually scans gzkit cleanly. After this OBPI: a durable baseline exists, regression-guarded by a unit test, BDD scenarios cover the end-to-end flow, Critical/High findings are filed as GHIs (never auto-fixed), the pool ADR `ADR-pool.agentic-security-review` is preserved as backlog, and the human attestation is bound to the ledger via `gz adr emit-receipt validated`.

### Key Proof

`.gzkit/chores/owasp-top10-2025-scan/proofs/baseline-2026-05.json` exists, validates against `OwaspScanReport`, and is the durable evidence anchor cited in the parent ADR Closeout. The ledger entry for `ADR-0.47.0 / validated` carries the named receipt IDs and the operator's name (no personal email).

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_To be filed during dogfood; one GHI per Critical/High finding via `gz issue file --label security`. Bodies authored under this brief; closure of those GHIs is follow-up work, not this brief._

## Human Attestation

- Attestor: `<Operator Name>` (per CLAUDE.md § Local Agent Rules — name only, never personal email)
- Attestation: substantive attestation text using verbatim-words + concrete characterization pattern (AGENTS.md § Attestation)
- Date: 2026-05-10 or later

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
