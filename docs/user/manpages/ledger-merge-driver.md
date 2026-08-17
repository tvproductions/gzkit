# gz ledger merge-driver

Reconcile a conflicted append-only JSONL file as a timestamp-ordered union.

Git invokes this, not you. It is registered as a merge driver and receives the
three sides of a conflict; the merged result is written back over the "ours"
path.

---

## Usage

```bash
gz ledger merge-driver ANCESTOR OURS THEIRS
```

---

## Why this exists

`.gzkit/ledger.jsonl` and its sibling JSONL surfaces are appended to by the
runtime during every session and tracked in git, so two clones in flight
collide by construction — each appends to the tail, and git reports a conflict
over disjoint additions. Resolving that by hand is the action
`AGENTS.md` § Never #2 prohibits ("NEVER: Modify the ledger directly"), and
before this verb existed there was no `gz` command that could do it instead.

Git's built-in `merge=union` is **not** a substitute. It concatenates one
side's unique lines after the other's without ordering them, while ledger rows
are strictly timestamp-ordered (`gz validate --ledger`). An earlier local
append merged after a later upstream one produces a descending pair — trading a
loud conflict for a silent invariant violation.

---

## PASS/FAIL Contract

Exits 0 having written the merged rows when both sides are disjoint appends on
a shared ancestor.

Exits 1, leaving git's conflict in place for a human, when the merge falls
outside append-only semantics:

- the ancestor is not a prefix of both sides (a row was edited or removed)
- an appended row carries no parseable `ts`, so it cannot be ordered
- the result would not be non-decreasing

Refusing never destroys evidence, so it is the safe direction whenever the
inputs are not plainly appends.

---

## Registration

The `.gitattributes` rule ships with the repository:

```
.gzkit/ledger.jsonl merge=gzkit-jsonl
```

The driver *command* cannot ship with it — git reads that from local config,
which is per-clone and uncommittable. `gz git-sync` registers it on every apply
(idempotently), and `gz init` seeds it for new clones. To register by hand:

```bash
git config merge.gzkit-jsonl.driver "uv run gz ledger merge-driver %O %A %B"
```

---

## Example

```bash
# Normally invoked by git during a rebase or merge:
uv run gz ledger merge-driver .merge_file_O .merge_file_A .merge_file_B
```

---

## Options

| Option | Description |
|--------|-------------|
| `ANCESTOR` | Common-ancestor version (git `%O`) |
| `OURS` | Our version; the merged result is written here (git `%A`) |
| `THEIRS` | Their version (git `%B`) |
