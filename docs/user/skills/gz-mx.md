# /gz-mx

Enter and exit the MX Maintenance Hangar — operator's interface to `gz mx`.

---

## Purpose

`/gz-mx` is the operator's interface to the MX Maintenance Hangar. The hangar
exists so governance surfaces can be repaired even when guards protect them.
While the hangar is open, most governance guards drop to advisory. Two things
never relax: `gate5_invariants` and the PRIME DIRECTIVE (ownership — fix what
you know AND what you find).

The skill is the correct interface. Nobody shells out to `gz mx enter` or
`gz mx exit` directly — the skill is the gate.

## When to Use

- **Entering the hangar** — governance repair requires guards to go advisory
- **Checking hangar status** — confirming whether the hangar is currently open
- **Clean exit** — repair is complete; re-enforce all guards at full strength

## Workflow

1. **Open the hangar**

   ```bash
   uv run gz mx enter
   ```

   Creates `.gzkit/mx.json`. Most governance guards drop to advisory.

2. **Perform the repair**

   Fix the governance surfaces that needed repair. Guards are advisory so
   you can fix the surfaces they protect — not so defects can be deferred.

3. **Close the hangar**

   ```bash
   uv run gz mx exit
   ```

   Removes `.gzkit/mx.json`. Every guard re-runs at full strength; exit
   is a hard gate (all guards must pass before exit succeeds).

## Invocation

```text
/gz-mx
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(none)* | — | See Workflow above; follow enter → repair → exit sequence |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-mx/SKILL.md` | Agent execution instructions | Read |
| `.gzkit/rules/mx-mode.md` | Binding rule for hangar sessions | Read |
| `.gzkit/mx.json` | Marker file indicating open hangar | Read/Write (by `gz mx enter/exit`) |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`gz mx enter`](../commands/mx.md) | CLI command this skill wields to open the hangar |
| [`gz mx exit`](../commands/mx.md) | CLI command this skill wields to close the hangar |
| [`/gz-status`](gz-status.md) | Check governance gate status mid-session |
| [`/gz-check`](gz-check.md) | Run full quality checks; also runs at exit to re-enforce guards |
