---
id: OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement
parent: ADR-0.34.0-foundation-sunset
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement: Terminal Partition Gate And Doctrine Retirement

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`
- **Checklist Item:** #3 — "terminal-partition-gate-and-doctrine-retirement: Add the terminal-partition assertion to gz validate --taxonomy reading the Layer-2 foundation_grandfathered ledger event (never frontmatter): every grandfathered foundation is terminal, none in Pending-with-attested-work limbo -> finding foundation_limbo, whose prose states it reads the ledger and points at gz closeout / gz adr demote. Retire ADR-0.0.18's choose-foundation guidance (record stays frozen). Execute the coupled-surface coherence sweep (gz-design Step 5, plan/promote help + parser choices, AGENTS.md/CLAUDE.md Kinds table, foundation-feature-invariance-test.md, ADR-0.0.35 review). (heavy lane: new validator behavior + doc coherence)."

**Status:** Draft

## Objective

Add the terminal-partition assertion to `gz validate --taxonomy` that computes each grandfathered foundation's terminal state from the Layer-2 `foundation_grandfathered` ledger event (never frontmatter), emits finding `foundation_limbo` (exit 3) with ledger-reads/next-step recovery prose when a grandfathered foundation is non-terminal, and — in the same movement — retires ADR-0.0.18's choose-foundation guidance (record frozen, not deleted) and sweeps the coupled authoring surfaces so no surface still teaches `foundation` as an available kind for a new ADR.

## Lane

**Heavy** — This OBPI changes a runtime contract: it extends the `gz validate --taxonomy`
scope with a new fail-closed assertion and a new `--json` finding
(`foundation_limbo`) that external consumers parse. Heavy per the parent ADR's
lane and per the Gate Covenant (validator-scope / runtime-contract change).

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->
<!-- First backtick token on each bullet is the path; **CREATE** marks net-new files (existence-gate exempt, GHI #419). -->

- `src/gzkit/governance/trust_audits/taxonomy.py` — add the terminal-partition assertion (`foundation_limbo` finding) as a helper composed into `audit_adr_taxonomy`; read the Layer-2 ledger by replaying raw `.gzkit/ledger.jsonl` lines via `json.loads` filtering `event == "foundation_grandfathered"` — the exact pattern already established in `audit_pool_adr_isolation` (this file, lines 63–93). NEVER read frontmatter for terminal state.
- `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md` — add a `> Superseded (choose-foundation guidance) by ADR-0.34.0-foundation-sunset` marker at the guidance sections; the ADR record and its Decision stay present (frozen-historic — void as instruction, preserved as history).
- `.gzkit/skills/gz-design/SKILL.md` — canonical skill (edits target this surface, NOT the generated vendor mirrors); Step 5 kind question (line ~137) must stop presenting `foundation` as a selectable kind for a new ADR (foundation kind closed by ADR-0.34.0; new ADRs are `feature` or `pool`). Run `gz agent sync control-surfaces` after the edit to regenerate the `.claude/`, `.agents/`, and `.github/` mirrors — never hand-edit those.
- `docs/user/concepts/foundation-feature-invariance-test.md` — note that the `foundation` kind is CLOSED for gzkit authoring (ADR-0.34.0); the invariance test remains valid doctrine for adopters (whose `gz init` scaffolds open) and for reading the grandfathered set.
- `docs/user/concepts/adr-taxonomy.md` — same closure note: `foundation` is a grandfathered-only kind for gzkit; no new foundation ADRs may be authored.
- `tests/test_foundation_limbo_gate.py` — **CREATE**: net-new `@covers` tests for the `foundation_limbo` finding + Layer-2 ledger-read (not frontmatter) behavior (REQ-0.34.0-03-01) and the recovery-prose assertion (REQ-0.34.0-03-02).
- `tests/test_foundation_doctrine_retirement.py` — **CREATE**: net-new `@covers` tests for the ADR-0.0.18 superseded-marker content assertion (REQ-0.34.0-03-03) and the coupled-surface closure assertions (REQ-0.34.0-03-04).

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `AGENTS.md`, `CLAUDE.md` — RENDERED surfaces composed from the corpus; NEVER hand-edited. The Kinds-table doctrine update (marking `foundation` closed for authoring) routes through the corpus source of truth via `gz content remember` against `.gzkit/corpus/AGENTS.md.jsonl`, then recomposition — a corpus write, not a rendered-surface edit. Capturing that corpus entry is deferred to the migration/compose movement; this brief records the routing so the sweep is not "completed" by an illegal direct edit.
- `src/gzkit/commands/validate_cmd.py` — NOT edited: `_taxonomy_runner` already calls `audit_adr_taxonomy`, so composing the new assertion into that function flows through the existing runner with no wiring change. (Registering the whole `--taxonomy` gate into `gz check` as the standing gate is OBPI-04's last act — "wiring equals populate" — not this OBPI.)
- `data/foundation_grandfather.json` — READ-ONLY here; authored by OBPI-01, populated by OBPI-04. This OBPI's assertion reads the ledger event, not this manifest.
- `src/gzkit/cli/parser_artifacts.py`, `src/gzkit/cli/parser_governance.py` — the `gz plan create`/`gz adr promote` `--kind` parser-choice rejection is OBPI-02's scope, not this one.
- `docs/design/adr/foundation/ADR-0.0.35-*` — ADR-0.0.35 is a *review* item (read-only confirmation it teaches nothing stale), not an edit target.
- New runtime dependencies; CI files; lockfiles.
- Any path not listed in Allowed Paths.

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language. -->

1. ALWAYS: The terminal-partition assertion MUST compute terminal state from the Layer-2 `foundation_grandfathered` ledger event. NEVER read ADR frontmatter (`status:`) for terminal state — the ADR-0.0.37 investigation proved frontmatter lies about repudiated OBPIs.
2. ALWAYS: When a grandfathered foundation is non-terminal (no covering `foundation_grandfathered` ledger event / sits in Pending-with-attested-work limbo), `gz validate --taxonomy` MUST emit finding `foundation_limbo` and exit 3.
3. ALWAYS: The `foundation_limbo` finding prose MUST explicitly state that it reads the ledger (not frontmatter) and MUST name `gz closeout` and `gz adr demote` as the governed next steps (three-part guardrail-feedback prose per `.claude/rules/guardrail-feedback-prose.md`).
4. ALWAYS: ADR-0.0.18's choose-foundation guidance MUST carry a superseded-by-ADR-0.34.0 marker, and its ADR record MUST remain present on disk (frozen-historic — NEVER deleted).
5. NEVER: Leave any coupled authoring surface (gz-design Step 5, `foundation-feature-invariance-test.md`, `adr-taxonomy.md`) presenting `foundation` as a selectable kind for a NEW gzkit ADR.
6. NEVER: Hand-edit `AGENTS.md` / `CLAUDE.md` to update the Kinds table — route through the corpus (`gz content remember`).
7. NEVER: Wire the assertion behind a hand-set staging flag or edit `validate_cmd.py` to force-green an interim red — anti-staging-flag doctrine (parent ADR § Decision). With an empty/backfill-pending manifest and no `foundation_grandfathered` events yet, the assertion has nothing to assert and stays green by construction until OBPI-04 populates.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.
9. REQUIREMENT: Verification commands MUST be concrete, runnable, single-program, shell-less lines with real outputs pasted into Evidence before acceptance.
10. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief, or without brief-level human attestation (ADR-0.0.36, universal Gate 5).

> STOP-on-BLOCKERS: if prerequisites are missing (OBPI-01 manifest model /
> `foundation_grandfathered` event shape not yet defined, or the coupled
> surfaces absent), print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary. The item: *"Add the terminal-partition assertion to gz validate --taxonomy reading the Layer-2 foundation_grandfathered ledger event (never frontmatter): every grandfathered foundation is terminal, none in Pending-with-attested-work limbo -> finding foundation_limbo, whose prose states it reads the ledger and points at gz closeout / gz adr demote. Retire ADR-0.0.18's choose-foundation guidance (record stays frozen). Execute the coupled-surface coherence sweep ..."*
- [ ] Parent ADR § Intent — the Layer-2-truth-not-frontmatter framing and the sealed-not-deleted rationale.
- [ ] Parent ADR § Decision "REVIEW REFINEMENTS" (b) — the BACKFILL-AT-POPULATE refinement: the ledger is INCOMPLETE for pre-ledger foundations, so this gate reads the `foundation_grandfathered` event that OBPI-04 backfills, staying Layer-2 while honoring never-frontmatter. This gate is green-by-construction until that populate lands.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Sibling OBPIs (this ADR — coupling, read once):**

- [ ] OBPI-01 (`grandfather-manifest-and-closed-kind-assertion`) — establishes `data/foundation_grandfather.json`, the `FoundationGrandfatherManifest` model, and the `foundation_kind_closed` / `grandfather_dangling` assertions this OBPI composes alongside in `taxonomy.py`. Read to match the assertion-composition pattern.
- [ ] OBPI-04 (`execute-migration-populate-and-resense`) — emits the `foundation_grandfathered` ledger events this gate reads and does the final `gz check` wiring. This OBPI ships the mechanism; OBPI-04 populates it.

**Existing Code (understand current state; read before editing):**

- [ ] `src/gzkit/governance/trust_audits/taxonomy.py` — `audit_pool_adr_isolation` (lines 63–93) is the exact raw-line ledger-replay pattern to reuse for the Layer-2 read; `audit_adr_taxonomy` (lines 180–196) is the function `_taxonomy_runner` invokes and the composition point for the new assertion.
- [ ] `src/gzkit/commands/validate_cmd.py` — confirm `_ScopeEntry("taxonomy", ...)` → `_taxonomy_runner` → `audit_adr_taxonomy` (lines 227, 433–437); confirm no runner edit is needed.
- [ ] `.claude/rules/guardrail-feedback-prose.md` — the three-part recovery-prose bar the `foundation_limbo` message must meet.
- [ ] `.gzkit/skills/gz-design/SKILL.md` Step 5 (line ~137) and `docs/user/concepts/foundation-feature-invariance-test.md` / `adr-taxonomy.md` — the current wording that presents `foundation` as a live authoring choice.
- [ ] `.gzkit/corpus/AGENTS.md.jsonl` — the corpus that renders the AGENTS.md/CLAUDE.md Kinds table; the `gz content remember` routing target (Denied-Paths note).

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract; § Kinds table (rendered — do not hand-edit)

**Prerequisites (check existence, STOP if missing):**

- [ ] `data/foundation_grandfather.json` model and the `foundation_grandfathered` event shape from OBPI-01/OBPI-04 are defined (or intentionally read as raw JSON so this gate does not hard-depend on the typed model).
- [ ] Parent ADR file present; ADR-0.0.18 package present; coupled surfaces present.

## Quality Gates

<!-- Which gates apply and how to verify them. Heavy lane — all gates apply. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from the four REQ acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] ADR-0.0.18 superseded marker + concept docs (`foundation-feature-invariance-test.md`, `adr-taxonomy.md`) updated for kind closure

### Gate 4: BDD (Heavy)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded (universal brief-level Gate 5, ADR-0.0.36)

## Verification

<!-- Single-program, shell-less lines only: no &&, ||, |, ;, $(...), redirects. -->

```bash
uv run gz validate --documents
uv run gz validate --taxonomy
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
test -f src/gzkit/governance/trust_audits/taxonomy.py
test -f docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md
rg -n "foundation_limbo" src/gzkit/governance/trust_audits/taxonomy.py
rg -n "Superseded" docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md
rg -n "ADR-0.34.0" docs/user/concepts/foundation-feature-invariance-test.md
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations. -->

