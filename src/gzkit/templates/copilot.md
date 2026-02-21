# GitHub Copilot Instructions

Instructions for GitHub Copilot when working with {project_name}.

## Project Context

{project_purpose}

## Canonical Contract

`AGENTS.md` is the source of truth for governance behavior.

If these instructions drift from `AGENTS.md`, follow `AGENTS.md` and run `gz agent sync control-surfaces`.

## Tech Stack

{tech_stack}

## Conventions

{coding_conventions}

## Quality Requirements

Before suggesting code:

1. Follow existing patterns in the codebase
2. Include type annotations for all public functions
3. Write tests for new functionality
4. Follow the invariants defined in governance docs

## Governance

This project uses gzkit for governance. Key commands:

- `gz status` - Check what gates are pending
- `gz validate --documents` - Validate governance artifacts
- `gz check` - Run all quality checks

## OBPI Acceptance

When completing an OBPI brief:

1. Provide value narrative + one key proof example
2. Provide verification evidence (tests/commands/output)
3. Wait for explicit human acceptance before setting `Completed` for Heavy/Foundation parent ADR work

Reference: `AGENTS.md` section `OBPI Acceptance Protocol`.

## Skills

Use the canonical skill catalog and keep mirrors synced via `gz agent sync control-surfaces`:

- Canonical skills: `{skills_canon_path}`
- Claude skill mirror: `{skills_claude_path}`
- Codex skill mirror: `{skills_codex_path}`
- Copilot skill mirror: `{skills_copilot_path}`

### Available Skills

{skills_catalog}

## Build Commands

```bash
{build_commands}
```

## Key Files

- `AGENTS.md` - Universal agent contract
- `.gzkit/manifest.json` - Governance manifest
- `.gzkit/ledger.jsonl` - Event ledger

---

<!-- BEGIN agents.local.md -->
{local_content}
<!-- END agents.local.md -->
