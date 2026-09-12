# Rule-pair review — partition 0

Local source witness: `464dd4ff8fa2ee12d98afe99a867280e1b82b431`. Read all 29 inventory files; hashes still match. Reviewed 203 even-indexed pairs. No repo edits or live state mutations.

## Findings

### P0-01 (blocking)

**A:** .gzkit/rules/chores.md:25,116-117 — Canonical chore packages live in `src/gzkit/chores/<slug>/` (shipped in the wheel). Project-specific overrides go in `.gzkit/chores/<slug>/`.
**B:** .gzkit/rules/AGENTS.md:56,62,150 (duplicate of skill-surface-sync.md:35,41,129) — Operator-authored content present at `.gzkit/<surface>/` — the source of truth

Amend a portable CHORE.md under a slug whose project acceptance.json is damaged. chores.md seats authority in the package; the sync rule seats it in .gzkit. doctor repairs the damaged slug from package bytes and can replace the amended project CHORE.md; sync copies project bytes into the package. The damage predicate is necessary: doctor does not overwrite every healthy differing slug.

Evidence: GHI #448; local SHA 464dd4ff8fa2ee12d98afe99a867280e1b82b431
Observed mechanism: Split by operation: src/gzkit/commands/chores.py:494-513 writes package bytes to project files, invoked only for DAMAGED at :574-575; src/gzkit/sync_surfaces.py:903-927 copies canonical-class project files to package. Both bodies read. No unique winner.
Suggested correction: Reconcile the authoring-source wording and the damaged-slug repair direction under a GHI; keep project-first runtime resolution separate from source authority.

### P0-02 (episodic)

**A:** .gzkit/rules/model-selection.md:40-46 — skill-version: 0.1.0
**B:** .gzkit/rules/skill-surface-sync.md:21 (duplicated at .gzkit/rules/AGENTS.md:42) — Skills carry the marker nested under `metadata:` as `metadata.skill-version`

An author copies model-selection.md’s prescribed SKILL.md frontmatter and changes model tier. Its version is a top-level key. The sync rule says that exact placement is invisible and requires metadata.skill-version. The skill audit reports missing metadata.skill-version.

Evidence: GHI #921; local SHA bb85e660e63e0642a4321954606bede4b5c60a24
Observed mechanism: src/gzkit/skills_audit.py:479-492 reads metadata.skill-version and emits SKA-METADATA-SKILL-VERSION-MISSING when absent. src/gzkit/sync_skill_validation.py:225-235 validates metadata.skill-version when present but does not itself require presence. Both bodies read; do not attribute the missing-field gate to both.
Suggested correction: Correct the model-selection frontmatter example to nest metadata.skill-version; sync derived copies. No model-policy change is needed.

### P0-03 (episodic)

