<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# 01 — Engineering-method assessment

> **This is a dated record.** Every figure below was observed on the tree at
> `6a0e5241e`. The values are ILLUSTRATIVE, never authoritative (`AGENTS.md`
> § Governance doctrine surfaces). Where a figure is re-derivable, prefer
> re-running the command shown beside it over trusting the number.
>
> **Superseded in part by [piece 02](02-requirements-vs-release-2026-09-22.md).**
> Its § 9 row filing 29148 § 6.6.2.2.2's four-baseline scheme under *do not
> adopt* is withdrawn; its § 4.4 finding that requirements "have no durable
> owner" is sharpened to *the release plan owns them*; and its attribution of
> "The requirements shall be configuration controlled" to 29148 § 6.6 is
> corrected to § 6.4.3.5.
>
> **Amended 2026-09-22 (Phase 3).** § 12 was titled *PROPOSED PHASE 2
> INVESTIGATION PLAN* and its items were numbered `P2-A … P2-H`. The
> investigation's phase model assigns Phase 2 to the adversarial review **of
> this piece**, so one label denoted two incompatible things. The items are
> renumbered **`M-A … M-H`** and the section retitled *PROPOSED MEASUREMENT
> PROGRAM*; no content changed. Operator ruling, 2026-09-22.
>
> **This piece is a raw investigation record, subordinate to
> [`FINDINGS.md`](FINDINGS.md).** Read the register first; come here for
> the evidence behind a row.


**Scope:** investigation only. No code, documentation, ADR, requirement, issue, or backlog item was created or changed. Every `gz` invocation was a read-only query.

**Method.** Repository evidence was gathered directly and through eight parallel investigation tracks (four over the standards corpus at `~/Library/Mobile Documents/com~apple~CloudDocs/IEEE`, four over the repository). Every number below carries the command that produced it. Where a subagent's reading was load-bearing, I re-verified it myself against the cited file; two readings were corrected in the process and are flagged where they appear. **Observation, interpretation, standard-derived principle and recommendation are labelled separately throughout.**

**Repository state:** branch `main`, HEAD `6a0e5241e`, 2026-09-22.

---

## 1. EXECUTIVE MODEL — how GZKit's engineering system actually works

### 1.1 The declared model

GZKit declares a linear pattern: `PRD → Constitution → ADR → OBPI → REQ → TASK → Attestation`, with five numbered gates, two lanes (lite = gates 1–2, heavy = adds 3–4), and a universal Gate 5 (human attestation). State is layered: L1 canon files, L2 append-only ledger, L3 derived views, with precedence `L2 > L1 > L3` (`docs/governance/state-doctrine.md`).

### 1.2 The operating model, reconstructed from evidence

The declared model describes a minority of the system's actual behaviour.

**(a) The pipeline is real but nearly idle; the repair channel carries the work.**

Over the last 500 commits (2026-09-01 → 2026-09-22, 21 days): 223 commits (44.6%) cite a GHI; 56 (11.2%) mention an OBPI; 17 (3.4%) are `feat`. Across all 3,834 commits: `chore` 2,028 (53%), `fix` 1,163 (30.3%), `feat` 138 (3.6%). The `fix:feat` ratio by month runs 0.8 (Mar) → 8.2 → 6.9 → **23.2 (Jun)** → 18.4 → 12.7 → 12.2 (Sep).

OBPI creation is collapsing: 410 (Mar) → 170 → 212 → 78 → 41 → 16 → 10 (Sep, partial). **The ADR→OBPI pipeline is not the primary change mechanism; the GHI→direct-fix channel is, by roughly 4:1.**

**(b) The requirements model is a live, working mechanism sitting on a dead foundation.**

