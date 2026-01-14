# gzkit

**GovZero Kit: A Development Covenant for Human-AI Collaboration**

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
| 2 | **TDD** | Verify correctness through automated tests |
| 3 | **Docs** | Ensure documentation describes actual behavior |
| 4 | **BDD** | Verify external contracts through acceptance tests |
| 5 | **Human** | Human observes artifacts and attests completion |

**Lite lane** (internal changes): Gates 1, 2

**Heavy lane** (external contracts): Gates 1, 2, 3, 4, 5

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
gz plan new "Feature description"

# Check gate status
gz status

# Run verification
gz verify
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

- [Charter](docs/charter.md) — The covenant itself
- [Lineage](docs/lineage.md) — Heritage from spec-kit and GovZero
- [Concepts](docs/concepts/) — The three concerns explained
- [Genesis](docs/genesis.md) — Origin story and founding conversation
- [Sources](docs/sources/) — Original AirlineOps documents

## Philosophy

> Governance is verification, not celebration.

gzkit treats governance as executable documentation. All state lives in Markdown, validated by a Python CLI. The framework is human-centric, auditable, and version-controlled.

Prompts are code. Constraints are first-class. Human attestation is the final gate.

## License

MIT
