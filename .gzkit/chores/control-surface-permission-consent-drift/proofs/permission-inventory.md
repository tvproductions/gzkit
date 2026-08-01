# Permission Inventory - Pass D run 2026-08-01

Both settings surfaces present this run. `.claude/settings.local.json` is gitignored
(`.gitignore:54`) - see `unwitnessable.md` UW-3: its rules are invisible to CI and to every
other machine.

| Surface | Committed? | allow | deny | Last commit |
|---|---|---|---|---|
| `.claude/settings.json` | yes | 0 | 6 | `758e33524` 2026-07-16 |
| `.claude/settings.local.json` | **no** (gitignored) | 180 | 0 | n/a - never committed |
| `_PERMITTED_BASH` (`src/gzkit/handoff_resume_gate.py:96-145`) | yes | 36 | (fail-closed default) | `44f7aac2e` 2026-08-01 |

Deny takes precedence over allow, so the 6 committed deny rules bind every allow rule below.

## Diff vs the 2026-07-16 run

```
$ diff <prior-run inventory allow block> <live .claude/settings.local.json allow>
(no output - IDENTICAL, 180 rules, 180 unique)
```

**The settings surfaces have not moved since the prior run.** `.claude/settings.json` last
committed 2026-07-16 (`758e33524`); the local file's mtime is 2026-07-16 09:37. Every new
finding in `consent-drift.md` this run comes from doctrine moving underneath a static
permission surface - `.gzkit/rules` last committed 2026-07-29 (`4b9db7592`). That is the
drift direction this chore's freshness gate was built to expose: nothing clicked
"always allow" since 2026-07-16; the rules that would have justified those clicks changed
anyway, and a `test -f` acceptance could never see it.

## .claude/settings.json (committed - policy)

### deny (6)

```
Bash(git *--no-verify*)
Bash(git *--no-verify)
Bash(git *commit -n *)
Bash(git *commit -n)
Bash(git *hooksPath=*)
Bash(git *config *hooksPath *)
```

### allow

_(none - deny-only by design: policy travels, convenience does not)_

Coverage note for CF-2: these six deny rules close `--no-verify` (2 forms), `git commit -n`
(2 forms), and `core.hooksPath` override (2 forms). They do **not** close `SKIP=<hook-id>`,
pre-commit's own per-hook bypass. See `consent-drift.md` row D-1.

## .claude/settings.local.json (machine-local - convenience)

### allow (180)