`uv run gz covers` (exit 0) reports **1,794 / 2,749 REQs covered (65.3%)**. `uv run gz drift` (exit 1) reports **713 unlinked specs, 0 orphan tests, 0 unjustified code**. REQ identifiers are globally unique and structurally encode parentage (`REQ-<adr-semver>-<obpi-NN>-<req-NN>`, one grammar at `src/gzkit/triangle.py:24-31`, consolidated from ~20 disagreeing regexes under GHI #615).

But the PRD those REQs nominally descend from is inert. `docs/design/prd/PRD-GZKIT-1.0.0.md` is `status: Draft`, dated 2026-01-22, and declares FR-001…FR-012, NFRs, a risk table and AC-001…AC-012. **`FR-*` identifiers appear nowhere outside the PRD. `AC-*` identifiers appear outside it only in ADR-0.1.0 and its eight OBPIs** — the very first pre-release ADR. Traceability to stated product intent was practised once, in January, and then abandoned across ADR-0.2.0 through ADR-0.39.0.

**(c) Durable system knowledge lives inside transient work artifacts, and is deleted with them.**

`gz adr demote` executes `shutil.rmtree(source_dir)` (`src/gzkit/commands/adr_demote.py:475`), deleting the ADR package including `obpis/`. Measured across git history: **378 brief files deleted, carrying 1,986 REQ acceptance criteria and 1,584 FAIL-CLOSED constraints — 39% of all REQs ever authored in this repository.** The surviving pool file retains the ADR's prose and zero REQ identifiers. The knowledge did not migrate to a model; it went to git history.

**(d) Jurisdiction is declared in prose and enforced almost nowhere.**

`## Allowed Paths` appears in 549 of 556 briefs and is parsed by five independent parsers. The only `PreToolUse Write|Edit` hook that consults one scopes *itself* to the allowlist — `.claude/hooks/pipeline-gate.py:156-158` executes `continue` when a path falls outside it, so an out-of-allowlist write escapes that hook's stage fence rather than being refused by it. (*Verified directly. Precise reading: this hook is a pipeline-**stage** fence that happens to be allowlist-scoped, not a jurisdiction fence that was inverted. The effect is the same — no hook refuses an out-of-scope write — but the mechanism is a gap, not a reversal.*) `## Denied Paths` (502 briefs) is never tested against a write anywhere.

The airlock (ADR-0.33.0) does compute a HOLD decision (`src/gzkit/airlock/enter.py:158-170`), but all six call sites print and continue, and its input is empty in practice — `gz ontology reach` returns 0 nodes for an OBPI id. `src/gzkit/commands/airlock.py:14-18` states this honestly in code.

**(e) The gates record exit codes, not observations.**

Of 943 `gate_checked` ledger events, **803 (85.2%) carry no observation of what was verified**: 506 empty, 246 the literal constant `"stdout/stderr captured"` (`gates.py:163`), 56 `"skipped: no baselines"` recorded as `pass`. Gate 2 ("Tests pass") was satisfied 115 times by `gz lint` and 111 times by `gz typecheck` — 226 of 509 Gate-2 events are not test runs. `_run_gate_5()` is `console.print(...); return True` (`gates.py:256-258`); **zero gate-5 events exist in the ledger**. And `gz gates` itself prints a deprecation notice on every invocation (`deprecations.py:41`, GHI #705) — the covenant in AGENTS.md is documented against a retiring verb.

**(f) The system knows all of this about itself, in durable artifacts, and says so without softening.**

`docs/governance/enforcement-claim-nc-audit-2026-07-18.md:50`, verbatim: *"32 of 47 claims do not prove what they assert."* — followed by *"`gz check` reports 47/47 verified."* `docs/governance/evidence-record-contract.md` concludes *"The contract auto-enforces nothing"* and labels its own effectiveness *"an UNTESTED HYPOTHESIS."* `data/mechanical_witness_grandfather.json` freezes 64 rows scored "Mechanical" that nothing witnesses. `Ledger.get_post_validation_failed_gates` exists specifically to re-surface failures that the effective view launders to pass (GHI #411; 5 ADRs, 16 such events).

**Interpretation.** This is the defining characteristic of the system. GZKit's error-detecting loop works — it finds its own facades and records them honestly in durable places. What it lacks is a mechanism to *retire* what it finds. The findings accumulate alongside the defects they describe.

**(g) Agent entry is the dominant cost.**

Mandatory reading before an agent writes a line against a median OBPI: AGENTS.md (19,979 B) + CLAUDE.md (2,014) + session-start hook (21,521) + resumed handoff (22,506) + `gz-obpi-pipeline/SKILL.md` (125,897) + median brief (12,901) + parent ADR (65,593) + `gz status` output (79,870) = **350,281 bytes ≈ 92,000 tokens**. The skill file alone is 36%; `gz status` is 23%; **the work product — the brief — is 3.7%.** Against the largest brief the total reaches ~130,000 tokens.

The handoff chain is a second entry cost. 758 handoffs, 10,517,986 bytes ≈ 2.63M tokens, growing at ~9.5/day in September. `src/gzkit/session_start.py:185` instructs the agent to read the lineage; `handoff_api.py:1181` caps that walk at 20 documents — **the "19 ancestors" figure in the session hook is a floor imposed by the depth bound, not the true chain length.** Obeying it literally costs ~54,000 tokens.

**(h) Governance prose outweighs source code 3.5:1.**

`src/gzkit`: 515 files, 156,794 lines. `tests/`: 705 files, 229,946 lines (1.47×). `docs/`: 1,782 markdown files, 326,799 lines (2.08×). `.gzkit/` markdown+JSON excluding the ledger: 1,281 files, 226,116 lines. Handoffs alone are 89,922 lines — **57% of the entire source tree**. Ledger: 14.3 MB, 17,030 rows, 67 distinct event names.

### 1.3 The model in one paragraph

GZKit is a defect-repair system with a governance pipeline attached. Work enters through GitHub issues labelled `defect` (86% of 1,075 issues), is repaired directly under a rule that authorises direct repair, and is recorded in an append-only ledger. The ADR/OBPI pipeline — the declared primary mechanism — now produces ~10 work packages a month and is reserved for operator-initiated work. Persistent engineering knowledge has no home of its own: it is distributed across six intake surfaces (212 pool ADRs, 1,075 GHIs, 806 insights, 41 chores, a 207 KB campaign plan, 758 handoffs) plus the work packages themselves, and each of those surfaces' transient layer is load-bearing. The verification stack is unusually sophisticated at the level of individual mechanisms (mutation witnesses, RED receipts, negative controls, cross-vendor adversaries) and unusually honest about its own gaps, but the gates that sit on top of those mechanisms record exit codes rather than claims.
---

## 2. ENGINEERING-OBJECT INVENTORY

Objects are listed as they *actually behave*, not as their names suggest. "P" = persistent, "T" = transient.

| Object | What it represents in practice | P/T | Source of truth | Upstream justification | Downstream evidence | Lifecycle | Overlap / conflict | Standard concept |
|---|---|---|---|---|---|---|---|---|
| **PRD** (1) | Original product intent, frozen | P (inert) | `docs/design/prd/PRD-GZKIT-1.0.0.md`, L1 | — | none — `FR-*` cited 0× outside it | `status: Draft` since 2026-01-22; 1 `prd_created` event | Superseded in practice by the campaign plan | 29148 stakeholder/system requirements spec; 15289 §10.60 |
| **Constitution** | Declared but unpopulated | — | `docs/design/constitutions/` — **empty directory** | — | — | `gz constitute` exists; nothing authored | — | — |
| **ADR** (372 files; 285 graph nodes) | Decision record **+** mini-requirements spec **+** work plan **+** evaluation record **+** interview transcript **+** attestation block | P | L1 file + L2 lifecycle events | `parent:` frontmatter — 212 name the PRD, **64 name nothing**, 7 name an ADR, 2 a GHI | OBPIs, `adr_eval_completed`, receipts | pending → validated → completed. **80 Validated, 4 Pending, 3 Completed** — the terminal state is essentially unreached | Carries `## Boundary Invariants` (23 ADRs) and `## Fidelity Assertions` (109) that are architecture/verification obligations, not decisions | 42010 §6.10 architecture decision + rationale — but **not** an architecture description (§4 + §6) |
| **Pool ADR** (204) | Undifferentiated intake: ~33% defects, ~20% verification obligations, ~15% feature requests, ~11% actual decisions | P (frozen) | L1 file | PRD (167) or none (26) | none | Created 2026-03…05 (81 in May), **1 in September**; 34 promotions ever, 2 in the last 4 months | Is simultaneously a backlog, a graveyard and a defect queue | 16085 §6.4.3.3 risk profile / 29148 requirement — **neither**, as used |
| **OBPI brief** (556 live; 378 deleted) | Bounded work package **and** the sole home of its requirements and constraints | T (but carries P) | L1 file | ADR item (all 901 graph OBPIs have an ADR parent) | REQs, receipts, gate events | created → (parked/withdrawn) → completed → attested. 954 created, 521 completed (54.6%), 48 withdrawn, 7 repudiated | **Deleted by `shutil.rmtree` on ADR demotion, taking 1,986 REQs and 1,584 constraints with it** | 16326 §7.7.3.2 work package — which §7.3.1.1 says must *reference* requirements, not carry them |
| **REQ** (3,105 on disk; 2,749 in `gz covers`) | Predominantly an acceptance criterion for one increment of labour | T in identity, P in obligation | Brief text; **no registry, no allocator** | The OBPI (identity is a coordinate *inside* it: `REQ-<adr>-<obpi>-<req>`) | `@covers` test (1,788 distinct), behave tag (337), ledger event | Dies with its brief | Identity derived from the work package, so it cannot outlive it | 29148 requirement — fails the identity and attribute tests (§4) |
| **FAIL-CLOSED constraint** (3,855 across 484 briefs) | NEVER/ALWAYS constraints — **mixes durable system constraints with per-OBPI scope fences in one list** | mixed | Brief prose | none | none | Only **267 of 3,855** carry any identifier; `hooks/obpi.py:344-346` checks the section is non-empty | The largest requirement-shaped population in the repo, with the least machinery | 29148 §4 design constraint; 42010 §6.9 correspondence |
| **Boundary Invariant** (23 ADRs, BI-01…BI-09) | Genuine cross-OBPI architectural constraint with a declared audit point | P in intent, T in fact | ADR §Boundary Invariants | ADR decision | STRUCTURAL-FENCE REQ proof channel | Audited **once**, at ADR closeout | **Numbered per-ADR**, so `BI-04` denotes different things in ADR-0.35.0 / 0.0.71 / 0.0.73 / 0.0.74 — yet `src/gzkit/enforcement.py:724,746`, `pipeline_runtime.py:602,641` and `fidelity.py:129,238,263` cite them from code | 42010 §6.9.3 correspondence method — the closest true match in any standard |
| **Invariant** (`.gzkit/invariants/`, **4 files**) | Claims about the *governance machinery* | P | JSON, with `structural_witness` | — | named `gz validate` flags | stable | **None of the four is about the software system's behaviour** | 15026-2 §5.3.3 claim — closest existing instance |
| **GHI** (1,075: 55 open, 1,020 closed) | The primary work-authorization channel | T | GitHub | agent or operator observation | `fix(...)  (GHI #N)` commit | median time-to-close **3.67 h**; 365 closed inside 1 h | **928 labelled `defect`** because that label is the only route to direct repair; only ~16% of open issues are ordinary defects | 15289 Table 3 problem record; 16085 risk — conflated |
| **Insight** (806) | Course-corrections, defects, discoveries | P in store, dead in effect | `.gzkit/insights/agent-insights.jsonl` | agent | — | **append-only; no `status` field exists in any record** | 164 typed `defect` with no reader, no triage, no close path | 15289 Table 3 record — a record with no report built from it |
| **Chore** (41 registered, 46 on disk) | Recurring verification obligation | P | `.gzkit/chores/registry.json` | — | `CHORE-LOG.md` (237 runs) | **no scheduler exists**; 26 of 40 last ran 2026-07-31/08-01 | `registry.json` declares `staleness.periodDays` that nothing reads; overlaps validators and GHIs | 1012 §9.13 reverification; 29119-2 §7.3 monitoring |
| **Campaign plan** (207 KB) | Priority ruling + doctrine + acceptance spec + measurement record | P (de facto canon) | `docs/governance/build-to-1.0-campaign-2026-09-20.md` | operator | checkboxes (7/30, frozen at 7 for 66 days) | 7 editions; **72.2% of the current one is `## Amendments`** (1,670 of 2,312 lines, 33 amendments, 12 correcting its own earlier text) | Sole home of at least two normative rulings (the `Draft` lifecycle ruling; the `@enforces` contract) | 16326 PMP §7 — which §7.3.1.1 says must *reference* requirements |
| **Handoff** (758; 2.63M tokens) | Session reconstruction | T by design, P in effect | `.gzkit/handoffs/*.md` | prior session | next session | never deleted or compacted; `archive/` holds 17 of 758 | Sole home of live cross-module facts (e.g. the OBPI identifier-shape split, 6 file:line citations, **0 hits anywhere else in the repo**) | — no standard analogue; this is agent-specific |
| **Ruling** (1,029 rows) | Operator decisions | P | `.gzkit/handoffs/rulings.jsonl` | operator utterance | carried forward by `_carried_settled` | append-only; **no kind, status, scope or retirement field** | **22% (226 rows) are transient session orders** ("write the handoff") sharing a store with durable doctrine | 15289 Table 3 decision record — missing the record's required fields |
| **Gate** (943 events) | A command's exit code | T | L2 | lane policy | `gate_checked` event | per ADR, re-run on failure | **803 of 943 (85.2%) record no observation**; Gate 2 satisfied 226× by lint/typecheck; Gate 5 never recorded | 24748-1 §4.3.2 decision gate — but gates decide nothing about stage transition |
| **Receipt** (1,663 files; 1,272 tracked) | An argv + exit status + git anchor | P | `artifacts/receipts/` | a verification command | cited in attestation text | written by `gz arb step` | **391 exist only on the authoring machine** (`artifacts/` is gitignored, these were force-added); command-binding covers only 4 canonical step names — `behave`, `specreview`, `qualityreview`, `codexadversary`, `red` have none | 15026-2 §5.3.2 evidence item — missing scope, uncertainty and assumptions |
| **Attestation** (622 with text) | The operator's words | P | L2 `obpi_receipt_emitted` | Gate 5 | — | one per completion | Mechanical content is `attestation_text.strip()` being non-empty (`obpi_complete.py:1258`). 43.7% name a receipt, 46.3% are ceremonial. **15 were attested by an agent** (`agent:claude`, `agent:codex`), 3 of those flagged `human_attestation: True` | 15026-2 supported claim — asserted without argument or context |
| **TASK** (628 started / 607 completed) | Sub-work-package unit | T | L2 | OBPI | task events | started → completed/blocked (18 blocked) | — | 16326 §7.7.3.2 work package |

**Objects that do not exist.** No **risk register** or risk profile of any kind (the only risks in the repository are four rows in a Draft PRD from January). No **architecture description** in the 42010 sense. No **requirements registry** outside brief text. No **interface specification** for the ~60-verb `gz` CLI beyond `docs/user/manpages/`. No **verification obligation list** independent of a work package. No **research-question** object.

---

## 3. STANDARDS CROSSWALK

Only findings where a standard *materially changed* the reading are listed. Normative (**shall**) vs guidance (should/may) is marked. Clause numbers that could not be located are stated as such.

| Standard / clause | Engineering question | GZKit mechanism | Current condition | Finding | Class | Evidence |
|---|---|---|---|---|---|---|
| **16326:2019 §7.3.1.1** (*shall*) — the project plan **shall** provide "a reference to the official statement of product requirements"; **§7.11** stratifies PMP above SEMP/SDP as separate documents | Should a work package carry requirements or point at them? | OBPI brief carries its REQs and constraints inline | Brief is the *only* home; `shutil.rmtree` on demotion deleted 1,986 REQs and 1,584 constraints (39% of all REQs authored) | The hypothesis in the brief is correct and the standard states the remedy normatively: a work package **references** a requirements statement it does not own | **REFINE** | `adr_demote.py:475`; 378 deleted brief files measured via `git log --diff-filter=D` |
| **29148:2018** — requirement attributes (identification, source, rationale, priority, verification method, status) | Does a REQ carry the attributes a requirement needs? | REQ id + optional `[kind]` tag + `@covers` link | ID and a test link only. No source, no rationale, no status, no priority. Verification *method* is approximated by `[kind]` | A REQ is an acceptance criterion, not a requirement. 43% are Given/When/Then naming test fixture paths | **REFINE** | 3,105 REQ ids; sample classification: ~40% test assertion, ~20% system property, ~20% implementation instruction, ~15% process obligation, ~5% design decision |
| **42010:2022 §4 + §6** (*shall*) — an AD **shall** identify entity of interest, stakeholders, concerns, viewpoints framing every concern, views addressing every concern, view components, correspondences, correspondence methods, and **known inconsistencies** | Do 372 ADRs constitute an architecture description? | ADRs + `lodestar/architectural-identity.md` + `hexagonal-architecture.md` | ADRs satisfy §6.10.1–6.10.2 (decisions + rationale) and **no other subclause of §6** | **A decision corpus is not an architecture description in the sense of §6.** Decisions are indexed by *when they were made*, not by *what they cover* — so no coverage property exists | **ADD** | 23 of 372 ADRs carry `## Boundary Invariants`; no viewpoint, view or correspondence artifact exists |
| **42010:2022 §6.9.3 NOTE 1** (*shall*) — for each correspondence method applied, record whether it holds **or record all known violations**; a method is violated when a correspondence "cannot be shown to be satisfied **or when no associated correspondence exists**" | Is there a standards name for GZKit's drift machinery? | `gz drift` (713 unlinked), `gz covers` (65.3%), `gz validate --brief-reconcile` | Already operating, unnamed | **GZKit has independently built correspondence methods with violation recording.** Absence-counts-as-violation is exactly `gz drift`'s "unlinked spec". This is the highest-leverage existing asset | **KEEP** | `uv run gz drift` exit 1, 713/0/0; `uv run gz covers` exit 0, 1794/2749 |
| **42010:2022 §6.9.1** (*shall*) — "An AD **shall** record any known inconsistencies" | Where do known inconsistencies live? | Scattered: GHIs, insights, handoffs, campaign amendments, `*_grandfather.json` | The inconsistencies **are** recorded, honestly and in detail — but in six stores with no index and no retirement path | The obligation is already met in substance and failed in form. One consolidated list would discharge it | **REFINE** | `mechanical_witness_grandfather.json` (64 rows); `enforcement-claim-nc-audit` (32/47); `evidence-record-contract` ("auto-enforces nothing") |
| **1012-2024 Annex C.1.2 / C.2.5** (informative) — technical independence requires the checking party "formulate its own understanding of the problem"; internal IV&V is compromised "by using the same assumptions or development environment that masked the error from the developers" | Are the Stage-2 reviewers independent? | `spec-reviewer`, `quality-reviewer`: `tools: Read, Glob, Grep`, `model: inherit` | Same vendor, same model, fresh context, **cannot execute anything** | Context independence, not technical independence. 1012 names this exact failure mode. The reviewer re-checks the implementer's reasoning rather than forming its own | **REFINE** | `.claude/agents/spec-reviewer.md:1-7`; `pipeline_dispatch.py:450-483` parses the grant and fails safe |
| **1012-2024 §6.3 NOTE 2** — V&V must not "repeat or duplicate the same or similar testing" done by development | Does Gate 4 (BDD) verify anything Gate 2 does not? | 74 features / 466 scenarios vs 10,795 unit tests | 34 of 58 step files import gzkit production code directly; `subagent_pipeline.feature` (29 scenarios) restates `tests/test_pipeline_dispatch.py` (83 tests) name-for-name against the same functions | Gate 4 largely duplicates Gate 2 — exactly what 1012 warns against. 84% of feature-tagged REQ ids already have an `@covers` test; only **54** are behave-only | **REMOVE** (most of it) | `features/steps/gz_steps.py:29-37` (`main(args)` in-process, not subprocess); 35 `@wip` scenarios excluded by `behave.ini:6` never run |
| **1012-2024 Clause 5** (***shall***) — "The degree of rigor and intensity… **shall** be commensurate with the integrity level"; assignment **shall** be recursive so high-consequence parts are segregated | Is verification effort proportioned to consequence? | Two lanes (lite/heavy) chosen per ADR; `security` sensitivity adds scan requirements | Lane is chosen by *surface kind* (CLI/API/schema = heavy), not by consequence. Every OBPI in a lane gets the same treatment | The lane mechanism is a two-level integrity scheme applied to the wrong axis. 1012 makes consequence-scaling normative and recursive | **REFINE** | `AGENTS.md` Gate Covenant; `.gzkit/rules/security-sensitivity.md` |
| **1012-2024 Annex G** — V&V tool qualification: a tool must not "mask errors that it was designed to find" | Has GZKit hit this? | `gz validate --tautological-test-audit` | **Yes, exactly.** `_walk_body` also yielded the decorator list, so `@covers` — a gzkit symbol — satisfied `_calls_production_code` before the body was read, **exempting 220 of 290 detected operations** | GZKit independently discovered 1012's tool-qualification requirement by suffering it. The code comment names why the blinded population was the worst possible one | **KEEP** | `src/gzkit/tautological_tests.py:108-134`, GHI #730 |
| **15026-2:2022 §5.3.3** — a claim is a true/false statement about **limits on the values of a named property**, **limits on the uncertainty** of those values, over a **stated duration under stated conditions** | Are GZKit's claims explicit? | Gate names ("Tests pass", "Docs updated", "BDD verified"); attestation text | Gate names are claim-shaped; gate evidence is an exit code. 803 of 943 gate events record no observation | "The checks passed" is not a claim in the standard's sense — no property, no limit, no uncertainty, no scope | **ADD** | `gates.py:163` records the literal constant `"stdout/stderr captured"` |
| **15026-2:2022 §5.3.2** — an evidence item carries the artefact **plus** scope of applicability, uncertainty including source credibility, and associated assumptions | Is a receipt evidence? | `gzkit.arb.step_receipt.v1`: argv, run_id, git anchor, exit status, output tails | Carries artefact + provenance. Carries **no** scope of applicability, **no** uncertainty, **no** assumptions | A receipt is a *record* (15289 §6.2), not an evidence item. It proves a command ran; it does not bound what that proves | **REFINE** | `src/gzkit/arb/step_reporter.py:106-120`; `run_id` is `uuid4().hex`, not content-bound |
| **15026-2:2022 §5.3.4 / §3.1.7 / §5.3.5** — an *inference* is the reasoning step from premises to claim; an *undeveloped argument* is a declared placeholder; "A supported claim is incomplete if it contains undeveloped arguments" | Does GZKit declare its incompleteness? | `*_grandfather.json` shrink-ratchets; `test_shape` advisory; `--behave-req-tags` | **Yes — this is a genuine rediscovery.** `mechanical_witness_grandfather.json` freezes 64 unwitnessed Mechanical rows as shrink-only debt; `tautological_test_baseline.json` freezes 280 operations | The grandfather files *are* undeveloped-argument declarations. They are the right mechanism, missing only the claim they attach to | **KEEP / REFINE** | `data/mechanical_witness_grandfather.json`, `data/tautological_test_baseline.json` |
| **15026-2:2022 §4.1** (guidance) — assurance cases "need to be maintained as the system evolves"; §5.3.6(e) requires a field for changes since the previous version | Do GZKit's claims decay? | `docs/governance/*.md` doctrine files; ADR Boundary Invariants | Boundary Invariants are audited once at closeout. `obpi-decomposition-matrix.md` is "Last reviewed: 2026-03-04" and still prescribes `Foundation (0.0.x)` decomposition for a kind ADR-0.34.0 **closed** | Claims are authored and not maintained. The standard makes maintenance the defining property of the artifact | **REFINE** | `docs/governance/GovZero/obpi-decomposition-matrix.md:4,27,67` vs `.gzkit/invariants/foundation-adr-registers-invariant.json:3` |
| **29119-4:2021 §5.1 / §5.3.1.3(c)** (***shall*** step lists) — expected results **shall** be determined "by applying the corresponding test inputs **to the test basis**", for structure-based techniques too | What is the standard defence against self-confirming tests? | `req-scope-discipline.md` three-kind REQ taxonomy with distinct proof channels | GZKit measured that **32% of `tests/` assertions (42% in `tests/governance/`) were "filesystem-shaped"** — grepping prose from production docs to satisfy `@covers` parity, detecting "zero code regressions" | Independent rediscovery of 29119-4 §5.1. GZKit's own framing — "the test suite signals what changed in CODE BEHAVIOR; it does not signal what changed in CONTENT" — is the same principle | **KEEP** | `docs/governance/req-scope-discipline.md:9-40`, operator 2026-05-25: *"staggering find."* |
| **29119 (all 4 parts)** — **clause not located**: no concept, requirement, measure or vocabulary for whether a test is *capable of failing*; no mutation testing; "test oracle" appears 0× in Parts 2–4 | Is GZKit's anti-tautology machinery over-engineering? | `red_witness.py`, `mutation_witness.py`, `tautological_tests.py`, `test_shape.py` | RED receipts classify `assertion`/`error`/`none`/`not-applicable` and refuse to equate them; mutation verdicts split `killed`/`survived` (guard) from `invalid`/`inconclusive` (run) | **This machinery is ahead of the testing standard.** 29119 has no vocabulary for it. It is the most defensible engineering in the repository | **KEEP** | `red_witness.py:14-27,49-62`; `mutation_witness.py:12-19,30-35` |
| **29119-2:2021 §8.2.4.3(b), §8.2.4.4(b)** (***shall***) — coverage items and test cases **shall be prioritized using risk exposure levels** | Is test effort risk-ordered? | 10,795 test methods, 1.47:1 test:source | No risk classification exists anywhere, so no prioritization is possible | Ordering is normatively mandatory; volume is not. GZKit has volume without ordering | **ADD** | No risk register found by exhaustive search |
| **29119-3:2021 §4.1.1** (***shall***) + **15289:2019 §5.1** (***shall***) — information "**shall** be considered as conforming if… unpublished but available in a repository, divided into separate documents, or combined"; §3.1.11 — "include" means "has either the information **or a reference to** it" | Does adopting a standard mean writing documents? | — | — | **No.** Every "shall include" in 15289 Clauses 7/9/10 is dischargeable by reference. A generated view over a repository conforms. This governs the entire bureaucracy question below | **KEEP** (as licence) | 15289 §5.1, §6.4.1, §8.2, §10.1 |
| **15289:2019 §8.2** (normative clause) — "definition does not in itself indicate that a specific information item is produced"; clauses requiring planning "do not necessarily mean that a documented plan is produced" | Does every declared process need an artifact? | 41 chores, 112 validators, 758 handoffs | — | The standard explicitly blocks the inference from process-mandate to document. GZKit has made that inference repeatedly | **REMOVE** (the inference) | 15289 §8.2 |
| **15289:2019 §6.2** — a record "state[s] results achieved or provide[s] evidence"; a *report* (§7.6, ***shall***) carries scope, **context (assumptions)**, **body including methods of obtaining results**, conclusions and recommendations | Is the insights ledger useful? | `agent-insights.jsonl`, 806 records, no reader | 164 `defect` records with no status field and no close path | The store is a correct *record* set. What is missing is any *report* built from it. 15289 names the gap precisely | **REFINE** | `src/gzkit/insights/` — every reader counts or shape-checks; none reads `summary` or `next_action` |
| **16085:2021 §3.5 / §3.7 / §6.4.3.3** — risk is "effect of uncertainty on objectives"; risk *exposure* is the probability×consequence arithmetic; the risk profile **shall** (by incorporation via §6.4.1) carry 10 items including **current state** and **history** | Does GZKit manage risk? | none | **No risk register, profile or object exists.** Risks are carried as prose inside GHIs, insights, handoffs and campaign amendments | Risk is one of two object kinds with no home at all (the other is research question) | **ADD** | Exhaustive search; PRD §9 holds 4 rows, Draft, 2026-01-22 |
| **16085:2021 §6.4.3.2** — a risk threshold is the level "acceptable **without explicit review by the stakeholders**"; three bands: accept / monitor / treat | What should decide operator escalation? | "IRON LAW": only the operator initiates OBPI work | Enforced in **12+ prose locations and zero code**. `obpi_pipeline_cmd` performs no identity or consent check. The corpus records its own violation | The standard reframes escalation as a *threshold on delegated authority*, not a blanket rule. A blanket rule that cannot be enforced is weaker than a threshold that can | **REFINE** | `OBPI-0.35.0-08-remember-post-append-advisory.md:52`: *"started by an agent on 2026-08-23 WITHOUT operator consent"* |
| **15939:2017** — the measurement information model: information need → measurable concept → entity/attribute → base measure → derived measure → indicator → information product | Are GZKit's numbers tied to decisions? | 67 ledger event types; `obpi_lock_ttl_warning` (32 events) | `ttl_warning` fires on every SessionStart at 50% of TTL, across 5 distinct OBPIs with repeats seconds apart, and **no consumer reads it**. It measures session restarts | A measure with no information need and no reader. 15939's whole point is that measures derive from a need, not from what is convenient | **REMOVE** | `scripts/session_orientation.py:952` |
| **24748-1:2024 §4.3.2 Table 1** (guidance) — a decision gate's outcome options are: begin subsequent stage / continue this stage / go to or restart another stage / hold project activity / terminate project. **15288:2023 §6.3.1.3 b)2)** (***shall***) — "Define achievement criteria for the life cycle stage decision gates" | Do GZKit's five gates decide anything? | Gates 1–5 | A gate records an exit code. **No gate outcome is a stage-transition decision**; none can hold, restart or terminate | GZKit's "gates" are *checks*, not decision gates. The vocabulary borrows authority the mechanism does not have | **REFINE** (rename/reframe) | 943 `gate_checked` events; `_run_gate_5()` returns `True` unconditionally |
| **24748-3:2020 §5.2.1** — "Use of these terms to define stages is **not normative**"; §6.3.3 stages "can be combined, eliminated or added" | Is GZKit's invented lifecycle conformant? | PRD→ADR→OBPI→REQ→TASK | — | **Yes, by construction.** An invented stage set is conformant; what is not optional (15288 §6.3.1.3 b)2), *shall*) is defining gate achievement criteria in advance and recording the authorisation to proceed | **KEEP** | — |
| **32675:2022 §6.3.1.3 b)4** (normative task list) — enable "normalization of frequent change through compact low-dependency scopes, **low gates**, low overhead, and fast handoffs" | Is heavier governance always safer? | 5 gates, 112 validators, 41 chores, 92k-token entry cost | — | A standard explicitly argues *against* heavy gating for change normalization. This is the clearest external warrant for simplification | **REMOVE** (excess) | 32675 §6.3.1.3 b)4 |
| **32675:2022 §5.4** (guidance) — "the same person or group can perform multiple processes"; **§5.3.2** — very small entities "can… operate without formal organizational structures" | Does role separation require separate people? | Operator + agents | — | Explicit permission for role collapse. Removes any obligation to simulate organizational separation | **KEEP** (as licence) | 32675 §5.4, §5.3.2 |
| **730-2026 §4.2 / §4.5** — "both dynamic and static testing are forms of software **quality control**"; SQA "confirms that suitable processes exist and have been performed" | Is `gz check` quality assurance? | 112 validators, 60 in `--fast` | It is quality *control* (checking products) plus process conformance checks | The distinction matters: 730's SQA question is "can this process produce quality?", which GZKit answers only in retrospective audits | **REFINE** | `uv run gz check --fast`: 60 steps, exit 0 |
| **730-2026 §5.3.6.2(d)–(g)** (***shall***) — the SQA function shall be independent of the development unit: technical, managerial and financial | Is 730's independence achievable here? | — | A solo operator cannot instantiate financial or managerial independence | On this axis **730 is stricter than 1012** and is simply not satisfiable. Do not pretend otherwise; 1012 Annex C's *embedded* form is the honest self-description | **REMOVE** (the aspiration) | 1012 Annex C.2.6 |
---

## 4. PERSISTENT-VS-TRANSIENT ANALYSIS

### 4.1 The standards' own answer

**Standard-derived principle.** ISO/IEC/IEEE 12207:2026 **Annex B, Table B.1** types every process output as `artefact`, `info`, `record` or `store`. **System requirements, stakeholder requirements, operational concept, architecture viewpoints, architecture views and models, and traceability mappings are all typed `artefact`** — defined at §3.1.10 as a work product "produced and used during a project to capture and convey information". Annex B's preamble states that artefacts "are usually initiated in one process and revised, enhanced, or completed in other processes."

Each technical process then carries a normative "Manage…" activity: §6.4.3.3 requires the project to "Maintain traceability of the system requirements" — bidirectionally, **"Through the life cycle"** — and to baseline them (§3.1.12: "formally approved version… fixed at a specific time"). §5.4.1 adds that "The life cycle processes… are not aligned to any specific stage."

**Processes are not increments, and increments do not own the engineering information.**

Verification is the interesting exception and it cuts the same way: 12207 §6.4.9.1 says verification "can be performed across all technical processes and reiterated throughout the life cycle" — it *runs* per increment — but Table B.1 types **verified system** as `artefact` and **verification records** as `record`, and outcome §6.4.9.2 g) requires that "Traceability of the verified system elements is established." Verification runs transiently and **deposits durably**.

