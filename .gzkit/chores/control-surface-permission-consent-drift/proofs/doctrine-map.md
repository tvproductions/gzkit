# Doctrine Map — Pass D run 2026-07-16

Re-derived from `AGENTS.md` + `.gzkit/rules/**` (26 rule files) this run. Prior-run map not consulted (CHORE.md § Known coverage limits #4 — the map is re-derived every run because a cached map can drift from AGENTS.md, reproducing the drift failure one level up).

Scope note: only prohibitions that could plausibly appear as a **command** in a permission rule are mapped. Prohibitions on artifacts, reasoning, or process (Gate 5 bypass, "do not read frontmatter as proof of completion", operator-PII, derived-views-as-source-of-truth) have no command surface and are out of scope by construction, not by omission.

## Context-free prohibitions (auditable by this pass)

| # | Doctrine citation | Verbatim | Command token(s) |
|---|---|---|---|
| CF-1 | `AGENTS.md:247` § Execution Rules | *"Always use `uv run` for Python commands. `gz --help` for full catalog."* | bare `python`, `python3` (any invocation not prefixed `uv run` / `uvx`) |
| CF-2 | `AGENTS.md:145` § Behavior Rules — Never #10 | *"Never commit with --no-verify. All commits and pushes must run through the configured hooks and quality gates."* | `--no-verify`, `git commit -n` |
| CF-3 | `AGENTS.md:94` § STDLIB-FIRST + `.gzkit/rules/tests.md:16` | *"Use **stdlib `unittest`**; no pytest. That means no pytest syntax, fixtures, parametrization, plugins, or bare py…"* — enforced by `forbid-pytest` pre-commit hook (`.pre-commit-config.yaml:31`) | `pytest` |
| CF-4 | `AGENTS.md:322` § Local Agent Rules | *"Never prefix `uv run gz` or `uv run -m gzkit` commands with `PYTHONUTF8=1` — the CLI entrypoint handles UTF-8 at runtime."* | `PYTHONUTF8=1 uv run gz`, `PYTHONUTF8=1 uv run -m gzkit` |
| CF-5 | `AGENTS.md:137` § Behavior Rules — Never #2 | *"NEVER: Modify the ledger directly (use gzkit commands)."* | `Edit(.gzkit/ledger.jsonl)` or any Edit rule whose glob covers it |
| CF-6 | `AGENTS.md:342` § Operator Doctrine (verbatim 2026-06-16) | *"Never create feature branches — work directly on main … 'don't do that feature branch bullshit again'"* | `git checkout -b`, `git switch -c` — **but see UW-2: broad-rule blind in practice** |

## Context-dependent prohibitions (NOT auditable — routed to unwitnessable.md)

| # | Doctrine citation | Verbatim | Why unauditable |
|---|---|---|---|
| CD-1 | `AGENTS.md:127` § Behavior Rules — Always #13 | *"Author GHIs through `/ghi-author` — never call `gh issue create` directly"* | Forbidden only *outside the skill*; `/ghi-author` invokes `gh issue create` itself at `SKILL.md:199`. Sanctioned and forbidden invocations are byte-identical. |
| CD-2 | `AGENTS.md:142` § Behavior Rules — Never #6 | *"Do not work around hook blocks. A blocking hook signals missing evidence or inactive pipeline state."* | "Working around" is an intent, not a command. No token distinguishes a legitimate retry from a workaround. |
| CD-3 | `AGENTS.md` § SKILLS FIRST | *"Matching skill first. No convenience exception."* | Prohibits raw-tool use *when a skill matches*. The same command is sanctioned or forbidden depending on whether a skill covers the task. |

## Counts

- Context-free, mapped: **6** (CF-1 … CF-6)
- Context-dependent, routed to `unwitnessable.md`: **3** (CD-1 … CD-3)
- Prohibitions with no command surface (out of scope by construction): Gate 5 bypass, frontmatter-as-proof, operator-PII, derived-views-as-truth, brief-boundary rules

**One in three command-shaped prohibitions in AGENTS.md is structurally invisible to this pass.** That ratio is the honest headline, not the drift count.
