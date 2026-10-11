# Permission Inventory — Pass D

> Chore: `control-surface-permission-consent-drift` (Lite lane, advisory)
> Run: **2026-10-10**, maintenance visit E. Both files read verbatim.

| Surface | allow | deny | ask |
|---|---|---|---|
| `.claude/settings.json` (committed; the `permissions` block is hand-kept and preserved by `sync_claude_settings`' merge) | 0 | 42 | 0 |
| `.claude/settings.local.json` (gitignored at `.gitignore:54`; present on this machine) | 25 | 0 | 0 |

August read 180 allow rules in the local file. That file was lost with the repository and rebuilt;
its own `_comment` says so:

> "Reconstructed 2026-08-29 from 203 session transcripts (24,466 Bash calls) after the original
> was lost with the repo. Read-only and project-CLI verbs only; mutating and outward-facing
> commands are deliberately absent so they still prompt."

## `.claude/settings.local.json` — allow (25)

```
Bash(uv run gz:*)
Bash(uv run ruff:*)
Bash(uv run -m:*)
Bash(git status:*)
Bash(git log:*)
Bash(git diff:*)
Bash(git show:*)
Bash(git rev-parse:*)
Bash(git rev-list:*)
Bash(git fetch:*)
Bash(grep:*)
Bash(rg:*)
Bash(ls:*)
Bash(cat:*)
Bash(head:*)
Bash(tail:*)
Bash(wc:*)
Bash(find:*)
Bash(jq:*)
Bash(gh issue list:*)
Bash(gh issue view:*)
Bash(gh run list:*)
Bash(gh run view:*)
WebSearch
Bash(shasum:*)
```

## `.claude/settings.json` — deny (42)

Hook-bypass, six rules:

```
Bash(git *--no-verify*)
Bash(git *--no-verify)
Bash(git *commit -n *)
Bash(git *commit -n)
Bash(git *hooksPath=*)
Bash(git *config *hooksPath *)
```

Secret-shaped files, 18 `Read(...)` rules and the same 18 as `Edit(...)`, new since August:

```
.env  .env.*  *.pem  *.key  *.p12  *.pfx  *.jks  *.keystore
id_rsa  id_dsa  id_ecdsa  id_ed25519  .netrc  .credentials.json
~/.ssh/id_*  ~/.aws/credentials  ~/.config/gcloud/**  ~/.claude/.credentials.json
```

## Hook matchers in `.claude/settings.json` (context for the unwitnessable ledger)

| Event | Matcher | Hooks |
|---|---|---|
| PreToolUse | `Bash` | verifier-pipe-gate, pipeline-completion-reminder, ghi-triage-chat-silence |
| PreToolUse | `Write\|Edit\|NotebookEdit` | session-staleness-check, pipeline-gate, obpi-completion-validator, instruction-router |
| PostToolUse | `Edit\|Write` | post-edit-ruff, ledger-writer |
| PreToolUse / PostToolUse | `ExitPlanMode` | plan-audit-gate / pipeline-router |
| SessionStart, PreCompact, Stop, UserPromptSubmit, SessionEnd | `*` | orientation, advisement, settings-local backup, stop-turn feedback, mx-awareness, exit bookmark |

No hook that guards a file write is matched on `Bash`.