### 4.2 What should persist

| Should persist | Standard basis | Does GZKit have it? |
|---|---|---|
| System intent / product requirements | 12207 Table B.1 (`artefact`); 29148 §6.3/§6.4 | **Inert.** PRD is Draft since 2026-01-22; `FR-*` cited 0× outside it |
| Requirements, with rationale and source | 29148 §5.2.8.2 (`should`); §5.2.7 (***shall*** — "All assumptions made regarding a requirement **shall** be documented") | REQs exist (3,105) with ID + test link only. **No rationale field exists** — so the one 29148 `shall` in this area has nowhere to be satisfied |
| Requirement **set** properties | 29148 §5.2.6 (***shall***) — complete, consistent (no overlap, one term one meaning), feasible, comprehensible, able to be validated | **Absent.** All checking is per-REQ. Set-level properties are structurally invisible to a per-item checker, and 5.2.6 is a `shall` |
| Constraints | 29148 §3.1.7, §6.3.3.5 ("Constraints are one type of requirement") | 3,855 FAIL-CLOSED constraints exist, **267 identified**, mixed with per-OBPI scope fences in the same list |
| Invariants / architectural obligations | 42010 §6.9.3 correspondence methods | 23 ADRs carry Boundary Invariants, numbered per-ADR, audited once at closeout; 4 machinery invariants in `.gzkit/invariants/` |
| Architecture description | 42010 §6 (***shall***) | **Absent.** 372 decision records; no viewpoints, views, view components, correspondences, or inconsistency list |
| Interfaces | 12207 §6.4.4 | `docs/user/manpages/` + `gz validate --cli-alignment`. Partial and real |
| Architecture decisions + rationale | 42010 §6.10.1–2 | **Strong.** This is GZKit's best-developed object |
| Risks | 16085 §6.4.3.3 (risk profile: 10 items incl. current state and history) | **Absent entirely** |
| Verification obligations | 1012 Tables 1a–2d; 29119-3 §7.2.7.7 (***Shall***) | Distributed across 112 validators, 41 chores and per-OBPI proof channels. No standing list |
| Traceability | 12207 §6.4.3.3 (***shall***, "Through the life cycle"); 29148 §6.4.3.5 (five legs) | **One leg of five.** REQ→test exists and works. REQ→need, REQ→architecture, REQ→element, REQ→parent do not |
| Current system state | 12207 §6.3.6 information management | `gz state` (1,187 nodes), `gz status` (2,362 lines) — real, but 23% of the status payload is campaign narrative |
| Known inconsistencies | 42010 §6.9.1 (***shall***) | Recorded honestly in six unlinked stores with no retirement path |

