---
id: ADR-pool.obpi-doctrine-mechanization-coherence
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.obpi-doctrine-mechanization-coherence: OBPI Doctrine-Mechanization Coherence (skill doctrine ↔ CLI exit codes)

## Status

Pool

## Intent

OBPI pipeline doctrine — encoded in `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, brief-authoring guidance, and AGENTS.md attestation rules — names stage-gate contracts ("the pipeline does not advance to Stage 4 until parity holds", "every brief carrying REQs that would be exercised by tests/** lists tests/** in Allowed Paths"). The doctrine binds agent behavior. It does not bind CLI exit codes. The gap means each fresh OBPI re-discovers the same class of failure: an agent reads the skill, follows the contract, then completes the brief through `gz obpi complete` even when the named precondition doesn't hold — because no CLI verb fail-closes on the contract the skill named.

Two concrete instances of this defect class were surfaced during ADR-0.0.23 / OBPI-0.0.23-02 closeout on 2026-04-30 (GHI #367):

- **REQ→@covers parity gate is not CLI-enforced.** `gz-obpi-pipeline` Stage 3 Phase 1b prescribes: *"The pipeline does not advance to Stage 4 until parity holds."* `gz obpi precomplete` does not consult `gz covers`; `gz obpi complete` will write the brief to `Completed` even with `summary.uncovered_reqs > 0`. OBPI-0.0.23-01 shipped with `status: Completed` while `gz covers ADR-0.0.23` reports OBPI-0.0.23-01 has 3 reqs / 0 covered. The skill says Stage 4 should have been blocked; the runtime did not block it. The agent's own attestation acknowledged the skip ("Parity-gate skip (3 uncovered REQs) consolidated into follow-up GHI per operator-decided route B"), confirming the doctrine was named and the runtime did not enforce it.
- **Brief-template Allowed-Paths drift between siblings.** OBPI-0.0.22-06 lists `tests/governance/**` in Allowed Paths and ships a 7-test sentinel (`tests/governance/test_security_sensitivity_rule.py`). OBPI-0.0.23-02 (same ADR series, foundation rule + cross-link + scorecard, same week) excludes `tests/` from Allowed Paths and carries `Tests added: n/a`. The two briefs share parent-ADR test surface but pick opposite test postures, with no fail-closed validator catching the drift. An operator authoring sibling-N+1 picks whichever earlier example they happen to read.

Both are the same architectural absence at different surface pairs. Skill doctrine names a Stage 3 precondition (parity, template coherence, attestation rigor); CLI exit codes do not honor it; agent honor-system fills the gap unevenly. The defect becomes load-bearing at closeout: a brief that completed with uncovered REQs or with sibling-drifted Allowed-Paths produces a ledger entry whose Layer-1↔Layer-2 metadata is consistent but whose underlying contract was never enforced — the same shape as GHI #290's agent-synthesized-payload vector, displaced one layer up.

This ADR opens the design conversation for binding skill-named per-OBPI contracts to CLI fail-closed exit codes. Two enforcement surfaces are in scope: `gz obpi precomplete` (Stage 3 gate) and a new `gz validate --brief-template` scope (authoring-time gate). Both share a common pattern — extract the contract from doctrine, mechanize it as an exit-code branch, define the explicit waiver shape for legitimately-exempt cases.

## Decision

_(Pool — design conversation in progress. Concrete decision items to be authored on promotion. Open surface decisions:)_

- **Parity-gate enforcement boundary**: refuse in `gz obpi precomplete` (Stage 3 boundary; matches the skill's "does not advance to Stage 4" framing), **vs. refuse in `gz obpi complete`** (final boundary; catches the skip even if precomplete is bypassed), **vs. both** (defense in depth at the cost of two error-message surfaces).
- **Doc-shape REQ escape mechanism**: a `--allow-uncovered-doc-reqs` flag on `gz obpi precomplete` plus doctrine in AGENTS.md naming when the flag is acceptable, **vs. extend brief frontmatter** with an `obpi-shape: doc` declaration that mechanically waives the parity gate (no flag needed; the brief itself declares its shape), **vs. require doc-shape REQs to carry the existing `[doc]` syntax in the Acceptance Criteria block** (already supported by `compute_coverage`'s `include_doc=False` filter; just promote it to the parity-gate predicate).
- **Brief-template validator scope folding**: standalone `gz validate --brief-template` (clearer audit narrative; matches the layered-validator pattern from `--documents`, `--surfaces`, `--insights-shape`), **vs. fold into `gz validate --documents`** (existing scope; fewer surfaces).
- **Allowed-Paths waiver shape**: reuse `data/behave_coverage_waivers.json` shape (per-brief entries with rationale + expiry), **vs. inline the waiver as `tests-deferred: <rationale>` brief frontmatter** (per-brief locality; reviewer sees the waiver next to the Allowed Paths declaration), **vs. require a foundation-attested ADR rule** for any brief deferring tests (highest ceremony; smallest vibing surface).
- **Allowed-Paths drift detection rule**: heuristic match (briefs whose REQs cite "test" / "scenario" / "@covers" without `tests/**` glob), **vs. structural rule** (REQ-derived shape — any brief whose acceptance criteria reference behavioral verification must list `tests/**` or carry the waiver), **vs. explicit `tests-required: true|false` brief frontmatter** that the validator pins.
- **Stage-3 precomplete error-message form**: cite `gz covers <slug>` output verbatim with the recommended remediation ("re-run with --allow-uncovered-doc-reqs" / "decorate the missing test"), **vs. terse exit-code-only failure** (operator runs the diagnostic themselves), **vs. structured JSON error** that downstream tooling can parse.

## Alternatives Considered

_(Pool — full rejected-alternatives table to be authored on promotion. Sketch:)_

1. **Leave both gaps as agent-honor-system enforcement.** Lowest ceremony cost; matches the current state. Rejected at routing time: the GHI-367 surface evidence shows the honor-system has already produced the failure mode it's nominally guarding against — OBPI-0.0.23-01 shipped Completed with uncovered REQs because the agent following the skill read "the pipeline does not advance" as descriptive rather than prescriptive when the runtime didn't block. Doctrine that binds behavior without binding exit codes is the canonical Layer-3 derived view becoming source-of-truth pattern (`docs/governance/state-doctrine.md` § Architectural Boundary 6).
2. **Enforce parity-gate via post-completion audit only** (e.g. `gz adr audit-check` flags ADRs whose child OBPIs completed with uncovered REQs). Rejected: post-hoc detection produces the GHI #348-shape silent-state-demotion pattern — the brief is already Completed, the ledger event is already emitted, the audit catches drift after the fact. The whole point of a Stage 3 gate is to refuse at the boundary, not to detect after.
3. **Promote both gaps via in-flight `fix(...)` commits** rather than via this ADR's design conversation. Rejected at routing time: each gap requires a new CLI flag (`--allow-uncovered-doc-reqs`) plus doctrine for when the flag is acceptable, or a new validator scope (`--brief-template`) plus a waiver shape — heavy-lane new capability per `.claude/rules/cli.md` § Adding CLI Features. Direct fix is the wrong route per AGENTS.md § Defect-fix routing; the appropriate route is design conversation → planned increment.
4. **Two separate pool ADRs, one per gap** (`obpi-precomplete-parity-gate`, `brief-template-validator-scope`). Rejected at routing time: the two gaps share the architectural signature — skill-named contract not bound to CLI exit code — and folding them into one design conversation lets the rejected-alternatives table for one gap inform the other. Two separate ADRs would force two relationship matrices and two promotion ceremonies for the same architectural class.
5. **Skill-level enforcement only** (extend `gz-obpi-pipeline` Stage 3 with a verbatim agent-run parity check that calls `gz covers --json --output <path>` and parses the file via a UTF-8-reconfigured helper per `.gzkit/rules/cross-platform.md` § Windows-safe helper patterns, then self-reports the result). Rejected: skill-level enforcement is a Layer-3 derived check, not a Layer-1/Layer-2 mechanical witness; relies on agent honor-system rather than fail-closed CLI exit codes. The architectural absence is precisely *that the agent layer is the only enforcement layer*.

## Notes

**Sibling routing receipts:**

- GHI #367 (consolidated three doctrine-mechanization gaps surfaced under OBPI-0.0.23-02) closes `superseded` against this ADR. Of the three gaps the GHI consolidated, two route here:
  - Gap 1 (REQ→@covers parity gate not CLI-enforced) — § Intent first concrete instance.
  - Gap 2 (Brief-template Allowed-Paths drift between siblings) — § Intent second concrete instance.
  - Gap 3 (`gz covers OBPI-X --json` short-form returns empty entries) — verified non-reproducing on 2026-04-30. Both forms returned 3 entries; the GHI's reproducer included the string `(3 REQs found)` which is not present in the actual `gz covers` text output. Disposition documented in the close comment as withdrawn-as-misobserved within the consolidated `superseded` close.

**Promotion criteria:** before `gz adr promote --kind foundation`, the open surface decisions in § Decision must be resolved with operator preference. Specifically: parity-gate enforcement boundary (precomplete vs complete vs both), doc-shape escape mechanism (flag vs frontmatter vs `[doc]` syntax promotion), and waiver shape (waivers JSON vs frontmatter vs ADR rule). Promotion semver candidate: next foundation slot at promotion time.

**Adjacent mechanization precedents:**

- `gz validate --insights-shape` (GHI #358) — validator scope added to fail-close on agent-insights drift; the same shape applies to brief-template drift here.
- `gz validate --advisory-scorecard` (GHI #322 era) — validator scope that pins a doctrine surface to a scorecard row; direct precedent for promoting an authoring-time contract to a fail-closed check.
- `data/behave_coverage_waivers.json` — the waiver-shape precedent for Gap 2's Allowed-Paths exception mechanism.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
