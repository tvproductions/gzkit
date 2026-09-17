---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-17T01:56:45Z'
agent: claude-code
session_id: 66adf070-d656-4f3b-ba51-2c6e94e13ef3
continues_from: 20260915T103613Z-rnd-design-discussion-resume.md
---

## Current State Summary

Continues `20260915T103613Z-rnd-design-discussion-resume.md`, whose ruling was booked `proceed` (operator verbatim: "resume h/o"). Three threads ran: the R&D design discussion, which reached a substantially settled frame; two ADR-lifecycle defects found and filed; and Gemini vendor support removed at operator direction.

**The R&D design, as settled.** An R&D run IS diamond 1 of the Design Council double diamond (Discover + Define). It ends with the problem defined and a plan naming which fan-out artifacts are warranted, closed by operator sign-off — kill or fund. Diamond 2 is producing those artifacts, downstream, by machinery that already carries its own gates. MPAS supplies the mechanics that run inside each diamond; the Design Council supplies the shape and the gate apparatus; gzkit supplies the six-way fan, which neither source has because neither begins destination-unknown.

**Two ADR-lifecycle defects, GHI #1014 and #1015.** Together they mean no ADR has ever legally entered `Accepted` or `Validated` at Layer 2. `Accepted` is unreachable because `closeout.py:509` hardcodes `from_state="Proposed"` and appends straight to the ledger, bypassing `LifecycleStateMachine.transition()` so validation never runs — 62 of 62 recorded ADR transitions are `Proposed -> Completed`, a pair absent from `ADR_TRANSITIONS`. `Validated` is unreachable because `audit_cmd` writes the `validated` receipt and then guards the transition on `derive_adr_semantics`, which reads that receipt first, so the guard observes its own write and always skips. Every `Validated` shown by `gz adr status` is a Layer-3 derivation from a receipt.

**Gemini removed.** Four hand-authored `GEMINI.md` files and the Gemini pool ADR deleted; one coupled false claim in the lodestar corrected. The runtime half is NOT done and needs an operator routing call.

At authoring: HEAD `95d8e243d`, level with `origin/main` (0/0), no OBPI locks, working tree dirty with the Gemini removal and the lodestar fix.

## Important Context

### THREAD: the R&D design discussion

Records: `docs/governance/mpas-appropriation-analysis.md` (§ Questions for the design session), `docs/governance/rnd-discipline.md` and `.gzkit/skills/gz-rnd/SKILL.md` — both **still provisional**; the discipline file's own "Status: RULED 2026-09-15" header predates this session and several of its six recommendations are now superseded.

**The settled frame, in one place:**

- An R&D run is diamond 1. Artifact production is diamond 2 and lives outside the run. The Design Council's own text carries this: Define "ends with a clear definition of the problem(s) and a plan for how to address this… ends in a project go-ahead through corporate level sign-off."
- Both diamonds carry MPAS invariant 4's pair of stopping conditions. Diamond 1 mechanical: frontier empty AND the challenge deliberately restated AND every one of the six dispositions carries a decision. Diamond 1 human: sign-off, kill or commit. Diamond 2 human: the operator agrees convergence is reached — the IRON LAW gates artifact production and cannot stand in for a stopping condition, because they answer different questions.
- The run's durable product is one **R&D record** per run at `docs/rnd/<slug>.md`, written throughout and finished at the end, never composed at the end. MPAS is explicit: an entry lands "at the moment it is resolved, in the middle of the conversation, rather than producing a tidy glossary at the end."
- The record accretes **two entry kinds**: `source` (a primary source, cited not summarized) and `decision` (crystallized in session), where a decision optionally carries `commissions:` naming the fan-out disposition it warrants. The plan is the view over decisions with `commissions` set; the six-row disposition map renders from it; the sign-off one-pager is derivable rather than authored. A plan item is deliberately NOT its own kind — that shape would let work be commissioned with no recorded reasoning.
- `term` and `insight` get no entry kinds. They write to `GLOSSARY.md` and `gz insights remember` at the moment they resolve, carrying the run id as provenance. The destination points back at the run; the record never holds a copy.
- Ledger: `opened` / `sign-off` / `run closed`, with a run killed at sign-off ending at two events.
- Three documents must not collapse into each other: an **R&D run** (the activity), an **R&D record** (its per-run document), and the **R&D discipline record** (`docs/governance/rnd-discipline.md`, the one doctrine document governing all runs).