### 4.3 What should exist only for the duration of a work package

Objective; task decomposition; implementation activity; findings-in-flight; repairs; generated evidence pointers; completion/exit criteria; the session's own reconstruction notes. **GZKit models all of these correctly.** The OBPI brief's `## Objective`, `## Discovery Checklist`, `## Evidence`, `## Quality Gates`, `## Completion Checklist` and `## Tracked Defects` are appropriately transient, and together they are ~55% of brief content.

### 4.4 What currently lives on the wrong side of the boundary

**Persistent knowledge trapped in transient carriers — the central finding.**

| Knowledge | Currently lives in | Evidence |
|---|---|---|
| Requirements (3,105) | OBPI briefs only; identity is a coordinate *inside* the work package (`REQ-<adr>-<obpi>-<req>`) | **1,986 REQs (39% of all ever authored) deleted with 378 briefs by `shutil.rmtree`** (`adr_demote.py:475`) |
| Constraints (3,855) | OBPI brief prose, unaddressable | 1,584 deleted with those briefs |
| Architectural obligations | 23 ADRs' `## Boundary Invariants`, per-ADR numbering, audited once | Cited from production code: `enforcement.py:724,746`, `pipeline_runtime.py:602,641`, `fidelity.py:129,238,263` |
| Normative rulings | Campaign-plan amendments | The `Draft`-lifecycle ruling (~1,200 words) appears **only** in 3 campaign editions and 4 handoffs — not in the ADR, not in `.gzkit/rules/`, not in state-doctrine |
| Cross-module contract facts | A single handoff | The OBPI identifier-shape split (6 file:line citations) has **0 hits** across `docs/`, `.gzkit/rules/` and `src/`, and 0 hits across all 1,075 GHI bodies |
| Deliberate design refusals | A closed GHI comment + one handoff | *"The 466 unanswered OBPI citations are… refused on purpose… A future session that 'improves' the hit rate by guessing is reversing a ruling."* |
| Defects and verification gaps | 212 pool ADRs (67 defects, 41 verification obligations) | Pool promotion rate: 2 in the last 4 months against 204 entries |
| Course-corrections, discoveries | 806 insights, **no reader, no status field** | 164 typed `defect` with no close path |
| Risks | Prose scattered across GHIs, campaign amendments, handoffs | No risk object exists |

**Transient matter polluting durable stores — the mirror problem.**

- **226 of 1,029 rows (22%) in `rulings.jsonl` are transient session orders** — verbatim: *"Author this handoff (verbatim: 'write the handoff')."*, *"Work GHI #770 (verbatim: 'do 770')."* — sharing an untyped, retirement-free store with durable doctrine such as *"Retire `.gzkit/schemas/ledger_events.json` by forward supersession."*
- **758 handoffs, never compacted** (17 of 758 archived), growing at ~9.5/day.
- **`## Evidence` is 24.2% of all brief content** (33,698 of 139,443 lines) and is pure work log, preserved in L1 canon.
- **`obpi_lock_ttl_warning`**: 32 events across 5 OBPIs, fired on every SessionStart at 50% of TTL, **read by nothing**.

**The measured consequence** is a three-session rediscovery loop, which the repository documents about itself: *"Three sessions (2026-06-09, 2026-07-02, 2026-09-22) have independently re-derived this as a suspected defect."*

---

## 5. TRACEABILITY MODEL

### 5.1 What GZKit can answer today — measured

