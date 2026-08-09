# Doctrine Map — Pass D

> Chore: `control-surface-permission-consent-drift` (Lite lane, audit-only)
> Run: **2026-08-09**. **Re-derived from the corpus, not carried from the prior run**
> (CHORE.md § Workflow 1 — the map is hand-maintained and can itself drift, which
> would reproduce the failure one level up).

Prohibitions enumerated from root `AGENTS.md` (§ Execution Rules, § Behavior Rules
— Never / Always, § Operator Doctrine, § Local Agent Rules, § STDLIB-FIRST) and
`.gzkit/rules/**`.

**Only `context-free` entries are eligible for a drift row.** `context-dependent`
entries route to [`unwitnessable.md`](unwitnessable.md) without pattern-matching —
their sanctioned and forbidden invocations are byte-identical.

| Doctrine citation | Kind | Verbatim quote (trimmed) | Command token(s) |
|---|---|---|---|
| `AGENTS.md` § Execution Rules | context-free | *"Always use `uv run` for Python commands."* | `python`, `python3`, `pip` |
| `AGENTS.md` § Never #2 | context-free | *"NEVER: Modify the ledger directly (use gzkit commands)."* | writers targeting `.gzkit/ledger.jsonl` |
| `AGENTS.md` § Never #6 | context-free | *"Do not work around hook blocks… never hand-write marker files or ledger entries."* | writes to `.gzkit/**` marker/ledger paths |
| `AGENTS.md` § Never #9 | **context-dependent** | *"Run every stage through the governing skill, not via direct CLI."* | — |
| `AGENTS.md` § Never #10 | context-free | *"Never commit with `--no-verify`. All commits and pushes must run through the configured hooks and quality gates."* | `--no-verify`, `commit -n`, `hooksPath`, `SKIP=<hook-id>` |
| `AGENTS.md` § Never #1/#8 | context-free (not command-expressible) | *"NEVER: Bypass Gate 5 (human attestation)."* | none — no command string names a bypass |
| `AGENTS.md` § Always #11 | context-free | *"never hand-append the jsonl"* | writes to `.gzkit/insights/agent-insights.jsonl` |
| `AGENTS.md` § Always #13 | **context-dependent** | *"Author GHIs through `/ghi-author` — never call `gh issue create` directly"* | — |
| `AGENTS.md` § Local Agent Rules | context-free | *"Never prefix `uv run gz` … with `PYTHONUTF8=1`"* | `PYTHONUTF8=1` |
| `AGENTS.md` § Local Agent Rules (PII) | context-free | *"never include the operator's personal email in any repo-bound artifact"* | the literal address; `git config user.email`, `--author`, `Co-authored-by` |
| `AGENTS.md` § Operator Doctrine | context-free | *"Never create feature branches — work directly on main… no `fix/*` or `feature/*` branches"* | `git checkout -b`, `git switch -c`, `git branch <name>` |
| `AGENTS.md` § STDLIB-FIRST | context-free | *"**Testing:** `unittest` over pytest."* | `pytest` |
| `governance-core.md` § Non-negotiable rules | context-free | *"Do not edit `.gzkit/ledger.jsonl` manually."* | same as Never #2 |
| `skill-surface-sync.md` § Non-negotiable #4 | context-free | *"**Never edit vendor mirrors directly.** `.claude/skills/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/` are generated outputs."* | write/`cp`/`mv` targeting those four roots |
| `skill-surface-sync.md` § Non-negotiable #5 | context-free | *"**Never edit `src/gzkit/<surface>/` directly.**"* | Edit/Write under `src/gzkit/{skills,rules,personas,templates}/` |
| `skill-surface-sync.md` § Do Not | context-free | *"Do not manually copy skill files between surfaces — use the sync command"* | `cp`/`mv` between skill-surface roots |
| `gh-cli.md` § Prohibited without explicit approval | context-free | *"Repository/org settings mutations"* | `gh repo edit\|delete\|archive`, `gh api -X PATCH /repos/…` |
| `gh-cli.md` § Prohibited without explicit approval | context-free | *"Secret/token management"* | `gh auth login\|logout\|refresh\|token`, `gh secret …` |
| `gh-cli.md` § Prohibited without explicit approval | context-free | *"Force pushes"* | `git push --force`, `-f`, `--force-with-lease` |
| `gh-cli.md` § Prohibited without explicit approval | context-free | *"Merging PRs without explicit human authorization"* | `gh pr merge` |
| `gh-cli.md` § Filing an issue | **context-dependent** | *"The prohibition is on the **caller**, not the string"* | — |
| `chores.md` § Evidence & Attestation | context-free | *"Prohibited Evidence: Raw SQL statements; Direct DB queries"* | `sqlite3`, `psql` |
| `tests.md` § Verification exit-code integrity | **context-dependent** | *"NEVER pipe `unittest`/`behave`/`mkdocs --strict` … through `tail`/`head`/`grep`"* | — (forbidden only in a non-final pipeline stage) |
| `mx-mode.md` § Do Not | **context-dependent** | *"Do not invoke `gz mx enter` or `gz mx exit` directly in a shell step — use the `gz-mx` skill"* | — |
| `adr-audit.md` § Do Not | **context-dependent** | *"Do not run `gz audit` before attestation."* | — (temporal precondition) |
| `cli.md` | context-free | *"**do not hand-write release notes.** `RELEASE_NOTES.md` and `CHANGELOG.md` are authored at release time by the `gz-patch-release` ceremony"* | Edit/Write of `RELEASE_NOTES.md`, `CHANGELOG.md` |
| `tests.md` § Unit-test rules | context-free (not command-expressible) | *"unit tests MUST use `tempfile` temp DBs; NEVER use live/production databases"* | none — code content, no path or command |

## Counts

| Kind | Count |
|---|---|
| context-free, command-expressible | 19 |
| context-free, **not** command-expressible | 3 |
| context-dependent | 6 |

The three *not command-expressible* entries are context-free in principle — the act
is forbidden outright — but name no command or path a matcher could see. They are
listed here rather than silently dropped, and routed to `unwitnessable.md` § U13.
