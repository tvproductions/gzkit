---
id: OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement
parent: ADR-0.34.0-foundation-sunset
item: 3
lane: Heavy
status: Completed
allowlist:
- src/gzkit/governance/trust_audits/taxonomy.py
- docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md
- .gzkit/skills/gz-design/SKILL.md
- .claude/
- .agents/
- .github/
- docs/user/concepts/foundation-feature-invariance-test.md
- docs/user/concepts/adr-taxonomy.md
- tests/test_foundation_limbo_gate.py
- tests/test_foundation_doctrine_retirement.py
- tests/governance/test_taxonomy_closed_kind.py
- src/gzkit/commands/validate_cmd.py
reqs:
- REQ-0.34.0-03-01
- REQ-0.34.0-03-02
- REQ-0.34.0-03-03
- REQ-0.34.0-03-04
# REQ-0.34.0-03-01 is deliberately ABSENT — its labor genuinely subdivided across
# three distinct surfaces and is accounted as TASK-...-01-01/02/03:
#   01 the ledger-read predicate + set-difference in taxonomy.py
#   02 the exit-3 policy-breach registration in validate_cmd.py (a separate file and
#      a separate contract, surfaced only by Step-4b adversarial pass 1)
#   03 the non-object-ledger-line robustness guard (surfaced by adversarial pass 2)
req_atomic:
# One indivisible unit of labor each; no step below the REQ existed.
- REQ-0.34.0-03-02  # authoring one finding message to the three-part prose bar
- REQ-0.34.0-03-03  # seating the superseded marker on one ADR record
- REQ-0.34.0-03-04  # one coherent closure sweep: skill Step 5 + 2 concept pages + sync
verification:
- uv run gz validate --documents
- uv run gz validate --taxonomy
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run mkdocs build --strict
---

# OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement: Terminal Partition Gate And Doctrine Retirement

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`
- **Checklist Item:** #3 — "terminal-partition-gate-and-doctrine-retirement: Add the terminal-partition assertion to gz validate --taxonomy reading the Layer-2 foundation_grandfathered ledger event (never frontmatter): every grandfathered foundation is terminal, none in Pending-with-attested-work limbo -> finding foundation_limbo, whose prose states it reads the ledger and points at gz closeout / gz adr demote. Retire ADR-0.0.18's choose-foundation guidance (record stays frozen). Execute the coupled-surface coherence sweep (gz-design Step 5, plan/promote help + parser choices, AGENTS.md/CLAUDE.md Kinds table, foundation-feature-invariance-test.md, ADR-0.0.35 review). (heavy lane: new validator behavior + doc coherence)."

**Status:** Completed

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
- `tests/governance/test_taxonomy_closed_kind.py` — coupled-surface coherence only (DO IT RIGHT 1a; operator-approved allowlist amendment 2026-07-29). OBPI-01's `test_listed_foundation_adr_is_clean` fixture predates the terminal-partition assertion and asserts the whole audit is silent for a foundation with no ledger witness. Fix is fixture-only: seed the `foundation_grandfathered` event so the fixture describes a genuinely valid grandfathered foundation. The `assertEqual(..., [])` assertion is NOT weakened, and no attested REQ-0.34.0-01-* claim changes.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `AGENTS.md`, `CLAUDE.md` — RENDERED surfaces composed from the corpus; NEVER hand-edited. The Kinds-table doctrine update (marking `foundation` closed for authoring) routes through the corpus source of truth via `gz content remember` against `.gzkit/corpus/AGENTS.md.jsonl`, then recomposition — a corpus write, not a rendered-surface edit. Capturing that corpus entry is deferred to the migration/compose movement; this brief records the routing so the sweep is not "completed" by an illegal direct edit.
- `src/gzkit/commands/validate_cmd.py` — **narrowed, not blanket-denied** (amended 2026-07-29, operator-approved, after the Step-4b adversarial refutation). NOT rewired: `_taxonomy_runner` already calls `audit_foundation_closure`, so the assertion needs no runner change, and registering the `--taxonomy` gate into `gz check` remains OBPI-04's last act ("wiring equals populate"). The ONE permitted edit is adding `foundation_limbo` to `_POLICY_BREACH_ERROR_TYPES`. The original blanket denial contradicted REQ-0.34.0-03-01's own exit-3 mandate: unregistered finding types route to `SystemExit(1)` (`validate_cmd.py:1168`) and only registered ones reach `SystemExit(3)` (line 1170), so exit 3 is unreachable without the registration. Sibling OBPI-01 registered `foundation_kind_closed` / `grandfather_dangling` in the same frozenset for the same reason. This is registration, NOT the force-green edit REQ-7 forbids — it makes a real finding fail *harder*, never green.
- `data/foundation_grandfather.json` — READ-ONLY here; authored by OBPI-01, populated by OBPI-04. This OBPI's assertion reads the ledger event, not this manifest.
- `src/gzkit/cli/parser_artifacts.py`, `src/gzkit/cli/parser_governance.py` — the `gz plan create`/`gz adr promote` `--kind` parser-choice rejection is OBPI-02's scope, not this one.
- `docs/design/adr/foundation/ADR-0.0.35-*` — ADR-0.0.35 is a *review* item (read-only confirmation it teaches nothing stale), not an edit target.
- `.gzkit/ledger.jsonl` — never edited directly. Deliberately NOT in § Allowed Paths despite being written during this OBPI's ceremony: declaring it livelocks the pipeline — `gz obpi brief-drift` emits a `brief_reconciled` ledger event, which drifts the now-allowlisted path, which re-stales the receipt it just wrote, forever. Ceremony control artifacts written only by `gz` commands belong here, not in the allowlist. Matches sibling OBPI-0.34.0-01 § Denied Paths verbatim in rationale (adjacent: GHI #677).
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
#    the covering event for one grandfathered ADR and re-run.
#    NOTE: `--json` reports `"valid": false` with the finding in `errors[]` and
#    exits 0 — the established repo-wide contract for EVERY finding type, pinned
#    by tests/commands/test_validate_cmds.py:726 ("--json doesn't raise
#    SystemExit"). Exit 3 is the TEXT-mode path (command 1 above); read `valid`
#    when consuming JSON. Corrected 2026-07-29 after a Step-4b adversarial pass
#    flagged the prior wording as promising exit 3 from `--json`.
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

### Step 4b — Independent Adversarial Validation

**Adversary:** Codex (tier 1, different vendor — `codex-cli 0.145.0`). `codex:setup`
reported `ready: true`, `sessionRuntime: direct` (no wedged broker), so tier 1 was
genuinely available and tiers 2/3 were forbidden. Three passes, each prompted to
REFUTE and to produce its own evidence rather than trust pasted output:

| Pass | Job | Session | Verdict |
|---|---|---|---|
| 1 | `task-ms5gaqdb-6721ed` | `019faba6-2de4-7701-978e-4c524e1d9018` | REFUTED |
| 2 | `task-ms5iz3ye-w4z656` | `019fabea-c5be-7160-b0a4-7684bad36283` | REFUTED |
| 3 | `task-ms5uezyf-6coaah` | `019fad10-007b-7b10-8d9b-387d5f48140c` | REFUTED |

**Pass 1 — decisive refutation, FIXED.** `foundation_limbo` was absent from
`_POLICY_BREACH_ERROR_TYPES`, so a limbo-only validation rendered the finding and then
exited **1** where REQ-0.34.0-03-01 requires **3**. The live repo's 74 inherited
`foundation_kind_closed` findings masked it — the CLI exited 3 for a sibling's reason.
Reproduced locally as `AssertionError: 1 != 3`, fixed by registering the type (an
operator-approved narrowing of the `validate_cmd.py` denial), and re-verified by the
adversary: `limbo_only_text exit=3`, `mixed_text exit=1`.

**Pass 2 — two new defects, both FIXED.** (a) `_grandfathered_event_ids` crashed with
`AttributeError: 'list' object has no attribute 'get'` on a valid non-object ledger
line — guarded with `isinstance(event, dict)` plus two tests, one proving junk lines do
not mask a real witness beside them. (b) The exit test was hollow as CLI proof —
`test_taxonomy_scope_dispatch_surfaces_the_finding` now drives `_taxonomy_runner`
itself; the adversary confirmed the fix meaningful.

**Pass 3 — REQ-03/04 proof channel STILL BROKEN, and the caveat was DISHONEST.** An
earlier draft of § Tracked Defects claimed fence decoys, nested blockquotes, and
duplicate headings were rejected. Direct mutations disproved it (tilde fences,
four-space indented blocks, setext/case/closing-hash duplicates, nested blockquotes,
HTML-comment/fence interactions all still pass). The caveat has been **corrected to a
verbatim accepted-bypass table**; the false claim was also corrected on GHI #615
(comment `5115546992`). The adversary's position was *"Gate 5 should not proceed."*

**Resolution and disposition.** Every refutation admitting a mechanical fix was fixed
and independently re-verified. The residual — REQ-03/04's doc-content proof channel —
is a **proof-channel** weakness, not an artifact defect: it under-detects a hostile
*future* edit; it does not misreport the *present* state, which is verifiable by reading
the four surfaces (§ Demo 4 and 5). Root cause is the one `.gzkit/rules/tests.md`
§ The discriminator names — a `@covers` grep is the wrong channel for a document claim —
and it is homed as an instance on GHI #615. The operator attested **holding this
verdict and the corrected caveat**, having been offered the alternatives of rewriting
the tests against a parsed Markdown structure or halting unattested.

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

The load-bearing claim is *ledger, never frontmatter* — and it is proven by a negative
control, not by a happy-path run:

```text
$ uv run -m unittest tests.test_foundation_limbo_gate -v
test_frontmatter_status_cannot_clear_the_finding ... ok
test_terminal_ledger_event_clears_the_finding ... ok
test_declared_foundation_without_ledger_event_is_flagged ... ok
Ran 12 tests — OK
```

A grandfathered foundation marked `status: Validated` — the most terminal-looking
frontmatter available — still returns `['foundation_limbo']`, because the ledger carries
no witness. Seeding a `foundation_grandfathered` event clears it. Neither containment
breach is double-reported. The finding reaches the operator as **exit 3**, verified
end-to-end by the independent adversary:

```text
limbo_only_text  exit=3   (policy breach)
mixed_text       exit=1   (non-policy error present — masking prevented)
```

Receipts: `arb-step-unittest-d2bb1e6dbb1e4922af795e855ebe12a1` (7574 tests),
`arb-ruff-6894721afdfc4dd8b8d9b7c4eb5c799b`,
`arb-step-typecheck-6180fce77ca44b96aed3e61f8fcfbe95`,
`arb-step-mkdocs-91e7b8fdebd44fe3aac73978b4fdadfd`.
RED witnesses, all `failure_class=assertion`:
`arb-red-REQ-0.34.0-03-01-d688344bde8f4c8da66ec3350596805c`,
`arb-red-REQ-0.34.0-03-02-648088e049ba44c196710313f026c8b1`,
`arb-red-REQ-0.34.0-03-03-dcb61d90d3654509825bd377252430fa`,
`arb-red-REQ-0.34.0-03-04-83cb31b55893467ea7bc57f08f723935`.

**Scope honesty:** `uv run gz validate --taxonomy` exits 3 with **74
`foundation_kind_closed`** findings inherited from OBPI-01's assertion over the empty
manifest (cleared by OBPI-04). This OBPI adds **zero** findings and removes zero —
census verified as `{"foundation_kind_closed": 74}` with `git blame` attributing all 74
to committed sibling work. The green signal here is the census, not the exit code.

### Implementation Summary


- Parent ADR § Decision item (quoted): *"terminal-partition-gate-and-doctrine-retirement: Add the terminal-partition assertion to gz validate --taxonomy reading the Layer-2 foundation_grandfathered ledger event (never frontmatter): every grandfathered foundation is terminal, none in Pending-with-attested-work limbo -> finding foundation_limbo, whose prose states it reads the ledger and points at gz closeout / gz adr demote. Retire ADR-0.0.18's choose-foundation guidance (record stays frozen). Execute the coupled-surface coherence sweep (gz-design Step 5, plan/promote help + parser choices, AGENTS.md/CLAUDE.md Kinds table, foundation-feature-invariance-test.md, ADR-0.0.35 review). (heavy lane: new validator behavior + doc coherence)."*
- Mechanism: `_grandfathered_event_ids` replays raw `.gzkit/ledger.jsonl` lines for `event == "foundation_grandfathered"` (raw read, not the typed `Ledger` — the event type has no model until OBPI-04); `_limbo_error` builds the three-part finding; both composed into `audit_foundation_closure`, which `_taxonomy_runner` already invokes.
- Composition point: `audit_foundation_closure`, NOT `audit_adr_taxonomy` as § Allowed Paths states. Following the brief literally would have broken the scope-mates-not-callees separation OBPI-01 attested in that function's own docstring. Judged "technically justified, not a rationalization" by the independent adversary.
- Predicate ranges over `declared & on_disk` — genuine members — so neither containment breach (`foundation_kind_closed`, `grandfather_dangling`) is also reported as non-terminal.
- Exit-3 registration: `foundation_limbo` added to `_POLICY_BREACH_ERROR_TYPES`. Found by adversarial pass 1; without it the finding rendered and exited 1.
- Doctrine retirement: ADR-0.0.18 carries seated superseded blockquotes at `## Why foundation tier?` and `## Decision`; record and Decision text intact (frozen-historic).
- Coupled-surface sweep: `gz-design` Step 5 offers `feature`/`pool` (skill-version 1.3.2 -> 1.4.0, `last_reviewed` bumped, mirrors regenerated via `gz agent sync control-surfaces`); both concept pages carry scoped closure admonitions preserving the adopter carve-out. ADR-0.0.35 reviewed read-only — its operator-facing surface is the concept page, already closed; no edit warranted. AGENTS.md/CLAUDE.md Kinds table deferred to the corpus route per § Denied Paths.
- Files created: `tests/test_foundation_limbo_gate.py` (12 tests), `tests/test_foundation_doctrine_retirement.py` (6 tests).
- Files modified: `src/gzkit/governance/trust_audits/taxonomy.py`, `src/gzkit/commands/validate_cmd.py`, `docs/design/adr/foundation/ADR-0.0.18-.../ADR-0.0.18-adr-taxonomy-doctrine.md`, `docs/user/concepts/adr-taxonomy.md`, `docs/user/concepts/foundation-feature-invariance-test.md`, `.gzkit/skills/gz-design/SKILL.md` (+3 vendor mirrors + pkg copy), `tests/governance/test_taxonomy_closed_kind.py` (fixture only).
- Brief amendments (all operator-approved): removed `.gzkit/ledger.jsonl` from the allowlist (it livelocked the reconcile-freshness gate — sibling OBPI-01 records the identical finding); added `tests/governance/test_taxonomy_closed_kind.py` (coupled-surface coherence); narrowed the `validate_cmd.py` denial to permit the one registration line.
- Date completed: 2026-07-29
- Attestation status: operator-attested at Gate 5 holding three adversarial REFUTED verdicts and the corrected § Tracked Defects caveat.
- Defects noted: REQ-03/04 doc-content proof-channel weakness — recorded in full in § Tracked Defects with a verbatim accepted-bypass table; homed on GHI #615 (comments `5115304791`, `5115546992`).

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI. -->

