# R&D run — design-amendment

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-09-27T17:40Z.

**Challenge.** Operator g0, `/gz-rnd` invocation, current conversation · read 2026-09-27,
verbatim:

> formalize amendment of a prior design (yes, we don't have an ammend verb and that can
> happen with reference to the original - we can do GHI or we can do an amended
> OBPI-REQ-TASK. I would think even both. I know that these things get heavily sealed with
> receipts from ceremony, but the REQ/TASK system has annotations that allow for select
> tests to specifically pass against them, let alone the full suite, so we probably need a
> way to indicate that an ADR has been amended and specify which subpart has been. No need
> to re-open it. Right now, we are stuck with a bad design of tight coupling of adr to
> release. So, rnd is really going to have to talk use through. at a minimum and amendment
> should a mandatory patch release bump regardless of what other work is completed. So, we
> need commands and ledgers for sure. not sure about gate because I don't want to fully
> re-enter entire pipelines. Also, we don't change the original REQ, a new one would be
> added. not sure about nomenclature. we DO need new build (GHI might be fine) and V&V
> processes. I agree about the need to resovle gates. Not sure about 611, refresh me.
>
> There is no doubt we are in rnd territory here.

Earlier in the same conversation, the operator framed the class, verbatim: *"we likely have
something new we are dealing with, which is a formalization of an amendment of a prior
design without a full-blown total revision or subsumption"* and *"we need to be able to
revise priors without going into a deep new adr. I guess we have no amendment provision in
our governance."*

The first instance that raised it: the operator's intent to amend `REQ-0.0.32-05-03` so
that adopter edits to gzkit-shipped files are overwritten, applied to every shipped surface
rather than skills alone — *"it is just not feasible to allow downstream adopter edits for
the sake of stability."*

---

## source · the attested REQ that seeded the run

`docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/OBPI-0.0.32-05-init-update-flag.md:165`
· read 2026-09-27

> - [ ] REQ-0.0.32-05-03: STALE artifacts are refreshed in place; EDITED artifacts are NOT overwritten and surface as conflicts

`uv run gz adr status ADR-0.0.32` on 2026-09-27: lane `heavy`, lifecycle `Validated`,
OBPI 15/15. The behaviour this REQ asserts was made to work that morning by GHI #1122
(`3cad9e3f1`), which shipped `src/gzkit/canonical_history.json` so `--update` can tell an
edited file from a stale one.

## source · the only ruled precedent for amending an attested REQ

`docs/governance/attested-req-subject-retirement.md` § Worked example 3 · read 2026-09-27

> - the REQ line keeps its attested text and gains a dated `Amended 2026-09-26` note
>   quoting the ruling — the record of 2026-05-06 is not rewritten;
> - the covering test keeps `@covers("REQ-0.0.29-02-06")` and asserts the amended
>   behaviour, with its docstring recording why;

and, from § The discriminator:

> One instance has been escalated and ruled (§ Worked example 3); that
> ruling decided its own case and is not a procedure for the next one.

The precedent re-pointed the covering test at the original REQ ID. The challenge departs
from it: *"we don't change the original REQ, a new one would be added."*

## source · GHI #611, the corrective-action primitive

`gh issue view 611` · read 2026-09-27. Title: *"governance: no general append-only
corrective-action primitive to undo agent/human error (repudiate is a point-solution)"*.
Operator intent, verbatim from the body:

> "we need the power to UNDO agent (or human) error"

> "not to erase the ledger, but to provide subsequent corrective actions."

Comment of 2026-09-06T23:58Z, verbatim, on what shipped:

> | 1 | *"A governed, **append-only corrective-action primitive**"* | **Delivered** — `ledger_event_corrected` over all 75 declared types; `gz ledger correct` |

> **Settled** — one meta-action not a typed family; whole artifact graph; last-correction-wins; `reinstated` plus required `attestor`/`reason`

Comment of 2026-08-18T01:12Z, verbatim, separating it from the attested-REQ case:

> They differ on premise: error versus supersession-of-subject. A general corrective-action
> primitive built for #611 would not answer #823, because there is no erroneous event to
> supersede.

The issue remains OPEN on one clause: migrating `repudiate`, `park` and `block` onto the
shipped port, which awaits an operator design call.

## source · how a patch release qualifies today

`.gzkit/skills/gz-patch-release/SKILL.md` § When to Use · read 2026-09-27

> - **Either qualifier holds:**
>   - **Behavior-level GHIs** closed since last tag with runtime label + src diff
>     (auto-discovered by `gz patch release --dry-run`)
>   - **Foundation-ADR closeouts** — a foundation ADR (`0.0.x`) reached
>     `Validated` status with all OBPIs `Validated` and a Gate-5 `validated`
>     receipt in the ledger since the last tag (auto-discovered by
>     `gz patch release --dry-run`)

Minor and major releases go through `gz closeout`. So a feature ADR's identifier is its
minor release, and a patch release has exactly two qualifiers. An amendment is neither.

## source · the REQ identifier grammar

`src/gzkit/triangle.py:31` · read 2026-09-27

> REQ_ID_BODY = r"REQ-(?P<semver>\d+\.\d+\.\d+)-(?P<obpi_item>\d{2})-(?P<criterion>\d{2})"

A REQ ID encodes its ADR semver, its OBPI item and a criterion number. `src/gzkit/tasks.py:123`
derives TASK IDs from the same three parts. Any amendment REQ either fits this grammar or
extends it.

## decision · positions the operator stated in the challenge

These came in the operator's invocation text and are carried as the run's starting
constraints, not re-asked:

- the original ADR is not re-opened — *"No need to re-open it."*
- the original REQ is never changed; a new REQ is added — *"we don't change the original
  REQ, a new one would be added."*
- an amendment forces a patch release — *"at a minimum and amendment should a mandatory
  patch release bump regardless of what other work is completed."*
- it needs commands and ledger events — *"we need commands and ledgers for sure."*
- it needs a build and V&V route, possibly a GHI — *"we DO need new build (GHI might be
  fine) and V&V processes."*
