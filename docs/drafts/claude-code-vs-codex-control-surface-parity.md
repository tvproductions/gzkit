# Claude Code vs. Codex: Control-Surface Parity

_Last updated: April 18, 2026_

## What this is

This is a **product-control-surface comparison**, not a model comparison.

I’m comparing every practical surface that shapes how the coding agent behaves:

- where you can use it (CLI, IDE, app, web, mobile, Slack, CI)
- what persistent repo guidance it reads
- how “rules” actually work
- how permissions, sandboxing, approvals, and hooks work
- how reusable workflows are packaged (skills, plugins, MCP)
- how multi-agent delegation works
- how review, worktrees, automations, and cloud execution work
- what is admin-enforceable versus advisory only

---

## Bottom line

Claude Code and Codex are **close at the primitive layer** and **different at the control-surface layer**.

- **Claude Code** is stronger as a **cross-surface, terminal-first, hookable, subagent-rich coding harness**.
- **Codex** is stronger as a **structured app/worktree/cloud/automation platform**.

The biggest planning mistake is to treat these as clones. They are not.

The biggest naming trap is this:

> **Claude `.claude/rules` and Codex `.rules` are not the same thing.**

- Claude `.claude/rules/*.md` = **instruction/context-loading rules**
- Codex `.rules` = **command-execution policy rules**

That distinction matters a lot for migration, governance, and parity planning.

---

## 1) Executive readout

### Where Claude Code is ahead

Claude Code is ahead when the job depends on:

- **cross-surface continuity**: terminal ↔ desktop ↔ web ↔ phone ↔ Slack ↔ CI
- **Remote Control**: continue a local session from another device while execution stays local
- **instruction layering** with `CLAUDE.md`, `CLAUDE.local.md`, and path-scoped `.claude/rules`
- **tool-native permission rules** over Bash, Read/Edit, WebFetch, MCP, and subagents
- **mature lifecycle hooks** with many interception points
- **automatic subagent delegation**
- **agent teams**
- **authenticated browser automation** through the Chrome extension
- **broader plugin packaging**: skills, agents, hooks, MCP, LSP, monitors, executables, settings

### Where Codex is ahead

Codex is ahead when the job depends on:

- **app-centric parallel work**
- **first-class worktree mode**
- **review pane + inline comments + stage/revert by file/hunk**
- **structured automation** with `codex exec`, JSONL, and schema outputs
- **app-server / custom-client integration**
- **explicit sandbox / approval / network controls**
- **artifact handling** in the app
- **native Windows sandboxing**
- **plugin/app integration surfaces**
- **Codex Security** as a separate scanning product

### Clean planning summary

If you want a **coding-agent shell with strong policy and orchestration**, Claude is ahead.

If you want a **desktop app + worktree + review + cloud + automation operating system**, Codex is ahead.

---

## 2) Parity at a glance

| Control surface | Claude Code | Codex | Planning call |
|---|---|---|---|
| CLI | Strong | Strong | Near parity; different emphasis |
| IDE | Strong | Strong | Near parity |
| App/Desktop | Good | Stronger | Codex is more app-centric |
| Web/Cloud | Strong | Strong | Similar goal, different execution model |
| Mobile/local continuity | Strong | Limited equivalent | Claude lead |
| Repo instructions | Strong | Strong | Similar purpose, different mechanics |
| Rules | Broader taxonomy | Different taxonomy | Not 1:1 |
| Permissions | Tool-native | Sandbox/approval-native | Different mental model |
| Sandboxing | Secondary but important | Central | Codex lead |
| Hooks | Broad and mature | Experimental and narrower | Claude lead |
| Skills | Strong | Strong | Very high parity |
| Plugins | Broader runtime packaging | Stronger app-integration packaging | Split lead |
| MCP | Strong | Strong | High parity |
| Subagents | More autonomous | More explicit | Claude lead |
| Agent teams | Yes | No direct equivalent | Claude lead |
| Worktrees | Indirect / less central | First-class | Codex lead |
| Review UX | Good | Stronger | Codex lead |
| CI / non-interactive | Strong | Stronger structure | Codex lead |
| Browser automation | Stronger | More limited | Claude lead |
| Computer use | Yes | Yes | Near parity |
| Windows sandboxing | Less central | Strong | Codex lead |
| Enterprise policy | Strong | Strong | High parity |

