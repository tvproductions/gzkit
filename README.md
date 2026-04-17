# gzkit

**GovZero Kit: A Development Covenant for Human-AI Collaboration**

[![Version](https://img.shields.io/badge/version-0.25.9-blue.svg)](RELEASE_NOTES.md)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-3776ab.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Docs CI](https://img.shields.io/github/actions/workflow/status/tvproductions/gzkit/docs.yml?branch=main&logo=github&label=Docs%20CI)](https://github.com/tvproductions/gzkit/actions/workflows/docs.yml)
[![Docs](https://img.shields.io/badge/docs-MkDocs-blue.svg?logo=readthedocs)](https://gzkit.org)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg?logo=ruff)](https://github.com/astral-sh/ruff)
[![Package Manager: uv](https://img.shields.io/badge/package%20manager-uv-de5fe9.svg?logo=astral)](https://github.com/astral-sh/uv)

[Documentation](https://gzkit.org)
[Release Notes](RELEASE_NOTES.md)
[Roadmap](docs/design/roadmap/ROADMAP-GZKIT.md)

gzkit is cognitive infrastructure for extended human-AI collaboration—a protocol that preserves human intent across agent context boundaries, gives agents constraints to reason against, creates verification loops both parties trust, and reserves final judgment for humans.

## Why gzkit?

Modern AI-assisted development faces a structural problem: agents are powerful but context-bound. They drift without constraints, forget across sessions, and can't distinguish between "should do" and "could do." Humans provide intent and judgment but can't scale execution.

gzkit bridges this gap by formalizing the collaboration:

| Role | Human | Agent |
|------|-------|-------|
| **Intent** | Originates | Interprets, clarifies |
| **Constraints** | Defines, enforces | Operates within, flags violations |
| **Exploration** | Guides | Executes, surfaces options |
| **Judgment** | Final authority | Proposes, explains tradeoffs |
| **Memory** | Long-term, cross-project | Session-bound, needs scaffolding |
| **Verification** | Attests | Generates evidence |

## Three Concerns

gzkit spans three distinct but interrelated concerns:

| Concern | Purpose | Primary Audience |
|---------|---------|------------------|
| **Specification** | Invariants, constraints, acceptance criteria | Agent (grounding) |
| **Methodology** | Phases, workflows, checkpoints | Process (structure) |
| **Governance** | Authority, attestation, audit | Human (oversight) |

**Specification** is agent-native: explicit constraints, declarative intent, immutable canon.

**Methodology** is process-native: phases, gates, verification loops.

**Governance** is human-native: attestation rituals, authority boundaries, audit ceremonies.

All three are necessary. Specification without governance drifts. Governance without methodology is theater. Methodology without specification is arbitrary.

## The Covenant

gzkit implements a **development covenant**—a binding agreement between human and agent:

1. **Human defines intent** through canon, ADRs, and acceptance criteria
2. **Agent operates within constraints** and flags potential violations
3. **Verification is mutual** through tests, checks, and evidence
4. **Human attests completion** after observing artifacts
5. **Artifacts survive sessions** preserving intent across context boundaries

This is not "AI governance" in the compliance sense. It's a protocol for productive partnership.

## Lineage

gzkit evolved from:

- **[GitHub spec-kit](https://github.com/github/spec-kit)** — the `constitute → specify → plan → implement → analyze` phase model
- **GovZero** — governance framework developed in AirlineOps through ~100 work items of iterative learning
- **Claude Code conventions** — CLAUDE.md patterns for agent-native constraint specification

See [docs/lineage.md](docs/lineage.md) for full heritage.

## Five Gates

Work flows through five gates, adapted by lane (Lite or Heavy):

| Gate | Name | Purpose |
|------|------|---------|
| 1 | **ADR** | Record intent and tradeoffs before implementation |
| 2 | **TDD** | Red-Green-Refactor: tests derived from spec, not implementation |
| 3 | **Docs** | Ensure documentation describes actual behavior |
| 4 | **BDD** | Verify external contracts through acceptance tests |
| 5 | **Human** | Human observes artifacts and attests completion |

**Lite lane** (internal changes): Gates 1, 2

**Heavy lane** (external contracts): Gates 1, 2, 3, 4, 5

## Workflow Lifecycle

```
  DEFINE        PLAN          BUILD         VERIFY        ATTEST        RELEASE
 ┌──────┐    ┌──────┐    ┌──────────┐    ┌──────┐    ┌──────┐    ┌──────────┐
 │Design│───▶│  ADR │───▶│ Pipeline │───▶│Gates │───▶│Human │───▶│ Closeout │
 │ PRD  │    │ OBPI │    │ TDD Impl │    │Check │    │Attest│    │ Release  │
 └──────┘    └──────┘    └──────────┘    └──────┘    └──────┘    └──────────┘
  gz-design   gz-adr-      gz-obpi-       gz-check    gz-adr-     gz-patch-
  gz-prd      create       pipeline       gz-gates    closeout-   release
              gz-obpi-     gz-obpi-       gz-validate ceremony
              specify      simplify
```

## Skill Catalog

| Category | Skills |
|----------|--------|
| **ADR Lifecycle** | `gz-adr-create`, `gz-adr-evaluate`, `gz-adr-promote`, `gz-adr-status`, `gz-design`, `gz-plan` |
| **ADR Operations** | `gz-adr-autolink`, `gz-adr-emit-receipt`, `gz-adr-map`, `gz-adr-recon`, `gz-adr-sync` |
| **ADR Audit & Closeout** | `gz-adr-audit`, `gz-adr-closeout-ceremony`, `gz-patch-release` |
| **OBPI Pipeline** | `gz-obpi-lock`, `gz-obpi-pipeline`, `gz-obpi-reconcile`, `gz-obpi-simplify`, `gz-obpi-specify`, `gz-plan-audit` |
| **Governance Infrastructure** | `gz-constitute`, `gz-gates`, `gz-implement`, `gz-init`, `gz-prd`, `gz-state`, `gz-status`, `gz-validate` |
| **Agent & Repository** | `git-sync`, `gz-agent-sync`, `gz-check-config-paths`, `gz-migrate-semver`, `gz-session-handoff`, `gz-tidy` |
| **Code Quality** | `gz-check`, `gz-chore-runner`, `gz-cli-audit` |
| **Routing** | `gz-skill-router` |

For details on any skill, read its `SKILL.md` in `.gzkit/skills/<skill-name>/`.

## Installation

```bash
# Using uv (recommended)
uv add gzkit

# Or pip
pip install gzkit
```

## Quick Start

```bash
# Initialize gzkit in a project
gz init

# Create a new ADR
gz plan create feature --title "Feature description"

# Check gate status
gz status

# Run verification
gz check
```

## Configuration

gzkit uses `.gzkit.json` for project configuration:

```json
{
  "mode": "lite",
  "paths": {
    "canon": "docs/canon",
    "adrs": "docs/adr",
    "specs": "docs/specs"
  }
}
```

## Documentation

- [Charter](docs/user/reference/charter.md) — The covenant itself
- [Lineage](docs/user/reference/lineage.md) — Heritage from spec-kit and GovZero
- [Concepts](docs/user/concepts/) — The three concerns explained
- [Genesis](docs/user/reference/genesis.md) — Origin story and founding conversation

## Philosophy

> Governance is verification, not celebration.

gzkit treats governance as executable documentation. All state lives in Markdown, validated by a Python CLI. The framework is human-centric, auditable, and version-controlled.

Prompts are code. Constraints are first-class. Human attestation is the final gate.

## License

MIT