- the ADR-to-release coupling is named as a bad design — *"we are stuck with a bad design of
  tight coupling of adr to release."*

Open on the operator's own word: nomenclature, and which gates run.

## decision · #611 is a neighbour, not the vehicle

An amendment revises a design that was right when it was made. #611's primitive
(`gz ledger correct`) exists to say an earlier row was false (`void`) or has lapsed
(`discharged`). Using it to amend would record the original REQ as wrong, which falsifies
the attestation. The same separation #611's own 2026-08-18 comment draws for #823 applies
here. What may still be reused is its mechanics: an append-only forward event naming its
subject, with Layer 3 netting the result.

Agent's reading, pending the operator's confirmation in the interrogation.

## decision · the release route for an amendment is a patch release

The ADR-to-release coupling leaves an amendment no minor version to ride. Operator,
verbatim: *"we will have moved on from a feature (foundations are retired) minor version
anyhow, so the only recourse is patch releasing."* A shipped amendment therefore becomes a
third patch-release qualifier beside the two in `gz-patch-release` § When to Use.

## decision · Q1 — the amendment is its own record, riding with the original ADR

Asked: where does the new REQ live — (A) a separate amendment record attached to the
original ADR, (B) appended to the original sealed brief, or (C) in the GHI body.
Recommended A. Operator, verbatim: *"yes, A, something that rides along with the original
ADR and references the OBPI/REQ/TASK(s) it is related to. it must be GHI'd and we likely at
least get acknowledgement as a gate 5."*

Carried with it, same turn, verbatim:

- *"Also, BDD and TDD might have changed."* — an amendment's V&V covers both the unit tier
  and the behave tier, not only the unit tier.
- *"Yes to a ledger event."*
- *"I don't believe we need a full re-entry into the pipeline."*
- *"So, I think A, but I seem to require a bit more review with it and you."* — A is the
  working choice, open to review, not closed.

Two threads opened by the same turn and placed on the frontier:

