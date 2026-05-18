# AUDIT — ADR-0.0.36

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.36-universal-obpi-attestation |
| ADR Title | Universal OBPI Attestation (Zero-Maxxing) |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/ |
| Audit Date | 2026-05-18 |
| Auditor(s) | g0 (operator) + agent-relayed audit (pipeline-orchestrator persona) |
| Lane | heavy |
| Kind | foundation |
| Pre-audit state | Lifecycle=Completed, Phase=attested, Closeout=READY, QC=READY |

## Feature Demonstration (Step 3 — MANDATORY)

ADR-0.0.36 collapses the Lane & Kind Attestation Matrix's `feature × lite → Self-closeable` cell at the doctrine layer, making the matrix's downstream rationalizations (runtime branching, receipt-shape leniency, skill prose) structurally unreachable for new entries.

### Capability 1: Runtime gate is universal (`_requires_human_obpi_attestation` returns True)

```bash
$ uv run python -c "from gzkit.commands.adr_audit import _requires_human_obpi_attestation; \
                    import inspect; print(inspect.getsource(_requires_human_obpi_attestation))"
def _requires_human_obpi_attestation(
    parent_adr: str | None,
    parent_lane: str,
    brief_frontmatter: Mapping[str, Any] | None = None,
) -> bool:
    """Return whether completed evidence must include human-attestation fields.

    Per ADR-0.0.36 and OBPI-0.0.36-02, human attestation is UNIVERSAL: every
    OBPI completion requires it regardless of parent ADR kind, lane, or
    sensitivity. The foundation/lane/security branching logic has been
    collapsed. The signature is preserved for call-site compatibility; all
    three parameters are accepted but not evaluated.
    """
    return True
```

The runtime gate that previously branched on `kind`/`lane`/`sensitivity` to admit lite-lane feature self-close has collapsed to an unconditional `True`. The signature is preserved so call-sites do not change, but the predicate is structurally unable to return False.

Tests pin universality across every prior branch (`tests/test_adr_audit_predicates.py`):

```
test_heavy_feature_no_sensitivity_still_required ... ok
test_heavy_lane_security_brief_still_required ... ok
test_lite_feature_no_sensitivity_requires_attestation ... ok
test_lite_feature_security_brief_requires_attestation ... ok
test_lite_foundation_no_sensitivity_still_required ... ok
test_frontmatter_argument_is_optional_for_call_site_compat ... ok
```

**Why it matters:** the pre-doctrine vibing-leak surface was "agent runs lite-lane feature OBPI, agent self-closes, no operator was present." That path is now structurally absent from the codebase — an agent attempting it cannot reach a completion state without operator attestation, regardless of which `kind`/`lane` combination the parent ADR carries.

### Capability 2: Validator fail-closed scope (`gz validate --receipt-shape`)

```bash
$ uv run gz validate --receipt-shape
Validated: manifest, surfaces, ledger, instructions, briefs, documents,
personas, frontmatter, version, taxonomy

[OK] All validations passed (10 scopes).
```

Test-bench coverage (`tests/governance/test_validate_receipt_shape.py`):

```
test_post_cutoff_agent_attestor_case_insensitive ... ok
test_post_cutoff_agent_attestor_fails ... ok
test_post_cutoff_canonical_attestation_passes ... ok
test_post_cutoff_optional_attestation_requirement_fails ... ok
test_post_cutoff_bare_completed_fails ... ok
test_pre_cutoff_with_waiver_passes_silently ... ok
test_pre_cutoff_without_waiver_file_is_warn_only ... ok
```

**Why it matters:** the mechanical defense binds the doctrine. Any future receipt carrying `attestation_requirement: optional`, `obpi_completion: completed` (un-prefixed), or `attestor: ^agent:` is refused by the validator — Exit 3 in CI, blocking the offending commit before it lands. Doctrine drift now requires either editing the validator (visible, attestable) or adding a waiver (also visible, also attestable). Silent drift is structurally unreachable.

### Capability 3: Historical waiver list is closed-set under OBPI-0.0.36-04

```bash
$ uv run python -c "import json; d = json.load(open('data/historical_self_close_waivers.json')); \
                    print('waiver count:', len(d.get('waivers', []))); \
                    print('all added_under:', sorted({w['added_under'] for w in d.get('waivers', [])}))"
waiver count: 42
all added_under: ['OBPI-0.0.36-04-historical-self-close-waivers']
```

**Why it matters:** 42 pre-doctrine receipts that would otherwise fail the new validator are explicitly catalogued. The `added_under` constraint means a new waiver cannot be added without authoring a "waiver-extension" ADR — i.e., the waiver list is not a soft-rationalization escape hatch. Historical drift is documented, not rewritten (ledger immutability honored).

### Capability 4: AGENTS.md matrix collapse — universal-attestation rule binding