```bash
# 1. Clean run — with no grandfathered foundation in limbo, the gate is green.
uv run gz validate --taxonomy

# 2. The limbo finding, shown as JSON (the machine-parseable contract).
#    After OBPI-04 backfills foundation_grandfathered events, remove/repudiate
#    the covering event for one grandfathered ADR and re-run to see exit 3.
uv run gz validate --taxonomy --json

# 3. The recovery prose proves it reads the LEDGER, not frontmatter, and names
#    the governed next steps.
uv run gz validate --taxonomy --json
rg -n "reads the ledger" src/gzkit/governance/trust_audits/taxonomy.py
rg -n "gz closeout" src/gzkit/governance/trust_audits/taxonomy.py
rg -n "gz adr demote" src/gzkit/governance/trust_audits/taxonomy.py

# 4. ADR-0.0.18 is frozen-historic: record present, guidance marked superseded.
test -f docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md
rg -n "Superseded .*ADR-0.34.0" docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md

# 5. The coupled authoring surfaces no longer offer foundation as a new-ADR kind.
rg -n "ADR-0.34.0" docs/user/concepts/foundation-feature-invariance-test.md
rg -n "foundation" .gzkit/skills/gz-design/SKILL.md
```

## Acceptance Criteria

<!-- Each checkbox carries a deterministic REQ ID and a [kind] tag (ADR-0.0.59). -->

