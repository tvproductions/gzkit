---
id: ADR-pool.obpi-req-taxonomy-scope-fence
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.obpi-req-taxonomy-scope-fence: OBPI REQ Taxonomy: Scope-Fence vs Feature REQs in Coverage Model

## Status

Pool

## Intent

The OBPI Decomposition Mandate (`docs/governance/GovZero/obpi-decomposition-matrix.md`) encourages right-sizing implementation units across multiple OBPIs, and the brief-authoring template encourages enumerating REQs that pin scope boundaries between sibling OBPIs. The audit-check coverage model (`uv run gz adr audit-check`, backed by `.gzkit/rules/adr-audit.md` and `.gzkit/rules/tests.md` § Invariant 6f) assumes all REQs are persistent feature claims testable at HEAD: an uncovered REQ either gets a `@covers`-decorated test or the assertion is re-derived per Invariant 6f. The two surfaces are mutually consistent in isolation but produce an unresolvable advisory-coverage gap at integration when an ADR decomposes across N OBPIs that touch related surfaces.

ADR-0.0.32 surfaces the gap concretely (GHI #467, 2026-05-15). `uv run gz adr audit-check ADR-0.0.32` exits 0 PASS but reports 8 advisory uncovered REQs (130/138 = 94.2% coverage). Reading each REQ's text in its parent brief reveals a common shape — every one of them is a *scope-fence* assertion: a negative-existence claim or byte-identity claim about an intermediate handoff state between OBPIs.

| REQ | Brief | Claim text (paraphrased) |
|---|---|---|
| `01-07` | `OBPI-0.0.32-01` | `src/gzkit/templates/skill.md` continues to exist (its deletion is OBPI-02's job) |
| `02-03` | `OBPI-0.0.32-02` | `src/gzkit/templates/skill.md` is deleted |
| `03-04` | `OBPI-0.0.32-03` | NO `CORE_RULES`/`scaffold_core_rules`/`_iter_canonical_rule_slugs` exists in `src/gzkit/rules/__init__.py` after this OBPI (those are OBPI-04's scope) |
| `03-05` | `OBPI-0.0.32-03` | `src/gzkit/commands/init_cmd.py` is byte-identical to pre-OBPI version |
| `09-03` | `OBPI-0.0.32-09` | NO `CORE_PERSONAS`/`scaffold_core_personas`/`_iter_canonical_persona_slugs` added in this OBPI |
| `09-04` | `OBPI-0.0.32-09` | `src/gzkit/commands/init_cmd.py` is byte-identical to pre-OBPI version |
| `11-06` | `OBPI-0.0.32-11` | NO `CORE_TEMPLATES`/`scaffold_core_templates`/`_iter_canonical_template_slugs` exists post-OBPI |
| `11-08` | `OBPI-0.0.32-11` | `pyproject.toml` is byte-identical to pre-OBPI version (no wheel-include extension) |

Each REQ asserts either (a) a file's existence at a moment that no longer exists, or (b) byte-identity of a file at an intermediate OBPI boundary that subsequent OBPIs have intentionally changed. Neither Invariant 6f remediation path applies: a test at HEAD cannot assert "OBPI-03 left `init_cmd.py` byte-identical to pre-OBPI-03" because OBPI-04, -05, -14 have all touched the file by design. The class is structurally unfalsifiable post-integration, yet the REQ was the *right* authoring shape during decomposition — it prevented scope creep, made the OBPI handoff explicit, and let `gz validate --documents` accept the brief.

`gz adr audit-check` correctly labels these advisory (non-blocking) — the gap is honest. But the doctrine has no clean home: scope-fence REQs are not test-derivable, not removable (they were the right authoring shape), and not exemptible under any of the five existing legitimate-authoring exemptions in `.gzkit/rules/adr-audit.md` § Legitimate-authoring exemptions (those govern `@covers` decorator backfill, not REQ-shape exemption).

This ADR is the design home for the doctrine extension that distinguishes *scope-fence REQs* (transient OBPI-handoff invariants, used during decomposition to prevent scope creep, structurally untestable at HEAD post-integration) from *feature REQs* (persistent capability claims testable at HEAD). The class will recur in any ADR decomposed across more than 2-3 OBPIs that handle related surfaces — ADR-0.0.32's 8 instances are the first concrete sample, not the last.

## Decision

_(Pool — design conversation in progress. Concrete decision items to be authored on promotion. Open surface decisions:)_

- **Mechanization surface.** Schema-level marker (Path A) vs. doctrine-only authoring guidance (Path B) vs. composition of both — see Alternatives.
- **Definition of "scope-fence REQ".** The working definition above (negative-existence claim OR byte-identity claim at intermediate OBPI handoff) is grounded in 8 observed instances on ADR-0.0.32. Promotion authors should re-derive against any additional samples surfaced before promotion.
- **Coverage-report behavior.** If a marker is adopted (Path A), scope-fence REQs are excluded from coverage reporting entirely (not even advisory) — they are structurally untestable at HEAD by design. If doctrine-only (Path B), existing scope-fence REQs remain advisory; new ADRs author them differently.
- **Migration posture for shipped ADRs.** ADR-0.0.32 is the first observed sample; any other shipped ADR with scope-fence REQs would surface the same advisory output. Promotion authors decide whether to retroactively re-shape vs. accept the advisory-only state for already-shipped briefs.
- **Relationship to `.gzkit/rules/adr-audit.md` § Legitimate-authoring exemptions.** Those exemptions govern `@covers` decorator backfill (Component A regression-invariant overlay, same-commit creation, ceremony trailers). Scope-fence REQ exemption is a different layer — it operates on REQ kind in the brief, not on decorator legitimacy. The two systems compose but do not overlap.

## Alternatives Considered

### Path A — Schema-level REQ kind marker (runtime touch)

**Shape.** Add a per-REQ structured marker in OBPI brief frontmatter or inline (e.g. `REQ-X-NN [scope-boundary]: ...`, or a structured REQ kind enum on the brief schema). `gz adr audit-check` honors the marker and exempts scope-boundary REQs from coverage reporting entirely — they are structurally untestable at HEAD by design, not "untested" in the sense the coverage report exists to flag.

**Estimated diff.** ~50-150 lines across `src/gzkit/commands/adr_coverage.py`, `src/gzkit/traceability.py`, OBPI brief schema validator (`src/gzkit/schemas/obpi-brief.json` or equivalent), plus a small `.gzkit/rules/obpi.md` doctrine paragraph. Schema migration: every existing OBPI brief either gets explicit `[feature]` REQ markers or relies on a default-feature-kind interpretation.

**Strengths.**

- Mechanical defense against doctrine drift: the brief schema fail-closes on missing kind in the long run.
- Audit-check signal cleanliness: 0 advisory REQs after migration means the gap is genuinely closed, not silenced by convention.
- Matches the anti-vibing mantra (`AGENTS.md` § Make LLM Stochastic Vibes Inert) — every option framed by smallest-vibing-surface.
- Composable with existing `.gzkit/rules/adr-audit.md` exemptions (operates on REQ kind, not decorator legitimacy).

**Weaknesses.**

- Schema migration on every existing OBPI brief is a substantive ceremony in its own right.
- The marker introduces a new surface that itself can drift (operators marking persistent REQs as scope-fence to silence audit-check) — the migration must include validator rules that fail-close on "marker without negative-existence or byte-identity assertion pattern."
- Runtime cost (~50-150 lines) is non-trivial for a defect class that affects 8 REQs out of 138 (5.8%) on the first observed ADR.

### Path B — Doctrine-only authoring guidance (rule touch)

**Shape.** Rule in `.gzkit/rules/obpi.md` and `docs/governance/GovZero/obpi-decomposition-matrix.md` advising: scope-fence REQs should be phrased as *integration-state properties at the parent ADR level* (e.g. "module X's public surface contains only Y" — testable at HEAD against the integrated state) rather than as per-OBPI handoff fences. Existing scope-fence REQs in shipped ADRs remain advisory; new ADRs author them differently.

**Estimated diff.** ~30 lines doctrine. No runtime touch. Worked example added to the decomposition matrix showing the bad-shape REQ and its parent-ADR-integration-state equivalent.

**Strengths.**

- Smallest possible diff for closing the doctrine gap.
- No schema migration ceremony; no risk of a new marker surface drifting.
- Matches the existing pattern (decomposition matrix already prescribes authoring shape via doctrine, not mechanization).
- Preserves the agent-attestation surface — the operator reading the rule is the gate, which matches the rest of OBPI authoring discipline.

**Weaknesses.**

- No mechanical defense: operators authoring briefs against the existing template can continue to write scope-fence REQs and the audit-check advisory output persists.
- Existing shipped ADRs (starting with ADR-0.0.32) continue to report advisory uncovered REQs forever — the audit-check noise floor is permanent at the historical baseline.
- Relies on doctrine compliance, which is the failure mode `AGENTS.md` § Make LLM Stochastic Vibes Inert names as Operative Claim #4 ("doctrine drift is invariant drift").

### Path C — Compose A + B with phased migration

**Shape.** Author the doctrine (Path B) first as a 30-line rule update to `.gzkit/rules/obpi.md` and the decomposition matrix. New ADRs are authored under the new shape from day one. After observing N ≥ 3 ADRs authored under the new doctrine without scope-fence REQ regressions, promote to the schema-level marker (Path A) with the migration informed by the observed-correct authoring patterns.

**Strengths.**

- Sequenced risk: doctrine lands first (cheap, reversible); mechanization lands after operator behavior demonstrates the doctrine is sufficient (or, equivalently, demonstrates it is not, scoping Path A's design).
- Preserves the design-pressure-first principle — mechanization without observed authoring practice tends to over-specify the marker surface.
- Matches GHI #466's two-component pattern (Component A inline marker for operator attestation, Component B structural detection for same-commit creation) — different layers of the same defense.

**Weaknesses.**

- Two-phase work is two surfaces of authoring ceremony; if Path A is the right answer it's deferred unnecessarily.
- The "N ≥ 3 ADRs without regression" gate is itself a judgment surface that can drift.
- Long-tail ambiguity: between Phase 1 and Phase 2, the audit-check advisory output is unchanged from today's state.

### Path D — Promotion of scope-fence REQs to parent-ADR REQs

**Shape.** Variant of Path B with a stronger constraint: scope-fence REQs are *moved* from per-OBPI briefs to the parent ADR's invariant set, expressed as integration-state properties. Per-OBPI briefs no longer carry scope-fence REQs at all. The parent ADR carries a "boundary invariants" section that audits at the parent level, not per-OBPI.

**Strengths.**

- Eliminates the REQ-kind ambiguity entirely (all per-OBPI REQs are feature REQs by definition; scope assertions live at the parent layer).
- Aligns with the principle that "boundary invariants" are an ADR-level property, not an OBPI-level property.

**Weaknesses.**

- Requires re-authoring the parent ADR's invariant section, which is heavier than authoring per-OBPI REQs.
- Loses the per-OBPI scope-creep defense that scope-fence REQs currently provide during decomposition — the OBPI brief is the authoring-time surface where scope creep is most likely.
- Adds a new surface (parent-ADR boundary-invariant section) that itself needs schema rules to prevent it from becoming a dumping ground.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

### Related artifacts

- **GHI #467** — opens this design conversation; 8 instances on ADR-0.0.32 (REQ-0.0.32-01-07, -02-03, -03-04, -03-05, -09-03, -09-04, -11-06, -11-08)
- **GHI #165** — `audit-check uses @covers as sole proof channel — no support for non-code REQ evidence` (adjacent; addresses REQ-kind proof channels for BDD/decision/integration REQs, distinct from scope-fence REQs)
- **GHI #268** — `audit-check exits 1 on advisory @covers gaps for Lite-lane docs-only OBPIs` (adjacent; Lite-lane advisory exit-code behavior, distinct from heavy-lane scope-fence)
- **GHI #466** — `covers-backfill detector: same-commit block-creation flagged as backfill` (same family — covers/audit-check heuristic refinement; closed by commit a4cca07d)
- **ADR-0.0.32 § AUDIT.md S3** — documents the 8 advisory REQs as non-blocking but leaves the doctrine gap unresolved
- **`docs/governance/GovZero/obpi-decomposition-matrix.md`** — decomposition mandate; doesn't currently distinguish scope-fence from feature REQs
- **`.gzkit/rules/adr-audit.md`** — Invariant 6f remediation paths; § Legitimate-authoring exemptions catalogues `@covers` decorator exemptions (orthogonal to REQ-kind exemption)
- **`.gzkit/rules/tests.md`** — Invariant 6f remediation paths

### Promotion guidance

The promotion author must commit to one of Path A, B, C, or D (or articulate a fifth option grounded in evidence) and re-derive the Rejected Alternatives matrix in the canonical ADR-template format. Until promotion, this ADR is the routing destination for any new GHI surfacing additional scope-fence REQ instances — close those `superseded` against this pool ADR and add their evidence to the Intent section's table.