**Attested-with-caveat (operator ruling 2026-07-29): REQ-03/04 proof-channel limitation.**

**THREE** independent Step-4b adversarial passes (Codex, jobs `task-ms5gaqdb-6721ed`,
`task-ms5iz3ye-w4z656`, `task-ms5uezyf-6coaah`) established that the
REQ-0.34.0-03-03 and -03-04 tests — being doc-content assertions — cannot prove
*semantic polarity*, and that successive hardening does not close the gap.

**Stated precisely, because an earlier draft of this caveat overstated the fix and the
third pass correctly judged it dishonest.** What the tests DO reject (verified negative
controls, `scratchpad/verify_bypass*.py`): mis-seated markers, triple-backtick fence
decoys, 40-line blank gaps, HTML comments, vacuous absence, and the specific
contradiction phrasings in `_CONTRADICTION_PHRASES`.

What the tests STILL ACCEPT (measured by the third pass, not hypothesised):

| Bypass shape | Status |
|---|---|
| `~~~` (tilde) code fences | **accepted** — only triple-backtick fences are neutralised |
| Four-space indented code blocks | **accepted** |
| Setext (`===`/`---`) heading duplicates | **accepted** |
| Case-variant heading duplicates (`## decision`) | **accepted** |
| Closing-hash heading duplicates (`## Decision ##`) | **accepted** |
| Nested blockquotes (`>>`) | **accepted** |
| HTML comment spanning a closing fence | **accepted** |
| Contradiction wording outside the denylist | **accepted** (non-exhaustive by construction) |

