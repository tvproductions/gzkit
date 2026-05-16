# AUDIT — ADR-0.0.33-agent-control-surface-fidelity

| Field | Value |
|-------|-------|
| ADR | ADR-0.0.33-agent-control-surface-fidelity |
| Mode / Lane / Kind | lite / heavy / foundation |
| Lifecycle target | Completed → Validated |
| Anchor commit | 5c62a11 |
| Current HEAD | f7d1e66 |
| Audit ceremony | gz-adr-audit (SKILL.md v6.9.0, Layer 2) |
| Persona (driver) | pipeline-orchestrator |
| Audit date | 2026-05-15 |

## Verdict: READY-TO-VALIDATE

All 10 planned checks PASS. Ledger proof complete (5/5 OBPIs `attested_completed`, 27/27 REQs covered). All five `gz validate --<scope>` flags exit 0 on the live tree. Composite, `gz check` integration, and pre-commit hook wiring all confirmed present. No shortfalls identified; no defects filed.

The ADR delivers an operator-runnable, mechanically-enforced four-invariant fidelity contract over the per-turn agent control surface, plus a composite scope and a pre-commit cheap-subset hook. The doctrine page (`docs/governance/agent-control-surface-fidelity-doctrine.md`) is anchored by working validators, not narrative.

## Feature Demonstration (Step 3 — MANDATORY)

> **Narrator framing.** Before ADR-0.0.33, "did our diet pass silently drop a binding rule?" had no structural answer — it was a question only an audit could ask, and only after harm. After ADR-0.0.33, that question is a single CLI invocation. The four invariants make the agent control surface's fidelity to its declared rules observable at *compile time*, not at audit time. The composite makes "is the surface still honest?" a one-line check that pre-commit and `gz check` both run on the operator's behalf.

### Capability 1 — Bullet retention is mechanically enforced

**Operator value:** A diet pass on `AGENTS.md` or `CLAUDE.md` that silently drops a Mechanical/Promotable bullet from the per-turn surface is now caught by the validator before it lands.

**Command run:**

```
$ uv run gz validate --bullet-retention
Validated: bullet_retention

✓ All validations passed (1 scopes).
$ echo $?
0
```

Proof: [`proofs/bullet-retention.txt`](proofs/bullet-retention.txt). This is the GHI #327 backstop running clean — the same validator that, at OBPI-0.0.33-01 completion, surfaced 41 Era-1 gaps. Post-remediation the surface is honest against the scorecard.

### Capability 2 — Surface weight is direction-bound

**Operator value:** Agent control surface cannot regress past its tested floor. Bloat is fail-closed in pre-commit; recalibration is a deliberate, attested act.

**Command run:**

```
$ uv run gz validate --surface-weight
Validated: surface_weight

✓ All validations passed (1 scopes).
$ echo $?
0
```

Proof: [`proofs/surface-weight.txt`](proofs/surface-weight.txt). Floor at 1859 lines per `data/surface_weight_floor.json`; current corpus at floor. Warning bands (green ≤ 1800, yellow 1801–2200, red >2200) provisional pending 6-month recalibration.

### Capability 3 — Pointer integrity is bidirectional

**Operator value:** Lift-to-rationale pages and `> See [...]` blockquotes are kept in sync. A broken anchor or a missing `<!-- lifted-from: -->` back-pointer becomes a compile-time failure.

**Command run:**

```
$ uv run gz validate --pointer-anchors
Validated: pointer_anchors

✓ All validations passed (1 scopes).
$ echo $?
0
```

Proof: [`proofs/pointer-anchors.txt`](proofs/pointer-anchors.txt). At OBPI-0.0.33-03 completion this validator detected 6 real pointer-drift findings; those have since been remediated and the validator runs clean against the live tree.

### Capability 4 — Scenario reachability ships as advisory (Era 1)

**Operator value:** The Era-1 advisory surfaces orphan-bullet risk without false fail-closed noise; Era 2 hardens to fail-closed once ADR-0.0.34 lands the loading-scenarios registry.

**Command run:**

```
$ uv run gz validate --scenario-reachability
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
Validated: scenario_reachability

✓ All validations passed (1 scopes).
$ echo $?
0
```

Proof: [`proofs/scenario-reachability.txt`](proofs/scenario-reachability.txt). Era-1 advisory contract honored: exit 0 + stderr advisory per REQ-0.0.33-04-01.