| Question | Answerable? | How | Result |
|---|---|---|---|
| a. Why does this requirement exist? | **No** | No rationale or source field exists on a REQ | — |
| b. What requirement caused this implementation? | **Partially** | Reverse of `@covers`; code→test→REQ | Works where a test exists |
| c. Which ADR affects this requirement? | **Yes** | REQ id encodes it | `REQ-0.35.0-04-01` → ADR-0.35.0 |
| d. What code realizes it? | **No** | No REQ→code edge; only REQ→test | — |
| e. What tests verify it? | **Yes** | `gz covers` | 1,794/2,749 (65.3%) |
| f. What evidence demonstrates it? | **Partially** | Receipt IDs in attestation text | 43.7% of attestations name one; 391 receipts exist only on the authoring machine |
| g. What work package changed it? | **Yes** | REQ id encodes the OBPI | — |
| h. What requirements are affected if module X changes? | **No** | `gz ontology reach` returns `Unknown node` for a source path | Blast radius is the hand-written `## Discovery Checklist`, presence-checked only |
| i. Which requirements lack verification? | **Yes** | `gz drift` | 713 unlinked, exit 1 |
| j. Which implementation has no governing requirement? | **No** | `--orphaned-implementation` **does not mean this** — it detects an OBPI with lock-claim + edits + force-release and no completion event | Name/behaviour mismatch (`governance/trust_audits/orphaned_implementation.py:1-20`) |
| k. Which ADRs rest on obsolete assumptions? | **No** | No assumption is recorded as a first-class object | `obpi-decomposition-matrix.md` still prescribes a decomposition for the `foundation` kind that ADR-0.34.0 closed |

**Two coverage numbers disagree:** `gz covers` reports 955 uncovered; `gz drift` reports 713 unlinked. Different populations, no reconciling statement.

**Graph parentage, measured** (`gz state --json`, 1,187 nodes): all 901 OBPIs have an ADR parent. Of 285 ADR nodes, **64 have no parent at all** (38 non-pool, 26 pool); 212 name the PRD; 7 name an ADR; 2 name a GHI. Ten pool ADRs on disk are absent from the graph; two graph entries have no file.

### 5.2 The minimum useful traceability graph

**Standard basis.** 29148 §6.4.3.5 names five legs: down to lower-level requirements, to architecture, to implementing elements, to verification entities, and **up** to parent requirements or stakeholder needs. 12207 §6.4.3.3 makes maintaining it normative "Through the life cycle". 42010 §6.9.3 supplies the enforcement shape: a correspondence method is violated when a correspondence "cannot be shown to be satisfied **or when no associated correspondence exists**".

**Recommendation.** The smallest graph that closes GZKit's actual gaps has **six node types and seven edge types**. It is deliberately smaller than the standards' full model, and four of the seven edges already exist.

```
  NEED ──justifies──▶ REQUIREMENT ──constrained-by──▶ CONSTRAINT
                           │  ▲                            │
              allocated-to │  │ derived-from               │ fenced-by
                           ▼  │                            ▼
                       COMPONENT ◀──governs────── ARCHITECTURAL OBLIGATION
                           │
                  verified-by │
                           ▼
                      VERIFICATION ──produces──▶ EVIDENCE
```

| Edge | Exists today? | What it would close |
|---|---|---|
| REQUIREMENT → VERIFICATION | **Yes** — `@covers`, behave tags, `gz covers`/`gz drift` | — |
| VERIFICATION → EVIDENCE | **Yes** — ARB receipts | Weak for 5 of 9 step names (no command binding) |
| REQUIREMENT → work package | **Yes** — encoded in the REQ id | But *only* there, which is the defect |
| ARCH OBLIGATION → COMPONENT | **Partially** — Boundary Invariants cited from code comments | Would give BIs a home outside a decision record |
| **NEED → REQUIREMENT** | **No** | Question (a); the 29148 §5.2.7 `shall` on assumptions |
| **REQUIREMENT → COMPONENT** | **No** | Questions (d) and (h) — impact analysis, blast radius |
| **CONSTRAINT identity** | **No** | 3,855 constraints, 267 identified |

**Minimum viable addition, stated as principle not design:** give REQUIREMENT and CONSTRAINT identity independent of the work package that introduced them, and add one upward edge and one allocation edge. Everything else GZKit already has. *This is a measurement-program question (M-A), not a Phase-1 recommendation.*

---

## 6. OBPI ASSESSMENT

Against the six questions posed, with evidence.

**Does it carry persistent knowledge it should merely reference? — Yes, and this is the load-bearing finding.**

Section inventory across all 556 briefs (139,443 lines): `## Evidence` 24.2%, `## Quality Gates` 10.7%, `## Discovery Checklist` 9.2%, `## Allowed/Denied Paths` 7.4%, `## Verification` 5.6%, **`## Requirements (FAIL-CLOSED)` 5.3%**, **`## Acceptance Criteria` 4.7%**. **The two sections carrying durable engineering knowledge are 10% of the artifact; the other 90% is work log.** In the largest brief (1,728 lines), Acceptance Criteria is 19 lines and Evidence is 1,048 (61%).

16326:2019 §7.3.1.1 (***shall***) states the remedy: a project plan **shall** provide "a reference to the official statement of product requirements". §7.11 stratifies the plan above the engineering plans as separate documents. GZKit inverted this: the work package is the requirements statement.

The cost is measured, not theoretical: **`shutil.rmtree` on ADR demotion deleted 378 briefs carrying 1,986 REQs and 1,584 constraints — 39% of all REQs ever authored.** The surviving pool file retains the prose and zero REQ identifiers. `src/gzkit/obpi_lifecycle.py:256-260` names the worse case in its own code comment: demoting an already-parked parent emits no park events *"while still deleting every brief… A hollow exit 0."*

**Is its jurisdiction too broad? — No. Its jurisdiction is too *unenforced*.**

`## Allowed Paths` appears in 549 of 556 briefs and is parsed by five parsers. No hook refuses an out-of-scope write; `## Denied Paths` is never tested against a write. The airlock computes a HOLD that all six call sites print and continue past, over an input that is empty in practice. Brief-reconcile drift runs at **23.4% post-fix** (39 of 167; the headline 51% figure is contaminated by 86 events from a bug fixed by `e040df408`), and the dominant signals are `allowlist_missing_in_brief` (166) and `discovery_unresolved_paths` (135) — **jurisdiction discovered after the work**. 68 reconciles carry `applied: true`: the allowlist was widened to fit what had already been touched.

**Does it duplicate other artifacts? — Yes, in two directions.** `## Evidence` duplicates the ledger (which already holds gate events, receipts and completion records) in L1 canon. `## Quality Gates` duplicates the 943 `gate_checked` events. `## Discovery Checklist` (5,498 items, median 12.6/brief, top targets `AGENTS.md` ×360 and `CLAUDE.md` ×207) duplicates what path-scoped rules already deliver.

**Does it mix planning, specification, implementation, repair and assurance? — Yes, all five, in one document.** Objective (planning), Acceptance Criteria + FAIL-CLOSED (specification), Evidence (implementation), Tracked Defects (repair), Quality Gates + Human Attestation (assurance).

**Has it accumulated responsibilities? — Measured, and affirmatively.** Template `src/gzkit/templates/obpi.md`: 2026-01-22 → 57 lines / 8 sections; 2026-03-12 → 223 / 15; 2026-09-09 → **273 / 15**. **4.8× line growth, 1.9× section growth in 8 months.** Briefs at birth (`git log --diff-filter=A`, n=482): median 96 lines / 9 sections (Feb) → 242 / 14 (Apr) → **382 / 15 (Jul)**. Post-birth growth is modest (median +30 lines), so **the accumulation is in the template, not in evidence accrual — the work package was given more responsibilities.** REQ statements themselves swelled 6×: median characters per REQ at birth 61 (Feb) → 264 (Jun) → 369 (Jul), with Given/When/Then form rising 26.5% → 61–72%.

**Is the hypothesis in the brief correct?** **Yes, and more sharply than framed.** The OBPI does not merely *carry* persistent knowledge — it is the *only* place that knowledge exists. There is no REQ registry; REQ identity is a coordinate inside the work package; the 3,855-item constraint layer is unaddressable; and the one designated durable home for system invariants (`## Boundary Invariants`) is present on 23 of 372 ADRs — 6% of parents.

**Health, measured.** 954 OBPIs created, 521 completed (54.6%), 48 withdrawn, 7 repudiated. Duration created→completed (n=519): median **3.07 days**, p75 10.5, p90 20.4, max 74.5; **33% exceed 7 days, 7% exceed 30**. Creation is collapsing: 410/month (Mar) → 10 (Sep).

*Correction to an earlier reading in this investigation:* the 377 `obpi_parked` events are **not** evidence of work stalling. All 377 carry `reason: pool_demotion`, land on five timestamps across three days, and represent one backlog-demotion campaign (GHI #520, repaired under GHI #584). The park count says nothing about work-package health.

<!-- gz-validate-skip: command-shape -->
Parking has no operator verb: `gz obpi park` does not exist, and the 377 events were emitted only by `gz adr demote` and a backfill module. The absence is the finding — a lifecycle state with doctrine, a schema and a lifecycle module, but no way for an operator to enter it deliberately.

The 7 repudiations are the more informative signal: all fall in one 7-day window (2026-06-13→19), 5 typed `model-induced-fabrication`, 2 `verification-invalid`, all attested `g0`. One reversed an attested claim of a *"byte-deterministic Jinja2 renderer"* that contained no Jinja2. **The reversal mechanism works and was exercised** — which also says Gate 5 was, at that moment, accepting agent claims unverified.
---

## 7. AGENT ENTRY / EXIT ANALYSIS

### 7.1 What an agent must reconstruct on entry — measured

Mandatory reading before writing a line against a **median** OBPI:

| Source | Bytes | Share |
|---|---:|---:|
| `gz-obpi-pipeline/SKILL.md` | 125,897 | 36% |
| `gz status` output | 79,870 | 23% |
| Parent ADR | 65,593 | 19% |
| Resumed handoff | 22,506 | 6% |
| Session-start hook | 21,521 | 6% |
| `AGENTS.md` | 19,979 | 6% |
| **Median OBPI brief** | **12,901** | **3.7%** |
| `CLAUDE.md` | 2,014 | 0.6% |
| **Total** | **350,281** | **≈ 92,000 tokens** |

Against the largest brief (156,416 B) the total reaches 493,796 B ≈ **130,000 tokens**. Obeying the session hook's instruction to read the handoff lineage adds ~54,000 tokens (20 documents, 216,956 B — and the walk is **truncated at the cap**, so the "19 ancestors" figure is a floor imposed by `handoff_api.py:1181`, not the true chain length).

**Interpretation.** The artifact describing the work is 3.7% of what must be read to begin it. The largest single item is the procedure, not the problem. 23% is a status command whose first 55 lines are campaign narrative transcribed from a 207 KB plan.

Beyond volume, an entering agent must **reconstruct**, because nothing states it:

1. **Which requirements govern the surface it is about to touch** — there is no index from a source path to REQs.
2. **What will break** — `gz ontology reach` cannot resolve a source path; blast radius is a hand-written checklist whose contents are never validated.
3. **Which constraints are durable and which are this-OBPI scope fences** — both are unnumbered items in one `## Requirements (FAIL-CLOSED)` list.
4. **Which architectural obligations bind** — Boundary Invariants live in 23 ADRs, numbered per-ADR, audited once at closeout.
5. **Which known gaps are already known** — the honest gap inventory is spread across `enforcement-claim-nc-audit`, `evidence-record-contract`, three `*_grandfather.json` files, 806 insights, 55 open GHIs and 758 handoffs, with no index and no retirement path.
6. **Which prior rulings are still live** — `rulings.jsonl` has no status, scope or retirement field, and 22% of it is transient session orders.
7. **Whether a declared rule is enforced or aspirational** — answerable only via `docs/governance/advisory-rules-audit.md`, itself 736 lines with 64 rows frozen as unwitnessed.

### 7.2 What should already be explicit before an agent begins

**Standard basis.** 15288:2023 §6.3.1.3 b)2) (***shall***): "Define achievement criteria for the life cycle stage decision gates". 12207 §6.3.1.3 a)4) NOTE 5: a breakdown element binds to an architecture element at a detail level "consistent with identified risks". 16326 §7.7.3.2 (`should`): a work package specifies resources, duration, work products, **acceptance criteria** and predecessor/successor dependencies — note it does **not** specify requirements. 42010 §6.9.3: a correspondence method's violation includes *absence*.

