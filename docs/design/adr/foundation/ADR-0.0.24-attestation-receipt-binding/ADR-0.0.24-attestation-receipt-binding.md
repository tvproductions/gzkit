---
id: ADR-0.0.24-attestation-receipt-binding
status: Validated
kind: foundation
semver: 0.0.24
lane: heavy
parent:
date: 2026-04-25
---

# ADR-0.0.24-attestation-receipt-binding: Attestation Receipt Binding

## Persona

`main-session` + `implementer`. Heavy-lane runtime contract change to the
attestation surface; methodical TDD discipline, atomic edits per behavior
increment, complete units rather than half-finished plumbing.

## Why foundation tier?

Without this ADR, attestation claims bind to narrative recall — an agent says "tests pass" without any tamper-evident proof, and the gzkit governance chain has no defense against fabricated evidence or training-corpus-drifted claims.

This ADR authors a port: the attestation-to-receipt-ID binding contract that every claim-emitting surface (closeout, complete, emit-receipt) must honor.

## Intent

Promote the inline ARB receipt-ID requirement on heavy-lane attestation from
"the citing agent must verify" (a narrative-trust pathway) to a mechanical
fail-closed check at receipt-emission time. AGENTS.md § Attestation today
states that the citing agent must verify the receipt exists and the
`exit_status` matches the claim — but no code enforces it. A heavy-lane
attestation lacking valid `arb-…` IDs, or citing IDs that don't resolve
in the ledger, currently records as narrative-only without rejecting.

The Opus 4.7 system card (§ 2.3.6.2 "Skipped cheap verification" + § 2.3.6.4
"Dishonest when caught") and the GPT-5.5 Apollo evaluation (§ 9.2: 29% lying
about completing an Impossible Coding Task) both document the same shape at
the model level: claiming-completion-without-cheap-verification is a
high-frequency failure mode at the current capability frontier. gzkit's
mechanical surface for closing this vector at the governance layer is the
ARB middleware; this ADR makes the binding fail-closed instead of advisory.

## Decision

1. Extend `gz validate` with `--attestation-receipts` scope that, given an
   attestation string, parses it for `arb-…` receipt IDs, looks each up in
   the ARB receipts directory (`artifacts/receipts/<run_id>.json` resolved
   via `gzkit.arb.paths.receipts_root()`), and asserts:
   - The receipt file exists and parses as JSON conforming to its declared
     schema (`gzkit.arb.lint_receipt.v1` or `gzkit.arb.step_receipt.v1`)
   - Its `exit_status == 0`
   - Its canonical claim category — derived from the receipt shape
     (`arb-ruff-*` => `lint`; `arb-step-<name>-*` => `<name>` keyed to
     `CANONICAL_STEP_COMMANDS`) — matches the category named adjacent to
     the citation (e.g., `lint:` adjacent to an `arb-ruff-…` receipt).
2. Wire the new scope into `gz obpi complete --attestation-text …` and
   `gz adr emit-receipt … --attestor …` as a pre-emission gate.
3. Lane behavior:
   - **Heavy lane**: fail-closed (exit 3) on any unresolved or
     status-mismatched receipt.
   - **Foundation kind**: same as heavy regardless of lane (per § Lane &
     Kind Attestation Matrix).
   - **Lite-lane non-foundation**: warn-only, preserving existing narrative
     behavior.
4. Update AGENTS.md § Attestation: replace "the citing agent must verify"
   with "the receipt-binding gate verifies"; the attesting human (Gate 5)
   still attests the work, but the receipt-existence verification is
   mechanical.
5. Receipts the gate cites for its own enforcement appear in the ledger
   under a new `arb-meta-receipt-bind-…` family — self-attesting evidence
   that the gate fired on the attestation it ratified.

## Non-Goals

1. **No emergency-skip flag.** No `--skip-receipt-binding` or equivalent
   bypass. The gate is the contract; an emergency-skip path reintroduces the
   narrative-trust pathway this ADR exists to close. A future GHI may revisit
   if operational evidence forces it.
2. **No git-pre-receive enforcement.** Receipt binding lands at the same
   layer as receipt emission (the ledger entry itself), not at the push that
   records it. Pre-receive hooks are Layer-3 derived checks per
   `docs/governance/state-doctrine.md`; this ADR keeps enforcement at
   Layer 2.
3. **No fail-closed on lite-lane non-foundation.** Lite-lane attestation
   today legitimately accepts narrative-only for non-contract work.
   Tightening lite without prior narrative-to-receipt migration breaks
   existing flows. Warn-only on lite preserves the existing covenant while
   tightening heavy/foundation.

## Consequences

### Positive

- Closes the narrative-trust pathway AGENTS.md § Attestation currently
  acknowledges and lives with. T2 ledger-of-truth becomes the single
  source for "this claim was attested with verifiable evidence."
- Prevents the GHI #290-class attestation-payload-synthesis vector at a
  second layer (the TTY/`ATTEST` confirmation gate is the first; this is
  the receipt-binding gate).
- Makes "Skipped cheap verification" mechanically detectable on heavy-lane
  attestations — the gate fires before the receipt event is written.

### Negative