Root cause, in the adversary's words: *"The REQ-03/04 proof treats Markdown as a few raw
string patterns rather than checking the rendered document or a real Markdown structure.
That makes the test sensitive to selected spellings and locations, while structurally
equivalent reader-visible content remains invisible to the proof."*

This is the limitation `.gzkit/rules/tests.md` § The discriminator predicts for any
`@covers` test over document content — its named remedy is the **SUPPORT** proof
channel (a structural validator over a parsed document), not a harder grep. Each
hardening round closed the previous round's spellings and the next round found new
ones; that treadmill IS the evidence that the channel is wrong, not the regex.

This is the limitation `.gzkit/rules/tests.md` § The discriminator predicts for any
`@covers` test over document content — its named remedy is the **SUPPORT** proof
channel (ledger event + structural validator), not a harder grep. This brief
deliberately tagged both REQs `[BEHAVIOR]` (see the kind-choice rationale under
§ Acceptance Criteria); that tagging is **retained** by operator ruling 2026-07-29 and
is NOT re-litigated here. The residual gap is recorded above in full, so Gate 5 is
given knowingly and accurately.

**What this means for the deliverable.** The doc edits themselves are correct and
reader-visible — ADR-0.0.18 carries seated superseded markers, the concept pages carry
scoped closure admonitions, and `gz-design` Step 5 offers `feature`/`pool`. What is weak
is the *proof channel*, not the artifact: the tests under-detect a hostile future edit,
they do not misreport the present state. Verify the present state by reading the four
surfaces directly (§ Demo commands 4 and 5).

