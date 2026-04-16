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
re-initialization. After init, your project has:

```text
your-project/
├── .gzkit/                    ← Ledger, manifest, skills, rules
├── .gzkit.json                ← Project config (mode, paths)
├── .claude/                   ← Agent mirrors (generated, do not edit)
├── design/
│   ├── prd/                   ← PRDs go here
│   ├── constitutions/
│   └── adr/                   ← ADRs and OBPIs go here
├── src/<project>/             ← Source code
├── tests/                     ← Tests
├── AGENTS.md                  ← Agent governance contract
└── CLAUDE.md                  ← Claude Code instructions (generated)
```

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

## Common Friction Points

Things that trip up first-time adopters:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `gz gates` can't find tests | `.gzkit.json` has wrong `tests_root` | Check `paths.tests_root` in `.gzkit.json` |
| `gz specify` doesn't parse checklist items | ADR checklist uses non-standard format | Use `1. [ ] Description` format in the ADR's `## Checklist` |
| `gz status` shows 0 OBPIs | OBPIs not registered in ledger | Run `gz specify` to create OBPIs (creates ledger events) |
| Skills don't appear in Claude Code | Skills not synced to `.claude/skills/` | Run `gz agent sync control-surfaces` |
| Ledger events have wrong IDs | Manual file creation instead of CLI | Always use `gz plan`, `gz specify`, `gz prd` — they generate correct IDs |
| `gz closeout` says "prerequisites not met" | OBPIs not marked complete | Run `gz obpi complete` for each OBPI before closeout |
| Init creates wrong directory structure | Pre-existing `docs/` with non-standard layout | Use `gz init --no-skeleton` and configure paths in `.gzkit.json` |

If you hit something not listed here,
[file an issue](https://github.com/tvproductions/gzkit/issues/new/choose)
using the appropriate template.

---

## Next

- [Runbook](runbook.md)
- [Skills](skills/index.md)
- [Lifecycle](concepts/lifecycle.md)
- [Closeout](concepts/closeout.md)
- [Command reference](commands/index.md)