### Capability 5 — Composite + pre-commit + `gz check` integration

**Operator value:** "Is the agent control surface still honest?" is one line. Pre-commit catches three-of-four invariants before a commit even forms; `gz check` rolls the full four-of-four into the standard quality sweep.

**Composite command run:**

```
$ uv run gz validate --surface-fidelity
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
Validated: surface_fidelity

✓ All validations passed (1 scopes).
$ echo $?
0
```

Proof: [`proofs/surface-fidelity-composite.txt`](proofs/surface-fidelity-composite.txt). Composite runs all four constituents in declared order; exit code is worst-of-four; current tree clean.

**Pre-commit wiring (cheap subset 1, 2, 3):**

```
      - id: surface-fidelity-cheap
        name: surface-fidelity cheap subset (invariants 1, 2, 3)
        entry: uv run gz validate --bullet-retention --surface-weight --pointer-anchors
        language: system
        pass_filenames: false
```

Proof: [`proofs/pre-commit-wiring.txt`](proofs/pre-commit-wiring.txt). Single CLI call (per REQ-0.0.33-05-05); `--scenario-reachability` deliberately excluded (per REQ-0.0.33-05-04).

**`gz check` integration:**

```
src/gzkit/commands/quality.py:301:        run_surface_fidelity_audit,
src/gzkit/commands/quality.py:323:        ("Surface fidelity", run_surface_fidelity_audit),
src/gzkit/quality.py:632:def run_surface_fidelity_audit(project_root: Path) -> QualityResult:
```

Proof: [`proofs/gz-check-wiring.txt`](proofs/gz-check-wiring.txt). Composite folded into the default quality sweep.

## Execution Log

| # | Check | Result | Evidence |
|---|-------|:------:|----------|
| 1 | Ledger completeness (`gz adr audit-check`) | ✓ | [`proofs/adr-audit-check.txt`](proofs/adr-audit-check.txt) — 5/5 OBPIs PASS, 27/27 REQs covered (100.0%) |
| 2 | REQ coverage parity (`gz covers`) | ✓ | [`proofs/req-coverage.txt`](proofs/req-coverage.txt) — 27/27 covered, 0 uncovered |
| 3 | Invariant 1 — `--bullet-retention` | ✓ | [`proofs/bullet-retention.txt`](proofs/bullet-retention.txt) — exit 0 |
| 4 | Invariant 2 — `--surface-weight` | ✓ | [`proofs/surface-weight.txt`](proofs/surface-weight.txt) — exit 0 |
| 5 | Invariant 3 — `--pointer-anchors` | ✓ | [`proofs/pointer-anchors.txt`](proofs/pointer-anchors.txt) — exit 0 |
| 6 | Invariant 4 — `--scenario-reachability` | ✓ | [`proofs/scenario-reachability.txt`](proofs/scenario-reachability.txt) — exit 0 + Era-1 advisory |
| 7 | Composite — `--surface-fidelity` | ✓ | [`proofs/surface-fidelity-composite.txt`](proofs/surface-fidelity-composite.txt) — exit 0 |
| 8 | CLI flag registration | ✓ | [`proofs/cli-help-flags.txt`](proofs/cli-help-flags.txt) — all 5 flags in `gz validate --help` |
| 9 | Pre-commit cheap-subset hook | ✓ | [`proofs/pre-commit-wiring.txt`](proofs/pre-commit-wiring.txt) — `surface-fidelity-cheap` registered, `--scenario-reachability` correctly absent |
| 10 | `gz check` composite step | ✓ | [`proofs/gz-check-wiring.txt`](proofs/gz-check-wiring.txt) — `("Surface fidelity", run_surface_fidelity_audit)` step present |

## Evidence Index

