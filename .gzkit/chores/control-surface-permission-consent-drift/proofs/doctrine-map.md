# Doctrine Map — Pass D

> Chore: `control-surface-permission-consent-drift` (Lite lane, advisory)
> Run: **2026-10-10**, maintenance visit E. **Re-derived from the current files, not carried
> from the 2026-08-09 run**: root `AGENTS.md` was rewritten on 2026-09-17 and its
> `Always #N` / `Never #N` numbering no longer exists, so every citation below is by section.

Prohibitions enumerated from root `AGENTS.md` and all 26 authored rules under `.gzkit/rules/`,
each read whole on 2026-10-10. Only `context-free` entries are eligible for a drift row.
`context-dependent` entries go to [`unwitnessable.md`](unwitnessable.md) without pattern-matching.

| # | Doctrine citation | Kind | Verbatim quote (trimmed) | Command token(s) |
|---|---|---|---|---|
| 1 | `AGENTS.md` § Project Identity | context-free | *"always `uv run` for Python commands."* | `python`, `python3`, `pip`, `pip3` |
| 2 | `AGENTS.md` § Behavior Rules | context-free | *"Write the ledger only through `gz` commands… rather than hand-writing markers or ledger rows."* | writers targeting `.gzkit/ledger.jsonl` and marker files |
| 3 | `AGENTS.md` § Behavior Rules | context-free | *"Commit and push through the configured hooks; `--no-verify` is not used."* | `--no-verify`, `commit -n`, `hooksPath`, `SKIP=<hook-id>` |
| 4 | `AGENTS.md` § Execution Rules | context-free | *"Never prefix `uv run gz` or `uv run -m gzkit` with `PYTHONUTF8=1`"* | `PYTHONUTF8=1` |
| 5 | `AGENTS.md` § Execution Rules (operator PII) | context-free, mostly not command-expressible | *"never include the operator's personal email in any repo-bound artifact"* | `git config user.email`, `--author`, `Co-authored-by` |
| 6 | `AGENTS.md` § Operator Doctrine | context-free, with a carve-out | *"Do not create feature branches or a branch/merge/delete workflow."* | `git checkout -b`, `git switch -c`, `git branch <name>`, `git merge <branch>`; a subagent's unpushed local worktree is permitted since 2026-09-27 |
| 7 | `AGENTS.md` § STDLIB-FIRST | context-free | *"`unittest` (pytest is blocked by the `forbid-pytest` hook)"* | `pytest` |
| 8 | `AGENTS.md` § Control Surfaces | context-free | *"generated surfaces are not edited directly."* | writes to `AGENTS.md`, `CLAUDE.md`, `.claude/**`, `.agents/**`, `.codex/**` |
| 9 | `skill-surface-sync.md` rules 4 and 5 | context-free | *"Never edit vendor mirrors directly."* / *"Never edit `src/gzkit/<surface>/` directly."* | write, `cp`, `mv` into mirror roots and `src/gzkit/{skills,rules,personas,templates}/` |
| 10 | `chores.md` § Authoring a New Chore | context-free, new since August | *"Never edit the package copy."* | writes under `src/gzkit/chores/<slug>/` |
| 11 | `chores.md` § Suppression | context-free, new since August | *"A chore never discharges a finding by suppression."* | `ruff --add-noqa`, `ty --add-ignore`, `pyrefly suppress` |
| 12 | `chores.md` § Prohibited Evidence | context-free | *"Raw SQL statements; Direct DB queries for attestation"* | `sqlite3`, `psql` |
| 13 | `gh-cli.md` § Prohibited without explicit approval | context-free | *"Repository/org settings mutations; Secret/token management; Force pushes; Merging PRs"* | `gh repo edit`, `gh secret`, `gh auth token`, `git push --force`, `gh pr merge` |
| 14 | `gh-cli.md` § Allowed commands, read as an allowlist | context-free if the block is exhaustive | the block lists `issue list`, `close`, `comment`, `reopen`, `release create` | `gh issue edit` and any unlisted mutating `gh` verb |
| 15 | `cli.md`, `changelog-release-notes.md` rule 3 | context-free | *"Release notes are never hand-written"* | writes to `RELEASE_NOTES.md`, `CHANGELOG.md` |
| 16 | `task-discovery.md` § Conventions | context-free, advisory in the rule | *"The trailer set is CLOSED… do not author [a harness session trailer]"* | `Claude-Session:` inside a commit message |
| 17 | `AGENTS.md` § PRIME DIRECTIVE 6, § Behavior Rules; `gh-cli.md` § Filing an issue | **context-dependent** | *"never `gh issue create` directly"*; *"The prohibition is on the **caller**, not the string"* | — |
| 18 | `AGENTS.md` § OBPI Acceptance Protocol | **context-dependent** | *"Never independently claim/release OBPI locks, create/clear pipeline markers, start/complete/block TASKs, dispatch OBPI implementers/reviewers, or edit briefs."* | — |
| 19 | `AGENTS.md` § Gate Covenant | **context-dependent** | *"Only a human may repudiate a Gate-5"*; the operator attests | — |
| 20 | `AGENTS.md` § SKILLS FIRST | **context-dependent** | *"Do not autonomously launch unrequested implementation work"* | — |
| 21 | `tests.md` § Verification exit-code integrity | **context-dependent**, hook-witnessed | a verifier's status must not be masked by a pipe, a chain or a group | — (position in a pipeline) |
| 22 | `mx-mode.md` § Do Not | **context-dependent** | *"Do not invoke `gz mx enter` or `gz mx exit` directly in a shell step"* | — |
| 23 | `adr-audit.md` § Rules | **context-dependent** | *"Do not run `gz audit` before attestation."* | — (temporal) |
| 24 | `token-block-discipline.md` Sub-Invariant 4 | **context-dependent** | *"reaping before expiry requires the operator's explicit `--force`"* | — |
| 25 | `task-discovery.md` § Conventions | **context-dependent** | *"Filing a GHI to satisfy the trailer is a moratorium violation"* | — |
| 26 | `security-sensitivity.md` § Do Not | **context-dependent** | *"Editing `data/security_surfaces.json` without declaring `sensitivity: security`"* | — |
| 27 | `agents-md-map-doctrine.md` § Shape enforcement | **context-dependent** | *"ordinary sessions add to sources… and never resize a render surface"* | — |
| 28 | `complexity-thresholds.md` § Operator-amendable mapping | **context-dependent**, validator-witnessed | *"Silent edits are forbidden"* | — |
| 29 | `AGENTS.md` § Attestation; `tests.md`; `cross-platform.md`; `models.md`; `pythonic.md` | context-free, not command-expressible | fabricated receipt ids; live databases in tests; `shell=True`; dataclasses; bare excepts | none: code or prose content, no command names it |

**29 entries: 16 context-free (rows 1 to 16), 12 context-dependent (17 to 28), 1 group that no
command expresses.** August enumerated 28 with a different numbering; rows 10, 11, 14 and 16 are
new, and August's `Never #1/#8` (bypass Gate 5) is now row 19.
