---
name: gz-wp
persona: main-session
description: Use to create, attach issues to, move, change, add evidence to or record an issue close on a work package (WP-<NN>-<slug>) through gz wp.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-11-08
metadata:
  skill-version: "0.15.0"
model: sonnet
---

# gz-wp

Run a work package through its record, lifecycle and change ladder with `gz wp`
(drydock RO-5, `docs/governance/harbor-ro5-work-packages.md`). This is the lean
wielder the operator ruled for tranche 2 ("New lean gz-wp skill (Recommended)",
2026-10-28); RO-12's contractor kit composes it.

## The record

A work package is `delivery` (it names one outcome) or `repair` (it names one or
more GitHub issues and stores its lane). Its record in
`data/catalog/work_packages.json` holds the formal work package (initial
conditions, procedure, test and inspection, system restoration, each text or
`NA`), its objective quality evidence, its planned alterations and its
departures from specification. Never edit the file by hand (ruling 3):

```bash
uv run gz wp new --kind repair --slug <slug> --issue <n> --lane lite [--alias RO-<n>]
uv run gz wp new --kind delivery --slug <slug> --outcome <code> [--alteration ID:replaced:<text>]
uv run gz wp attach <WP-id> --issue <n>
```

Attaching an issue, by `new` or `attach`, also labels it `repair` and comments
the package id on it, aliases in parentheses (ruling 7); the verb creates the
label when the repository lacks it. If `gh` fails, the verb exits 2 and writes
nothing; fix `gh` and re-run.

## Objective quality evidence

The OQE is required from initiation (amendment 1). Record each receipt, commit
or path as the work produces it, so the record stands without explanation:
`uv run gz wp evidence <WP-id> --oqe "<entry>"`. Entries are append-only.

## An issue's close

`ghi-close` records each fixed issue against its repair package (ruling 10):
`uv run gz wp resolve <WP-id> <n> --commit <fix-sha> --reviewer <reviewer>`.
The last issue's close never closes the package; it closes only through Gate 5.

## The lifecycle

One step at a time. A delivery package moves `initiated`, `frozen`, `commenced`,
`accepted`, `closed`. A repair package moves only `initiated` to `closed`: steps 2
to 5 are its orders' (below), and its own freeze, commence, accept and acceptance
refuse and name the order's verb (RP-12 ruling 44).

1. **Initiate on the operator's words.** Only the operator initiates a work
   package. Pass their words verbatim; never author them.
   `uv run gz wp initiate <WP-id> --operator-text "<their exact words>"`
2. **Freeze after the independent review.** A reviewer who did not write the
   baseline checks each REQ against the nine criteria; the operator approves
   every planned alteration.
   `uv run gz wp freeze <WP-id> --baseline REQ-<n>@<rev> --risk-note "<note>" --review-receipt <id> --approve-alteration <id> --evidence <id>`
3. **Commence** once every surface the package works has its tag hung:
   `uv run gz wp commence <WP-id> --evidence <what was checked>`. This crosses the
   airlock and books `airlock_in`.
   Commit the package's work under a `Task:` trailer that starts with the lowercased
   package id, such as `TASK-wp-02-resume-#1185`: that trailer is how the exit knows
   the commit is the package's. A defect fix keeps its own trailer.
4. **Prove and review.** `uv run gz wp acceptance <WP-id> init --author <session>`,
   then `prove --spec <file>` and `review --receipt <run-id>`, on the frozen REQs. Spec, quality and adversarial reviews approve each proof. A
   package gets three adversarial rounds with a mapped finding; dispatch, accept and
   `human-review` then refuse until `gz wp block` and the operator's unblock. See
   `docs/user/manpages/wp-acceptance.md`.
5. **Accept** at final inspection with no tag still hung, once
   `uv run gz wp acceptance <WP-id> status` reads ready:
   `uv run gz wp accept <WP-id> --evidence <inspection>`. This crosses the airlock
   outward. A package stopped by an
   exit is excused, and unless its acceptance reads ready it closes as `redirect`,
   `pause` or `terminate`.
