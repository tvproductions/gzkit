# Lanes

Lanes determine which gates apply to your work.

---

## Two Lanes

| Lane | Gates | When to Use |
|------|-------|-------------|
| **Lite** | 1, 2 | Internal changes |
| **Heavy** | 1, 2, 3, 4, 5 | External contract changes |

---

## Lite Lane (Default)

Gates: **ADR → TDD**

Use for:

- Internal refactoring
- Bug fixes
- New internal features
- Building blocks that support heavy lane work
- Anything that doesn't change external contracts

Lite work is often a stepping stone—internal components that eventually compose into user-facing features (which go through heavy lane).

What you skip:

- Documentation gate (Gate 3)
- BDD acceptance tests (Gate 4)
- Human attestation (Gate 5)

---

## Heavy Lane

Gates: **ADR → TDD → Docs → BDD → Human**

Use for:

- CLI command changes
- API endpoint changes
- Schema changes
- Public interface changes
- Anything users or external systems depend on

What you add:

- Documentation must be updated
- Acceptance tests must pass

---

## Choosing a Lane

| Question | If Yes |
|----------|--------|
| Does this change a CLI command? | Heavy |
| Does this change an API endpoint? | Heavy |
| Does this change a database schema? | Heavy |
| Does this change a public interface? | Heavy |
| Will external users notice? | Heavy |
| Is this purely internal? | Lite |

When in doubt, use **lite**. Escalate to **heavy** if contracts change.

---

## Setting the Lane

### At initialization

```bash
gz init --mode heavy
```

### Per brief

```bash
gz specify my-feature --parent PRD-x --lane heavy
```

### Per ADR

```bash
gz plan my-adr --brief BRIEF-x --lane heavy
```

---

## Why Two Lanes?

**Ceremony is debt.**

Five gates for every change would be exhausting and counterproductive. Most internal work doesn't need acceptance tests and documentation updates.

But external contract changes affect users. They need the extra verification.

The distinction keeps governance proportional to risk.

---

## Related

- [Gates](gates.md) — What each gate verifies
- [gz init](../commands/init.md) — Set project-wide mode
- [gz specify](../commands/specify.md) — Set lane per brief
