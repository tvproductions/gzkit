---
id: OBPI-0.0.69-04-retire-ln-closeout-proof-binding-surface
parent: ADR-0.0.69-channels-first-closeout-proof
item: 4
lane: Heavy
status: Completed
# req_atomic: each REQ is a single indivisible deletion unit — removing the
# module/model/field (01), the CLI flag + dispatch (02), the #599 producer (03),
# and the schema property under extra="forbid" (04) are each one coherent surface
# excision; the 22-brief strip (05) is a single one-pass operation; the docs +
# GHI supersession (06) is one SUPPORT deliverable. None decomposes into parallel
# seq=02+ sub-tasks (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.69-04-01
  - REQ-0.0.69-04-02
  - REQ-0.0.69-04-03
  - REQ-0.0.69-04-04
  - REQ-0.0.69-04-05
  - REQ-0.0.69-04-06
---

# OBPI-0.0.69-04-retire-ln-closeout-proof-binding-surface: Retire `ln:` Closeout-Proof-Binding Surface

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md`
- **Checklist Item:** #4 - "OBPI-0.0.69-04: Retire `ln:` surface — model, schema, producer + tests, 19-brief strip, docs (manpage, `gz-adr-closeout-ceremony` SKILL.md, restore-health roadmap, ADR-0.0.63 package), supersede #599, strike #593 premise (Heavy)"

**Status:** Completed

## Objective

The `ln:` closeout-proof-binding surface is retired entirely — module, model, schema
property, CLI flag, and the #599 producer are deleted; the 19 `ln`-carrying briefs are
stripped; docs are updated; #599 is superseded and the #593 premise is struck — so closeout
proof has exactly one home: the derived `--closeout-proof` view.

## Lane

**Heavy** - Removes a `gz validate --closeout-proof-binding` scope (a CLI/runtime-contract
surface) and a schema property — a contract removal.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? -->

- `src/gzkit/governance/trust_audits/closeout_proof_binding.py` — DELETE the module (270 lines)
- `src/gzkit/governance/brief_structure.py` — DELETE the `ReqEvidence` model and the `BriefStructure.ln` field
- `src/gzkit/schemas/obpi_brief_structure.json` — DELETE the `ln` property (lines ~61-85)
- `src/gzkit/cli/parser_maintenance.py` — DELETE the `--closeout-proof-binding` flag (lines ~601-602)
- `src/gzkit/commands/validate_cmd.py` — DELETE the `--closeout-proof-binding` dispatch (lines ~386-387)
- `src/gzkit/commands/obpi_complete.py` — DELETE the #599 producer (`_inject_ln_block` / `_render_ln_block` / `_strip_existing_ln`); reuse `_strip_existing_ln` to strip the 19 briefs BEFORE deleting it
- `tests/` — DELETE producer/binding tests; add a regression test that a brief carrying `ln:` fails `gz validate --documents` via `extra="forbid"`
- the 19 `ln`-carrying OBPI brief files (enumerate via grep) — one-time strip of the `ln:` frontmatter block
- `docs/user/manpages/validate.md` — remove the `--closeout-proof-binding` scope entry
- `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` — remove `ln:`/closeout-proof-binding references
- `docs/design/restore-health-convergence-roadmap.md` — remove `ln:`/closeout-proof-binding references
- `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/` — remove `ln:`/closeout-proof-binding references from the ADR-0.0.63 package
- `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md` — parent ADR (read-only reference)
- `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/obpis/OBPI-0.0.69-04-retire-ln-closeout-proof-binding-surface.md` — this brief

> The line numbers above are current locations; if a refactor has moved them, locate the
> real home before editing and note the divergence. Enumerate the 19 briefs by grep rather
> than trusting this count blindly — the strip must cover every `ln`-carrying brief.

## Denied Paths

<!-- What is OUT OF SCOPE? -->

- `src/gzkit/governance/trust_audits/closeout_proof.py` and the `--closeout-proof` view — OBPI-03's scope
- The SUPPORT branch and FENCE arm of `req_kind.py` — OBPI-01/02 scopes
- `.pre-commit-config.yaml` and the `gz check` session-green wiring (ADR-0.0.68) — must stay untouched
- New runtime dependencies; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The `closeout_proof_binding.py` module, the `ReqEvidence` model, the `BriefStructure.ln` field, the schema `ln` property, the `--closeout-proof-binding` flag + dispatch, and the #599 producer (`_inject_ln_block`/`_render_ln_block`/`_strip_existing_ln`) MUST all be deleted.
1. REQUIREMENT: All `ln`-carrying briefs (enumerate by grep) MUST be stripped of the `ln:` block in one pass (reusing `_strip_existing_ln` before it is deleted); a leftover `ln:` MUST then fail `gz validate --documents` via the schema's `extra="forbid"`.
1. REQUIREMENT: All docs that reference `ln:`/`--closeout-proof-binding` (manpage, `gz-adr-closeout-ceremony` SKILL.md, restore-health roadmap, ADR-0.0.63 package) MUST be updated; `mkdocs build --strict`, `gz cli audit`, and `gz validate --cli-alignment` MUST stay green.
1. REQUIREMENT: GHI #599 MUST be marked superseded with a pointer to ADR-0.0.69; the #593 premise MUST be struck (its premise no longer holds once the stored block is gone).
1. REQUIREMENT: The derived `--closeout-proof` view, the SUPPORT/FENCE arms, and all ADR-0.0.68 surfaces MUST NOT be modified (scope boundary).
1. REQUIREMENT: This OBPI MUST be executed LAST in the ADR-0.0.69 sequence so the strip reuses `_strip_existing_ln` before it is deleted (process prerequisite).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item (4)** — quote it verbatim into this brief's Implementation Summary.
- [ ] Parent ADR § Intent and § Consequences (supersession of #599, drift-surface rationale).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md`

