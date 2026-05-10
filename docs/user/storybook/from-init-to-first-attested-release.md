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

A runbook is a recipe — *here are the steps; follow them in order.* A
storybook is a meal — *here is the experience these courses compose into.*
You can read a recipe and not know whether the dish is worth cooking. The
storybook tells you why a meal matters before you commit a Saturday to
preparing it.

Each storybook arc traces a single value-flow from start to finish, naming
the courses (skills, CLI verbs, gates), the order in which they are served,
and the accoutrement (validators, hooks, ARB receipts) without which the
plate would be incomplete. The narrative is operator-curated. The anchors
below are derived — regenerable from the artifact graph.

---

## Anchored facts (Layer 3 — regenerable)

> Regenerated from artifact graph on 2026-05-09. Do not hand-edit; rerun
> `gz storybook derive` (planned) to refresh.

### Anchored ADRs

| ID | Title | Course |
|---|---|---|
| ADR-0.0.1 | Canonical GovZero Parity | Scaffolding |
| ADR-0.0.2 | Stdlib CLI and Agent Sync (argparse) | Scaffolding |
| ADR-0.0.4 | CLI Standards & Presentation Foundation | Scaffolding |
| ADR-0.0.7 | Config-First Resolution Discipline | Scaffolding |
| ADR-0.0.10 | Storage Tiers — Simplicity Profile | Scaffolding |
| ADR-0.0.17 | ADR Taxonomy Mechanical | Decomposition |
| ADR-0.0.18 | ADR Taxonomy Doctrine | Decomposition |
| ADR-0.0.19 | Pre-execution Reasoning Walkthrough (`gz justify`) | Pre-execution |
| ADR-0.0.22 | Security Sensitivity Doctrine | Verification |
| ADR-0.0.24 | Attestation Receipt Binding | Implementation, Closeout |
| ADR-0.0.25 | OBPI Completion REQ-Coverage Gate | Verification |
| ADR-0.0.36 | Universal OBPI Attestation | Closeout |
| ADR-0.7.0 | OBPI-First Operations | Decomposition |
| ADR-0.13.0 | OBPI Pipeline Runtime Surface | Implementation |
| ADR-0.18.0 | Subagent-Driven Pipeline Execution | Implementation |
| ADR-0.19.0 | Closeout & Audit Processes | Closeout |
| ADR-0.20.0 | Spec-Test-Code Triangle Sync | Verification |
| ADR-0.0.15 | GHI-Driven Patch Release Ceremony | Release |

### Anchored skills (in serving order)

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

## The meal (Layer 1 — operator-authored canon)

### Course 1 — Scaffolding (`gz init`)

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

The accoutrement matters more than it looks. Hooks are wired. The
SessionStart hook will read `AGENTS.md` to every new agent session. The
pre-commit hook will reject pytest. The post-edit ruff hook will strip
unused imports. None of this is suggestion; all of it is mechanical.

### Course 2 — Intent (PRD → Constitution → Design)

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

### Course 3 — Decomposition (ADR → OBPI)

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

### Course 4 — Pre-execution (`gz justify`)

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

### Course 5 — Implementation (pipeline + ARB receipts)

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
together so none of the three can drift independently. The lock
discipline (ADR-0.0.41 if landed, otherwise the OBPI-lock skill) makes
sure two agents never silently work the same brief.

### Course 6 — Verification (Gates 1–5)

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

### Course 7 — Closeout (audit + ceremony)

> *Value claim:* human attestation is irreducible.

`gz-adr-audit` runs Gate-5 audit templates. `gz-adr-closeout-ceremony`
walks the human through attestation. ADR-0.19.0 owns the ceremony shape;
ADR-0.0.36 (universal OBPI attestation, if landed) closes the
self-closeable loophole — under the matrix, foundation-kind, heavy-lane,
and security-sensitivity all force a human in the loop, no exceptions.

A release that does not bear a person's name is not a release.

### Course 8 — Release (`gz patch-release`)

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

That is the meal.

---

## Gaps surfaced during derivation (candidate GHIs)

> The derive step found three places where the artifact graph does not yet
> compose into the story above. None are fatal; all are honest. Each is a
> candidate GHI for operator decision.

1. **Candidate GHI — First-time-operator runbook entry is missing.**
   `docs/user/runbook.md` opens at *Loop A: OBPI Increment*, which
   assumes the project is already mid-flight. The journey from empty
   directory through `gz init` and the intent course (PRD → Constitution
   → Design) has no canonical entry. The storybook arc above is currently
   the only end-to-end account; the runbook should at minimum link to it.

2. **Candidate GHI — PRD → Constitution → Design wiring is partly
   aspirational.** The skills `gz-prd`, `gz-constitute`, and `gz-design`
   are listed and exist, but the storybook narrative implies they compose
   into a single intent-recording dialogue. Whether the actual handoff is
   smooth (PRD output feeds `gz-constitute`, which feeds `gz-design`,
   which feeds `gz-adr-create`) needs operator verification. If the
   handoff has seams, the seams are themselves candidate refactors.

3. **Candidate GHI — The "first release" ceremony is undocumented.**
   `gz-patch-release` covers patch releases on a versioned project. It
   does not cover the *first* release — the moment a pre-release project
   crosses to v0.1.0 or v1.0.0. That ceremony has different mechanics
   (changelog seeding, version-floor doctrine, PyPI registration) and is
   not currently a skill or runbook entry.

---

## Provenance footer

- **Arc unit:** system-level value journey (one of multiple planned arcs).
- **Derived from:** ADR-0.0.{1, 2, 4, 7, 10, 15, 17, 18, 19, 22, 24, 25,
  36}, ADR-0.{7, 13, 18, 19, 20}.0, plus the skill registry as of
  2026-05-09.
- **Authored sections:** all prose under "The meal" headings.
- **Regenerator (planned):** `gz storybook derive --arc from-init-to-first-attested-release`.
- **Freshness validator (planned):** `gz validate --storybook-fresh`.