**Recommendation.** An agent should receive, as data rather than prose: the requirements in force on the surface (not the requirements invented for this increment); the constraints in force, with durable ones distinguished from scope fences; the architectural obligations that bind the surface; the components in the blast radius; the assumptions that must remain true; the exit criteria; and the escalation threshold. GZKit today supplies exit criteria and a scope declaration, and expects the rest to be reconstructed.

### 7.3 What evidence should exist on exit

GZKit already produces most of this and the parts it produces are good: `obpi_receipt_emitted` with attestation text, ARB step receipts with git anchors, `gate_checked` events, `@covers` linkages, RED receipts, mutation sweeps, `brief_reconciled` drift records.

The gaps are specific:

- **Gate events record no observation** — 803 of 943 (85.2%). 15026-2 §5.3.2 requires an evidence item to carry scope of applicability, uncertainty and assumptions; a receipt carries provenance only.
- **391 receipts exist only on the authoring machine** (`artifacts/` is gitignored; 1,272 of 1,663 were force-added). An evidence record nobody else can retrieve is not evidence.
- **No exit record of what the work *assumed***. 29148 §5.2.7 (***shall***): "All assumptions made regarding a requirement **shall** be documented." Nothing captures this, and it is precisely what a handoff cannot recover — as one handoff says of itself: *"what this document cannot recover is what the working session considered and rejected without writing down."*
- **No exit record of what the work *disturbed*** beyond the allowlist reconcile. `gz airlock out` exists and is diagnostic-only.

---

## 8. TOP FINDINGS

### 8.1 Five strongest existing practices

**Presented without numeric ranking — the evidence supports each as strong, not an ordering among them.**

- **The REQ→test correspondence machinery.** `gz covers` (1,794/2,749, 65.3%), `gz drift` (713 unlinked / 0 orphan / 0 unjustified), one consolidated REQ grammar (`triangle.py:24-31`, replacing ~20 disagreeing regexes under GHI #615), 5,359 `@covers` annotations. **This is 42010 §6.9.3 correspondence methods with violation recording, independently built, with absence correctly counted as violation.** It is the single most valuable asset in the repository and the natural foundation for everything the measurement program might propose.

- **The anti-tautological-test stack.** `red_witness.py` classifies RED into `assertion` / `error` (weak) / `none` / `not-applicable` and refuses to equate them; `mutation_witness.py` splits `killed`/`survived` (a claim about the guard) from `invalid`/`inconclusive` (a claim about the run), and documents a real `.pyc`-cache contamination bug (GHI #963). **29119 has no vocabulary for any of this** — "test oracle" appears zero times in Parts 2–4. This machinery is ahead of the testing standard. The measured honesty is the point: 235 RED receipts are 71.9% `error`, 16.6% `assertion`, **8.9% `none`** — 21 tests that demonstrably cannot fail, found and recorded rather than suppressed.

- **The REQ-kind taxonomy and its origin measurement.** GZKit measured that 32% of `tests/` assertions (42% in `tests/governance/`) were filesystem-shaped — grepping prose from production docs to satisfy `@covers` parity, detecting "zero code regressions" (`req-scope-discipline.md:9-40`). The remedy — three REQ kinds with **distinct proof channels** — is an independent rediscovery of 29148 §6.5.2.2's four verification methods and 29119-4 §5.1's rule that expected results derive from the *basis*, not the implementation.

- **The self-audit habit, recorded durably and unsoftened.** `enforcement-claim-nc-audit-2026-07-18.md:50`: *"32 of 47 claims do not prove what they assert. `gz check` reports 47/47 verified."* `evidence-record-contract.md`: *"The contract auto-enforces nothing"*, effectiveness *"an UNTESTED HYPOTHESIS."* `Ledger.get_post_validation_failed_gates` exists to re-surface 16 failures the effective view launders to pass (GHI #411). `tautological_tests.py:108-134` records that `@covers` blinded the audit over 220 of 290 operations — **exactly 1012 Annex G's tool-qualification failure mode**, discovered by suffering it. The `*_grandfather.json` shrink-ratchets are, in 15026-2 §3.1.7 terms, **declared undeveloped arguments**.

- **Path-scoped agent instructions and real runtime enforcement.** All 25 `.claude/rules/*.md` carry `paths:` scoping (ADR-0.0.20, enforced by `gz validate --unscoped-rules`) — genuine progressive disclosure against a 150 KB rule corpus. And `.claude/hooks/verifier-pipe-gate.py` blocked two of my own commands during this assessment for masking a verifier's exit status behind a pipe and behind a later statement, citing the rule and supplying the corrected form. **That is a claim made explicit and then mechanically enforced, in an external agent's hands, on first contact.**

### 8.2 Five most important structural weaknesses

- **Requirement and constraint identity is a coordinate inside a work package.** `REQ-<adr>-<obpi>-<req>` cannot outlive its OBPI, and did not: **1,986 REQs and 1,584 constraints (39% of all REQs authored) were deleted by `shutil.rmtree`** at `adr_demote.py:475`. 12207 §6.4.3.3 makes maintaining requirement traceability "Through the life cycle" normative; this breaks it structurally, not incidentally.

- **No persistent system model exists, so six intake surfaces each carry part of one.** Requirements are split across pool ADRs, GHIs, insights, the campaign plan and handoffs. **Risk and research-question have no home at all.** No surface is a backlog *against* a model, because no surface holds the model. The measured consequence is a documented three-session rediscovery loop.

- **Jurisdiction is declared and unenforced.** No hook refuses an out-of-allowlist write; `## Denied Paths` is tested against nothing; the airlock's HOLD is printed and passed over at all six call sites, over an empty input. Post-fix brief-reconcile drift is 23.4%, dominated by jurisdiction discovered *after* the work, and 68 reconciles widened the allowlist to match what had already been touched. The "IRON LAW" that only the operator initiates OBPI work appears in 12+ prose locations and **zero code**; the corpus records its own violation (`OBPI-0.35.0-08…md:52`).

- **The gates record exit codes where the covenant promises claims.** 803 of 943 gate events carry no observation; 226 of 509 Gate-2 events are lint or typecheck under a gate named "Tests pass"; Gate 5 in `gz gates` is `return True` and has never emitted an event; the real Gate 5's mechanical content is `attestation_text.strip()` being non-empty. `gz gates` itself is deprecated (GHI #705) while AGENTS.md documents the covenant against it. In 24748-1 §4.3.2 terms these are **checks, not decision gates** — no outcome can hold, restart or terminate anything.

- **Agent entry costs ~92,000 tokens, of which the work product is 3.7%.** The procedure (125,897 B) and a status command (79,870 B) are 59% of it. The handoff corpus has reached 2.63M tokens and is never compacted. Governance prose outweighs source 3.5:1; handoffs alone are 57% of the source tree's line count.

### 8.3 Five highest-leverage opportunities

**Stated as directions, not designs. The measurement program would test them.**

- **Give requirements and constraints identity independent of the work package.** This single change addresses the deletion loss, the rediscovery loop, and traceability questions (a), (d) and (h). The REQ grammar already exists and is already unique — only its *ownership* is wrong. 16326 §7.3.1.1 states the target shape normatively: the work package **references** the requirements statement.

- **Name the claim each gate asserts, and record one observation per gate.** 15026-2 §5.3.3: a claim needs a property, a limit, an uncertainty bound and a scope. GZKit already has the vocabulary in two places — the falsifiability discriminator at `.gzkit/rules/tests.md:52` and the 89-entry enforcement-claim registry. Extending that to the five gates, and replacing the literal `"stdout/stderr captured"` with an actual observation, is cheap and removes the largest source of false confidence.

- **Consolidate the known-inconsistency inventory into one list with a retirement path.** 42010 §6.9.1 makes recording known inconsistencies a `shall`; GZKit already exceeds it in substance and fails it in form. The findings currently live in six stores that only accumulate. Note the shape of the problem: `enforcement-claim-nc-audit` disqualified its own method — *"a stochastic surface auditing a stochastic surface"* — which is a correct 1012 Annex G tool-qualification judgment and means the inventory needs a non-agent witness, not another audit.

- **Retire Gate 4 as a separate gate and keep the ~54 behave-only REQs.** 1012 §6.3 NOTE 2 warns V&V against duplicating development's testing; 34 of 58 step files call production code in-process, `subagent_pipeline.feature` restates `tests/test_pipeline_dispatch.py` name-for-name, 84% of feature-tagged REQs already have `@covers`, and 35 `@wip` scenarios never run at all. The genuinely additive residue is the 9 subprocess-driving step files and the `@expected-warning` negative controls.

- **Introduce a risk object with thresholds, and let the threshold replace the un-enforceable IRON LAW.** 16085 §6.4.3.2 defines a risk threshold as the level "acceptable **without explicit review by the stakeholders**" — escalation as a *boundary of delegated authority*, in three bands (accept / monitor / treat). GZKit's operator-initiation rule is a blanket prohibition that no code enforces and that the corpus records being violated. A threshold on consequence is both enforceable and better aligned to 1012 Clause 5's normative requirement that rigour scale to integrity level.

---

## 9. BUREAUCRACY FILTER — standards machinery GZKit should probably NOT adopt

The governing permission is explicit and normative. **15289:2019 §5.1 (*shall*):** information items conform when "unpublished but available in a repository… divided into separate documents… or combined with other information items into one document", and "Use of the nomenclature… is not required to claim conformance." **§3.1.11 + §5.1:** "include" means "has either the information **or a reference to** the information" — so every "shall include" is dischargeable by reference. **§8.2:** "definition does not in itself indicate that a specific information item is produced"; clauses requiring planning "do not necessarily mean that a documented plan is produced." **29148 Clause 7 and §4.4 NOTE 2** say the same for requirements items. **29119-3 §4.1.1 (*shall*)** says the same for test documentation.

**Adopting these standards does not mean writing documents. GZKit's existing instinct — put it in the ledger, derive the view — is already the conformant form.**

| Do not adopt | Standard / clause | Why not here |
|---|---|---|
| Agreement processes (Acquisition, Supply); SLAs and OLAs | 12207/15288 §6.1; 32675 §6.1 | Presuppose two parties. 12207 §4.1: where a contract governs, claim compliance with the agreement instead |
| Organizational project-enabling processes — portfolio, HR, knowledge management | 12207/15288 §6.2; 32675 §6.2.3–6.2.6 | §5.6.3: these "apply outside the span of a project's life". A one-person project inventing a portfolio layer builds §6.2 machinery without the organization it serves |
| The four mandated requirements documents (BRS, StRS, SyRS, SRS) | 29148 Clause 7 (`shall`) | 29148's strongest `shall`, and it exists to structure acquirer/supplier agreement. Clause 7 itself waives physical documentation |
| The four-baseline scheme with change-approval authority levels | 29148 §6.6.2.2.2 | Partitions change authority between acquirer and supplier. One operator has one authority level |
| Formal VVP, 108 task-report types, 16 activity-summary reports per domain | 1012 Clause 12, §11.1 | Calibrated to a formal V&V engagement |
| IV&V organizational forms (classical / modified / integrated) | 1012 Annex C.2 | Financial and managerial independence are not instantiable by a solo operator. **1012's `embedded` form is the honest self-description** |
| The SQA Plan outline and SQA-unit independence | 730-2026 Annex A Table A.1; §5.3.6.2(d)–(g) (*shall*) | On independence **730 is stricter than 1012** and simply unsatisfiable here. Do not adopt the aspiration |
| Organizational test policy and organizational test practices | 29119-1 §4.3.1.2; 29119-3 Annex A | The standard itself says these are "usually seen in… larger organizations running multiple projects"; organizational-level criteria are only `Should`, against `Shall` at project level |
| Full 29119-3 document set (15 items × 9 common elements incl. issuing organization, approval authority) | 29119-3 Clause 5 | §4.1.1 already exempts tool-held, combined information |
| Architecture boards, forums, design authorities, responsibility matrices, secretariats | 42020 §6.4.1 d)–j), §7.4.1 c)–d), Annex G.1 d) | Presuppose multiple parties with divergent authority. Note `board` appears in 42020 only in an **example** and an **informative annex** — never as a `shall` |
| Formal architecture description frameworks (ADFs) and viewpoint catalogues | 42010 §7.1; §5.4.2 | Scoped to domains like defence and banking, to normalize across a community. 42010 §6.6 NOTE 1: "This document does not require the use of any particular architecture viewpoints" |
| The full 42030 evaluation apparatus — customized framework, AE plan (15 `shall` items), AE report (22 `shall` items), three tiers | 42030 Clause 7, §8.2.1, §8.3.1 | Calibrated to a formal evaluation engagement; evaluator independence there is only a `may` (§8.2.3 k) |
| Formal measurement programme apparatus — measurement policy, budget allocation, the ~18-element measurement plan, the five-role model | 15939 §6.3.1, Annex F | **§1 (Scope, normative): the document "does not assume or prescribe an organizational model for measurement."** §6.3.1.2.1 names two minimum roles and then says the count "does not imply the specific number of actual roles" |
| PMBOK-style scheduling — earned value, resource levelling, critical path | 12207 §6.3.1.3 a)4) NOTE 6 points *outward* to ISO 21511 | The standards require a breakdown structure and a schedule; they do not import PMI practice. **24765 §3.4607: "work package" has no ISO/IEEE sense at all — it is PMBOK-only** |
| Stakeholder negotiation ceremony | 42010 §6.2–6.4; 29148 §6.4.3.4, §3.1.21 | 42010 §3.17 defines a stakeholder as a *role or position* — where one person holds every role this collapses to naming the roles occupied. With no second party the mediation apparatus is empty |
| Risk committees, enterprise risk management | 16085 §5.1.6 | 16085 **itself** disclaims being the enterprise instrument and defers organizational-level risk to ISO 31000 |
| Conformance-claim apparatus and tailoring ceremony | 29148 §4.2–4.5, Annex C; 42010 §4 (tailoring "neither required nor permitted") | Audit machinery. Note 29148 Annex C.2.3 NOTE 1: additional content is "always permitted" regardless |

