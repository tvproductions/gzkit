---
name: gz-complexity-guide
description: Preview authoring-time complexity hints before committing. Use when the operator says "authoring-time complexity hint", "complexity guide preview", "preview before commit", or "advise-band hints".
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-25
metadata:
  skill-version: "0.1.3"
  govzero-framework-version: "v6"
  govzero_layer: "Layer 3 - File Sync"
gz_command: complexity guide
model: sonnet
---

# gz-complexity-guide

Operator-runnable skill wrapping the `gz complexity guide` CLI verb
(ADR-0.0.30, OBPI-0.0.30-01). The guide is the authoring-time hint surface
for the four-ADR complexity-doctrine cluster (ADR-0.0.27 corpus /
0.0.28 thresholds / 0.0.29 advisor / 0.0.30 authoring-guidance). Use this
skill **before** running `gz complexity advise` or attempting a commit — it
surfaces functions in the `advise` band while you are actively editing, so
refactor decisions land at design time rather than at gate time.

## When to Use

The guide is the **first-stop authoring surface** for complexity hints. Use it
at two operator moments:

1. **Ad-hoc authoring-time review** — preview hints for a file or directory
   while actively editing code. The guide surfaces functions approaching the
   warn threshold before they cross into `warn` or `block`.
2. **Preflight complexity check** — before committing, use the guide to catch
   functions that are growing toward the warn threshold so refactor decisions
   land at design time.

If a function has already crossed into `warn` or `block`, use the trigger-time
advisor instead (see `gz-complexity-advisor` in § Related).

## Operator Moment: Authoring-Time Review

The primary operator moment: invoke the guide directly while editing to preview
which functions are approaching the warn threshold. The guide never blocks — it
surfaces hints for information only.

```bash
# Ad-hoc authoring-time review
gz complexity guide src/gzkit/commands/validate_cmd.py
gz complexity guide src/gzkit/ --json
```

Default output is in-line hint prose — one block per function in the advise
band. Each block names the archetype, the position within the advise band
(`approaching` or `approaching_warn`), the one-line doctrinal-frame headline,
and the recommended move. The `--json` flag emits the canonical `AuthoringHint`
Pydantic serialization for machine consumption.

## Output Contract

**Declared form:** in-line hint prose (default human-readable).

Each hint block in the default output contains:

- **Archetype** — the canonical refactor archetype name (e.g. `long_parameter_list`)
- **Band** — position within the advise band (`approaching` or `approaching_warn`)
- **Guidance** — one-line doctrinal-frame headline from the active
  distilled-characteristics document
- **Move** — the recommended-move excerpt

**Machine-readable mode:** `--json` emits the canonical `AuthoringHint`
Pydantic serialization as a JSON array. Each element is a frozen Pydantic
model with fields: `metric`, `precedence_band`, `crossing_value`,
`archetype`, `doctrinal_frame_headline`, `recommended_move`, plus the
editor-navigation triple `file_path`, `start_line`, `end_line`.

## Trigger-Time vs. Authoring-Time

| Surface | Skill | Trigger | Blocks? |
|---------|-------|---------|---------|
| Authoring-time hints | `gz-complexity-guide` (this skill) | Operator-invoked while editing | Never |
| Trigger-time diagnosis | `gz-complexity-advisor` | Xenon-as-gate at pre-commit | At `block` band |

Use the guide **before commit** for design-time decisions. Use the advisor
**at commit time** when xenon-as-gate fires or to preview a full structured
diagnosis with proof ranges and doctrinal frame citations. The two skills share
the `AdvisorDiagnosis` schema at the architecture level (the guide projects to
the lighter `AuthoringHint` shape via OBPI-0.0.30-03), but serve different
operator moments.

See `.gzkit/skills/gz-complexity-advisor/SKILL.md` for the trigger-time surface
(ADR-0.0.29).

## Related

- Sister skill: `.gzkit/skills/gz-complexity-advisor/SKILL.md` (ADR-0.0.29)
- Manpage: `docs/user/manpages/complexity-guide.md`
- Runbook: `docs/user/runbook.md` § Governance Doctrine Surfaces
- Parent ADR: `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/`
- Threshold table: `.gzkit/rules/complexity-thresholds.json` (ADR-0.0.28)