Follow-on: a structural-validator scope giving these doc-closure claims a durable
SUPPORT channel over a parsed Markdown structure. Not in scope here — it is a new
validator surface, not defect repair. Homed as an instance on **GHI #615**
(*"structured governance docs regex-scraped, not schema-enforced"* — the same class),
comment `5115304791`, rather than filed as a sibling-cut duplicate.

**Not a defect (adjudicated).** The same adversary flagged `gz validate --taxonomy
--json` exiting 0 while reporting findings. This is the established repo-wide contract
for EVERY finding type, pinned by `tests/commands/test_validate_cmds.py:726`
(`--json doesn't raise SystemExit`) against the registered `frontmatter` type. Exit 3
is the text-mode path. The brief's § Demo comment was imprecise and has been corrected;
no code change was warranted.

## Human Attestation

- Attestor: `g0`
- Attestation: Attest with the corrected caveat — OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement: gz validate --taxonomy now computes grandfathered-foundation terminality from the Layer-2 foundation_grandfathered ledger event and never from frontmatter, emitting foundation_limbo at exit 3 with three-part recovery prose naming gz closeout / gz adr demote; ADR-0.0.18 is frozen-historic (seated superseded markers, record and Decision text intact); and gz-design Step 5, adr-taxonomy.md and foundation-feature-invariance-test.md all declare the foundation kind CLOSED for gzkit while preserving the adopter carve-out. 18 new tests across tests/test_foundation_limbo_gate.py and tests/test_foundation_doctrine_retirement.py; 7574 unit tests OK; 4/4 REQ @covers parity; four RED witnesses all failure_class=assertion. The gate adds ZERO findings to the 74 pre-existing foundation_kind_closed inherited from OBPI-01. Attested holding THREE independent Codex adversarial REFUTED verdicts (task-ms5gaqdb-6721ed, task-ms5iz3ye-w4z656, task-ms5uezyf-6coaah): pass 1 caught the decisive exit-1-not-exit-3 defect that 7570 green tests had masked, pass 2 caught a ledger crash and a hollow dispatch test, pass 3 caught that my own caveat overstated its closure. All mechanically-fixable refutations were fixed and independently re-verified; the residual REQ-03/04 doc-content proof-channel weakness is recorded verbatim as an accepted-bypass table in the brief's Tracked Defects and homed on GHI #615. Receipts arb-step-unittest-d2bb1e6dbb1e4922af795e855ebe12a1, arb-ruff-6894721afdfc4dd8b8d9b7c4eb5c799b, arb-step-typecheck-6180fce77ca44b96aed3e61f8fcfbe95, arb-step-mkdocs-91e7b8fdebd44fe3aac73978b4fdadfd.
- Date: 2026-07-29

---

**Date Completed:** 2026-07-29

**Evidence Hash:** -
</content>
</invoke>
