---
id: OBPI-0.23.0-02-product-proof-gate
parent: ADR-0.23.0-agent-burden-of-proof
item: 2
lane: Lite
status: Completed
---
<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.23.0-02 — Product Proof Gate

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/ADR-0.23.0-agent-burden-of-proof.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.23.0-02 — "Product proof gate — automated runbook/manpage/docstring checks block closeout"`

## ADR ALIGNMENT

1. **Critical Constraint:**
   > ADR states: "Implementations MUST ensure the burden of proof falls on the completing agent at the END of the run."
   >
   > In my own words: The closeout command must programmatically verify that operator-facing documentation exists for each OBPI's delivered capability before allowing closeout to proceed.

2. **Integration Points:**
   > This OBPI must integrate with: `src/gzkit/cli.py` (closeout_cmd), `src/gzkit/quality.py` (new check function), `docs/user/runbook.md`, `docs/user/manpages/`

3. **Anti-Pattern:**
   > A failed implementation would: check only that files exist without verifying they contain substantive content relevant to the delivered increment. File-existence checks are necessary but not sufficient.

4. **Alignment Check:**
   > - [x] **YES** — Proceed. Reasoning: Automated product proof checks create a hard gate that agents cannot bypass, directly enforcing the burden of proof.

## OBJECTIVE

Add automated product proof validation to `gz closeout` that checks, for each OBPI in the target ADR: (a) a runbook entry referencing the capability, OR (b) a manpage entry with current CLI synopsis, OR (c) meaningful docstrings on public interfaces introduced. At least one form of product proof must exist per OBPI. Closeout exits 1 if missing.

## ROLE

**Agent Identity:** Quality gate implementer

**Success Behavior:** Build a product proof checker in `quality.py` that `closeout_cmd()` invokes, producing a clear report of what's proven and what's missing.

**Failure Behavior:** Building a check that only verifies file existence without content relevance, or a check that's easily bypassed by adding boilerplate.

## ASSUMPTIONS

- OBPIs that are purely internal (no operator-facing surface) can satisfy product proof via docstrings alone
- Runbook and manpage paths follow existing conventions (`docs/user/runbook.md`, `docs/user/manpages/*.md`)
- The check produces a table showing proof status per OBPI

## NON-GOALS

- Natural language quality assessment of documentation (that's the reviewer agent's job)
- Enforcing specific documentation structure beyond presence and non-emptiness

## CHANGE IMPACT DECLARATION

- [x] **YES** — External contract changes: `gz closeout` gains new validation behavior and output.

## LANE

Heavy — CLI contract change (new exit behavior, new output).

## EXTERNAL CONTRACT

- Surface: `gz closeout ADR-X.Y.Z` CLI command
- Impacted audience: agents and operators running closeout

## ALLOWED PATHS

- `src/gzkit/quality.py`
- `src/gzkit/cli.py`
- `tests/test_product_proof.py`
- `features/closeout_product_proof.feature`
- `features/steps/closeout_product_proof_steps.py`
- `docs/user/commands/closeout.md`

## REQUIREMENTS (FAIL-CLOSED)

1. New function `check_product_proof(adr_id)` in `quality.py` that scans for operator documentation per OBPI
1. `closeout_cmd()` invokes product proof check before proceeding; exits 1 with clear report if missing
1. Product proof types: runbook entry (keyword match), manpage (file existence + non-empty synopsis), docstring (public module/class/function docstrings for new code)
1. Output: table per OBPI showing proof type found or "MISSING"
1. BDD scenario: closeout with and without product proof

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.23.0-02-01: Given an ADR identifier, when `check_product_proof(adr_id)` is invoked, then it scans for operator documentation per OBPI and returns a structured per-OBPI proof status.
- [x] REQ-0.23.0-02-02: Given `closeout_cmd()` is invoked for an ADR, when it runs, then it invokes the product proof check before any closeout side-effects proceed.
- [x] REQ-0.23.0-02-03: Given a target ADR with at least one OBPI lacking product proof, when `closeout_cmd()` runs, then it exits 1 and emits a clear per-OBPI report identifying the missing proof.
- [x] REQ-0.23.0-02-04: Given an OBPI delivers an operator capability, when product proof is checked, then a runbook entry whose text references the capability is accepted as proof (keyword match).
- [x] REQ-0.23.0-02-05: Given an OBPI delivers a CLI command, when product proof is checked, then an existing manpage file with a non-empty synopsis is accepted as proof.
- [x] REQ-0.23.0-02-06: Given an OBPI delivers a public module/class/function, when product proof is checked, then a meaningful docstring on the introduced public interface is accepted as proof.
- [x] REQ-0.23.0-02-07: Given a closeout run, when the product proof check completes, then a per-OBPI table is emitted showing the proof type found or `MISSING` for each OBPI.
- [x] REQ-0.23.0-02-08: Given the closeout product proof feature, when BDD scenarios run, then both the with-proof and without-proof paths are exercised end-to-end.

## EDGE CASES

- OBPI delivers only internal refactoring with no operator-facing surface: docstring on changed public interfaces satisfies the gate
- Multiple OBPIs contribute to the same manpage: each OBPI's contribution is independently detectable
- ADR with no Heavy OBPIs: product proof gate still runs but accepts docstring-only proof

## QUALITY GATES

### Gates 1-4: Implementation

- [x] Gate 1 (ADR): Intent recorded in brief
- [x] Gate 2 (TDD): Unit tests pass, coverage >= 40%
- [x] Gate 3 (Docs): `mkdocs build --strict` passes
- [x] Gate 4 (BDD): Behave scenarios pass
- [x] Code Quality: Lint, type check clean

### Gate 5: Human Attestation

- [x] Agent presents `uv run gz closeout ADR-0.23.0 --dry-run` showing product proof table
- [x] **STOP** — Agent waits for human attestation

## Evidence

### Implementation Summary

- Files created: `tests/test_product_proof.py` (29 tests), `features/closeout_product_proof.feature` (3 BDD scenarios), `features/steps/closeout_product_proof_steps.py`
- Files modified: `src/gzkit/quality.py` (added `check_product_proof`, `ObpiProofStatus`, `ProductProofResult`), `src/gzkit/commands/closeout.py` (integrated product proof gate), `docs/user/commands/closeout.md`
- Validation commands run: `uv run gz lint`, `uv run gz typecheck`, `uv run gz test` (1920 pass), `uv run mkdocs build --strict`, `uv run -m behave features/closeout_product_proof.feature` (3/3 pass)
- Date completed: 2026-03-28

### Key Proof

```
$ uv run -m unittest tests.test_product_proof -v
Ran 29 tests in 0.008s — OK

$ uv run -m behave features/closeout_product_proof.feature
3 scenarios passed, 0 failed — closeout blocks on missing proof, allows with docstring proof, shows product_proof in JSON
```

## Closing Argument

We added `check_product_proof()` to `src/gzkit/quality.py` with three detection mechanisms (runbook keyword match, command doc existence, AST-parsed public docstrings) and integrated it into `closeout_cmd()` as a blocking gate. Operators running `uv run gz closeout ADR-X.Y.Z` now see a per-OBPI product proof table and cannot proceed when any OBPI lacks documentation proof. This matters because previously agents could declare completion without proving their work was documented — the gate makes rubber-stamp closeout impossible.
