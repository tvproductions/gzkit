# gz parity check

Run deterministic parity regression checks for governance surfaces.

---

## Usage

```bash
gz parity check [--json]
```

---

## PASS/FAIL Contract

When parity-report surfaces are present, this command fails if any required contract is missing:

- `.github/discovery-index.json`
- `docs/governance/parity-intake-rubric.md`
- `docs/proposals/REPORT-TEMPLATE-airlineops-parity.md` (with required section markers)
- `.gzkit/skills/airlineops-parity-scan/SKILL.md` (with required ritual commands)
- At least one dated report matching `docs/proposals/REPORT-airlineops-parity-YYYY-MM-DD.md`

If parity-report surfaces are not present, the command reports a non-blocking skip.

---

## Example

```bash
uv run gz parity check
```

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable output |