```text
$ grep -A2 'brief-level human attestation is\|UNIVERSAL\|Self-closeable' AGENTS.md
**Agent MUST NOT mark an OBPI brief as `Completed` without explicit human attestation.
Brief-level human attestation is universal (ADR-0.0.36, GHI #342).
Enforced by `_requires_human_obpi_attestation`.**

### Universal OBPI Attestation (ADR-0.0.36, GHI #342)

**Brief-level human attestation is ALWAYS required for every OBPI completion, regardless
of parent ADR kind or lane. There is NO self-close path.**
```

No `Self-closeable` cell survives in `AGENTS.md`; the universal-attestation rule replaces it. Lane and kind axes remain — only as gate-firing-scope determinants, never as attestation-required determinants.

**Why it matters:** the doctrine source-of-truth is unambiguous. Adopters reading `AGENTS.md` from a freshly-installed wheel inherit the universal rule by default; no per-project re-derivation, no matrix-cell choosing.

### Capability 5: Skill prose sweep — live `self-clos` references absent from named OBPI-05 scope

```text
$ rg -in 'self-clos' .gzkit/skills/
.gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md:50:- [ ] **Parent ADR is Lite** → Agent may self-close after presenting evidence
```

The four skill files named in OBPI-0.0.36-05's explicit scope (`gz-obpi-pipeline`, `gz-obpi-reconcile`, `ghi-close`, `gz-adr-closeout-ceremony`) are clean. **One residue surface (`gz-obpi-specify` template) was outside OBPI-05's enumerated scope and carries one live reference.** See § Recommendations for the routing decision; tracked as GHI #487.

**Why it matters:** the named-scope sweep delivered for OBPI-05's stated allowed-paths; the doctrine-layer collapse correctly closes the vibing path even when the template prose is stale (runtime gate refuses the action the template would scaffold). The residue is doc-cosmetic, not runtime-enforcing, but it does seed misleading scaffolds and should be cleaned.

### Value Summary

Before ADR-0.0.36: an agent could rationalize lite-lane feature OBPI self-close by following the matrix's permissive cell, the receipt schema's `optional` enum value, or any of the skill prose that named "self-closeable after evidence" as a valid path. Each surface was a separate doctrine pin; agents could route around any single hardening.

After ADR-0.0.36: the matrix collapses to one row (universal attestation), the runtime gate is `return True`, the validator fails closed on deprecated receipt shapes, the waiver list is closed-set under one OBPI origin, and the named skills are swept. Every doctrine pin moves together. An agent today cannot construct a valid OBPI completion path that omits brief-level human attestation, regardless of which combination of `kind`/`lane` they choose for the parent ADR — exactly the craft-standard reviewer test the ADR's Persona section names.

---

## Execution Log

| Check | Command / Method | Result | Notes |
|-------|------------------|--------|-------|
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.36` | OK | All 5 OBPIs PASS; 29/29 REQs covered (100%). Layer-2 trust intact. |
| Lifecycle state | `uv run gz adr status ADR-0.0.36` | OK | Lifecycle=Completed, Phase=attested, Closeout=READY, QC=READY; 5/5 OBPIs `attested_completed`. |
| Runtime gate source | `python -c inspect.getsource(_requires_human_obpi_attestation)` | OK | Returns `True` unconditionally; signature preserved. Proof: `audit/proofs/runtime-gate-source.txt` |
| Runtime gate test universality | `uv run python -m unittest tests.test_adr_audit_predicates` | OK | All lane/kind/sensitivity branches still require attestation (13 tests). Proof: `audit/proofs/adr-0.0.36-tests.txt` |
| Validator fail-closed scope | `uv run gz validate --receipt-shape` | OK | Exit 0; no post-cutoff drift in current ledger across 10 scopes. Proof: `audit/proofs/validate-receipt-shape.txt` |
| Validator semantic tests | `uv run python -m unittest tests.governance.test_validate_receipt_shape` | OK | 7 post-cutoff fail-closed + pre-cutoff waiver behavior tests pass. Proof: `audit/proofs/adr-0.0.36-tests.txt` |
| Waiver list schema/closure | `python -c "load waivers; check added_under set"` | OK | 42 entries, all `added_under == OBPI-0.0.36-04-historical-self-close-waivers`. Proof: `audit/proofs/waiver-list.txt` |
| AGENTS.md matrix collapse | `grep` for universal-attestation language | OK | Universal rule present at L256-258 and § Universal OBPI Attestation (ADR-0.0.36, GHI #342); no `Self-closeable` cell. Proof: `audit/proofs/agents-md-matrix-grep.txt` |
| Skill prose sweep | `rg -in 'self-clos' .gzkit/skills/` | WARN | OBPI-05 named scope clean; one residue surface (`gz-obpi-specify/assets/OBPI_BRIEF-template.md`) outside OBPI-05 scope still references self-close. Tracked: GHI #487. Proof: `audit/proofs/skills-self-clos-grep.txt` |

Symbols: OK = passed, WARN = warning (non-blocking discrepancy), FAIL = blocking.

## Dataset Spot Examples

Live runtime-gate predicate (collapsed to constant):

```python
def _requires_human_obpi_attestation(
    parent_adr: str | None,
    parent_lane: str,
    brief_frontmatter: Mapping[str, Any] | None = None,
) -> bool:
    ...  # docstring
    return True
