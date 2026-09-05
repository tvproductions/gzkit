---
id: OBPI-0.35.0-04-section-ownership-and-ratchet
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 4
lane: Heavy
status: Active
allowlist:
- src/gzkit/content/ownership.py
- src/gzkit/commands/content/unown.py
- src/gzkit/commands/content/__init__.py
- src/gzkit/cli/**
- src/gzkit/schemas/section_ownership.json
- config/doc-coverage.json
- .gzkit/ownership/AGENTS.md.json
- src/gzkit/governance/events.py
- src/gzkit/events.py
- src/gzkit/schemas/ledger.json
- src/gzkit/ontology/corpus.py
- data/ledger_vocabulary_grandfather.json
- tests/test_schemas.py
- src/gzkit/ledger.py
- src/gzkit/commands/validate_cmd.py
- .gitignore
- tests/content/test_ownership.py
- tests/commands/test_content_unown.py
- tests/content/test_tui_affordances.py
- tests/commands/test_validate_ownership_declarations.py
- features/**
- docs/user/manpages/content.md
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md
reqs:
- REQ-0.35.0-04-01
- REQ-0.35.0-04-02
- REQ-0.35.0-04-03
- REQ-0.35.0-04-04
- REQ-0.35.0-04-05
- REQ-0.35.0-04-06
- REQ-0.35.0-04-07
- REQ-0.35.0-04-08
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz cli audit
- uv run mkdocs build --strict
tasks:
  - TASK-0.35.0-04-01-01
  - TASK-0.35.0-04-02-01
  - TASK-0.35.0-04-03-01
  - TASK-0.35.0-04-04-01
  - TASK-0.35.0-04-05-01
  - TASK-0.35.0-04-06-01
  - TASK-0.35.0-04-07-01
  - TASK-0.35.0-04-08-01
  - TASK-0.35.0-04-02-02
  - TASK-0.35.0-04-03-02
  - TASK-0.35.0-04-05-02
  - TASK-0.35.0-04-07-02
  - TASK-0.35.0-04-08-02
---

# OBPI-0.35.0-04-section-ownership-and-ratchet: Section Ownership And Ratchet

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #4 - "Section ownership declaration + decrease-only unowned-byte ratchet + attested ratchet-raise path for un-owning"

**Status:** Draft

## Objective

Declare every AGENTS.md H1/H2 section either `corpus-owned` or `unowned`, record the unowned byte total in a decrease-only ratchet, and gate the only move that raises it — un-owning a section — behind an attested raise-path with the same corpus-attestation shape as gz content withdraw.

> **AMENDED 2026-08-18 (operator-ruled, GHI #822): this brief's content-surface
> attestation is renamed from "Gate 5" to CORPUS ATTESTATION.** Gate 5 names
> OBPI/ADR completion attestation (`ADR-0.0.36`) and nothing else; a build step
> wearing that name is the collision the transit/exchange/handoff fence forbids
> (operator ruling 2026-08-17, `AGENTS.md` § Operator Doctrine). The noun is
> `corpus`, not `rendition`, because the same ruling puts the attestable subject on
> the corpus and holds a rendition to be a Layer-3 derived view, "never the thing
> attested." Parent ADR § Decision carries the governing amendment. This brief's own
> `### Gate 5 (Human)` gate-covenant sections are UNCHANGED — those are the genuine
> Gate 5, on this OBPI's completion. Naming only; no REQ semantics change.

> **AMENDED 2026-09-02 (operator-ruled): the ratchet is measured in SECTION-SPAN BYTES.**
> Operator ruling, verbatim: *"span-based, consistent with REQ-05"*. As authored, this
> brief defined its unit twice and incompatibly. REQ-05 raises the floor "by that
> section's byte count" (a span), while REQ-02/07 quoted 22,378 unowned B and 31.2%
> coverage of 31,990 B — figures computed as (document bytes − corpus-entry TEXT bytes),
> which is not a span and was never distributed across the 14 sections REQ-07 attributed
> it to. Re-measured at the authoring commit (`4738aa69`), the 14 unowned sections spanned
> 11,607 B, not 22,378 B. The ruling settles the unit as span-based; REQ-02, REQ-07 and
> REQ-08 are amended to it, and the corpus-addressed roster is refreshed from 8 sections
> to the measured 10 (`gate-covenant` and
> `operator-economy-of-effort-design-dialogue-mode` were captured after authoring).
> COUPLING NOTE: the parent ADR's § Decision item 4 and § Consequences Positive #4 still
> carry the entry-witness figures (31.2%, 354 B → 22,378 B). Those items are scoped to
> OBPI-0.35.0-05 and -06, not to this brief, and are left for the operator to rule on
> separately rather than amended from inside an OBPI whose allowlist excludes the ADR body.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 04 has no prerequisite inside ADR-0.35.0 and may land in parallel with 01-03. 05 depends on 01 + 04; 06 depends on 04 + 05. Per § Scope Minimization, 04 and 06 are cut together or not at all — cutting 06 alone leaves ownership as a claim with no enforcement, which IS pre-mortem #2.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/content/ownership.py` — ownership declaration model, store, and ratchet **CREATE**
- `src/gzkit/commands/content/unown.py` — the attested ratchet-raise command **CREATE**
- `src/gzkit/commands/content/__init__.py`, `src/gzkit/cli/**` — parser registration for the raise-path verb only
- `src/gzkit/schemas/section_ownership.json` — declaration schema **CREATE**
- `config/doc-coverage.json` — doc-surface exemption entry for the new `content unown`
  verb, matching the identical entry all 11 sibling `content` verbs already carry.
  ADDED 2026-09-02 by operator ruling (Gate Friction escalation): `gz cli audit` is a
  brief-declared verification command, and it fail-closes on the new verb's five doc
  surfaces; the manifest is the coupled surface the brief under-declared at authoring.
- `.gzkit/ownership/AGENTS.md.json` — the day-one declaration and ratchet floor **CREATE**
- `src/gzkit/governance/events.py` — ownership and ratchet ledger events
- `tests/content/test_ownership.py`, `tests/commands/test_content_unown.py` — covering tests **CREATE**
- `tests/content/test_tui_affordances.py` — admit `unown` to the `gz content`
  subcommand fence bound to REQ-0.0.34-05-05. ADDED 2026-09-02 by operator ruling
  ("add to allowed"; Gate Friction escalation, same shape as the
  `config/doc-coverage.json` entry above): the fence pins a hardcoded roster, and
  Task 3's registration of `unown` fail-closes `uv run gz test`, a brief-declared
  verification command. The test's own docstring rules the disposition — *"the
  fence is updated to admit it, not relaxed"* — and six sibling verbs were admitted
  the same way. The fence is the coupled surface this brief under-declared at
  authoring; the roster is widened by one id, never weakened.
- `src/gzkit/commands/validate_cmd.py`, `tests/commands/test_validate_ownership_declarations.py`
  — give REQ-08's SUPPORT proof channel a validator that actually reads the artifact.
  ADDED 2026-09-02 by operator ruling (Gate Friction escalation, same shape as the two
  entries above): Step-4b adversary finding 3 demonstrated that `gz validate --documents`
  never reads `.gzkit/ownership/*.json`, so REQ-08's claim that it *"admits the shape"*
  was satisfied vacuously — a probe carrying malformed ownership JSON returned
  `documents_error_count 0`, and for a window the committed declaration did not validate
  against its own schema while nothing said a word. The operator ruled the repair lives
  here and extends `--documents` rather than adding a new scope flag, so REQ-08's text
  becomes literally true as written. Sibling `OBPI-0.35.0-06-validate-rendition-lineage`
  owns this file too, but its subject is whether rendition text derives from the corpus;
  the declaration's own well-formedness is this brief's artifact, schema and REQ.
- `.gitignore` — ignore the write-discipline sidecars the atomic raise-path creates.
  ADDED 2026-09-02 by operator ruling (Gate Friction escalation, fourth entry of the same
  coupled-surface shape): finding 2's fix stages `<decl>.json.lock`, `.<decl>.json.<rand>.tmp`
  and `<decl>.json.journal` inside `.gzkit/ownership/`, which IS tracked because the day-one
  declaration is committed there. Both Step-4b reviewers graded the omission **major** and
  cited DO IT RIGHT 1a. `.gitignore` already carries the identical precedent for
  `.gzkit/corpus/**/*.lock` and `*.tmp` with a comment stating the same reasoning verbatim,
  and AGENTS.md § Execution Rules mandates `git add -A` before `gz check` — so without this
  the first real `gz content unown` commits ephemeral runtime state into Layer-1 canon's
  own directory. The journal in particular is the crash-recovery record and must never be
  committed.
- `features/**` — Gate 4 scenarios for the attested raise-path
  and the six-line actor-identity correction in `features/obpi_lock.feature` found
  by full verification under Codex (operator's 2026-09-05 "fix everything" direction).
  The latter repairs the fixtures belonging to terminal `OBPI-0.0.14-01`, not the
  production lock contract: holder and requester must be different agents under
  both primary runtimes.
- `docs/user/manpages/content.md` — the raise-path section
- `.github/workflows/ownership-directory-barrier-probe.yml` — TEMPORARY Windows
  capability experiment only. Operator authorization, 2026-09-05, verbatim:
  "fix everything, also what are we going about this OBPI?" This answers the
  explicit request to add, run, and remove this prepared probe. Record its actual
  Windows result, then remove the workflow; this exception does not authorize a
  weaker platform contract or a production durability claim from a capability test.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md` — this brief's evidence sections

## Denied Paths

> **`src/gzkit/ledger.py` is declared in the allowlist but is READ-ONLY here.**
> The covering tests import `Ledger` to arrange and read ownership events, and
> `--brief-reconcile` derives `missing_in_brief` from those test imports, so the
> declaration is what makes the brief honest about its test surface. It does NOT
> license editing the module: the one defect found against it — a non-crash-durable
> `append` (round-4 finding 3) — was ROUTED OUT to GHI #952 by operator ruling
> precisely because the fix changes durability for every event producer in the repo.

- `AGENTS.md` — this OBPI declares ownership OVER sections; it never edits them
- `src/gzkit/content/composer.py` — materialization is OBPI-0.35.0-05
- `src/gzkit/governance/trust_audits/**` — `--rendition-lineage` is OBPI-0.35.0-06; this OBPI ships the declaration and the ratchet, not the gate
- `src/gzkit/content/models/corpus.py` — the corpus model is OBPI-0.35.0-01
- New dependencies, CI files other than the temporary probe explicitly allowed above, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. ALWAYS declare a closed enum. A section's ownership is exactly one of `corpus-owned` or `unowned`. Any third value, or a section present in AGENTS.md with no declaration, is fail-closed — an undeclared section is the silent third state this OBPI exists to remove.
2. DAY-ONE BASELINE — SPAN-BASED (operator-ruled 2026-09-02; re-derived at implementation time, never stored). "Unowned bytes" means the summed BYTE SPAN of the sections declared `unowned`, consistent with REQ-05's *"the ratchet floor RISES by that section's byte count"*. Measured 2026-09-02: AGENTS.md is 46,876 B across 22 H1/H2 sections. TEN sections are corpus-addressed — `attestation`, `behavior-rules`, `defect-fix-routing`, `do-it-right-craftsmanship-maxim`, `gate-covenant`, `governance-doctrine-surfaces`, `obpi-acceptance-protocol`, `operator-doctrine-verbatim-canon`, `operator-economy-of-effort-design-dialogue-mode`, `prime-directive-ownership` — spanning 38,239 B. The remaining 8,637 B across 12 sections is the day-one unowned ratchet floor. Every figure here is ILLUSTRATIVE of the measure and MUST be re-derived at implementation time (`.claude/rules/governance-core.md` — a value written in a Markdown doc is never authoritative).
3. NEVER let the ratchet increase without attestation. Recording an unowned-byte total GREATER than the stored floor MUST be refused. Decrease or equality updates the floor; an increase is only reachable through the attested raise-path.
4. ALWAYS gate the raise-path at the corpus attestation, fail-closed, with the SAME shape as gz content withdraw: empty or whitespace-only `--attestor` or `--reason` exits non-zero and writes nothing. Un-owning a section is the same act on the same kind of canon, so it takes the same ceremony (ADR § Reversibility).
5. ALWAYS emit a ledger event on both moves — an ownership transition and a ratchet-floor change — carrying the section id, the prior and new byte totals, and, on a raise, the attestor and reason.
6. NEVER couple ownership to a section TITLE. Declarations key on the stable kebab-case section id used by the corpus `section` field, so renaming an H2 heading does not silently orphan a declaration (`DESIGN_FORCING_FUNCTIONS.md` § 2 assumption a1).
7. ALWAYS record the coverage figure alongside the ratchet so it can be read without recomputation: owned span over total span, plus the owned-section count out of 22 — measured 2026-09-02 as 38,239 of 46,876 B = 81.6%, 10 of 22 sections.
8. NAMED HONESTLY IN THE BRIEF, NOT MARKETED: the span-based measure INFLATES apparent coverage relative to how much of the contract is actually witnessed, because an owned section's FULL span counts even where a single corpus entry backs it. Four of the ten owned sections (`gate-covenant`, `governance-doctrine-surfaces`, `obpi-acceptance-protocol`, `operator-economy-of-effort-design-dialogue-mode`) carry exactly ONE corpus entry each, and `governance-doctrine-surfaces`'s single entry is `compressible` tier, so it is not on the invariant floor at all. "10 of 22 sections / 81.6%" is functionally six sections plus four tokens (ADR § Consequences Negative #1). The implementation MUST surface the per-section entry-count histogram alongside the percentage, and MUST NOT round, average, or otherwise present the figure as stronger than this.
9. ALWAYS emit three-part recovery prose on every fail-closed exit per `.claude/rules/guardrail-feedback-prose.md`.
10. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- [ ] `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/DESIGN_FORCING_FUNCTIONS.md` — pre-mortem, WWHTBT, constraint archaeology, 2am-operator, reversibility, scope minimization.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — the three-kind proof-channel matrix this brief's Acceptance Criteria are tagged against

**Context:**

- [ ] ADR § Decision item 3 — ownership plus decrease-only ratchet, and the attested raise-path.
- [ ] ADR § Consequences (Negative) #1, #2 and #4 — thin coverage, the ratchet's missing forcing function, and owned-section fail-closed becoming the thing agents route around.
- [ ] `DESIGN_FORCING_FUNCTIONS.md` § 1 pre-mortem #1 and #2, and § 6 Reversibility — the raise-path exists because the undefined reversal path is the one agents invent.
- [ ] `DESIGN_FORCING_FUNCTIONS.md` § 4 — ownership is declared surface-wide but materialization is per-consumer; that looseness is deliberate and is resolved in the OBPI-0.35.0-05 lineage map.

**Prerequisites (check existence, STOP if missing):**

- [ ] `AGENTS.md` present; 22 H1/H2 headings and 31,990 B re-measured at implementation time
- [ ] `.gzkit/corpus/AGENTS.md.jsonl` present; the eight corpus-addressed section ids re-derived at implementation time
- [ ] `src/gzkit/governance/events.py` exists and carries the emit-helper pattern
- [ ] `src/gzkit/commands/content/commit.py` exists (the corpus-attestation fail-closed pattern the raise-path mirrors)
- [ ] `docs/user/manpages/content.md` exists

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/models/corpus.py:43` — `section: str` is flat and `anchor: str | None` is largely unused; ownership is declared at a granularity the model supports only weakly
- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:87-91` — the staged-warn precedent, and `_checkpoint.resolve`'s hangar downgrade; the in-repo evidence for pre-mortem #2
- [ ] `src/gzkit/commands/content/commit.py:88-117` — the corpus-attestation shape to mirror (re-seated by GHI #821; was 47-54). Mirror the FAIL-CLOSED arm: un-owning a section is a canon change, so it never reaches the unchanged-canon exemption

## Quality Gates

<!-- Which gates apply and how to verify them. -->

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

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. -->

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content unown --help
uv run python -c "import subprocess, sys, pathlib; d = pathlib.Path('.gzkit/ownership/AGENTS.md.json'); before = d.read_bytes(); r = subprocess.run(['uv','run','gz','content','unown','AGENTS.md','--section','attestation','--attestor','','--reason','probe'], capture_output=True, text=True); sys.exit(0 if r.returncode != 0 and d.read_bytes() == before else 1)"
uv run python -c "import json, pathlib; from gzkit.content.models import Corpus; from gzkit.content.ownership import compute_baseline; d = json.loads(pathlib.Path('.gzkit/ownership/AGENTS.md.json').read_text(encoding='utf-8')); corpus = Corpus.loads(pathlib.Path('.gzkit/corpus/AGENTS.md.jsonl').read_text(encoding='utf-8')); b = compute_baseline(pathlib.Path('AGENTS.md').read_text(encoding='utf-8'), corpus); print('owned', sum(1 for v in d['sections'].values() if v == 'corpus-owned'), '| unowned floor', d['unowned_byte_floor'], '| coverage', b.coverage_pct)"
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-04-01 [behavior]: Given a section declaration whose value is neither `corpus-owned` nor `unowned`, or an AGENTS.md section with no declaration at all, when the ownership store is loaded, then it fails closed naming the offending section id — there is no undeclared third state.
- [ ] REQ-0.35.0-04-02 [behavior]: Given a stored unowned-byte floor of N, when a recorded total greater than N is submitted through the ordinary (unattested) path, then the update is REFUSED and the stored floor is unchanged — the ratchet is decrease-only.
- [ ] REQ-0.35.0-04-03 [behavior]: Given a stored floor of N, when a recorded total less than or equal to N is submitted, then the floor is updated to the new total and a ratchet ledger event is emitted carrying the prior and new values.
- [ ] REQ-0.35.0-04-04 [behavior]: Given the attested raise-path invoked with an empty or whitespace-only `--attestor` or `--reason`, when it runs, then it exits non-zero, the ownership declaration and ratchet floor are byte-unchanged, and no ledger event is written.
- [ ] REQ-0.35.0-04-05 [behavior]: Given the attested raise-path invoked with a non-empty attestor and reason against a `corpus-owned` section, when it runs, then the section becomes `unowned`, the ratchet floor RISES by that section's byte count, and a ledger event records the section id, both floor values, the attestor, and the reason.
- [ ] REQ-0.35.0-04-06 [behavior]: Given an AGENTS.md whose H2 heading TEXT changed while its kebab-case section id is unchanged, when the ownership store is loaded, then the declaration still resolves — ownership keys on the id, never on the title.
- [ ] REQ-0.35.0-04-07 [behavior]: Given the day-one AGENTS.md and corpus, when the baseline is computed, then it reports the owned-section count, the summed BYTE SPAN of the `unowned` sections, and coverage as owned-span over total-span — every figure derived by measurement at run time, never read from a stored constant. (Span-based per the operator ruling of 2026-09-02; measured that day as 10 owned sections, 8,637 unowned B across 12 sections, 81.6% of 46,876 B.)
- [ ] REQ-0.35.0-04-08 [support]: The day-one declaration at `.gzkit/ownership/AGENTS.md.json` is present and validates against `src/gzkit/schemas/section_ownership.json` — witnessed by an `artifact_edited` ledger event citing `.gzkit/ownership/AGENTS.md.json` — and `gz validate --documents` admits the shape.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

**Executed mutation sweep — 18 guards, all witnessed.** Each row deletes ONE
guard from `src/gzkit/commands/content/unown.py` in isolation, runs only that
guard's named test, and restores the file. Base
`sha256 a4c2e3ad45e3e0ffff9941b5dcbe0aac71141308da60365e69971eedbfe93500`; every mutation ran AFTER `uv run ruff format .` and the file was
verified byte-identical to that SHA after each restore.

| Guard deleted | Named test's observed failure |
|---|---|
| G1 fresh-path snapshot identity check | `AssertionError: 2 != 1 : Error: the witness source declaration declares identity 'doc.md', but this transaction's target is 'Doc.md' ('/private/var/fo` |
| G2 unlanded-branch snapshot identity check | `AssertionError: 'the on-disk predecessor declares identity' not found in "Error: the landed declaration declares identity 'Other.md', but this transac` |
| G3 landed-branch snapshot identity check | `AssertionError: 'the landed declaration declares identity' not found in "Error: the witness source declaration declares identity 'Other.md', but this` |
| G4 witness-site identity check | `AssertionError: SystemExit not raised` |
| G5 witness-site transition validation | `AssertionError: SystemExit not raised` |
| G6 entry different-file refusal | `AssertionError: 0 == 0 : Un-owned section 'alpha-section' of 'Doc.md'. Unowned-byte floor rose from 26 to 83 (+57 B). Attested by g0: probe` |
| G7 entry missing-file arm | `AssertionError: 'does not exist' not found in 'Error: surface \'Missing.md\' does not resolve to the identity its ownership declaration declares: the` |
| G8 _declared_surface fail-closed posture | `AssertionError: OSError not raised` |
| G9 journal-identity check | `AssertionError: 0 != 2 : Completed the interrupted un-owning of section 'alpha-section' of 'Doc.md'. Unowned-byte floor rose from 26 to 83. Attested b` |
| G10 pre-commit recheck raw-byte digest | `AssertionError: 2 != 1 : the recheck must refuse BEFORE either store is touched; exit 2 means the transition already landed. Error: surface 'Doc.md' c` |
| G11 fresh-commit finalization digest guard | `AssertionError: 0 == 0 : the command must not report clean success when the surface moved inside the transaction. Un-owned section 'alpha-section' of` |
| G12 replay finalization digest guard | `AssertionError: 0 == 0 : replay must not report clean recovery after the journalled surface changed. Completed the interrupted un-owning of section 'a` |
| G13 alias canonicalization arm | `AssertionError: 1 != 0 : Error: the loaded declaration declares identity 'Doc.md', but this transaction's target is 'doc.md' ('/private/var/folders/7y` |
| G14 next-step omits a declaration hand-edit | `` AssertionError: '  Re[66 chars]or "<your name>" --reason "<why>"`, or repair the declaration.' != '  Re[66 chars]or "<your name>" --reason "<why>"`.' `` |
| G15 replay read-failure reported as a read failure | `AssertionError: 'cannot read the ownership declaration' not found in "Error: the on-disk predecessor declares identity None, but this transaction's ta` |
| G16 refusal exit code / residue pairing | `AssertionError: 2 != 1 : Error: the loaded declaration declares identity 'doc.md', but this transaction's target is 'Doc.md' ('/private/var/folders/7y` |
| G17 recovery-witness fixture sanity | `AssertionError: 0 != 1 : fixture sanity: this invocation must have completed the pending transition, or there is no durable change to contradict. Comp` |
| G18 forged-journal next step omits a hand-edit | `AssertionError: 'by hand' unexpectedly found in "Error: the pending-transition journal '/private/var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpt1` |

**What this sweep does NOT establish — two limits, stated because a sweep reads
as stronger than it is.**

1. **Each mutation runs only its ONE named test.** A row therefore proves *"this
   test witnesses this guard"*. It never proves *"no other test depended on that
   guard"*, and it never proves the guard is the only thing standing between the
   defect and the operator. Four of the identity checks demonstrably overlap:
   deleting any one still leaves a sibling refusing the same fixture, visible in
   the G1/G2/G3 messages, where the refusal that arrives names a *different*
   phase than the test pinned. Those tests remain guards for their own checks
   only because each pins its phase string.
2. **This is a mutation sweep, NOT an adversarial acceptance verdict.** It says
   the tests are sensitive to the code they name. It says nothing about whether
   the design is right, whether the threat model is correctly drawn, or whether
   an unmodelled attack exists. Step 4b remains the arm that answers those.

**A harness defect found while running it — and it cuts both ways.** Two
mutations that delete byte-identical text produce files of the SAME SIZE, and
CPython invalidates source caches on `(mtime-seconds, size)`. Back-to-back
mutations therefore collide and the second subprocess imports the FIRST
mutation's bytecode. Measured on G11/G12: G12 reported `PASSED — VACUOUS` inside
the sweep and `FAIL` in isolation, reproducibly, twice.

The contamination is **not** biased toward false PASSes. An observed FAILURE
could equally be a prior mutation's code state rather than the one the row
names — the subprocess simply runs whichever bytecode the cache retained, and a
neighbouring mutation's tree can fail a test just as easily as it can pass one.
Every row in an affected run is suspect in both directions, which is why no row
above is carried over from a pre-fix run.

The fix is a private `PYTHONPYCACHEPREFIX` per iteration, applied
**unconditionally** to every mutation rather than only to the colliding pair, so
no row in the table above retains the collision. The whole sweep was re-run from
scratch under the fix.

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

Before this OBPI, gzkit asserted an invariant floor over ALL of `AGENTS.md` while
verifying it over none of it: which sections the corpus actually backs was silence,
not a fact. This ships the closed-enum ownership declaration, the decrease-only
unowned-byte ratchet, and the attested `gz content unown` raise-path — so "how much
of the contract is witnessed" becomes an explicit, fail-closed, ledger-anchored
number instead of an assumption.

The measure is named honestly rather than marketed (REQ-08): span-based coverage
INFLATES apparent witnessing, because an owned section's full byte span counts even
where a single corpus entry backs it. Four of the ten owned sections carry exactly
one entry, and one of those is `compressible` tier — so "10 of 22 sections" is
functionally six sections plus four tokens.

### Key Proof

Three rounds of tier-1 cross-vendor adversarial review drove the design. The
load-bearing repair is that a ratchet floor is now witnessed by a ledger STATE, never
by a declaration agreeing with itself:

```
$ uv run python /tmp/probe_v2.py      # scratch root holding the REAL ledger
control (unmodified)       : ACCEPTED      <- no false positive on the real tree
attack A (flip+recompute)  : REFUSED       <- the originally reproduced attack
attack B (flip, keep floor): REFUSED       <- caught by span coherence alone
legit shrink (sum < floor) : ACCEPTED      <- proves the relation is <=, not ==
```

Attack B refuses citing REQ-0.35.0-04-02: *"the true unowned span may legitimately
sit BELOW the stored floor (a surface shrink before the next ratchet recording), but
it may never sit above."* Before the repair, attack A loaded cleanly with no ledger
file in existence (floor 8637 -> 10182).

Full suite 9259 tests green, receipt `arb-step-unittest-824691c6b184421ea828cfab16abe9bb`;
lint `arb-ruff-0381d7a4a04d46d3a971cb2d692fb646`; typecheck
`arb-step-typecheck-31f339cc29ac42c5a5b7de515d093ea3`; docs
`arb-step-mkdocs-13bcc36cf24c404bace5f68390fa061a`.

### Implementation Summary

- Files created/modified: `src/gzkit/content/ownership.py` (uniform ledger-anchored
  load path; null `floor_event_id` refused; event type + surface + floor checks;
  always-on `unowned span <= stored floor`; parent-directory fsync after
  `os.replace`), `src/gzkit/commands/content/unown.py` (journal replay hardened —
  re-mint, on-disk predecessor continuity, real measured span, `corpus-owned`
  eligibility, derived-not-verbatim successor write, `NoReturn` refusal helper),
  `src/gzkit/governance/events.py` + `src/gzkit/events.py` + `src/gzkit/schemas/ledger.json`
  + `src/gzkit/ontology/corpus.py` (three ownership event types registered across
  schema, typed-model union, and ontology disposition),
  `src/gzkit/schemas/section_ownership.json`, `.gzkit/ownership/AGENTS.md.json`
  (repointed to genesis event `section-ownership-genesis-AGENTS.md-8632cf1aa340695d`).
- Tests added: `TestLoadDeclarationChainValidation` (5), `TestContentUnownReplayJournalValidation` (7),
  `TestSectionOwnershipSchema`, `TestCommittedDeclarationLoadsCleanly`, directory-fsync durability test.
- Negative controls: all six replay checks and the durability barrier were each
  deleted in isolation and their named test observed to FAIL, then restored — the
  tests are guards, not decoration.
- Date completed: 2026-09-03
- Attestation status: operator-attested (Gate 5)
- Defects noted: see Tracked Defects — one accepted residual (coordinated
  declaration+journal edit) and one deferred architectural item (OBPI-0.35.0-05).

### Step 4b — Independent Adversarial Validation

**Verdict: REFUTED / `CORROBORATION: NOT-CORROBORATED` (round 11, the STANDING verdict).
Receipt `arb-step-codexadversary-cc9aa913064b4550807e717c51982f4b`, `exit_status: 0`,
duration 925s, `stdout_truncated: False`, no failure markers. ONE HIGH and TWO MEDIUM
in-scope findings, no critical — recorded at § Round 11. **Round 10's two high findings are
DISCHARGED**; the high in round 11 is a NEW consequence of the D-beats-E correction.

Round 10 is SUPERSEDED as the standing verdict. Its receipt was
`arb-step-codexadversary-658c8ce606114de39730cd01a66e5f3d`, `exit_status: 0`,
commit `397301c6` + the fixed-target working tree, dispatched 2026-09-05, duration 689s;
log grepped for `Turn failed` / `Codex error` / `flagged for possible` / content-filter
markers and carries NONE; `stdout_truncated` is `False`. **TWO HIGH in-scope findings, no
critical, no medium** — both on a NEW root (recovery durability), recorded at § Round 10.
**Round 9's root is CLOSED**: round 10 positively demonstrated the fixed-target correction
holding across fresh, CRLF, unlanded-replay and landed-replay.

Round 9 is SUPERSEDED as the standing verdict. Its receipt was
`arb-step-codexadversary-dd8d6bbcb51c4f4a8d1042687a90964b`, `exit_status: 0`,
commit `397301c6`, dispatched 2026-09-05T06:18:06Z; the log was grepped for `Turn failed` /
`Codex error` / `flagged for possible` / content-filter markers and carries none, and
`stdout_truncated` is `False`.** Round 9 returned ONE high and THREE medium findings, no
critical, all in scope. It is recorded in full at § Round 9 below.

**Round 8 is SUPERSEDED as the standing verdict.** Its receipt was
`arb-step-codexadversary-9a16acc9764848088cfa9130a98db71b`, `exit_status: 0`, commit
`b5138874`, dispatched 2026-09-04T01:54:35Z; it returned two high and one medium finding,
ALL in scope, and all three are FIXED at `a90a8d14` with mutation-verified tests. Round 9
re-derived those three fixes independently and confirmed each — see § Round 9.

**THAT GAP IS NOW CLOSED — ROUND 9 OBSERVED THE CURRENT TREE.** Until 2026-09-05 no
adversary round had: `a90a8d14` is the last commit touching
`src/gzkit/commands/content/unown.py` and it landed *after* round 8 observed the tree, so
the standing verdict described a tree that no longer existed. Round 9 ran against commit
`397301c6` and independently re-derived all three of round 8's fixes. It did NOT converge
the gate — it found a new high — but the discharge of round 8 is no longer uncorroborated.
Round 8 additionally **ran in a read-only sandbox**
(*"The writable CLI suite could not run because the sandbox has no writable temporary
directory"*), so it could execute neither the failure/concurrency matrix nor the mutation
sweep and found its three defects by reading. Its NOT-CORROBORATED is therefore partly a
coverage limit — and a CORROBORATED from that environment would have been equally weak.
This is the GHI #941 shape: **resolve the writable-workspace problem, or rule that a round
without it is acceptable, before dispatching round 9.**

Round 6's two criticals remain NOT fixed here: both root in `Ledger.append`, which this
brief's § Denied Paths declares read-only, and both are ROUTED OUT to **GHI #953** on the
precedent set when round-4 finding 3 was routed to GHI #952.

**This completion is therefore made WITH THE REFUTATION RECORDED, never dressed as clean.**
The claim in § Threat Model is amended below to be bounded by the ledger's transaction
semantics, because round 6 proved the unamended claim FALSE within this brief's own scope:
a crash leaving a truncated final ledger row does leave the ownership state unrecoverable.
Recording the refutation and amending the claim is the honest disposition; completing
against the old claim would have asserted something a tier-1 adversary disproved.

**A CONVERGENCE RULE NOW GOVERNS THIS GATE (operator ruling 2026-09-03).** Step 4b converges
when a round returns NO critical and NO high findings; medium and below are disclosed in
Tracked Defects or routed to a GHI, never silently. *"Clean adversary or we cannot pass"*
against an adversary instructed to REFUTE is unbounded by construction. Measured here: five
rounds, 53 minutes of adversary compute across a 12.5-hour wall clock — 7%. The rest was fix
cycles. A second rule accompanies it: when a round's *Weakest point* names the SAME ROOT as
the prior round, STOP dispatching and bring the design decision to the operator. Rounds 2, 3
and 4 each patched a different surfacing of one root cause at roughly 3h per cycle; the
operator ruled round 4's design in a single exchange and it closed in one pass.

**Eleven rounds ran.** Each round's findings were repaired before the next was dispatched, so
every round re-ran against a repaired tree. **ROUND 11 IS THE VERDICT THAT STANDS** — rounds
1-10 are recorded below as history, and their verdicts describe trees that no longer exist.
This section states that explicitly because `gz obpi precomplete` reads the section for a
standing verdict and cannot infer supersession from prose. Round 9 is the FIRST round whose
verdict describes the tree as it currently is.

**Rounds 1-6 were prompted to REFUTE; rounds 7, 8 and 9 were prompted to CORROBORATE.** That
wording changed mid-gate on an operator ruling (2026-09-04) and the change is load-bearing,
not cosmetic — a model told *"your job is to REFUTE this, not to confirm it"* escalates until
something falls, and its best available outcome is *"I could not refute it"*, which is absence
of evidence rather than confirmation. Rounds 7 and 8 carry a `CORROBORATION:` line for that
reason; `NOT-CORROBORATED` is the corroboration-framed statement of the same refusal, and
`not-refuted` is the CLI enum's passive phrasing of the corroborated state. Round 7 is the
first round in this gate's history to produce genuine positive corroboration — see its
record below. Do NOT reuse a rounds-1-6 prompt; build round 9's from the four-part
Purpose / Method / Boundary / Pass condition block at the head of
`.gzkit/skills/gz-obpi-pipeline/SKILL.md` § Step 4b.

Adversary for every round: Codex, tier 1 cross-vendor, dispatched through the `openai-codex`
plugin runtime (`codex-companion.mjs adversarial-review --wait`), ARB-wrapped. Rounds 1-5 ran
`--scope working-tree` against a dirty tree; rounds 6-8 ran `--scope branch --base 5108d7cf`,
because the tree is now clean and working-tree would have shown the adversary nothing. Tier-1
readiness was confirmed BEFORE each dispatch (`ready: true`, runtime mode `direct`, no stale
broker), so tiers 2 and 3 were forbidden throughout. Every receipt cited in this section was
re-verified against Layer 2 on 2026-09-04: `exit_status: 0`, `stdout_truncated: False`, the
`step.command` invoking `node .../codex-companion.mjs` (which is what PROVES tier 1 — a vendor
named only in the prompt does not), and no `Turn failed` / `Codex error` /
`flagged for possible` / content-filter marker in either stream.

> **EVIDENCE-PROVENANCE CAVEAT — every guard in rounds 6, 7 and 8, and every one of the ten
> mutation verifications, was proven on macOS ONLY.** `tests/content/test_ownership.py`
> imported `fcntl` at module scope, so on `windows-latest` the file failed to IMPORT and all
> 69 of its tests were *absent*, not skipped — a zero-collection that reads identically to a
> green run in a summary line. The production lock was never broken
> (`corpus_store.py:140` guards its POSIX branch correctly); only the EVIDENCE was missing.
> Fixed under **GHI #955** at `de9a3cf9`. **Read any pre-`de9a3cf9` green in this section as
> macOS-only.** First Windows-inclusive green for this OBPI's guards: CI run `33866911329`
> (2026-09-04), both `check (ubuntu-latest)` and `check (windows-latest)` passing, after
> `98f2827e` skipped two directory-fsync fault-injection tests whose faults the POSIX-only
> barrier means Windows never reaches.

**Round 2's four findings, dispositioned:**

| # | Severity | Finding | Disposition |
|---|---|---|---|
| 1 | high | Genesis had no provenance anchor | **FIXED.** Operator ruled 2026-09-03: anchor genesis to a `section_ownership_genesis` ledger event and forbid a null `floor_event_id` outright. The genesis branch is deleted; the loader has ONE uniform path. Reproduced attack now refuses. |
| 2 | high | Journal replay was an unvalidated arbitrary declaration write | **FIXED.** Six independent checks; the successor is re-derived from the on-disk predecessor and the journal's own `declaration_json` bytes never reach disk. Independent spec review additionally caught that the eligibility check was missing entirely and that four tests were refused by a different check than the one they named; both repaired. |
| 3 | medium | `record_unowned_total`'s two-store transaction is not recoverable | **DEFERRED, disclosed** — and the deferral was subsequently RULED DEFENSIBLE by round 3 (see below). |
| 4 | medium | No directory fsync after `os.replace` | **FIXED**, with a proven negative control (barrier removed -> `no directory was fsynced`). |

**Round 3a — a cut-off run, retained as a worked example, NOT a witness.** Receipt
`arb-step-codexadversary-9631113ec5f44bb4bf64e1fe38cecd46` records `exit_status: 1`: the run
terminated on an upstream content filter (*"This content was flagged for possible cybersecurity
risk"*, `Turn failed`) after completing substantive analysis. Its summary line read "No material
findings" and was very nearly read as a pass, while its own body carried a real finding above
the cut. It does NOT meet the exit-0 bar for a tier-1 claim and is not counted as a round.
Its finding — the coordinated declaration+journal edit — was carried forward, ruled on by the
operator, and is recorded in Tracked Defects as an accepted residual.

**Round 3 — REFUTED, superseded.** Receipt
`arb-step-codexadversary-209abafb666f4572ae68ab464d0a99fe`, `exit_status: 0`, 2026-09-03T06:30:47Z.
One critical and three high findings, ALL FOUR NOW REPAIRED:

| # | Severity | Finding (adversary's own words, abridged) | Disposition |
|---|---|---|---|
| 1 | critical | "A permitted decrease-event type can raise the floor without the governed command." A probe emitted `unowned_ratchet_updated` with `prior=26, new=83` and observed `floor_raised=True, load=ACCEPTED, ledger_validation_errors=0`. | **FIXED** in `779ff0ba`. Each event type is now held to the transition it can witness. `section_ownership_genesis` is deliberately exempt (it records no prior floor and asserts no direction), carried by the missing-`prior` guard rather than the type dispatch — its negative control needed BOTH exemption paths defeated to fail. |
| 2 | high | "Ratchet slack permits an unledgered corpus-owned-to-unowned reversal." Floor 83, unowned sum 26; flipping `alpha-section` gave `after_unowned_sum=83, after_load=unowned, floor_event_id_unchanged=True`, ledger count 1 before and 1 after. | **FIXED** in `779ff0ba`, by the adversary's own recommendation: a canonical digest of the whole section map is bound to every ownership event and re-derived by the loader from the declaration. The `<=` relation the legitimate-shrink case needs is preserved. The digest lives ONLY on the event — a copy stored beside the sections it summarizes would be a second source of truth that can disagree with itself. |
| 3 | high | "A post-replace directory-fsync failure deletes the recovery journal after changing state." Injected fourth-fsync failure gave `exit=2, alpha_state=unowned, floor_changed=True, ownership_event_count=0, journal_exists=False, post_failure_load=REJECTED`, while the command printed `Nothing written` and `the declaration is byte-unchanged`. | **FIXED** in `0488f8f4`. A regression this session introduced with the round-2 finding-4 fsync repair, and reachable by plain failing media with no adversary involved. The journal is now retained on any declaration-write `OSError`, and the prose no longer asserts a premise it cannot know. |
| 4 | high | "Already-landed recovery bypasses live-state validation and clears the journal on an invalid state." After an injected ledger-append failure, expanding the section before retry gave `retry_exit=0, journal_exists_after_retry=False, ownership_event_count=1`, then `post_retry_load=REJECTED`. | **FIXED** in `0488f8f4`. A coherence gate now runs on BOTH branches and fails closed, retaining the journal. `_replay_pending_transition` crossed the xenon C ceiling under these additions, so its validation half was extracted as `_apply_unlanded_transition`. |

Round 3 also answered two questions carried into it, and both answers are recorded rather than
paraphrased away:

- **The round-2 finding-3 deferral is defensible.** Verbatim: *"The two accepted residuals still
  reason correctly: (a) `record_unowned_total` can leave an unrecoverable declaration/ledger gap,
  but has no production caller and is deferred to OBPI-0.35.0-05."* An earlier reading of this
  session recorded the deferral question as unanswered; that was a conflation with round 3a,
  which was cut off. Round 3 answered it.
- **What `_mint_event_id` establishes.** Verbatim: *"Recomputing `_mint_event_id` proves only
  that the journal is internally consistent with its own surface, section, floors, attestor,
  reason, and parent. It does not prove the command ran, authenticate provenance, corroborate
  those values against live state, or prove the measured span."* It further observed that
  `parent_event_id` is omitted from the final ledger row, so ledger-only recomputation is
  unavailable afterward.

Round 3 confirmed one guard was real by mutation rather than by inspection: *"after an in-memory
AST mutation removed exactly one prior-floor comparison, it failed with `AssertionError: 0 != 2`
... That test is a real guard, not an any-rejection false positive."*

**Round 4 (this round) — REFUTED. THIS IS THE STANDING VERDICT.** Receipt
`arb-step-codexadversary-54fac48a53cc46d8b31595036399df08`, `exit_status: 0`. The run
completed cleanly: the log carries no `Turn failed`, no `Codex error`, and no content-filter
termination, so unlike round 3a this receipt DOES meet the exit-0 bar for a tier-1 claim.

Three NEW findings, one critical and two high. None of them is the accepted
declaration+journal residual — the adversary says so explicitly: *"The findings above are
distinct: they allow false provenance or destroy recoverability outside that accepted
two-file coherent-edit case."* All three are OPEN.

| # | Severity | Finding (adversary's own words, abridged) | Status |
|---|---|---|---|
| 1 | critical | "Transition direction is self-certified instead of chained to the real predecessor" (`src/gzkit/content/ownership.py:363-433`). The loader checks only the event's CLAIMED `prior` and `new`; it never verifies `prior_unowned_byte_floor` against the preceding ledger state, and genesis is not restricted to the first ownership event for a surface. A real raise 18 -> 38 was accepted by claiming the fictitious decrease 138 -> 38: `actual_previous_floor=18`, `accepted_claimed_transition=138 -> 38`, `actual_floor_rose=True`, `ledger_schema_errors=[]`, `attestor_present=False`, `reason_present=False`. A LATE genesis is also accepted as a fresh baseline (`late_genesis_load=late-genesis`, `late_genesis_has_attestor=False`), and the missing-`prior` guard is reachable by non-genesis events. | **FIXED** in `565ab200`. Operator ruled the design 2026-09-03: chain by WALKING the ledger (no schema change), and seat genesis as a root with a distinct re-anchoring event type. `_refuse_unchained_witness` reads the surface's ownership chain and holds each row to it — genesis at position 0, every other type with something beneath it, a claimed prior floor equal to the real predecessor's new floor, and a named predecessor that is the actual one. The missing-`prior` exemption is scoped to genesis alone. `section_ownership_reanchored` is registered across all four registries; AGENTS.md is re-anchored onto it at an unchanged floor of 8637. Negative control: removing the guard fails both named chain tests; restoring passes. |
| 2 | high | "Already-landed replay can write a digest for the wrong map and destroy recovery state" (`src/gzkit/commands/content/unown.py:401-456`). The shared coherence gate checks only `landed_floor` and `live_unowned_span`; `_append_event_once` hashes `record['declaration_json']` rather than the declaration on disk, and `_mint_event_id` omits both `declaration_json` and the map, so a changed-but-valid journal map passes id recomputation. Observed: `journal_unlinked=True`, disk digest `380c4e7a...`, ledger digest `a21473dc...`, then `post_replay_loader=REJECTED`. | **FIXED**. The coherence gate now compares the journal successor's section map against the declaration ACTUALLY ON DISK and fails closed retaining the journal, and `_append_event_once` derives the emitted `sections_digest` from the landed declaration rather than from the journal's claimed one — so a witness can no longer describe a map that never landed. `_refuse_incoherent_landed_state` was extracted when the additions pushed `_replay_pending_transition` back to xenon rank D. Negative control: neutering the map arm reproduces `0 == 0 : a journal whose map disagrees with the landed declaration must fail closed`. |
| 3 | high | "Recovery journal is cleared before the ledger witness is durable" (`src/gzkit/commands/content/unown.py:521-542`). `Ledger.append` writes and flushes the Python stream but never fsyncs: `Ledger.append_has_fsync=False`. A power loss can preserve the already-fsynced declaration and the journal deletion while losing the buffered ledger row, leaving a new floor whose witness AND recovery journal are both absent. | **ROUTED OUT** to GHI #952 (operator ruling 2026-09-03) — the ledger module is outside this brief's allowlist and the fix changes durability for every event producer in the repo, not just the ownership path. |

**Round 4 CONFIRMED the round-3 repairs it was asked to attack.** These are recorded because a
later round must not re-derive them:

- The map-digest binding works and does not over-refuse: `slack_control=ACCEPTED`,
  `slack_flip=REJECTED` for digest mismatch, `legitimate_shrink=ACCEPTED`, and both
  `digest_absent` and `digest_null` `REJECTED`. Verbatim: *"The map digest itself correctly
  closes the ratchet-slack edit while preserving legitimate surface shrink; `<=` remains the
  correct relation."* Ordering was stable and separator/whitespace/Unicode variants produced
  distinct digests; no canonicalization ambiguity was found.
- The post-swap `OSError` repair (round-3 finding 3) held: `exit_code=2`,
  `journal_unlink_called=False`, `says_journal_retained=True`, `claims_nothing_written=False`.
- Two guards were proven real BY MUTATION, not inspection: deleting
  `_refuse_unwitnessed_section_map(...)` turned its named test `PASS -> FAIL: OwnershipLoadError
  not raised`; deleting `_refuse_wrong_direction_witness(...)` turned its named test
  `PASS -> FAIL: 'decrease-only' not found`.

**Round 4 answered REQ-0.35.0-04-02's open wording question, and the answer is against us.**
Verbatim: *"REQ-0.35.0-04-02's absolute 'increase is only reachable through the attested
raise-path' is literally false: the loader accepts schema-valid ledger witnesses whose claimed
predecessor is fabricated, and accepts later genesis rows as fresh baselines."* The question was
deliberately held open across two rounds so a clean adversary could rule on it rather than the
REQ being narrowed to make a gate pass. It has ruled: the gap is in the CODE, not the wording.

**Three caveats on round 4's own evidence, recorded rather than suppressed:**

1. **Its canonical execution was environment-blocked.** Verbatim: *"`uv run` exited 2 because
   its cache/temp paths were read-only. Direct targeted unittest execution likewise produced
   four setup errors: `FileNotFoundError: No usable temporary directory`."* It fell back to
   read-only in-memory probes and the installed `.venv` entrypoint. Its findings carry concrete
   observed output, but they were not produced through the canonical runner.
2. **`gz validate --ledger` is VACUOUS for both transition types.** Live counts were
   `genesis=2, ratchet-updated=0, unowned=0`, so `--ledger` exercises only genesis, and
   `--event-schemas` proves discriminator-name parity rather than transition semantics. This is
   the mechanical counterpart of the never-fired disclosure already recorded in
   `data/ledger_vocabulary_grandfather.json`.
3. **The any-rejection helper was NOT eliminated.** `_assert_refused_and_untouched` still exists
   at `tests/content/test_ownership.py:848`; of its eight call sites, three (1062, 1088, 1118)
   pin no defect message. The adversary allows that those three "currently have independent
   exit-code or follow-up assertions," but states plainly that *"the requested 'no such helper
   remains' condition is not met."*

**The two carried-forward residuals were re-affirmed.** (a) The round-2 finding-3 deferral is
*"defensible as a sequencing decision because repository search found no production caller —
only tests — and OBPI-0.35.0-05 is explicitly required to lift the shared journal before
activating the path. It is not defensible after any production caller is connected."* (b) The
coordinated declaration+journal residual *"holds within its exact trust-boundary premise."*

**Weakest point (verbatim):** *"provenance is inferred from a witness's internally
self-consistent claims instead of being chained to the preceding ledger state; the gate still
confuses a plausible record with proof of the governed transition."*

**Round 5 — REFUTED, all five findings DISCHARGED.** Receipt
`arb-step-codexadversary-93c85d5b7ab44fcf8bd2ea90d6495fd3`, `exit_status: 0`. Two critical,
two high, one medium. Its weakest point named the SAME ROOT as round 4 one layer deeper —
*"`_refuse_unchained_witness` is called a ledger walk, but it validates one edge. Everything
behind that edge — including this repository's acknowledged second genesis — is trusted
without replay."* That repetition triggered the escalation rule, so the design went to the
operator rather than into another fix cycle.

**Operator design ruling 2026-09-03**, three parts: replay the COMPLETE prefix from genesis
(rejected: caching the verdict; keeping terminal-edge and disclosing the gap); constrain a
re-anchor to MIGRATION-ONLY, floor and map both unchanged (rejected: adding attestor/reason
instead; allowing an attested floor change, which would be a second raise-path alongside
`gz content unown`); and treat later genesis rows as INERT rather than illegitimate
(rejected: rejecting such chains outright, which strands the committed `AGENTS.md`
permanently; a third first-class supersession event).

| # | Severity | Finding (adversary's own words, abridged) | Disposition |
|---|---|---|---|
| 1 | critical | "The ledger 'walk' validates only the terminal edge." Root 0, a middle claiming `100 -> 50`, a tail claiming `50 -> 40` gave `load=ACCEPTED floor=40`, `net_unattested_raise=0->40`, `unique_ids=True`. An invalid middle laundered by appending one locally-consistent tail. | **FIXED.** `_refuse_broken_prefix` replays every edge from the root. Negative control: reverting the loop to the terminal edge alone reproduces the laundering and fails the named test. |
| 2 | critical | "Re-anchor is an unconstrained, unattested ownership-change path." `load=ACCEPTED floor=12 alpha=unowned`, `attestor_present=False` — ownership changed and the floor rose 0->12 with no `gz content unown`. | **FIXED.** A hole this OBPI INTRODUCED while closing round 4's. `_refuse_non_migration_reanchor` requires floor unchanged and map unchanged. The map arm is deliberately vacuous when the predecessor records no digest — that vacuum IS the migration the type exists for. |
| 3 | high | "Existing same-id witness bypasses landed-map binding and consumes recovery." `existing_digest_matches_landed=False`, `journal_unlinked=True`, then `post_replay_load=REJECTED`. | **FIXED.** Round 4's map binding guarded the append path and left the early return open. Idempotence now means "this exact witness is already recorded", proven by semantic equality across type, surface, section, floors, attestation, reason and digest. |
| 4 | high | "Duplicate ids bind the last payload to the first row's predecessor." `latest_event` returns the LAST payload while positional lookup finds the FIRST. `accepted_claimed_predecessor=g floor=100` against `actual_predecessor_of_latest_dup=mid floor=60`. | **FIXED.** The ambiguity is refused outright rather than reconciled: an id that does not name exactly one row makes a chain unreplayable. |
| 5 | medium | "A non-integer new floor bypasses direction validation." `prior=0,new=12.0` gave `load=ACCEPTED floor=12 type=int`; only the separate ledger validator objected. | **FIXED.** Fails closed on any non-integer floor before equality or direction, excluding `bool` explicitly since it is an `int` subclass. |

**A consequence of the INERT ruling, applied rather than hidden.** With later genesis rows
skipped, the re-anchor minted earlier this session names a row no longer in the chain, so
`AGENTS.md` would have been stranded — the exact outcome the INERT ruling exists to prevent.
A link naming an inert genesis is therefore treated as naming the root: inert rows are
skipped, the root is then the surface's only genesis, and a genesis row carries no prior
floor, so naming one asserts the state the root asserts. The FLOOR edge is still enforced
against the real predecessor and the map binding still holds, so this grants nothing an
attacker can use. No second re-anchor mint was needed.

**Round 5 also confirmed** the round-4 chain guard is non-vacuous by mutation
(`named_test_result=FAIL`), that the three unpinned `_assert_refused_and_untouched` call
sites do not currently mask their targets, and that the LITERAL text of REQ-0.35.0-04-02
agrees with `record_unowned_total` (`Ran 2 tests ... OK`) — the disagreement round 4 reported
was with a broader paraphrase, not the requirement as written.

**Two of this session's own test fixtures were silently vacuous and had to be rebuilt** — a
hand-typed `event_id` that failed id-recomputation before reaching the branch under test, and
a forged map flipping an already-`unowned` section so the two maps were identical. Both
produced PASSING tests that witnessed nothing; both were caught only by asking why a test
passed without its fix. Round 5 was told to hunt for that shape and found no more.

#### Round 6 — the first BOUNDED round, and the one that converged the process (not the claim)

Dispatched with the prompt committed at § Step 4b — the BOUNDED round-6 prompt, verbatim.
One dispatch parameter differed from rounds 1-5 and the difference was load-bearing:
those rounds ran `--scope working-tree` against a DIRTY tree, and the tree is now clean, so
working-tree would have shown the adversary nothing. Proven accidentally before dispatch —
a stray probe reviewed the empty diff and returned *"Verdict: approve / No material
findings"* on no code at all, which is exactly the vacuous-clean receipt this gate must
never accept. Round 6 ran `--scope branch --base 5108d7cf`, presenting this session's three
ownership fixes including `6a4ab55d`, the round-5 discharge no adversary round had seen.

**The threat model worked.** Zero out-of-scope findings; no escalation to ledger forgery,
hand-edited declarations or hand-written journals. Every reproduction below was reached
without any write access to `.gzkit/`. That is the first round of six where the adversary's
effort landed entirely inside the boundary the operator accepted.

**The convergence rule was applied, not re-litigated.** Two criticals and a high mean NOT
converged, so this round did not close the gate on its own terms. The *Weakest point* named
a NEW root — *"declaration locking is mistaken for transaction isolation even though the
command consumes an unlocked surface snapshot and mutates a shared ledger"* — not a
re-surfacing of rounds 1-5's chaining root, so the same-root escalation rule did not fire.
What fired instead is the allowlist: the criticals live in a module this brief may not edit.

| # | Severity | Finding (adversary's own words, abridged) | Disposition |
|---|---|---|---|
| 1 | critical | "A failed append can erase another surface's successful witness." Different surfaces take different declaration locks, but `_append_event_once` appends the SHARED ledger with no ledger-wide lock. `thread_A=OSError: injected partial write`, `thread_B=success`, `event_B_present=False`, `final_bytes='SEED\n'` — A's rollback truncation deleted B's committed row after B reported success. | **ROUTED OUT to GHI #953.** Roots in `Ledger.append`; § Denied Paths declares `src/gzkit/ledger.py` read-only, it is a registered `ledger_integrity` security surface, and the gap belongs to every event producer in the repo. Adversary's own framing: *"The critical fixes require a shared ledger transaction boundary, not another declaration-local guard."* |
| 2 | critical | "A crash leaving a truncated final ledger row makes journal recovery loop forever." `latest_event` raises `JSONDecodeError`; `_replay_pending_transition` catches only `OSError`. `retry_exit=1`, `second_retry_exit=1`, `journal_after_retries=True` — every retry dies before the intact journal can restore the witness. Required no hand-written row: the probe injected a crash inside `Ledger.append`. | **ROUTED OUT to GHI #953**, same module and same reasoning. This is the finding that makes the unamended claim false in scope, so the claim is amended rather than the finding minimised. |
| 3 | high | "The command can exit 0 using a stale surface snapshot and leave an unloadable declaration." The surface was read BEFORE the lock. `command_exit=0` with a success line claiming 26 -> 83, `journal_exists=False`, then `post_command_loader=REJECTED` because the summed span 484 exceeded the witnessed floor. | **FIXED.** The surface is now read INSIDE the lock, and `_refuse_surface_changed_under_us` re-reads once more before the journal is written — two windows, two guards. Both are mutation-verified: reverting the read to outside the lock kills `test_a_surface_edited_on_lock_entry_is_refused_not_committed_stale`; deleting the re-check kills `test_a_surface_edited_after_measurement_is_refused_before_either_store`. |
| 4 | medium | "Post-replace journal fsync failure falsely reports that nothing was written." `write_declaration_atomically` may raise from the directory fsync AFTER the journal rename landed, but the handler said `Nothing written.` unconditionally. | **FIXED.** The journal branch now says what the declaration branch has said since round 3: both stores are unchanged, but the journal itself may or may not have landed. The sibling test's comment asserting the opposite — that "Nothing written" is *"entirely true"* on this branch — was WRONG and is corrected in place. |
| 5 | medium | "Four rejection tests survive deletion of the guard they claim to witness." Substitute reasons were, respectively, missing prior floor; illegal 0->999 direction; event-floor disagreement; predecessor mismatch. The last test's `assertIn('prior', ...)` was satisfied by its own fixture id `no-prior`. | **FIXED.** Every fixture is now valid through all guards EXCEPT the one under test, and every assertion names a branch-specific diagnostic instead of `REQ-0.35.0-04-02`, which every guard in the loader emits. Two of the four now kill their mutation with `OwnershipLoadError not raised` — the strongest signal available, meaning nothing else in the loader objects to the fixture. |
| 6 | low | "A non-UTF-8 surface escapes the governed failure prose." `read_text` raises `UnicodeDecodeError`, a `ValueError`, so `except OSError` missed it: `exit=1 unchanged=True output=Unexpected error: 'utf-8' codec can't decode byte 0xff...`. | **FIXED.** `_read_surface_or_exit` catches both and emits the three-part what/why/next-step. Mutation-verified. |

**Five vacuous fixtures now, not four — and one of them was written THIS round.** The
first draft of `test_a_surface_edited_on_lock_entry_is_refused_not_committed_stale`
accepted *either* a correct success *or* a refusal, and SURVIVED reverting the guard it
named, because the second guard refused and the permissive branch accepted that refusal. It
was caught by mutating the guard, never by the suite going green. The lesson round 6 taught
about this OBPI's old tests applied immediately to its new ones; a test that accepts both
outcomes of the fix it names witnesses neither.

**Mutation verification, all eight guards touched this round** — each check deleted in
isolation, its named test observed to FAIL, then restored (the harness asserts byte-identical
restoration):

```
A_read_inside_lock         killed
B_refuse_surface_changed   killed
C_unicode_decode           killed
D_journal_prose            killed
roster_check               killed   (AssertionError: OwnershipLoadError not raised)
floor_equality             killed   (AssertionError: OwnershipLoadError not raised)
null_pointer               killed
missing_prior              killed
```

#### Round 7 — the first CORROBORATION-framed round, and the one that forced the design ruling

Receipt `arb-step-codexadversary-5a988275da32415386087b4a8656b86d`, `exit_status: 0`,
12.3 min, commit `1c8b15fc`, dispatched 2026-09-04T01:36:14Z. `--scope branch --base
5108d7cf`. Log grepped for `Turn failed` / `Codex error` / `flagged for possible` /
content-filter markers — none present; `stdout_truncated: False`.
**`CORROBORATION: NOT-CORROBORATED` / `VERDICT: REFUTED`, two high findings.**

**This is the first round in the gate's history to produce real positive corroboration, and
that is the point of recording it.** Rounds 1-6 were told to refute and returned only what
they broke; round 7 was told to corroborate and had to demonstrate the feature WORKING before
it could report what it could not confirm. Its observed-corroboration paragraph is the
evidence the pass condition actually asks for, in its own words (abridged): a legitimate
raise exited 0, measured +57 B, moved the floor 26→83, reloaded successfully, and emitted
exactly one witness carrying section, both floors, `attestor=g0` and reason; blank attestor,
blank reason, unknown section and already-unowned section each exited 1 with declaration and
ledger unchanged; injected failures at **six** boundaries — before journal write, between
journal and declaration, during replace, at both directory-fsync boundaries, during ledger
append, and after append/before unlink — all retried to floor 83, one witness, no journal,
same journalled event id, loader acceptance; same-surface concurrency landed both distinct
sections once and duplicate same-section calls yielded one success and one refusal; truncated
declaration/journal, pre-read section rename and non-UTF-8 input produced governed refusals
without store mutation; scoped suite 102/102; and the eight guards touched by `3d4f06ac` were
each deleted independently with none surviving its mutation. **A round that only lists what it
broke has not met the pass condition. This one met the demonstrate half and failed the
no-high half.**

**Its `Weakest point` named the SAME ROOT as round 6, and the same-root rule fired.** Verbatim:
*"the mutable surface is not transactionally version-bound to the declaration, journal, and
witness; both new failures arise because a scalar re-read is being used as a substitute for
that missing binding."* Round 6's own fix WAS that scalar re-read. Per the rule booked
2026-09-03, dispatching STOPPED and the design went to the operator instead of a third patch
at one root — operator ruling, verbatim: *"bind the surface into the transaction. this has
never been an issue before."* It closed in one pass, as the rule predicts.

| # | Severity | Finding (adversary's own words, abridged) | Disposition |
|---|---|---|---|
| 1 | high | "Final surface check still permits a mid-run edit to commit stale state" (`unown.py:802-803`). The surface is checked, then committed separately. An ordinary editor write at that boundary produced `exit=0`, success prose claiming `26 to 83 (+57 B)`, `stored_floor=83`, `live_unowned_span=653`, `witnesses=1`, `journal_exists=False`, then `post_success_load=REJECTED: OwnershipLoadError` — success reported, recovery state destroyed, declaration rejected by its own canonical loader. | **FIXED at `b5138874`.** The surface digest is now JOURNALLED with the transition, making the surface a versioned participant rather than an unversioned input read twice and hoped about. `_refuse_clean_success_on_a_moved_surface` re-verifies it after the declaration and the ledger witness are both durable and BEFORE the journal is cleared — the only point where the check can still act on the outcome. A pre-flight check cannot cover this by construction: `_refuse_surface_changed_under_us` is KEPT (a refusal there writes nothing at all) but is check-then-act. The transition is NOT rolled back — the witness is a truthful append-only record of what was committed; what is refused is the CLAIM OF CLEAN SUCCESS, and what is retained is the journal, so the state can be reconciled instead of being silently wrong. |
| 2 | high | "Already-landed recovery consumes the journal after a section rename" (`unown.py:408-447`). After an injected ledger-append failure left declaration and journal, renaming `alpha-section` by ordinary edit and retrying gave `retry_exit=0`, "Completed the interrupted un-owning", one witness, `journal_exists=False`; reload then rejected the undeclared `renamed-section`. "The coherence calculation silently omits live section IDs absent from the landed map, so it validates only the scalar span rather than full declaration/surface coverage." | **FIXED at `b5138874`.** Section-ID coverage is now compared as a SET, not summed. `live_unowned_span` sums only ids present in the landed map, so a renamed section contributed nothing and the scalar check passed while the declaration no longer covered the surface. **A sum cannot witness coverage** — for the same reason a scalar could not witness the map at round 4 or the direction at round 5. A false-positive test is added alongside, pinning that an unchanged surface still completes cleanly: a guard with no false-positive test can be made infinitely strict without any test objecting. |

**Mutation-verified at `b5138874`: all eleven guards touched across rounds 6 and 7** — each
check deleted in isolation, its named test observed to FAIL, source restored byte-identically.

#### Round 8 — THE STANDING VERDICT, and a round whose environment limited what it could witness

Receipt `arb-step-codexadversary-9a16acc9764848088cfa9130a98db71b`, `exit_status: 0`,
commit `b5138874`, dispatched 2026-09-04T01:54:35Z. `--scope branch --base 5108d7cf`. Log
grepped for the same four failure markers — none present; `stdout_truncated: False`.
**`CORROBORATION: NOT-CORROBORATED` / `VERDICT: REFUTED`, two high and one medium finding.**

**READ THE COVERAGE LIMIT BEFORE READING THE VERDICT.** Round 8's own `Weakest point`,
verbatim: *"full filesystem failure/concurrency demonstrations and deletion-based mutation
checks for all 105 tests could not be executed in this read-only environment."* It observed
22 read-only ownership tests passing, the committed `AGENTS.md` declaration loading, and the
blank-attestor / malformed-declaration / malformed-journal / non-UTF-8 / no-trailing-newline
probes behaving correctly — then found its three defects **by reading the code**. A
NOT-CORROBORATED from that environment is partly a statement about the sandbox; a
CORROBORATED from it would have been weak for the same reason. **Round 9 must run in a
writable workspace or its verdict means little either way (GHI #941).**

| # | Severity | Finding (adversary's own words, abridged) | Disposition |
|---|---|---|---|
| 1 | high | "Recovery bypasses the new surface-digest binding" (`unown.py:548-565`). Replay validated the captured surface before `_append_event_once`, then cleared the journal without ever calling `_refuse_clean_success_on_a_moved_surface`: `post_digest_guard_calls=0`, `exit=0`, `event_appended=True`, `journal_exists=False`, clean-success prose after the journalled surface had moved. A second probe changed only a corpus-owned section between attempts; coherence accepted it despite `digest_changed=True`. The fresh path also had a check-to-unlink interval. | **FIXED at `a90a8d14`.** ONE FINALIZATION PATH. The round-7 binding had been implemented on the fresh-commit path only; this applies the operator's already-ruled design to its twin rather than deciding anything new — which is why it was NOT escalated as a fourth same-root design question. The adversary's own recommendation said the same: *"use one finalization path for fresh commits and replay."* The coherence checks were not a substitute: they ran correctly, against the surface as it was before the append. |
| 2 | high | "The digest binds normalized text, not the surface bytes whose span is governed" (`unown.py:687-700`). Both reads used `Path.read_text`, whose universal-newline handling normalizes CRLF to LF, so the digest hashed the normalized string: `raw_lengths=25,29 decoded_equal=True digests_equal=True measured_totals=25,25`. An LF↔CRLF edit therefore changed the physical byte spans the floor governs WITHOUT firing the digest, and the floor silently undercounted the file. | **FIXED at `a90a8d14`.** The surface is read as raw BYTES, hashed as bytes, and decoded with `bytes.decode` (no translation), so the text measured round-trips to the bytes hashed. **This is not exotic input:** `.claude/rules/cross-platform.md` makes Windows co-equal and an editor there produces CRLF by saving. |
| 3 | medium | "Recovering a different pending section makes the subsequent 'nothing written' refusal false" (`unown.py:819-851`). The handler returned after recovery only when the recovered section equalled the requested one; otherwise it completed the pending transition, appended its witness, deleted its journal, then fell through into refusal prose reading "nothing written". Observed `exit=1 event_appended=True journal_exists=False`. Reachable with no `.gzkit/` access at all. | **FIXED at `a90a8d14`.** Recovery now ALWAYS terminates its invocation and reports the recovery, regardless of the newly requested section — so later refusal prose can never claim the stores were unchanged after a durable state change. |

**TWO OF ROUND 8'S OWN FIX-TESTS WERE VACUOUS AND WERE CAUGHT BY MUTATION, NOT BY THE SUITE.**
The digest test called `_surface_digest` directly and SURVIVED a mutation making the read path
hash normalized text — *a helper can be perfectly correct while nothing routes real input
through it* — so a test at the seam was added. And round 7's coverage guard began surviving
its own deletion once round 8's digest guard MASKED it; its test now pins the case where
coverage is genuinely load-bearing (a journal carrying no `surface_digest`, which the digest
guard skips by design). **This is the second recorded instance of guard masking in this OBPI**
(round 6's `_refuse_surface_changed_under_us` masked the read-inside-the-lock fix). Both were
found only by re-running EVERY mutation after each change. **Re-run the whole set, never only
the new guards.**

**Mutation-verified at `a90a8d14`: all ten guards across rounds 6, 7 and 8** — each deleted in
isolation, its named test observed to FAIL, source restored byte-identically. The ten: the
read-inside-the-lock move, `_refuse_surface_changed_under_us`, the `UnicodeDecodeError` catch,
the journal-branch prose, the journalled `surface_digest`, the fresh-path post-durability
verification, the section-ID coverage set comparison, the raw-byte digest at the read seam,
the replay-path finalization guard, and recovery-always-terminates.

> **The mutation harness itself did not survive its session** (`scratchpad/mutate_all.py` is
> gone). Re-derive it before trusting any test in this OBPI; the suite going green has never
> once caught a vacuous test here.

**A scalar has stood in for a structure FOUR times in this OBPI** — the map at round 4, the
direction at round 5, the span at rounds 6 and 7. When a check compares a number where the
property is a set or a map, assume that is the next finding.

#### Round 9 — THE STANDING VERDICT, and the first round ever to observe the current tree

Receipt `arb-step-codexadversary-dd8d6bbcb51c4f4a8d1042687a90964b`, `exit_status: 0`,
commit `397301c6`, dispatched 2026-09-05T06:18:06Z, duration 737s. `--scope branch
--base 5108d7cf`, dispatched through the Codex plugin runtime
(`node .../codex-companion.mjs adversarial-review --wait`) — tier 1, cross-vendor. The log
was grepped for `Turn failed` / `Codex error` / `flagged for possible` / content-filter
markers and carries NONE; `stdout_truncated` is `False`.
**`CORROBORATION: NOT-CORROBORATED` / `VERDICT: REFUTED`, one high and three medium
findings, no critical, all in scope.**

**This is the round the previous eight could not be: it saw `a90a8d14`.** Prompted from the
operator's four-part Purpose / Method / Boundary / Pass-condition block, bounded by
§ Threat Model, and told explicitly that `No usable temporary directory` is an environmental
limit rather than a defect. It re-derived all three of round 8's fixes independently and
**confirmed each**: both fresh and replay paths refuse a moved surface (`exit 2 journal True
appended 1`) and accept a restored one (`exit 0 journal False appended 1 reload ACCEPTED`);
raw-byte reads round-trip LF and CRLF to different digests; different-section recovery
reports what it recovered, exits 1, and leaves the requested section owned.

**IT ALSO DEMONSTRATED THE FEATURE WORKING — the thing six rounds never did.** Legitimate
un-owning printed `Unowned-byte floor rose from 26 to 83 (+57 B)` and reloaded. The ratchet
behaved in all three directions: `increase27 REFUSED writes 0 appended 0`, `equality26
ACCEPTED`, `decrease18 ACCEPTED`. Blank attestor/reason, unknown and already-unowned
sections, undeclared/stale/duplicate section ids and invalid UTF-8 were all refused. A
title change with an unchanged section id loaded successfully (REQ-06). Baseline reported
`10/22 owned sections, 8637/46876 unowned bytes, 81.57479307108116% coverage` with the
per-section histogram (REQ-07), and empty/one-entry corpus controls moved the measurements
appropriately.

| # | Severity | Finding (adversary's own words, abridged) | Disposition |
|---|---|---|---|
| 1 | high | "Bind the witness to the declaration's canonical surface identity" (`unown.py:910-915`). On a case-insensitive filesystem `AGENTS.md` and `agents.md` are the same file. The command copies the declaration's surface unchanged but records THE CALLER'S SPELLING in the witness: `surface_samefile True`, `declaration_samefile True`, `PARSED_CLI exit 0 appended 1 journal False reload REJECTED` — the reload reporting *"declares surface 'AGENTS.md' ... but that event witnesses surface 'agents.md'."* A canonical retry also failed. Only the CLI argument changed; nothing was forged. **The command destroys recovery state while reporting success for a declaration its own loader then rejects.** | **OPEN — ESCALATED TO THE OPERATOR.** In scope and high, so the gate does not converge. See § Round 9 — same-root escalation below. |
| 2 | medium | "Preserve raw bytes in the pre-commit surface recheck" (`unown.py:791-798`). The initial read preserves CRLF but this `read_text` call normalizes to LF, so an unchanged valid CRLF surface ALWAYS appears changed: `CRLF raw_bytes 129 measured_bytes 129 roundtrips True initial_load ACCEPTED` then `exit 1 writes [] appended 0 journal False`. The LF control succeeded 26 -> 83. "The raw-byte digest fix is correct, but fresh CRLF operations cannot reach it successfully." | **OPEN.** This is ROUND 8 FINDING 2 AT A THIRD READ SITE — the same root, not a new one. Part of the escalation below. |
| 3 | medium | "Make schema rejection fixtures otherwise valid" (`tests/content/test_ownership.py:884-893`). The enum, extra-property and negative-floor tests all omit the required `floor_event_id` and merely assert `ValidationError`, so each fails on `required` before reaching the constraint it names: `validators=['required', 'enum']`, `['additionalProperties', 'required']`, `['required', 'minimum']`. "Each test would therefore survive deletion of its named schema constraint." | **OPEN — three more vacuous fixtures.** Found by reading, not mutation (it cannot write). This is the SEVENTH, EIGHTH and NINTH vacuous fixture in this OBPI. |
| 4 | medium | "Distinguish replay coherence refusal from the later digest refusal" (`tests/commands/test_content_unown.py:520-530`). `test_replay_refuses_to_complete_into_a_state_the_loader_would_reject` asserts only a nonzero exit and a retained journal, but its changed surface also trips the digest guard: `landed_span exit 2 journal True satisfies_test_final_assertions True` / `post_digest exit 2 ... True`. Removing the landed-span check would still pass this test through the digest refusal. | **OPEN — GUARD MASKING, THE THIRD RECORDED INSTANCE** in this OBPI (round 6's `_refuse_surface_changed_under_us` masked the read-inside-the-lock fix; round 8's digest guard masked round 7's coverage guard). |

**Coverage limits the adversary declared itself**, verbatim: *"real filesystem crash
durability, concurrent writers, directory-fsync recovery, Windows execution, or a complete
mutation sweep"* could not be confirmed — *"In-memory adapters demonstrate control flow, not
storage guarantees."* It also noted that the brief records ten mutation checks while stating
its harness is gone, and that this *"cannot establish mutation coverage of every remaining
test."* The read-only two-module run was `Ran 111 tests`, 21 passing and 90 erroring on the
declared-environmental temp-directory signature; an isolated read-only subset ran `23 tests
... OK`. It correctly reported the temp-directory errors as a coverage limit, not a defect —
the prompt instruction worked.

**SAME-ROOT ESCALATION — THIS IS WHY ROUND 10 WAS NOT DISPATCHED.** The skill's rule is that
when a round's *Weakest point* names the same root as the prior round, stop dispatching and
put the DESIGN decision to the operator. Round 9's weakest point, verbatim: *"surface
identity is not consistently bound across the CLI argument, filesystem alias, declaration,
and ledger witness."* Finding 1 is that root at the witness; finding 2 is round 8's own
finding 2 at a THIRD read site, after round 8 fixed the initial read and the final digest.
The brief already records that **a scalar has stood in for a structure four times here** —
the map at round 4, the direction at round 5, the span at rounds 6 and 7. Findings 1 and 2
are the fifth and sixth: a surface's IDENTITY is a canonical structure, and it is being
carried as the caller's raw string; a surface's BYTES are the governed property, and they
are being re-read through a decoder at each new site. Patching site three invites site four.
The design question is whether the transaction should canonicalize surface identity and
raw-byte reads ONCE at entry, rather than at each call site. That is an operator decision,
not another fix cycle.

#### Round 10 — THE STANDING VERDICT: round 9's root CLOSED, a NEW root opened

Receipt `arb-step-codexadversary-658c8ce606114de39730cd01a66e5f3d`, `exit_status: 0`,
duration 689s, `--scope branch --base 5108d7cf`, dispatched through the Codex plugin runtime
(tier 1, cross-vendor). Log carries none of the four failure markers; `stdout_truncated` is
`False`. **`CORROBORATION: NOT-CORROBORATED` / `VERDICT: REFUTED` — two HIGH findings, no
critical, no medium.** The prompt stated the claim EXACTLY as round 9 did (bounded by the
ledger precondition, not strengthened) per the operator ruling of 2026-09-05, and required the
adversary to state the access each finding's reproduction requires.

**THE FIXED-TARGET CORRECTION IS CORROBORATED.** Round 10 ran the real CLI and canonical
loader against in-memory storage adapters and demonstrated, positively:

```
fresh_alias    {'identity': 'Doc.md', 'floor': 83, 'witnesses': 1, 'journal': False, 'source_unchanged': True, 'reload': 'ACCEPTED'}
CRLF_alias     {'identity': 'Doc.md', 'floor': 88, 'witnesses': 1, 'journal': False, 'source_unchanged': True, 'reload': 'ACCEPTED'}
unlanded_replay{'identity': 'Doc.md', 'floor': 83, 'witnesses': 1, 'journal': False, 'source_unchanged': True, 'reload': 'ACCEPTED'}
landed_replay  {'identity': 'Doc.md', 'floor': 83, 'witnesses': 1, 'journal': False, 'source_unchanged': True, 'reload': 'ACCEPTED'}
RATCHET 27 REFUSED writes 0 witnesses 0 reload ACCEPTED
```

Verbatim: *"All paths used Doc.md.json for locking/declaration, Doc.md.json.journal for
journalling/cleanup, and Doc.md for the witness. Actual host resolution also returned: REAL
targets_equal True identity AGENTS.md."* It also confirmed all four snapshot identity guards
fired at their named phases, and — as instructed — classified the injected foreign-snapshot
probes as **defence-in-depth evidence, not in-scope findings**. The acceptance boundary held.

**The two HIGH findings are a DIFFERENT ROOT, so the same-root escalation rule does not fire.**
Rounds 8 and 9 rooted in identity/bytes re-derived per call site; that is closed. Round 10's
weakest point, verbatim: *"recovery treats a visible declaration as durably committed and a
retained digest as sufficient recovery information. The fixed target resolves identity
consistency, but neither assumption establishes recoverability."*

| # | Severity | Finding (adversary's words, abridged) | Required access | Disposition |
|---|---|---|---|---|
| 1 | high | "Re-establish declaration durability during landed recovery" (`unown.py:887-898`). After `os.replace` succeeds but the directory fsync fails, retry sees the new `floor_event_id` and SKIPS the atomic writer — appends the witness, deletes the journal, and reports success without ever retrying the failed durability barrier. `REAL_WRITER first_exit 2 directory_fsync_attempts 2` then `REAL_WRITER retry_exit 0 fsync_calls 0 witnesses 1 journal False`. The declaration rename remains unconfirmed as durable when recovery reports completion. | **Ordinary CLI invocation + a failing directory fsync. No `.gzkit/` write access.** | **OPEN — IN SCOPE.** Adversary states explicitly: *"This is independent of the disclosed `Ledger.append` defects"* — so it is NOT covered by the GHI #952/#953 residual. The consequence (a later crash losing acknowledged state) is inferred from the missing barrier, not observed through a physical crash. |
| 2 | high | "Preserve enough information to recover a changed surface" (`unown.py:1342`). Recovery requires the exact original surface digest, but the journal retains no original surface bytes. If an editor replaces the uncommitted text, neither a retry nor a request for another section can complete: `UNBACKED requested alpha-section exit 2`, `doc-title exit 2`, `alpha-section exit 2`, each reporting *"surface 'Doc.md' changed DURING the un-owning"*. **The retained journal permanently blocks further governed ownership transitions.** Restoring the exact old bytes succeeds — but those bytes are an undisclosed recovery prerequisite. | **Ordinary CLI invocation + an atomic append failure + editor access to the source surface. No declaration, journal or ledger edits.** | **OPEN — IN SCOPE.** A liveness defect: the governed path can reach a state only an out-of-band byte restore can leave. |

**Both findings were produced by the PRODUCTION CLI**, not by hand-built state — the adversary
notes the production CLI generated every recovery artifact in the second probe
(`journal_source_fields ['surface', 'surface_digest']`).

#### Round 11 — THE STANDING VERDICT: round 10 discharged, the D-beats-E correction overreached

Receipt `arb-step-codexadversary-cc9aa913064b4550807e717c51982f4b`, `exit_status: 0`, 925s,
`--scope branch --base 5108d7cf`, Codex plugin runtime (tier 1, cross-vendor).
`stdout_truncated: False`; none of the four failure markers present. Prompt stated the claim
EXACTLY as rounds 9 and 10 did, not strengthened. **`CORROBORATION: NOT-CORROBORATED` /
`VERDICT: REFUTED` — one high, two medium, no critical.** Both replay branches, case-alias
handling and ratchet behaviour were positively demonstrated.

**Round 10's two high findings are discharged.** The recovery protocol landed as one design
(five states plus the orthogonal source axis) rather than per-finding patches.

| # | Sev | Finding (adversary's words, abridged) | Required access | Disposition |
|---|---|---|---|---|
| 1 | high | "Preserve reconciliation material when D also has a changed source" (`unown.py:1229-1233`). First invocation correctly refuses in D+E; the retry skips the source binding, DELETES both recovery copies, and reports completion while the loader still rejects the surface. `D+E retry_exit 0 floor 83 span 102 journal False snapshot False extract False`, then `advertised_raise alpha-section exit 1` / `doc-title exit 1` with *"declares unowned_byte_floor 83, but the summed byte span … is 102, which exceeds it."* The advertised re-run cannot repair it — its initial load rejects the exceeded floor. *"D proves the original transition was witnessed, not that source reconciliation is finished."* | **Ordinary CLI + an editor save during the transaction. No `.gzkit/` writes.** | **OPEN — IN SCOPE.** A CONSEQUENCE OF THE D-BEATS-E CORRECTION recorded in the plan on 2026-09-05. That correction fixed E shadowing D by making D swallow E; the two are distinct obligations. Awaiting operator ruling on shape. |
| 2 | medium | "Report cleanup failures instead of silently consuming later artifacts" (`unown.py:1370-1376`). `contextlib.suppress(OSError)` over all three unlinks lets journal deletion fail while its snapshot is deleted: `journal_unlink_failed exit 0 journal True snapshot False diagnostic_mentions_IO_fault False`. Later requests recover the same uncleared journal repeatedly without exposing the fault. | Ordinary CLI + an OS unlink failure. No `.gzkit/` writes. | **OPEN.** Suppress only expected absence; report other cleanup failures as state-D cleanup pending. |
| 3 | medium | "Ignore and manage extraction staging files left by crashes" (`.gitignore:128-135`). The atomic writer stages under `.<surface>.unowning-recovery.<n>.tmp`; the new rule covers only the final extract. `EXTRACT_CRASH exit 99 residue ['/review/.doc.md.unowning-recovery.3.tmp']`, `RESIDUE_IS_MEASURED_SOURCE True`, and successful recovery retained it. | Ordinary CLI recovery + interruption during extraction. No `.gzkit/` writes. | **OPEN — INDEPENDENTLY VERIFIED HERE**: `git check-ignore` returns exit 0 for `AGENTS.md.unowning-recovery` and exit 1 (NOT ignored) for `.AGENTS.md.unowning-recovery.abc123.tmp`. |

**Weakest point, verbatim:** *"the protocol still treats completion of the declaration/ledger
transition as completion of all recovery obligations. D does not establish source
reconciliation, and attempted unlink does not establish cleanup. Repair these lifecycle
distinctions together, then repeat acceptance review."*

##### OPERATOR RULING — 2026-09-05 (binding; booked at `.gzkit/handoffs/rulings.jsonl`)

The round-11 high was put to the operator rather than settled by an agent, because the
previous correction went wrong precisely by settling a lifecycle distinction without a ruling.
Operator verbatim:

> Reject "D beats E." Keep three obligations separate: the transition is durably witnessed;
> the source is reconciled; recovery cleanup is complete. Establishing one does not discharge
> the others.
>
> 1. D+E: preserve the existing witness without duplication, report "transition witnessed;
>    source reconciliation pending," return a non-success status, and retain the measured bytes
>    while preserving newer edits.
> 2. Prove the recovery instructions actually work. Execute the printed sequence from the
>    reproduced failure through a canonical loader accepting the recovered state. Restoring
>    retained measured bytes can achieve that while newer edits remain safely saved. Do not
>    instruct users to reapply an oversized edit and then invoke a command whose initial loader
>    rejects it.
> 3. Make cleanup recoverable. A journal-removal failure must preserve dependent recovery
>    material and report the storage fault. Account for interruption between deletions,
>    including their durability barriers. Retries must handle residual artifacts even when the
>    journal is already absent.
> 4. Handle the complete extraction-file family. Cover final and temporary filenames in ignore
>    rules and recovery cleanup.
> 5. Bind verification to the final code. Record the actual test and mutation results against
>    its final SHA. Updating the brief with an unverified account of an earlier sweep does not
>    establish current coverage.
>
> Correct the existing plan, implementation, tests, and recovery documentation together, then
> run the required review. Preserve the existing scope and rulings.

**The three obligations are now the module's organising distinction** — witnessed, reconciled,
cleaned — each established independently and each reported independently. "D beats E" is
RETIRED as a resolution; the orthogonality observation it was built on stands. The plan's
§ CORRECTION (2026-09-05) records the superseded first attempt beside the ruling that replaced
it, and § Binding constraints 5-7 carry points 3, 4 and 2 respectively.

**EVIDENCE-CURRENCY GAP THE ADVERSARY CAUGHT.** The § Evidence Gate 2 mutation table records
source SHA `a4c2e3ad…`; `src/gzkit/commands/content/unown.py` is now `49b2ad58…`. A later
22-guard sweep was executed and reported during the fix cycle but was never written here, so
**the recorded 18-guard sweep does not establish mutation coverage of the current recovery
protocol.** The table must be refreshed to the 22-guard sweep and its SHA before the next
acceptance round is dispatched.

### Codex continuation — 2026-09-05

The operator paused Claude and directed Codex to carry the repair forward. The
existing implementation stage continues; no new pipeline was launched and no
completion or replacement adversarial verdict is claimed.

The unsupported-directory-barrier warning exception was corrected against the
existing preservation/non-success ruling. Before the correction, actual directory
`fsync` failures permitted new snapshot creation on fresh entry and deletion of
retained material during cleanup. After correction, unsupported operations enter
the existing exit-2 refusals; the diagnostic distinguishes an unavailable required
operation from a transient storage fault. No platform exception was added.

The isolated correction received an implementer pass plus independent specification
and quality review passes, with all three actual Codex dispatches recorded for the
recovery correction. It was then integrated while preserving the existing scanner
and canonical-loader test edits. Live scoped verification ran 183 tests successfully:
`arb-step-ownershipunown-0b99a378bc45413d84b5828b58720270`. This is a scoped integration
receipt, not the final full-suite, mutation, or Step-4b evidence.

Equivalent Windows directory durability remains unproved: the current helper's
Windows return performs no barrier. Its existence does not establish the mandatory
boundary or authorize the unsupported-error exception. A standalone native Windows
capability probe is prepared. The operator subsequently authorized its temporary CI
exception above; it has not yet run on Windows and establishes no platform-equivalence
claim until actual evidence is evaluated.

The remaining named recovery corrections are integrated: directory-enumeration
errors are reported rather than treated as an empty result; residue matching treats
surface names literally; the writer test checks the actual parent inode and ordering;
reconciliation ends at restored measured bytes and a loader-accepted retry; extraction
failures do not claim a verified final copy; unreadable/non-UTF-8 source refusals name
the unverified retained material and a verification route; and the exit-1 documentation
accounts for recovery writes. The D+E caller also delegates extraction status to the
helper instead of asserting that a failed extract exists. The manpage example was
regenerated from actual CLI output.

Independent bounded specification and quality reviews passed. Specification review's
one remaining D+E diagnostic concern received an observed assertion failure before
correction, a passing regression afterward, and a passing re-review. The correction
cycles recorded twelve assertion failures before their corresponding fixes; these
are direct RED logs, not fabricated ARB RED receipts.

Verification of the integrated correction:

- 190 scoped tests pass: `arb-step-ownershipunown-f76b9086907a418884556220c66134b2`.
- Full suite: 9,406 tests pass in 27.674 seconds,
  `arb-step-unittest-5d8aafb1b439413e8072f919aead60d4`.
- Ruff: `arb-ruff-bf0781b398f544b3a159c19fd899a35d`; formatting check passes.
- Type checking: `arb-step-typecheck-6a38214d71aa42d1970917f7e933a9c6`.
- Strict documentation build: `arb-step-mkdocs-ee54e14777f34271b9d58691e5afb0b9`.
- Raise-path BDD: five scenarios and 29 steps pass, no skips,
  `arb-step-ownershipbdd-aac398586d884cbcb67f9b8b6b490073`.

Two earlier full-suite attempts failed five tests because the verification sandbox
blocked `uvx radon` from writing its global tools directory. Captured subprocess output
established the shared cause, including the hook test. Providing a writable
`UV_TOOL_DIR` alongside `UV_CACHE_DIR` resolved all five without source changes; the
passing full-suite receipt above uses that environment correction. The failed receipts
remain evidence (`arb-step-unittest-30af4f81f79e4dc3a3b4a048a6527d6b` and
`arb-step-unittest-02f2fb73e6ea4b3cab7c44145723f962`).

These results do not replace the standing Step-4b refutation, establish Windows
durability, or constitute human attestation. The final mutation binding and required
adversarial review remain pending the platform correction.

The subsequent full `gz check` passed 58 of 59 checks and exposed a separate
Claude-first BDD fixture assumption: an implicit Codex requester matched the fixture's
hardcoded Codex holder. The claim-conflict and ownership-refusal scenarios failed,
and the force-override scenario did not exercise a different owner. Six feature lines
now name distinct holder/requester identities explicitly. All 13 lock scenarios and
66 steps pass under actual Codex detection and simulated Claude detection. Production
lock code is unchanged; the repair is captured in the insights store and this evidence.

## Threat Model (binding for this OBPI's Step 4b)

**This section exists because its absence cost roughly nine hours.** Step 4b ran five
rounds against an ABSOLUTE claim ("no ownership transition can occur without ..."). An
adversary instructed to REFUTE an absolute security property can always escalate the
attacker one notch, so the gate could not converge by construction. Rounds 4 and 5 then
spent their effort hardening attacks that sit strictly INSIDE a residual the operator had
already accepted at round 3. The boundary below is what makes the claim refutable in a
bounded way, and therefore closable.

### In scope — MUST be prevented

An actor with **no write access to `.gzkit/`**. Concretely, everything reachable through
the `gz` CLI, through ordinary operation, and through FAILURE: a disk error, an
interrupted run, a crash between the declaration write and the ledger append, an NFS
mount that fails a directory fsync. No adversary is required to reach any of these.

Three findings were in this class and are FIXED: the post-swap `OSError` that deleted the
recovery journal while printing "Nothing written" (round-3 finding 3); the already-landed
replay branch that completed having validated nothing (round-3 finding 4); and recovery
consuming the journal while leaving a declaration the loader rejects (round-5 finding 3).
Round 6 added three more, all FIXED: the stale surface snapshot committed under a success
exit (finding 3), the journal branch's false "Nothing written" (finding 4), and the
non-UTF-8 surface escaping governed prose (finding 6).

#### AMENDMENT — the claim is bounded by the ledger's transaction semantics (2026-09-04)

**Operator-ruled, on the round-6 evidence.** The claim this gate defends previously read
that no ordinary failure *"can leave the ownership state unrecoverable, silently wrong, or
reported as successful when it is not."* Round 6 proved that FALSE inside this brief's own
scope: a crash leaving a truncated final ledger row makes every retry raise
`JSONDecodeError` before the intact journal can restore the witness, so the transition
becomes permanently uncompletable through the governed path. No special access was needed.

The claim is therefore amended, and the amendment is a NARROWING, never a weakening:

> Within the threat model above, **and given a ledger append that is atomic with respect to
> concurrent writers and leaves no partial record on a crash**, a section-ownership floor
> changes only through the governed `gz content unown` path, and no ordinary failure can
> leave the ownership state unrecoverable, silently wrong, or reported as successful when
> it is not.

The italicised precondition is **not currently true** — that is the point of stating it.
It is tracked at **GHI #953**, is a property of `src/gzkit/ledger.py` rather than of this
brief's surfaces, and is shared by every event producer in the repo. Naming it as a
precondition is what keeps this brief's attested claim honest: the ownership path holds up
its end, and the end it depends on is disclosed rather than assumed.

**What this amendment does NOT license.** It does not widen the residual to anything else,
it does not weaken any guard landed in rounds 1-6, and it is not a precedent for amending
a claim rather than fixing a defect — the two criticals are fixed *somewhere*, just not
here, and GHI #953 is open with a blocker comment naming the operator's next action.

### Out of scope — DISCLOSED RESIDUAL, defended by auditability

An actor **with write access to `.gzkit/`**, including the ability to append arbitrary rows
to `.gzkit/ledger.jsonl`.

The operator ruled this boundary at round 3 for `.gzkit/ownership/`: such an actor is
inside the trust boundary, and the defence is AUDITABILITY — the transition lands in the
append-only ledger carrying its attestor and reason — never prevention. The ledger sits
under the same directory and the same access, so the ruling covers it. An actor who can
append arbitrary ledger rows can forge attestations, completions and receipts across the
whole governance surface; moving a byte floor is the least thing available to them.
Preventing it at the ownership layer while that holds is theatre.

**Defence-in-depth is still kept, not reverted.** The chain replay, the migration-only
re-anchor, the duplicate-id refusal and the integer-floor check all remain: they are cheap,
they are proven by negative control, and several also catch ordinary corruption. They are
recorded here as DEFENCE-IN-DEPTH BEYOND THE BOUNDARY rather than as gate conditions, so a
future round does not re-litigate them as blockers.

### What this does NOT license

It does not license a weaker `gz content unown`. Every raise still requires the attested
path, an attestor and a reason. It does not license skipping Step 4b. And it does not
license widening the residual by argument: extending it to any surface outside `.gzkit/`
is a fresh operator ruling, never an inference from this one.

### Step 4b — the BOUNDED round-6 prompt (reuse verbatim)

Rounds 1-5 each prompted an ABSOLUTE claim and could not converge. This is the
first prompt bounded by § Threat Model: it states the boundary and forbids the
adversary from reporting an out-of-scope attack as a finding. It is recorded here
rather than left in scratch because the prompt is the durable artifact — an
unbounded prompt is what cost this OBPI nine hours, so a later session must not
have to re-derive this one or fall back to an earlier round's wording.

The round it was written for was dispatched and then stopped by the operator
before producing a verdict, so no round-6 receipt exists.

```text
Adversarial CODE CORRECTNESS review of the working tree. Your job is to REFUTE a BOUNDED correctness claim, not to confirm it. Paste observed command output for every check. This is a defensive review of data-integrity invariants in a governance tool.

READ THE THREAT MODEL FIRST. IT IS BINDING ON THIS REVIEW.

`docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md` § Threat Model.

IN SCOPE — an actor with NO write access to `.gzkit/`. That means everything reachable through the `gz` CLI, through ordinary operation, and through FAILURE: disk errors, interrupted runs, a crash between the declaration write and the ledger append, a failing directory fsync.

OUT OF SCOPE — an actor WITH write access to `.gzkit/`, including appending arbitrary rows to `.gzkit/ledger.jsonl`. This is an ACCEPTED, DISCLOSED RESIDUAL ruled by the project operator: such an actor is inside the trust boundary and the defence is auditability, not prevention. An actor who can append arbitrary ledger rows can forge attestations, completions and receipts across the entire governance surface — the byte floor is the least thing available to them.

**Do NOT report a finding whose reproduction requires hand-writing a ledger row, hand-editing a declaration, or hand-writing a journal.** Four previous rounds did exactly that and the work was wasted. If your strongest attack needs those capabilities, say so plainly and report NOT-REFUTED with that observation, rather than escalating the attacker to manufacture a finding. Reporting an out-of-scope attack as a finding is the specific failure this instruction exists to prevent.

THE CLAIM TO REFUTE, BOUNDED: "within that threat model, a section-ownership floor changes only through the governed `gz content unown` path; and no ordinary failure — a disk error, an interrupted run, a crash between the two stores — can leave the ownership state unrecoverable, silently wrong, or reported as successful when it is not."

Surfaces: `src/gzkit/content/ownership.py`, `src/gzkit/commands/content/unown.py`, and their tests. Latest commit `6a4ab55d`.

ATTACK THESE, all reachable WITHOUT any special access:

1. THE CLI SURFACE. Can `gz content unown` itself raise a floor without recording an attestor and reason, or record one that disagrees with what it wrote? Can any argument combination — a missing section, a section already unowned, a surface that shrank, repeated invocations, concurrent invocations — produce a declaration the loader then rejects?

2. CRASH RECOVERY, EVERY WINDOW. `_commit_transition` journals, writes the declaration, appends the ledger witness, then unlinks the journal. Inject failure at EACH boundary — before the journal write, between journal and declaration, during the atomic replace, on the post-replace directory fsync, during the ledger append, between the append and the unlink — and for each, state whether the resulting state is recoverable by re-running the command, and whether the command's own prose told the truth about what happened. Prior rounds found real defects here twice; assume more remain.

3. IDEMPOTENCE AND RETRY. Re-running after each of those failures must complete the SAME transition, never a second one and never a different one. `_append_event_once` now derives the expected witness from the landed declaration and requires exact semantic equality on an existing id. Attack the retry path.

4. CONCURRENCY. Two `gz content unown` invocations against the same surface, and against different surfaces sharing a ledger. Is the declaration lock sufficient? Can a lost update or an interleaved append occur?

5. ORDINARY CORRUPTION, NOT FORGERY. A truncated declaration, a truncated journal, a truncated final ledger line, a surface edited between the measure and the write, a section renamed, a file with no trailing newline, a non-UTF-8 byte. These arise from crashes and editors, not attackers.

6. TEST QUALITY — the highest-value target this round. FOUR fixtures in this OBPI were found to be silently vacuous: a hand-typed id that failed recomputation before reaching the branch under test; a forged map flipping an already-`unowned` section so the maps were identical; a floor below the live span; and a direction the type forbids. Each produced a PASSING or wrongly-failing test that witnessed NOTHING. Systematically hunt that shape across `tests/content/test_ownership.py` and `tests/commands/test_content_unown.py`: for each test, delete the check it names and confirm it fails FOR THE RIGHT REASON. Report every test that survives its own check's deletion, and every test that fails via a guard other than the one it names.

ALREADY KNOWN — do not re-derive and do not report:
  (a) `record_unowned_total` has no journal and no production caller; deferred to OBPI-0.35.0-05.
  (b) The coordinated declaration+journal edit residual.
  (c) `Ledger.append` never fsyncs — routed to GHI #952.
  (d) `gz validate --ledger` cannot corroborate chain semantics.
  (e) Anything requiring `.gzkit/` write access, per the threat model above.

Report NEW in-scope findings only, ranked by severity. The governing gate converges when NO critical and NO high in-scope findings remain. End with an explicit line "VERDICT: REFUTED" or "VERDICT: NOT-REFUTED" or "VERDICT: REFUTED-WITH-CAVEATS", plus a "Weakest point" section.
```

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- **Ledger append has no transaction boundary across writers or crashes (round-6 adversary
  findings 1 and 2, BOTH `[critical]`, ROUTED OUT to GHI #953 — operator-ruled 2026-09-04).**
  Two distinct in-scope reproductions of one root. (a) CONCURRENT WRITERS: different
  surfaces take different declaration locks, but `_append_event_once` reads and appends the
  SHARED ledger with no ledger-wide lock, so a failing writer's rollback truncation deletes
  a different writer's already-committed row — `thread_A=OSError: injected partial write`,
  `thread_B=success`, `event_B_present=False`. B reported success and its declaration is
  permanently unwitnessed with no journal left to replay. (b) CRASH RESIDUE: an interruption
  leaving partial ledger bytes bypasses `Ledger.append`'s exception rollback; on retry
  `latest_event` raises `JSONDecodeError` and `_replay_pending_transition` catches only
  `OSError`, so recovery loops forever (`retry_exit=1`, `second_retry_exit=1`,
  `journal_after_retries=True`). Neither required `.gzkit/` write access; (b) was reproduced
  by injecting a crash inside `Ledger.append`.
  NOT FIXED HERE, on the precedent GHI #952 set from this same brief: `src/gzkit/ledger.py`
  is declared read-only in § Denied Paths, it is a registered `ledger_integrity` security
  surface, and the defect belongs to every event producer in the repo rather than to the
  ownership path that surfaced it. The adversary's own recommendation is a shared
  transaction boundary, *"not another declaration-local guard"* — a fix of that shape cannot
  land inside this allowlist without breaching it.
  **This is the finding that forced § Threat Model's claim amendment.** Unlike #952, these
  are criticals that falsify the unamended claim in scope, so the claim was narrowed to name
  ledger atomicity as an explicit precondition rather than left asserting something a tier-1
  adversary disproved. Tracked at GHI #953, cross-linked to #952 (neither should be designed
  without the other: the fsync belongs inside the same critical section), open with a blocker
  comment naming the operator's next concrete action.

- **Ledger append is not crash-durable (round-4 adversary finding 3, `[high]`,
  ROUTED OUT to GHI #952 — operator-ruled 2026-09-03).**
  `Ledger.append` writes and flushes the Python stream but never calls `os.fsync`
  (`Ledger.append_has_fsync=False`; independently confirmed — a repo-wide fsync grep
  over the ledger module returns nothing). `_commit_transition` unlinks the recovery
  journal immediately after the append returns, so a power loss can preserve the
  already-fsynced declaration AND the journal deletion while losing the buffered
  ledger row — leaving a raised floor whose witness and recovery journal are both
  absent. NOT FIXED HERE: the ledger module is outside this brief's allowlist,
  it is a registered `ledger_integrity` security surface, and the durability gap
  belongs to every event producer in the repo rather than to the ownership path
  that surfaced it. Tracked at GHI #952.

- **Coordinated declaration+journal edit raises the floor (round-3 adversary finding,
  `[medium-high]`, ACCEPTED RESIDUAL — operator-ruled 2026-09-03).**
  Every check in `_replay_pending_transition` compares the journal against the
  declaration ON DISK. An actor able to write the journal can write the declaration
  too; forging both coherently makes the code mint a genuine `section_ownership_unowned`
  witness and clear the journal, routing around the loader protection installed for
  round-2 finding 1. Reproduced by the adversary at floor 26 -> 1025.
  NOT A BUG TO PATCH AT THIS LAYER: coherence with attacker-controlled state cannot
  prove provenance, which is the same limit that made genesis unanchorable before it
  gained a ledger witness. The operator ruled to ACCEPT: write access to
  `.gzkit/ownership/` is inside the trust boundary, and the defense there is
  AUDITABILITY — the forged transition is recorded in the append-only ledger carrying
  its attestor and reason rather than applied silently. Revisit if the threat model
  ever admits an actor holding canon-directory write access.

- **Content-layer ledger write (architectural debt, deferred to OBPI-0.35.0-05).**
  `record_unowned_total` (`src/gzkit/content/ownership.py`) takes a filesystem `root`
  and calls `emit_unowned_ratchet_updated`, departing from the established split that
  `composer.py` ("caller writes to disk and ledger") and `commands/content/commit.py`
  encode: the content layer stays pure, the command layer writes the ledger. Confirmed
  by independent review 2026-09-02. It fails `.claude/rules/hexagonal-architecture.md`
  operative rule 6 (core testable without an adapter) — the success path cannot be
  exercised without a real `Ledger` file write.
  KEPT DELIBERATELY, not overlooked: within this brief's allowlist there is NO
  command-layer caller for the ordinary decrease-only path. `commands/content/unown.py`
  implements the attested RAISE path (REQ-04/05), a structurally different operation
  with no reason to call `record_unowned_total`, and `src/gzkit/content/composer.py` —
  the analogous real caller — is in this brief's Denied Paths as OBPI-0.35.0-05 scope.
  Moving emission out would leave REQ-0.35.0-04-03's "a ratchet ledger event is
  emitted" unprovable by any `@covers` test this OBPI is authorised to write. The
  natural home is OBPI-0.35.0-05's materialization caller, mirroring `commit.py`.

- **Journal replay accepts an unvalidated declaration (adversary finding 2, `[high]`, OPEN).**
  `_replay_pending_transition` (`src/gzkit/commands/content/unown.py`) checks only that the
  journal is an object carrying `_JOURNAL_FIELDS`, then writes `declaration_json` verbatim and
  appends its claimed event. It never validates attestor/reason, never recomputes the event id,
  never compares the intended transition against the live section span, and never proves the
  journal starts from the declaration currently on disk. A forged journal was accepted with exit
  0, raised the floor `26 -> 1025`, and printed blank provenance. Additionally `_JOURNAL_FIELDS`
  omits `ts` while `_append_event_once` reads `record["ts"]`, so a field-complete journal can
  still escape as a raw `KeyError` instead of the governed three-part refusal.
  INTRODUCED BY THIS SESSION'S OWN REPAIR of adversary finding 2 — the journal that made the
  two-store transaction recoverable became a new unattested write path. Recorded rather than
  fixed because the operator ruled a CHECKPOINT; it is mechanical and should be repaired first
  on resume.

- **Genesis has no provenance anchor (adversary finding 1, `[high]`, RULED AND REPAIRED 2026-09-03).**
  `load_declaration` accepts any declaration whose stored floor equals its own summed unowned
  spans and whose `floor_event_id` is null as a legitimate genesis. Self-coherence is trivially
  re-satisfiable, so a hand edit that flips a section and recomputes the floor loads cleanly with
  no ledger event in existence — reproduced at floor `8637 -> 10182`. The non-null branch is only
  an id/floor equality check and accepts an unrelated event type for a different surface. Together
  these defeat REQ-0.35.0-04-02's claim that the ratchet rises only through the attested path.
  NOT a bug to patch: genesis has no provenance anchor by construction. The repair shape is an
  operator ruling — candidates are a `section_ownership_genesis` ledger event, a commit-SHA
  anchor, or forbidding a null `floor_event_id` after day one.
  **AMENDED 2026-09-04. Everything above is the finding AS RECORDED on 2026-09-02 and is kept
  verbatim; the disposition it states is no longer current.** The operator ruled the next day and
  the repair shipped in `0488f8f4` (*"fix(ownership): anchor the ratchet to ledger state, and
  harden journal replay"*), whose message records the ruling verbatim: *"Operator ruled to anchor
  genesis to a `section_ownership_genesis` ledger event and forbid a null id outright."* That is
  the FIRST of the three candidates listed above, combined with the THIRD. Both halves of the
  finding are closed at HEAD, verified by reading the loader rather than the commit message:
  a null `floor_event_id` is refused outright with no genesis branch remaining
  (`src/gzkit/content/ownership.py:347`), and the non-null branch no longer accepts any event
  that resolves — the event must sit on `_OWNERSHIP_EVENT_TYPES` (`:384`) and its
  `extra["surface"]` must equal the declaration's own surface (`:401`).
  Amended because the entry was still reading `OPEN — DESIGN DECISION` and inviting a ruling the
  operator had already given, which is a live invitation to re-rule and land somewhere other than
  canon. Recorded here rather than deleted: the finding, its reproduction at floor `8637 -> 10182`,
  and the candidate set the ruling chose from are the audit trail for why the loader has the shape
  it now has. **Consequence not to lose: `features/steps/content_unown_steps.py` still seeds the
  `floor_event_id: None` declaration this repair made invalid, so `uv run gz check` has been red
  since `0488f8f4`. Tracked at GHI #957; that path is in this brief's allowlist, so its routing is
  the operator's call.**

- **Declaration write-lock primitive is a PRIVATE cross-module import (structural debt).**
  `src/gzkit/content/ownership.py` imports `_exclusive_store_lock` from
  `src/gzkit/content/corpus_store.py`. Raised as a `minor` finding by the Step-4b task-6
  quality review 2026-09-02, which judged the compromise ACCEPTABLE — the rejected
  alternative was duplicating the platform-conditional `fcntl`/`msvcrt` pair, and two
  implementations of an OS lock drift silently and only manifest under concurrency. Both
  modules are intra-package, so this is not a layer violation. It is nonetheless a real
  liability: the leading underscore is `corpus_store`'s declaration that the symbol is not
  part of its contract, its docstring reasons entirely in corpus terms, and neither ruff
  nor any test would signal breakage if a future refactor renamed or inlined it.
  RIGHT HOME: a neutral module exporting a PUBLIC `exclusive_file_lock(path)` that both
  `corpus_store` and `ownership` call — nothing about `flock`/`msvcrt.locking` on a
  `<name>.lock` sidecar is content-specific. Pure relocation, ~30 lines, zero behaviour
  change. NOT done here because `corpus_store.py` is outside this brief's Allowed Paths.
  Recorded per PRIME DIRECTIVE #6 — the source comment at the import site is a note, not
  a tracker.
  **TRACKED AT GHI #945; CLOSED `fixed` 2026-09-04 by `5fbc5b3c`.** The promotion landed
  exactly as RIGHT HOME describes, at package level (`src/gzkit/file_lock.py`,
  `exclusive_file_lock`) rather than under `content/`, on this entry's own reasoning that
  the primitive is not content-specific. `ownership.py` now imports the public name and
  the source comment this entry called "a note, not a tracker" is gone with it.
  `tests/test_file_lock.py` asserts MUTUAL EXCLUSION between the two callers rather than
  symbol identity — an identity assertion passes on an alias, and only contention proves
  both callers reach the same kernel lock on the same sidecar, which is the drift this
  entry warned about. Nothing in this brief's own REQ set changes: the import site moved,
  the locking semantics did not, and `tests/content/test_ownership.py` and
  `tests/commands/test_content_unown.py` pass unchanged (127 tests across the four
  affected modules, `arb-step-unittest-17ba834f8f4c4a0fb285cc24c20c8554` exit_status=0
  over the full 9301-test suite). Recorded here because this entry was the only place the
  finding lived and it named no tracker.

- **No directory `fsync` after `os.replace` in `write_declaration_atomically`.**
  Raised `minor` by the Step-4b task-6 spec review 2026-09-02. File CONTENTS are fsync'd
  before the rename, but the rename itself is not, and two renames into one directory
  carry no ordering guarantee without it. On host power loss the declaration rename can
  be durable while the journal rename is not, leaving a declaration naming an unresolvable
  `floor_event_id` with no journal to complete it — the bricked state the journal exists
  to prevent, requiring exactly the hand-edit ADR-0.35.0 § Consequences Negative #4 closes.
  SCOPED OUT DELIBERATELY: process-level death (`kill -9`, the adversary's weapon) does not
  reach this window; only power or kernel loss does. Both reviewers graded it minor on that
  basis. Recorded rather than fixed so the durability claim's real boundary is stated
  rather than implied.
  A prior ruling by this session's orchestrator — move it to `unown.py` at Task 3 —
  was CHALLENGED AND OVERTURNED by the reviewer on the reasoning above.
- **`emit_unowned_ratchet_updated` constructs `LedgerEvent` inline (minor).**
  It is the sole outlier among six `emit_*` helpers in
  `src/gzkit/governance/events.py`; every other delegates to a `*_event()` constructor
  in `ledger_events.py`. Forced here because `ledger_events.py` is outside this brief's
  allowlist. No functional drift today; costs standalone unit-testability of the event
  shape and risks drift from the canonical constructor pattern.
- **`no ledger event "{event}" was emitted` step lives outside the sanctioned shared
  home (minor).** `features/content_unown.feature`'s REQ-0.35.0-04-04 scenarios reach
  for this generic ledger-absence assertion, but its only definition is in
  `features/steps/content_retire_steps.py`, not in `features/steps/gz_steps.py` where a
  cross-feature shared step belongs. Behave resolves it through its global step
  registry, so the scenarios pass today; the failure mode if
  `content_retire_steps.py` is ever renamed or deleted is a loud undefined-step
  collection error, never a silent pass. KEPT DELIBERATELY, not overlooked: relocating
  the definition would require deleting it from `content_retire_steps.py`, and that
  file is Gate-4 evidence for OBPI-0.35.0-02, which is already attested-completed —
  editing it here is out of this brief's allowlist and out of scope for a completed
  OBPI's evidence surface. The natural fix is a follow-up that moves the step to
  `gz_steps.py` and updates `content_retire_steps.py`'s own docstring in the same
  patch, under whatever OBPI or GHI next touches that surface.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