- **Gate 5's register.** *"acknowledgement as a gate 5"* joins two words canon keeps
  apart: Gate 5 is completion attestation (`AGENTS.md` § Gate Covenant), and
  acknowledgement is the lighter transit register `gz handoff decide` uses (GHI #757).
  Which one an amendment carries is open.
- **Adversarial review as a reusable part.** Verbatim: *"I am starting to think that the
  adversarial aspects baked into the obpi pipeline are really needed elsewhere at times.
  Hard part is backing that out to be modular for reuse. Not sure."*

## source · REQs have no machine-readable retired state

GHI #611, comment of 2026-07-28 · read 2026-09-27

> The available vocabulary is `- [ ]` / `- [x]` (`ReqStatus.UNCHECKED` /
> `CHECKED` in `src/gzkit/triangle.py:66-70`) — there is no third value meaning
> *"retired; no longer owed."* So the author's only channel is bold prose that no
> scanner reads, and the REQ reports as an open obligation permanently.

> Whatever primitive this issue lands should be able to answer: *given a REQ,
> is its obligation live or retired, and by which authorizing event?*

The same comment lists eight REQs already superseded in prose only: `REQ-0.0.41-02-07`,
`REQ-0.0.59-03-03`, `REQ-0.0.63-03-01` through `-03-04`, `REQ-0.0.63-06-01`,
`REQ-0.0.63-06-02`. Under design A, the amended REQ is a ninth of the same shape: it
stays untouched, yet its behaviour is no longer owed.

## decision · Q2 — the amended REQ is marked superseded by a ledger event, never erased

Asked: once the amendment ships, what happens to the original REQ and its covering tests —
(A) a ledger event marks it superseded by the new REQ and readers treat it as no longer
owed, (B) delete the tests and change no state, (C) keep the tests skipped. Recommended A.
Operator, verbatim: *"A, supersede via ledger event - tests need to be either adjusted or
sunsetted (likely the best)."* and *"yes, we'd need to mark it, but not erase it. I agree
with your A."*

On why a GHI carries it, verbatim: *"we are amending upstream it would seem the ADR->OBPI
now has something new in their chain of assumptions. the flaw you've found in superseding
priors is a real problem, but we are here to help solve that. we must adjust all downstream
side effects as a part of the work, that is why GHI is very appropriate here."*

So the amendment's scope includes every downstream surface its change falsifies — tests,
behave scenarios, docs, manpages, skills — adjusted in the same work. The concrete instance
for 05-03: `tests/commands/test_init_update.py:299` and `features/init.feature:32` both
assert the behaviour being retired.

## decision · amendment work is a GHI-routed change, possibly with its own mini pipeline

Operator, verbatim: *"On gate 5, I think we need some acknolwedgement that the amendment is
sane. But I am not sure if we want a "mini obpi pipeline" - we may need one any way, if so,
that takes care of the adversarial review question because we'd bake it into the
gz-obpi-amend pipeline. that skill would keep all of these rules, we'd still GHI it because
it is a "change/fix/refactor" and not truly newly introduced feature/behavior."*

Settled by this: an amendment is classed as change, fix or refactor, not new feature, so it
routes through a GHI. Still open: whether the mini pipeline exists, and Gate 5's register.

## decision · Q3 — full Gate 5 attestation; a mini pipeline exists

Asked: at Gate 5, (A) full attestation, (B) a lighter acknowledgement like
`gz handoff decide`, or (C) no Gate 5. Recommended A, on the asymmetry that the original
REQ was attested, so a weaker witness must not retire it. Operator, verbatim: *"A, full
attestation, retiring attested canon needs attestation. That means we need a new "mini
pipeline" here which is also tied to a GHI. if we are going to attest, we're getting out
the heavy lane here - which means some form of 4a and 4b. It doesn't have to be shaped
exactly like the obpi-pipeline, but it feels like a lighter version of it to me."*

Settled: attestation, not acknowledgement; a mini pipeline, GHI-tied; a Step 4a and a
Step 4b in some form; shaped as a lighter OBPI pipeline, not a copy.

## source · what Step 4a and Step 4b are in the OBPI pipeline

`.gzkit/skills/gz-obpi-pipeline/SKILL.md:61,74,75,77` · read 2026-09-27

> No pause except the Stage 4 human attestation in Normal mode — and that pause comes only
> **after** Step 4b (the independent adversary) has run and its verdict is on the table.

> | "My Step 4a evidence is green — tests pass, REQs covered — so I can present it and await attestation" | STOP. Green-on-your-own-evidence is the EXACT state Step 4b exists to distrust.

> | "Step 4b is probably overkill for this small/authoring-only/obviously-correct OBPI" | There is no size, lane, or kind exception to Step 4b.

> Codex (tier 1) is REQUIRED first; tier 2 is permitted ONLY after a checked `ready: false`.

Step 4a is the authoring agent's own evidence; Step 4b is an independent, cross-family
adversary. In the OBPI pipeline, 4b is already lane-independent.

## decision · Q4 — the amendment's own change sets Gates 3 and 4

Asked: what sets the amendment's gates — (A) Gates 3 and 4 by what the amendment changes,
using the OBPI lane test, (B) always heavy, (C) the original ADR's lane. Recommended A.
Operator, verbatim: *"A, gates set by what the amendment changes."* and *"So, yes, your A
seems good."*

A design constraint came with it, verbatim: *"Be careful that we don't over emulate the
obpi pipeline here, I make reference to 4a and 4b as that is part of the adversarial review
system."* The mini pipeline borrows the adversarial review system; it does not copy the
OBPI pipeline's stages.

And a wider signal, verbatim: *"I can see that we'll want one eventually for ghi-close
too."* Adversarial review is wanted beyond OBPIs and amendments. That is the
reusable-review thread already on the frontier.

Left open by the operator, verbatim: *"if we are lite-lane, then I suppose we don't bring
in 4a and 4b? let's use judgment here and understand AGENTS.md's warning, which is
prudent."*

## decision · Q5 — Steps 4a and 4b run on every amendment, the adversary sized to the change

The agent applied the AGENTS.md § Gate Covenant test, verbatim: *"Gates 1–4 verify the
artifact, and whether their question has a subject depends on what changed, so lane scopes
them. Gate 5 asks who accepted the work; every completion has an accepter, so nothing
scopes it."* Behave has no subject in a doc-only amendment. Step 4a (the evidence the
operator attests against) and Step 4b (whether agent-authored evidence can be trusted
before attested canon is retired) have a subject in every amendment.

Asked: (A) 4a and 4b on every amendment, the adversary's scope sized to the change, only
Gates 3 and 4 lane-scoped; (B) lite skips 4b; (C) lite skips both. Recommended A.
Operator, verbatim: *"Okay, go with A."*

The OBPI pipeline's ceremony around 4b (plan-audit receipts, multi-round stages) is not
carried over, per the Q4 constraint against over-emulation. What is carried over is a
second model family checking the work before the operator attests.

## source · ADR-0.0.32 REQs that assert adopter-edit protection

`docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/` · read
2026-09-27, verbatim REQ lines:

> - [ ] REQ-0.0.32-02-04: Project-first → package-fallback resolution holds; `skip_existing=True` preserves operator edits

> - [ ] REQ-0.0.32-04-06: Project-first → package-fallback resolution holds; `skip_existing=True` preserves operator edits

> - [ ] REQ-0.0.32-05-03: STALE artifacts are refreshed in place; EDITED artifacts are NOT overwritten and surface as conflicts

> - [ ] REQ-0.0.32-10-06: Project-first → package-fallback resolution holds; `skip_existing=True` preserves operator edits

> - [ ] REQ-0.0.32-12-08: `skip_existing=True` preserves operator edits to `.gzkit/templates/<name>.md`

> - [ ] REQ-0.0.32-14-03: Without `--force`, EDITED project-local artifacts are reported as conflicts and left unchanged; exit non-zero when any EDITED conflict remains; exit 0 when zero c

Also bearing on it: `REQ-0.0.32-02-07`, `-04-08` and `-08-11` require
`skill-surface-sync.md` to document that `gz init` populates the adopter's copy, and
`REQ-0.0.32-05-06` documents the operator-edit marker. This came from one keyword pass
over one ADR's briefs, so it is a lower bound: other ADRs may carry REQs of the same shape.