- A heavy-lane attestation that legitimately uses a brand-new ARB receipt
  family the validator does not know about will fail-closed until the
  validator's `CANONICAL_STEP_COMMANDS` map is extended. Mitigated by the
  existing extend-only rule on `CANONICAL_STEP_COMMANDS` (AGENTS.md §
  Canonical invocations).
- Adds a small validation cost to every heavy-lane completion. Acceptable
  given the alternative (narrative claims with no mechanical floor).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 1
- Observability: 1
- Lineage: 0
- Dimension Total: 6
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 4

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.24-01: Implement `gz validate --attestation-receipts` scope (parse, ledger lookup, claim/category match) with table-driven unit tests
- [ ] OBPI-0.0.24-02: Wire the gate into `gz obpi complete` and `gz adr emit-receipt` with lane-conditional fail/warn behavior and a new `arb-meta-receipt-bind-…` self-attesting receipt family
- [ ] OBPI-0.0.24-03: Update AGENTS.md § Attestation, the attestation rule mirror, and `docs/governance/arb-middleware.md` to reflect the mechanical contract
- [ ] OBPI-0.0.24-04: BDD coverage — heavy-lane `@REQ-…`-tagged scenarios in `features/` covering valid receipts, missing receipts, status-mismatched receipts, and lite-lane warn-only

## Q&A Transcript

Authored from a system-card review session (2026-04-25). External evidence:
GPT-5.5 Apollo § 9.2 (29% Impossible Coding Task lie rate) + Opus 4.7 § 2.3.6
six-pattern failure taxonomy. Both converge on "claimed completion without
cheap verification" as the dominant frontier failure mode; gzkit's mechanical
backstop is the ARB middleware, currently advisory at the citation layer.

## Evidence

- [ ] Validator: `src/gzkit/governance/trust_audits.py` (or equivalent home)
- [ ] CLI: `src/gzkit/commands/obpi.py`, `src/gzkit/commands/adr_emit_receipt.py`
- [ ] Doc: `AGENTS.md` § Attestation, `docs/governance/arb-middleware.md`
- [ ] Tests: `tests/governance/test_attestation_receipt_binding.py`
- [ ] BDD: `features/attestation_receipt_binding.feature`

## Alternatives Considered

1. **Keep advisory, raise visibility via reviewer checklist** — rejected.
   Opus 4.7 § 2.3.6.2 documents a model writing six memory files about a
   verification rule and re-violating it. Discipline-only enforcement is
   demonstrably insufficient at the current capability frontier.
2. **Fail-closed on all lanes including lite** — rejected. Lite-lane
   attestation today legitimately accepts narrative-only for non-contract
   work; tightening it without prior narrative-to-receipt migration breaks
   existing flows. Warn-only on lite preserves the existing covenant while
   tightening heavy/foundation.
3. **Move enforcement to a git pre-receive hook on the remote** — rejected.
   Hook-on-remote is a Layer-3 derived check; the receipt-binding decision
   belongs at the same layer as receipt emission so the ledger entry
   itself is gated, not the push that records it.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.24 | Completed | Jeffry Babb | 2026-05-02 | Completed — ADR-0.0.24 ships the receipt-binding gate as a mechanical fail-closed check on heavy-lane and foundation-kind attestations, replacing the prior narrative-trust pathway. All four OBPIs Completed; gz validate --attestation-receipts registered with --lane and --kind axes. Closeout receipts: lint arb-ruff-ea49a20864a040bd91f641190bb8c093, tests arb-step-unittest-948af27ee6064019bff20ee5afe3ead0 (3946 tests OK), typecheck arb-step-typecheck-b6fba06b1efc4d98addf63b1ad03ad3b, mkdocs arb-step-mkdocs-899f852a2d5d4b6c824cd3984bc85d8d. In-flight defects fixed during evidence-gathering: insights record schema (line 25), gz-deps-upgrade operator manpage and skills-index link, test_instruction_audit cp1252-vs-utf8 write_text encoding (4 call sites), quality.py _expand_allowed_paths cross-platform path separator via as_posix(). |
| 0.0.24 | Validated | Jeffry Babb | 2026-05-02 | accept audit — ADR-0.0.24 validated; ledger proof complete (4/4 OBPIs attested_completed), all five Decision-section capabilities demonstrated against live receipts (resolved arb-ruff-983215b7e2d64c15bded4f5ca5fe64bc, missing-fail-closed exit 3, lite-feature warn-only exit 0, claim/category mismatch exit 3, foundation-kind fail-closed regardless of lane exit 3). Audit-check exit 0 under interim covers-backfill heuristic demotion (commit dc52d537, GHI #385) with proper-fix tracked at GHI #386 (teach heuristic about Ceremony: gz-git-sync trailers). Mechanical checks: lint clean (arb-ruff-983215b7e2d64c15bded4f5ca5fe64bc), unittest 3946 OK (arb-step-unittest-74aad395ecee4b81910d50b3f61363c1). Coverage 14/19 REQs (73.7%) with 5 advisory uncovered REQs in OBPI-0.0.24-03 doc-update OBPI by design (doc REQs validated by mkdocs build --strict, not unit tests). AUDIT.md and 6 proof files captured under audit/. Audit-trail GHIs: GHI #385 (interim demotion, landed dc52d537), GHI #386 (proper roll-forward), GHI #387 (skill phrasing conflation: 'attest completed' vs 'accept audit'). |
