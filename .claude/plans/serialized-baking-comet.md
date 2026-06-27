# Plan: OBPI-0.0.74-08 — gz-mx Skill and mx-mode Rule

## Context

OBPI-0.0.74-08 delivers the two human/agent-facing companions to the MX marker
mechanism that prior OBPIs in ADR-0.0.74 landed:

- **gz-mx skill** — the operator's interface to the maintenance hangar. Tool-skill
  Invariant 1 requires every CLI verb to have a wielding skill. `gz mx` (enter/exit)
  landed in OBPI-0.0.74-04/05 but has no skill yet; nobody is authorized to wield it.
- **mx-mode rule** — tells agents to honor the marker AND that the PRIME DIRECTIVE binds
  the whole hangar session. Naked doctrine without a binding rule file is rationalized away.

ADR-0.0.74 Decision item #8 (verbatim): "The gz-mx skill + AGENTS.md binding rule. The
operator operates the skill; the skill invokes the tool; nobody shells out (gzkit is a
meta-harness inside the vendor harness). The AGENTS.md rule tells agents to honor the marker
and that the PRIME DIRECTIVE binds the whole session."

REQ coverage (3 REQs, all `req_atomic:` — each is one indivisible artifact):
- REQ-0.0.74-08-01 [SUPPORT] — gz-mx skill exists
- REQ-0.0.74-08-02 [SUPPORT] — mx-mode rule exists with honor-marker + PRIME-DIRECTIVE-binds
- REQ-0.0.74-08-03 [BEHAVIOR] — gz_command "mx" resolves to the real `gz mx` verb

## Files

### CREATE
- `.gzkit/skills/gz-mx/SKILL.md` — canonical gz-mx skill (edit here; sync propagates)
- `.gzkit/rules/mx-mode.md` — canonical mx-mode binding rule

### MODIFY
- `tests/commands/test_skills.py` — add REQ-0.0.74-08-03 covering tests
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-08-mx-skill-and-agents-rule.md` — evidence recording

### GENERATED (by gz agent sync)
- `.claude/skills/gz-mx/SKILL.md` — Claude vendor mirror
- `.agents/skills/gz-mx/SKILL.md` — Codex vendor mirror
- `.github/skills/gz-mx/SKILL.md` — Copilot vendor mirror
- `.claude/rules/mx-mode.md` — Claude vendor mirror
- `.agents/rules/mx-mode.md` — Codex vendor mirror
- `.github/rules/mx-mode.md` — Copilot vendor mirror

## Implementation Steps

### Step 1: RED — write failing tests first

Add two test cases to `tests/commands/test_skills.py` in `TestSkillCommands`:

**Test A — skill catalogs (REQ-0.0.74-08-01, passive cover for 08-02 via existence)**
```python
@covers("REQ-0.0.74-08-01")
def test_gz_mx_skill_catalogs_after_init(self) -> None:
    """gz-mx skill ships in the canonical catalog and appears in gz skill list."""
    with _InitFromTemplate():
        runner = CliRunner()
        result = runner.invoke(main, ["skill", "list", "--json"])
        self.assertEqual(result.exit_code, 0)
        skills = json.loads(result.output)
        names = [s["name"] for s in skills]
        self.assertIn("gz-mx", names)
```

**Test B — gz_command resolves (REQ-0.0.74-08-03)**
```python
@covers("REQ-0.0.74-08-03")
def test_gz_mx_skill_gz_command_resolves(self) -> None:
    """gz-mx skill's gz_command 'mx' resolves to the registered gz mx verb."""
    with _InitFromTemplate():
        runner = CliRunner()
        # gz validate --cli-alignment exits 0 only when every gz_command in
        # every SKILL.md resolves to a registered parser verb.
        result = runner.invoke(main, ["validate", "--cli-alignment"])
        self.assertEqual(result.exit_code, 0, result.output)
```

Watch both fail (assertion-level) before writing the artifacts.

### Step 2: CREATE `.gzkit/skills/gz-mx/SKILL.md`

Frontmatter shape mirrors gz-arb (sibling reference):
```yaml
---
name: gz-mx
persona: main-session
description: >
  Enter and exit the MX Maintenance Hangar — operator's interface to gz mx.
  Use when entering the hangar to perform governance repair, status-checking
  during a session, or clean exit when repair is complete.
  Operator operates the skill; the skill invokes gz mx; nobody shells out.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-06-27
model: haiku
gz_command: mx
metadata:
  skill-version: "1.0.0"
