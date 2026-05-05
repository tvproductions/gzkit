---
id: OBPI-0.0.27-06-distill-skill
parent: ADR-0.0.27
item: 6
lane: Heavy
status: Completed
---

# OBPI-0.0.27-06-distill-skill: gz-complexity-distill Skill

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- **Checklist Item:** #6 — "`gz-complexity-distill` skill (ad-hoc + scheduled invocation, vendor-mirrored)"

**Status:** Draft

## Objective

Author the `gz-complexity-distill` skill at `.gzkit/skills/gz-complexity-distill/` and propagate it to the three vendor mirrors. The skill carries the corpus list, per-project path filters, methodology rationale, and the three distillation-cadence triggers (annual calendar, drift-signal > 25%, judgment); it is operator-invocable ad-hoc and is the canonical surface for OBPI-04's distillation pass.

## Lane

**Heavy** — New operator-facing skill is a surface contract per `.gzkit/rules/cli.md` § "New Subcommand (Heavy Lane)" semantics; foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `.gzkit/skills/gz-complexity-distill/SKILL.md` — canonical skill body
- `tests/skills/test_gz_complexity_distill.py` — REQ-derived assertions
- `docs/user/skills/gz-complexity-distill.md` — operator manpage (coupled-surface per DO IT RIGHT 1a; `tests/test_skill_manpage_coverage.py` fail-closes on every active canonical skill)
- `docs/user/skills/index.md` — index entry linking to the manpage (same coupled-surface check)
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` — brief evidence updates only

> Vendor mirrors at `.claude/skills/gz-complexity-distill/`, `.agents/skills/gz-complexity-distill/`, `.github/skills/gz-complexity-distill/` are **emitted** by `gz agent sync control-surfaces` per `.gzkit/rules/skill-surface-sync.md` Rule #4 and are never listed as direct-edit Allowed Paths. Sync runs in Stage 5; mirror equality is asserted by REQ-07.

## Denied Paths

- `data/exemplar_corpus.json` — corpus is OBPI-02 (skill references it, does not edit)
- `src/gzkit/complexity/measurement.py` — measurement is OBPI-03
- `docs/governance/complexity/distilled-characteristics-*.md` — distillation outputs are produced when the skill runs (OBPI-04's contract), not authored here
- `src/gzkit/governance/trust_audits.py` — link validator is OBPI-07
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `SKILL.md` carries valid frontmatter per the skill schema (`src/gzkit/skills/schema.py` or equivalent), including `skill-version: 0.1.0`, `gz_command:` field naming the canonical CLI invocation, `description:` triggering on the operator phrases the design dialogue identified ("run distillation", "refresh complexity corpus", "distill complexity").
2. REQUIREMENT: The skill body documents the three cadence triggers verbatim from the parent ADR § Decision: (a) annual calendar default with rationale, (b) advisor verdict-frequency drift > 25% from baseline of last distillation with 6-month minimum re-distillation guard, (c) operator-judgment trigger for ground-breaking projects.
3. REQUIREMENT: The skill body lists the corpus by reference (`data/exemplar_corpus.json`) — the skill does not duplicate corpus content (single source of truth) and points the operator at the canonical file.
4. REQUIREMENT: The skill body declares per-project path filters by reference to the corpus entries (corpus is the source of truth); never duplicates the filter content.
5. REQUIREMENT: The skill body documents the methodology rationale (why distillation is agent-driven + operator-attested per OEE) and the OBPI-04 brief shape it is bound to produce.
6. REQUIREMENT: The skill body declares an Output Contract per `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3 — the output form of the destination CLI verb is named (e.g. "writes a dated distilled-characteristics document under `docs/governance/complexity/`").
7. REQUIREMENT: `uv run gz agent sync control-surfaces` propagates the skill to all three vendor mirrors with empty post-sync diff.
8. REQUIREMENT: Tests cover: SKILL.md frontmatter validates against the schema; rule-version + body-marker discipline (if rule-style markers apply); skill body declares all three cadence triggers; skill body cites corpus by reference (does not duplicate content); the three vendor-mirror copies have identical content after sync; the `gz_command` target either resolves to a registered CLI verb (Invariant 1 of `.gzkit/rules/tool-skill-runbook-alignment.md`) **or** is declared `deferred-to-GHI:<#>` in the SKILL.md frontmatter and the named GHI is open and labeled `enhancement` (waiver path per REQUIREMENT 9). Each test decorated with `@covers(REQ-0.0.27-06-NN)`.
9. REQUIREMENT: Tool / Skill / Runbook alignment per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariants 1, 2, 3 holds **or** the destination CLI verb is explicitly deferred via the waiver path: SKILL.md frontmatter carries `gz_command_status: deferred` and `deferred_gh_issue: <#>`; the named GHI is open at brief-completion time; the brief's `## Tracked Defects` section names the GHI and the deferred verb. The waiver path satisfies REQs 04, 05, 08 against the deferred surface; the test suite asserts the waiver shape (frontmatter fields present, named GHI parses) instead of the live verb. Authoring the verb in this OBPI requires brief amendment to expand `Allowed Paths`.
10. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures; tests do NOT spawn the actual measurement pipeline (mocked at the subprocess boundary).
11. REQUIREMENT: NEVER include the operator's personal email in skill body, frontmatter, or fixtures.