```
Edit(docs/**)
Edit(src/**)
Edit(tests/**)
Bash(grep:*)
WebFetch(domain:github.com)
WebFetch(domain:medium.com)
WebFetch(domain:redreamality.com)
WebFetch(domain:openspec.pro)
Bash(uvx ruff check src tests)
Bash(uvx ruff format --check .)
WebFetch(domain:promptkit.natebjones.com)
Bash(gh repo:*)
Bash(gh api:*)
WebFetch(domain:raw.githubusercontent.com)
Bash(for dir:*)
Bash(do echo:*)
Bash(done)
WebFetch(domain:www.anthropic.com)
WebFetch(domain:openai.github.io)
Bash(xargs -I {} dirname {})
WebFetch(domain:openai.com)
WebFetch(domain:docs.github.com)
WebSearch
WebFetch(domain:developers.openai.com)
WebFetch(domain:code.visualstudio.com)
Read(//tmp/**)
Bash(find:*)
Bash(ls:*)
Bash(uvx ty:*)
Bash(wc:*)
WebFetch(domain:slsa.dev)
Bash(sort -t. -k1,1n -k2,2n -k3,3n)
WebFetch(domain:www.ntia.gov)
Bash(gh auth:*)
Bash(gh issue:*)
Bash(for cmd:*)
Bash(do)
Bash(echo "OK: gz $cmd")
Bash(echo "FAIL: gz $cmd")
Bash(awk 'NR>=17 && NR<=46' /Users/jeff/Documents/Code/gzkit/src/gzkit/commands/preflight.py)
Bash(awk 'NR>=91 && NR<=141' /Users/jeff/Documents/Code/gzkit/src/gzkit/commands/preflight.py)
Bash(xargs -I {} basename {})
Bash(while read:*)
Bash(do basename:*)
Bash(sort -t. -k2,2n -k3,3n)
WebFetch(domain:alignment.anthropic.com)
WebFetch(domain:docs.anthropic.com)
mcp__plugin_playwright_playwright__browser_navigate
Bash(npx playwright:*)
Bash(PLAYWRIGHT_BROWSERS_PATH="$HOME/Library/Caches/ms-playwright" npx playwright install --list 2>&1)
WebFetch(domain:arxiv.org)
WebFetch(domain:transformer-circuits.pub)
WebFetch(domain:www.lesswrong.com)
Bash(cp .github/skills/gz-obpi-pipeline/SKILL.md .claude/skills/gz-obpi-pipeline/SKILL.md)
Bash(cp .github/skills/gz-obpi-pipeline/DISPATCH.md .claude/skills/gz-obpi-pipeline/DISPATCH.md)
Bash(cp .github/skills/gz-obpi-pipeline/VERIFICATION.md .claude/skills/gz-obpi-pipeline/VERIFICATION.md)
Bash(cp .github/skills/gz-obpi-pipeline/REFERENCE.md .claude/skills/gz-obpi-pipeline/REFERENCE.md)
WebFetch(domain:x.com)
WebFetch(domain:nitter.net)
WebFetch(domain:threadreaderapp.com)
Bash(for skill:*)
Bash(echo "=== $skill ===")
Bash(for mirror:*)
Bash(cp .gzkit/skills/gz-plan-audit/SKILL.md "$mirror/gz-plan-audit/SKILL.md")
Bash(echo "Synced: $mirror")
Bash(uv build:*)
Bash(uv tool:*)
Bash(head -50 /Users/jeff/Documents/Code/gzkit/docs/design/adr/pre-release/ADR-0.14.0*/ADR*.md)
Bash(gh label:*)
Bash(export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH")
Bash(for f:*)
Bash(do sed:*)
Bash(brew --prefix gh)
Read(//opt/homebrew/**)
Bash(export PATH="/opt/homebrew/bin:/opt/homebrew/Cellar/gh/2.89.0/bin:$HOME/.local/bin:$HOME/.cargo/bin:$PATH")
Bash(export PATH="/opt/homebrew/bin:$HOME/.local/bin:$HOME/.cargo/bin:$PATH")
Bash(SKIP=gitleaks uv run gz git-sync --apply --lint --test)
Bash(echo PATH=$PATH)
Bash(echo SHELL=$SHELL)
Read(//Users/jeff/**)
Bash(source ~/.zprofile)
Bash(source ~/.zshrc)
WebFetch(domain:strategicdecisionsolutions.com)
WebFetch(domain:www.sei.cmu.edu)
WebFetch(domain:ardura.consulting)
WebFetch(domain:nazdelam.medium.com)
WebFetch(domain:www.theuncertaintyproject.org)
WebFetch(domain:www.viewpoints-and-perspectives.info)
WebFetch(domain:www.geeksforgeeks.org)
WebFetch(domain:wellarchitected.github.com)
WebFetch(domain:www.techtarget.com)
WebFetch(domain:continuousarchitecture.com)
WebFetch(domain:www.humintell.com)
WebFetch(domain:problemsolving.engin.umich.edu)
WebFetch(domain:rogermartin.medium.com)
Bash(gh release:*)
Bash(uvx xenon:*)
WebFetch(domain:pydantic.dev)
Bash(sed:*)
Bash(curl -sL "https://transformer-circuits.pub/2025/attribution-graphs/biology.html" -o /tmp/biology.html)
Bash(curl -sL -A "Mozilla/5.0" "https://blog.bytebytego.com/p/how-anthropics-claude-thinks" -o /tmp/bbg.html)
Bash(git *)
Bash(gh search:*)
Bash(cat)
Bash(bash /tmp/time_tests.sh)
Bash(gh run *)
WebFetch(domain:tvproductions.github.io)
Bash(gh workflow *)
Bash(/usr/bin/time -p uv run gz --help)
Bash(uv pip *)
Bash(curl -s https://pypi.org/pypi/ty/json)
Bash(awk '{print $2}')
Bash(perl -i -pe ' *)
Bash(perl -i -pe 's/^from typing import Any, Callable$/from collections.abc import Callable\\nfrom typing import Any/' src/gzkit/cli/parser_artifacts.py src/gzkit/cli/parser_governance.py src/gzkit/cli/parser_maintenance.py)
Bash(uv sync *)
Bash(uvx unittest-parallel *)
Bash(time GZKIT_TIER=integration uv run -m unittest discover tests/integration)
Bash(GZKIT_TIER=integration uv run -m unittest discover tests/integration)
Bash(GZKIT_TIER=integration uv run -m unittest tests.integration.commands.test_audit.TestConfigAndCliAuditCommands.test_cli_audit_detects_mismatch)
Bash(awk -F':' '{print $2}')
Bash(mv docs/design/adr/pre-release/ADR-0.42.0-frontmatter-ledger-coherence-guard docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard)
Bash(mv docs/design/adr/ADR-0.0.16.md docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md)
Bash(echo "EXIT: $?")
WebFetch(domain:agents.md)
WebFetch(domain:claude.com)
Bash(xargs -I {} bash -c "ls -la {} 2>/dev/null | grep -E 'output-styles|statusline'")
WebFetch(domain:deploymentsafety.openai.com)
WebFetch(domain:cdn.sanity.io)
Bash(curl -sL -o /tmp/syscards/gpt-5-5.pdf "https://deploymentsafety.openai.com/gpt-5-5/gpt-5-5.pdf")
Bash(curl -sL -o /tmp/syscards/anthropic.pdf "https://cdn.sanity.io/files/4zrzovbb/website/037f06850df7fbe871e206dad004c3db5fd50340.pdf")
Bash(pdftotext -layout gpt-5-5.pdf gpt-5-5.txt)
Bash(pdftotext -layout anthropic.pdf anthropic.txt)
Bash(wait)
Bash(codex --help)
Bash(codex plugin *)
Bash(curl -s https://tvproductions.github.io/gzkit/user/)
Bash(xargs -I {} sh -c 'echo "=== {} ===" && head -40 "{}"')
Bash(GZKIT_DOCS_VERSION=v0.test uv run -m mkdocs build --strict --site-dir /tmp/gzkit-test-site)
WebFetch(domain:gzkit.readthedocs.io)
Bash(curl -sS https://gzkit.readthedocs.io/en/latest/user/runbook/)
Bash(uvx radon *)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/size-cap.txt)
Bash(awk '{print $1, $3}')
Bash(sort -k2 -n -r)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/complexity.txt)
Bash(uv run *)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/lint.txt)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/types.txt)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/cli-drift.txt)
Bash(tee -a .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/cli-drift.txt)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/governance.txt)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/todo-rot.txt)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/types-suppression.txt)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/tests.txt)
Bash(tee -a .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/tests.txt)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/validators.txt)
Bash(tee .gzkit/audits/tech-debt/2026-04-29-ADR-0.0.21/probes/cc.txt)
Bash(echo "exit=$?")
Bash(echo "---exit=$?---")
Bash(echo "ADR-0.0.16 audit-check exit=$?")
Bash(tee .gzkit/chores/instructions-files-diet/proofs/post-trim-2026-05-04.txt)
Bash(chmod +x *)
Bash(xargs -I {} basename {} .py)
Skill(git-commit:*)
Bash([ -f ".claude/skills/$skill/SKILL.md" ])
Bash([ -f ".github/skills/$skill/SKILL.md" ])
Bash(echo "Exit code: $?")
Bash([ -f "docs/user/commands/$f.md" ])
Bash(rmdir docs/user/commands/)
Bash(echo "---EXIT: $?")
Bash(mkdir *)
Bash(/Users/jeff/Documents/Code/gzkit/.venv/bin/gz --version)
Bash(rm -rf /tmp/gz-personas-demo2)
Bash(/Users/jeff/Documents/Code/gzkit/.venv/bin/gz init *)
Bash(rm -rf /tmp/gz-templates-demo)
Bash(echo "captured exit=$?")
Skill(ghi-author)
Bash(date -v-30d +%Y-%m-%d)
Bash(kill -9 3820 3525 3816 3521)
Bash(ps -Ao pid,rss,args)
```

