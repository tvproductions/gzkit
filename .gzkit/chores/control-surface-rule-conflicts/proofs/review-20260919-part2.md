# Rule-pair review, partition 2 — 2026-09-19

Persona: quality-reviewer. Entire 28-file population read, 2,244 lines; every
owned pair (126 of 378, zero-based index modulo 3 = 2) has an individual
substantive disposition in `review-20260919-part2.json`, with source hashes.
A combined read that truncated was reread in smaller batches. This is semantic
review coverage, not a guarantee of absence. No rules, source, issue or OBPI
state was changed. Trust and state doctrine and the prior summary/matrix were
read. The separate large advisory scorecard read truncated and is not represented
as a complete read or used as evidence of current implementation.

## R01 — carried, pairs 5 and 161

- `.gzkit/rules/chores.md:25` labels `src/gzkit/chores/<slug>/`
  **"Canonical (package)"** and **"Authoritative templates"**; lines 126–127
  prescribe **"Canonical chore packages live in `src/gzkit/chores/<slug>/`"**.
- `.gzkit/rules/skill-surface-sync.md:29–35` labels `.gzkit/chores/<slug>/`
  **"Canonical (edit here)"**, with package copy **"generated"**. Generated
  `.gzkit/rules/AGENTS.md:49–55` repeats that table.
- Worked case: amend a canonical-class chore's CHORE.md in project, then have
  invalid acceptance.json in the same slug. Authoring at the package path and
  authoring at the project path are opposite prescriptions. Doctor identifies
  DAMAGED and replaces all three differing package-controlled files, including
  the otherwise valid edited CHORE.md; sync subsequently writes project to package.
- Implementation read: `src/gzkit/commands/chores.py:496–533` defines the damaged
  predicate and repair; `:594–595` invokes repair only for DAMAGED. Healthy byte
  disagreement is not enough. `src/gzkit/sync_surfaces.py:827–940` reads project
  canonical surfaces; its chore loop `:911–928` copies canonical-class files into
  package. No destructive doctor probe was run. No single coherent writer/recovery
  authority was established by these two functions.
- Recommendation: resolve authoring provenance and damaged-file recovery as one
  coupled GHI; preserve project-first execution and proof preservation. Prior R01
  / GHI #448 lineage, not evidence of current encounter frequency. Severity:
  theoretical under this chore's taxonomy.

## R21 — carried, resolved authority, pairs 14 and 305

- `.gzkit/rules/model-selection.md:44` required example: `skill-version: 0.1.0`
  at top level.
- `.gzkit/rules/skill-surface-sync.md:20`: **"Skills: `metadata.skill-version`, a
  quoted `X.Y.Z` string nested under `metadata:`"**; generated subtree repeats it
  at `.gzkit/rules/AGENTS.md:41`.
- Worked case: copying the version field from the required model example omits
  the nested version consumed by audit. The example therefore directs an edit the
  companion rule rejects.
- `src/gzkit/skills_audit.py:478–501` reads `metadata.skill-version`, and emits
  `SKA-METADATA-SKILL-VERSION-MISSING` if absent. This specific function was read;
  no claim that all other frontmatter fields in the illustrative example satisfy
  the full skill schema.
- Recommendation: correct the example to quoted nested metadata; retain model
  policy. GHI #921 lineage. Severity theoretical, no fresh occurrence count.

## New candidate — follow-up GHI does not satisfy same-patch skill coverage, pair 185

- `.gzkit/rules/cli.md:83`: **"Seven obligations fire for a new verb, each
  mechanically checked; satisfy them in the authoring patch."** Line 91 names a
  wielding skill or explicit `_NO_SKILL_VERBS` waiver.
- `.gzkit/rules/tool-skill-runbook-alignment.md:66`: **"author the skill in the
  same patch or file a follow-up GHI"**. The same sentence explicitly calls
  `cli.md` the authority, so this is a stale alternative with settled precedence,
  not an unresolved governance choice.
- Worked case: a newly registered, nondeprecated, unwaived command has no skill;
  author files only a follow-up issue. The alternative appears satisfied while
  the authoring-patch rule is not.
- Read `src/gzkit/governance/trust_audits/cli.py:427–530`: known paths derive from
  the parser; `audit_skill_alignment` admits a wielding reference or explicit
  waiver and reports a `skill_alignment` error otherwise. Issue existence is not
  an admission channel in that function. No new command was added or gate state
  mutated for this audit.
- Recommendation: remove the follow-up-only alternative; describe same-patch
  skill/waiver admission consistently. Severity theoretical; no live occurrence
  or new issue status inferred. Root assigns the final finding ID after prior-art.

## Additional resolved-authority observations

- Pair 332, MX/Claude: `mx-mode.md:68–71` says **"Fix what you know **AND** what
  you find"** and **"\"Not my work\" / \"out of scope\" stays **forbidden in the
  bay**"**; `:83` says **"Do not exit the hangar while any detectable defect
  remains unfixed"**. `CLAUDE.md:13` says **"hold the requested scope, report
  unrelated findings rather than fixing them"**. Concrete case: unrelated CLI
  defect found during a bounded MX repair. Root `AGENTS.md:12` explicitly requires
  coupled correctness but routing unrelated defects. Claude inherits it; root is
  authority. Reconcile stale MX breadth against root, rather than using a marker
  as permission to expand scope. No MX runtime or skill execution was tested.
- Pair 146 retains R23 through Claude's root inheritance: release rule `:50`
  says **"attested at Gate 5"**; root `:156` restricts Gate5 to completed OBPI/ADR
  work. A GHI patch release needs review, not an invented OBPI attestation.
- Pair 215 retains the R07 precedence disposition: Pythonic explicitly makes
  function/module limits guidance and refers threshold claims to the table;
  a stale numeric paraphrase remains a dated-record hygiene concern, not evidence
  of two active runtime gates. No threshold values remeasured in this partition.
- Pairs 353/374 retain the prior token-reaper observation: `token-block-discipline.md:46`
  authorizes any starting agent to reap/reclaim; root `AGENTS.md:130` forbids
  independently claiming/releasing OBPI locks. Skill-authoring and Claude both
  point to/inherit root. This reading grants no automatic-reaper implementation
  verdict and no lock operation was performed.
