---
name: gz-obpi-pipeline
description: Thin wrapper over the canonical `uv run gz obpi pipeline` runtime for post-plan OBPI execution.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-14
---

# gz-obpi-pipeline

Use this skill when an agent or operator wants the familiar wrapper ritual for
post-plan OBPI execution, but the canonical runtime remains `uv run gz obpi pipeline`.

This skill is intentionally thin. It does not redefine stage sequencing,
completion accounting, marker semantics, or closeout order. Those behaviors
belong to the runtime command and its docs.

## When to Use

- After an OBPI plan is approved
- When the user asks for `/gz-obpi-pipeline`
- When implementation is already done and the user needs `--from=verify` or
  `--from=ceremony`

## Invocation

```text
/gz-obpi-pipeline OBPI-0.13.0-05-runtime-engine-integration
/gz-obpi-pipeline OBPI-0.13.0-05-runtime-engine-integration --from=verify
/gz-obpi-pipeline OBPI-0.13.0-05-runtime-engine-integration --from=ceremony
```

Canonical runtime equivalents:

```bash
uv run gz obpi pipeline OBPI-0.13.0-05-runtime-engine-integration
uv run gz obpi pipeline OBPI-0.13.0-05-runtime-engine-integration --from=verify
uv run gz obpi pipeline OBPI-0.13.0-05-runtime-engine-integration --from=ceremony
```

## Wrapper Contract

1. Resolve the requested OBPI and optional `--from` flag.
2. Launch `uv run gz obpi pipeline ...` with the same arguments.
3. Follow the runtime output for marker state, next commands, blockers, and
   closeout sequencing.
4. Do not restate or override the stage engine in skill prose.

## Required References

- `docs/user/commands/obpi-pipeline.md`
- `docs/user/concepts/workflow.md`
- `AGENTS.md` section `OBPI Acceptance Protocol`

## Notes

- The runtime owns the verify -> evidence -> guarded sync -> completion
  accounting path.
- `uv run gz git-sync --apply --lint --test` remains the required sync ritual
  before final completion accounting.
- If the runtime prints `BLOCKERS`, stop and resolve them instead of bypassing
  the command surface.
