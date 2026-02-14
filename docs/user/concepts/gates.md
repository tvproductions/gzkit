# Gates

Gates are verification checkpoints in the covenant.

---

## Gate Set

| Gate | Name | Applies |
|------|------|---------|
| 1 | ADR | Lite, Heavy |
| 2 | TDD | Lite, Heavy |
| 3 | Docs | Heavy |
| 4 | BDD | Heavy |
| 5 | Human Attestation | Heavy |

---

## Enforcement Notes

- `gz attest` enforces prerequisite gates by default.
- Lite lane attestation requires Gate 2 pass.
- Heavy lane attestation requires Gate 2 and Gate 3 pass.
- Heavy lane Gate 4 must pass when `features/` exists; otherwise explicit N/A rationale applies.
- `--force` exists for accountable overrides and requires rationale when bypassing failed prerequisites.

---

## Gate 5 Authority

Gate 5 is explicit human attestation.

- Agents present evidence.
- Humans observe evidence.
- Humans record attestation.

Audit and receipts are downstream accounting, not substitutes for human attestation.

---

## Related

- [Lanes](lanes.md)
- [Closeout](closeout.md)
- [gz attest](../commands/attest.md)
- [gz audit](../commands/audit.md)