> STOP-on-BLOCKERS: if the destination CLI verb the skill routes to is not registered in `src/gzkit/cli/parser_artifacts.py`, surface the gap in `Tracked Defects` and either resolve in this OBPI or open a GHI before merge.

## Discovery Checklist

**Prerequisites**

- [x] OBPI-0.0.27-04 `attested_completed` — `src/gzkit/complexity/distillation.py` (`render_document`, `render_diff_section`, `render_metric_triple`, `_DOCTRINAL_FRAMES`, `DocumentExistsError`, `PerMetricTriple` frozen Pydantic model) and the OBPI-04 brief shape this skill is bound to produce (frontmatter + per-metric triple + cold-start diff + citation-form sections).
- [x] OBPI-0.0.27-02 `attested_completed` — `data/exemplar_corpus.json` carries the 13 pinned-SHA projects (corpus_revision=1, schema_version=1.0.0); `gzkit.models.exemplar.load_corpus(Path)` returns the validated `ExemplarCorpus` model. The skill cites the corpus by path, never duplicates entries (REQ-03).
- [x] OBPI-0.0.27-03 `attested_completed` — `src/gzkit/complexity/measurement.py` (`measure_corpus()`, `CANONICAL_METRICS`) is the engine the deferred destination verb wraps. `BaselineArtifact` model surfaces the per-metric distributions the distillation pass consumes.
- [x] Parent ADR-0.0.27 § Decision Cadence — three triggers (annual calendar default; advisor verdict-frequency drift > 25% from baseline of last distillation with 6-month minimum re-distillation guard; operator judgment for ground-breaking project) are mirrored verbatim into the skill body (REQ-02).
- [x] AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix — foundation+heavy → brief-level Gate 5 walkthrough required regardless of axis-overlap; `_requires_human_obpi_attestation` returns True via the foundation branch.
- [x] AGENTS.md § Operator Economy of Effort — the methodology section documents the agent-drafted-then-operator-attested seam the skill mechanizes (REQ-04 methodology assertion).
- [x] `.gzkit/rules/tool-skill-runbook-alignment.md` Invariants 1, 2, 3 — destination CLI verb deferred under GHI #400 waiver path per REQUIREMENT 9 (amended this OBPI). Operator manpage at `docs/user/skills/gz-complexity-distill.md` linked from `docs/user/skills/index.md` per coupled-surface check `tests/test_skill_manpage_coverage.py`.
- [x] `.gzkit/rules/skill-surface-sync.md` Rule #4 — vendor mirrors at `.claude/skills/`, `.agents/skills/`, `.github/skills/` are emitted by `gz agent sync control-surfaces`; the brief Allowed Paths intentionally exclude them after this OBPI's amendment.

**Existing Code**

