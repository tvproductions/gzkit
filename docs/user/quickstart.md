# Quickstart

Run one governed ADR cycle with canonical closeout semantics.

---

## 1. Initialize

```bash
uv tool install gzkit
cd your-project
gz init
```

---

## 2. Create Intent Artifacts

```bash
gz prd GZKIT-1.0.0
gz plan 0.1.0 --title "Example governed increment"
```

Create OBPIs for ADR checklist items as needed.

---

## 3. Implement And Verify

```bash
uv run gz gates --adr ADR-0.1.0
```

For heavy lane also run docs checks:

```bash
uv run mkdocs build --strict
uv run gz lint
```

---

## 4. Closeout Presentation

```bash
uv run gz closeout ADR-0.1.0
```

Run the presented commands and observe results directly.

---

## 5. Human Attestation

```bash
uv run gz attest ADR-0.1.0 --status completed
```

---

## 6. Post-Attestation Audit

```bash
uv run gz audit ADR-0.1.0
```

---

## 7. Receipt Accounting

```bash
uv run gz adr emit-receipt ADR-0.1.0 --event validated --attestor "<Human Name>" --evidence-json '{"scope":"ADR-0.1.0","date":"YYYY-MM-DD"}'
```

For OBPI-scope receipts during daily increments, use:

```bash
uv run gz obpi emit-receipt OBPI-0.1.0-01-<slug> --event completed --attestor "<Human Name>" --evidence-json '{"attestation":"observed","date":"YYYY-MM-DD"}'
```

---

## Next

- [Runbook](runbook.md)
- [Lifecycle](concepts/lifecycle.md)
- [Closeout](concepts/closeout.md)
- [Command reference](commands/index.md)
