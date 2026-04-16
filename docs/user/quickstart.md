# Quickstart

Run one governed ADR cycle with canonical closeout semantics.

gzkit has two operator surfaces: **CLI commands** (`gz <verb>`) for terminal
use and **skills** (`/gz-<name>`) for Claude Code sessions. Skills carry
interview logic, forcing functions, and governance validation that raw CLI
commands do not — use them when they exist.

---

## 1. Initialize

| CLI | Skill |
|-----|-------|
| `gz init` | `/gz-init` |

```bash
uv tool install gzkit
cd your-project
gz init
```

The `/gz-init` skill detects missing scaffolding and enters repair mode on
re-initialization.

---

## 2. Create Intent Artifacts

| CLI | Skill | What the skill adds |
|-----|-------|---------------------|
| `gz prd MYPROJECT-1.0.0` | `/gz-prd` | Guided project intent declaration |
| `gz plan 0.1.0 --title "..."` | `/gz-plan` | 20+ design forcing-function questions (pre-mortem, constraint archaeology, reversibility) |
| `gz specify slug --parent ADR-0.1.0 --item 1` | `/gz-obpi-specify` | Semantic authoring with lane resolution from the ADR's WBS table |

Create OBPIs for ADR checklist items as needed.

---

## 3. Implement And Verify

| CLI | Skill |
|-----|-------|
| `uv run gz obpi pipeline OBPI-0.1.0-01-<slug>` | `/gz-obpi-pipeline OBPI-0.1.0-01-<slug>` |
| `uv run gz gates --adr ADR-0.1.0` | `/gz-gates ADR-0.1.0` |

For heavy lane also run docs checks:

```bash
uv run mkdocs build --strict
uv run gz lint
```

---

## 4. Closeout Presentation

| CLI | Skill | What the skill adds |
|-----|-------|---------------------|
| `uv run gz closeout ADR-0.1.0` | `/gz-adr-closeout-ceremony ADR-0.1.0` | Full walkthrough protocol; rejects vague acknowledgment |

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
- [Skills](skills/index.md)
- [Lifecycle](concepts/lifecycle.md)
- [Closeout](concepts/closeout.md)
- [Command reference](commands/index.md)