6. **Close through Gate 5.** The attestor is the operator and is never
   defaulted. Account every alteration and name each departure still open. A
   repair package closes from `initiated` with the same payload (ruling 62).
   `uv run gz wp close <WP-id> --decision proceed --attestor g0 --residual-risk "<risk>" --account <alt-id> --evidence <id>`

## Withdrawing a legacy unit

`uv run gz wp withdraw-legacy <OBPI-id> --reason "<why, and where its REQs went>" --attestor g0`
withdraws a legacy OBPI for good, as `gz obpi withdraw` does; RO-8 runs it on the
operator's word. It takes a legacy id, not a package, the attestor is human and never
defaulted, and `--dry-run` shows the event first.

## The run

Once commenced, each dispatch is booked, and the runtime holds the fix-cycle bound:

1. `uv run gz wp dispatch <WP-id> --role Implementer --model <tier> --req REQ-<n>`,
   and the same for `SpecReviewer` and `QualityReviewer`; a repair package's run
   verbs name `--order <ORD-id>`, and an issue is never a subject (ruling 64). The
   bound counts against that frozen subject, across packages: its first dispatch
   is free, any review in the package arms it, and each later one is a fix cycle. A delivery package that
   cannot dispatch declares `--role SingleDriver --reason "<why>"`; a repair package
   cannot. The verb mints the dispatch's id and prints its `GZKIT-DISPATCH:` line:
   put that line in the dispatched agent's prompt, and name another project's root
   with `--root <dir>` when the dispatch is meant for one (RP-12 rulings 1 and 35).
   A stamped `gz` call from any other root exits 3 before it writes (ruling 36).
   A dispatch you booked and will not spawn, or handed to a harness with no
   hooks, holds ad hoc subagents to no root while it is open: void it from the
   main session with `uv run gz wp dispatch <WP-id> --void <D-id> --reason "<why>"`
   (rulings 40 and 42).
2. **At the bound the dispatch refuses (exit 3).** Do not route around it: a further
   repair cycle does not exist. Escalate:
   `uv run gz wp block <WP-id> --reason "<why>" --next-action "<decision>"`. The
   runtime writes the count; you may add a recommendation among the exits.
3. **The operator rules:**
   `uv run gz wp unblock <WP-id> --ruling "<their exact words>" --operator g0 --exit <exit>`.
   `reopen` and `departure` add `--req REQ-<n>`, the REQ at the bound, and a waiver
   is recorded through `gz wp change` since the block first. `hold` and `terminate` name no REQ.

## The change ladder

Every change to a live package is one `gz wp change` with its rung:

| Rung | Approver | Must carry |
|------|----------|------------|
| `pen_and_ink` | coordinator | `--superseded` |
| `change_order` | operator | `--superseded`, `--work-stopped` (work stops when the need is found) |
| `attachment` | operator | added work inside the boundary, no new tag-outs |
| `supplement` | operator | `--supplement <WP-id>`; a test change by change order is one |
| `alteration` | operator | `--item <id>` (`--configuration-change` for a new one) |
| `departure` | operator | `--item <id> --form deviation\|waiver --duration temporary\|permanent [--clear-by]` |

An order sits inside a package: the unit Gate 5 sits at (RP-12 O2). Write its
record with the next `ORD-<NN>-<slug>`; its kind is its package's. Only a repair
package that is initiated and not closed takes one until RP-14, and an alias is
unique within its package (rulings 43 to 49). The order is born on the ledger:
the verb books its `order_transitioned` to `opened` on the operator's words
before it writes the record (ruling 52):

```bash
uv run gz wp order new <WP-id> --slug <slug> --purpose "<what it restores>" \
  --operator-text "<the operator's words>" [--alias O<n>]
```

A repair requirement is held on its open repair package and answers an issue the
package carries; write it with the next `REQ-<n>` (rulings 45, 48). A change to
its obligation is a new REQ carrying `--supersedes`, never an edit (ruling 31):

