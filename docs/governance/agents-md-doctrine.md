# AGENTS.md Map-Not-Encyclopedia Doctrine

**Source ADR:** `ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine`
**Rule file:** `.gzkit/rules/agents-md-map-doctrine.md` (version `0.1.0`)
**Authored:** OBPI-0.0.54-01

---

## The failure pattern

The OpenAI Harness Engineering thesis (2026-02-11) names four predictable failure modes for monolithic instruction files:

> *"Context is a scarce resource. A giant instruction file crowds out the task, the code, and the relevant docs — so the agent either misses key constraints or starts optimizing for the wrong ones.*
>
> *Too much guidance becomes non-guidance. When everything is 'important,' nothing is. Agents end up pattern-matching locally instead of navigating intentionally.*
>
> *It rots instantly. A monolithic manual turns into a graveyard of stale rules. Agents can't tell what's still true, humans stop maintaining it, and the file quietly becomes an attractive nuisance.*
>
> *It's hard to verify. A single blob doesn't lend itself to mechanical checks (coverage, freshness, ownership, cross-links), so drift is inevitable.*
>
> *So instead of treating AGENTS.md as the encyclopedia, we treat it as the table of contents."*

gzkit's AGENTS.md was exhibiting all four. At the doctrine's authoring (2026-05-19): 390 lines / 30,924 chars, containing both binding bullet lists AND multi-paragraph rationale prose, worked examples, anti-pattern catalogs, and "Why this is canon" coda paragraphs. The `gz-context-diet` skill existed as a reactive remedy; this doctrine makes the map shape the mechanical resting state.

## The invariant

**AGENTS.md MUST contain only:**
- **(a) Binding bullet rules** — one bullet = one rule, ≤ 3 lines per bullet
- **(b) Structured tables** — Persona, Gate Covenant, OBPI kinds, canonical-invocations, defect-fix routing thresholds
- **(c) Canonical-link references** — `See [text](docs/governance/…)` links to deeper documentation at stable URLs

**AGENTS.md MUST NOT contain:**
- **(i) Multi-paragraph rationale prose** — paragraph > 5 lines without a binding-bullet anchor
- **(ii) Worked examples or anti-pattern catalogs** — subsections titled "Worked example", "Anti-patterns", "Example", or equivalent
- **(iii) "Why this is canon" coda blockquotes** — blockquotes explaining why a rule exists
- **(iv) Narrative pedagogical sections** — multi-paragraph explanations of how rules work
- **(v) Operative-claims expansions** — prose blocks restating operative claims already stated in binding-bullet form

CLAUDE.md and `.claude/rules/*.md` inherit the same shape contract.

## Port vs adapter framing

This doctrine authors a **port**: it declares the abstract shape AGENTS.md must satisfy. The specific section layout, per-section character targets, and choice of which subsections to lift first are adapters behind the port. The existing `gz-context-diet` skill becomes the *operator-facing procedure* against the port; `gz validate --agents-md-map-conformance` (OBPI-0.0.54-03) becomes the *mechanical witness*.

## Budget targets

The operator selected "Moderate" (halve current weight; preserve binding-bullet density):

| File | Old budget | Target budget (destination — not the live enforced value) | Rationale |
|------|-----------|-----------|-----------|
| `AGENTS.md` | 40,000 chars | 15,000 chars | Halves per-turn injection; preserves ~200 lines of binding bullets |
| `CLAUDE.md` | 40,000 chars | 4,000 chars | Already 1,378 chars; 4k provides 2.6k headroom for model-specific addenda |
| `.claude/rules/*.md` | 16,000 chars/file | 16,000 chars/file | Unchanged; per-file shape audit deferred to OBPI-0.0.54-04 |