> **STOP:** If you cannot quote the parent ADR § Decision item (4) that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] OBPI-03 has landed (the `--closeout-proof` view is the replacement home before the binding surface is removed)

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.69-03 has landed (the derived view exists before the stored surface is removed)
- [ ] `closeout_proof_binding.py`, `brief_structure.py` `ReqEvidence`/`ln`, the schema `ln` property, the flag, and the #599 producer all located
- [ ] The full set of `ln`-carrying briefs enumerated by grep (validate the "19" count)
- [ ] The doc surfaces (manpage, `gz-adr-closeout-ceremony` SKILL.md, restore-health roadmap, ADR-0.0.63 package) located

**Existing Code (understand current state):**

- [ ] `_strip_existing_ln` read whole — it is reused for the strip, then deleted in the same OBPI
- [ ] The schema `extra="forbid"` mechanism confirmed so a leftover `ln:` fails `gz validate --documents`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- Single-program, shell-less invocations only (GHI #415). -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --cli-alignment
uv run gz cli audit
```

## Demo

```bash
# The retired flag no longer resolves (argparse rejects it):
uv run gz validate --closeout-proof-binding
# No brief carries an `ln:` block any longer; documents validate clean:
uv run gz validate --documents
```

## Acceptance Criteria

<!-- Each REQ carries exactly one inline [kind] tag (ADR-0.0.59). -->

- [ ] REQ-0.0.69-04-01 [behavior]: Given the codebase after this OBPI, when `closeout_proof_binding`, `ReqEvidence`, and `BriefStructure.ln` are referenced, then they no longer exist (import fails / attribute absent). (@covers test asserting absence)
- [ ] REQ-0.0.69-04-02 [behavior]: Given the retired `--closeout-proof-binding` flag, when it is invoked, then `gz validate` rejects it as an unknown flag (exit 2, argparse error). (@covers test)
- [ ] REQ-0.0.69-04-03 [behavior]: Given a completed OBPI, when `gz obpi complete` runs, then no `ln:` block is injected — the #599 producer (`_inject_ln_block`/`_render_ln_block`/`_strip_existing_ln`) is gone. (@covers test asserting no `ln:` injection)
- [ ] REQ-0.0.69-04-04 [behavior]: Given a brief carrying an `ln:` frontmatter block, when `gz validate --documents` runs, then it fails via the schema's `extra="forbid"` (the `ln` property is removed). (@covers test driving a fixture brief with `ln:`)
- [ ] REQ-0.0.69-04-05 [support]: All `ln`-carrying briefs (enumerated by grep) are stripped of the `ln:` block in one pass. Proof: `artifact_edited` ledger events for the stripped briefs + `gz validate --documents` exit 0.
- [ ] REQ-0.0.69-04-06 [support]: Docs are updated (manpage `--closeout-proof-binding` entry removed, `gz-adr-closeout-ceremony` SKILL.md, restore-health roadmap, ADR-0.0.63 package); GHI #599 is superseded and the #593 premise struck. Proof: `artifact_edited` ledger events + `mkdocs build --strict` + `gz cli audit` + `gz validate --cli-alignment` exit 0.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

Before: the `ln:` closeout-proof-binding block stored a redundant copy of receipt evidence
across 19 briefs, backed by a 270-line module, a schema property, a CLI flag, and a #599
auto-populate producer — a drift surface storing derived evidence as canon. Now: the entire
surface is gone and closeout proof has exactly one home, the derived `--closeout-proof` view.

### Key Proof


The retired flag is rejected as unknown, and no brief carries a stale ln: block:

    $ uv run gz validate --closeout-proof-binding
    -> exit 2: error: unrecognized arguments: --closeout-proof-binding

    $ grep -r "^ln:" docs/design/adr --include="*.md" | wc -l
    -> 0

Full suite green: 6023/6023 tests (arb-step-unittest-2149c3e4c485462595eb9af7b1245ae0); lint clean (arb-ruff-e5cff6dfbd1148b6842de3c2c78d2a6b); typecheck clean (arb-step-typecheck-c34e64840e874ebca1c2b3f87dee2a3d); mkdocs --strict clean (arb-step-mkdocs-bfa173737b8e49c5a491382795616b37); gz validate --cli-alignment exit 0 (104/104); gz validate --documents exit 0.

### Implementation Summary


- Files deleted: src/gzkit/governance/trust_audits/closeout_proof_binding.py (270 lines); tests/governance/test_closeout_proof_binding.py (333 lines); tests/test_obpi_complete_ln_producer.py
- Files modified: brief_structure.py (deleted ReqEvidence + BriefStructure.ln); obpi_brief_structure.json (deleted ln property); parser_maintenance.py + validate_cmd.py (deleted --closeout-proof-binding flag + 7 check refs); obpi_complete.py (deleted 3 producer functions + injection); trust_audits/__init__.py (removed binding import/export); test_obpi_complete.py (removed TestObpiCompleteWritesLnProofBinding); 22 OBPI briefs (stripped ln: frontmatter); docs/user/manpages/validate.md; .gzkit/skills/gz-adr-closeout-ceremony/SKILL.md (v7.13.1->7.14.0); docs/design/restore-health-convergence-roadmap.md
- Files created: tests/governance/test_retire_ln_surface.py (5 @covers absence tests, REQ-01..04)
- Tests added: TestRetireLnSurface (5 tests, RED->GREEN confirmed)
- GHIs: #599 superseded; #593 premise struck
- Date completed: 2026-06-10
- Attestation status: operator attested ("attest completed") in Stage 4 ceremony
- Defects noted: none

## Tracked Defects

- Supersedes #599 (auto-populate producer deleted); strikes the #593 premise.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.69-04 retire-ln-closeout-proof-binding-surface: the ln: surface is gone entirely. Deleted closeout_proof_binding.py (270 lines), ReqEvidence model + BriefStructure.ln field, schema ln property, --closeout-proof-binding flag + dispatch (7 refs across parser_maintenance.py/validate_cmd.py), and the #599 producer (_inject_ln_block/_render_ln_block/_strip_existing_ln) + injection call. Stripped ln: from all 22 carrying briefs in one pass (reusing _strip_existing_ln before deleting it). Docs updated (manpage, gz-adr-closeout-ceremony SKILL.md v7.13.1→7.14.0, restore-health roadmap). #599 superseded, #593 premise struck. 5 @covers absence tests in test_retire_ln_surface.py (RED→GREEN); deleted test_closeout_proof_binding.py (333 lines) + test_obpi_complete_ln_producer.py. Full suite 6023/6023 (arb-step-unittest-2149c3e4c485462595eb9af7b1245ae0); lint clean (arb-ruff-e5cff6dfbd1148b6842de3c2c78d2a6b); typecheck clean (arb-step-typecheck-c34e64840e874ebca1c2b3f87dee2a3d); mkdocs --strict clean (arb-step-mkdocs-bfa173737b8e49c5a491382795616b37); gz validate --cli-alignment 104/104; gz validate --documents exit 0. Closeout proof now has exactly one home: the derived gz validate --closeout-proof view.
- Date: 2026-06-11

---

**Date Completed:** 2026-06-11

**Evidence Hash:** -
