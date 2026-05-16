# AUDIT_PLAN — ADR-0.0.33-agent-control-surface-fidelity

> **Trust model:** Layer 2 (ledger consumption). Layer 1 OBPI tests + receipts
> already produced proof on each OBPI completion; this audit verifies that
> the ledger proof is complete and reproducible, and demonstrates the
> integrated capability through live commands.

## Scope

- **ADR:** ADR-0.0.33-agent-control-surface-fidelity (lite mode / **heavy** lane / **foundation** kind)
- **Lifecycle transition:** Completed → Validated
- **OBPIs covered:** OBPI-0.0.33-01 through OBPI-0.0.33-05 (all 5 attested_completed)
- **Anchor commit:** 5c62a11
- **Current HEAD:** f7d1e66

## Claims extracted from ADR § Decision

1. **Bullet retention** — Mechanical/Promotable bullets in `advisory-rules-audit.md` present verbatim in per-turn surface. Validator: `gz validate --bullet-retention`.
2. **Surface weight regression** — direction-binding (no growth past snapshot 1768 lines, now floor at 1859); green ≤ 1800, yellow 1801–2200, red >2200. Validator: `gz validate --surface-weight`.
3. **Pointer integrity** — every `> See [...](path#anchor)` lift pointer resolves; every lifted-pedagogy page carries a `<!-- lifted-from: -->` back-pointer. Validator: `gz validate --pointer-anchors`.
4. **Loading-scenario reachability** — every Mechanical/Promotable bullet reachable from a declared loading scenario. Advisory until ADR-0.0.34 lands the registry. Validator: `gz validate --scenario-reachability`.
5. **Composite** — `gz validate --surface-fidelity` runs all four; wired into `gz check`; cheap subset (1, 2, 3) in pre-commit.

## Checks

| # | Check | Command / Method | Layer | Expected |
|---|-------|------------------|-------|----------|
| 1 | Ledger completeness | `uv run gz adr audit-check ADR-0.0.33` | L2 | PASS, 5/5 OBPIs, 27/27 REQs covered |
| 2 | REQ coverage parity | `uv run gz covers ADR-0.0.33 --json` | L1 | 100% covered, 0 uncovered |
| 3 | Invariant 1 — bullet-retention CLI | `uv run gz validate --bullet-retention` | L1 | exit 0, clean |
| 4 | Invariant 2 — surface-weight CLI | `uv run gz validate --surface-weight` | L1 | exit 0, clean |
| 5 | Invariant 3 — pointer-anchors CLI | `uv run gz validate --pointer-anchors` | L1 | exit 0, clean |
| 6 | Invariant 4 — scenario-reachability CLI | `uv run gz validate --scenario-reachability` | L1 | exit 0, advisory stderr |
| 7 | Composite — surface-fidelity CLI | `uv run gz validate --surface-fidelity` | L1 | exit 0, all four ran |
| 8 | CLI flag registration | `gz validate --help` | L1 | all 5 flags present |
| 9 | Pre-commit cheap-subset hook | `.pre-commit-config.yaml` greps | L1 | `surface-fidelity-cheap` registered, no `--scenario-reachability` |
| 10 | `gz check` composite wiring | `src/gzkit/commands/quality.py` | L1 | `("Surface fidelity", run_surface_fidelity_audit)` step present |

## Persona dispatch evidence

The ADR's parent attestation block (line 231 of the ADR) records that
`spec-reviewer` and `quality-reviewer` were dispatched as independent
subagents during the OBPI-0.0.33-05 closeout immediately prior to this
audit ceremony:

- **spec-reviewer verdict:** CLEAN — 27/27 REQs covered by 71 REQ-derived tests under independent persona dispatch.
- **quality-reviewer verdict:** COHERENT — composite is a thin orchestrator, CLI dispatch uniform, Era-1/Era-2 contract honored.
- **narrator:** drives the Value Demonstration section of this AUDIT.md (Step 3).
- **implementer:** NOT dispatched (no code written in an audit ceremony).

The audit ceremony is the gate immediately downstream of those completion-time
reviews; per the SKILL.md Layer 2 trust model, re-running spec-reviewer /
quality-reviewer would duplicate Layer-1 work done within the last commit.
The audit's job is to verify ledger proof + demonstrate value, not to
re-score what the completion ceremony just scored.

## Risk focus

- **Bullet-retention reaches into rendered surface** — even after the OBPI-0.0.33-01 in-flight remediation (BUCKET_3_ROOTS self-perpetuation fix), the validator's failure mode is silent regression if the scorecard and per-turn surface drift in opposite directions. Verified by reproducing exit 0 on current tree.
- **Surface weight is a one-way ratchet** — floor at 1859 lines; this audit only verifies current state passes, not the long-term direction. (Recalibration cadence: 6 months minimum, against operational evidence — see ADR § Negative consequences.)
- **Scenario reachability is advisory in Era 1** — exits 0 with stderr advisory. Era 2 (post-ADR-0.0.34) will harden this to fail-closed once the registry is authored.

## Demonstration plan (Step 3 — MANDATORY)

The ADR's product surface is the five `gz validate --<scope>` flags + composite + pre-commit hook. Demonstration runs each flag against the live tree, capturing real output to `proofs/`.

## Outputs

- `audit/AUDIT.md` — annotated audit with Feature Demonstration, execution log, evidence index, summary table
- `audit/AUDIT_PLAN.md` — this file
- `audit/proofs/*.txt` — captured command output (one file per check)
