# Plan: OBPI-0.0.29-04 — complexity-advisor Skill

## Context

**OBPI:** OBPI-0.0.29-04-complexity-advisor-skill
**Parent ADR:** ADR-0.0.29 (Complexity Advisor) — foundation, heavy lane
**Objective:** Author the `complexity-advisor` skill at `.gzkit/skills/complexity-advisor/SKILL.md`,
propagate to vendor mirrors, and cover all 9 REQs with `@covers`-decorated tests.

The CLI verb `gz complexity advise` is already registered (OBPI-03 complete). The manpage
exists at `docs/user/manpages/gz-complexity-advise.md`. The exemplar skill
`gz-complexity-distill` (same cluster) provides the shape reference.

## Files

**Create:**
- `.gzkit/skills/complexity-advisor/SKILL.md` — canonical skill
- `tests/skills/test_complexity_advisor.py` — REQ-derived tests

**Generate (via sync):**
- `.claude/skills/complexity-advisor/SKILL.md`
- `.agents/skills/complexity-advisor/SKILL.md`
- `.github/skills/complexity-advisor/SKILL.md`

**Read-only (consumed, not edited):**
- `.gzkit/skills/gz-complexity-distill/SKILL.md` — shape reference
- `.gzkit/rules/tool-skill-runbook-alignment.md` — Invariants 1, 2, 3
- `.gzkit/rules/skill-surface-sync.md` — version discipline
- `.gzkit/schemas/skill.schema.json` — frontmatter schema
- `docs/user/manpages/gz-complexity-advise.md` — cross-reference target
- `src/gzkit/cli/parser_artifacts.py` — verb registration check

## Steps

### Step 1: RED — Write failing tests

Create `tests/skills/test_complexity_advisor.py` with `@covers` decorators:

1. `test_frontmatter_validates_against_schema` — `@covers("REQ-0.0.29-04-01")`
   Parse SKILL.md frontmatter YAML; validate `skill-version` is `0.1.0`, `gz_command`
   is `complexity advise`, `description` contains trigger phrases.

2. `test_skill_body_documents_three_operator_moments` — `@covers("REQ-0.0.29-04-02")`
   Assert body contains sections/prose covering: (a) ad-hoc preview-before-fail,
   (b) auto-chain context, (c) intrinsic-attestation guidance.

3. `test_output_contract_declares_structured_prose_and_json` — `@covers("REQ-0.0.29-04-03")`
   Assert Output Contract section names structured prose as default form and `--json`
   as machine-readable mode.

4. `test_cross_references_runbook_and_manpage` — `@covers("REQ-0.0.29-04-04")`
   Assert body cross-references the runbook entry and manpage path.

5. `test_gz_command_resolves_to_registered_verb` — `@covers("REQ-0.0.29-04-05")`
   Extract `gz_command` from frontmatter; verify the CLI parser has it registered.

6. `test_vendor_mirrors_byte_identical_after_sync` — `@covers("REQ-0.0.29-04-06")`
   After sync, compare canonical skill against each vendor mirror for byte equality.

7. Additional tests for REQ-07 through REQ-09 are structural — REQ-07 is satisfied
   by the existence and `@covers` decoration of tests 1-6; REQ-08 is satisfied by
   never spawning the advisor subprocess in any test; REQ-09 is verified by asserting
   no email pattern in SKILL.md content.

All tests mocked at the subprocess boundary (REQ-08). No operator PII in fixtures (REQ-09).

### Step 2: GREEN — Author SKILL.md

Create `.gzkit/skills/complexity-advisor/SKILL.md` with:

**Frontmatter:**
- `name: complexity-advisor`
- `description:` with trigger phrases ("preview complexity advisor", "complexity diagnosis",
  "advisor recommendation", "what does the advisor say", "intrinsic complexity attestation")
- `category: code-quality`
- `lifecycle_state: active`
- `owner: gzkit-governance`
- `last_reviewed: 2026-05-06`
- `metadata.skill-version: "0.1.0"`
- `metadata.govzero-framework-version: "v6"`
- `metadata.govzero_layer: "Layer 3 - File Sync"`
- `gz_command: complexity advise`

**Body sections:**
- `# complexity-advisor` — intro paragraph
- `## When to Use` — three operator moments as triggers
- `## Operator Moments` — subsections for each:
  - `### Ad-hoc preview-before-fail` — `gz complexity advise <path>`, verbose preview,
    OEE-aligned preview-before-fail
  - `### Auto-chain context` — xenon-as-gate failure fires `gz complexity advise --auto-chain`,
    different presentation defaults, SKIP-bypass guard wiring preserved
  - `### Intrinsic-complexity attestation` — `@intrinsic_complexity` decorator vs
    `--attest-intrinsic` commit-time flag, both land at Gate 5
- `## Timeout and Failure Handling` — references OBPI-09's timeout/fail-open/logging
- `## Output Contract` — structured prose per-diagnosis block (metric, crossing band,
  archetype, doctrinal frame, proof range, recommended move); `--json` emits Pydantic
  serialization
- `## Commands` — canonical invocations
- `## Related` — cross-references runbook + manpage

### Step 3: Sync vendor mirrors

```bash
uv run gz agent sync control-surfaces
```

Verify post-sync diff is empty.

### Step 4: Run tests and quality checks

```bash
uv run -m unittest tests/skills/test_complexity_advisor.py -v
uv run gz lint
uv run gz typecheck
```

Fix any failures. Re-run until green.

### Step 5: Verify vendor mirror parity

```bash
diff .gzkit/skills/complexity-advisor/SKILL.md .claude/skills/complexity-advisor/SKILL.md
diff .gzkit/skills/complexity-advisor/SKILL.md .agents/skills/complexity-advisor/SKILL.md
diff .gzkit/skills/complexity-advisor/SKILL.md .github/skills/complexity-advisor/SKILL.md
```

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/skills/test_complexity_advisor.py -v
uv run gz validate --documents --surfaces
uv run gz agent sync control-surfaces
```

## Notes

- The `gz_command` field uses space-separated format (`complexity advise`) matching the
  existing `complexity distill` skill convention — not the hyphenated `complexity-advise`
  the brief's REQ-01 text mentions.
- The brief's STOP-on-BLOCKERS condition (OBPI-03 verb not registered) is resolved:
  `gz complexity advise --help` succeeds.
- The ADR mentions "OBPI-09 timeout-handling description" in the skill — the plan includes
  a dedicated Timeout section per ADR intent.
