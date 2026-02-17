---
name: gz-adr-check
description: Blocking ADR evidence audit — fails if any ADR has insufficient evidence.
compatibility: GovZero v6 framework; CI gate for ADR evidence completeness
metadata:
  skill-version: "1.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
opsdev_command: adr check
invocation: uv run -m opsdev adr check
---

# gz-adr-check

Blocking ADR evidence audit — fails if any ADR has insufficient evidence.

**Command:** `uv run -m opsdev adr check`

**Layer:** Layer 1 — Evidence Gathering

---

## When to Use

- As CI gate before merging PRs
- Before marking an ADR as Completed
- To verify all ADRs have required evidence
- During governance reviews

---

## Invocation

```text
/gz-adr-check
```

**CLI equivalent:**

```bash
uv run -m opsdev adr check
```

---

## What It Checks

For each ADR in Accepted/Completed status:

| Check | Requirement |
|-------|-------------|
| Test coverage | At least one test with @covers decorator |
| OBPI completion | All briefs in Completed status |
| Documentation | Required sections present |
| Evidence artifacts | Proof files exist in audit/ directory |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All ADRs have sufficient evidence |
| 1 | One or more ADRs have insufficient evidence |

---

## Output Example

### Passing

```text
ADR Evidence Check: PASS

Checked 12 ADRs:
  - 10 Validated (skipped)
  - 2 Completed (verified)

All ADRs have sufficient evidence.
```

### Failing

```text
ADR Evidence Check: FAIL

ADR-0.0.21 (Hexagonal Architecture):
  ✗ Missing test coverage (0 @covers tests)
  ✗ OBPI incomplete (7/9 briefs completed)

ADR-0.1.15 (Fleet Optimization):
  ✗ Missing audit artifacts

Fix these issues before proceeding.
```

---

## Difference from Related Tools

| Tool | Purpose |
|------|---------|
| `gz-adr-check` | **Blocking gate** — fails CI if evidence missing |
| `gz-adr-verification` | **Report** — shows coverage without failing |
| `gz-adr-audit` | **Procedure** — full Gate 5 audit workflow |
| `gz-adr-map` | **Discovery** — infers ADR→artifact mappings |

---

## CI Integration

Add to CI workflow:

```yaml
- name: ADR Evidence Gate
  run: uv run -m opsdev adr check
```

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| gz-adr-verification | Non-blocking coverage report |
| gz-adr-audit | Full Gate 5 audit procedure |
| gz-obpi-audit | Audit individual OBPI briefs |

---

## References

- Command: `src/opsdev/commands/adr_subcommands.py`
- Related: `uv run -m opsdev audit` (broader governance audit)
