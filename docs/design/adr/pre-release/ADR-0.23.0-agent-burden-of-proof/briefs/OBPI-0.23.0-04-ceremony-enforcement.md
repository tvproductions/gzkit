<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.23.0-04 — Ceremony Skill Enforcement

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/ADR-0.23.0-agent-burden-of-proof.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.23.0-04 — "Ceremony skill enforcement — closeout skill blocks on missing product proof and reviewer assessment"`

## ADR ALIGNMENT

1. **Critical Constraint:**
   > ADR states: "Implementations MUST ensure the burden of proof falls on the completing agent at the END of the run."
   >
   > In my own words: The ceremony skill is the last line of defense before human attestation. It must present the agent's case (closing arguments, product proof, reviewer assessment) and block if the case is incomplete.

2. **Integration Points:**
   > This OBPI must integrate with: `.claude/skills/gz-adr-closeout-ceremony/SKILL.md`, `.claude/skills/gz-closeout/SKILL.md`, `src/gzkit/commands/common.py` (closeout form rendering)

3. **Anti-Pattern:**
   > A failed implementation would: add more manual checklist items that agents can tick without engaging. The ceremony must present the evidence (closing arguments, product proof table, reviewer verdict) so the human can judge substance, not checkboxes.

4. **Alignment Check:**
   > - [x] **YES** — Proceed. Reasoning: The ceremony skill is the orchestration point where all evidence converges for human judgment.

## OBJECTIVE

Update the closeout ceremony skill to: (a) present each OBPI's closing argument (not just a checklist), (b) display the product proof status table from `gz closeout`, (c) include the reviewer agent's assessment, and (d) block the ceremony if product proof is missing or no reviewer assessment exists. The human attestor sees a defense brief, not a rubber-stamp form.

## ROLE

**Agent Identity:** Ceremony design architect

**Success Behavior:** Transform the ceremony from a checklist into a defense presentation where the agent makes its case and the human judges it.

**Failure Behavior:** Adding more checkbox items to the existing ceremony without changing the fundamental dynamic from declaration to defense.

## DEPENDENCIES

- **OBPI-01, -02, -03 must be complete** before this OBPI begins. However, 01-03 are fully independent of each other and can execute in parallel. This OBPI is the integrator that wires their outputs into the ceremony.
- Effective dependency depth is 2 (parallel tier + integrator), not 4 (serial chain).

```text
  OBPI-01 (template) ──┐
  OBPI-02 (gate)     ──┼──► OBPI-04 (ceremony integration)
  OBPI-03 (reviewer) ──┘
```

## ASSUMPTIONS

- The ceremony skill is a SKILL.md file that guides agent behavior during closeout
- The closeout form (`ADR-CLOSEOUT-FORM.md`) can be enhanced to include the defense brief

## NON-GOALS

- Automating human judgment — the ceremony presents evidence, the human decides
- Changing the attestation response format (Completed / Partial / Dropped)

## CHANGE IMPACT DECLARATION

- [x] **YES** — External contract changes: ceremony skill behavior, closeout form format.

## LANE

Heavy — Ceremony contract change (new presentation format, new blocking conditions).

## EXTERNAL CONTRACT

- Surface: Closeout ceremony skill, ADR-CLOSEOUT-FORM.md template
- Impacted audience: agents running closeout, human attestors

## ALLOWED PATHS

- `.claude/skills/gz-adr-closeout-ceremony/SKILL.md`
- `.claude/skills/gz-closeout/SKILL.md`
- `src/gzkit/commands/common.py`
- `tests/test_closeout_ceremony.py`
- `features/closeout_ceremony.feature`
- `features/steps/closeout_ceremony_steps.py`
- `docs/user/commands/closeout.md`
- `docs/user/manpages/closeout.md`

## REQUIREMENTS (FAIL-CLOSED)

1. Ceremony skill presents each OBPI's closing argument in sequence, not just a checklist
1. Product proof status table is displayed with per-OBPI proof type and status
1. Reviewer agent assessment is presented: promises-met, docs-quality, closing-argument-quality
1. Ceremony blocks (does not prompt for attestation) if: any OBPI missing closing argument, any OBPI missing product proof, no reviewer assessment available
1. ADR-CLOSEOUT-FORM.md template includes "Defense Brief" section with closing arguments, proof table, and reviewer verdict
1. Closeout manpage documents the new ceremony flow

## EDGE CASES

- Lite-lane-only ADR: ceremony still requires closing arguments and product proof, but reviewer assessment is advisory (warning, not blocker)
- Reviewer assessment is negative but not blocking: human sees the concerns and can still attest if they judge the work acceptable
- Partial product proof (some OBPIs have it, some don't): ceremony blocks only on the missing ones

## QUALITY GATES

### Gates 1-4: Implementation

- [ ] Gate 1 (ADR): Intent recorded in brief
- [ ] Gate 2 (TDD): Unit tests pass, coverage >= 40%
- [ ] Gate 3 (Docs): Manpage and runbook updated, `mkdocs build --strict` passes
- [ ] Gate 4 (BDD): Behave scenarios pass
- [ ] Code Quality: Lint, type check clean

### Verification Commands (Concrete)

```bash
# Prove ceremony skill references closing arguments
grep -c "Closing Argument\|closing argument" .claude/skills/gz-adr-closeout-ceremony/SKILL.md
# Expected: >= 2

# Prove ceremony blocks on missing product proof
grep "block\|BLOCK\|exit 1" .claude/skills/gz-adr-closeout-ceremony/SKILL.md | grep -i proof
# Expected: blocking condition documented

# Prove closeout form template has Defense Brief section
grep "Defense Brief" src/gzkit/commands/common.py
# Expected: match in closeout form renderer

# End-to-end: dry-run closeout shows defense brief
uv run gz closeout ADR-0.23.0 --dry-run
# Expected: output includes Closing Arguments, Product Proof Table, Reviewer Assessment sections
```

### Gate 5: Human Attestation

- [ ] Agent presents the updated ceremony flow with a real ADR example
- [ ] **STOP** — Agent waits for human attestation

## Closing Argument

*To be authored at completion from delivered evidence.*