---

## 3) The critical taxonomy: guidance vs policy vs enforcement

This is the right way to think about control-surface parity.

### A. Behavioral guidance

This is the layer that answers:

> “How should the agent behave in this repo?”

**Claude Code**

- `CLAUDE.md`
- `CLAUDE.local.md`
- `.claude/rules/*.md`
- auto memory

**Codex**

- `AGENTS.md`
- `AGENTS.override.md`
- nested `AGENTS.md`
- optional local memories

These are **guidance surfaces**, not hard enforcement.

### B. Tool / command policy

This is the layer that answers:

> “What may the agent run, read, edit, fetch, or delegate?”

**Claude Code**

- `permissions.allow`
- `permissions.ask`
- `permissions.deny`
- rules over `Bash(...)`, `Read(...)`, `Edit(...)`, `WebFetch(...)`, `Agent(...)`, MCP tools

**Codex**

- `sandbox_mode`
- `approval_policy`
- `.rules` with `prefix_rule(...)`
- network / filesystem constraints in config

### C. Deterministic enforcement

This is the layer that answers:

> “How do I actually block or validate behavior even if prompting isn’t enough?”

**Claude Code**

- hooks
- managed settings
- sandbox

**Codex**

- sandbox
- approval policy
- `.rules`
- hooks
- managed requirements/defaults

---

## 4) Rules: the most important parity correction

## 4.1 Claude has **three** rule surfaces

### 1. Instruction rules

Claude supports `.claude/rules/*.md` to break repo guidance into modular rule files.

These can be:

- always loaded
- user-level
- shared across projects via symlinks
- **path-scoped** using YAML frontmatter like `paths:`

Example:

```md
---
paths:
  - "src/api/**/*.ts"
  - "tests/api/**/*.test.ts"
---

# API Rules

- Validate all inputs.
- Use the standard error shape.
- Update API tests when behavior changes.
```

This is a real control surface because it lets teams keep repo guidance modular and conditionally loaded.

### 2. Permission rules

Claude also has tool-native permission rules.

Example:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git diff *)",
      "Edit(/src/**)"
    ],
    "ask": [
      "Bash(git push *)",
      "WebFetch"
    ],
    "deny": [
      "Read(./.env)",
      "Bash(curl *)",
      "Agent(Explore)"
    ]
  }
}
```

This is much broader than shell-only control because it reaches:

- shell commands
- built-in file tools
- web fetch
- subagents
- MCP tools

### 3. Hook-enforced rules

Claude hooks can enforce deterministic policy at many lifecycle points.

This is where Claude becomes much stronger than “just instructions” or “just permission prompts.”

---

## 4.2 Codex “rules” mean something different

Codex `.rules` are **not** repo-guidance files.

They are **command-execution policy** files used to control which commands can run outside the sandbox.

Example:

```python
prefix_rule(
    pattern = ["git", "push"],
    decision = "prompt",
    justification = "Pushing affects the remote repository."
)

