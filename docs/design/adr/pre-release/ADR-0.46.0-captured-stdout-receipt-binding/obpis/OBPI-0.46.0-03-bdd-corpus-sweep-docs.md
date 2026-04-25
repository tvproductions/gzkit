---
id: OBPI-0.46.0-03-bdd-corpus-sweep-docs
parent: ADR-0.46.0-captured-stdout-receipt-binding
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.46.0-03-bdd-corpus-sweep-docs: BDD + corpus sweep + docs

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.46.0-captured-stdout-receipt-binding/ADR-0.46.0-captured-stdout-receipt-binding.md`
- **Checklist Item:** #3 — "BDD scenarios + manpage and doc updates; one-time corpus sweep to bind existing heavy-lane manpages, with a corpus-frozen waiver list for any binding deferred to follow-up GHIs"

**Status:** Draft

## Objective

Author behave coverage, sweep the existing heavy-lane manpage corpus to bind EXAMPLES blocks (or waive with rationale), and ship updated AGENTS.md / runbook / arb-middleware docs.

## Lane

**Heavy** — Gate 3 docs and Gate 4 BDD.

## Allowed Paths

- `features/manpage_example_binding.feature`
- `features/steps/manpage_example_binding_steps.py`
- `docs/user/manpages/**` — corpus sweep: rebind every heavy-lane manpage's EXAMPLES blocks
- `data/manpage_example_waivers.json` — close out waivers for any unbound corpus entries with explicit rationale
- `AGENTS.md` — § Prime Directive item 2 cross-references the new validator
- `docs/governance/arb-middleware.md` — captured-stdout binding section
- `docs/user/runbook.md` — manpage authoring flow updated
- `docs/user/manpages/gz-validate.md` — `--manpage-examples` flag documented
- `docs/user/manpages/gz-arb.md` (or wherever ARB manpage lives) — `--capture` flag and `rebind-manpage` verb documented
- `docs/design/adr/pre-release/ADR-0.46.0-captured-stdout-receipt-binding/**`

## Denied Paths

- `src/gzkit/arb/**` — owned by OBPI-01
- `src/gzkit/governance/trust_audits.py`, `src/gzkit/commands/arb_rebind.py` — owned by OBPI-02
- Any path not listed

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `features/manpage_example_binding.feature` exists with `@REQ-0.46.0-NN-MM` scenario tags covering REQs from OBPI-01 and OBPI-02.
2. REQUIREMENT: Scenarios run against real `gz arb step --capture`, real `gz validate --manpage-examples`, and real `gz arb rebind-manpage` (not mocked subprocess); fixture manpages and fixture proofs.
3. REQUIREMENT: Corpus sweep: every existing heavy-lane manpage has either (a) bound EXAMPLES blocks (rebound during this OBPI), or (b) an explicit entry in `data/manpage_example_waivers.json` with rationale and a follow-up GHI link.
4. REQUIREMENT: After the sweep, `gz validate --manpage-examples` exits 0 against the live manpage corpus.
5. REQUIREMENT: AGENTS.md § Prime Directive item 2 expands one line to reference `gz validate --manpage-examples` as the mechanical floor for the "real CLI output, not placeholders" rule.
6. REQUIREMENT: `docs/governance/arb-middleware.md` gains a § "Captured-stdout binding" subsection documenting the `--capture` flag, the proofs storage layout, and the binding comment convention.
7. REQUIREMENT: `gz cli audit` exits 0; `mkdocs build --strict` exits 0; `gz validate --behave-req-tags` exits 0.
8. REQUIREMENT: NEVER include the operator's personal email anywhere in the corpus sweep edits, manpage examples, or docs.
9. REQUIREMENT: NEVER hand-write a "captured" stdout into a manpage; every binding must come from a real captured receipt via `gz arb rebind-manpage`.

> STOP-on-BLOCKERS: if OBPI-01 and OBPI-02 have not landed, STOP.

## Discovery Checklist

- [ ] Parent ADR § Decision (all items) and § Consequences (Negative — backwards compat)
- [ ] OBPI-0.46.0-01 + -02 evidence
- [ ] `docs/user/manpages/` — current corpus
- [ ] AGENTS.md § Prime Directive item 2 — exact text to extend
- [ ] `.claude/rules/gate5-runbook-code-covenant.md`

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded
### Gate 2: TDD
- [ ] behave passes; full test suite still passes
### Code Quality
- [ ] Lint clean
### Gate 3: Docs (Heavy)
- [ ] mkdocs strict + cli audit pass
### Gate 4: BDD (Heavy)
- [ ] All scenarios pass; req-tags clean
### Gate 5: Human (Heavy)
- [ ] Required

## Verification

```bash
uv run gz lint
uv run gz cli audit
uv run mkdocs build --strict
uv run -m behave features/manpage_example_binding.feature
uv run gz validate --behave-req-tags
uv run gz validate --manpage-examples  # should exit 0 against live corpus after sweep
```

## Acceptance Criteria

- [ ] REQ-0.46.0-03-01: Given the corpus-sweep work, when `gz validate --manpage-examples` runs against the live manpage corpus, then exit 0.
- [ ] REQ-0.46.0-03-02: Given any unbound block deferred to follow-up, when `data/manpage_example_waivers.json` is read, then the entry has a rationale field and a GHI link field.
- [ ] REQ-0.46.0-03-03: Given AGENTS.md § Prime Directive item 2, when reviewed, then the prose names `gz validate --manpage-examples` as the mechanical floor.
- [ ] REQ-0.46.0-03-04: Given the post-edit repo, when `gz cli audit` and `mkdocs build --strict` run, then both exit 0.
- [ ] REQ-0.46.0-03-05: Given the BDD scenarios, when behave runs, then every REQ from OBPI-01 and OBPI-02 has at least one passing tagged scenario.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** behave + tests pass
- [ ] **Gate 3:** mkdocs strict + cli audit pass
- [ ] **Gate 4 (BDD):** scenarios pass
- [ ] **Code Quality:** clean
- [ ] **OBPI Acceptance:** Heavy = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD)
```text
# behave + test suite output
```

### Code Quality
```text
# lint output
```

### Gate 3 (Docs)
```text
# mkdocs build --strict, gz cli audit
```

### Gate 4 (BDD)
```text
# behave + req-tags
```

### Gate 5 (Human)
```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified (corpus sweep):
- BDD scenarios added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy lane requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
