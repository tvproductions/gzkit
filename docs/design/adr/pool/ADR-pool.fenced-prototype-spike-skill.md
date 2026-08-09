---
id: ADR-pool.fenced-prototype-spike-skill
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.fenced-prototype-spike-skill: Fenced throwaway prototype-spike skill

## Status

Pool

## Intent

**gzkit has no sanctioned way to answer a question by building a throwaway.** An external-catalog alignment scan (GHI #567) compared 29 skills from Matt Pocock's public catalog against gzkit's ~70-skill catalog and doctrine. gzkit already covers or out-builds roughly 26 of them; the actionable surface collapsed to three moves, and this is the one genuine gap — a disposable spike that pushes a state machine or data model through hard-to-reason cases until the shape is understood, then is deleted.

Today an agent facing an unclear design either reasons in prose (cheap, and frequently wrong about runtime behavior — this repo has repeatedly found that *running beat reading*) or builds production-shaped code under full ceremony to learn one fact. Neither is right. The spike is the missing third option.

**The fencing argument is the whole ADR, and it is non-negotiable.** The source skill's rules read as a direct doctrine violation, verbatim from its `SKILL.md`: *"Skip the polish. No tests, no error handling beyond what makes the prototype runnable, no abstractions"* and *"Throwaway from day one, and clearly marked as such."* Against AGENTS.md § DO IT RIGHT #2 (no plausible-looking code without a failing test first) and #10 (nothing speculative), that is adoptable **only** under a fence:

- Marked throwaway at creation, located outside production paths, and **deleted or absorbed** when the question is answered.
- **The only durable output is the answer**, attested into an ADR or captured via `gz insights remember` — never the code.
- The fence must be written into the skill body itself, not merely into this ADR. A skill whose text carries the source's rules without gzkit's fence would be a licence to vibe, wearing a governed name.

The reconciliation that makes it admissible: the anti-vibing rules govern *production code claiming to be done*. A spike whose sole surviving artifact is an attested answer, and whose code is deleted by construction, is a different artifact class — it never claims to be done, because it never claims to exist past the question. If that argument fails review, the skill should not land.

**Scope: LOGIC branch only.** The source skill's UI branch is web-route-flavored and irrelevant to a Python CLI toolkit. Drop it rather than port it.

**ADR-worthiness (per `docs/governance/pool-curation.md` § Is it ADR-shaped at all?).** Hard to reverse — a skill lands in `.gzkit/skills/` plus three vendor mirrors and enters every agent's routing surface; withdrawing one is a delete-on-retire sweep across five roots. Surprising without context — the skill's own rules read as a doctrine violation, and *why gzkit admits them anyway* is exactly the non-obvious reasoning a reader needs. A real tradeoff — admitting a fenced anti-vibing exception versus declining the capability, with the fence itself the thing being traded.

## Decision

*(To be authored at promotion — this entry records the problem, the fence, and the option space.)*

The scope a promoter would be committing to:

1. `.gzkit/skills/prototype/SKILL.md` — LOGIC branch only, carrying the fencing argument in its body as a binding section, with `metadata.skill-version` and `last_reviewed` per `.claude/rules/skill-surface-sync.md`.
2. Mirrors regenerated via `uv run gz agent sync control-surfaces` (never hand-copied).
3. A named disposal step: the skill does not end at "the prototype works", it ends at "the answer is attested and the code is gone".
4. A wielding path so `gz validate --skill-alignment` Invariant 1 is satisfied, and a routing entry in `gz-skill-router`.

## Alternatives Considered

**(a) Fenced skill, LOGIC branch only.** The recommendation this entry carries. Supplies the missing capability with the anti-vibing exception written down and bounded.

**(b) Decline the skill; keep spikes informal.** Agents already write throwaway probes in the scratchpad — this session did so twice, and both probes changed a design decision. The capability exists in practice, ungoverned. Declining formalization means the fence is never written, which is the worse of the two failure modes: the spiking happens either way, and only the discipline is optional. Recorded as the strongest argument *for* (a).

**(c) Adopt the skill unfenced, as published.** Rejected outright. Its stated rules contradict DO IT RIGHT #2 and #10 by name, and adopting them without the fence would make gzkit ship a licence to vibe under a governed skill name.

**(d) Fold the capability into an existing skill** (`gz-justify`, or the design dialogue). Cheaper — no new skill surface, no mirrors. Cost: the disposal obligation is the load-bearing half, and hanging it off a skill whose purpose is durable reasoning artifacts puts a delete-the-code rule inside a keep-the-artifact workflow. The conflict would be resolved by whoever read it last.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

**Provenance.** Move 1 of GHI #567's three-move disposition. Move 2 (two doctrine filters — the ADR-worthiness three-gate into `docs/governance/pool-curation.md`, and the horizontal-slicing prohibition into `.gzkit/rules/tests.md`) landed 2026-08-09 as a direct doc edit. Move 3 (`diagnose`, a disciplined bug-loop skill) was **declined** as redundant with the Codex rescue path plus the complexity advisor plus DO IT RIGHT #2/#4.

**Not a gap: the glossary.** The scan flagged the source catalog's CONTEXT.md glossary mechanism and its deprecated `ubiquitous-language` skill. `ADR-0.0.43-ddd-domain-cascade` is a deeper, Evans-citing native version (ubiquitous language § 2.1, bounded contexts § 2.2, context map § 2.3, AST cross-context import enforcer), so gzkit out-builds the concept. The one transferable detail is the inline-glossary-update mechanism — resolve a term, write it immediately, do not batch — which could inform how § 2.1 gets populated during `gz-design`.

**Anti-aligned, do NOT adopt:** the source catalog's `caveman` skill ultra-compresses *agent output*, which undercuts attestation, observed-output, and evidence-to-decision requirements. It is distinct from gzkit's § OPERATOR ECONOMY OF EFFORT, which compresses *operator typing*, never agent evidence.
