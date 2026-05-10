# Storybook — From Empty Repo to First Attested Release

> **Status:** STRAWMAN DRAFT (2026-05-09). Not canon. Not yet linked from the
> runbook. Authored as a first-cut to test voice, derive-quality, and the
> gap-surfacing mechanic before the storybook doctrine is locked.

> **Audience:** an operator who has just decided to govern their next project
> with gzkit. They are not a gzkit contributor — they are a downstream
> consumer who wants to know what value flows through their workflow once
> they adopt the meta-harness.

---

## How to read this

A runbook tells you *what to do, step by step.* A storybook tells you
*why a journey through the system matters and what value emerges* — the
shape the work takes when the parts compose, not just the procedure for
each part.

Each storybook arc traces a single value-flow from start to finish, naming
the stages (skills, CLI verbs, gates), the order in which they are taken,
and the supporting surfaces (validators, hooks, ARB receipts) that hold
the chain together. The narrative is operator-curated. The anchors below
are derived — regenerable from the artifact graph.

---

## Anchored facts (Layer 3 — regenerable)

> Regenerated from artifact graph on 2026-05-09. Do not hand-edit; rerun
> `gz storybook derive` (planned) to refresh.

### Anchored ADRs

| ID | Title | Stage | Status |
|---|---|---|---|
| ADR-0.0.1 | Canonical GovZero Parity | Scaffolding | Validated |
| ADR-0.0.2 | Stdlib CLI and Agent Sync (argparse) | Scaffolding | Validated |
| ADR-0.0.4 | CLI Standards & Presentation Foundation | Scaffolding | Validated |
| ADR-0.0.7 | Config-First Resolution Discipline | Scaffolding | Validated |
| ADR-0.0.10 | Storage Tiers — Simplicity Profile | Scaffolding | Validated |
| ADR-0.0.17 | ADR Taxonomy Mechanical | Decomposition | Validated |
| ADR-0.0.18 | ADR Taxonomy Doctrine | Decomposition | Validated |
| ADR-0.0.19 | Pre-execution Reasoning Walkthrough (`gz justify`) | Pre-execution | Validated |
| ADR-0.0.22 | Security Sensitivity Doctrine | Verification | Validated |
| ADR-0.0.24 | Attestation Receipt Binding | Implementation, Closeout | Validated |
| ADR-0.0.25 | OBPI Completion REQ-Coverage Gate | Verification | Validated |
| ADR-0.0.36 | Universal OBPI Attestation | Closeout | **Draft** |
| ADR-0.0.41 | Token-Block Lock Discipline | Implementation | **Draft** |
| ADR-0.7.0 | OBPI-First Operations | Decomposition | Validated |
| ADR-0.13.0 | OBPI Pipeline Runtime Surface | Implementation | Validated |
| ADR-0.18.0 | Subagent-Driven Pipeline Execution | Implementation | Validated |
| ADR-0.19.0 | Closeout & Audit Processes | Closeout | Validated |
| ADR-0.20.0 | Spec-Test-Code Triangle Sync | Verification | Validated |
| ADR-0.0.15 | GHI-Driven Patch Release Ceremony | Release | Validated |

### Anchored skills (in invocation order)

`gz-init` → `gz-prd` → `gz-constitute` → `gz-design` → `gz-adr-create` →
`gz-adr-evaluate` → `gz-justify` → `gz-plan` → `gz-plan-audit` →
`gz-obpi-specify` → `gz-obpi-pipeline` → `gz-arb` → `gz-obpi-simplify` →
`gz-obpi-reconcile` → `gz-adr-audit` → `gz-adr-closeout-ceremony` →
`gz-patch-release`

### Anchored manpages

`gz init`, `gz status`, `gz state`, `gz justify`, `gz adr create`,
`gz obpi pipeline`, `gz arb`, `gz check`, `gz validate`, `gz attest`,
`gz adr emit-receipt`, `gz git-sync`

### Anchored runbook workflows

- `docs/user/runbook.md` — Loop A (OBPI Increment, primary daily loop)
- `docs/governance/governance_runbook.md` — closeout / audit operations

---

## Narrative (Layer 1 — operator-authored canon)

### Stage 1 — Scaffolding (`gz init`)

> *Value claim:* the meta-harness exists before any code does. The contract
> precedes the commits.

You begin in an empty directory with a Python project you intend to take
seriously. `gz init` writes the entire governance shape — `.gzkit/`,
`AGENTS.md`, `CLAUDE.md`, the ledger, the manifest, the persona library,
hooks, schemas, validators — before you have written a line of feature
code. The ledger is empty. The artifact graph has no nodes. But the rules
that will police every future commit are already in place. ADR-0.0.1
fixes the parity floor; ADR-0.0.2 picks `argparse` over a third-party CLI
framework so the surface ages with the language. ADR-0.0.10 names which
state lives where (canon, ledger, derived view) so nothing silently
mutates into source-of-truth.