The operator's pervasive position therefore reaches at least six REQs across six OBPIs
(02, 04, 05, 10, 12, 14), not the one REQ first named.

## decision · Q6 — one amendment per ADR, named at ADR level

Asked: what does one amendment cover — (A) one per ADR, superseding REQs across any of its
OBPIs, (B) one per OBPI, (C) either, chosen each time. Recommended A, since the first real
case spans six OBPIs. Operator, verbatim: *"A, one amendment per ADR"* and *"as far as
naming scope, sure, if we want it to go ADR-level, that's fine."*

With it, verbatim: *"Remember that all skills are skills + gz CLI surfaces."* The amendment
capability is therefore a pair: a skill and the `gz` verbs it drives. Naming it means
naming both.

## source · what `gz init` places in an adopter's repo

A scratch repo, `git init` then `uv run gz init` (exit 0), 2026-09-27. Top level of
`.gzkit/`, verbatim `find .gzkit -maxdepth 1`:

> .gzkit/chores
> .gzkit/ledger.jsonl
> .gzkit/ledger.jsonl.lock
> .gzkit/manifest.json
> .gzkit/personas
> .gzkit/rules
> .gzkit/skills
> .gzkit/templates

Outside `.gzkit/`, the same run wrote `.agents`, `.claude`, `.codex`, `.github`,
`.gzkit.json`, `.pre-commit-config.yaml`, `AGENTS.md`, `CLAUDE.md`, `design` and a
Python project skeleton. Hooks are generated from code by
`src/gzkit/hooks/claude.py` (`setup_claude_hooks`) and are not in
`src/gzkit/canonical_history.json`, which tracks five surfaces: chores, skills, rules,
templates, personas.

## decision · the tooling and the aircraft are two separate things

The run nearly misaligned on ownership, because gzkit builds itself with gzkit. Settled
across three turns, operator verbatim:

> I created gzkit after I realized that the factory, jigs, and tooling, and the aircraft
> being designed/assembled, are two separate things.

> gzkit is my tool, that can be used to design/manufacture/maintain other artifacts,
> projects, tools, etc. When I ship gzkit and it is adopted, it is tooling to now create
> other things.

> When an adopter updates/upgrades gzkit, some or all of its foundational surfaces are
> updated/replaced. If they modified originals, they will lose those - I have no plans for
> configirability for modification for the first 1.0 release - that is too much scope.

> an adopter is not encouraged to modify anything about gzkit, it is not a good idea. That
> keeps it simple.

> Your statement is correct, we can use amendments to planning/delivery artifacts while we
> are building gzkit and so too can adopters for THEIR artifacts. BUT, they may not modify
> ours. Even if they do, the next update will overwrite everything.

> I think we have a match.

The statement the operator confirmed: in an adopter's repo, gzkit's tooling (the five
shipped surfaces, the harness skill copies, the generated hooks) belongs to gzkit; an
upgrade replaces it, and adopter edits are overwritten. The adopter's records under
`.gzkit/` (the ledger and what accrues beside it) belong to the adopter's project; an
upgrade never touches them. Nobody hand-edits either: records are written only through
`gz` verbs, in the adopter's repo as in this one.

Consequences for this run:

- The amendment capability ships. Adopters use it on their own ADRs; gzkit's first use is
  on its own ADR-0.0.32 (the dogfood). Operator: *"yes, they will generate ADRs for their
  project just like we do."*
- In the gzkit repo, `.gzkit/` stays editable: it is where the tooling is made. Operator:
  *"that is a byproduct of dogfooding (and the pain of it)"*.
- Extension and configuration of gzkit's tooling by adopters are not designed, and this
  run assumes neither. An earlier agent statement that adopters could add their own skills
  under non-colliding names was retracted.
- The files `gz init` writes once outside `.gzkit/` (`AGENTS.md`, `design/`, and
  `settings.json`, which mixes gzkit's hooks with the adopter's own settings) are not
  classified here. The amendment names the tooling explicitly and leaves the rest open.

## decision · Q7 — the noun is "amendment"