**Two standards texts argue affirmatively for less, and both are worth keeping in view.**

- **32675 §6.3.1.3 b)4** (a normative task list) requires enabling "normalization of frequent change through compact low-dependency scopes, **low gates**, low overhead, and fast handoffs." A DevOps standard explicitly arguing against heavy gating is the clearest external warrant GZKit has for simplification.
- **12207 §4.3:** claiming "full conformance to a smaller list of processes" is often better than tailored conformance to a larger one. **Scope down the declared set rather than dilute each element.** For GZKit this reads directly as: fewer gates, honestly discharged, beats five gates recording exit codes.
- **32675 §5.4** and **§5.3.2**, and **12207 §4.2.1** (task lists demote to guidance under an outcome-conformance claim): one person may perform multiple processes; very small entities may operate without formal structures. There is no obligation to simulate organizational separation.
---

## 10. QUESTIONS REQUIRING HUMAN DECISION

Questions answerable from the repository have been answered above and are not repeated here. These seven are genuine engineering ambiguities where the evidence constrains the options but does not choose among them.

**Q1 — Was the deletion of requirements on ADR demotion intended?**
`gz adr demote` executes `shutil.rmtree(source_dir)` (`adr_demote.py:475`), which has removed 378 briefs carrying 1,986 REQs and 1,584 constraints. `docs/governance/pool-curation.md:47` rules that *"Deleting a retired pool file is an anti-pattern"* — but that ruling is about the **pool file**, not about the brief tree, and I found no ruling covering the latter. Either this is a deliberate decision that demoted work forfeits its specification, or it is an unexamined consequence. The answer determines whether the measurement program treats this as a defect or as a premise.

**Q2 — What is GZKit's product, and is the PRD retired or dormant?**
`PRD-GZKIT-1.0.0.md` describes a governance CLI shipped to other projects, with users, adoption friction and a graduate-course validation path. The repository's observable behaviour is a system whose primary user is its own operator. These imply different requirement sets. `FR-*` has not been cited since January and `AC-*` since ADR-0.1.0. Reviving the PRD, replacing it, or formally retiring it are all defensible; leaving it `Draft` and uncited is the one option that costs without paying.

**Q3 — Is the pool an intake, a graveyard, or a defect queue, and which should it stop being?**
204 entries; classification puts ~33% defects against shipped code and ~20% missing verification obligations, against ~11% actual architecture decisions. Architectural Boundaries 1 and 2 forbid promoting post-1.0 pool ADRs and forbid adding pool ADRs to the runtime track. Creation has stopped (81 in May, 1 in September) and promotion has effectively stopped (2 in four months). The 67 defects are real and currently unreachable by any repair route. Only the operator can rule whether they are abandoned, re-routed, or the boundaries relaxed.

**Q4 — What consequence scale should govern verification rigour?**
1012 Clause 5 makes it normative that rigour scale to integrity level, assigned recursively so that high-consequence parts are segregated. GZKit's lite/heavy lanes are a two-level scheme keyed to **surface kind** (CLI, API, schema = heavy), not to consequence. Defining consequence bands — what actually goes wrong, and how badly, when a given surface is wrong — is a judgment only the operator can make, and every proportionality question downstream depends on it.

**Q5 — Will an enforceable escalation threshold be accepted in place of the un-enforced IRON LAW?**
The operator-only-initiation rule appears in 12+ prose locations and no code, and the corpus records its own violation. 16085 §6.4.3.2 offers the alternative shape: a threshold defining what is "acceptable without explicit review by the stakeholders", in three bands. That is enforceable but is a *weaker* rule than a blanket prohibition, because it delegates below the line. This is a governance preference, not a technical finding.

**Q6 — Are handoffs working memory or an archive, and may they be compacted?**
758 documents, 2.63M tokens, ~9.5/day, 17 archived. They are demonstrably the sole custodian of live engineering facts. Compacting them risks losing exactly the material that is nowhere else; not compacting them guarantees the entry cost keeps rising. The answer depends on whether the durable facts get a home first — which is a sequencing decision.