The supporting surfaces matter more than they look. Hooks are wired.
The SessionStart hook will read `AGENTS.md` to every new agent session.
The pre-commit hook will reject pytest. The post-edit ruff hook will
strip unused imports. None of this is suggestion; all of it is mechanical.

### Stage 2 — Intent (PRD → Constitution → Design)

> *Value claim:* the irreversible discussion happens at the semantic layer,
> not at diff-review.

You have an idea. You do not start typing. `gz-prd` records the
project-level intent — the thing the project exists to do. `gz-constitute`
captures invariants that no later decision can violate. `gz-design` enters
a collaborative dialogue with you: what are you building, why, what does
it cost, what alternatives lose? The output is an ADR draft with REQs,
proposed lane, proposed kind. `gz-adr-evaluate` then scores the draft on
eight weighted dimensions and can run ten red-team challenges against it
before you commit.

This is where the storybook diverges most sharply from how most projects
operate. The decision is recorded *before* the code, in language a human
can argue with. By the time anyone types `def`, the irreversible part of
the work — the part that determines whether the project still makes sense
in two years — is already done.

### Stage 3 — Decomposition (ADR → OBPI)

> *Value claim:* atomic implementation units carry their own contract.
> Scope boundaries are mechanical, not aspirational.

`gz-adr-create` (or `gz adr promote` from a pool entry) lands the ADR with
its taxonomy correct (ADR-0.0.17 enforces `kind:` frontmatter mechanically;
ADR-0.0.18 gives you operator doctrine for *which* kind). `gz-obpi-specify`
breaks the ADR into atomic OBPI briefs — One Brief Per Item. Each brief
declares **allowed paths**, **denied paths**, **REQs it covers**, and the
**lane / sensitivity** that determines its rigor.

ADR-0.7.0 establishes the OBPI as the atomic unit of delivery, not the ADR.
This is load-bearing: it means daily work iterates increment-by-increment,
not in giant ADR-shaped batches. The brief tells the agent what it is
*not* allowed to touch. Scope-creep stops being a judgment call.

### Stage 4 — Pre-execution (`gz justify`)

> *Value claim:* you cannot pretend you weren't unsure.

Before implementation begins, if your self-reported confidence is below
90% (Behavior Rule 7) — or if `gz-adr-evaluate` flagged a low score — you
run `gz justify`. ADR-0.0.19 makes this canon. The CLI renders an
eight-section reasoning scaffold pre-populated with anchor evidence; you
fill in the reasoning, citing what you read. The artifact attaches to the
brief.

This is the single most direct anti-vibing surface in the system. A
plausible plan that turns out to be wrong-direction is the most expensive
agent-failure mode gzkit knows. `gz justify` forces the reasoning into
the open before the code exists, where it costs ninety seconds to fix
instead of nine days.

### Stage 5 — Implementation (pipeline + ARB receipts)

> *Value claim:* every quality claim is bound to a receipt. The ledger is
> the audit trail.

Plan approved (`gz-plan-audit` confirmed alignment). You run
`gz obpi pipeline <OBPI-ID>`. ADR-0.13.0 owns the runtime; ADR-0.18.0
distributes the work to subagents (implementer, narrator, reviewers).
Each stage emits ledger events. Each quality command runs through
`gz arb` (ADR-0.0.24 binds attestation to receipts), which wraps the
canonical invocations from `AGENTS.md § Attestation` and writes
receipt IDs into `.gzkit/receipts/`. "Tests pass" is no longer a
narrative claim; it is `arb-step-unittest-<hash>`.

The triangle-sync (ADR-0.20.0) keeps spec, test, and code locked
together so none of the three can drift independently. Lock discipline
keeps two agents from silently working the same brief — today via the
`gz-obpi-lock` skill, with mechanical token-block coupling under
ADR-0.0.41 (Draft) once that lands. **WIP — see § Work-in-progress
dependencies.**

### Stage 6 — Verification (Gates 1–5)

> *Value claim:* lane discipline decides rigor. You do not argue about
> which gates apply.

Five gates: ADR recorded → tests pass → docs updated → BDD verified →
human attests. The lane (lite vs heavy), the kind (foundation vs
feature), and the sensitivity axis (security vs absent) compose into a
matrix that decides which gates fire (`AGENTS.md § Lane & Kind &
Sensitivity Attestation Matrix`). ADR-0.0.22 adds the security axis;
ADR-0.0.25 closes the REQ-coverage hole — every requirement must have
a covering passing test, or be explicitly waived with a reason.