## Extended surface (parent-task scope): `_PERMITTED_BASH`

Not named by CHORE.md v1.0.0 § Overview, which scopes the pass to the two settings files.
Added this run on the dispatching operator's instruction (2026-08-01): *"the permission
surface includes `.claude/settings.json` (and any `settings.local.json`), the hook allowlists
under `.claude/hooks/`, and the standing-consent doctrine in `AGENTS.md` and `.gzkit/rules/`"*.
Recorded as an explicit scope extension rather than silently folded in.

Survey of `.claude/hooks/*.py` (15 hooks) found **exactly one** allowlist: none of the 15
adapters carries an `ALLOW` / `PERMITTED` / `SAFE_` / `WHITELIST` constant (grep returned no
matches). `handoff-resume-gate.py` is a thin adapter over `gzkit.handoff_resume_gate`, where
the allowlist actually lives. It is a **committed, doctrine-derived** standing-consent
surface - unlike `settings.local.json` it IS visible to CI and to every clone, which makes
it the one part of this pass that is reproducible off the authoring machine.

### `_PERMITTED_BASH` allow (36 command prefixes; unmatched command = refused)

```
gz handoff authorize
gz obpi status
gz obpi lock list
gz gates
gz state
gz status
gz adr status
gz context
gz handoff list
gz handoff resume
gh issue view
gh issue list
gh issue status
gh pr view
gh pr list
gh pr diff
gh pr status
gh release view
gh release list
git status
git log
git diff
git show
git branch
git rev-parse
git ls-files
grep
rg
ls
cat
head
tail
wc
find
jq
pwd
```

