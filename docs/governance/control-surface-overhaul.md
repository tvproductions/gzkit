# The control-surface overhaul — program record

> **Status:** program record, opened 2026-09-19. A dated record with live pointers: it
> states what the overhaul is, what has landed, what is owed and who owns each part.
> It is not canon and it grants nothing; see § What this record does not license.
> Work order: GHI #921. Chore: `instructions-files-diet`.
>
> **Read this first.** A session that picks up any part of this work reads, in order:
> this record, the chore it is about to run (`uv run gz chores show <slug>`), then the
> newest handoff. The record exists because the effort was otherwise held only in a
> chain of handoffs, and a session that read only the newest one mistook a slice for
> the whole (2026-09-19).

## Evidence standard

A value written here is illustrative, never authoritative (`AGENTS.md` § Governance
doctrine surfaces). Every figure below carries its date and the command that produced it
in § Reproduction record. Re-run the command; do not cite the figure.

## The target

Every surface an agent consumes is either rendered from the corpus or reviewed by a
chore. Nothing an agent reads per turn or on edit is hand-carried.

**Authority.** [`agent-control-surface-rendering-substrate.md`](agent-control-surface-rendering-substrate.md)
§ Binding claim — corpus construction applies to the agents/claude and rules surfaces;
skills are canonical files under `.gzkit/skills/`, synchronized to their copies, and are
not corpus constructed; vendor mirrors are derived outputs, never authoring locations.

**Operator rulings that set the target, verbatim.**

- 2026-09-09: "skills are not corpus constructed. only agents/claude and rules."
- 2026-09-17: "every section should be corpus sourced and rendered from corpus" and
  "nothing should be hand carried".
- 2026-09-17: "claude.md should be a pointer/include of AGENTS.md" and "I think the same
  audit needs to be applied to other control surfaces that are rendered".
- 2026-09-19: "all agents.md and rules must eventually be cms rendered. skills should be
  reviewed as a part of a chore (new or existing), where parsimony and new model
  alignment are part of the review."
- 2026-09-19, on skill review: "its both an authoring AND chore scope".

**Working mode** (operator, 2026-09-17, and every session since): the agent proposes a
full before and after per surface, the operator rules, the agent lands only what was
ruled. `src/**` moves only under a GHI the operator names. Tests that pin surface wording
are re-derived from the ruled canon, not restored.

## The surfaces