prefix_rule(
    pattern = ["rm", "-rf"],
    decision = "forbidden",
    justification = "Do not allow recursive destructive deletion."
)
```

Codex applies the most restrictive matching decision:

- `forbidden`
- `prompt`
- `allow`

So the right mapping is:

- **Claude `.claude/rules/*.md`** ↔ **Codex `AGENTS.md` / nested `AGENTS.md`**
- **Claude Bash permission rules** ↔ **Codex `.rules`**
- **Claude hooks** ↔ **Codex hooks + sandbox + rules**

### Practical parity call on rules

| Rule type | Claude | Codex | Winner |
|---|---|---|---|
| Modular repo guidance | `.claude/rules/*.md` | nested `AGENTS.md` | Claude |
| Path-glob-scoped guidance | yes | not the same | Claude |
| Command prefix policy | Bash permission rules | `.rules` | slight Codex lead |
| Tool-level file/web/subagent rules | yes | not the same mechanism | Claude |
| OS-level enforcement | sandbox + hooks | sandbox + approvals + rules | slight Codex lead |
| Lifecycle rule enforcement | hooks | hooks, narrower | Claude |

---

## 5) Repo instructions and memory

## 5.1 Claude Code

Claude’s guidance stack is richer and more modular.

### Main instruction surfaces

- `CLAUDE.md`
- `.claude/CLAUDE.md`
- `CLAUDE.local.md`
- `.claude/rules/*.md`
- auto memory

### Key strengths

- multiple scopes: project, local, user, org
- path-specific instruction loading via `.claude/rules`
- `CLAUDE.local.md` for personal project-specific rules that should not be committed
- auto memory as a lightweight carry-forward mechanism

### Important limitation

These are still **context**, not hard enforcement.

## 5.2 Codex

Codex is simpler and cleaner, but less granular here.

### Main instruction surfaces

- `AGENTS.md`
- `AGENTS.override.md`
- nested `AGENTS.md`
- optional memories

### Key strengths

- good directory-local guidance model
- clean global vs repo vs subdirectory guidance chain
- strong best-practice framing around keeping `AGENTS.md` short and practical
- memories are clearly separated from repo guidance

### Important limitation

Codex does not expose a direct equivalent to Claude’s **path-frontmatter rule files**.

### Migration guidance

| Claude | Codex | Note |
|---|---|---|
| `CLAUDE.md` | `AGENTS.md` | straightforward mapping |
| `CLAUDE.local.md` | local untracked guidance / user defaults | no exact equivalent |
| `.claude/rules/*.md` | nested `AGENTS.md` | closest approximation |
| path-scoped `.claude/rules` | nearest directory `AGENTS.md` | loses glob precision |
| auto memory | Codex memories | Codex memories are opt-in |

---

## 6) Permissions, approvals, and sandboxing

## 6.1 Claude Code mental model

Claude is **tool-policy first**.

The main question is:

> “Can Claude use this tool without asking me?”

Claude gives you:

- permission modes (`default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`)
- allow/ask/deny rules
- tool-pattern matching
- admin controls to disable risky modes

This is user-friendly and expressive, especially for repo-local workflows.

## 6.2 Codex mental model

Codex is **sandbox first**.

The main question is:

> “What is technically possible inside the boundary, and when should Codex ask to cross it?”

Codex gives you:

- `sandbox_mode = read-only | workspace-write | danger-full-access`
- `approval_policy = untrusted | on-request | never`
- `.rules` for command-prefix policy
- more explicit filesystem/network/runtime policy modeling

### Important non-equivalence

`--full-auto` in Codex is **not** the same thing as “full access.”

- `--full-auto` = `workspace-write` + `on-request`
- full access = `danger-full-access` + `never`

That matters if you are mapping from Claude `auto` or `bypassPermissions`.

### Permission parity summary

| Need | Claude | Codex |
|---|---|---|
| analyze only | `plan` | `read-only` |
| edit workspace with some prompts | `default` / `acceptEdits` | `workspace-write` + `on-request` |
| low-friction auto work | `auto` or allow rules | `--full-auto` |
| full unattended execution | `bypassPermissions` | `danger-full-access` + `never` |
| allow/prompt/deny shell commands | yes | yes |
| allow/prompt/deny built-in file tools | yes | less direct |
| allow/prompt/deny subagents | yes | less direct |
| explicit OS boundary | partial / secondary | central |

### Hard planning note

Claude permission rules over `Read(...)` and `Edit(...)` do **not** automatically sandbox Bash. If you deny `Read(./.env)`, that blocks Claude’s file tool, not necessarily `cat .env` inside Bash. For process-level enforcement, Claude still needs sandboxing.

That is one reason Codex’s sandbox model is operationally stronger for hard runtime boundaries.

---

## 7) Hooks and lifecycle control

## 7.1 Claude Code

Hooks are one of Claude’s clearest advantages.

Claude hooks can be:

- shell commands
- HTTP endpoints
- LLM prompt hooks

Claude exposes many lifecycle points, including:

- `InstructionsLoaded`
- `UserPromptSubmit`
- `PreToolUse`
- `PermissionRequest`
- `PostToolUse`
- `Stop`
- `SubagentStop`
- `TaskCreated`
- `TaskCompleted`
- `TeammateIdle`
- `ConfigChange`
- `WorktreeCreate`
- more

That makes Claude’s hook surface useful for:

- validation
- audit/logging
- policy enforcement
- prompt filtering
- tool-call gating
- permission-dialog automation
- agent-team orchestration hooks

## 7.2 Codex

Codex hooks are useful, but clearly less mature.

Current characteristics:

- experimental
- feature-flagged
- disabled on Windows
- turn-scoped hooks include `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`
- current `PreToolUse` / `PostToolUse` emission is effectively Bash-only

That means Codex hooks are best thought of as:

- a useful extensibility layer
- not yet a broad lifecycle-governance system on par with Claude

### Hook parity summary

| Hook dimension | Claude | Codex |
|---|---|---|
| maturity | high | lower / experimental |
| breadth | broad | narrower |
| shell hooks | yes | yes |
| HTTP hooks | yes | not documented the same way |
| LLM hooks | yes | not documented the same way |
| permission-dialog interception | yes | no equivalent |
| instruction-load hook | yes | no equivalent |
| Windows support | yes | disabled for now |

---

## 8) Skills, plugins, and MCP

## 8.1 Skills

This is one of the highest-parity areas.

### Claude Code

- `SKILL.md`
- project / user / plugin / enterprise skill locations
- direct `/skill-name` invocation
- automatic invocation when relevant
- bundled skills like `/debug`, `/simplify`, `/loop`
- custom commands folded into skills

### Codex

- `SKILL.md`
- progressive disclosure
- `$skill-name` / `/skills`
- automatic invocation when relevant
- built-in creator workflow (`$skill-creator`)
- optional scripts, references, and assets

### Skill parity call

Very high parity. A Claude skill usually ports to Codex with modest adjustment.

## 8.2 Plugins

### Claude plugins

Claude plugins can package:

- skills
- agents
- hooks
- MCP servers
- LSP servers
- monitors
- executables
- default settings

This is closer to a **runtime extension package**.

### Codex plugins

Codex plugins package:

- skills
- app integrations
- MCP servers

This is closer to a **workflow/app-integration package**.

### Plugin parity call

- Claude is broader for runtime packaging.
- Codex is stronger for app-facing integrations.

## 8.3 MCP

Both have strong MCP support.

### Claude advantages

- tightly integrated with its cross-surface model
- plugin-packaged MCP
- org/admin control surfaces

### Codex advantages

- very explicit TOML config surface
- detailed server/env/header/timeout/tool controls

### MCP parity call

High parity. This is not a major differentiator unless your team cares a lot about config style or plugin packaging model.

---

## 9) Subagents and multi-agent control

## 9.1 Claude Code

Claude’s subagent story is deeper.

Claude supports:

- built-in and custom subagents
- automatic delegation
- explicit invocation
- @-mention patterns
- session-wide agent selection
- rich per-agent configuration
- agent teams as a separate orchestration layer

This matters because Claude is comfortable acting as an orchestrator.

## 9.2 Codex

Codex supports specialized subagent workflows in parallel, but they are more explicit.

Codex only spawns subagents when the user explicitly asks it to.

This is a more conservative, easier-to-reason-about model, but it is less autonomous.

### Subagent parity summary

| Dimension | Claude | Codex |
|---|---|---|
| built-in/custom agents | yes | yes |
| automatic delegation | yes | no |
| explicit parallel agents | yes | yes |
| per-agent control richness | stronger | good but narrower |
| agent teams | yes | no direct equivalent |
| predictability | lower by design | higher by design |

### Planning call

If you want **autonomous decomposition**, Claude is ahead.

If you want **explicit parallel task spawning with clearer operator intent**, Codex is solid.

---

## 10) App/worktrees/review/Git

## 10.1 Codex is meaningfully ahead here

Codex turns worktrees and review into first-class product surfaces.

### Worktrees

Codex thread modes include:

- Local
- Worktree
- Cloud

Worktree mode is not just “Git worktrees exist.” It is an actual app workflow:

- create a worktree for a thread
- keep work isolated from your main checkout
- hand the thread off between Worktree and Local
- preserve thread ↔ worktree association over time
- use worktrees for background automation

### Review pane

Codex’s review pane is unusually strong as a control surface:

- inspect diff
- leave inline comments
- stage / unstage / revert
- do that at entire diff, file, or hunk level
- keep the full PR-fix loop in one place

That is real product surface, not just “can review code.”

## 10.2 Claude is good here, but less productized

Claude can:

- stage changes
- write commit messages
- create branches and PRs
- run code review in GitHub
- operate through CI surfaces
- use desktop for visual diff review

But in the docs reviewed, Claude does not expose the same **app-native review loop** as Codex.

### App/review parity call

| Surface | Claude | Codex | Winner |
|---|---|---|---|
| Git actions | strong | strong | tie |
| visual diff review | good | stronger | Codex |
| inline review comments in app | limited equivalent | strong | Codex |
| hunk-level accept/revert in app | less central | strong | Codex |
| GitHub PR review | strong | strong | tie |
| GitLab CI/CD | strong | weaker / not equivalent in docs reviewed | Claude |
| worktree-first parallel tasks | less central | strong | Codex |

---

## 11) Automation and non-interactive execution

## 11.1 Claude Code

Claude’s automation style is more conversational and shell-native.

Main surfaces:

- `claude -p`
- CLI piping
- GitHub Actions
- GitLab CI/CD
- routines
- desktop scheduled tasks
- `/loop`
- Agent SDK

This is especially good when you want:

- terminal composition
- recurring remote tasks
- local scheduled tasks
- agent flows that stay close to normal Claude usage

## 11.2 Codex

Codex’s automation style is more infrastructure-like.

Main surfaces:

- `codex exec`
- JSONL event stream
- structured final output with schema
- app automations
- thread automations
- app-server JSON-RPC
- GitHub Action
- SDK

This is especially good when you want:

- robust CI integration
- machine-readable output
- background work in worktrees
- custom clients
- task orchestration in app/cloud systems

### Automation parity summary

| Need | Better fit |
|---|---|
| quick shell one-shot | tie |
| CI with event stream | Codex |
| schema-constrained output | Codex |
| scheduled local task | Codex or Claude |
| scheduled remote/cloud task | Codex or Claude |
| GitLab CI/CD | Claude |
| custom rich client | Codex |
| lifecycle-enforced automation | Claude |

---

## 12) Browser and computer use

## 12.1 Claude Code

Claude’s Chrome integration is a major differentiator.

It supports:

- browser automation from CLI / VS Code
- visible Chrome/Edge tab control
- shared browser login state
- authenticated app testing
- local web app debugging
- console log debugging

That is stronger than a generic “browser preview.”

Claude also has computer use for GUI tasks.

## 12.2 Codex

Codex has:

- in-app browser for local/public/unauthenticated pages
- browser comments for UI feedback
- computer use in the app

The in-app browser is useful, but the docs explicitly limit it:

- no authentication flows
- no signed-in browser profile behavior
- no cookies/extensions/tabs in the usual browser sense

### Browser parity call

| Capability | Claude | Codex |
|---|---|---|
| authenticated web app testing | strong | weak |
| local/public preview | yes | yes |
| visual browser feedback in app | weaker | stronger |
| GUI operation | yes | yes |

Claude wins on real browser automation. Codex wins on app-contained preview/comment workflow.

---

## 13) Governance and admin control

Both products have serious enterprise policy surfaces.

### Claude strengths

- managed settings precedence
- per-surface shared policy model
- managed-only hook policy options
- mature permission-rule governance
- good fit if your policy model is “who can use what tool, when?”

### Codex strengths

- managed requirements/defaults
- sandbox/approval policy enforcement
- stronger runtime-policy posture
- explicit config around network, app approvals, and providers
- Codex Security as a separate repository-scanning product
- native Windows sandbox administration

### Governance planning call

If your internal security team thinks in terms of:

- **tool allow/deny + lifecycle interception**, Claude will feel natural.
- **runtime boundary + approvals + managed requirements**, Codex will feel natural.

---

## 14) Migration map

## 14.1 Artifact mapping

| Claude | Codex | Difficulty | Note |
|---|---|---:|---|
| `CLAUDE.md` | `AGENTS.md` | low | best direct mapping |
| `CLAUDE.local.md` | local defaults / untracked guidance | medium | no exact equivalent |
| `.claude/rules/*.md` | nested `AGENTS.md` | medium | closest fit |
| path-scoped rule files | directory-local `AGENTS.md` | medium/high | loses glob precision |
| auto memory | Codex memories | medium | Codex is opt-in |
| permission rules | sandbox + approvals + `.rules` | high | different semantics |
| Claude Bash rules | Codex `.rules` | medium | closest command-policy mapping |
| Claude file/web/subagent rules | sandbox/config/custom policy | high | no exact `.rules` mapping |
| Claude hooks | Codex hooks + sandbox + wrapper logic | high | Claude is broader |
| Claude skills | Codex skills | low | easy migration |
| Claude plugins | Codex plugins | medium/high | package model differs |
| Claude MCP | Codex MCP | low/medium | config differs |
| Claude subagents | Codex subagents | medium/high | autonomy differs |
| agent teams | no direct equivalent | high | major gap |
| `claude -p` | `codex exec` | low/medium | Codex more structured |
| routines / scheduled tasks | automations | medium | similar intent, different packaging |
| Remote Control | no direct equivalent | high | real gap |

## 14.2 The safest migration strategy

Do **not** migrate by filename or feature name.

Migrate by intent:

1. **guidance**
2. **command policy**
3. **runtime boundary**
4. **deterministic enforcement**
5. **workflow packaging**
6. **parallelism model**
7. **review model**
8. **automation model**

That avoids the classic trap of assuming:

- `CLAUDE.md` = `AGENTS.md` in every way
- `.claude/rules` = Codex `.rules`
- `auto` = `--full-auto`
- hooks = hooks
- subagents = subagents

Those are all misleading simplifications.

---

## 15) Where parity is genuinely high

These are the areas where parity is strongest:

- core coding-agent loop
- CLI usage for interactive coding work
- IDE integration
- repo instruction files at a broad level
- skills
- MCP
- GitHub review flows
- cloud execution in some form
- computer use in some form
- enterprise/admin seriousness

If your requirements live mostly here, you can build a two-vendor strategy.

---

## 16) Where parity is weak or misleading

These are the areas where “feature parity” is easy to overstate:

- rules
- permission semantics
- sandbox semantics
- hooks
- subagent autonomy
- agent teams
- worktrees as a product surface
- app review UX
- browser automation
- machine-readable automation
- Windows sandboxing

If your roadmap depends on any of these, you need a product-specific plan.

---

## 17) Decision guidance

### Choose Claude Code as the lead platform if you need:

- terminal-first control
- rich lifecycle hooks
- path-scoped repo guidance
- tool-native permission rules
- automatic delegation
- agent teams
- mobile/browser continuation of local work
- authenticated browser automation
- GitLab CI/CD parity
- plugin packages that include runtime components like hooks and agents

### Choose Codex as the lead platform if you need:

- worktrees as a first-class operating model
- an app-centric review loop
- inline diff comments as agent feedback
- stronger structured CI/non-interactive automation
- JSONL and output-schema workflows
- app-server / custom client integration
- native Windows sandboxing
- app automations
- artifact workflow in the app
- Codex Security

### If you need both

Define your internal abstraction layer around these control objectives:

- repo guidance
- command policy
- runtime boundary
- deterministic enforcement
- reusable workflows
- external tools/connectors
- multi-agent decomposition
- review workflow
- automation workflow
- governance

Then implement each objective separately for Claude and Codex.

---

## 18) Final scorecard

| Area | Parity | Lead |
|---|---:|---|
| Core coding loop | 9/10 | Tie |
| CLI | 8/10 | Tie |
| IDE | 8/10 | Tie |
| App/Desktop | 7/10 | Codex |
| Web/Cloud | 8/10 | Tie |
| Remote/mobile continuation | 4/10 | Claude |
| Repo instructions | 8/10 | Tie |
| Instruction rules | 5/10 | Claude |
| Command-policy rules | 8/10 | Slight Codex edge |
| Tool-native permission rules | 6/10 | Claude |
| Sandboxing | 8/10 | Codex |
| Hooks | 4/10 | Claude |
| Skills | 9/10 | Tie |
| Plugins | 7/10 | Split lead |
| MCP | 9/10 | Tie |
| Subagents | 6/10 | Claude |
| Agent teams | 2/10 | Claude |
| Worktrees | 5/10 | Codex |
| Review UX | 7/10 | Codex |
| Non-interactive automation | 7/10 | Codex |
| Browser automation | 6/10 | Claude |
| Computer use | 7/10 | Tie |
| Enterprise governance | 8/10 | Tie |
| Windows sandboxing | 5/10 | Codex |
| Security scanning product | 4/10 | Codex |

---

## 19) Final conclusion

Claude Code and Codex are **not** interchangeable control-surface products.

- Claude Code is the stronger **agent harness**.
- Codex is the stronger **agent platform shell**.

Claude is better when you need:

- more orchestration
- more lifecycle control
- more instruction layering
- more autonomous delegation
- more cross-surface continuity

Codex is better when you need:

- more app structure
- more worktree discipline
- more review ergonomics
- more automation plumbing
- more sandbox clarity

The planning-safe conclusion is this:

> Build parity around **outcomes**, not feature names.

Especially for:

- rules
- permissions
- hooks
- subagents
- worktrees
- automation

That is where the apparent surface similarity hides the deepest product differences.

---

## Source links

### Claude Code

- Overview: https://code.claude.com/docs/en/overview
- Memory / instructions / `.claude/rules`: https://code.claude.com/docs/en/memory
- Permissions: https://code.claude.com/docs/en/permissions
- Hooks: https://code.claude.com/docs/en/hooks
- Skills: https://code.claude.com/docs/en/skills
- Subagents: https://code.claude.com/docs/en/sub-agents
- Agent teams: https://code.claude.com/docs/en/agent-teams
- Remote Control: https://code.claude.com/docs/en/remote-control
- Chrome: https://code.claude.com/docs/en/chrome
- Best practices: https://code.claude.com/docs/en/best-practices

### Codex

- Codex overview: https://developers.openai.com/codex
- App features: https://developers.openai.com/codex/app/features
- Worktrees: https://developers.openai.com/codex/app/worktrees
- Review: https://developers.openai.com/codex/app/review
- Automations: https://developers.openai.com/codex/app/automations
- Rules: https://developers.openai.com/codex/rules
- Hooks: https://developers.openai.com/codex/hooks
- Skills: https://developers.openai.com/codex/skills
- Best practices: https://developers.openai.com/codex/learn/best-practices
- Sandboxing: https://developers.openai.com/codex/concepts/sandboxing
- Subagents: https://developers.openai.com/codex/subagents
- Plugins: https://developers.openai.com/codex/plugins
- MCP: https://developers.openai.com/codex/mcp
- Non-interactive mode: https://developers.openai.com/codex/noninteractive
- App Server: https://developers.openai.com/codex/app-server
- Windows: https://developers.openai.com/codex/windows
