# Why gzkit?

You're not against AI. You're against losing the plot.

---

## The Degradation Pattern

| Week | What happens |
|------|--------------|
| 1 | You prompt carefully, review every line, understand what's built |
| 2 | You start skimming diffs, trust the green checkmarks |
| 3 | You batch approvals, "looks good" becomes reflexive |
| 4 | You're approving PRs you didn't read, for code you don't understand |

By month two, you're a rubber stamp. The AI is the architect.

---

## The Pain Points

| Pain | Without gzkit | With gzkit |
|------|---------------|------------|
| Claude forgets your decisions | Repeat context every session | ADRs persist intent; `gz state` shows history |
| Review backlog grows | Batch approve and hope | Gates force checkpoints; can't skip |
| Lose track of what's done | Scroll through chat history | Ledger tracks everything; `gz status` shows state |
| Constraints drift | Re-explain rules every conversation | CLAUDE.md generated from canon |
| No checkpoint before ship | Merge when CI passes | Gate 5 requires explicit `gz attest` |

---

## The Honest Tradeoff

This is slower than multi-agent orchestration. **That's the point.**

Some people can YOLO through agentic workflows—let agents spawn agents, approve PRs in batches, ship at machine speed. If that works for you, gzkit is not your tool.

But here's the bet: **more people need the sanity of this pace than can handle the chaos of full autonomy.**

The friction is intentional:

- Reading everything is a pain. (That keeps you engaged.)
- Gates interrupt your flow. (That prevents rubber-stamping.)
- Attestation is manual. (That proves you were there.)

---

## Who This Is For

- **Solo developers** using Claude Code who want to stay architects
- **Small teams** who need audit trails for AI-assisted work
- **Anyone** who's felt the drift from "I'm building this" to "I'm approving this"

---

## Who This Is Not For

- Teams that want fully autonomous AI agents
- Projects where speed matters more than understanding
- Anyone comfortable approving code they didn't review

---

## The Philosophy

gzkit implements the **Zero Doctrine**: the human is index zero.

- First in priority
- Final in authority
- Cannot be automated away

The covenant has two sides:

1. **Gates constrain agents** — They can't skip checkpoints
2. **Humans must engage** — Read everything, question everything

Without both sides, the covenant fails silently.

---

## Learn More

- [Quickstart](quickstart.md) — Try it in 5 minutes
- [OBPIs](concepts/obpis.md) — Atomic work units
- [Closeout Ceremony](concepts/closeout.md) — How attestation works
- [Daily Workflow](concepts/workflow.md) — The daily habits
- [Commands](commands/index.md) — Full reference
