# /gz-issue-file

Cross-repo defect/enhancement filing wrapper for gzkit-owned surfaces.

---

## Purpose

Operationalizes the `Safeguard circumvention` failure shape (codified in
`.gzkit/rules/agent-failure-modes.md`) at the cross-repo defect-filing
surface. When an agent or operator working **inside a gzkit-consuming
repository** finds a defect or enhancement against a **gzkit-owned
surface** — the `gz` CLI, schemas under `src/gzkit/schemas/`, validator
scopes, ledger event semantics, files under `.gzkit/**` or
`src/gzkit/**`, or rules under `.gzkit/rules/**` — the right
authorization path is to file the issue directly at
`tvproductions/gzkit` with a provenance trailer, **not** at the
consumer's tracker and **not** as an `agent-insights.jsonl` entry.

The skill wraps `gz issue file`, which:

1. Resolves the consumer repo's slug from `git remote -v` (origin
   precedence; SSH and HTTPS forms; `.git` suffix stripped).
2. Reads the running gzkit version from package metadata.
3. Composes a `Filed from <slug> running gz vX.Y.Z` provenance trailer.
4. Validates that the body references at least one gzkit-owned surface
   marker (`gz <verb>`, `.gzkit/`, `src/gzkit/`, `gzkit.<module>`).
5. **Hard-rejects** (exit 1) bodies that reference no gzkit-owned
   surface — the misrouting failure class is closed structurally.
6. Routes the issue against `tvproductions/gzkit` regardless of the
   consumer's `git remote`.

## When to Use

Reach for `/gz-issue-file` when:

- The `gz` CLI itself misbehaves (parser, dispatcher, output, exit code).
- A schema under `src/gzkit/schemas/` is over- or under-strict.
- A validator scope (`gz validate --<scope>`) misses or false-flags drift.
- A rule under `.gzkit/rules/**` contradicts another rule.
- A skill or hook surface in `.gzkit/skills/` or `.gzkit/hooks/` regresses.
- An enhancement is wanted on any of the above (file with
  `--enhancement`).

## When NOT to Use

- Defects in **consumer-repo** code, content, or governance — file at the
  consumer's own tracker via plain `gh issue create`.
- In-flight gzkit defects meeting the direct-fix thresholds in
  `AGENTS.md` § Defect-fix routing — fix in place with
  `fix(<scope>): … (GHI #N)` instead of filing.
- Filing a GHI at the **current** repo (not cross-repo) — use
  [`/ghi-author`](ghi-author.md).

## What to Expect

A typical session: dry-run preview to confirm the trailer and target,
then a live run that files at `tvproductions/gzkit` and prints the new
issue URL. The skill records the assigned issue number into session
evidence after creation.

## Related

- [`/ghi-author`](ghi-author.md) — author a GHI at the current repo.
- [`/ghi-close`](ghi-close.md) — work and close a filed GHI.
- Manpage: [`gz issue file`](../commands/issue-file.md).
- Doctrine: `.gzkit/rules/gh-cli.md` § Cross-repo filing.
- Failure shape: `.gzkit/rules/agent-failure-modes.md` § Safeguard circumvention.
- Parent ADR: ADR-0.0.23-agent-failure-mode-taxonomy.
