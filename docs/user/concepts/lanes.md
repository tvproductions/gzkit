# Lanes

Lanes determine which gates must be satisfied.

---

## Lane Matrix

| Lane | Required gates | Typical trigger |
|------|----------------|-----------------|
| Lite | 1, 2 | Internal behavior changes |
| Heavy | 1, 2, 3, 4, 5 | External contract changes |

---

## Heavy-Lane Gate 4 Detail

Heavy lane expects BDD verification (Gate 4). If no `features/` suite exists, runtime surfaces mark Gate 4 as N/A with explicit rationale rather than silently passing.

---

## Operational Implication

Even when lane requirements differ, the closeout habit order remains consistent:

1. Orientation
2. Verification/tool use
3. Closeout presentation
4. Human attestation
5. Post-attestation audit
6. Receipts/accounting

---

## Related

- [Gates](gates.md)
- [Workflow](workflow.md)