**A:** .gzkit/rules/adr-audit.md:24,29 — uv run gz arb step --name unittest -- uv run -m unittest -q
**B:** .gzkit/rules/tests.md:19; AGENTS.md:285,289 — the canonical "Tests pass" invocation runs `unittest-parallel` (GHI #856)

Run ADR audit Step 2 today exactly as prescribed. The emitted unittest step receipt names the serial command, while current attestation canon requires the pinned parallel command. A fresh serial receipt is not admitted by the retired-canon exception, which only admits receipts timestamped before 2026-08-27.

Evidence: GHI #856; local SHA 21ade0551153b15ebf3c1e46be6a30c00e133b43
Observed mechanism: src/gzkit/canonical_steps.py:110 selects unittest-parallel; src/gzkit/arb/validator.py:217-268 compares current command and permits retired command only before its retirement timestamp (retirement entry :95). Actual table and predicate read.
Suggested correction: Replace the stale ADR audit invocation with the current canonical command and synchronize mirrors. Retain historical pre-cutover receipts.

## Prior odd-row dispositions

### R01 — carried

The opposite canonical authoring directions persist. Correct the previous overstatement: doctor only takes its destructive repair arm after the slug is classified DAMAGED, not merely because CHORE.md differs.

Sources: .gzkit/rules/chores.md:25,116-117; .gzkit/rules/skill-surface-sync.md:35,41,129; src/gzkit/commands/chores.py:494-513,574-575; src/gzkit/sync_surfaces.py:903-927
Evidence: GHI #448; SHA 464dd4ff8fa2ee12d98afe99a867280e1b82b431

### R03 — retired

chores.md:133 now says "Manpage — `docs/user/manpages/chores.md`", consistent with governance-core.md:55 "Manpages use `<verb>.md` — never a `gz-` prefix". The old dead-pointer example is gone. The manpage scanner still enumerates docs/features/skills rather than rules (:249-279), so retirement proves this pointer repaired, not scanner expansion.

Sources: .gzkit/rules/chores.md:133; .gzkit/rules/governance-core.md:55; src/gzkit/governance/trust_audits/cli.py:249-279
Evidence: GHI #532; SHA 464dd4ff8fa2ee12d98afe99a867280e1b82b431

### R05 — refuted

The old reading treated broad ownership as permission to cross a brief. AGENTS.md:159 explicitly says "Follow the brief: active briefs define allowed/denied paths"; :301 now names the live-owner operator wait; :139 limits a narrow skill to its task; :373 forbids agent-initiated OBPI work. These specific limits coexist with :36 "If fixing requires updating 3 docs, do it". Worse, the claimed mechanical winner was inverted: orphaned_implementation.py:175 SELECTS edits inside allowed paths, then audits claim + force-release without completion. It does not gate edits outside the allowlist.

Sources: AGENTS.md:36,139,159,301,373; src/gzkit/governance/trust_audits/orphaned_implementation.py:61,165-176,203-239
Evidence: GHI #438; GHI #864; SHA 9e1e017a23fdb99cf99e8364d4d6437374e3b792

### R07 — refuted

The full rule already supplies an explicit interim precedence: pythonic.md:55-56 says "treat <=300 as binding (it gates), <=50 and <=600 as guidance, and cite the table — not this rule — for any threshold claim." Thus the 45-line/700-line example does not give two operative gate instructions. Residual implementation/doctrine limitations remain disclosed: class-size uses limit=300 and advisor inspects radon_cc only. The old row’s numeric assertion is additionally stale: JSON now gives radon_raw_nloc 1031.9 WARN and 3143.82 BLOCK, while pythonic.md:36 still describes the former as BLOCK. Do not copy that old measurement.

Sources: .gzkit/rules/pythonic.md:31-56; .gzkit/rules/complexity-thresholds.md:36-44; .gzkit/rules/complexity-thresholds.json:112-122; src/gzkit/governance/trust_audits/code_quality.py:129-163; src/gzkit/commands/complexity_advise.py:47,126
Evidence: GHI #404; GHI #405; SHA 9b1cbc32acdef3bb2ebb1daccc63c452efbdff9f

### R09 — carried

The authoring case remains contradictory when a routing skill declares JSON: Invariant 3 demands JSON as default, whereas CLI doctrine reserves JSON for --json. This is a permitted-form authoring example, not evidence that a current skill shipped the mistake. Existing GHI #202 is enforcement lineage only, not an observed JSON conflict; downgrade from episodic to theoretical.

Sources: .gzkit/rules/cli.md:81-82; .gzkit/rules/tool-skill-runbook-alignment.md:29,33-48
Evidence: GHI #202; SHA 464dd4ff8fa2ee12d98afe99a867280e1b82b431

No demonstrated mechanical winner for output-form arbitration. tool-skill-runbook-alignment.md:33-48 explicitly declares Invariants 2/3 advisory. No code winner is inferred from a search.

### R11 — refuted

complexity-thresholds.md:97 forbids silent amendments; skill-surface-sync.md:20 requires version bumps. Neither orders the opposite of the other. The old worked example establishes an absent enforcement channel, not contradictory directives. Read canonical_rule_files: it scans authored *.md only; that remains the exact scope limit. Do not manufacture a rule conflict by treating an uninspected JSON file as authorization to edit silently.

Sources: .gzkit/rules/complexity-thresholds.md:97; .gzkit/rules/skill-surface-sync.md:20-27; src/gzkit/validators/rule_version_markers.py:87-91
Evidence: GHI #307; SHA 464dd4ff8fa2ee12d98afe99a867280e1b82b431

### R13 — refuted

AGENTS.md:91 explicitly says stdlib is chosen "absent named rationale to depart" and :101 names Pydantic as "the explicit named departure". models.md:14 prescribes that same ratified choice; hexagonal-architecture.md:43-45 repeats the exception. A missing reciprocal pointer cannot produce opposite required behavior when the root’s exception is read.

Sources: AGENTS.md:91,101; .gzkit/rules/models.md:14; .gzkit/rules/hexagonal-architecture.md:43-45
Evidence: GHI #448; SHA 464dd4ff8fa2ee12d98afe99a867280e1b82b431

### R15 — refuted

security-sensitivity.md:23 explicitly scopes the briefless GHI case: "state the sensitivity in the commit body and cite the GHI". The :42 ban on editing the registry without declaring sensitivity can be satisfied through that declared channel; it does not require creating a brief. The limitation is mechanical, already disclosed: current record walker iterates briefs and reads sensitivity frontmatter, not commit bodies. Its module has moved from validate_cmd.py to validate_sensitivity.py.

Sources: .gzkit/rules/security-sensitivity.md:21-23,42; AGENTS.md:362; src/gzkit/commands/validate_sensitivity.py:31-74
Evidence: GHI #682; SHA 464dd4ff8fa2ee12d98afe99a867280e1b82b431

### R17 — carried

Internal chronology conflict persists: the same existing validator is both shipped and forthcoming. Its claimed subject also differs from the code: the rule names root AGENTS.md for shape, but code applies shape to the package template and only budget to the root. Do not repeat the old conclusion that a diagnostic path itself commands editing a generated file; edit .gzkit/templates and sync is available under the authoritative source rule.

Sources: .gzkit/rules/agents-md-map-doctrine.md:34,38-42; .gzkit/rules/skill-surface-sync.md:30; src/gzkit/governance/trust_audits/agents_md_map_conformance.py:99-147
Evidence: GHI #533 (historical lineage only); SHA 464dd4ff8fa2ee12d98afe99a867280e1b82b431

src/gzkit/governance/trust_audits/agents_md_map_conformance.py:99-146: package template shape checks at :129-138, root budget at :141-147. This demonstrates implemented behavior, not correct doctrine fulfillment.

### R19 — retired

governance-core.md:21 explicitly excludes operator-authored repo canon, naming "the active campaign plan", from the externally-authored tool-output restriction. That agrees with AGENTS.md:358. Current :371 and :373 further constrain campaign sequencing/OBPI initiation, and do not reintroduce the old external-output conflict. The old cited SHA 1c36e0c4b does not resolve in this checkout; use current local source evidence instead.

Sources: .gzkit/rules/governance-core.md:21; AGENTS.md:358,371,373
Evidence: SHA 464dd4ff8fa2ee12d98afe99a867280e1b82b431

## Limits

- Read-only static review: no runtime mutation, no claimed fresh gate execution, no external issue-state lookup.
- All 29 files read; every truncated content segment was recovered by narrower reads.
- No ADR implementation-intent samples selected or read.
- Old R09 authoring-case remains hypothetical and is explicitly theoretical; GHI lineage does not prove occurrence.

Full pair-by-pair record and source hashes: `/tmp/gz-health-rules-part0.json`.
