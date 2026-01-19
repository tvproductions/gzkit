# GitHub Copilot Instructions

Instructions for GitHub Copilot when working with {project_name}.

## Project Context

{project_purpose}

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
- `gz validate` - Validate governance artifacts
- `gz check` - Run all quality checks

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
