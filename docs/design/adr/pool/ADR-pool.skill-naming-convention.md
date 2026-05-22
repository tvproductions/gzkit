---
id: ADR-pool.skill-naming-convention
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.skill-naming-convention: Skill-naming convention enforcement (gz- prefix)

## Status

Pool

## Intent

GHI #488 (2026-05-18) surfaced two skills under `.gzkit/skills/` —
`complexity-advisor` and `complexity-guide` — that lacked the `gz-` prefix
worn by 45 of the (then) 52 skill directories. The **symptom** (renaming
those two skills to `gz-complexity-advisor` / `gz-complexity-guide` across
all five skill trees) was fixed directly under GHI #488 — commit `a3d454ed`,
2026-05-22.

The symptom fix does not address the **class of failure**: the `gz-` prefix
is an *implicit* convention. No rule in `AGENTS.md` or `.gzkit/rules/`
declares it; nothing at `gz validate` or `gz agent sync control-surfaces`
time fails closed on a violation. The convention is honor-system — 45/52
adherence is its only witness, and any future skill author can repeat the
exact `complexity-advisor` mistake with no mechanical signal.

Per `docs/governance/advisory-rules-audit.md`, a convention the system
behaves as if it has — but which is unwritten and carries no structural
fail-close — is the canonical **Promotable-class** shape. This ADR is the
design home for promoting the skill-naming convention from implicit
honor-system to canonized rule plus mechanical validator.

**Class of failure addressed:** convention drift on skill directory naming.
A new skill authored without the `gz-` prefix lands silently — `gz agent
sync` mirrors it, `gz validate` passes it, the catalog lists it — until a
human happens to notice the odd name out. GHI #488 is the first observed
instance; absent a fail-close it will not be the last.

## Decision

Two coupled deliverables, to land when this ADR promotes to `foundation`:

