# Quickstart

Add a feature to your project with gzkit governance in 5 minutes.

---

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- A project with git initialized

---

## 1. Install and Initialize

```bash
uv tool install gzkit
cd your-project
gz init
```

This creates:

- `.gzkit/` — Ledger and state
- `.gzkit.json` — Configuration
- `CLAUDE.md` — Agent constraints (auto-generated)
- `design/` — Governance documents

---

## 2. Record Your Intent

Create a brief describing what you want to build:

```bash
gz specify add-login --parent PRD-1.0.0 --title "Add login button"
```

Edit `design/briefs/BRIEF-add-login.md` to describe:

- What you want
- Acceptance criteria
- What's out of scope

---

## 3. Create an ADR

Before implementation, record your technical decision:

```bash
gz plan login-impl --brief BRIEF-add-login --title "Login implementation"
```

Edit `design/adr/ADR-0.1.0.md` to capture:

- Problem statement
- Decision
- Checklist of items to implement

---

## 4. Create OBPIs (for multi-item ADRs)

If your ADR has multiple checklist items, create an OBPI for each:

```bash
gz obpi ADR-0.1.0 --item 1 --title "Create login form component"
gz obpi ADR-0.1.0 --item 2 --title "Add authentication API"
gz obpi ADR-0.1.0 --item 3 --title "Write login tests"
```

Each OBPI is one atomic piece of work.

---

## 5. Implement with Claude

Tell Claude what to work on:

```
Implement OBPI-0.1.0-01 (login form) following ADR-0.1.0
```

Claude has access to:

- Your intent (the brief)
- Your decision (the ADR)
- Your constraints (CLAUDE.md)
- The specific scope (the OBPI)

---

## 6. Check Progress

```bash
gz status
```

Output (for heavy lane work):

```
Lane: heavy

ADR-0.1.0 (Pending)
  Gate 1 (ADR):   PASS
  Gate 2 (TDD):   PENDING
  Gate 3 (Docs):  PENDING
  Gate 4 (BDD):   PENDING
  Gate 5 (Human): PENDING
```

For lite lane (internal work), only Gates 1 and 2 apply—no closeout ceremony needed.

---

## 7. Run Quality Checks

```bash
gz check
```

Runs lint, format, typecheck, and tests. Gate 2 requires tests to pass.

---

## 8. Closeout Ceremony

When all OBPIs are complete, trigger the closeout:

```
Begin closeout for ADR-0.1.0
```

The agent presents commands for you to run. **You observe directly**—don't trust summaries.

---

## 9. Attest and Ship

After observing that all gates pass:

```bash
gz attest ADR-0.1.0 --status completed
```

This records your explicit sign-off. The ADR is now closed.

---

## What Just Happened?

1. **Intent recorded** — Brief captured what you wanted
2. **Decision captured** — ADR documented the approach
3. **Work atomized** — OBPIs broke it into observable units
4. **Constraints enforced** — Claude worked within boundaries
5. **Gates verified** — Quality checks passed
6. **Human attested** — You observed and signed off

The ledger (`gz state`) shows the full history.

---

## The Flow

```
gz init → gz specify → gz plan → gz obpi → Claude → gz check → closeout → gz attest
```

Every decision recorded. Every change verified. Nothing ships without you.

---

## Next Steps

- [Why gzkit?](why.md) — The philosophy
- [OBPIs](concepts/obpis.md) — Atomic work units
- [Closeout](concepts/closeout.md) — The attestation ceremony
- [Workflow](concepts/workflow.md) — Daily habits
- [Commands](commands/index.md) — Full reference
