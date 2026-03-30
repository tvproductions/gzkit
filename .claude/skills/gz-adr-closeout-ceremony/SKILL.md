---
name: gz-adr-closeout-ceremony
description: Execute the ADR closeout ceremony protocol for human attestation. GovZero v6 skill.
category: adr-audit
compatibility: GovZero v6 framework; provides runbook walkthrough for human ADR attestation
metadata:
  skill-version: "8.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/audit-protocol.md"
  govzero-gates-covered: "Gate 5 (Human Attestation)"
  govzero_layer: "Layer 2 - Ledger Consumption"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-30
---

# gz-adr-closeout-ceremony

Execute the ADR closeout ceremony via CLI-driven step sequencing.

**Authority:** `docs/governance/GovZero/audit-protocol.md`

---

## Architecture

The CLI is the step driver. Each `--next` call returns exactly one step's content.
The agent cannot skip or reorder steps because it never sees future steps.

State is persisted in `.gzkit/ceremonies/ADR-X.Y.Z.ceremony.json`.

---

## Invocation

The skill receives an ADR semver as its argument (e.g. `0.0.8`). Normalize to
`ADR-X.Y.Z` format and begin immediately. Do not ask clarifying questions.

---

## Agent Loop

The agent keeps advancing through ceremony steps, running commands as instructed,
and only stops at **attestation** (the one real human gate).

```
gz closeout ADR-X.Y.Z --ceremony           # Initialize, get step 2
gz closeout ADR-X.Y.Z --ceremony --next     # Advance to next step
gz closeout ADR-X.Y.Z --ceremony --attest "Completed"  # Record attestation
```

### Flow

1. Run `uv run gz closeout ADR-X.Y.Z --ceremony`.
2. Run evidence commands (tests, lint, typecheck) listed in the summary.
3. Keep advancing with `--next` through mechanical steps (docs checklist, etc.).
4. **Walkthrough step:** When the CLI lists walkthrough commands, ask the human:
   "Want me to run these, or will you run them yourself?" Then do what they say.
5. Advance to attestation. **Stop. Wait for human decision.**
   Then run `--attest "<their decision>"`.
6. After attestation, continue advancing — run closeout, GH issues, etc. as
   instructed until the CLI says "COMPLETE".

For foundation (0.0.x) ADRs, release notes and GitHub release steps are
automatically skipped.

### Human gates (where the agent stops)

- **Walkthrough offer** — "run these or you run them?"
- **Attestation** — wait for human decision

Everything else the agent just does.

---

## MUST Rules

1. **MUST** run the CLI command immediately on invocation — no preamble
2. **MUST** keep advancing through steps until attestation or completion
3. **MUST** run commands the CLI instructs (evidence, walkthrough, closeout, gh)
4. **MUST** stop only at attestation — the one human gate
5. **MUST** use `--attest` only when CLI output says "I await your attestation"

## MUST NOT Rules

1. **MUST NOT** compose step content yourself — the CLI controls what is presented
2. **MUST NOT** stop between mechanical steps to ask the human "next"
3. **MUST NOT** add commentary or offers — just relay CLI output and run commands
4. **MUST NOT** skip the attestation gate