1. **Canonize the convention as an explicit rule** — a `.gzkit/rules/`
   entry (new `skill-naming.md`, or a section of an existing skill-surface
   rule) stating: every skill directory under `.gzkit/skills/` MUST begin
   with `gz-`, unless it is a registered exemption. The rule is the canon;
   the validator is its enforcement artifact, not the rule itself (per
   `.claude/rules/governance-core.md` — "the validator implementation … is
   an enforcement artifact of this rule, not the rule itself").

2. **A mechanical fail-close** — `uv run gz validate --skill-naming` (flag
   name final at promotion) — that walks `.gzkit/skills/<dir>/` and exits
   non-zero on any directory that neither begins with `gz-` nor appears in
   the exemptions registry. Wired into the default `uv run gz check`
   pipeline so a mis-named skill fails closed at commit/PR time.

### The exemption boundary (load-bearing)

Three skill directories legitimately do not carry the `gz-` prefix. They
are **not outliers to be "fixed"** — they are exempt under a principled
taxonomy, and the convention is meaningless without that taxonomy written
down. A bare whitelist would only relocate the honor-system problem. A
skill is exempt when its leading token is not a free-choice description but
a **fixed referent**:

- **Category A — external-surface mirror.** The leading token names a
  non-gzkit tool the skill is a thin wrapper over, and the wrapper's
  discoverability depends on matching that tool's name. `git-sync` → the
  `git` tool. Re-prefixing to `gz-git-sync` would obscure the very surface
  the operator searches for.
- **Category B — cross-repository target.** The leading token is a proper
  noun naming a specific external repository the skill operates against.
  `airlineops-parity-scan` → the AirlineOps repo.
- **Category C — established prefix-family namespace.** A deliberate
  multi-skill family sharing a non-`gz-` prefix that itself names a
  coherent operational domain. `ghi-author`, `ghi-close`, `ghi-triage` →
  the `ghi-` (GitHub Issue) lifecycle family; the prefix is itself the
  namespace by which the set is discoverable.

**The discriminating test:** does the leading token name a fixed external
referent or an established family namespace (exempt), or is it a
free-choice description of a gzkit-internal capability (must be `gz-`)?
`complexity-advisor` / `complexity-guide` failed the test — `complexity`
is a gzkit-internal doctrine area (the ADR-0.0.27–0.0.30 cluster), not an
external referent, and there was no `complexity-*` family: the sibling
`gz-complexity-distill` already used `gz-`. They were free-choice
gzkit-internal names that simply omitted the prefix.

Exemptions are recorded in a registry — `data/skill_naming_exemptions.json`
— where each entry carries its skill name, its category (A/B/C), and a
one-line rationale. The category + rationale make each exemption an
attested decision and make adding a new one a deliberate, reviewable act;
a bare whitelist with no recorded "why" would be the same honor-system
smell one layer down.

## Alternatives Considered

1. **Leave the convention implicit (honor-system).** Rejected — 45/52
   adherence with no fail-close is precisely the Promotable-class shape
   `advisory-rules-audit.md` exists to surface; GHI #488 is proof the
   honor-system already failed once.
2. **Bare exemptions whitelist, no per-entry rationale.** Rejected — a
   whitelist with no recorded "why" is the honor-system smell one layer
   down: the next author cannot tell a legitimate exemption from an
   unfixed violation. The category + rationale taxonomy is the
   load-bearing part of this ADR.
3. **Rename the exempt skills too** (`gz-git-sync`, `gz-ghi-close`, …) for
   a no-exemption universal rule. Rejected — it erases the discoverability
   the external-referent and family-namespace tokens provide, and
   `gz-ghi-close` double-prefixes a name that already carries a coherent
   namespace. A universal rule that is wrong is not simpler than a correct
   rule with a written exemption taxonomy.
4. **Enforce at `gz agent sync` time rather than `gz validate`.** Rejected
   as the primary site — sync is a generative step, not a gate. Every
   other Promotable→Mechanical promotion lands as a `gz validate --<scope>`
   entry wired into `gz check` (consistency with CLAUDE.md § Mechanical
   scopes). A sync-time warning may be added as a secondary surface.
5. **Promote straight to a foundation ADR with no pool stop.** Rejected at
   routing time (GHI #488 close, 2026-05-22): the symptom rename is a
   direct fix; the convention canonization is a doctrine addition that
   earns the foundation-tier ceremony (evaluation scorecard, gate
   covenant) via `gz adr promote` at the right time — not retroactively
   under a closing GHI. The pool ADR is the design-conversation home.

## ADR Relationships

- **`docs/governance/advisory-rules-audit.md`** — the Promotable→Mechanical
  scorecard pattern this ADR instantiates. The promotion adds the
  `--skill-naming` scope to the audit catalogue and to CLAUDE.md
  § Mechanical scopes; the new `.gzkit/rules/skill-naming.md` rule itself
  requires a scorecard entry (the scorecard self-tests via
  `gz validate --advisory-scorecard`).
- **`ADR-pool.skill-version-review-coupling`** — sibling pool ADR, same
  Promotable→Mechanical shape (a binding skill-surface rule lacking a
  mechanical witness). The two promotions are independent but share the
  `gz validate` skill-surface validator family and could be sequenced
  together.
- **ADR-0.0.32 (canonical-surface packaging)** — owns the five-tree skill
  layout (`.gzkit/`, `src/gzkit/`, `.claude/`, `.agents/`, `.github/`).
  The `--skill-naming` check operates on the canonical `.gzkit/skills/`
  tree; conformance propagates to the other four via sync.

## Notes

Routing facts for the promotion's plan (advisory, carried from GHI #488's
scope hint):

- **Estimated diff:** larger — new `.gzkit/rules/skill-naming.md` rule
  (plus scorecard entry and sync to mirrors), new
  `data/skill_naming_exemptions.json`, new validator scope plus flag
  registration and `gz check` wiring, tests.
- **Stale scope hint:** GHI #488 named `src/gzkit/governance/trust_audits.py`
  as the validator entry point. That path is stale — `trust_audits` is now
  a package; the new scope lands as a module under
  `src/gzkit/governance/trust_audits/`.
- **Lane:** heavy — adds a `gz validate` CLI surface and a runtime-contract
  validator wired into `gz check` (same lane rationale as
  `ADR-pool.skill-version-review-coupling`).
- The symptom (the two-skill rename) is already landed under GHI #488
  commit `a3d454ed`; the promotion's scope is convention + validator only.

Pool ADRs are backlog items — they carry no `semver:` or `kind:`
frontmatter. Promotion into the active tree (foundation or feature) is
performed via `gz adr promote`, which rewrites the frontmatter with the
chosen taxonomy.