### `_MUTATING_FLAGS` (revokes an otherwise-allowlisted head)

```
-i   --in-place   -delete   -exec   --fix
```

## Fossil grants (no doctrine contradiction - recorded, not routed)

These carry no drift row: no doctrine forbids them. They are logged because each is a
one-time "always allow" click frozen into a permanent rule, which is the accretion mechanism
CHORE.md § Overview names - *"Every 'always allow' click converts a one-time situational
judgment into a permanent rule that outlives the context that justified it."*

| Allow rule (verbatim) | Why it is dead |
|---|---|
| `Bash(kill -9 3820 3525 3816 3521)` | Pinned to four PIDs from a past session. PIDs are recycled by the OS, so the grant now names whatever processes happen to hold those numbers. |
| `Bash(mv docs/design/adr/pre-release/ADR-0.42.0-frontmatter-ledger-coherence-guard docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard)` | One-shot semver migration, completed. Source path no longer exists. |
| `Bash(rmdir docs/user/commands/)` | Directory removed; `docs/user/manpages/` is the live surface. |
| `Bash(rm -rf /tmp/gz-personas-demo2)`, `Bash(rm -rf /tmp/gz-templates-demo)` | Demo scratch dirs from a one-off `gz init` run. |
| `Bash(bash /tmp/time_tests.sh)` | Script lived in `/tmp` and is long gone; the rule now grants execution of whatever next occupies that path. |
| `Bash(cp .github/skills/gz-obpi-pipeline/{DISPATCH,VERIFICATION,REFERENCE}.md ...)` | Source files no longer exist (the skill's aux docs moved under `references/`). Dead **and** doctrine-contradicting - see `consent-drift.md` rows D-3..D-5. |