---
```

Body content (key sections):
- **Overview**: The MX Maintenance Hangar lets the operator repair governance
  surfaces that the guards themselves protect. While the hangar is open, most
  governance guards drop to advisory so the operator can fix governance itself.
  `gate5_invariants` and the PRIME DIRECTIVE still bind.
- **When to Use**: entering the hangar (governance repair session), checking
  hangar status mid-session, clean exit with re-enforcement
- **Workflow**: 1) `uv run gz mx enter` — open the hangar, 2) perform repair
  (governance surfaces, briefs, rules), 3) `uv run gz mx exit` — close and
  re-enforce all guards
- **Example**: enter + repair + exit sequence
- **Constraints**: Operator operates the skill; never shell out to `gz mx`
  directly. PRIME DIRECTIVE binds the entire hangar session.

### Step 3: CREATE `.gzkit/rules/mx-mode.md`

Frontmatter shape mirrors token-block-discipline (sibling reference):
```yaml
---
id: mx-mode
description: >
  Binding rule for MX hangar sessions — honor the marker, PRIME DIRECTIVE
  binds the whole session (ADR-0.0.74 Decision item #8).
paths:
  - "src/gzkit/mx/**"
  - ".gzkit/skills/gz-mx/**"
  - ".claude/hooks/mx-awareness.py"
  - "src/gzkit/mx/awareness.py"
---
<!-- rule-version: 1.0.0 -->
```

Body content (binding rule — verbatim doctrine):
- **Honor the marker**: read `.gzkit/mx-active` before every action; if it
  exists, the hangar is open — guards are advisory, not blocking
- **PRIME DIRECTIVE binds the entire session**: even in the hangar,
  ownership is not relaxed. Fix what you know AND what you find. "Not my
  work" / "out of scope" stays forbidden in the bay. Guards are advisory
  so the operator can repair governance itself — not so agents can ignore
  defects they find in flight.
- **Operate the skill, not the shell**: the operator uses `gz-mx` (the
  skill); the skill invokes `gz mx`; agents do not shell out to `gz mx` directly
- **Do Not** section: never invoke `gz mx enter/exit` directly in shell;
  never treat advisory guards as license to defer visible defects; never
  conflate "guard dropped to advisory" with "PRIME DIRECTIVE suspended"

### Step 4: Run `uv run gz agent sync control-surfaces`

Propagates `.gzkit/skills/gz-mx/SKILL.md` and `.gzkit/rules/mx-mode.md`
to all vendor mirrors (`.claude/`, `.agents/`, `.github/`).

### Step 5: Verify (GREEN bar + quality gates)

```bash
uv run -m unittest tests.commands.test_skills.TestSkillCommands.test_gz_mx_skill_catalogs_after_init -v
uv run -m unittest tests.commands.test_skills.TestSkillCommands.test_gz_mx_skill_gz_command_resolves -v
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --cli-alignment
uv run gz validate --documents
uv run mkdocs build --strict
```

Also run the BDD gate (Heavy lane):
```bash
uv run -m behave --tags=@REQ-0.0.74-08-03 features/
```

## Disclosure (Plan-Before-Exploration ordering)

**Destination-in-mind before writing this plan:** Create a SKILL.md with
`gz_command: mx` and an mx-mode rule file with the honor-marker + PRIME-DIRECTIVE-binds
doctrine. This conclusion was formed during the discovery reads in Stage 1 of the pipeline.

**Rejected alternatives:**
- AGENTS.md body prose (rejected by the brief's denied paths — AGENTS.md invariant-coherence
  re-render surface makes this fragile; the scoped rule file is the correct landing pad)
- Embedding the rule in the skill (rejected — rule and skill are separate surfaces per
  tool-skill-runbook-alignment.md; the rule is agent-contract, the skill is operator-workflow)
- gz_command: "mx enter" (rejected — "mx" is the top-level subcommand group; enter/exit
  are sub-verbs the skill body describes; the frontmatter field declares the CLI parent)

## Verification

End-to-end:
1. All new tests GREEN (`test_gz_mx_skill_catalogs_after_init`, `test_gz_mx_skill_gz_command_resolves`)
2. `uv run gz skill list` shows `gz-mx`
3. `uv run gz validate --cli-alignment` exits 0
4. `uv run gz validate --documents` exits 0
5. `uv run gz validate --unscoped-rules` exits 0 (mx-mode.md carries `paths:`)
6. `uv run mkdocs build --strict` exits 0
7. Full unittest suite GREEN (no regressions)