You do not negotiate which gates apply. The matrix decides. This is
what *governance-as-product* feels like: discipline is mechanical, not
charismatic.

### Stage 7 — Closeout (audit + ceremony)

> *Value claim:* human attestation is irreducible.

`gz-adr-audit` runs Gate-5 audit templates. `gz-adr-closeout-ceremony`
walks the human through attestation. ADR-0.19.0 owns the ceremony shape.
The current attestation matrix already forces a human in the loop for
foundation-kind, heavy-lane, and security-sensitivity work; ADR-0.0.36
(Draft) is the planned move to make universal OBPI attestation the
floor — eliminating the lite-feature self-closeable carve-out.
**WIP — see § Work-in-progress dependencies.**

A release that does not bear a person's name is not a release.

### Stage 8 — Release (`gz patch-release`)

> *Value claim:* the value you delivered is itself a traceable artifact,
> all the way back to the issues that motivated it.

`gz-patch-release` (ADR-0.0.15) walks the GHI-driven release ceremony.
It drafts release notes from the closed GHIs in scope, asks for operator
approval, updates `RELEASE_NOTES.md`, runs guarded git-sync, and creates
the GitHub release. The release tag triggers PyPI publish and binary
builds.

You can now point at the release and trace any line of code in it back
through: receipt → gate → OBPI → REQ → ADR → PRD → constitution. The
chain has no missing link. The operator who signed the release has a
name. Every node has a witness. Stochastic LLM vibing has nowhere left
to leak.

That is the value flow this arc claims to deliver.

---

## Work-in-progress dependencies

> The narrative above leans on two ADRs that are still `Draft`. They are
> called out inline with **WIP** markers; this section is the consolidated
> view. If any of these fail to land, or land in a shape that does not
> compose with the rest of the chain, the storybook's cohesion is the
> early warning signal — that is the storybook's job.

| ADR | Stage | Status | Cohesion question if it does not land |
|---|---|---|---|
| ADR-0.0.36 — Universal OBPI Attestation | Closeout (Stage 7) | Draft | Lite-feature self-closeable OBPIs remain a carve-out. The Stage-7 claim that "human attestation is irreducible" weakens to "human attestation is required for foundation/heavy/security." Storybook narrative needs hedging; matrix in `AGENTS.md § Lane & Kind & Sensitivity` becomes the source of truth. |
| ADR-0.0.41 — Token-Block Lock Discipline | Implementation (Stage 5) | Draft | Lock-release stays decoupled from handoff register entry. The Stage-5 claim that "two agents never silently work the same brief" weakens to skill-level discipline, not a mechanical invariant. Risk: silent stomp on shared state under multi-agent execution. |

---

## Gaps surfaced during derivation (filed GHIs)

> The derive step found three places where the artifact graph does not yet
> compose into the story above. None are fatal; all are honest. All three
> have been filed as GHIs.

1. **[GHI #428](https://github.com/tvproductions/gzkit/issues/428) —
   Operator runbook missing first-time-operator entry.**
   `docs/user/runbook.md` opens at *Loop A: OBPI Increment*, which
   assumes the project is already mid-flight. The journey from empty
   directory through `gz init` and the intent stage (PRD → Constitution
   → Design) has no canonical entry. The storybook arc above is
   currently the only end-to-end account.

2. **[GHI #429](https://github.com/tvproductions/gzkit/issues/429) —
   PRD → Constitution → Design → ADR handoff cohesion.**
   The skills `gz-prd`, `gz-constitute`, `gz-design`, and `gz-adr-create`
   exist independently. Stage 2 of this arc narrates them as a smooth
   four-step pipeline. Whether the artifacts actually compose end-to-end
   has not been verified.

3. **[GHI #430](https://github.com/tvproductions/gzkit/issues/430) —
   First-release ceremony undocumented.**
   `gz-patch-release` covers patch releases on a versioned project. It
   does not cover the *first* release — the moment a pre-release project
   crosses to v0.1.0 or v1.0.0. Different mechanics (changelog seeding,
   version-floor doctrine, PyPI registration) are not currently a skill
   or runbook entry.

---

## Provenance footer

- **Arc unit:** system-level value journey (one of multiple planned arcs).
- **Derived from:** ADR-0.0.{1, 2, 4, 7, 10, 15, 17, 18, 19, 22, 24, 25,
  36}, ADR-0.{7, 13, 18, 19, 20}.0, plus the skill registry as of
  2026-05-09.
- **Authored sections:** all prose under "Narrative" headings.
- **Regenerator (planned):** `gz storybook derive --arc from-init-to-first-attested-release`.
- **Freshness validator (planned):** `gz validate --storybook-fresh`.