```

Validator clean across all 10 scopes:

```
Validated: manifest, surfaces, ledger, instructions, briefs, documents,
personas, frontmatter, version, taxonomy
[OK] All validations passed (10 scopes).
```

Waiver-list closure constraint:

```
waiver count: 42
all added_under: ['OBPI-0.0.36-04-historical-self-close-waivers']
```

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | OK — all 5 OBPIs `attested_completed`; 29/29 REQs covered; ledger Layer-2 proof complete |
| Doctrine Integrity (matrix collapse) | OK — AGENTS.md universal-attestation rule binding; runtime gate `return True`; no live matrix `Self-closeable` cell |
| Mechanical Defense (validator) | OK — `gz validate --receipt-shape` fail-closed; 7 semantic tests pin pre/post-cutoff behavior |
| Waiver Discipline | OK — 42 entries; closed-set under OBPI-0.0.36-04; new entries refused without waiver-extension ADR |
| Documentation Alignment | WARN — one residue surface outside OBPI-05's named scope (GHI #487); named OBPI-05 scope is clean |
| Risk Items Resolved | OK (with one tracked non-blocking shortfall) |

## Evidence Index

Proof logs co-located under `audit/proofs/`:

- `audit/proofs/runtime-gate-source.txt` — `_requires_human_obpi_attestation` collapsed predicate source
- `audit/proofs/adr-0.0.36-tests.txt` — 20 tests passing (13 runtime-gate universality + 7 validator receipt-shape)
- `audit/proofs/validate-receipt-shape.txt` — `gz validate --receipt-shape` clean across 10 scopes
- `audit/proofs/waiver-list.txt` — waiver-list closure constraint output
- `audit/proofs/agents-md-matrix-grep.txt` — AGENTS.md universal-attestation language grep
- `audit/proofs/skills-self-clos-grep.txt` — skill prose sweep result (residue surface flagged)

Ledger proof (Layer 2) — 41 events scoped to `ADR-0.0.36-universal-obpi-attestation` in `.gzkit/ledger.jsonl`, including 5 `obpi_completed` (one per OBPI), 5 `attested` events with `by: Jeffry`, gate_checked entries for Gates 1-4, and the final `lifecycle_transition` from `Proposed` to `Completed` (2026-05-18T10:00:58Z).

## Recommendations

- **Shortfall 1 (non-blocking, tracked):** `.gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md` line 50 carries `Agent may self-close after presenting evidence`. This template scaffolds new OBPI briefs and would seed doctrine-violating prose. The runtime gate already refuses the action the template scaffolds (so no runtime hole exists), but a fresh brief drafted from this template misleads the author.
  - **Severity:** non-blocking (template residue, not runtime defect). The runtime gate is the authoritative enforcement point and is correct.
  - **Routing:** filed as **GHI #487** (`defect`, `tech-debt` — template-only, not `runtime`). Eligible for direct-fix per AGENTS.md § Defect-fix routing (≤10 lines, single file, in-flight).
  - **Remedy:** collapse the template's lite/heavy branches to a single `Human attestation required` rail; bump `gz-obpi-specify` skill-version; `gz agent sync control-surfaces` to propagate.
- **Class-of-failure observation (for future ADR doctrine sweeps):** OBPI-0.0.36-05 enumerated its skill prose sweep as a hand-curated file list; the residue surface (`gz-obpi-specify`) was missed by scope-definition rather than by error. The class-fix is to author universal-doctrine sweeps as `rg -in '<pattern>' .gzkit/ .claude/ .github/` evidence-scope rather than hand-enumerated allowed-paths. Captured in GHI #487's class-of-failure section; class-level remediation is out of scope for this audit and would be a separate ADR/OBPI if pursued.

## Attestation

**Agent attestation (audit-side):** This audit verifies ADR-0.0.36's five claims are delivered with reproducible evidence. The Layer-2 ledger proof is complete (all 5 OBPIs `attested_completed` by Jeffry, 29/29 REQs covered, lifecycle transitioned to `Completed`); the runtime gate's collapse to `return True` is structurally confirmed; the validator's fail-closed scope passes both live ledger validation and 7 semantic test fixtures; the waiver list's closure constraint holds (42 entries, all under OBPI-0.0.36-04); and the AGENTS.md matrix collapse is verbatim binding. One residue surface (`gz-obpi-specify` template) carries deprecated language but is outside OBPI-0.0.36-05's named scope and does not breach runtime enforcement; it is tracked as GHI #487 for separate remediation.

Signed: pipeline-orchestrator persona via Claude agent relay — 2026-05-18

**Operator attestation (audit-validation):** _Awaiting operator verbatim `accept audit` or `verify audit` per `.gzkit/skills/gz-adr-audit/SKILL.md` § Step 8.2. The verbal ack IS the Gate-5 attestation; the agent relays it into the validated receipt's `attestation_text` field._

Signed: _<operator name & date — pending operator verbatim ack>_
