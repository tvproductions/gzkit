# FDAU roadmap and backlog model (tvproductions/xplane-fdau)

Retrieved via `gh api repos/tvproductions/xplane-fdau/contents/<path>` at the default branch HEAD. Access date: 2026-10-30. All excerpts are **primary** (the project's own canon). Quotations are verbatim; line breaks are reflowed only where the source wraps mid-sentence.

## Files read

- `docs/project/backlog-method.md` (read in full)
- `docs/project/backlog-governance-model.md` (the retrospective specification; read in full)
- `ROADMAP.md` (node kinds, status model, release path, D1, release gates, version 0.1.0 gates, maintenance rules)
- `BACKLOG.md` (headings, "Canonical release boundary")

A GitHub code search for `candidate_release` in the repository returned one file only: `docs/project/backlog-governance-model.md`.

## The four separate questions

Source: `docs/project/backlog-method.md` § "Why this shape exists". Primary.

> The method tracks four separate questions: **scope** (who owns the outcome), **order** (what must precede it), **maturity** (which lifecycle stage it has reached), and **proof** (which acceptance gates have evidence).

Source: `docs/project/backlog-governance-model.md` § "The problem it solves". Primary.

> A single numbered list easily mixes five different statements: a capability is desired, its design is approved, code exists, another project may plan against it, and a release may ship. Those statements have different owners, prerequisites, and evidence.

> A work item's **stable identity** answers what outcome is being pursued. Its **kind and owner** answer who may act on it. Dependencies answer when it is ready. Lifecycle state answers how far execution has advanced. Linked evidence answers why that state is credible. A release version answers which public artifact was published and what compatibility it represents. The model does not make one field answer all six questions.

## Identifiers

Source: `docs/project/backlog-method.md` § "Read an identifier". Primary.

> The letters are local mnemonics, not a universal alphabet. A whole number such as C2 names a family; a dotted number such as C2.3 names an outcome. Numbers are identities, not dates, estimates, or priority scores. **The roadmap section gives the node kind:** dotted IDs can name local children or external boundaries.

> The roadmap does not formally expand the letter I; it uses it for downstream consumer and adapter boundaries. C1 through C4 are separate canonical-contract epics.

## Node kinds (the containers)

Source: `docs/project/backlog-governance-model.md` § "Conceptual data model". Primary.

> The roadmap defines a tagged set of five nonoverlapping node kinds.

> | Kind | Identity and purpose | Can be the selected local work? | Mutable local state? |
> | --- | --- | --- | --- |
> | Milestone | A verified prerequisite, such as M0 | No | No |
> | Epic | A related family of local children, such as C2 | No | No |
> | Local child | One independently planned and reviewed outcome, such as C2.3 | Yes | Yes |
> | Release gate | Cross-child reconciliation, such as G1 | No | Derived readiness and gate evidence |
> | External boundary | When another owner may act, such as I1.0 | No | No |

> In conceptual terms, a local child contains a stable ID, epic, outcome, ordered dependency IDs, lifecycle state, governing specification, one implementation plan, acceptance statements, gate evidence, review evidence, and optional suspension reason/resume state.

Source: `ROADMAP.md` § "Roadmap node kinds". Primary.

> | Milestone | Verified prerequisite such as `M0` | No |
> | Epic | Related local capability family such as canonical contracts | No |
> | Local child | One independently testable, reviewable xplane-fdau outcome | Yes—one primary local child per run |
> | Release gate | Cross-child reconciliation before a separate release decision | No |
> | External boundary | Consumer adoption or organizational authority owned outside xplane-fdau | No |

> The former `C1`–`C4`, `A1`, `R1`, and `P1` labels are epics. They are not implementation-plan units. A child slice receives its own specification link, plan, status, and acceptance gates in `BACKLOG.md`.

Source: `docs/project/backlog-method.md` § "Node kinds, state, and evidence". Primary.

> Only a local child can be selected as the primary work of a run. One broad design may govern several exact children, while an implementation plan covers one child. Plan tasks sit below that child. Explicit dependencies establish readiness; an earlier-looking ID alone does not.

## Design-to-child and plan-to-child cardinality

Source: `docs/project/backlog-governance-model.md` § "Authority layers". Primary.

> A design can cover several named children when their semantics must agree. An execution plan covers exactly one child. Plan tasks remain beneath that child; new scope needs a child or a gate amendment. Backlog gate statements match the governing design's acceptance criteria. Evidence is an explicit artifact, not an inference from a file's existence or recent commit.

Source: `ROADMAP.md` § "C — Canonical semantic contract kernel". Primary.

> The canonical measurement-contract design is explicitly a cross-epic design spanning `C1`, `C2`, `C3`, and `C4`; its governance metadata is anchored by `Roadmap epic: C1`.

## Dependencies and readiness (prerequisites)

Source: `docs/project/backlog-governance-model.md` § "Core invariants". Primary.

> 2. Local dependencies name known local children or M0 and form an acyclic graph. The backlog repeats dependencies so an audit can detect drift.
> 3. A child is dependency-ready only when every local predecessor is verified or released. Readiness does not itself change its lifecycle state.

> 6. External boundaries remain report-only. Release gates reconcile multiple children; a separate release decision controls publication.

Source: `docs/project/backlog-governance-model.md` § "Dependencies, lifecycle, and selection". Primary.

> The dependency graph determines eligibility. A local dependency is satisfied when it is verified or released; M0 is the verified initial prerequisite.

## The D1 example: an epic inserted as a prerequisite deliverable

Source: `docs/project/backlog-governance-model.md` § "The D1 example". Primary.

> D1 was inserted because q4xpcc could revise its Phase 24A plans using stable contracts before the complete FDAU engine existed.

> This is a useful answer to the apparent paradox that D1 is verified while much of C/A/R/P is queued or specified: D1's deliverable is a reviewed design-and-brief package. Its acceptance gates ask whether that package exists and is coherent, not whether the future runtime exists.

Source: `ROADMAP.md` § "D1 — q4xpcc contract-handoff readiness epic". Primary.

> D1 freezes consumer planning contracts without delivering runtime artifacts.

> D1 changes readiness priority only: it does not change T1.3's dependency, C/A/R/P delivery order, G1, adoption boundaries, or release gates.

## Release gate and release decision

Source: `ROADMAP.md` § "G1 — Canonical vertical-slice review". Primary.

> `G1` is a release gate, not an implementation epic. It begins only after `C4.4`, `A1.9`, `R1.7`, and `P1.6` are verified. It reconciles identity, timing, quality, lineage, continuity, recovery, replay, projection loss, source artifacts, and installed artifacts before a separate release decision.

Source: `ROADMAP.md` § "Version 0.1.0 release gates". Primary.

> - [ ] `C1.1` through `C4.4` verified and independently reviewed.
> - [ ] `A1.1` through `A1.9` verified and independently reviewed.
> - [ ] `R1.1` through `R1.7` verified and independently reviewed.
> - [ ] `P1.1` through `P1.6` verified and independently reviewed.
> - [ ] `G1` reconciles the complete canonical vertical slice.
> - [ ] Source and installed-wheel verification passes on supported Python 3.12.
> - [ ] A separate release review authorizes publication.
>
> No checked gate authorizes release by itself.

Source: `BACKLOG.md` § "Canonical release boundary". Primary.

> Before any release, separately reviewed increments must implement:

Source: `ROADMAP.md` § "Status model". Primary.

> | `deferred` | Deliberately outside the active release path. |
> | `released` | The verified slice is included in a published release. |

## Work IDs versus release versions; `candidate_release`

Source: `docs/project/backlog-governance-model.md` § "Work IDs and release versions answer different questions". Primary.

> This repository does name an intended 0.1.0 release gate. It does **not** embed 0.1.0 in child identities. C2.3 remains C2.3 if a gate or schedule changes. Whether it belongs in a particular release is a separate planning and authorization statement, with its own evidence.

> A target release may still be recorded for planning, but it should remain a separate, revisable relationship. Publishing the release then requires the applicable release gate and its own decision. A version number cannot serve as completion evidence.

Source: `docs/project/backlog-governance-model.md` § "Candidate pattern for gzkit and airlineops". Primary.

> The transferable classification is by **capability or feature family** and then by **specific outcome**. A family names a coherent area of product or repository responsibility; a child names one result that can be specified, reviewed, and evidenced. A family may include design or tooling outcomes as well as runtime features. Release assignment is a separate relationship that can be revised without changing either ID.

> 4. Can a release view select eligible children and enforce a gate without becoming the source of their identities or status?

## ADR, feature record, release record

Source: `docs/project/backlog-governance-model.md` § "ADRs, feature records, and releases are different records". Primary.

> A **feature record** is the proposed local artifact name for a capability or reviewable outcome. It answers **what result is wanted, for whom, under which constraints, with which prerequisites, and what evidence will prove delivery**. It can link to one or more ADRs. A feature may need no new ADR if existing decisions already govern it. A feature can be split, deferred, or dropped without rewriting a decision's history. This artifact name and schema are a recommendation, not a published ADR standard.

> A **release record** selects completed outcomes, checks compatibility and release gates, and receives a version.

> | Record | Stable identity represents | Own status answers | Typical links |
> | --- | --- | --- | --- |
> | ADR | One significant choice and its rationale | Is this decision proposed, accepted, or superseded? | Architecture, affected feature records, superseding ADR |
> | Feature record | One capability or reviewable outcome in a family | Is this outcome specified, in progress, verified, or released? | ADRs, dependencies, briefs/plans, tests, evidence |
> | Release record | One published artifact and compatibility boundary | Is this release candidate ready, authorized, and published? | Included feature records, gate evidence, version/tag |
> | Issue | One tracker conversation or defect report | Is the issue open or resolved? | Any of the above; its number need not encode meaning |

> The relationships are many-to-many. The same retention-policy ADR may constrain configuration, rollup, and purge-safety features; a rollup feature may also depend on a separate storage-interface ADR. The release selects the features that actually ship.

Source: `docs/project/backlog-governance-model.md` § "Proposed classification and minimum schemas". Primary.

> A pool idea without a chosen solution belongs in a capability pool, not in an accepted-decision register.

> A feature record minimally needs a stable ID under a named capability family; one-sentence outcome and owner; architecture and governing-ADR links; dependencies; scope/non-goals; acceptance claims; mutable delivery status; plan/brief links; and evidence. `candidate_release` is optional, mutable planning data. `released_in` is historical evidence added after publication. These are different fields: the former can slip, the latter cannot be revised merely to replan. Keep issue numbers as aliases or links.

## Shape as stated

In its own terms, FDAU has five node kinds in `ROADMAP.md`: **milestone** (a verified prerequisite), **epic** (a related family of local children, a stable area of responsibility, no own state), **local child** (one independently planned, reviewed and evidenced outcome; the only selectable unit; carries acceptance gates), **release gate** (a cross-child reconciliation such as G1 with derived readiness only), and **external boundary** (when another owner may act). `BACKLOG.md` holds mutable child state and gate evidence. One design may govern several children (even across epics); one plan covers exactly one child; plan tasks sit beneath it. Prerequisites are explicit acyclic dependency edges between children (or M0), satisfied when the predecessor is verified or released; D1 shows a whole epic inserted to deliver a design-and-brief package that makes external work eligible. Release is a separate decision after the release gate(s); the release record "selects completed outcomes" and receives a version, while a child's `candidate_release` is optional mutable planning data and `released_in` is post-publication history. The retrospective spec proposes a "feature record" (one capability or reviewable outcome) and a "capability pool" for ideas without a chosen solution; it names no container that groups children by shared value other than the epic (which groups by responsibility family) and the release gate (which groups by what must be reconciled before a release).
