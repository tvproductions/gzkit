# Design Notes

- AirlineOps is the behavioral reference implementation for this pipeline.
- gzkit adapts the control surface to its native command vocabulary
  (`uv run gz lint`, `uv run gz test`, etc.) and repository structure.
- **Hooks do the hard enforcement.** This pipeline is orchestration narrative, not a security boundary. The real gates are:
  - `plan-audit-gate.py` -- enforces plan <-> OBPI alignment at plan-mode exit
  - `obpi-completion-validator.py` -- enforces evidence requirements when marking briefs Completed
  - `pipeline-gate.py` -- blocks src/tests writes until pipeline is active
- The pipeline's value is **sequencing and governance memory** -- ensuring the ceremony and sync stages happen, which is exactly what gets lost in freeform execution.
- `src/gzkit/pipeline_runtime.py` is the canonical shared runtime used
  by the CLI and generated pipeline hooks.
- In gzkit, `uv run gz git-sync --apply --lint --test` is the canonical Stage 5
  sync ritual. Do not substitute ad-hoc git commands.