- [ ] REQ-0.34.0-03-01 [BEHAVIOR]: `gz validate --taxonomy` emits finding `foundation_limbo` and exits 3 when a grandfathered foundation lacks a covering `foundation_grandfathered` Layer-2 ledger event (is non-terminal / in Pending-with-attested-work limbo), computing terminal state from ledger events — NEVER from ADR frontmatter. Proof: a `@covers(REQ-0.34.0-03-01)` test that seeds a fixture project with a grandfathered foundation and NO covering ledger event, runs the assertion, and asserts a `foundation_limbo` ValidationError with exit-3 semantics; a companion assertion proves a frontmatter `status:` change alone cannot flip the result.
- [ ] REQ-0.34.0-03-02 [BEHAVIOR]: the `foundation_limbo` finding prose explicitly states it reads the ledger (not frontmatter) and names `gz closeout` and `gz adr demote` as the governed next steps. Proof: a `@covers(REQ-0.34.0-03-02)` test asserting the message string contains the ledger-not-frontmatter clause and both verb names (three-part guardrail-feedback shape).
- [ ] REQ-0.34.0-03-03 [BEHAVIOR]: ADR-0.0.18's choose-foundation guidance carries a superseded-by-ADR-0.34.0 marker (a content assertion), and its ADR record remains present on disk (frozen-historic, not deleted). Proof: a `@covers(REQ-0.34.0-03-03)` test asserting the ADR-0.0.18 file exists AND contains the `ADR-0.34.0` superseded marker.
- [ ] REQ-0.34.0-03-04 [BEHAVIOR]: the coupled authoring surfaces (gz-design Step 5, `docs/user/concepts/foundation-feature-invariance-test.md`) no longer present `foundation` as an available authoring choice for new ADRs. Proof: a `@covers(REQ-0.34.0-03-04)` test asserting each surface carries the kind-closed note referencing ADR-0.34.0 and no longer offers `foundation` as a selectable new-ADR kind.

