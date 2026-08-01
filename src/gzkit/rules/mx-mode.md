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
<!-- rule-version: 1.0.1 -->

# MX Mode (Maintenance Hangar) (gzkit)

> **Rule version:** `1.0.1` — marker path aligned to `.gzkit/mx.json`; `e2d38c3c0` bumped the
> HTML marker only (GHI #650). Prior `1.0.0` — initial authoring under ADR-0.0.74 (OBPI-0.0.74-08).

## Non-negotiable rules

### Honor the marker

- Honor the marker: when `.gzkit/mx.json` exists, most guards drop to advisory

Before every action in a session where `.gzkit/mx.json` exists, confirm the
hangar is open. When the marker is present:

- `gate5_invariants` remain **fail-closed**. Gate 5 is never advisory.
- The MX awareness hook fires every turn to remind the agent of the open state.

### PRIME DIRECTIVE binds the entire session

Guards dropping to advisory means the operator can repair the surfaces the
guards protect — it does NOT mean ownership relaxes. In the hangar:

- Fix what you know **AND** what you find.
- "Not my work" / "out of scope" stays **forbidden in the bay**.
- Defects visible in flight are still defects; advisory guards are not a
  license to defer them.

### Operate the skill, not the shell

The operator uses the `gz-mx` skill; the skill invokes `gz mx`; agents do not
shell out to `gz mx enter` or `gz mx exit` directly.

## Do Not

- Do not invoke `gz mx enter` or `gz mx exit` directly in a shell step — use the `gz-mx` skill
- Do not treat advisory guards as license to defer visible defects
- Do not conflate "guard dropped to advisory" with "PRIME DIRECTIVE suspended"
- Do not exit the hangar while any detectable defect remains unfixed

## Related

- `gz-mx` skill — the operator's interface (`.gzkit/skills/gz-mx/SKILL.md`)
- MX awareness hook — per-turn reminder (`.claude/hooks/mx-awareness.py`)
- Parent ADR — `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/`