```bash
uv run gz wp req new <WP-id> --statement "<what must hold again>" \
  --criterion "<state>|<outcome>|<evidence>" --kind BEHAVIOR --problem-report <n>
```

Once its repair requirements are written, freeze the order on them, then record
commencement. The order moves one step at a time while its package is initiated
(rulings 2, 44). Its baseline holds only repair REQs held on its package, each in
one live order's baseline at a time (ruling 53). The freeze seals the package's
footprint, which must be valid as a brief's Allowed Paths are, so a change order may
then only add a path (ruling 56), and approves each planned alteration no earlier
order's freeze approved (ruling 63). Commencement crosses the airlock (ruling 65).
Commit the order's work under the package's `Task:` trailer, as step 3 says:

```bash
uv run gz wp order freeze <ORD-id> --baseline REQ-<n>@<rev> --risk-note "<risk>" \
  --review-receipt <receipt> [--approve-alteration <id>] --evidence "<what justifies it>"
uv run gz wp order commence <ORD-id> --evidence "<what justifies it>"
```

The order's run is the package's run with `--order`: dispatch only against a REQ
the order's freeze holds, while the order is commenced (ruling 57). A block on the
order holds that order alone, its dispatches and moves refused until the operator
rules; the package's other orders carry on (ruling 59). A blocked, accepted or
stopped order fences production writes across the tree, as a package does
(ruling 58):

```bash
uv run gz wp dispatch <WP-id> --order <ORD-id> --role Implementer --model <tier> --req REQ-<n>
uv run gz wp block <WP-id> --order <ORD-id> --reason "<why>" --next-action "<decision>"
uv run gz wp unblock <WP-id> --order <ORD-id> --ruling "<their exact words>" --operator g0
```

Acceptance runs on the order, its obligations the order's frozen REQs and its
proofs and reviews under its id; accept refuses until it reads ready and the
package's sealed footprint holds, the order and requirement stores aside (ruling
66), a stopped order excused (ruling 60), and crosses the airlock outward. A freeze
names at least one REQ (ruling 61):

```bash
uv run gz wp acceptance <ORD-id> init --author <implementing session>
uv run gz wp acceptance <ORD-id> status
uv run gz wp order accept <ORD-id> --evidence "<final inspection>"
```

Gate 5 at the order closes it, on the operator's verbatim words, which you relay
and never author. It closes from `accepted`, or from `opened` as a terminate alone;
each decision carries its own field and refuses the others': proceed the residual
risk, redirect an order of the same package already opened and not frozen, pause
the revisit condition, terminate nothing more. A subagent's call is refused
(rulings 73 to 77):

```bash
uv run gz wp order close <ORD-id> --decision proceed --attestor g0 --attestation-text "<the operator's words>" --residual-risk "<text>" --evidence "<what justifies it>"
```

Work outside the package's general scope is a new work package, never a change.
A departure from specification is recorded only where the work cannot meet its
own approved specification; a difference from the prior shape is not one.

## Read

`uv run gz wp order show <ORD-id>` prints an order's record, its package's kind, and
its state and baseline from the ledger;
`uv run gz wp show <WP-id>` prints the record, the state and the history;
`uv run gz wp runs` reports what the ledger says every run in flight, a package's or
an order's, has reached;
`uv run gz validate --catalog` checks the store against RO-5's rulings.

## Common Rationalizations

| Thought | Reality |
|---------|---------|
| "I'll fix the JSON directly, it's one field" | The store is edited only through verbs (ruling 3); a hand edit skips the checks `gz validate --catalog` reads. |
| "The operator clearly wants this started" | Initiation carries the operator's words. Without them there is no initiation. |
| "This scope change is small, pen and ink will do" | Pen and ink is administrative. A change to scope, boundary or test is a change order, and work stops. |
| "The close can default the attestor" | Gate 5 is the operator's own act; `--attestor` is never defaulted. |

## Red Flags

- Writing `data/catalog/work_packages.json` with an editor or a script
- An `--operator-text` the operator did not say
- A change order recorded without `--work-stopped`
- Calling a remodel a departure from specification
