---
name: gz-complexity-guide
description: Preview authoring-time complexity hints before committing. Use when the operator says "authoring-time complexity hint", "complexity guide preview", "preview before commit", or "advise-band hints".
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-26
metadata:
  skill-version: "0.2.0"
  govzero-framework-version: "v6"
  govzero_layer: "Layer 3 - File Sync"
gz_command: complexity guide
model: sonnet
---

# gz-complexity-guide

Run `gz complexity guide`, the authoring-time hint surface of the
complexity-doctrine cluster (ADR-0.0.27 corpus, 0.0.28 thresholds, 0.0.29
advisor, 0.0.30 authoring guidance). It measures per-function `radon_cc` and
reports only the functions in the `advise` band of
`.gzkit/rules/complexity-thresholds.json`, the band below `warn`, so a refactor
decision lands while the code is being written. It never blocks: it exits 0
whatever it finds, and exits 1 only on a user error such as a missing path.

This skill ends at the hints. It does not refactor.

## When to Use

The guide is the **first-stop authoring surface** for complexity hints:

1. **Authoring-time review** — preview hints for a file or directory while
   editing it.
2. **Before a commit** — catch functions growing toward `warn`.

A function already at `warn` or `block` produces no hint here; use
`gz-complexity-advisor` for it.

```bash
uv run gz complexity guide src/gzkit/commands/validate_cmd.py
uv run gz complexity guide src/gzkit/ --json
```

A path is required unless `--server` is given. `--server` starts a
JSON-over-stdio server for editors (Content-Length framing; `initialize`,
`analyze` with a `file_path`, `shutdown`), whose envelope is
`src/gzkit/schemas/authoring_guide_protocol.json`.

## Output Contract

**Declared form:** in-line hint prose (default human-readable). Each hint is a
block headed `── <file>:<start>-<end> ──` with four lines:

- **Archetype** — the refactor archetype name
- **Band** — `approaching`, or `approaching_warn` in the upper half of the
  advise band
- **Guidance** — the doctrinal-frame headline
- **Move** — the recommended-move excerpt

The line range is the diagnosis's first proof range, which is often the `def`
line alone rather than the whole function. No archetype rule in
`data/advisor_archetype_rules.json` covers the `advise` band, so every hint's
archetype is the `long_parameter_list` fallback; judge the function from its
code, not the label.

**Machine-readable mode:** `--json` emits an array of `AuthoringHint` objects
with `metric`, `precedence_band`, `crossing_value`, `archetype`,
`doctrinal_frame_headline`, `recommended_move`, `file_path`, `start_line` and
`end_line`.

## Trigger-Time vs. Authoring-Time

| Surface | Skill | Bands reported | Blocks? |
|---------|-------|----------------|---------|
| Authoring-time hints | `gz-complexity-guide` (this skill) | `advise` | Never |
| Trigger-time diagnosis | `gz-complexity-advisor` | `advise`, `warn`, `block` | Exits 3 on `block` |

Both are run by hand in this repository; the advisor's auto-chain pre-commit
hook is not installed.

## Related

- Sister skill: `.gzkit/skills/gz-complexity-advisor/SKILL.md` (ADR-0.0.29)
- Manpage: `docs/user/manpages/complexity-guide.md`
- Runbook: `docs/user/runbook.md` § Governance Doctrine Surfaces
- Parent ADR: `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/`
- Threshold table: `.gzkit/rules/complexity-thresholds.json` (ADR-0.0.28)
