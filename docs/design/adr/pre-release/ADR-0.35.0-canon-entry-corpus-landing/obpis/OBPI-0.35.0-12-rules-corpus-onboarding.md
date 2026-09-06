---
id: OBPI-0.35.0-12-rules-corpus-onboarding
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 12
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/governance/trust_audits/rendition_lineage.py
  - tests/governance/test_rendition_lineage.py
  - src/gzkit/events.py
  - src/gzkit/schemas/ledger.json
  - src/gzkit/governance/events.py
  - src/gzkit/rules/__init__.py
  - src/gzkit/rules/corpus.py
  - src/gzkit/sync_surfaces.py
  - src/gzkit/commands/content/remember.py
  - src/gzkit/commands/content/onboard_rules.py
  - src/gzkit/commands/content/__init__.py
  - src/gzkit/content/composer.py
  - src/gzkit/content/lineage.py
  - src/gzkit/content/landing.py
  - src/gzkit/content/vendors.py
  - src/gzkit/schemas/rules_corpus.json
  - .gzkit/rules-corpus.json
  - .gzkit/corpus/rules.jsonl
  - .gzkit/renditions/rules/
  - data/vendor-manifest.json
  - config/doc-coverage.json
  - tests/test_rules.py
  - tests/test_sync_surfaces.py
  - tests/content/test_rule_corpus.py
  - tests/content/test_vendor_manifest.py
  - tests/commands/test_content_remember.py
  - tests/commands/test_content_onboard_rules.py
  - tests/content/test_tui_affordances.py
  - features/rules_corpus.feature
  - features/steps/rules_corpus_steps.py
  - docs/user/manpages/content.md
  - docs/governance/agent-control-surface-rendering-substrate.md
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-12-rules-corpus-onboarding.md
  - .gzkit/rules/*.md
  - src/gzkit/rules/*.md
  - src/**/AGENTS.md
  - src/**/CLAUDE.md
  - docs/**/AGENTS.md
  - docs/**/CLAUDE.md
  - tests/AGENTS.md
  - tests/CLAUDE.md
  - .gzkit/**/AGENTS.md
  - .gzkit/**/CLAUDE.md
  - .github/AGENTS.md
  - .github/CLAUDE.md
reqs:
  - REQ-0.35.0-12-01
  - REQ-0.35.0-12-02
  - REQ-0.35.0-12-03
  - REQ-0.35.0-12-04
  - REQ-0.35.0-12-05
  - REQ-0.35.0-12-06
  - REQ-0.35.0-12-07
  - REQ-0.35.0-12-08
verification:
  - uv run -m unittest tests.content.test_rule_corpus tests.commands.test_content_onboard_rules tests.commands.test_content_remember tests.test_rules tests.test_sync_surfaces
  - uv run -m behave features/rules_corpus.feature
  - uv run gz validate --vendor-manifest --rendition-freshness --corpus-retirement-witness
  - uv run gz validate --documents --req-kind-discipline
  - uv run gz cli audit
  - uv run gz lint
  - uv run gz typecheck
  - uv run mkdocs build --strict
---

# OBPI-0.35.0-12-rules-corpus-onboarding: Rules Corpus Onboarding

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #12 — "Corpus the `.gzkit/rules/**` family -- the canonical rule files become addressed corpus entries under their own surface, closing the largest remaining under-population named in the SOURCE-OF-TRUTH DIRECTION above; the generated nested `AGENTS.md` render from the corpus rather than from uncorpused rule text (GHI #921)"

## Objective

Onboard canonical rule sources into one addressed, append-only `rules` corpus and
carry their full metadata and markdown through the existing candidate, lineage,
landing and rule-projection paths. The same source population must feed vendor rules
and shared nested AGENTS.md files; generated projections never get independent corpora.

**Dependencies:** 01/02 provide effective-fold and governed retirement semantics;
05/06/07 must deliver generation, lineage verification and landing before this item
can complete. This brief owns their Rule-family integration, not reimplementation
of their core algorithms. Rule records are wholly owned at onboarding; root AGENTS.md's
partial section ratchet is not reused as a rule-population model. 10's classification
resolver and 11's AgentContract shape audit remain separate contracts. 13 orders root sections.