| Artifact | Path |
|----------|------|
| Audit plan | [`AUDIT_PLAN.md`](AUDIT_PLAN.md) |
| Ledger audit-check | [`proofs/adr-audit-check.txt`](proofs/adr-audit-check.txt) |
| REQ coverage (JSON) | [`proofs/req-coverage.txt`](proofs/req-coverage.txt) |
| `--bullet-retention` output | [`proofs/bullet-retention.txt`](proofs/bullet-retention.txt) |
| `--surface-weight` output | [`proofs/surface-weight.txt`](proofs/surface-weight.txt) |
| `--pointer-anchors` output | [`proofs/pointer-anchors.txt`](proofs/pointer-anchors.txt) |
| `--scenario-reachability` output | [`proofs/scenario-reachability.txt`](proofs/scenario-reachability.txt) |
| `--surface-fidelity` (composite) | [`proofs/surface-fidelity-composite.txt`](proofs/surface-fidelity-composite.txt) |
| CLI flag registration | [`proofs/cli-help-flags.txt`](proofs/cli-help-flags.txt) |
| Pre-commit hook wiring | [`proofs/pre-commit-wiring.txt`](proofs/pre-commit-wiring.txt) |
| `gz check` step wiring | [`proofs/gz-check-wiring.txt`](proofs/gz-check-wiring.txt) |

## Summary Table

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Completeness** | ✓ | All 5 OBPIs attested_completed; 27/27 REQs covered; all 5 gates pass |
| **Integrity** | ✓ | Ledger proof present for every OBPI; anchor commits clean; no drift detected |
| **Alignment** | ✓ | ADR § Decision claims map 1:1 to OBPI briefs and to landed validators; composite invokes all four in declared order |
| **Value demonstration** | ✓ | All 5 capabilities exercised via live `gz validate` calls; output captured to `proofs/` |
| **Persona dispatch** | ✓ | spec-reviewer (CLEAN), quality-reviewer (COHERENT) recorded in parent ADR attestation block at OBPI-05 completion; narrator dispatched here for Value Demonstration framing |
| **Defects filed** | — | None — no shortfalls identified |

## Shortfalls

None. All checks pass; ledger proof is complete and reproducible; integrated capability demonstrated.

## Persona dispatch evidence

| Persona | Role in audit | Verdict / output | Source |
|---------|---------------|------------------|--------|
| pipeline-orchestrator | Driver of this ceremony (audit COMPLETED→VALIDATED) | Ceremony executed in declared order: plan → ledger verify → live demonstration → AUDIT.md → recommend ceremony to parent | This document |
| spec-reviewer | Independent REQ-tracing | CLEAN — 27/27 REQs covered by 71 REQ-derived tests | ADR-0.0.33 attestation block, line 231 (recorded at OBPI-05 completion immediately prior to this audit) |
| quality-reviewer | Structural coherence | COHERENT — composite is thin orchestrator, CLI dispatch uniform, Era-1/Era-2 contract honored | ADR-0.0.33 attestation block, line 231 |
| narrator | Value Demonstration framing | Above "Feature Demonstration" section composed in operator-value terms | This document |
| implementer | NOT dispatched | n/a — no code written in an audit ceremony per SKILL.md | — |

## Attestation

**Agent signature (audit driver):** pipeline-orchestrator persona, executed under Claude Opus 4.7. The ledger proof for the underlying OBPIs records human (`Jeffry Babb`) attestation at each OBPI's Gate-5 closeout (2026-05-15 / 2026-05-16). This audit verifies that proof is present and reproducible, and demonstrates the integrated feature working on the live tree.

**Human attestation for ADR-level Validated transition:** PENDING — to be relayed via `gz adr audit-begin` → operator verbal `accept audit` / `verify audit` → `gz adr emit-receipt … --event validated` → `gz adr audit-end`. This audit ceremony stops here per the parent dispatch contract; the parent will relay this audit's recommendation to the operator for verbatim attestation.

## Recommendation to parent

**Proceed with the `gz adr audit-begin` → operator-attestation → `gz adr emit-receipt --event validated` → `gz adr audit-end` ceremony.** All preconditions are met:

- Ledger proof complete (5/5 OBPIs, 27/27 REQs)
- All five validators exit 0 against the live tree
- Composite, `gz check`, and pre-commit wiring all confirmed
- No shortfalls; no defects filed
- No code changes required

Suggested attestation payload (operator verbatim placeholder + agent enrichment):

```
"<operator verbatim ack> — ADR-0.0.33 Validated: 5/5 OBPIs attested_completed, 27/27 REQs covered, all four invariants + composite exit 0 on live tree (proofs at docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/audit/proofs/); pre-commit cheap-subset hook registered; gz check Surface-fidelity step wired; persona dispatch verdicts CLEAN / COHERENT preserved from OBPI-05 closeout."
```
