# Lanes

Lanes determine which gates must be satisfied.

---

## Lane Matrix

| Lane | Required gates | Typical trigger |
|------|----------------|-----------------|
| Lite | 1, 2 | Internal implementation, documentation, process, or template changes that do not alter an external runtime contract |
| Heavy | 1, 2, 3, 4, 5 | Command, API, schema, or other runtime-contract changes used by humans or external systems |

---

## Heavy-Lane Gate 4 Detail

Heavy lane requires BDD verification (Gate 4) to pass.

---

## Operational Implication

Even when lane requirements differ, the closeout habit order remains consistent:

1. Orientation
2. Execute through `uv run gz obpi pipeline`
3. Verification/tool use
4. Human attestation when required
5. Guarded `git sync`
6. OBPI completion accounting
7. ADR closeout and post-attestation audit later

---

## Related

- [Gates](gates.md)
- [Workflow](workflow.md)
