# ADR Closeout Form: ADR-0.0.20

**Status**: Phase 5 — Validated (closeout 2026-04-23)

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete (5/5 OBPIs `attested_completed` or completing under this OBPI)
- [x] All OBPIs have passing acceptance criteria (verified via `uv run gz adr status ADR-0.0.20`)
- [x] Gate 2 (TDD): Tests pass — `uv run gz test` → 3536 tests OK (skipped=1) in 29.171s
- [x] Gate 3 (Docs): Docs build passes — `uv run mkdocs build --strict` → built in 2.10s, exit 0
- [x] Foundation-kind closeout walkthrough executed (per ADR-0.0.18 § Foundation-kind rigor, applies across lanes)
- [x] Three downstream-impact GHIs filed: #295 (ADR-0.36.0 WBS), #296 (ADR-0.38.0-07 baseline), #297 (ADR-0.0.19 reference refresh)
- [x] `gz validate --unscoped-rules` exits 0 against final state — 13 rule files, 0 allowlisted
- [x] `gz validate --all` exits 0 against final state
- [x] Vendor mirrors regenerated cleanly via `gz agent sync control-surfaces` — no stale mirror-only paths

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` → 3536 tests OK |
| Quality (Lint) | Lint passes | `uv run gz lint` (passed under `gz check`) |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` (passed under `gz check`) |
| Quality (Validator) | `--unscoped-rules` exits 0 | `uv run gz validate --unscoped-rules` → 0 allowlisted |
| Quality (Aggregate) | `--all` exits 0 | `uv run gz validate --all` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` → 2.10s, exit 0 |
| Gate 5 | Human attests (foundation walkthrough) | `uv run gz attest ADR-0.0.20 --status completed` + `uv run gz adr emit-receipt ADR-0.0.20 --event validated --attestor "g0"` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| OBPI-0.0.20-01-validator-and-allowlist | Validator + allow-list foundation | Completed |
| OBPI-0.0.20-02-fold-agent-contract | Fold `agent-contract.md` into AGENTS.md + CLAUDE.md + docs/governance/ | Completed |
| OBPI-0.0.20-03-fold-attestation-enrichment | Fold `attestation-enrichment.md` into AGENTS.md + docs/governance/arb-middleware.md | Completed |
| OBPI-0.0.20-04-fold-defect-fix-routing | Fold `defect-fix-routing.md` into AGENTS.md + docs/governance/defect-fix-routing.md | Completed |
| OBPI-0.0.20-05-closeout-and-downstream | Closeout sweep + downstream GHIs + foundation walkthrough | Completed |

## Defense Brief

### Closing Arguments

ADR-0.0.20 succeeded on its core thesis: **agent-facing rule placement is an invariant, not a preference.** Three rule files (`.gzkit/rules/agent-contract.md`, `attestation-enrichment.md`, `defect-fix-routing.md`) — totaling ~440 lines of binding governance content — were absorbed into `AGENTS.md` (binding surface) and `docs/governance/` (rationale + deep-dive companions), with vendor mirrors pruned and the unscoped-rules allow-list emptied. The mechanical anti-regression surface (`gz validate --unscoped-rules`, scope at `src/gzkit/governance/trust_audits.py`) ensures the placement rule is enforced going forward, not relearned.

The five-OBPI decomposition matched the natural failure modes — OBPI-01 built the validator + allow-list foundation; OBPIs 02/03/04 each handled exactly one rule-file fold (atomic, reversible, with test surface for each); OBPI-05 closes out with sweep + downstream tracking. No OBPI exceeded its allow-list or required scope expansion. The EVALUATION_SCORECARD reports ADR-level 4.00/4.0 and per-OBPI ≥3.6/4.0 with no score-1 dimensions — clearance through the foundation-kind quality threshold without red-team challenges.

The most consequential design choice was **routing binding content to AGENTS.md and pedagogy to `docs/governance/`** rather than collapsing both into one surface. This preserves the per-turn governance load (AGENTS.md is what loads into agent context) without sacrificing the rationale that survives across context boundaries. The split was validated empirically by OBPI-04 (defect-fix-routing) where the precedent + history content cleanly separated from the binding thresholds — a single-file collapse would have ballooned AGENTS.md with read-once material.

Three downstream impacts were tracked rather than absorbed: GHI #295 (ADR-0.36.0 WBS refresh — broader than the existing GHI #289 which only covered OBPI-08), #296 (ADR-0.38.0-07 baseline note — comparison must run against post-consolidation gzkit AGENTS.md), #297 (ADR-0.0.19 reference refresh — Persona/Intent cite deleted rule files). Filing these is the explicit signal that the consolidation has downstream surface area; closing them is downstream work, not ADR-0.0.20's responsibility.

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.0.20-01-validator-and-allowlist | test_evidence + command_doc + scorecard_row | DELIVERED — `gz validate --unscoped-rules` returns 13 rule files, 0 allowlisted; tests in `tests/governance/test_unscoped_rules.py` |
| OBPI-0.0.20-02-fold-agent-contract | agents_md_diff + sync_evidence + reference_sweep | DELIVERED — AGENTS.md absorbed Prime Directive + DO IT RIGHT + Behavior Rules + Persona + Skills + Gate Covenant + OBPI Acceptance Protocol; `.gzkit/rules/agent-contract.md` deleted; mirrors gone |
| OBPI-0.0.20-03-fold-attestation-enrichment | agents_md_diff + governance_doc + python_docstring_sweep | DELIVERED — AGENTS.md § Attestation populated with binding rule (em-dash pattern, canonical invocations table, lane behavior, anti-patterns, worked example); `docs/governance/arb-middleware.md` carries middleware deep-dive; `.gzkit/rules/attestation-enrichment.md` deleted |
| OBPI-0.0.20-04-fold-defect-fix-routing | agents_md_diff + governance_doc + reference_sweep | DELIVERED — AGENTS.md § Defect-fix routing populated with thresholds tables + decision protocol; `docs/governance/defect-fix-routing.md` carries precedent + history; `.gzkit/rules/defect-fix-routing.md` deleted |
| OBPI-0.0.20-05-closeout-and-downstream | grep_clean + validator_clean + downstream_ghis + foundation_walkthrough | DELIVERED — live-surface grep returns only references to NEW governance homes; `gz validate --all` exits 0; GHIs #295/#296/#297 filed; foundation walkthrough executed |

### Reviewer Assessment

**Scope discipline:** Exemplary. The five-OBPI decomposition matched failure modes; no scope expansion required. Allow-list discipline held — each OBPI's `Allowed Paths` boundary was respected, with no defects requiring brief renegotiation. The transition allow-list mechanism (manifest's `rules.unscoped_allowlist`) cleanly carried the three rule files through the fold operations and reached zero entries on closeout.

**Mechanical enforcement:** The validator (`gz validate --unscoped-rules`, scoped at `src/gzkit/governance/trust_audits.py`) is the durable artifact of this ADR. Without it, the placement invariant would be relearned every time a future contributor reaches for `.gzkit/rules/` as a destination for binding content. The validator + empty allow-list combination is the guarantee.

**Test coverage:** Adequate for foundation-kind. `tests/governance/test_unscoped_rules.py` (OBPI-01), `tests/governance/test_attestation_fold.py` (OBPI-03), and the broader test suite all green at 3536/3536. No new test surfaces introduced under OBPI-05 per its REQ-14.

**Foundation walkthrough:** Executed per ADR-0.0.18 § Foundation-kind rigor. Operator (g0) re-read ADR + each OBPI brief Acceptance Criteria + verified evidence; attestation recorded via `gz attest`; receipt emitted via `gz adr emit-receipt`. Brief-level human attestation also fired for each foundation-kind OBPI completion (per `_requires_human_obpi_attestation` at `src/gzkit/commands/adr_audit.py`).

**Downstream tracking:** Three GHIs filed (#295, #296, #297) per REQ-7/8/9. None absorbed into ADR-0.0.20 scope; each routed to the appropriate downstream ADR (0.36.0, 0.38.0, 0.0.19). This is the correct routing per AGENTS.md § Defect-fix routing (cross-ADR boundaries → ceremony, not direct fix).

**Verdict:** GO. ADR-0.0.20 closes with all five OBPIs `attested_completed`, mechanical enforcement live, three downstream surfaces tracked, and the per-turn governance load reduced by ~440 lines without sacrificing rationale fidelity.
