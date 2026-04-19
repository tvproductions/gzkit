# Claude Code Feature Inventory

Detailed capability-level inventory built from eight Claude Code documentation pages. Organized by category, one row per capability, to support later side-by-side comparison with Codex.

## Source key

| Abbr. | Page |
|---|---|
| OV | [Overview](https://code.claude.com/docs/en/overview) |
| HW | [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) |
| DIR | [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory) |
| CW | [Explore the context window](https://code.claude.com/docs/en/context-window) |
| MEM | [How Claude remembers your project](https://code.claude.com/docs/en/memory) |
| PM | [Choose a permission mode](https://code.claude.com/docs/en/permission-modes) |
| CWF | [Common workflows](https://code.claude.com/docs/en/common-workflows) |
| BP | [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices) |

---

## Inventory

| # | Feature | Category | What it does | Invocation / Location | Configuration | Notes & caveats | Source |
|---|---|---|---|---|---|---|---|
| 1 | Native install script (macOS/Linux/WSL) | Install | Installs Claude Code CLI | `curl -fsSL https://claude.ai/install.sh \| bash` | N/A | Auto-updates in background | OV |
| 2 | Native install (Windows PowerShell) | Install | Installs Claude Code CLI | `irm https://claude.ai/install.ps1 \| iex` | Requires Git for Windows on native (not WSL) | Auto-updates | OV |
| 3 | Native install (Windows CMD) | Install | Installs Claude Code CLI | `curl ... install.cmd && install.cmd` | As above | Auto-updates | OV |
| 4 | Homebrew stable | Install | Package-managed install, stable channel | `brew install --cask claude-code` | Runs ~1 week behind, skips releases with major regressions | No auto-update; run `brew upgrade claude-code` | OV |
| 5 | Homebrew latest | Install | Package-managed install, latest channel | `brew install --cask claude-code@latest` | Receives versions as they ship | No auto-update | OV |
| 6 | WinGet | Install | Windows package install | `winget install Anthropic.ClaudeCode` | N/A | No auto-update; `winget upgrade Anthropic.ClaudeCode` | OV |
| 7 | VS Code extension | Interface | Inline diffs, @-mentions, plan review, conversation history in editor | VS Code marketplace or `vscode:extension/anthropic.claude-code` | Settings via `claudeCode.initialPermissionMode` etc. | Also works in Cursor and other VS Code forks | OV, PM |
| 8 | JetBrains plugin | Interface | IntelliJ/PyCharm/WebStorm integration with interactive diff viewing | JetBrains Marketplace | Launches Claude Code in IDE terminal | Same Shift+Tab mode switching as CLI | OV, PM |
| 9 | Desktop app | Interface | Standalone app; visual diff review, parallel sessions, scheduled tasks, cloud sessions | macOS (Intel/ARM), Windows x64, Windows ARM64 | Paid subscription required | Separate Mode selector in UI | OV, PM |
| 10 | Web (claude.ai/code) | Interface | Browser-based, no local setup, cloud VMs, long-running tasks | `claude.ai/code` | Mode dropdown next to prompt box | Cloud sessions only support acceptEdits and plan | OV, PM |
| 11 | iOS app | Interface | Mobile access, can kick off tasks | Claude iOS app | N/A | Pairs with `claude --teleport` | OV |
| 12 | Chrome extension (beta) | Interface | Live web application debugging; opens tabs, tests UI, iterates | Chrome Web Store | N/A | Beta; used for visual verification | OV, BP |
| 13 | Slack integration | Interface | `@Claude` in Slack to route bug reports, trigger PRs | Slack app install | Per-workspace setup | Bug-report-to-PR workflow supported | OV |
| 14 | Remote Control | Interface | Phone/browser controls session running on your local machine | `claude remote-control [--permission-mode ...]` | Starting permission mode configurable | Prompts appear in claude.ai for approval | OV, PM |
| 15 | Channels | Interface | Push events from Telegram, Discord, iMessage, or webhooks into a session | N/A | Per-channel config | Not detailed in source pages | OV |
| 16 | Dispatch | Interface | Message a task from phone, opens Desktop session | Desktop app | N/A | Part of cross-surface handoff | OV |
| 17 | `claude --teleport` | Interface | Kick off task on web/iOS, pull into terminal | CLI flag | N/A | Cross-surface session handoff | OV |
| 18 | `/desktop` slash command | Interface | Hand off terminal session to Desktop app for visual diff review | In-session | N/A | Reverse of `--teleport` | OV |
| 19 | Local execution environment | Env | Code runs on your machine, full access to files and tools | Default | N/A | Default execution model | HW |
| 20 | Cloud execution environment | Env | Code runs on Anthropic-managed VMs | Web interface primarily | N/A | For offloaded or long-running work, or repos you don't have locally | HW |
| 21 | Remote Control environment | Env | Code runs on your machine, controlled via browser | `claude remote-control` | Permission mode flag | Hybrid of local execution + web UI | HW, PM |
| 22 | Agentic loop | Architecture | Three phases: gather context → take action → verify; chains dozens of actions with course-correction | Automatic | None | User can interrupt at any point | HW |
| 23 | Model selection | Architecture | Sonnet (default), Opus (stronger reasoning), Haiku | `/model` in session; `claude --model <name>` | Per-session or startup | Sonnet 4.6 / Opus 4.6 / Opus 4.7 are referenced in auto mode and thinking docs | HW, PM |
| 24 | File operations tools | Tools | Read, edit, create, rename, reorganize | Automatic | Controlled by permission mode and allow/deny rules | Core agency | HW |
| 25 | Search tools | Tools | Find files by pattern, regex content search, explore codebases | Automatic | N/A | No codebase indexing; search on demand | HW |
| 26 | Execution tools (Bash) | Tools | Run shell commands, start servers, run tests, use git | Automatic | Permission rules, sandboxing | Prompts in default mode | HW |
| 27 | Web tools | Tools | Search web, fetch docs, look up error messages | Automatic | Allowlist domains via `/permissions` | | HW, BP |
| 28 | Code intelligence | Tools | See type errors, jump to definitions, find references | Requires code intelligence plugins | Language-specific plugins | Plugin-gated capability | HW |
| 29 | Subagent spawning | Tools | Delegate isolated tasks in separate context | Claude invokes automatically or on explicit request | Subagent definitions in `.claude/agents/` | | HW, CWF |
| 30 | `AskUserQuestion` tool | Tools | Claude asks user structured questions; used by Plan Mode to gather requirements | Automatic in Plan Mode | N/A | Also usable for "interview me" prompts | CWF, BP |
| 31 | Session persistence | Sessions | Each message, tool use, result stored locally | Automatic | Storage is per project directory | Enables rewind, resume, fork | HW |
| 32 | Pre-edit file snapshots | Sessions | Claude snapshots file contents before any edit | Automatic | N/A | Enables checkpoint rewind | HW |
| 33 | `claude --continue` | Sessions | Resume most recent session in current directory | CLI flag | N/A | Also works with `--print` | HW, CWF, BP |
| 34 | `claude --resume [name]` | Sessions | Open session picker or resume by exact name | CLI flag | N/A | Ambiguous names open picker with search pre-filled | HW, CWF |
| 35 | `/resume` in-session | Sessions | Switch to another conversation from active session | In-session | N/A | Ambiguous name errors, must run without arg | CWF |
| 36 | `claude --from-pr <number>` | Sessions | Resume session linked to a PR | CLI flag | Auto-linked when `gh pr create` runs | | CWF |
| 37 | `--fork-session` | Sessions | Branch off a new session preserving history up to that point | CLI flag with `--continue` | Creates new session ID | Does not inherit session-scoped permissions | HW |
| 38 | `claude -n <name>` (session naming at startup) | Sessions | Name a session at creation | CLI flag | N/A | Appears on prompt bar | CWF |
| 39 | `/rename` | Sessions | Rename session in progress | In-session | N/A | Also `Ctrl+R` in picker | CWF |
| 40 | Session picker | Sessions | Interactive UI to select and resume sessions | `/resume` or `claude --resume` with no arg | N/A | Shortcuts: ↑↓→← Enter Space Ctrl+R Ctrl+A Ctrl+W Ctrl+B Esc | CWF |
| 41 | Forked session grouping | Sessions | Forks collapsed under root session in picker | Automatic | N/A | Related conversations kept together | CWF |
| 42 | Context window (core) | Context | Holds history, file contents, command outputs, CLAUDE.md, auto memory, loaded skills, system instructions | Automatic | Model-dependent | 1M context included for Max/Team/Enterprise with Opus 4.6/4.7 | HW, CW |
| 43 | Auto-compaction | Context | When context fills, clears older tool outputs first, then summarizes | Automatic | `Compact Instructions` section in CLAUDE.md | Early detailed instructions may be lost | HW, BP |
| 44 | `/compact [focus]` | Context | Manual compaction with optional focus | In-session | `/compact focus on the API changes` | Project-root CLAUDE.md survives; nested ones reload on demand | HW, MEM, BP |
| 45 | `/context` | Context | Live breakdown of token usage by category | In-session | N/A | System prompt, memory, skills, MCP tools, messages | HW, DIR, CW |
| 46 | Partial-context compaction from checkpoint | Context | Summarize from a selected message forward, preserving earlier context | `Esc+Esc` or `/rewind`, then "Summarize from here" | N/A | Condense part of the conversation without losing setup | BP |
| 47 | MCP tool definition deferral | Context | Only tool names in context at start; full definitions load on demand via tool search | Automatic | `/mcp` shows per-server cost | Reduces startup context cost | HW |
| 48 | Skill lazy loading | Context | Descriptions visible at session start; body loads only when skill used | Automatic | `disable-model-invocation: true` to keep description out of context | Lets users hold many skills without context bloat | HW |
| 49 | `/btw` side questions | Context | Ask quick question, answer appears in dismissible overlay, not added to context | In-session | N/A | Keeps main context clean during focused work | BP |
| 50 | Subagent context isolation | Context | Subagents run in separate context window; return summary to parent | Automatic or explicit invocation | Subagent defs in `.claude/agents/` | Single strongest tool for long sessions | HW, BP |
| 51 | CLAUDE.md (project root) | Memory | Markdown instructions loaded every session | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Commit to git for team sharing | Target under 200 lines | MEM, BP |
| 52 | CLAUDE.md (user/home) | Memory | Personal instructions across all projects | `~/.claude/CLAUDE.md` | Personal | | MEM, BP |
| 53 | CLAUDE.local.md | Memory | Personal per-project preferences, gitignored | `./CLAUDE.local.md` | Add to `.gitignore`; `/init` personal option does this | In gitignored form, only exists in the worktree where created | MEM, BP |
| 54 | Managed policy CLAUDE.md | Memory | Org-wide instructions; cannot be excluded | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux/WSL: `/etc/claude-code/CLAUDE.md`; Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | Deploy via MDM, Group Policy, Ansible | Takes precedence over user settings; not excludable | MEM |
| 55 | CLAUDE.md directory walk | Memory | Walks up from CWD, concatenates all found CLAUDE.md and CLAUDE.local.md | Automatic | N/A | Subdirectory CLAUDE.md loads on demand when files read in those dirs | MEM |
| 56 | `@path/to/import` syntax | Memory | Import other files into CLAUDE.md | `@README.md`, `@~/.claude/my-project.md` | Relative paths resolve to containing file | Max depth 5; recursive imports allowed; approval dialog on first external import | MEM, BP |
| 57 | `/init` | Memory | Generate starter CLAUDE.md based on codebase | In-session | `CLAUDE_CODE_NEW_INIT=1` for multi-phase interactive flow | Claude suggests improvements if CLAUDE.md already exists | MEM, BP |
| 58 | AGENTS.md compatibility | Memory | Not read natively; bridge via `@AGENTS.md` import | Manual bridge in CLAUDE.md | N/A | Lets repos stay compatible with other coding agents | MEM |
| 59 | `--add-dir` flag | Memory | Give Claude access to additional directories | CLI flag | `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` to also load CLAUDE.md from those dirs | By default, memory files from added dirs not loaded | MEM |
| 60 | HTML comment stripping | Memory | Block-level `<!-- -->` in CLAUDE.md removed before context injection | Automatic | N/A | Comments in code blocks preserved; Read tool shows them | MEM |
| 61 | `.claude/rules/*.md` | Rules | Topic-scoped instruction files, discovered recursively | `.claude/rules/testing.md` etc. | Loaded at launch if no frontmatter | Same priority as `.claude/CLAUDE.md` | MEM, DIR |
| 62 | Path-scoped rules | Rules | Rules only load when Claude works with matching files | YAML frontmatter `paths: ["src/**/*.ts"]` | Glob patterns, brace expansion | Triggers on file read, not every tool use | MEM |
| 63 | Rule symlinks | Rules | Share rules across projects via symlinks | `ln -s ~/shared-rules .claude/rules/shared` | N/A | Circular symlinks handled | MEM |
| 64 | User-level rules | Rules | Personal rules across all projects | `~/.claude/rules/*.md` | N/A | Loaded before project rules | MEM |
| 65 | `claudeMdExcludes` | Memory | Skip specific CLAUDE.md files by path/glob | `settings.local.json` or any settings layer | Arrays merge across layers | Cannot exclude managed-policy CLAUDE.md | MEM |
| 66 | Auto memory (MEMORY.md) | Memory | Claude writes notes to itself across sessions | `~/.claude/projects/<project>/memory/` | `autoMemoryEnabled`, `autoMemoryDirectory` settings; `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` | Requires v2.1.59+; first 200 lines or 25KB of MEMORY.md loaded at startup | MEM, HW |
| 67 | Auto memory topic files | Memory | Detailed notes split into separate files, loaded on demand | e.g. `debugging.md`, `api-conventions.md` in memory dir | N/A | Not loaded at startup; Claude reads on demand | MEM |
| 68 | `/memory` | Memory | List loaded instruction files, toggle auto memory, open memory folder | In-session | N/A | Plain markdown, user-editable | MEM, DIR |
| 69 | `InstructionsLoaded` hook | Memory | Log exactly which instruction files loaded | Hook config | N/A | Useful for debugging path-specific rules | MEM |
| 70 | `--append-system-prompt` | Memory | Append text to the system prompt itself | CLI flag | Per invocation | Must pass every time; better for scripts | MEM, CW |
| 71 | Skills | Extension | Reusable prompts invoked with `/name` or auto-invoked; can take `$ARGUMENTS` | `.claude/skills/<name>/SKILL.md`, `~/.claude/skills/<name>/SKILL.md` | `disable-model-invocation: true` to require manual trigger | Descriptions in context at start; body loads on use | BP, DIR |
| 72 | Single-file commands | Extension | Simpler form of skills; single markdown file | `.claude/commands/*.md`, `~/.claude/commands/*.md` | Same mechanism as skills | | DIR |
| 73 | Subagents | Extension | Specialized agents with own prompt, tools, model; isolated context | `.claude/agents/*.md`, `~/.claude/agents/*.md` | `name`, `description`, `tools`, `model`, `isolation: worktree` frontmatter | Automatic delegation via description field; explicit via prompt; max 3 parallel before UX collapses outputs | BP, CWF, DIR |
| 74 | `/agents` | Extension | View, configure, and create subagents | In-session | N/A | Walks through subagent creation | CWF |
| 75 | Subagent persistent memory | Extension | Subagents can maintain their own auto memory | `agent-memory/<name>/` | N/A | Per subagent; committed with project | DIR, MEM |
| 76 | Subagent worktree isolation | Extension | Each subagent runs in its own worktree | `isolation: worktree` in frontmatter, or ask Claude to "use worktrees for your agents" | N/A | Auto cleanup when subagent finishes without changes | CWF |
| 77 | Hooks | Extension | Shell commands that run at workflow points; deterministic | `.claude/settings.json` hooks section | Events include `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Notification`, `InstructionsLoaded`, `WorktreeCreate`, `WorktreeRemove` | Claude can write hooks on request | BP, OV, MEM, CWF |
| 78 | `/hooks` | Extension | Browse configured hooks | In-session | N/A | | DIR, BP |
| 79 | `Notification` hook matchers | Extension | Narrow notification hook to specific events | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog` | matcher field in hooks config | Default matcher fires on all | CWF |
| 80 | MCP servers | Extension | Connect Claude to external tools (Jira, Figma, Google Drive, custom tooling) | `claude mcp add` at user scope; `.mcp.json` at project scope | Project scope committed for team sharing | MCP tool defs deferred until used | OV, BP, DIR |
| 81 | `/mcp` | Extension | Connected MCP servers and status, per-server costs | In-session | N/A | | HW, DIR |
| 82 | MCP resource references | Extension | `@server:resource` syntax to fetch from connected MCP server | In prompts | N/A | e.g., `@github:repos/owner/repo/issues` | CWF |
| 83 | Plugins | Extension | Bundle skills, hooks, subagents, MCP servers as installable unit | `/plugin` to browse marketplace | N/A | Code intelligence plugins add symbol nav and error detection | BP |
| 84 | Output styles | Customization | Custom system-prompt sections | `output-styles/*.md` | Project or global | Load into system prompt at startup | DIR, CW |
| 85 | Keybindings | Customization | Custom keyboard shortcuts | `~/.claude/keybindings.json` | Global only | | DIR |
| 86 | Status line | Customization | Custom status line, track context usage continuously | Custom status line config | N/A | Recommended for context tracking | BP |
| 87 | `settings.json` | Config | Permissions, hooks, env vars, model defaults, etc. | Project or global | Commit project version | | DIR |
| 88 | `settings.local.json` | Config | Personal overrides, auto-gitignored | Project only | N/A | Not committed | DIR |
| 89 | Managed settings | Config | Enterprise-enforced settings that cannot be overridden | System-level; location varies by OS | `forceLoginMethod`, `forceLoginOrgUUID`, `permissions.deny`, `sandbox.enabled`, `env` | Deployed via MDM, Group Policy, etc. | DIR, MEM |
| 90 | `~/.claude.json` | Config | App state, OAuth, UI toggles, personal MCP servers | Global only, not committed | Managed by app | | DIR |
| 91 | `default` permission mode | Permissions | Claude asks before file edits and shell commands | Startup default | `--permission-mode default` | Baseline, best for sensitive work | HW, PM |
| 92 | `acceptEdits` permission mode | Permissions | Edits files without asking, still prompts for commands | `Shift+Tab` once, or `--permission-mode acceptEdits` | | Best for iterating on code you're reviewing | HW, PM |
| 93 | `plan` permission mode | Permissions | Read-only; writes a plan, no source edits | `Shift+Tab` twice, `--permission-mode plan`, `/plan` prefix | | Still prompts for Bash and network | HW, PM |
| 94 | `auto` permission mode | Permissions | Classifier-gated, no prompts unless fallback triggers | `Shift+Tab` (after `--enable-auto-mode`); `--permission-mode auto` | Team/Enterprise/API plan; Sonnet 4.6 or Opus 4.6 required; admin enable on Team/Enterprise | Research preview; classifier on Sonnet 4.6; counts toward token usage; added latency | HW, PM, BP |
| 95 | `dontAsk` permission mode | Permissions | Auto-denies everything not explicitly allowed | `--permission-mode dontAsk` | Pre-approved allow rules only | Fully non-interactive; `ask` rules also denied | PM |
| 96 | `bypassPermissions` permission mode | Permissions | Skip all prompts and checks | `--permission-mode bypassPermissions` or `--dangerously-skip-permissions` | Can be disabled via `permissions.disableBypassPermissionsMode` in managed settings | Still prompts on `.git`, `.vscode`, `.idea`, most of `.claude`; for isolated containers only | PM, BP |
| 97 | `--allow-dangerously-skip-permissions` | Permissions | Adds bypass mode to cycle without activating it | CLI flag | Composes with `--permission-mode plan` etc. | | PM |
| 98 | `defaultMode` setting | Permissions | Persistent default permission mode | `permissions.defaultMode` in settings.json | | | PM |
| 99 | `Shift+Tab` cycle | Permissions | Cycle through modes in CLI | In-session | Auto appears only after `--enable-auto-mode`; bypass appears only after explicit flags | Desktop/VS Code/web have UI equivalents | PM |
| 100 | Permission allow/ask/deny rules | Permissions | Pre-approve, force prompt, or block by tool name and argument pattern | `.claude/settings.json` `permissions.allow/ask/deny` | Any settings layer | Applies in every mode except bypassPermissions | PM, HW |
| 101 | `/permissions` | Permissions | View and edit current allow/deny rules | In-session | N/A | Shows Recently denied tab in auto mode | PM, DIR |
| 102 | `PreToolUse` hook (decision control) | Permissions | Programmatic allow/deny/escalate before every tool call | Hook config | Based on command content, path, time of day, external policy | Covers logic rules can't express | PM |
| 103 | `PermissionRequest` hook | Permissions | Intercept the permission dialog and answer automatically | Hook config | | | PM |
| 104 | Sandboxing | Permissions | OS-level filesystem and network isolation | `/sandbox` or `sandbox.enabled` setting | | Lets Claude work more freely within defined boundaries | BP |
| 105 | Auto mode decision order | Permissions | (1) Allow/deny rules → (2) read-only and WD edits auto-approved → (3) classifier | Automatic in auto mode | N/A | First match wins | PM |
| 106 | Auto mode stripped allow rules | Permissions | On entering auto, drops blanket shell like `Bash(*)`, `Bash(python*)`, `Bash(node*)`, package-manager run, `Agent` allow rules | Automatic | Narrow rules like `Bash(npm test)` survive | Restored on leaving auto mode | PM |
| 107 | Auto mode classifier input scope | Permissions | Sees user messages + tool calls + CLAUDE.md; not Claude's own text or tool results | Automatic | N/A | Injection protection: hostile content never reaches classifier | PM |
| 108 | Auto mode subagent handling | Permissions | Classifier evaluates delegated task at spawn; reviews full action history on return | Automatic | Subagent's own `permissionMode` frontmatter ignored in auto | Return check prepends security warning if concern found | PM |
| 109 | Auto mode default blocks | Permissions | curl\|bash, sensitive data exfiltration, prod deploys/migrations, mass cloud deletion, IAM/repo grants, shared infra, irreversible destruction, force push, direct push to main | Automatic | N/A | `claude auto-mode defaults` to view full lists | PM |
| 110 | Auto mode default allows | Permissions | Local file ops in WD, installing declared deps, .env read/send to matching API, read-only HTTP, push to starting or Claude-created branch | Automatic | N/A | | PM |
| 111 | `autoMode.environment` setting | Permissions | Add trusted repos, buckets, internal services | Managed settings | N/A | Admin configuration for org infrastructure | PM |
| 112 | Auto mode fallback thresholds | Permissions | 3 consecutive or 20 total classifier blocks in session pauses auto mode | Automatic | Not configurable | Non-interactive (-p) mode aborts instead | PM |
| 113 | `/feedback` | Permissions | Report classifier false positives/misses | In-session | N/A | | PM |
| 114 | Checkpoints | Safety | Pre-edit file snapshots; every edit reversible | Automatic | N/A | Local to session, separate from git; only covers file changes | HW, BP |
| 115 | `Esc` (interrupt) | Safety | Stop Claude mid-action, preserve context | In-session | N/A | You can redirect with new input | BP |
| 116 | `Esc+Esc` or `/rewind` | Safety | Open rewind menu; restore conversation, code, or both | In-session | N/A | Checkpoints persist across sessions | HW, BP |
| 117 | "Undo that" | Safety | Ask Claude to revert changes | Natural language | N/A | | BP |
| 118 | `/clear` | Context | Reset context window between unrelated tasks | In-session | N/A | Best practice between tasks | BP |
| 119 | Git worktrees (`--worktree` / `-w`) | Parallelism | Create isolated worktree with new branch and start Claude in it | `claude --worktree [name]` | Creates `.claude/worktrees/<name>`, branch `worktree-<name>`, based on `origin/HEAD` | Base branch not configurable via flag; use `WorktreeCreate` hook for custom logic | CWF |
| 120 | `WorktreeCreate` hook | Parallelism | Replace default git worktree logic for custom branching, non-git VCS | Hook config | N/A | Replaces default git behavior entirely | CWF |
| 121 | `WorktreeRemove` hook | Parallelism | Custom worktree cleanup | Hook config | N/A | For non-git VCS | CWF |
| 122 | `.worktreeinclude` | Parallelism | Copy gitignored files (like `.env`) into new worktrees | Project root file, gitignore syntax | N/A | Only applies when default git worktree logic used | CWF, DIR |
| 123 | `cleanupPeriodDays` | Parallelism | Auto-remove orphaned subagent worktrees past this age | Setting | N/A | Only touches subagent worktrees, never `--worktree` | CWF |
| 124 | Routines (cloud scheduled) | Scheduling | Run on Anthropic-managed infrastructure, even when computer off; can trigger on API calls or GitHub events | `/schedule` in CLI, web, or Desktop | `claude.ai/code/routines` | | OV, CWF |
| 125 | Desktop scheduled tasks | Scheduling | Run on your machine, direct access to local files | Desktop app | N/A | For tasks needing local tools or uncommitted changes | OV, CWF |
| 126 | `/loop` | Scheduling | Repeat a prompt within a CLI session for polling | In-session | N/A | Stops on new conversation; `--resume`/`--continue` restores unexpired | OV, CWF |
| 127 | GitHub Actions integration | CI/CD | Automate PR review and issue triage | `.github/workflows/...` | Per-workflow config | Subagents not yet integrated | OV, CWF |
| 128 | GitLab CI/CD integration | CI/CD | Similar automation for GitLab | GitLab pipelines | N/A | | OV |
| 129 | GitHub Code Review | CI/CD | Automatic code review on every PR | Repo install | N/A | | OV |
| 130 | Headless mode (`-p`) | Automation | Non-interactive single-prompt execution | `claude -p "prompt"` | Output formats available | Core to scripting and CI integration | OV, CWF, BP |
| 131 | `--output-format text` | Automation | Plain text output (default) | `-p` flag | N/A | Simple integrations | CWF |
| 132 | `--output-format json` | Automation | JSON array of messages with metadata (cost, duration) | `-p` flag | N/A | Full conversation log | CWF |
| 133 | `--output-format stream-json` | Automation | Real-time JSON object stream | `-p` flag | N/A | Concatenated output not valid JSON | CWF |
| 134 | `--verbose` | Automation | Debug verbose output in headless mode | CLI flag | N/A | Turn off in production | BP |
| 135 | `--allowedTools` | Automation | Restrict what Claude can do in batch runs | `claude -p ... --allowedTools "Edit,Bash(git commit *)"` | N/A | Important for unattended fan-out runs | BP |
| 136 | Unix pipes | Automation | `cat file \| claude -p "..."` and `claude -p "..." \| other_tool` | Shell | N/A | Composable in existing pipelines | OV, CWF, BP |
| 137 | Fan-out across files | Automation | Loop `claude -p` for each file in a list | Shell loop | N/A | Test on 2-3 files first, refine prompt, scale | BP |
| 138 | Writer/Reviewer pattern | Parallelism | Parallel sessions with separate contexts for code-write and code-review | Two sessions | N/A | Fresh context improves code review, not biased toward just-written code | BP |
| 139 | Agent teams | Parallelism | Automated coordination of parallel sessions with shared tasks, messaging, team lead | `agent-teams` feature | N/A | Higher-order orchestration | CWF, BP |
| 140 | Agent SDK | Extension | Build custom agents with full orchestration control | SDK | Tool access and permissions fully configurable | | OV |
| 141 | `@file` reference | Prompting | Include full file content in conversation | `@src/utils/auth.js` in prompt | Adds CLAUDE.md from file's directory and parents | | CWF, BP |
| 142 | `@directory` reference | Prompting | Include directory listing (not contents) | `@src/components` | N/A | Listing only, not file contents | CWF |
| 143 | Images via drag/drop | Prompting | Add images to conversation | Drag into Claude Code window | N/A | | CWF, BP |
| 144 | Images via clipboard paste | Prompting | Paste with `Ctrl+V` (not `Cmd+V`) in CLI | In-session | N/A | | CWF |
| 145 | Images via path reference | Prompting | Provide path like `/path/to/image.png` | In prompt | N/A | | CWF |
| 146 | Click to open image references | Prompting | `Cmd/Ctrl+Click` on `[Image #1]` to open in viewer | In-session | N/A | | CWF |
| 147 | Extended thinking (default on) | Reasoning | Model reasons step-by-step before responding | Automatic | Toggle via `/config`, `Option+T` / `Alt+T` | Adaptive reasoning on Opus 4.7, Opus 4.6, Sonnet 4.6 | CWF |
| 148 | `Ctrl+O` (verbose toggle) | Reasoning | Show internal reasoning as gray italic text | In-session | N/A | | CWF |
| 149 | `/effort` | Reasoning | Control thinking depth on supported models | In-session | Also adjustable via `/model` | | CWF |
| 150 | `CLAUDE_CODE_EFFORT_LEVEL` env var | Reasoning | Set effort level via environment | Env | Same as `/effort` | | CWF |
| 151 | `ultrathink` keyword | Reasoning | In-context instruction to reason more on that turn | In prompt | Does not change effort level itself | `think`, `think hard`, `think more` are NOT special | CWF |
| 152 | `MAX_THINKING_TOKENS` env var | Reasoning | Limit thinking budget on older models | Env | On adaptive models, only `0` (disable) applies unless `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` | Opus 4.7 always adaptive, no fixed budget | CWF |
| 153 | `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | Reasoning | Revert to fixed thinking budget on 4.6 models | Env | Opus 4.6 / Sonnet 4.6 only | Does nothing on Opus 4.7 | CWF |
| 154 | `alwaysThinkingEnabled` setting | Reasoning | Default thinking on/off across all projects | `~/.claude/settings.json` | Set via `/config` | | CWF |
| 155 | `showThinkingSummaries` setting | Reasoning | Show full thinking summaries (not collapsed stub) | settings.json | Default collapsed | You are charged for thinking tokens regardless | CWF |
| 156 | `/init` command | Diagnostic | Guided CLAUDE.md creation; optional multi-phase flow with `CLAUDE_CODE_NEW_INIT=1` | In-session | N/A | | HW, MEM |
| 157 | `/doctor` | Diagnostic | Installation and configuration diagnostics | In-session | N/A | | HW, DIR |
| 158 | `/skills` | Diagnostic | Available skills from project, user, plugin sources | In-session | N/A | | DIR |
| 159 | `/model` | Config | Switch models during session | In-session | N/A | | HW |
| 160 | `/config` | Config | Configuration UI including thinking toggle | In-session | N/A | | CWF |
| 161 | `/plan` prefix | Prompting | Single-turn plan mode for one prompt | `/plan <task>` | N/A | Alternative to session-wide mode switch | PM, CWF |
| 162 | `Ctrl+G` in plan mode | Prompting | Open plan file in default text editor | In-session plan mode | N/A | Edit plan directly before execution | CWF |
| 163 | Auto session naming on plan accept | Sessions | Session named from plan content when plan accepted | Automatic | Skipped if `--name` or `/rename` already used | | CWF |
| 164 | Plan mode exit options | Prompting | On plan approval: auto / acceptEdits / manual / keep planning; each with optional context clear | Plan acceptance menu | N/A | | PM |
| 165 | `/powerup` | Learning | Interactive lessons with animated demos | In-session | N/A | Built-in tutorial system | CWF |
| 166 | Documentation self-reference | Learning | Ask Claude questions about Claude Code itself | Natural language | N/A | Claude has access to latest Claude Code docs | CWF |
| 167 | Self-authored hooks | Automation | Ask Claude to write hook scripts | Natural language prompt | N/A | e.g., "Write a hook that runs eslint after every file edit" | BP |
| 168 | Self-authored skills | Automation | Claude can create skills, subagents, commands on request | Natural language; bypass mode explicitly permits writes to `.claude/skills`, `/agents`, `/commands` | N/A | | PM, BP |

---

## Notes on the table

**Granularity choice.** One row per invocation surface or config knob, not per feature family. This makes absence in Codex easy to mark as a gap when we do the comparison.

**What isn't here.** Several pages link out to deeper docs (hooks reference, tools reference, env vars reference, settings reference, agent SDK, plugins, sandboxing, costs, routines details, GitHub Actions config). Those expansions would roughly double the row count. Worth fetching those pages if the Codex comparison shows the summary rows aren't specific enough.

**Cross-cutting observations worth tracking separately from Codex:**

- Context management is treated as the central constraint, with at least nine distinct mechanisms (compaction, /clear, /btw, subagents, skill lazy loading, MCP tool deferral, path-scoped rules, partial-context compaction, /context introspection).
- The permission system has six modes and four layers (modes, allow/ask/deny rules, hooks, sandboxing), composable with managed-settings overrides.
- Extensibility is layered: skills, commands, rules, subagents, hooks, MCP, output styles, plugins, Agent SDK. Each has different load semantics (always loaded vs on-demand vs explicit invocation).
- Session model supports fork, resume-by-name, PR-linked resume, cross-worktree resume. Sessions are directory-scoped but resumable across worktrees of the same repo.
- Non-interactive mode (`-p`) is first-class and treated as the integration path for CI, pre-commit hooks, fan-out.

**Ready for Codex comparison.** To extend: add one column per Codex to this table, mark Present / Absent / Partial / Different with a short note. Keep the Feature and Source columns intact so the provenance is stable.