Budget is enforced by `gz validate --instructions-files-budget` reading `data/instructions_files_budget.json` — the single source of truth. The **live enforced** values are whatever that JSON carries (currently higher than these targets); the column above records the doctrine *destination*, deferred to `ADR-0.35.0-canon-entry-corpus-landing` § Decision 3, not a currently-enforced number. (The intermediate hop through GHI #533 is retired — that issue closed 2026-09-01 `superseded` into this ADR.)

> The 15,000-char figure above is the doctrine *destination*. During the
> `ADR-0.35.0` CMS work the enforced interim budget is higher (GHI #533, closed 2026-09-01). The live
> enforced value is always whatever `data/instructions_files_budget.json` carries —
> the single source of truth — never a number duplicated into prose or tests.
>
> The predecessor pointer to `ADR-0.0.37` is **retired**: that ADR went terminal
> 2026-07-18 (§ Terminal Disposition, "Split-and-Supersede") with its
> registry-spine OBPIs permanently withdrawn, so no weight-halving work can land
> there. The successor is corpus-shaped — sections declare `corpus-owned` or
> `unowned`, the generator materializes owned sections from the corpus, and the
> unowned byte total is held in a decrease-only ratchet.

## Per-section targets (OBPI-02 lift guide)

The ADR-0.0.54 § Intent table records operator-reviewed per-section target sizes. These are **Judgment** class (not Mechanical — they require review of surviving text density). The table is the canonical reference; this doc does not duplicate it.

Summary action: each section's rationale prose lifts to a named target under `docs/governance/`; the surviving AGENTS.md bullet replaces the prose with a `See [doc §anchor]` link preserving the binding text verbatim.

## Lift targets

| AGENTS.md section | Lift target | Status |
|-------------------|-------------|--------|
| Why this contract is not minimal | `docs/governance/agent-contract-rationale.md` § Why this contract is not minimal | OBPI-02 |
| PRIME DIRECTIVE anti-rationalizations | `docs/governance/prime-directive.md` (new) | OBPI-02 |
| DO IT RIGHT pedagogical examples | `docs/governance/agent-contract-rationale.md` § DO IT RIGHT worked examples | OBPI-02 |
| ANTI-VIBING MANTRA blockquote | `docs/governance/agent-contract-rationale.md` § Anti-vibing mantra | OBPI-02 |
| STDLIB-FIRST canonical applications | `docs/governance/agent-contract-rationale.md` § Stdlib-First doctrine | OBPI-02 |
| OPERATOR ECONOMY anti-patterns | `docs/governance/agent-contract-rationale.md` § Operator economy | OBPI-02 |
| Behavior Rules prose explanations | `docs/governance/behavior-rules.md` (new) | OBPI-02 |
| Skills catalog | `docs/governance/skills-catalog.md` (new; auto-regenerated from manifest) | OBPI-02 |
| Universal OBPI Attestation expansion | `docs/governance/obpi-attestation.md` (new) | OBPI-02 |

## Consequences

### What changes (OBPI-02 outcome)

- AGENTS.md shrinks from ~31k chars to ~15k chars — halving per-turn context injection
- Every binding rule, operative claim, and behavior-rule item **survives verbatim** — at a stable URL under `docs/governance/` rather than inline
- The path of least resistance for rationale becomes the lift, not the in-place expansion
- `gz validate --agents-md-map-conformance` (OBPI-03) surfaces any re-accretion at CI time

### What does not change (scope boundary)

- The *content* of any binding bullet — only the *location* of rationale prose
- The existing `gz validate --instructions-files-budget` weight cap (additive, not replaced)
- Lifted prose is preserved verbatim — no compression-by-summarization permitted

## Reversibility

This is a deliberate one-way door at the file-shape level. Once AGENTS.md is lifted and the validator binds the shape, the binding-bullets-and-links structure is the contract. Justified by: the alternative is indefinite encyclopedia-style accretion, which the OpenAI thesis names as a four-pattern failure mode. Reversal requires an amendment ADR loosening the shape or a re-merge of lifted content.

## Related

- `.gzkit/rules/agents-md-map-doctrine.md` — the rule file (version `0.1.0`)
- `docs/governance/agent-contract-rationale.md` — existing encyclopedia; six sections previously lifted here
- `docs/governance/advisory-rules-audit.md` — scorecard entry (row 58, Mechanical for shape)
- `ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine` — parent ADR with full rationale, Q&A transcript, and per-OBPI decomposition
- `.gzkit/skills/gz-context-diet/SKILL.md` — the operator-facing remedy this doctrine makes the mechanical default