- [x] `.gzkit/skills/gz-adr-create/SKILL.md` — foundation-aligned skill body shape reference (frontmatter conventions, body section ordering, references-table form).
- [x] `.gzkit/skills/gz-justify/SKILL.md` and `tests/skills/test_gz_justify_skill.py` — exemplar pair for skill-shape REQ-derived testing (`_parse_frontmatter` helper, `_section_body` H2-extraction pattern, `@covers` decoration model).
- [x] `src/gzkit/sync_skills.py` (`SKILL_REQUIRED_FRONTMATTER_FIELDS`, `SKILL_CAPABILITY_FIELDS`) and `src/gzkit/sync_skills_validation.py` (`validate_skill_frontmatter`) — the canonical frontmatter schema validators the skill body must satisfy (REQ-01 frontmatter test surface).
- [x] `src/gzkit/skill_contract.py` (`SKILL_DESCRIPTION_MAX_CHARS = 1024`) — description length bound asserted by REQ-01 test.
- [x] `tests/test_skill_manpage_coverage.py` — coupled-surface check requiring every active canonical skill to have a manpage at `docs/user/skills/<skill>.md` and an index link at `docs/user/skills/index.md` (DO IT RIGHT 1a — drove the brief amendment expanding Allowed Paths to those two surfaces).
- [x] `src/gzkit/traceability.covers` — `@covers("REQ-X.Y.Z-NN-MM")` decorator validates REQ identifiers at import time against extracted brief Acceptance Criteria; consumed by `gz covers OBPI-... --json` parity gate at Stage 3 Phase 1b.
- [x] `data/behave_coverage_waivers.json` rationale `adr-0.0.27-04-bdd-deferred-to-obpi-06` — OBPI-04 deferred BDD coverage to this OBPI; this OBPI inherits/honors that deferral via the BDD waiver shape (verified PASS via `gz arb step --name behave -- uv run -m behave features/`).

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Runbook entry under "Complexity doctrine surfaces" cites `gz-complexity-distill`

