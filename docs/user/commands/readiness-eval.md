# gz readiness eval

Run the instruction architecture eval suite with positive and negative controls across four readiness dimensions.

---

## Usage

```bash
gz readiness eval [--json]
```

---

## What It Evaluates

Ten baseline eval cases exercise instruction surfaces across:

- **Codex loading** — AGENTS.md as primary surface, agent-exclusion filtering
- **Claude loading** — .claude/rules/ sync from .github/instructions/, orphan detection
- **Workflow relocation** — skills in .gzkit/skills/, command documentation coverage
- **Drift detection** — applyTo reachability, foreign references, instruction/rule sync

Each case is classified by:

- **Surface**: codex, claude, or shared
- **Dimension**: outcome, process, style, or efficiency
- **Control**: positive (expected to pass) or negative (expected to detect problems)

Scoring is 0.00-3.00 per dimension. The command fails when any eval case fails.

---

## Example

```bash
uv run gz readiness eval
```

---

## Extensibility

New eval cases can be added by appending to the `BASELINE_CASES` list in `src/gzkit/instruction_eval.py` or by passing custom cases to `run_eval_suite()`. No model changes required.

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable output |
