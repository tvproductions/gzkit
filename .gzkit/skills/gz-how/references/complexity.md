# Complexity

You are here when code is getting complex: while writing it, when a commit
crosses a threshold, or when the thresholds themselves need re-grounding.

## Steps

1. **While writing** → **`gz-complexity-guide`**: authoring-time hints before
   you commit.
2. **At commit, a crossing** → **`gz-complexity-advisor`**: the advisor's
   diagnosis of the crossing and its refactor archetype, or the route to attest
   the complexity as intrinsic.
3. **The doctrine itself** → **`gz-complexity-distill`**: a distillation pass
   over the exemplar corpus, on its cadence triggers.

## Branches

- **The code is idiomatic line by line but its shape is class-heavy** →
  `gz-pythonic-pattern-detect`, in [Codebase upkeep](codebase-upkeep.md).
- **The thresholds** live in `.gzkit/rules/complexity-thresholds.json`; cite the
  table, not a number.

## Only you can

Accept an intrinsic-complexity attestation, and trigger a distillation outside
its cadence.

## Then

[Commit and sync](commit-and-sync.md).