### Gate 4: BDD (Heavy)
- [ ] BDD scenario tagged `@REQ-0.0.27-06-NN` covers a skill invocation against fixture corpus + fixture baseline (or registered as waived if OBPI-04's BDD scenario covers it transitively)

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents --surfaces
uv run gz agent sync control-surfaces  # post-sync diff empty
uv run gz arb step --name unittest -- uv run -m unittest tests/skills/test_gz_complexity_distill.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.27-06-01: Given the canonical skill, when its frontmatter is parsed, then the schema validates and the `skill-version` is `0.1.0`.
- [ ] REQ-0.0.27-06-02: Given the skill body, when the cadence section is parsed, then all three triggers (annual calendar, drift > 25%, judgment) are present with the 6-month minimum re-distillation guard.
- [ ] REQ-0.0.27-06-03: Given the skill body, when the corpus reference is parsed, then it points at `data/exemplar_corpus.json` and does not duplicate the corpus content.
- [ ] REQ-0.0.27-06-04: Given the skill's Output Contract, when the destination CLI verb's default human-readable output is observed against a fixture corpus + baseline, then the observed output matches the form the skill declares — **or** when the verb is deferred (`gz_command_status: deferred`), the SKILL.md Output Contract declares the form the verb is required to produce on its first registration and the brief's `## Tracked Defects` names the GHI carrying that requirement forward.
- [ ] REQ-0.0.27-06-05: Given the skill's `gz_command` field, when resolved against `src/gzkit/cli/parser_artifacts.py`, then a registered CLI verb exists and the runbook prescribes it — **or** the SKILL.md frontmatter carries `gz_command_status: deferred` and `deferred_gh_issue: <#>` naming an open GHI labeled `enhancement` against `tvproductions/gzkit`, and the test suite asserts the waiver shape.
- [ ] REQ-0.0.27-06-06: Given a clean working tree, when `uv run gz agent sync control-surfaces` runs, then the three vendor-mirror copies are byte-identical to the canonical and the post-sync diff is empty.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict clean; runbook entry added
- [ ] Gate 4: BDD scenario or waiver
- [ ] Gate 5: TTY + `ATTEST` captured

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR observations + final unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict output + runbook diff hunk
```

### Gate 4 (BDD)
```text
# Paste behave output or waiver entry
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs
```

### Value Narrative

<!-- Problem before: distillation cadence existed only as ADR § Decision prose with no operator-runnable surface; running distillation required reconstructing the corpus + filters + methodology from memory each time. Capability now: a vendor-mirrored skill that carries the corpus reference, cadence triggers, and methodology rationale, invocable ad-hoc by the operator and aligned with OBPI-04's brief contract. -->

### Key Proof


```
$ uv run gz covers OBPI-0.0.27-06-distill-skill --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"parity={d['by_obpi'][0]['covered_reqs']}/{d['by_obpi'][0]['total_reqs']} ({d['by_obpi'][0]['coverage_percent']}%)\")"
parity=6/6 (100.0%)

$ uv run gz arb step --name unittest -- uv run -m unittest tests/skills/test_gz_complexity_distill.py -v 2>&1 | tail -3
Ran 21 tests in 0.003s
OK
arb step name=unittest exit_status=0 receipt=arb-step-unittest-b223c18801d64682be415c2bec0a22fb

$ uv run gz arb step --name unittest -- uv run -m unittest -q 2>&1 | tail -2
Ran 4223 tests in 32.054s
arb step name=unittest exit_status=0 receipt=arb-step-unittest-a3f6656f2aca41d18e2989ef34804cc3

$ uv run gz arb step --name behave -- uv run -m behave features/ 2>&1 | tail -2
arb step name=behave exit_status=0 receipt=arb-step-behave-7a4b86f8152341e6b520eef3b507beb4

$ uv run gz agent sync control-surfaces 2>&1 | tail -2
Sync complete.

$ for mirror in .claude .agents .github; do diff .gzkit/skills/gz-complexity-distill/SKILL.md $mirror/skills/gz-complexity-distill/SKILL.md && echo "EQUAL: $mirror/skills/gz-complexity-distill/SKILL.md"; done
EQUAL: .claude/skills/gz-complexity-distill/SKILL.md
EQUAL: .agents/skills/gz-complexity-distill/SKILL.md
EQUAL: .github/skills/gz-complexity-distill/SKILL.md
```

Receipts: `arb-ruff-fdc95ce9a7464c98b33fb565882eb4b5`, `arb-step-typecheck-e750b859a7994859a971b73040f9c54f`, `arb-step-unittest-a3f6656f2aca41d18e2989ef34804cc3`, `arb-step-unittest-b223c18801d64682be415c2bec0a22fb`, `arb-step-mkdocs-69a374b405b045ba9abf25ef41e86802`, `arb-step-behave-7a4b86f8152341e6b520eef3b507beb4`.

### Implementation Summary


- Files created: `.gzkit/skills/gz-complexity-distill/SKILL.md` (canonical operator-facing skill body — frontmatter with `skill-version: "0.1.0"`, `gz_command_status: deferred`, `deferred_gh_issue: 400`; body covering all three cadence triggers verbatim from parent ADR § Decision Cadence, corpus reference at `data/exemplar_corpus.json` without duplication, per-project path-filter reference, agent-drafted methodology with operator-attested OEE binding, Output Contract naming the dated distilled-characteristics output dir, OBPI-04 brief shape reference, waiver disclosure pointing at GHI #400); `tests/skills/test_gz_complexity_distill.py` (21 REQ-derived tests across 6 test classes — TestSkillFrontmatter, TestCadenceTriggers, TestCorpusReference, TestOutputContractWaiver, TestDeferredCommandWaiver, TestVendorMirrorEquality + a doctrine TestNoOperatorPersonalEmail class without @covers since REQ-11 is not in Acceptance Criteria); `docs/user/skills/gz-complexity-distill.md` (operator manpage required by `tests/test_skill_manpage_coverage.py` — added under DO IT RIGHT 1a coupled-surface coherence after Stage 3 surfaced the gap); `.claude/plans/plan-OBPI-0.0.27-06-distill-skill.md` (approved plan with destination-in-mind disclosure + rejected alternatives per gz-plan-audit Step 6a).
- Tests added: 21 (4+4+3+4+3+1 across the six REQ-coverage classes + 2 doctrine assertions); REQ→@covers parity gate 6/6 (100.0%) verified by `gz covers OBPI-0.0.27-06-distill-skill --json`; full unittest sweep 4223 PASS; OBPI-scoped sweep 21 PASS in 0.003s.
- Vendor mirror sync: `gz agent sync control-surfaces` propagates the canonical SKILL.md to `.claude/skills/`, `.agents/skills/`, `.github/skills/` byte-equal — REQ-06 satisfied by post-sync diff empty + TestVendorMirrorEquality.test_each_vendor_mirror_matches_canonical PASS.
- Brief amendments this session (5 total, course-corrections logged to `.gzkit/insights/agent-insights.jsonl`): (1) removed vendor-mirror entries from Allowed Paths per `.gzkit/rules/skill-surface-sync.md` Rule #4; (2) amended REQs 04/05/08 to permit waiver-with-tracked-GHI path; (3) added GHI #400 to Tracked Defects; (4) added `docs/user/skills/gz-complexity-distill.md` and `docs/user/skills/index.md` to Allowed Paths under DO IT RIGHT 1a; (5) removed unused `scripts/` Allowed Path entry; expanded Discovery Checklist with Prerequisites + Existing Code subsections per `gz obpi validate --authored` contract.
- GHI filed: #400 — Author destination CLI verb for gz-complexity-distill skill (deferred from OBPI-0.0.27-06); body cites OBPI-06 REQUIREMENT 9 waiver path, names `src/gzkit/cli/parser_artifacts.py` as registration surface, names manpage + runbook + Output Contract conformance test as acceptance criteria. Filed at `tvproductions/gzkit` per `.gzkit/rules/gh-cli.md`.
- Date completed: 2026-05-05
- Attestation status: operator attested at Stage 4 (`attest completed`); Gate 5 fired foundation+heavy via brief-level walkthrough; --attestor-present co-presence proxy satisfied by active pipeline marker at `.claude/plans/.pipeline-active-OBPI-0.0.27-06-distill-skill.json`.
- Defects noted: GHI #400 (deferred destination CLI verb — tracked, waiver path declared in skill frontmatter); plan-audit's path-existence check has no carve-out for to-be-created paths and inherently FAILs on new-file OBPIs until files exist (worked around by creating files first, then re-running audit — surfaceable as a follow-up GHI but not blocking).

### Closing Argument

<!-- One paragraph: why the operator-runnable skill (vs CLI-verb-only) is the load-bearing surface for cadence triggers — the skill carries methodology rationale and corpus references the CLI flag cannot — and why mirror sync discipline is the structural defense against vendor-surface drift. -->

## Tracked Defects

- **GHI #400** — Author destination CLI verb for `gz-complexity-distill` skill.
  Filed 2026-05-05 against `tvproductions/gzkit` per OBPI-06's
  `gz_command_status: deferred` waiver path (REQs 04/05/08, REQUIREMENT 9).
  The skill ships against the waiver shape; on GHI #400 closeout the skill
  amends `gz_command_status: deferred` → live `gz_command:` and the
  `deferred_gh_issue:` field is removed.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Stage 4 ceremony presented per the canonical foundation+heavy template; operator witnessed the value narrative naming the cadence-doctrine-without-runnable-surface gap closure, the byte-equal vendor-mirror sync diff, the REQ→@covers parity gate at 6/6 (100.0%), and the GHI #400 waiver-path frontmatter discipline. All ARB receipts cited inline: lint clean (arb-ruff-fdc95ce9a7464c98b33fb565882eb4b5), typecheck clean (arb-step-typecheck-e750b859a7994859a971b73040f9c54f), full unittest 4223/4223 (arb-step-unittest-a3f6656f2aca41d18e2989ef34804cc3), OBPI-scoped 21/21 (arb-step-unittest-b223c18801d64682be415c2bec0a22fb), mkdocs strict clean (arb-step-mkdocs-69a374b405b045ba9abf25ef41e86802), behave heavy-lane clean (arb-step-behave-7a4b86f8152341e6b520eef3b507beb4). Brief amendments under operator-selected Option C: vendor mirrors removed from Allowed Paths per skill-surface-sync.md Rule #4; REQs 04/05 amended for waiver-with-tracked-GHI shape; GHI #400 filed at tvproductions/gzkit and added to Tracked Defects; manpage surfaces added to Allowed Paths per DO IT RIGHT 1a coupled-surface coherence with tests/test_skill_manpage_coverage.py; unused scripts/ entry removed. Course-correction logged to .gzkit/insights/agent-insights.jsonl per Behavior Rule 11.
- Date: 2026-05-05

---

**Brief Status:** Completed

**Date Completed:** 2026-05-05

**Evidence Hash:** -