Asked: (A) amendment, (B) engineering change notice, (C) revision. Recommended A: the
original text stays and the amendment is appended with its date and authority, the sense
the campaign's § Amendments and the briefs' informal *"Amended <date>"* notes already use.
Rejected with reasons: *revision* implies re-issuing the whole document, which the challenge
excludes (*"without a full-blown total revision or subsumption"*); *engineering change
notice* sits too close to *work order*, which canon reserves for a GHI; *erratum* and
*correction* imply the original was wrong (#611's premise); *patch* collides with patch
release; *supersession* names the effect on the old REQ, not the act. Operator, verbatim:
*"A, amendment"*. Working names that follow: the skill `gz-adr-amend` and an `amend` subcommand under `gz adr`; the ADR fixes the final CLI shape.

The operator also said *"yes create the glossary - that is a great DDD thing to have. why
did we not have it earlier? is that not mentioned elsewhere? DDD is not new to gzkit."*
Checking before creating it found the entry below.

## source · gzkit already has a glossary, in the PRD

`docs/design/prd/PRD-GZKIT-1.0.0.md` § 2.1 Ubiquitous Language · read 2026-09-27

> <!-- gzkit-namespace glossary entries. Each entry conforms to UbiquitousLanguageTerm schema (ADR-0.0.43):
>      term, scope (cross-cutting | <bc-slug>), definition (≥10 chars), provenance (list of ADR IDs).
>      Backticked `gz-glossary-<term>` markers in prose resolve here. -->

The section carries 17 entries under three scopes (Cross-cutting, Skill Evaluation,
Governance Triage), including `synthetic-memory` and `nominal-identifier`. No class named
`UbiquitousLanguageTerm` exists under `src/`; the schema is described in
`docs/design/adr/pool/ADR-pool.ddd-domain-cascade.md`, which also proposes a derived
`docs/design/domain/glossary.md` (that directory does not exist). No ADR-0.0.43 file was
found under `docs/design/adr/`.

Against it, the R&D ruling of 2026-09-17, `.gzkit/handoffs/rulings.jsonl:893`, verbatim:

> `GLOSSARY.md` at repo root, following MPAS's CONTEXT.md in function; the name differs
> because `gz context <ADR-ID>` already holds the word (verbatim: "yes ==> GLOSSARY.md at
> repo root").

`rnd-discipline.md` records the premise that ruling rested on, verbatim: *"| no glossary
surface | **`GLOSSARY.md` at repo root**, foundational DDD |"*. The premise was false:
PRD § 2.1 existed. The root file was never created, because neither earlier R&D run landed
a term. Canon now declares two glossary homes, and neither has a validator.

## source · the PRD glossary has barely moved since May

`git log -L '/## 2.1 Ubiquitous Language/,/## 2.2/:docs/design/prd/PRD-GZKIT-1.0.0.md'`
· run 2026-09-27, verbatim commit lines:

> 3efba51c4 2026-08-17 chore: update .gzkit (2 files), README.md, docs/design/adr, docs/design/prd +2 more (gz git-sync)
> 44982fc69 2026-05-23 chore: update .claude (3 files), .gzkit, data, docs/design/adr (2 files) +5 more (gz git-sync)
> 2e6056100 2026-05-22 chore: update .gzkit (2 files), docs/design/adr (32 files), docs/design/prd, docs/governance/GovZero (gz git-sync)

Three touches in four months, two of them in the two days after creation. Operator's
hypothesis, verbatim: *"I don't think we've even looked at or adjusted that glossary since
the creation of the PRD, that means that these entries are old and don't keep up with the
semantics and knowlege graph of what is going on with gzkit over time."* The history
supports it.

## source · how Matt Pocock keeps a glossary

`docs/governance/mpas-appropriation-analysis.md` § `domain-modeling` · read 2026-09-27

> **`CONTEXT.md` is a glossary and nothing else:** *"totally devoid of implementation
> details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for
> implementation decisions."* Each term is one or two sentences plus an `_Avoid_:` list of
> banned synonyms; `CONTEXT-MAP.md` serves multi-context repos.

> update `CONTEXT.md` inline —
> *"Don't batch these up: capture them as they happen."* Files are created lazily, only
> when there is something to write.

His glossary is its own file, fed during design conversation, not a section of a
product-intent document written once.

## source · the DDD guidance gzkit has

`.gzkit/rules/hexagonal-architecture.md` § The cascade & domain cohesion (binding) · read
2026-09-27

> 1. **DDD** — model the domain in governance's ubiquitous language (ADR, OBPI, REQ,
>    GHI, gate, receipt, ledger), never framework-generic nouns. gzkit's domain is
>    **modeled as the ontology** (typed Objects/Links, ADR-0.32.0) — *not* a folder tree.

> Bounded contexts are **subgraphs of the ontology** (corpus /
>    work / source), not directories.

`docs/governance/rnd-discipline.md` § Two taken as technique, operator verbatim: *"no,
other routines use DDD in gzkit, DDD is foundational to gzkit, as are TDD, and BDD."*

What this guidance covers: where the domain model lives (the ontology) and what not to do
(folder partitions). What it does not cover: the practice of keeping the ubiquitous
language current during design. The keyword pass over `.gzkit/rules`, skill files,
personas, `docs/governance`, `docs/user` and `AGENTS.md` found DDD named in two skills
(`gz-foundation-triage`, `gz-health-audit`) and no skill or rule step that has an agent
challenge, sharpen or record terms. TDD has Gate 2 and `@covers`; BDD has Gate 4 and
`features/`; the language arm of DDD has no gate, validator or skill step. A keyword pass
is a lower bound on absence, not proof of it.

## source · the DDD cascade ADR is pooled, and one doc still cites it as enforced

`docs/design/adr/pool/ADR-pool.ddd-domain-cascade.md:157` · read 2026-09-27

> Operator overrode with 'EVERYTHING in scope for 0.0.43.'

Its OBPI list (`OBPI-0.0.43-01` through `-04`, lines 231–234) is all unchecked. It lives
in the pool, so it was not lost. But `docs/governance/agent-contract-rationale.md:349`
still says, verbatim:

> gzkit: ADR-0.0.3 (hexagonal architecture), ADR-0.0.43 (DDD
> cascade), and the package import-direction invariant in ADR-0.0.55
> (Draft) are the structural floor that the corresponding
> `gz validate` scopes pin mechanically.

No `gz validate` scope pins the DDD cascade, so that sentence is false as written. It is a
defect to track, recorded here for the disposition map.

## decision · Q8 — DDD's language arm gets its own R&D run; "amendment" waits for its home

Asked: (A) a separate R&D run on DDD discipline, invoked by the operator, with the
"amendment" term held in this record until that run settles the glossary's home; (B) settle
the home inside this run; (C) put the term into PRD § 2.1 now. Recommended A, because
settling a glossary home as a side issue is how the 2026-09-17 ruling missed PRD § 2.1.
Operator, verbatim: *"okay, I was wrong, he keeps CONTEXT.md - I hope that is a canonical
way to refer to a DDD glossary/DSL. We need option A to make up for this lapse."*

On "canonical": `CONTEXT.md` is Pocock's own convention, not a DDD standard. Evans's term
for the shared vocabulary is *ubiquitous language*, and DDD names no file for it. Pocock
names the file after the bounded context it serves (one `CONTEXT.md` per context, a
`CONTEXT-MAP.md` across them). In gzkit the word collides with `gz context <ADR-ID>`,
which is why the 2026-09-17 ruling chose a different filename. A glossary is also not a
DSL: a glossary is shared vocabulary; a DSL is a language programs are written in. These
are inputs for the DDD run, not rulings.

**commissions:** a separate R&D run on DDD discipline (why the language arm lapsed, where
the glossary lives, how it stays current beside TDD and BDD, and how it fits the hexagonal
rule and the ontology). Only the operator can open it. The "amendment" term lands in the
glossary once that run names the glossary's home.

Operator, next turn, verbatim: *"you keep the need for a DDD run in both a h/o AND in the
magna carta. I am NOT waiting for post 1.0 for that."* Done the same turn: the Magna Carta
amendment of 2026-09-27 in `docs/governance/build-to-1.0-campaign-2026-09-20.md`, and the
checkpoint handoff `.gzkit/handoffs/20260927T194532Z-design-amendment-rnd-in-flight.md`.
Also verbatim, as an input to that run: *"Pocock's CONTEXT.md system is good and worthy of
appropration. He must have some naming convention for them, this is highly worthy of
appropriate during the DDD design makeup."*

## decision · Q9 — amendment and REQ identifiers

Asked: how new REQ IDs are formed, given today's grammar
`REQ-<semver>-<OBPI item>-<criterion>` and an ADR-level amendment. Options: (A) the
amendment takes its own slot in the OBPI position, (B) the next criterion number in the
superseded OBPI, (C) the ADR's next OBPI number. Recommended A. The operator answered *"Yes,
the amend is BEST as the last suffix - almost no matter what. So, yes to "A""*, which
pulled two ways, so the agent laid out A, A′ (`ADR-0.0.32-A01` as the amendment ID) and B
(`REQ-0.0.32-05-03-A01`). Operator, verbatim: *"A as offered, if that makes more sense to
you. A in the way you previously presented it."*

Adopted:

- amendment: `AMD-0.0.32-01`
- its REQs: `REQ-0.0.32-A01-01`, `REQ-0.0.32-A01-02`, …
- its TASKs: `TASK-0.0.32-A01-01-01`, …

The `A` prefix in the OBPI slot marks an amendment REQ at a glance and keeps the slot
fixed-width. Which REQs an amendment supersedes is carried by its ledger event, not by
the ID, so one amendment REQ can supersede several REQs or none. Cost: the `obpi_item`
slot in `src/gzkit/triangle.py:31` and the TASK regex in `src/gzkit/tasks.py:123` accept
`A\d{2}` alongside `\d{2}`, and every REQ parser follows.

## source · the 2026-09-25 grounding pivot already anticipates amendments

`docs/governance/ieee/design-candidates.md` § What an assignment contains and § What
acceptance claims · read 2026-09-27. Status of that file, verbatim: *"accepted design
grounding, with proposed mechanics below"*; the Magna Carta amendment of 2026-09-25
adopted its ownership relationship and *"does not implement catalog mechanics."*

> **Amendments are new contract versions.** Before execution, approval fixes the
> assignment contract and the requirement states it addresses. An approved change
> creates a distinguishable successor contract; existing acceptance records keep
> their original subject.

> For migration, existing `REQ-X.Y.Z-NN-MM` identities can remain local acceptance
> identities and assignment aliases.

> The [attested-REQ retirement rule](../attested-req-subject-retirement.md)
> already distinguishes repairable proof surfaces from literal obligations that
> a later ruling retires. The latter require an operator decision. The pivot
> needs an explicit supersession/applicability relation for them; it does not
> authorize rewriting sealed ADRs or deleting their evidence.

> **Conflict rule:** a catalog edit cannot silently override an applicable ADR
> constraint. Record the approving decision, the superseded statement, and its
> effective applicability.

The same section names a pilot case, `REQ-0.19.0-01-04`, which *"literally requires the
version bump to derive from ADR semver"*: the ADR-to-release coupling the challenge calls
*"a bad design"*.

This run's design is the *"explicit supersession/applicability relation"* the pivot says
it needs, built for legacy REQ identities before the catalog exists. It has to be designed
so it maps onto the catalog later rather than becoming a second supersession model.

## decision · Q10 — build it now in legacy identifiers, shaped to map onto the catalog

Asked: (A) build now in today's ID scheme, carrying the fields the pivot's conflict rule
names so each amendment later becomes a catalog revision with lineage; (B) wait for the
catalog; (C) build independently of the pivot. Recommended A. Operator, verbatim: *"A,
build it now and map to the catalog later"*.

So every amendment record carries the approving decision (the operator's Gate 5
attestation), the superseded statements (old REQ IDs and their verbatim text), and the
effective applicability (the release from which it holds).

## source · prior art — an amendment pool ADR already exists

`docs/design/adr/pool/ADR-pool.adr-amendment-tracking.md` · read 2026-09-27. Dated
2026-03-08, lane `lite`, `inspired_by: openspec`. Verbatim:

<!-- gz-validate-skip: command-shape -->
> Add `gz amend <adr-id>` to record mid-flight design changes. Currently, if an ADR's
> decision changes during implementation, the file is edited but there's no audit trail
> of what changed or why. This command records a `decision_amended` ledger event with
> a diff summary, preserving gate integrity while acknowledging that designs evolve.

> - ADR stays at its current gate — amendment doesn't reset progress

> 3. Gate-reset policy (no reset vs. selective reset) is decided.

> - Amendments should be rare — if they're frequent, the ADR was premature.
> - Consider: should amendments require re-verification of passed gates?

Its subject is a design change **during** implementation. This run's subject is a change
**after** attestation, to a closed ADR's attested REQs, with supersession, tests and a
patch release. The run answers its open promotion criterion 3 (gates: Q3–Q5) and its
closing question (re-verification: yes, through Steps 4a and 4b). The pool ADR had not
surfaced earlier in the run; `ghi-author` Step 0 would have found it, and the run's own
prior-art search should have.

`AGENTS.md` § Architectural Boundaries 1, verbatim: *"Do not promote post-1.0 pool ADRs
into active work."* The campaign's § 7 treats the pool as the post-1.0 release line. Any
disposition that builds this capability before 1.0 therefore needs an operator ruling of
the same kind as the 2026-09-27 DDD amendment.

## source · prior art — whole-OBPI supersession already exists

`src/gzkit/events.py:469` and `src/gzkit/cli/parser_obpi.py` (`gz obpi supersede`) · read
2026-09-27. Verbatim:

> class ObpiSupersededEvent(_EventBase):
>     """obpi_superseded event — one OBPI superseded by another (OBPI-0.31.0-02).

> event: Literal["obpi_superseded"]
>     superseded_by: str = Field(..., min_length=1)
>     rationale: str = Field(..., min_length=1)
>     attestor: str = Field(..., min_length=1)

`grep -c '"obpi_superseded"' .gzkit/ledger.jsonl` returned 0: the verb has never been used
in this repo. It supersedes a whole OBPI, one level above this run's REQ-level
supersession, and requires a human attestor. Its field shape (`superseded_by`,
`rationale`, `attestor`) is the in-repo precedent for the amendment's supersession event.

## decision · this is ADR design territory; the run moves to close

Asked Q11 (which ledger events an amendment writes: opened plus completed, completion
only, or per-REQ events). Operator, verbatim, in place of an answer: *"we clearly have
convergence on the verb being needed - this is why my ADR system is so broken, we need
this family of verbs now. we are now into ADR heavy design territory and to pretend
otherwise is asinine"*.

The agent agrees. The ADR admission question holds on all three counts: new ledger
events, a REQ grammar change and a new pipeline are hard to reverse; an attested REQ that
no longer binds is surprising without context; and each of Q1–Q10 chose between real
alternatives. The remaining questions (ledger events, the patch-release qualifier, the
defect-fix routing exception, who opens an amendment) are the ADR's to decide. None moves a
disposition, so they leave the diamond-1 frontier and travel to the ADR as open decisions,
with Q11's three options and the agent's recommendation (two events, supersession at
completion) attached.

One thing still moves a disposition. `AGENTS.md` § Architectural Boundaries 1, verbatim:
*"Do not promote post-1.0 pool ADRs into active work."* The operator's directive, verbatim:
*"we need this family of verbs now."* Promoting or superseding
`ADR-pool.adr-amendment-tracking` before 1.0 therefore needs the operator's explicit
ruling at sign-off, recorded in the Magna Carta, as was done for the DDD run.

**commissions:** disposition 1 (a heavy-lane feature ADR for the amendment verb family),
subject to that ruling.

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | commissioned | A heavy-lane feature ADR for the ADR amendment verb family: an `amend` subcommand under `gz adr` and the `gz-adr-amend` mini pipeline (Steps 4a and 4b, Gate 5 attestation, Gates 3 and 4 by what the amendment changes), the amendment record riding with its ADR (`AMD-<semver>-NN`), `REQ-<semver>-ANN-NN` in the REQ and TASK grammar, supersession by ledger event, the third patch-release qualifier, and the defect-fix routing exception. It carries the catalog-mapping fields from Q10. It supersedes or promotes `ADR-pool.adr-amendment-tracking` (the agent's recommendation is to supersede it, since its subject is mid-flight change), and it takes the open decisions above, starting with Q11. First use: `AMD-0.0.32-01`, gzkit's tooling becomes non-editable in adopter repos. Proposed only. | The operator initiates ADR work (IRON LAW). Building it before 1.0 needs the operator's ruling against § Architectural Boundaries 1 at sign-off. |
| 2 | GHI / direct fix | commissioned | (a) `docs/governance/agent-contract-rationale.md:349` claims the DDD cascade is pinned by `gz validate` scopes; it is not. (b) Apply the operator's R&D destinations ruling (Magna Carta, roadmap and backlog as row-4 destinations) to `.gzkit/skills/gz-rnd/SKILL.md` and `docs/governance/rnd-discipline.md`, and correct `rnd-discipline.md`'s false *"no glossary surface"* premise. (c) A work-order GHI for the ADR-0.0.32 amendment, so the adopter-edit reversal is tracked until the verb exists to discharge it. | Each files through `ghi-author` on the operator's go for this row. Go given 2026-09-28 (verbatim: *"deal with this"*). (a) and (b) landed as direct fixes to `agent-contract-rationale.md`, `rnd-discipline.md` and `gz-rnd` 0.4.0; (a) found the import-direction invariant is pooled too. (c) is GHI #1148, open and blocked on ADR-0.40.0. |
| 3 | chore | not pursued | none | Nothing here recurs on a schedule. Revisit if amendments turn out frequent enough to need a periodic sweep; the pool ADR's own note warns that frequent amendments mean premature ADRs. |
| 4 | control surface, rule, doc, skill, hook | commissioned | (a) A Magna Carta amendment placing the amendment ADR, carrying the operator's pre-1.0 ruling in their words. (b) Done this run: the 2026-09-27 Magna Carta amendment making the DDD-discipline R&D run pre-1.0. (c) The glossary term "amendment", after the DDD run names the glossary's home. | (a) written 2026-09-27 as the Magna Carta amendment "(2)", from the operator's sign-off and sequencing words; (b) was directed and done in-session; (c) waits on the DDD run. |
| 5 | one-shot refactoring | commissioned | Once the superseded state exists, move the eight REQs superseded in prose only (`REQ-0.0.41-02-07`, `REQ-0.0.59-03-03`, `REQ-0.0.63-03-01` to `-03-04`, `REQ-0.0.63-06-01`, `-06-02`; GHI #611 comment of 2026-07-28) onto it. | Proposed as a program; the operator selects its route. It cannot start before disposition 1 lands. |
| 6 | no action | not pursued | Using #611's `gz ledger correct` as the amendment vehicle; parallel agents that write to the repo. | #611 corrects errors, and marking an attested REQ `void` would falsify a correct attestation (#611 stays open on its own clause). Parallel writers were never proposed; parallel research subagents are already ruled by `AGENTS.md` § Behavior Rules. |

## Close

**Challenge restated.** gzkit has no way to revise an attested design short of writing a
new ADR, and so its ADRs cannot evolve without either silent drift or a full re-do. This
run defined the missing capability: an ADR amendment verb family. An amendment rides with
its original ADR, adds new REQs without changing the old ones, retires the old ones by an
attested ledger event, is verified by an adversary sized to the change, ships as a patch
release, and is shaped to become a requirement revision in the catalog the 2026-09-25 pivot
adopted. Building it is heavy ADR work, and the operator wants it now.

**Frontier.** Empty for diamond 1, apart from one ruling that moves disposition 1: whether
the amendment ADR is built before 1.0, against `AGENTS.md` § Architectural Boundaries 1.
Q11 and the other design questions travel to the ADR.

**Sign-off.** Operator g0, 2026-09-27, verbatim: *"fund it, pre-1.0, we need it now. I
have no idea what to do with it - we are stuck (and this has plagued me the entire gzkit
run) keeping in sequence."* — **fund**.

The pre-1.0 ruling answers `AGENTS.md` § Architectural Boundaries 1 for this ADR.

**Sequencing, ruled after sign-off.** The agent laid out the cause (a feature ADR's number
is its identity, its release version and its queue position, so new urgent work always
lands last) and three options: (A) author as the next number and complete in order;
(B) a named exception to completion order; (C) an R&D run on decoupling queue order from
the number. Recommended B plus C. Operator, verbatim: *"no, we have campaign plans to fix
this, so until it is fixed, I don't want to break how gzkit currently works. this makes it
clear ot me that we need to get going on adr work in the campaign. get these all made, then
go back to other refactoring"*.

So: no exception. The amendment ADR takes the next feature number in ascending order and
is authored and completed in turn, with this record as its design input (as
`config-surface-design-2026-09-20.md` was for `ADR-0.39.0`). Option C is not pursued here:
the operator states the campaign already carries the plan for the coupling. Disposition
4(a) proceeds on that basis.

**Combined with the pool ADR, and authored in turn.** Operator, verbatim: *"did you combine
that pool amendment with the 0.40.0 amendment? we should. write/book 0.40.0. questions?"*
Asked three questions; answered:

- Authoring 0.40.0 ahead of the unauthored `ADR-0.38.0`, which the 2026-09-20 amendment
  says needs its own exception: **"Wait for 0.38.0"**. 0.40.0 is not authored now.
- How to combine: *"we combine both uses of the verb - today's design and the pool's
  design."*
- Whether 0.40.0 also covers the pool ADR's mid-flight case: **"Both cases
  (Recommended)"**.

So the amendment ADR is `ADR-0.40.0` as the queue stands, and one verb family covers both
mid-flight design changes (`ADR-pool.adr-amendment-tracking`'s subject) and amendments to
attested designs (this run's subject). Whether it is booked by promoting the pool ADR
(`gz adr promote`, which GHI #1131 says never books `adr_created`) or authored fresh is
decided when it is authored.

## What this record does not license

No ADR, OBPI, chore or GHI has been started by this run. `REQ-0.0.32-05-03` is unchanged
and adopter edits remain protected until an amendment is built and ruled. Rows 1, 2, 4(a)
and 5 each wait for the operator's go on that row; sign-off alone executes none of them.
