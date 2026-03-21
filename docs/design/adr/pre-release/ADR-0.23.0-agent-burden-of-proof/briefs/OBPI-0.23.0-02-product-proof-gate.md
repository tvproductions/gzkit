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

## EDGE CASES

- OBPI delivers only internal refactoring with no operator-facing surface: docstring on changed public interfaces satisfies the gate
- Multiple OBPIs contribute to the same manpage: each OBPI's contribution is independently detectable
- ADR with no Heavy OBPIs: product proof gate still runs but accepts docstring-only proof

## QUALITY GATES

### Gates 1-4: Implementation

- [ ] Gate 1 (ADR): Intent recorded in brief
- [ ] Gate 2 (TDD): Unit tests pass, coverage >= 40%
- [ ] Gate 3 (Docs): `mkdocs build --strict` passes
- [ ] Gate 4 (BDD): Behave scenarios pass
- [ ] Code Quality: Lint, type check clean

### Gate 5: Human Attestation

- [ ] Agent presents `uv run gz closeout ADR-0.23.0 --dry-run` showing product proof table
- [ ] **STOP** — Agent waits for human attestation

## Closing Argument

*To be authored at completion from delivered evidence.*
