# gzkit

**Keep humans in the loop when AI writes your code.**

---

## The Problem

You're using Claude Code (or Copilot, or Cursor). Week one, you're the architect. Week four, you're approving PRs you didn't read.

gzkit prevents that drift.

---

## Install

```bash
uv tool install gzkit
```

---

## 30-Second Overview

gzkit adds **gates** between you and shipped code:

1. **Record intent** before implementation (`gz specify`, `gz plan`)
2. **Track progress** across sessions (`gz status`, `gz state`)
3. **Require attestation** before shipping (`gz attest`)

The AI can't skip gates. Neither can you.

---

## Next Steps

- [**Quickstart**](quickstart.md) — Try it in 5 minutes
- [**Why gzkit?**](why.md) — The problem in detail
- [**Commands**](commands/index.md) — Full reference

---

## How It Works

```
gz init → gz specify → gz plan → gz obpi → Claude → gz check → closeout → gz attest
 (setup)   (intent)     (ADR)    (items)   (code)   (quality)  (observe)   (human)
```

Every decision gets recorded. Work breaks into observable units (OBPIs). Nothing ships without you observing the evidence and explicitly attesting.

---

<p style="text-align: center; color: #666; font-style: italic;">
The human is index zero.
</p>