**Q7 — Should `gz gates` and the five-gate covenant be reconciled, and in which direction?**
`gz gates` prints a deprecation notice on every run and is superseded by `gz closeout` (GHI #705), while AGENTS.md's Gate Covenant documents the deprecated verb. Gate 5 within it is `return True`. The covenant can be re-pointed at the real mechanisms (`gz closeout`, `gz obpi complete`), or the gate vocabulary can be retired in favour of what 24748-1 would call checks. Both are coherent; they are not the same project.

---

## 11. DOCUMENTATION ↔ IMPLEMENTATION DISAGREEMENT REGISTER

Reported as disagreements. **No authoritative side is chosen.**

| # | Documentation says | Implementation does | Evidence |
|---|---|---|---|
| 1 | AGENTS.md: "Every REQ… MUST declare exactly one of three kinds… via an inline tag `[kind]`" | 73% of REQs are untagged; `validate_req_kind.py:207-209` grandfathers all-untagged briefs; untagged REQs are **keyword-inferred** with a BEHAVIOR default (`req_kind.py:95-112`). Validator exits 0 | 667 of 3,105 REQs tagged; 397 of 556 briefs all-untagged |
| 2 | AGENTS.md: the REQ-coverage gate "cannot be waived" | 74 `obpi_completion_uncovered_accept` events exist, **6 typed `lite-auto`** with no human. The BEHAVIOR-specific fence landed later (GHI #537) and the event stream stops 2026-06-07 | Both true at different times; AGENTS.md states the post-fence rule as timeless |
| 3 | AGENTS.md Gate Covenant documents `gz gates` | `gz gates` prints a deprecation notice every run (GHI #705); `_run_gate_5()` returns `True` unconditionally; 0 gate-5 events exist | `gates.py:256-258`, `deprecations.py:41` |
| 4 | `.gzkit/manifest.json`: `gates.lite = [1,2]`, `gates.heavy = [1,2,3,4,5]` | AGENTS.md: "Gate 5 is universal… every lane". The real Gate 5 lives in `obpi_complete.py`, which the manifest does not model | — |
| 5 | `work-phases-and-airlock.md:5` (marked **BINDING**): the airlock's "enforcement teeth are the registered floor claim `airlock-in-unaccounted-seam`" | That claim unit-tests the pure `_decide` function against a synthetic seam; it touches no production call site. All six real call sites print and continue. ADR-0.33.0 is **Validated** with "§ Shortfalls: None" | `airlock/enter.py:158-170, 244-263`; `commands/airlock.py:14-18` states it honestly in code |
| 6 | `advisory-rules-audit.md:352` scores brief-reconcile **Mechanical** via `gz validate --brief-reconcile` | That scope is tier `explicit` and **never runs under `gz check`** | `validate_cmd.py:431-433`; `data/check_scope_membership.json: in_check: False` |
| 7 | `capability-control-review-2026-09-12.md:355` scores code-side jurisdiction "healthy and fail-closed" | Its sibling `health-audit-2026-09-12.md:267`: "An allowlist in prose does not prove least-privilege enforcement." No hook refuses an out-of-scope write | Two governance documents, 12 days apart, disagreeing |
| 8 | `obpi_precomplete.py:754-757` names `_enforce_adversarial_validation` as the chokepoint "which refuses EVERY refutation verdict" | That function has **no production call site**. The live path *computes* the verdict: `verdict="degraded-human-only" if tier==3 else "not-refuted"` — a caller can no longer record "refuted" through `gz obpi complete` | `obpi_complete.py:1030` |
| 9 | `gz-adr-evaluate/SKILL.md:57-69` mandates three-persona dispatch | `persona_dispatched` = **0 events across all 237 ADR evaluations**. The skill discloses this at `:81` — declared degradation, not hidden drift, but the mandate has never once been satisfied | 237 `adr_eval_completed`: GO 180, NO_GO 33, CONDITIONAL_GO 24; **0 GO below score 3.0, but 19 NO_GO at score ≥3.5** |
| 10 | `trust-doctrine.md:124`: the gate and receipt producer "cannot diverge by construction" | True for the 4 populated canonical step names. `behave`, `specreview`, `qualityreview`, `codexadversary` and `red` receipts carry **no command binding** (`arb/validator.py:279` returns `None` for unknown names) — and those are exactly the receipts cited as Gate-4 and Stage-4 evidence | — |
| 11 | AGENTS.md: "A fabricated receipt ID is a fabricated claim" | Backed by a real check for existence, exit status and canonical-command match — but the strongest form, `--attestation-receipts`, is opt-in and a **deliberate no-op** in the umbrella sweep | `governance/trust_audits/attestation_receipts.py:223-239` |
| 12 | `pool-curation.md:47`: "Deleting a retired pool file is an anti-pattern" | **13 of 34** promoted pool files were deleted | See Q1 |
| 13 | `docs/design/adr/pool/README.md` § Promotion step 5 prescribes `status: archived` with forwarding frontmatter | **1 of 204** files uses `archived`; 17 use `Superseded`, 1 `Promoted`. The README's promotion table lists 6; the ledger records 34 | Three conventions, one prescription |
| 14 | `chore-class-system.md:31` (operator): "A chore is authorized to find, analyze, solve and fix" | Same document, `:45`: "Nothing enforces any of it… Nothing schedules any chore." `registry.json` declares `staleness.periodDays` for 8 chores with no scheduler to read it. `owasp-top10-2025-scan` exists on disk and in a pool ADR but is absent from `registry.json` | 26 of 40 chores last ran 2026-07-31/08-01 |
| 15 | `src/gzkit/templates/agents.md:46` instructs agents to append to the insights ledger as a tracking route satisfying "Untrackable defect = nonexistent defect" | **Nothing reads the content of that file.** Every reader counts rows or shape-checks JSON. 164 `defect` records have no status field and no close path | `src/gzkit/insights/` |
| 16 | `build-to-1.0-campaign-2026-09-20.md:111`: "**Slim by design — and this time it is enforced.** … Completion narrative belongs in the ADR, the ledger, and the release notes — **not here**" | Movement A checkbox items run ~1,200–1,500 words each, carrying design rulings and `src/` file:line citations. The same passage notes the 06-30 edition "accreted 800-word completion prose… that hole is closed." It is not | 72.2% of the document is `## Amendments` |
| 17 | `obpi-decomposition-matrix.md` (Last reviewed 2026-03-04) prescribes `Foundation (0.0.x)` decomposition at "5+ OBPIs" | ADR-0.34.0 **closed** the foundation kind; `foundation-adr-registers-invariant.json:3`: "no new foundation ADR can be registered" | The matrix prescribes a procedure for a kind that cannot exist |
| 18 | `tests/AGENTS.md:169` and `.gzkit/rules/tests.md` Rule 39 present `@REQ-*` scenario tags as the heavy-lane BDD obligation | `briefs.py:600` accepts an `@covers` unit test as an equal substitute — **a heavy OBPI can pass the "BDD" gate with zero behave scenarios.** The docstring acknowledges this (GHI #636); the surface docs do not | — |
| 19 | `.gzkit/agents/roles.json:19,24` and `.codex/agents/spec-reviewer.toml:2` say "Read-only independent review" | `.claude/agents/*.md:3` says "cannot execute commands (GHI #968)". `codex_roles.py:59-62` syncs only `developer_instructions`, never `description` | Three surfaces, two descriptions |
| 20 | `qc_binding.py:86` declares Behave's binding as `"subprocess"` | Gate 4's runner does use a subprocess, but **34 of 58 step modules invoke the CLI in-process** via `main(args)` under `redirect_stdout`. ARB/QC evidence describing behave as subprocess-bound overstates the isolation | `features/steps/gz_steps.py:29-37` |
| 21 | AGENTS.md § Governance doctrine surfaces cites `--orphaned-implementation` in a list of mechanical scopes | The validator detects an OBPI with lock-claim + allowed-path edits + force-release and **no completion event** — a ceremony-completion check, not a check for implementation without a governing requirement | `governance/trust_audits/orphaned_implementation.py:1-20` |
| 22 | Doctrine treats `gz covers` and `gz drift` as the coverage surface | They report **different numbers**: 955 uncovered vs 713 unlinked, with no reconciling statement | Both run this session, exits 0 and 1 |

---

## 12. PROPOSED MEASUREMENT PROGRAM (M-A … M-H)

Derived strictly from Phase-1 findings. **Not executed.** Each item names the finding it follows from and the decision it would inform. The measurement program remains investigation and measurement; it proposes no implementation.

**M-A — Determine what a persistent requirement object would have to carry, by reading what the existing ones actually assert.**
*Follows:* §4.4, §6, and the 29148 §5.2.6 set-level gap. *Method:* classify a stratified sample of ~200 REQs and ~200 FAIL-CLOSED constraints against 29148 §5.2.5 (individual) and §5.2.6 (set) characteristics; measure how many would survive as system properties once separated from their work package, and how many are inherently transient acceptance criteria. *Decides:* whether the persistent layer is a subset of today's REQs or a different object. *Open risk:* the answer may be that most REQs are correctly transient and the persistent layer must be authored fresh — which is a materially different and larger finding.

**M-B — Recover and characterise the deleted specification corpus.**
*Follows:* Q1 and the 1,986 REQ / 1,584 constraint loss. *Method:* reconstruct the 378 deleted briefs from their parent commits; classify what was lost as durable vs transient; check whether any deleted REQ is still cited by live code, a live test, or a `@covers` annotation. *Decides:* whether the loss is recoverable, material, and whether it has already produced silent breakage.

**M-C — Measure whether the six intake surfaces can be reduced, by tracing where items actually go.**
*Follows:* §2 and the cross-surface conflation. *Method:* for a sample from each of pool ADRs, GHIs, insights, chores, campaign checkboxes and handoff next-steps, trace the item's end state; measure duplication across surfaces (the same concern filed in two places) and mortality (items that never move). *Decides:* which surfaces are load-bearing and which are accumulating. *Specifically resolve:* whether the 806-record insights ledger has ever changed an outcome.

**M-D — Name the claim behind each gate and each of the 89 enforcement claims, and find a non-agent witness.**
*Follows:* §8.2 and the project's own finding that 32 of 47 claims did not prove what they asserted. *Method:* express each gate and each registered claim in 15026-2 §5.3.3 form (property, limit, uncertainty, scope); identify which have a negative control that constructs a violation *of that claim*. *Critical constraint:* the prior audit disqualified its own method as "a stochastic surface auditing a stochastic surface." **The measurement program must first establish what a non-agent witness for this looks like, or declare the question unanswerable by agent labour.** This is the highest-risk item in the plan.

**M-E — Establish whether an architecture description is warranted, or whether correspondence methods alone suffice.**
*Follows:* §3 (42010) and the finding that decisions are indexed by *when* rather than *what*. *Method:* enumerate the concerns GZKit's 372 ADRs actually address; test whether they are coverable by a small viewpoint set; compare the cost of a minimal AD (42010 §6 kernel: entity, concerns, viewpoints, views, correspondences, known inconsistencies) against extending the existing `gz drift`/`gz covers` correspondence machinery to architectural obligations. *Decides:* whether ADD-an-architecture-description or REFINE-the-existing-correspondence-methods is the cheaper route to the same property. *Bias to declare:* the correspondence route is likely cheaper and should be tested first.

**M-F — Measure the real duplication between Gate 4 and Gate 2 before proposing removal.**
*Follows:* §8.3. *Method:* execute the behave suite with coverage instrumentation and compare the covered set against the unit suite's; identify precisely which scenarios cover code no unit test reaches; verify the 54 behave-only REQ count. *Decides:* what a Gate-4 retirement would actually cost. *Note:* 35 `@wip` scenarios in `brief_reconcile.feature` never execute and should be counted separately.

**M-G — Baseline the metrics that Phase 1 could only measure once.**
*Follows:* §8.2 and 15939 §6.2 b). *Method:* for each candidate measure, state the **information need and the decision it would support first**, then the measure — never the reverse. Candidates that passed Phase 1's need test: OBPI duration distribution (decides work-package sizing); brief-reconcile drift rate post-fix (decides whether jurisdiction is knowable in advance); REQ coverage split by kind (decides where proof channels are failing); fix:feat ratio (decides whether repair load is rising); agent entry token cost (decides what to trim); RED receipt class distribution (decides whether falsifiability is improving). Candidates that **failed** the need test and should not be adopted: `obpi_lock_ttl_warning` (no reader, measures session restarts), handoff count, validator count, total REQ count. *Explicitly:* propose no measure whose information need cannot be stated in one sentence.

**M-H — Define consequence bands with the operator.**
*Follows:* Q4 and 1012 Clause 5. *Method:* a structured session enumerating what goes wrong when each major surface is wrong, and how badly. *Decides:* the input every proportionality question in Phase 3 would need. *Cannot be done by an agent alone* — this is a judgment about consequence, and the operator holds it.

**Sequencing note.** M-A, M-B and M-C are independent and can run concurrently. M-D is gated on resolving its own method problem first and should not be started until that is settled. M-E depends on M-A (what a persistent object carries determines what an architecture description would need to correspond to). M-G depends on M-H for the consequence-scaled measures. M-F is independent and cheap.

**What the measurement program should not do.** Not propose a replacement backlog taxonomy, a new lifecycle, a requirements-as-code implementation, or any new tooling. Phase 1 found a system that already contains most of the mechanisms it needs — correspondence methods, falsifiability witnesses, declared undeveloped arguments, a working ledger — and whose problem is that persistent knowledge has no owner and known gaps have no retirement path. **Adding machinery is the failure mode most consistent with this repository's history.** 12207 §4.3 states the alternative directly: prefer full conformance to a smaller declared set over tailored conformance to a larger one.