**Naming collisions found and fenced.** `brief` (OBPI), `gate` (the five-gate covenant; Gate 5 is OBPI/ADR completion attestation and nothing else), `freeze` (LEGO and Virgin use it for lock-down, Alessi for set-aside — the source collides with itself), `work order` (a GHI is the work order and the receipt), `CONTEXT.md` (`gz context <ADR-ID>` is a registered verb, which is why the glossary is `GLOSSARY.md`). Three agent coinages were caught by the operator mid-session and retired: **fan** (smuggled one-of-five when the operator's own note says any-or-all), **pinch** (smuggled one-way when re-entry is native), and a section-template shape for the record (smuggled compose-at-the-end). Each was a wrong model travelling under a new word. MPAS's own implementer advice covers it: prefer pretrained metaphors to coined terms.

### Primary sources read this session

- `https://www.aihero.dev/skills-grilling` and `https://www.aihero.dev/skills-grill-me` — the interrogation mechanic. `grill-me` is stateless and emits nothing; `grill-with-docs` is the in-repo door, "strictly the better one", and is the actual analogue for gzkit because it emits inline as decisions land.
- `https://www.aihero.dev/skills-domain-modeling` — the CONTEXT.md entry mechanic and its `_Avoid_` convention naming rejected synonyms, which is directly useful given the collision list above.
- `https://www.designcouncil.org.uk/resources/the-double-diamond/` — the four phases and the statement that findings "can send them back to the beginning of their diamond work", so re-entry is native.
- Design Council, *Eleven Lessons: managing design in eleven global brands* (2007), **all 144 pages**, local copy at `/Users/jeff/Documents/AI/ElevenLessons_Design_Council_20_282_29.pdf`. Virgin Atlantic has an explicit R&D stage where "ideas are deliberately kept as fluid as possible". Three of eleven converged independently on a fixed template, for comparability: "Before, we had some people presenting 6 pages, some presenting 86 pages… Now everyone presents in equal terms… so we can compare apples with apples." Four of eleven dissent from formal process at all: "the magic is never in the process". Alessi archives set-aside projects and revisits them "if trends change"; Yahoo retains out-of-scope findings "for future use".

**A caution about secondary Double Diamond material.** The personas / empathy-map / affinity-map / Crazy-8s artifact vocabulary that circulates around the framework appears NOWHERE in the primary source; it comes from downstream UX vendor pages. Importing it into a governance repo would be furniture.

### Method failure to carry forward

Twice this session an agent reported a rendered table column and then a source code path as verified governance state, and the second instance occurred **inside a correction of the first**. The operator, verbatim: "Do you not have any primedirected element that insists that you consule evidence and validate before you say stupid shit like that? I think gzkit is too big and complex for you to successfully navigate or remain contextually oriented in for any length of time." Spelling preserved. The rule exists — AGENTS.md § DO IT RIGHT #4, "Verify observed behavior, not assumed behavior. Run the command, paste actual output." Both failures had the authoritative ledger query one command away. Any claim about governance state goes through the ledger before it is spoken, and an unverified gap is named as unverified rather than filled with a plausible reading.

## Decisions Made

- [operator-ruled] Resume the prior handoff (verbatim: "resume h/o"); booked `proceed`.
- [operator-ruled] Put design questions one at a time, not batched (verbatim: "ask me the questions one at a time").
- [operator-ruled] `gz-rnd` is operator-invoked and the sensing arm is out (verbatim: "it is operator-invoked, I think the sensing is a mistake because you'd need to deduce that an exploratory session is meant to be R&D and I am not sure you'd do that realiably"). Spelling preserved.
- [operator-ruled] An offer is nonetheless permitted, on four signals — a paste of external material with no task attached; framing verbs; no named artifact target; subject is gzkit's purpose or shape (verbatim: "these are compelling, I think an offer isn't too harmful either").
- [operator-ruled] `disable-model-invocation: true` stays; the offer is seated in AGENTS.md or `.claude/rules/`, not in the skill; and a skill is wanted (verbatim: "leaving this is good: disable-model-invocation: true  so, yes, agents.md or rules might be the best way. we want a skill to be sure as we were meant to appropriate MPAS.").
- [operator-ruled] The running map is the six-row disposition table maintained live, consistent with `grill-with-docs` feeding CONTEXT.md as concepts emerge (verbatim: "yes, so that is consistent with grill-me-with-docs").
- [operator-ruled] MPAS has no way to do R&D (verbatim: "however, it don't think MPAS has a way to do R&D"). Every MPAS entry point is destination-typed before it starts; R&D is destination-unknown by construction.
- [operator-ruled] The shaping set is `research`, `grilling`, `domain-modeling`, `prototype`, with `codebase-design` as a pattern rather than a skill (verbatim: "yes, that's the set"). Later narrowed — see the DDD ruling below.
- [operator-ruled] All four shaping disciplines hold promise; the run's durable product is an MD in a `docs/rnd/` area; the operator moves to product when ready for one or more fan-outs (verbatim: "I think some combination of all four holds great promise - we can make the final product an MD in the end. maybe an area of docs that is rnd. I will likely move towards product when I am ready for one or more of the fanouts").
- [operator-ruled] Diamond 1's mechanical stopping condition is BOTH frontier-empty and the challenge restated, with "restated" satisfied by a deliberate restatement rather than a changed one (verbatim: "both").
- [operator-ruled] Diamond 2's stopping conditions accepted: mechanical = every row carries a disposition; human = the operator confirms (verbatim: "ok").
- [operator-ruled] An R&D run emits ledger events (verbatim: "yes to ledger").
- [operator-ruled] A run concluding at sign-off with nothing warranted closes there — two events, not three (verbatim: "yes, closes at sign-off").
- [operator-ruled] Read the whole Eleven Lessons PDF rather than stopping at the process chapters (verbatim: "read it").
- [operator-ruled] The MPAS / Double Diamond reconciliation net is agreed: Design Council frame, MPAS mechanics, Design Council gate apparatus, MPAS agent invariants, gzkit's six-way fan (verbatim: "ok, i agree with you net").
- [operator-ruled] `GLOSSARY.md` at repo root, following MPAS's CONTEXT.md in function; the name differs because `gz context <ADR-ID>` already holds the word (verbatim: "yes ==> GLOSSARY.md at repo root").
- [operator-ruled] `docs/examples/glossary.md` does not belong in gzkit (verbatim: "this does not belomg in gzkit: docs/examples/glossary.md"). Spelling preserved. Scoped this session to 16 files under `docs/examples/` carrying CIDM 6330/6395 course markers.
- [operator-ruled] Gemini is no longer supported; remove its surfaces (verbatim: "i no longer support gemini, get rid of them", preceded by "p.s., get rid of this: GEMINI.md").
- [operator-ruled] MPAS is appropriated JUST for R&D (verbatim: "also, we are appropriating mpas JUST for r&d").
- [operator-ruled] DDD is foundational to gzkit alongside TDD and BDD; it is not an MPAS import (verbatim: "no, other routines use DDD in gzkit, DDD is foundational to gzkit, as are TDD, and BDD").
- [operator-ruled] The appropriated-for-R&D set is three — `research`, `grilling`, `prototype` — and `GLOSSARY.md` is a foundational DDD surface, project-wide, fed by all work, with R&D one contributor among several. MPAS's `domain-modeling` technique remains appropriable for R&D runs without being a fourth R&D-scoped skill.
- [operator-ruled] If we start work on an ADR, it is accepted (verbatim: "also, if we start work on an ADR, it is accepted"). `Accepted` carries real meaning and the ledger cannot currently answer which ADRs are in it.
- [operator-ruled] Both ADR-lifecycle findings are GHIs (verbatim: "yes, these are absolutely ghis").
- [operator-ruled] Diamond 2's close is confirmed by the operator agreeing convergence has been reached, as MPAS works — not by the IRON LAW standing in for a stopping condition (verbatim: "we would agree that we've hit convergence, this is how mpas works").
- [operator-ruled] Diamond 1 ends in the design decisions and the plan; diamond 2 produces the fan-out products (verbatim: "yes, confirmed"). This supersedes the intermediate framing in which diamond 2 held the decisions.
- [operator-ruled] The record's entry model is option (a) — two kinds, `source` and `decision`, with `commissions:` as a field on a decision rather than a separate plan-item kind (verbatim: "a is fine").
- [agent-chose] Deleted all four `GEMINI.md` files as one class rather than the root one alone, and captured the three nested files' distinctive constraints as an insight so the guidance is not silently lost.
- [agent-chose] Reverted the hand-edit removing `vendors.gemini` from `.gzkit/manifest.json` on discovering the manifest is a generated surface, rather than proceeding into the `config.py` + schema change that carries adopter blast radius under `extra="forbid"`.
- [agent-chose] Left `"gemini"` in `_CROSS_VENDOR_ADVERSARY_PREFIXES` (`src/gzkit/commands/obpi_complete_adversarial.py`): that list answers whether a model can serve as a Step-4b cross-vendor adversary, not whether gzkit renders a surface for it.
- [agent-chose] Filed #1014 and #1015 as two GHIs rather than one, and posted the sibling cross-link on #867 at authoring time per `ghi-author` Step 0.

## Immediate Next Steps

1. **Rule the two pending routes.** (a) Removing `gemini` from `src/gzkit/config.py` and `src/gzkit/schemas/manifest.json` is a breaking runtime contract change — `VendorsConfig` carries `extra="forbid"`, so an adopter manifest holding `vendors.gemini` fails to parse. Under the IRON LAW the agent does not initiate OBPI work, so the route is the operator's. (b) GHI #1014 and #1015 are direct-fix shaped; #1014 should land first because #1015's fix is cleaner once transitions are actually validated.
2. **Decide whether to commit the working tree as-is.** It holds the four `GEMINI.md` deletions, the Gemini pool ADR deletion, the lodestar `Rendered outputs` correction, and two insight records. The operator has not asked for a commit; nothing has been committed this session.
3. **File the queued `docs/examples` GHI** — 16 files under `docs/examples/` carry CIDM 6330/6395 course markers, including the whole `presentations/` series and `glossary.md`, which is published at `mkdocs.yml:61`. Captured as a defect insight; the GHI was deferred to the end of the discussion and the discussion did not end.
4. **Resume the R&D discussion at its remaining frontier**, one question at a time as ruled: the `retained` third disposition (recommended: do not add it; two states with the reason field carrying a revisit condition, and let the first run produce evidence if a third is needed); `docs/rnd/` nav — published in the site or excluded like `docs/proposals/`; and the campaign amendment draft for the R&D entry under § Workflow fronts.
5. **When the discussion concludes, rewrite `docs/governance/rnd-discipline.md` end to end** from the settled frame and revise or delete `.gzkit/skills/gz-rnd/SKILL.md` to match. Both are provisional; the file's own "Status: RULED 2026-09-15" header predates this session and several of its six recommendations are now superseded. Then `uv run gz agent sync control-surfaces` and `uv run gz check`.

## Pending Work / Open Loops

- **GHI #1014** (`closeout: from_state is hardcoded and bypasses transition validation`) and **GHI #1015** (`audit: Completed -> Validated unreachable; guard reads its own write`) — both open, both `defect` + `runtime`, both capture-only this session per `ghi-author`'s invocation boundary. Neither implemented.
- **Gemini runtime removal unrouted** — `src/gzkit/config.py:55` and `src/gzkit/schemas/manifest.json` `/properties/vendors/properties/gemini`. `.gzkit/manifest.json` is a generated surface; hand-editing it fails `gz validate --surfaces`, so the real removal is upstream in the Pydantic model and the schema.
- **`docs/examples` course content** — 16 files, GHI not yet filed, captured as a defect insight.
- **Status table reporting** — `src/gzkit/commands/status_render.py:365` renders `closeout_label = "READY" if result.get("closeout_ready") else "BLOCKED"` with no terminal-state awareness, so a finished ADR still displays `Closeout: READY`, which reads as pending and did mislead a reader this session. Not filed; the operator was asked whether it is a defect and the thread moved on.
- **`REQ-0.19.0-07-01`** is checked `[x]` on a terminal brief under a terminal ADR and asserts a `Completed -> Validated` ledger event that has never been written. That is the attested-REQ-subject-retirement shape; repairing it is a separate call from fixing the code.
- **R&D open questions** — the `retained` third disposition; `docs/rnd/` nav; the campaign amendment draft; and the held beat-versus-boundary question (does diamond 1's sign-off sit inside one session or across a session boundary), softened but not answered by re-entry being native.
- **`gz-rnd` and `rnd-discipline.md` remain provisional**, and their manpage, index, nav and router entries go with them if the skill is revised or removed.
- Carried from the predecessor and untouched this session: chore estate at 36 overdue; GHIs #997, #808, #1009, #1011, #1012, #1013; and #810, #934, #983, #894, #969, #968.

## Verification Checklist

```bash
git status -sb
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
uv run gz validate --documents --surfaces
gh issue view 1014 --json state,title
gh issue view 1015 --json state,title
find . -name "GEMINI.md" -not -path "./.git/*" | wc -l
grep -n "Rendered outputs" docs/design/lodestar/architectural-identity.md
```

Expected: level with origin (0/0); no active locks; validation exits 0; #1014 and #1015 OPEN; zero `GEMINI.md` files remain; the lodestar row reads `.claude/`, `.github/`, `.agents/` with no `GEMINI.md` or `opencode.json`.

Re-derive the two defect claims rather than trusting this document — that is the method failure this session recorded:

```bash
python3 -c "
import json, collections
c = collections.Counter()
for line in open('.gzkit/ledger.jsonl'):
    d = json.loads(line)
    if d.get('event') == 'lifecycle_transition' and d.get('content_type') == 'adr':
        c[(d.get('from_state'), d.get('to_state'))] += 1
print(c)"
```

Expected: a single pair, `('Proposed', 'Completed')`, 62 occurrences. Any `Completed -> Validated` row means #1015 has been addressed since authoring.

## Evidence / Artifacts

- `.gzkit/handoffs/20260915T103613Z-rnd-design-discussion-resume.md` — predecessor.
- `docs/governance/mpas-appropriation-analysis.md` — the MPAS record and its open design questions.
- `docs/governance/rnd-discipline.md` — provisional; to be rewritten from the settled frame.
- `.gzkit/skills/gz-rnd/SKILL.md` — provisional on the same terms.
- `src/gzkit/commands/closeout.py` — line 509, the hardcoded `from_state` (GHI #1014).
- `src/gzkit/commands/audit_cmd.py` — the circular transition guard (GHI #1015).
- `src/gzkit/core/lifecycle.py` — `ADR_TRANSITIONS`, the table the ledger contradicts.
- `src/gzkit/ledger.py` — `derive_adr_semantics`, which computes `Validated` from a receipt.
- `src/gzkit/commands/status_render.py` — the closeout/QC readiness labels with no terminal-state awareness.
- `.gzkit/ledger.jsonl` — Layer-2 record; 62 ADR transitions, all `Proposed -> Completed`.
- `.gzkit/insights/agent-insights.jsonl` — four records written this session: design-dialogue pacing, the `docs/examples` course content, the GEMINI.md removal, and the two filed GHIs.
- `docs/design/lodestar/architectural-identity.md` — `Rendered outputs` row corrected.
- `docs/governance/build-to-1.0-campaign-2026-08-16.md` — the active campaign and its § Workflow fronts.

## Settled Rulings

876 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