| Surface | Authoring model (target) | Authored today | Owner of what remains |
|---|---|---|---|
| Root `AGENTS.md` | corpus-rendered | **corpus-rendered**: `.gzkit/corpus/AGENTS.md.jsonl` → `.gzkit/renditions/AGENTS.md/root.md` → playback | under the 20,000 ceiling, above the 15,000 ideal (2026-09-19): OBPI-0.35.0-10 for the pinned rows, the operator for § Operator Doctrine and § Gate Covenant wording. GHI #1018 stays open |
| `CLAUDE.md` | pointer to `AGENTS.md` plus Claude-only addenda | rendered from `.gzkit/templates/claude.md`; a pointer plus three addenda | none known |
| Rules, `.gzkit/rules/*.md` | corpus-rendered | **hand-edited canonical files**, copied to mirrors by `gz agent sync control-surfaces` | **OBPI-0.35.0-12 rules-corpus-onboarding** (ADR-0.35.0 Feature Checklist; GHI #921's subject) |
| Nested `AGENTS.md` (Codex subtree delivery) | rendered from the rules corpus | generated from the uncorpused rule text | OBPI-0.35.0-12, same item |
| Skills, `.gzkit/skills/*/SKILL.md` | canonical files, reviewed by chore | canonical files; reviewed ad hoc under `instructions-files-diet` on 2026-09-18 and 2026-09-19 | § Skill review below |
| Hooks, `.claude/hooks/*` | generated from `src/gzkit/hooks/scripts/` | generated | direct GHI repair as defects surface |
| Templates, personas | canonical files | canonical files | not audited in this overhaul |
| Vendor mirrors | derived, never authored | derived | `gz validate --distribution`, `--surfaces` |

ADR-0.35.0 is TOPMOST in the active campaign and `Draft`. Only the operator initiates its
OBPIs. Until OBPI-0.35.0-05 (corpus→candidate generator), -07 (the land orchestrator) and -12
land, a rule edit is a hand edit by construction: the diet keeps rule text honest and small,
and cannot bring it under the CMS. Read the ADR's state from
`uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing`, never from this page.

## What has landed

Each row names its proof. Commits are on `main`.

| Stage | What | Proof |
|---|---|---|
| Review packet, 2026-09-12 | Context audit of every delivered surface | `docs/governance/context-audit-2026-09-12/` |
| Root `AGENTS.md`, 2026-09-17 | 22 parts, each operator-ruled; rewritten and landed through the corpus; generated compose byte-identical to the rendition | `8ecb176f0`; `.gzkit/chores/instructions-files-diet/proofs/CHORE-LOG.md`; `corpus-operations-2026-09-17.json` |
| `CLAUDE.md` and `governance-core.md`, 2026-09-18 | `CLAUDE.md` a pointer plus three addenda; `governance-core.md` folded into root and deleted | handoff `20260918T091028Z` |
| Six large rules, 2026-09-18 | `tests`, `token-block-discipline`, `task-discovery` (scope narrowed), `agents-md-map-doctrine`, `cli`, `skill-surface-sync`; narrative lifted to rationale docs and `rule-version-history.md` | same handoff; `docs/governance/rule-version-history.md` |
| Skill catalog, first cut, 2026-09-18 | nine router skills user-invoked; six descriptions trimmed | same handoff |
| Model-card refresh, 2026-09-18 | Fable 5.1 / Mythos 5.1 card consumed; Opus-first profile precedence | GHI #934 closed, `5adb751ee`; `docs/governance/opus-tuning.md` |
| Delivery defects, 2026-09-18 | Claude double delivery of nested files removed (#1021); adopter template gate rows (#1022); `src` citations of the deleted rule (#1024); serial unittest retired everywhere (#856) | handoff `20260918T112540Z` |
| Per-turn load proof, 2026-09-18 | Claude per-turn load measured before and after | `proofs/baseline-2026-09-17.txt`, `proofs/post-trim-2026-09-18.txt` |
| Skills and small rules, pass two, 2026-09-19 | 22 skills read end to end (21 changed); 50 skills and the rules swept mechanically for known defect classes and dead paths (8 skills, 4 rules changed). **A correctness pass, not a size pass**: contradictions, stale pointers, retired commands, steps that initiated OBPI work | handoffs `20260919T073719Z`, `20260919T085029Z`, `20260919T100023Z` |
| Program record, range and skill standard, 2026-09-19 | this record; root `AGENTS.md` destination stated as a range; rule `skill-authoring.md` 0.1.0 (scorecard rows 94–97); `instructions-files-diet` 3.4.0 widened to skill bodies, `skill-authoring-quality` 2.2.0 governed by the rule, `frontier-model-card-currency` 1.4.0 reaching skill wording | `945db8431`, `626bd1e97`, `d279d7ebf`, `a8c1ed428` |
| Load re-measured, 2026-09-19 | per-turn flat since 2026-09-18; on-edit split by consumer now that Claude no longer imports nested files | `.gzkit/chores/instructions-files-diet/proofs/load-2026-09-19.txt` |
| `src` remainders of pass two, 2026-09-19 | runtime citations of retired rule numbers (#1035); attestor fill-in tokens (#1031); chat-silence hook trigger (#1033) | `4b576497d`, `e4f9e4dc5`, `c1201c766` |

## What is owed

Ordered by what the target implies, not by ease.

1. **Rules and nested `AGENTS.md` into the corpus.** Owner: OBPI-0.35.0-12, behind
   OBPI-0.35.0-05 and -07. Operator-initiated. This is the item that discharges GHI #921.
2. **Root `AGENTS.md` — under the ceiling, above the ideal.** Operator rulings
   2026-09-19, verbatim: "make target 20k", then "state a range: 15K is ideal, 20K a
   ceiling". The range lives in `agents-md-doctrine.md` § Budget targets and its history
   in `instructions-files-budget-history.md`; the enforced budget in
   `data/instructions_files_budget.json` is unchanged and advisory until 1.0. Owed: hold
   the ceiling as canon is added (headroom is small, so an addition needs a removal), and
   work toward the ideal through OBPI-0.35.0-10 (the rows `bullet-retention` pins) and
   the operator's wording of § Operator Doctrine and § Gate Covenant. Nothing mechanical
   reads the range yet; the budget file carries one number per file.
3. **The skill-body size pass that pass two did not do.** The 2026-09-18 plan was to lift
   dated incident narrative out of skill bodies to rationale docs, as the rule pass did,
   starting with `gz-obpi-pipeline`. Pass two found contradictions instead and fixed
   those; the lift is still owed. A 17-passage trim of the pipeline skill is parked
   (`proofs/pipeline-skill-trim-proposal-2026-09-18.md`) and must be rebuilt from the
   current skill version, after the next operator-initiated OBPI is measured against
   GHI #1028.
4. **Skill review, as authoring standard and as chores** — § Skill review below.
5. **Measurements — produced 2026-09-19.** Loads re-measured
   (`proofs/load-2026-09-19.txt`); `uv run gz chores run instructions-files-diet` logged
   PASS after pass two. One cost recorded there: the new skill-authoring rule adds about
   4.5 KB to what each consumer loads on a skill edit.
6. **The five `control-surface-*` audits are stale, and running them is reading work.**
   `uv run gz chores run` on each of the five exited 1 on 2026-09-19, all on the same
   criterion: `scripts/check_proof_freshness.py` exit 3 — their audit proofs date from
   2026-09-12, before the overhaul rewrote the surfaces they audit. The verb only checks
   criteria; the chore is performed by doing its workflow (the rule-pair conflict matrix,
   the skill/rule reachability matrix, rule-vs-check parity, permission-consent drift,
   validator reachability) and writing fresh proofs. All five are propose-rung: each
   ends in recommendations for the operator, not edits. They are the standing coherence
   check on exactly these surfaces and have not been performed against the rewritten
   ones.
7. **Fifty skills swept and not read.** Mechanical sweeps cannot find an internal
   contradiction; 21 of the 22 skills read in full had at least one.
8. **Carried and unruled:** whether `patch-release.md` carries the Foundation-skip rule;
   whether `gz-adr-audit` Step 8 survives a fix to GHI #1015; whether a rule's version
   belongs in frontmatter (a `src` model change); the "attests at Gate 5" wording shared
   by `gz-complexity-distill`, its manpage and `complexity-doctrine.md`, tied to
   REQ-0.0.27-04-10.

Open GHIs from this effort: read them live with
`gh issue list --state open --search "921 OR 943 OR 1019 OR 1023 OR 1028 OR 1029 OR 1030 OR 1032 OR 1034 OR 1036 OR 1037"`.

## Skill review

Skills are not corpus constructed, so review is their control. The operator's ruling puts
it in two places at once: at authoring, and in chores.

**The three concerns are three chore classes** ([`chore-class-system.md`](chore-class-system.md)
§ The five classes). Class is why a chore exists and what its staleness costs, so they are
not interchangeable and do not share one chore:

| Concern | Class | Staleness signal | Existing chore |
|---|---|---|---|
| Does the skill follow the authoring standard? | conformance | content delta | `skill-authoring-quality` — conformance · propose, `governingRule: none` |
| Has the body accumulated past usefulness (parsimony)? | curation | accumulated work | `instructions-files-diet` — curation · operator-only-repair; skills not yet in its declaration |
| Does the wording still match current model behaviour? | currency | elapsed time | `frontier-model-card-currency` — currency · operator-only-repair; skills not yet in its declared reach |

Review age is a validator, not a chore: `skills_audit.py` flags a `last_reviewed` older
than `DEFAULT_MAX_REVIEW_AGE_DAYS`. Any repair that touches a skill is
`operator-only-repair` (§ Implementation order step 5 of the class record), which is the
propose-rule-land mode above.

**Owed, in dependency order:**

*Items 1 to 3 landed 2026-09-19 (`d279d7ebf`, `a8c1ed428`), and item 4 with them by
operator ruling; the tooling gap they expose is GHI #1037. What follows is kept as the
record of what was owed and why.*

1. **An authoring standard, as a rule** loading on `.gzkit/skills/**`. It states how a
   skill is written: procedure stays and dated incident narrative goes to a rationale
   doc (parsimony); wording follows `opus-tuning.md` / `gpt-tuning.md` and cites them
   (model alignment). It settles one standing tension: `skill-authoring-quality` § Body
   Quality rewards a skill for carrying rationalization tables, anti-pattern sections and
   edge cases, which pulls against parsimony. As a rule it is itself a surface owed to the
   CMS under item 1 above. Wording is the operator's to rule.
2. **`skill-authoring-quality`** keeps its class and rung and names that rule as its
   `governingRule`. A conformance chore with no declared standard has nothing to conform to.
3. **`instructions-files-diet` is widened to declare skill bodies in scope** (operator
   ruling 2026-09-19, by selection: "Widen instructions-files-diet (Recommended)"). Its
   `governingRule`, `remediation.details` and `nonAuthority` are amended to say so. No new
   chore is admitted.
4. **`frontier-model-card-currency`** brings model-tuned skill wording into its declared
   reach, so a card rotation puts that wording up for re-sourcing.

**Tooling does not yet serve the standard (GHI #1037).** `gz skill new` scaffolds
"1. Step 1 / 2. Step 2 / 3. Step 3", the stub the conformance chore fails, and
`gz skill audit`, the only skill check inside `gz check`, reads no body. Until that is
repaired the standard is held only by the chores, which run when the operator draws them.

Thirteen skill bodies exceed the existing chore's own "Oversized — must decompose"
threshold; `gz-obpi-pipeline` is the largest by a wide margin and loads in full on every
OBPI run.

## What this record does not license

- **It does not authorize any OBPI.** Items 1 and 2 of § What is owed are OBPI work; only
  the operator initiates it, through `gz-obpi-pipeline`.
- **It does not admit a chore.** Admission is operator-directed on recurrence evidence.
- **It does not amend a chore declaration, a rule or a skill.** § Skill review states what
  is owed; each amendment is its own full before and after, ruled before it lands.
- **It does not close GHI #921.** Wording fixes do not corpus the rules.
- **It does not replace the handoff chain or the chore log.** Those hold the verbatim
  rulings; this record points at them.

## Reproduction record

Measured 2026-09-19 at `0ecb51242`. Re-run; never cite.

```bash
wc -c AGENTS.md CLAUDE.md                                  # 19872, 2014
ls .gzkit/rules/*.md | wc -l; cat .gzkit/rules/*.md | wc -c     # 25 files, 144436 B
ls .gzkit/skills/*/SKILL.md | wc -l; cat .gzkit/skills/*/SKILL.md | wc -c   # 71 skills, 673350 B
wc -l .gzkit/skills/*/SKILL.md | awk '$2!="total" && $1>300' | wc -l     # 13 over 300 lines
git ls-files | grep -c '/AGENTS.md$'                        # 26 nested
ls .gzkit/corpus/ .gzkit/renditions/                        # one corpus, one rendition: AGENTS.md
uv run gz validate --instructions-files-budget              # exit 0; budgets advisory until 1.0
uv run gz chores status                                     # staleness board; announces, never gates
```

Per-turn Claude load, 2026-09-18: 77,176 B before, 35,190 B after
(`.gzkit/chores/instructions-files-diet/proofs/post-trim-2026-09-18.txt`). Skills on
2026-09-18 before pass two: 690,894 B (handoff `20260918T112540Z`).

## Related

- GHI #921 — the work order. `agents-md-doctrine.md` § Budget targets — the destination.
- ADR-0.35.0-canon-entry-corpus-landing — OBPI-05, -07, -10, -12.
- [`agent-control-surface-rendering-substrate.md`](agent-control-surface-rendering-substrate.md),
  [`agent-control-surface-fidelity-doctrine.md`](agent-control-surface-fidelity-doctrine.md),
  [`chore-class-system.md`](chore-class-system.md),
  [`instructions-files-budget-history.md`](instructions-files-budget-history.md),
  [`rule-version-history.md`](rule-version-history.md).
- `.gzkit/rules/agents-md-map-doctrine.md`, `.gzkit/rules/skill-surface-sync.md`.
