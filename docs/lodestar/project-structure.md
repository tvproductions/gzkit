# Project Structure

This document defines the **canonical directory layout** for gzkit-governed projects.

## Guiding Principle

**Opinionated architecture, configurable paths.**

gzkit enforces invariant semantic surfaces—concepts that every governed project must have. Where those concepts live on disk is config-driven (with strong defaults), but their existence is non-negotiable.

This is not "build-a-bear." Do it this way or move along.

## Canonical Layout

```
project/
├── design/              # Product design artifacts (visible)
│   ├── adr/             # Architecture Decision Records
│   │   ├── adr-0.0.x/   # Foundational ADRs
│   │   ├── adr-0.1.x/   # Feature ADRs
│   │   └── pool/        # ADR candidates (not yet promoted)
│   ├── prd/             # Product Requirements Documents
│   └── briefs/          # OBPI briefs (one brief per item)
│
├── .gzkit/              # gzkit infrastructure (hidden)
│   ├── config.json      # Project gzkit configuration
│   ├── ledger/          # Attestation and governance ledgers
│   └── cache/           # Ephemeral state (gitignored)
│
├── docs/                # Product documentation
│   ├── lodestar/        # Foundational canon (gzkit itself)
│   └── ...              # User/operator docs
│
├── src/                 # Source code
└── tests/               # Test suite
```

## Two Domains

### `design/` — Product-Facing (Visible)

Design artifacts drive the application. They are product content, not tooling.

| Directory | Contains |
|-----------|----------|
| `design/adr/` | Architecture Decision Records organized by SemVer series |
| `design/prd/` | Product Requirements Documents |
| `design/briefs/` | OBPI briefs mapping to ADR checklist items |

**Why visible?** Stakeholders—humans and agents—need to discover, navigate, and reference design decisions. These artifacts are part of the product's intellectual heritage.

### `.gzkit/` — Tool-Facing (Hidden)

gzkit's own state and configuration. Infrastructure, not content.

| Path | Purpose |
|------|---------|
| `.gzkit/config.json` | Project-specific gzkit settings |
| `.gzkit/ledger/` | Attestation records, governance proofs |
| `.gzkit/cache/` | Ephemeral state (safe to delete, gitignored) |

**Why hidden?** Follows dotfile convention for tooling (`.git/`, `.github/`, `.vscode/`). Developers focused on code don't need this in their tree. Agents and governance tooling know where to find it.

## Config-First, Not Config-Optional

Physical locations come from config with strong defaults:

```json
{
  "design_path": "design/",
  "adr_path": "design/adr/",
  "prd_path": "design/prd/",
  "briefs_path": "design/briefs/",
  "gzkit_path": ".gzkit/"
}
```

Code resolves semantic targets through config:

```python
design_path = config.get("design_path", "design/")
adr_path = config.get("adr_path", f"{design_path}adr/")
```

The concepts are invariant. The paths are configurable. The defaults are strong.

## Semantic Targets (Invariants)

Every gzkit-governed project **must** have:

| Concept | Default Location | Negotiable? |
|---------|------------------|-------------|
| Design artifacts directory | `design/` | Location: yes. Existence: no. |
| ADR directory | `design/adr/` | Location: yes. Existence: no. |
| ADR-0.0.0 (organizing doctrine) | `design/adr/adr-0.0.x/` | No. Required. |
| gzkit config | `.gzkit/config.json` | Location: yes. Existence: no. |

## Parallels

| Tool | Product content | Tool infrastructure |
|------|-----------------|---------------------|
| Git | `src/`, `docs/` | `.git/` |
| GitHub | Workflows, templates | `.github/` |
| VSCode | Project files | `.vscode/` |
| **gzkit** | `design/` | `.gzkit/` |
