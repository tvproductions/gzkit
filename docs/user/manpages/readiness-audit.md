# gz readiness audit

Audit repository readiness for long-running autonomous agents using Nate B. Jones' four disciplines and five specification primitives.

---

## Usage

```bash
gz readiness audit [--json]
```

---

## What It Evaluates

Four disciplines:

- Prompt craft
- Context engineering
- Intent engineering
- Specification engineering

Five specification primitives:

- Self-contained problem statements
- Acceptance criteria
- Constraint architecture
- Decomposition
- Evaluation design

Evaluation design explicitly includes TDD/BDD governance signals (Gate 2 and Gate 4 surfaces) alongside recurring regression checks.

Scoring is 0.00-3.00 per dimension. The command fails when required control surfaces are missing or overall discipline score is below the minimum threshold.

## Reference Mapping

Use this command with the practitioner reference:

- [`Agent Input Disciplines`](../reference/agent-input-disciplines.md)

The audit operationalizes that reference into deterministic repository checks.

---

## Example

```bash
uv run gz readiness audit
```

---

## Design Follow-Through

After running this command:

1. Record a dated audit artifact under `docs/proposals/`.
2. Convert the top three gaps into ADR/OBPI follow-up work.
3. Re-run `gz readiness audit` after implementation and capture score delta.

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable output |