**Authoring disposition:** this is the missing decomposition of already-ratified scope,
not an implementation draw. The adapter design below is a concrete proposal for the
implementation plan to review; no new runtime path is claimed shipped. The breadth
of migration plus delivery warrants focused plan review before execution.

## Lane

**Heavy** — introduces a governed onboarding command and changes the authority read by
rule synchronization. Gates 1–5 apply; corpus attestation and OBPI completion are distinct.

## Allowed Paths

- `src/gzkit/governance/trust_audits/rendition_lineage.py` — **CREATE** by prerequisite OBPI-06; must exist before 12 starts.
- `tests/governance/test_rendition_lineage.py` — **CREATE** by prerequisite OBPI-06; must exist before 12 starts.
- `src/gzkit/events.py`
- `src/gzkit/schemas/ledger.json`
- `src/gzkit/governance/events.py`
- `src/gzkit/rules/__init__.py`
- `src/gzkit/rules/corpus.py` — **CREATE**.
- `src/gzkit/sync_surfaces.py`
- `src/gzkit/commands/content/remember.py`
- `src/gzkit/commands/content/onboard_rules.py` — **CREATE**.
- `src/gzkit/commands/content/__init__.py`
- `src/gzkit/content/composer.py`
- `src/gzkit/content/lineage.py` — **CREATE** by prerequisite OBPI-05; must exist before 12 starts.
- `src/gzkit/content/landing.py` — **CREATE** by prerequisite OBPI-07; must exist before 12 starts.
- `src/gzkit/content/vendors.py`
- `src/gzkit/schemas/rules_corpus.json` — **CREATE**.
- `.gzkit/rules-corpus.json` — **CREATE**.
- `.gzkit/corpus/rules.jsonl` — **CREATE**.
- `.gzkit/renditions/rules/` — **CREATE**.
- `data/vendor-manifest.json`
- `config/doc-coverage.json`
- `tests/test_rules.py`
- `tests/test_sync_surfaces.py`
- `tests/content/test_rule_corpus.py` — **CREATE**.
- `tests/content/test_vendor_manifest.py`
- `tests/commands/test_content_remember.py`
- `tests/commands/test_content_onboard_rules.py` — **CREATE**.
- `tests/content/test_tui_affordances.py`
- `features/rules_corpus.feature` — **CREATE**.
- `features/steps/rules_corpus_steps.py` — **CREATE**.
- `docs/user/manpages/content.md`
- `docs/governance/agent-control-surface-rendering-substrate.md`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-12-rules-corpus-onboarding.md`

New files are the Rule-family adapter, onboarding handler, enrollment schema/state,
flat corpus, family rendition directory and named tests/BDD files. Lineage and landing
modules are supplied by 05/07 before this item; they are extended only at Rule integration seams.
The parser change is confined to the content command group. The TUI roster and doc-coverage
entry are coupled consumers of the new verb, as observed during OBPI-04.

- `.gzkit/rules/*.md` — generated-only; no manual edits.
- `src/gzkit/rules/*.md` — generated-only; no manual edits.
- `src/**/AGENTS.md` — generated-only; no manual edits.
- `src/**/CLAUDE.md` — generated-only; no manual edits.
- `docs/**/AGENTS.md` — generated-only; no manual edits.
- `docs/**/CLAUDE.md` — generated-only; no manual edits.
- `tests/AGENTS.md` — generated-only; no manual edits.
- `tests/CLAUDE.md` — generated-only; no manual edits.
- `.gzkit/**/AGENTS.md` — generated-only; no manual edits.
- `.gzkit/**/CLAUDE.md` — generated-only; no manual edits.
- `.github/AGENTS.md` — generated-only; no manual edits.
- `.github/CLAUDE.md` — generated-only; no manual edits.

Generated-only output allowance: `.gzkit/rules/*.md`,
`src/gzkit/rules/*.md`, and the nested AGENTS.md/CLAUDE.md write set returned by
`nested_agents_md_paths` and its existing redirect writer. These are synchronized
projections, never manually authored under this allowance. Root AGENTS.md/CLAUDE.md
and corpus/brief/ledger files are not included in this generated-output allowance.
The implementation plan must record the concrete generated write set before publication.

## Generated Output Verification

The existing synchronization command also derives `.claude/rules/*.md` from canonical
rules. These vendor files are not editable inputs or a direct authoring allowance;
verify their bytes through the governed sync operation, never patch them by hand.

## Denied Paths

- `.gzkit/corpus/AGENTS.md.jsonl`, `AGENTS.md`, `CLAUDE.md` — this is rule-family onboarding, not root canon editing.
- `src/gzkit/content/models/corpus.py`, `src/gzkit/content/corpus_store.py` — reuse append/fold and baseline identity unchanged.
- `src/gzkit/content/models/rule.py` — do not force full CanonicalRule metadata through the lossy bullet-oriented Rule model.
- `data/instructions_files_budget.json`, `.codex/config.toml` — no budget or Codex configuration change.
- Any hand edit of generated vendor/package/nested instruction files.
- New dependencies, CI files, lockfiles and paths not explicitly allowed above.

## Requirements (FAIL-CLOSED)

1. ALWAYS discover the actual canonical markdown population using the existing rule loader's
   exclusion vocabulary. Exclude AGENTS.md, CLAUDE.md, Python helpers, JSON sidecars and mirrors;
   never hardcode a historical file count. Capture a complete baseline roster and byte hashes.
2. ALWAYS use one flat logical family surface `rules`, stored at `.gzkit/corpus/rules.jsonl`.
   Address entries by stable rule id in `section`, with their canonical relative source path
   in `anchor` and full original rule text in `text`. Validate id/anchor agreement and refuse
   duplicate live ids, duplicate output paths, traversal or paths outside the rule family.
   Flat storage keeps the family visible to existing flat corpus audit discovery.
3. ALWAYS preserve id, description, ordered path patterns, version markers, tables, fenced
   examples and body bytes. Adapt to the existing CanonicalRule/RuleFrontmatter model; do not
   invent a second rule model or convert the document to a list of bullets. Migration
   requires an explicit per-rule migration mapping of tier, classification and witness values,
   reviewed during planning. Existing RuleFrontmatter does not supply these decisions.
   Missing assignments block activation; dry-run reports unresolved assignments. No implicit
   defaults, automatic reclassification or compression.
<!-- gz-validate-skip: command-shape -->
4. IMPLEMENT `gz content onboard-rules` as the governed initial capture/landing entry point,
   with `--dry-run`, `--attestor` and `--attestation-text`. It uses the shared corpus store
   and records capture evidence, then invokes the 05/07 pipeline and activates enrollment
   only after complete verified publication. Never hand-write JSONL. A rerun recognizes
   already-captured identical entries and resumes using recorded evidence without duplicates.
5. EXTEND `content remember` for the enrolled `rules` family so future rule changes remain
   corpus capture, not edits of materialized rule files. The section names the rule id;
   text carries the full rule document. A replacement explicitly names `--supersedes`
   for that rule's effective entry; unrelated targets and duplicate live rule ids are refused.
   Valid capture remains append-first and has no new downstream-governance refusal. Corpus-delta
   attestation applies when onboarding/landing activates the new source, never as a new remember
   precondition or on an unchanged re-render; preserve
   the existing AgentContract capture/advisory contract. Retirement uses the existing verb.
6. KEEP source enrollment explicit in schema-validated `.gzkit/rules-corpus.json`, naming
   the logical family and the verified activation landing. A typed ledger activation event
   independently records the family, complete landing id and baseline roster hash, only after
   verified publication. Cross-check this durable witness against enrollment metadata: a prior
   activation event with a missing marker fails closed. No marker and no activation event
   identifies an unactivated bootstrap state; partial capture alone cannot activate authority.
   An enrolled family with a missing,
   malformed or unverified source/rendition fails closed. A valid empty effective family
   is empty and triggers stale projection cleanup; it never falls back to old rule markdown
   or legacy instruction files. Unenrolled adopters retain their existing bootstrap path.
7. REUSE 05/06/07 for Rule candidates, entry lineage and governed landing. Preserve per-rule
   boundaries and metadata so committed family content can reconstruct CanonicalRule objects
   losslessly. Route every active rule projection through one resolver shared by load_rules,
   sync_all and nested classification. Mirror contents never become source authority.
8. NEVER change unrelated corpus identities or invent separate attestation for each generated
   nested file. Capture/onboarding evidence names the canonical rule ids and corpus delta;
   generated outputs are deterministic projections of that one landing.
9. ALWAYS keep capture-sink/dry-run and apply write sets coherent, preserve existing vendor
   and subtree exclusions and CLAUDE redirects, and make repeated sync byte-stable. An
   interrupted onboarding cannot activate a partially migrated family. Recovery names the
   last complete state and resumes through the shared landing journal, not hand repair.

> STOP-on-BLOCKERS: 05/06/07 must exist with reviewed Rule integration seams before implementation.
> If those interfaces cannot carry this losslessly, surface the concrete conflict in plan review.

## Implementation Boundary

This item is one source-authority migration, with three test groups: complete capture and
identity preservation; verified activation and recovery; lossless vendor/nested projection.
05/06/07 supply generation, validation and publication, including the ledger durability
prerequisite of 07. The rule adapter adds no independent transaction engine, reclassification
heuristic, per-rule compression framework or vendor-specific corpus. Mapping review is an
implementation input under the existing operator policy. Capture works independently of
activation; invalid downstream state blocks activation, never an otherwise valid remember.

## Discovery Checklist

**Parent ADR (read first):**

- [ ] Quote § Decision SOURCE-OF-TRUTH DIRECTION in Implementation Summary.
- [ ] Read § Intent, the 2026-09-01 amendment and checklist item 12.
- [ ] Read parent: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`.

> STOP: do not infer the source from a generated marker; read the parent decision and the loader first.

**Governance:**

- [ ] Read AGENTS.md, the content rendering substrate doctrine and GHI #921's dated correction.
- [ ] Read the Heavy lane plan template and the rules for corpus versus completion attestation.

**Prerequisites:**

- [ ] Verify 01/02 and 05/06/07 delivery, including effective fold, separate lineage and resumable landing.
- [ ] Derive the canonical rule roster via load_rules, excluding NESTED_SURFACE_NAMES.
- [ ] Read the current manifest's Rule route/setpoint; do not infer ownership from a filename glob.
- [ ] Snapshot existing rule metadata, exact source bytes and generated write set for before/after proof.

**Existing Code:**

- [ ] Read rules/__init__.py: RuleFrontmatter, CanonicalRule, load_rules, _classify_canonical_rules,
  _shared_subtree_rules, nested_agents_md_paths and vendor renderers; empty-list fallback can resurrect rules.
- [ ] Read sync_surfaces.py: sync_all and package mirroring order; both vendor and nested readers must switch.
- [ ] Read remember.py's current AgentContract-only file/Pillar validation and the content parser.
- [ ] Read corpus_store.py and corpus_retirement_witness.py: slash-bearing names create nested stores
  which a flat glob will miss; this brief deliberately uses one flat family name.
- [ ] Read the completed 05/06/07 interfaces and tests before designing the family adapter.
- [ ] Read tests/test_rules.py and tests/test_sync_surfaces.py for dry-run/apply and cleanup contracts.

## Quality Gates

### Gate 1: ADR

- [ ] Parent checklist and this brief remain in 1:1 correspondence.

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Each BEHAVIOR REQ has a semantic failing test before implementation and passing evidence afterward.
- [ ] Negative controls exercise the production command path, not a substituted helper.
- [ ] Full tests pass with canonical ARB receipts before completion.

### Gate 3: Docs

- [ ] User documentation carries observed output and strict MkDocs build passes.

### Gate 4: BDD

- [ ] The named feature scenarios prove the delivered behavior through the CLI.

### Gate 5: Human

- [ ] Present concrete evidence and obtain explicit human completion attestation.
- [ ] Record the operator's words verbatim, with evidence enrichment, before completion.

## Verification

The new test modules and feature are implementation deliverables, not checks claimed to pass at authoring.

```bash
uv run -m unittest tests.content.test_rule_corpus tests.commands.test_content_onboard_rules tests.commands.test_content_remember tests.test_rules tests.test_sync_surfaces
uv run -m behave features/rules_corpus.feature
uv run gz validate --vendor-manifest --rendition-freshness --corpus-retirement-witness
uv run gz validate --documents --req-kind-discipline
uv run gz cli audit
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
```

## Demo

The first command is a read-only migration preview. The latter commands demonstrate the
landed family and deterministic projection during implementation; run mutations in an
isolated acceptance fixture until corpus attestation authorizes the repository migration.

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content onboard-rules --dry-run
uv run gz content show rules
uv run -m behave features/rules_corpus.feature
```

## Acceptance Criteria

- [ ] REQ-0.35.0-12-01 [BEHAVIOR]: Given canonical rule files plus generated redirects and non-rule assets, onboarding dry-run identifies exactly the canonical rule ids and paths, reports their byte hashes, excludes projections/assets, reports missing explicit migration assignments and writes nothing; duplicate identities, malformed frontmatter and unsafe output paths are rejected before capture or publication.
- [ ] REQ-0.35.0-12-02 [BEHAVIOR]: Given attested onboarding of a valid family, its complete source metadata and text are stored once per rule in the flat rules corpus through governed append operations; repeating or resuming the same onboarding creates no duplicate live entry and preserves all pre-existing corpus bytes.
- [ ] REQ-0.35.0-12-03 [BEHAVIOR]: Given an enrolled rules family, a valid replacement capture with matching rule id and supersedes target leaves prior rows unchanged and supplies the replacement through the effective view; retirement removes the rule from both vendor and nested delivery, while same-id duplication or cross-rule replacement is refused.
- [ ] REQ-0.35.0-12-04 [BEHAVIOR]: Given full rule documents containing scoped metadata, tables, fenced code and version markers, the family candidate/lineage/landing path reconstructs every CanonicalRule without losing metadata or body content; initial vendor and nested output bytes equal the pre-onboarding baseline, and a later captured body change affects the appropriate projections.
- [ ] REQ-0.35.0-12-05 [BEHAVIOR]: Given enrollment witnessed independently by the typed ledger activation event, missing/corrupt corpus, enrollment data or committed family evidence fails closed with a recovery path; a valid all-retired family removes stale projections without falling back to legacy files, while an unenrolled adopter retains bootstrap behavior.
- [ ] REQ-0.35.0-12-06 [BEHAVIOR]: Given an onboarding failure before final activation, synchronization continues to use the previous complete source state or refuses inconsistent state; resume reuses verified landing evidence without duplicating capture or asking again for the same corpus-delta attestation. Unchanged re-rendering requires no new corpus attestation.
- [ ] REQ-0.35.0-12-07 [BEHAVIOR]: Given the same committed rule family, capture-sink/dry-run and apply enumerate identical generated write sets and a second sync changes no output bytes; modifying a generated mirror cannot alter source authority, and unrelated root corpus fingerprints, subtree exclusions and CLAUDE redirects remain correct.
- [ ] REQ-0.35.0-12-08 [SUPPORT]: docs/user/manpages/content.md and the rendering substrate doctrine document rule-family capture, enrollment, lineage, failure recovery and generated-source boundaries, and the onboarding CLI examples resolve through `gz validate --cli-alignment`. Witnessed by `artifact_edited` citing `docs/user/manpages/content.md` + `gz validate --documents`.

## Tracked Defects

- GHI #921 — parent-ratified corpus ownership half only. Its rules diet and other issue findings are not implicitly completed here.

## Completion Checklist

- [ ] Gate 1 intent and scope recorded.
- [ ] Gate 2 semantic tests and negative controls verified.
- [ ] Lint, type checks, docs and BDD verified.
- [ ] Value narrative and key proof show the delivered capability.
- [ ] Human attestation recorded through the governed completion command.

## Evidence

### Gate 1 (ADR)

Authored on 2026-09-05 at the operator's request to rectify the thirteen-item decomposition.
This is authoring authorization, not an implementation draw or completion attestation.

### Gate 2 (TDD — Red-Green-Refactor)

No implementation test result claimed at authoring.

### Code Quality

Execution receipts will be recorded when this OBPI is implemented.

### Gate 3 (Docs)

Implementation documentation and observed command output remain to be delivered.

### Gate 4 (BDD)

No implementation scenario result claimed at authoring.

### Gate 5 (Human)

No completion attestation recorded.

### Value Narrative

The Objective states the missing capability. Record the measured before/after at implementation.

### Key Proof

Run the Demo after implementation and preserve its observed output with negative-control evidence.

### Implementation Summary

Parent Decision grounding, verbatim:

> SOURCE-OF-TRUTH DIRECTION (operator-ruled this session, stated explicitly rather than inherited): the corpus is the SOURCE that AGENTS.md is generated from.

The specific deliverable is the linked checklist item quoted above. No source implementation
was performed while authoring this brief.

## Human Attestation

- Attestor: pending
- Attestation: pending explicit human completion attestation
- Date: pending
