# Settings patch — DRAFT, not applied

> Chore: `control-surface-permission-consent-drift`, step 5 (propose). Drafted 2026-10-10,
> maintenance visit E. **Nothing in this file has been applied.** Step 6 applies a patch only in
> a run the operator starts for that purpose, because the permission surface records what the
> operator consented to. The operator rules on each block separately.

The drift ledger has no `live` row, so nothing here neutralizes a row. Each block answers an
entry in `unwitnessable.md` or a channel a deny rule could close.

## Block 1 — committed deny rules (`.claude/settings.json`, `permissions.deny`)

Defense for context-free prohibitions that today rest on prose alone. A deny rule binds in every
permission mode, which the allow list does not (U17).

```json
"Bash(python3 *)",
"Bash(python *)",
"Bash(pip *)",
"Bash(pip3 *)",
"Bash(SKIP=*)",
"Bash(* SKIP=* git *)",
"Bash(git push *--force*)",
"Bash(git push *-f *)",
"Bash(git checkout -b *)",
"Bash(git switch -c *)",
"Bash(gh pr merge*)",
"Bash(gh repo edit*)",
"Bash(gh repo delete*)",
"Bash(gh secret *)",
"Bash(gh auth token*)",
"Bash(sqlite3 *)"
```

| Rules | Doctrine row | Cost and precondition |
|---|---|---|
| `python3`, `python`, `pip`, `pip3` | 1, `uv run` for Python | `uv run python` is unaffected. **Two written procedures must be repaired first** or the deny breaks them: `gz-deps-upgrade/SKILL.md:85` and `frontier-model-card-currency/CHORE.md:103`. Whether the pattern also catches the interpreter inside a pipeline was not tested |
| `SKIP=` | 3, commit through hooks | closes the environment-variable channel August's row D1 used; `gz-complexity-advisor/SKILL.md:77` documents a `SKIP=` commit and would need repair |
| force push | 13 | none known |
| `checkout -b`, `switch -c` | 6, no branches | a subagent's local worktree is permitted since 2026-09-27; `git worktree add` is deliberately not denied |
| `gh pr merge`, `gh repo`, `gh secret`, `gh auth token` | 13 | none known |
| `sqlite3` | 12, no raw SQL evidence | none known |

Not proposed: a deny on `pytest` (the token appears in legitimate text and file names) and any
deny on `gh issue create` (U1: the sanctioned path runs the identical string).

## Block 2 — the local allow list (`.claude/settings.local.json`, operator's machine)

The file's `_comment` says mutating and outward-facing commands are absent so that they prompt.
Two rules contradict it (U13, U14). Options, for the operator:

- **A. Narrow.** Replace `Bash(uv run gz:*)` with the read-only verbs the comment describes
  (`status`, `state`, `validate`, `check`, `test`, `lint`, `typecheck`, `adr report`, `adr status`,
  `chores status`, `chores plan`, `chores advise`, `chores show`, `skill list`, `covers`) and drop
  `Bash(uv run -m:*)`. Mutating verbs (`git-sync --apply`, `obpi complete`, `attest`,
  `content land`, `issue file`, `mx enter`) then prompt, as the comment intends.
- **B. Keep and correct the comment.** State that every `gz` verb is pre-authorized, and rely on
  the verbs' own gates.
- **C. Replace `Bash(find:*)`** with `Bash(find * -name *)`-shaped reads, or accept it and say so.

Recommendation: A, then C. The verbs' own gates are real, but the comment promises a prompt.

## Block 3 — not a settings change, recorded here so it is not lost

U19 is not closable from the permission surface. A write hook matched on `Bash` would need to
decide which commands write; the alternative is a turn-end check that compares the working
tree's changed paths against the hooks that should have seen them. That is design work for the
operator to route, not a patch.