> **Kind choice for REQ-0.34.0-03-03 + rationale:** REQ-0.34.0-03-03
> is authored as **BEHAVIOR**, not SUPPORT. The retirement is a *content*
> assertion on a file (superseded marker present + record still on disk), and its
> natural proof channel is a `@covers` test that reads the file and asserts the
> marker string and file existence — a real, failable content test. SUPPORT's
> proof channel (a ledger event + a structural validator) would be heavier
> machinery than the two-way content fact warrants and would not actually prove
> the marker text a reader sees. BEHAVIOR with a `@covers` content test is the
> tighter, more honest proof, so all four REQs are BEHAVIOR.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from the four REQs, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** mkdocs strict build clean; ADR-0.0.18 + concept docs updated
- [ ] **Gate 4 (BDD):** behave scenarios pass
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **Gate 5 (Human):** Brief-level human attestation recorded (ADR-0.0.36, universal)
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation. -->

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
# Paste mkdocs --strict output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here (universal brief-level Gate 5, ADR-0.0.36)
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

Before: "no more foundation ADRs" and "no foundation may rot in limbo" were
policy the operator restated — nothing mechanically stopped a grandfathered
foundation from sitting Pending-with-attested-work, and the only terminal
signal available was frontmatter `status:`, which the ADR-0.0.37 investigation
proved can lie. After: `gz validate --taxonomy` reads the Layer-2
`foundation_grandfathered` ledger event and fail-closes (`foundation_limbo`,
exit 3) on any non-terminal grandfathered foundation, with recovery prose that
points at `gz closeout` / `gz adr demote`; and every authoring surface (skill
Step 5, concept docs, and — via the frozen ADR-0.0.18 marker — the doctrine
record) tells readers the foundation kind is closed.

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

`uv run gz validate --taxonomy --json` returns a `foundation_limbo` finding
(exit 3) for a grandfathered foundation with no covering `foundation_grandfathered`
ledger event, and the finding message names `gz closeout` / `gz adr demote` —
computed from the ledger, unchanged by any frontmatter `status:` edit.

### Implementation Summary

- Parent ADR § Decision item (quoted):
- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
</content>
</invoke>
