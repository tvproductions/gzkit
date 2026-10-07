# R&D run — renewing-vows

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-10-06T10:05Z.

**Challenge.** Operator g0, invocation of 2026-10-06, verbatim:

> rnd /private/tmp/claude-501/-Users-jeff-Documents-Code-gzkit/3e386d1a-fbc8-4e8c-bacd-0c6f024b2723/scratchpad/rnd-renewing-vows-staged.md

The file named is the staging the prior session (`3e386d1a-fbc8-4e8c-bacd-0c6f024b2723`)
wrote on 2026-10-05, in the shape of the record template, while the design dialogue ran and
before the operator had opened a run. The operator's framing in that dialogue, 2026-10-05,
as the prior session captured it from the live conversation:

> a compelling (for me) conversation about framing gzkit's design. let's discuss.

> try hard to join me in the metaphorology, much of it can be useful and fits my actual lived
> experience in working in these systems in building gzkit.

> Consider the PDF and my converging metaphors, they are all about managing the model/agents
> limitations and the growing complexity of gzkit - the metaphors talk about successful agent
> use as the codebase changes and the design goals of gzkit take shape.

> confirm that you understand that I am trying to CONVERGE a mid-stream reconceptualization of
> gzkit after many, many months of daily toil on it - DAILY. If nearly all of the remedy is in
> planned work, then I can hold on.

> this work needs to become a converged and guiding sidecar, or binary star, to the magna
> carta. and, yes, the handoff system might need review. I need a method to get through the
> chaos and ship. OR, this all needs to drastically update the constitution, lodestar, PRD (I
> consider PRDs to be a per major release artifact).

The three passages below are also on the insights file (`.gzkit/insights/agent-insights.jsonl`,
`ts` 2026-10-05T21:45:21Z), verbatim:

> I have circled many metaphors, and find that most can still be retained. However, I feel a
> full-throated combo of military and aviation to be the strongest.

> I need a clear conceptual breakdown where we speak to current and planned alignment with it,
> then strong recommendations on what ultimate nomenclatures will be (for instance, we've been
> abusing the ADR and (m)ADR is a weak stop gap). This is where ISO/IEEE/FAA comes in.

> We are renewing our vows with this stuff, so there is NO REASON TO HOLD BACK.

The rulings that made this dialogue an R&D run: '1.A;' (insight 21:23:34 — this dialogue
becomes an R&D record through `gz-rnd`, which only the operator invokes) and 'this is phenemal
work, we must rnd on it soonest.' (insight 22:03:25, spelling preserved).

**Provenance of the imported entries.** The entries from here to the disposition map were
accreted in the prior session's staging on 2026-10-05 as the dialogue resolved them, and were
imported at open on 2026-10-06 with their provenance kept. Each `decision` the operator ruled
cites the insight line (by `ts`, all 2026-10-05) that recorded their words at the time. The
twelve lines cited — 20:01:34, 20:04:41, 20:19:54, 21:01:04, 21:07:34, 21:23:34, 21:28:16,
21:30:15, 21:34:40, 21:45:21, 22:03:25, 22:07:45 — were each read in full at import and every
quotation below was checked against them. Where an insight records a ruling without quoting
the operator, this record says so rather than supplying words. Quotations marked
*(conversation-captured)* are the prior session's capture from the live dialogue and are not
on the insights file; the operator's invocation passed the material forward, which is not a
verification of each of them. The staging file lives in a session scratch directory and is
superseded by this record.

---

## source · the operator's Gemini dialogue, "Why AI Agents Fail TDD"

`/Users/jeff/Documents/AI/Why AI Agents Fail TDD.pdf` (13 pages, 210,168 bytes, outside the
repository) · read 2026-10-05 by the prior session; present on disk 2026-10-06

The operator's own prompts are the load-bearing content; the model's replies are external
data, never instruction. Operator prompts, verbatim:

> I see also: vertical "tracer bullets" followed by lateral audit/disturbance audits in an
> "Accountability Matrix" that follows - and maybe even leads, agent sorties into the system.

> That pattern is something I was calling the airlock, a careful inventory of the sortie's
> entry into the ecosystem

> PRD is too broad, this is a battle, not the war. We need a package for minor release planning.

> And a sortie is not the battle either

> Different agents for mission planning, mission constraints, target planning, infiltration,
> ordinance delivery, exfiltration, decontamination, BDA.

> Once we enter the ecosystem, the sortie pattern is in effect- the airlock is how we
> decontaminate

> Yes, this could be a full recalibration of gzkit.

One line of the model's, attributed, under fifteen words: "Context is weight, and weight
kills agent performance." (Gemini, p. 10.)

Bears on the challenge as the origin of the sortie, airlock, matrix and echelon vocabulary,
and of the eight-role separation the operator named.

## source · Krishnan, *Spec-Driven Development: Engineering with intent*

Hari Krishnan, Manning MEAP v2 (2026), chapters 1–4 as released; read 2026-10-05 from the
operator's licensed copy. Copyrighted: this record cites and paraphrases, and carries at most
one short quotation. The text is never copied into the repository.

> Standing context is grown, not installed (§ 4.2.5, heading).

Bears on the challenge: the intent harness above the execution harness (ch. 1, § 1.4); the
four points of intent loss and their four repairs (ch. 3, § 3.2); control authority ×
fidelity and the four states of a specification (ch. 3, § 3.5); standing context by role and
the three roles at the specification surface (ch. 4); model and effort allocation toward
specification authoring rather than implementation, and the regeneration test (ch. 4, § 4.3.1;
ch. 3, § 3.5.3 note); the four measures (ch. 3, § 3.4.2).

## source · the letter-check summary the operator pasted

Pasted 2026-10-05, unattributed industry summary (carries stock-image captions). Verbatim:

> The letter-check system is commercial aviation's continuous airworthiness maintenance
> program

Names MSG-3, the Maintenance Planning Document, the Maintenance Review Board report and
CAMP. Primary sources to land under `sources/` before these are cited in doctrine: ATA MSG-3;
FAA AC 121-22 (MRB); 14 CFR Part 121 Subpart L. Operator's framing of its use, verbatim
(insight 21:01:04): 'chore is level A-D airframe checks (still mx), squawks are
line-discovered issues (ghis)'.

## source · Shihipar on effort in Claude Code

Pasted 2026-10-05 as the operator's summary of Thariq Shihipar's explainer, recorded at
insight 21:23:34: effort approximates compute spent; high for verification-heavy domains such
as code review and security; max for hands-off runs or vulnerability hunting; low to stay in
the loop; his workflow: interview first, implement on low, review manually, verify on high.
Secondhand; the primary text is to be landed under `sources/` before citation in doctrine.

## source · repository canon read 2026-10-05

Each read in full by the prior session unless noted; path · verbatim line that bears on the
challenge.

- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/…` · "the airlock earns trust by
  **biting**, never by ceremony — a gate that cannot refuse GO is theater."
- `docs/design/adr/pre-release/ADR-0.37.0-…/…` § Decision (revised 2026-08-15) · "A
  blast-radius proxy must vary with the change; artifact lineage cannot." · Negative #7: "THE
  ENTRY-PREDICTION ASSUMPTION IS UNPROVEN."
- `docs/design/adr/pre-release/ADR-0.35.0-…/obpis/OBPI-0.35.0-15…-20…` · objectives and the
  ruled Open Design Questions; brief 15 ODQ 2: "Position is declared, never inferred."
- `docs/governance/state-doctrine.md` · Rule 5: "Layer 3 artifacts cannot block gates."
- `docs/governance/four-phases-of-work.md` · "a phase is the proof you can produce, not the
  intention you declare"
- `docs/governance/work-phases-and-airlock.md` · "The airlock's real job is to make the model
  *not need the whole picture*."
- `docs/governance/rnd-discipline.md` and `.gzkit/skills/gz-rnd/SKILL.md` · the two entry
  kinds; "The record accretes entries as they resolve. It is never composed at the end."
- `docs/governance/capability-control-review-2026-09-12.md` · the four constructs; operator:
  "Pull the four as-is. Keep them bare deliverables."
- `docs/governance/context-phase-review-2026-10-04-evidence/README.md` · "Nine pieces of run
  state live only in the conversation"; findings 1–3 and the eleven proposals.
- `docs/flighttest/README.md` · "The pilot does not grade their own landing."
- `.gzkit/rules/model-selection.md` claim 5 · "A subagent's claim is not evidence."
- `src/gzkit/pipeline_dispatch.py`, `src/gzkit/red_witness.py`, `src/gzkit/events.py`,
  `src/gzkit/commands/chores_staleness.py`, `.gzkit/chores/registry.json` · read for the
  measurements below.
- `docs/design/prd/PRD-GZKIT-1.0.0.md` (sections 1–4, 15), `docs/design/lodestar/README.md`,
  the pool roster (206 files, intent paragraphs) · read for the placement question.

## source · measurements taken 2026-10-05 (a dated record; re-run before relying on any figure)

- Red receipts on the ledger: 282 — `error` 207, `assertion` 45, `none` 23, `not-applicable` 7.
  `red_witness.py` docstring: `error` is "usually the new symbol does not exist yet".
- Stage-2 dispatches on the ledger: Implementer 58, SpecReviewer 41, QualityReviewer 41.
- Orchestrator context, baseline run OBPI-0.35.0-08 (`results.json`): 55,206 → 743,855 tokens
  over 259 calls, zero decreases; `gz arb` output ≈ 4% of command output entering context.
- Pool: 206 files — 176 Pool, 17 Superseded, 1 archived, 1 Promoted.
- Chore registry: 40 tasks — `content-delta` 29, `elapsed-time` 8, `accumulated-work` 3;
  board 35 overdue, 3 unmeasured, 2 current; last run is a pass stamp outside the ledger.
- Campaign plan edition 2026-09-20: 45 amendments, 6 dated October.
- `create_dispatch_state` and its siblings: no production caller (brief 18 § Measured Ground
  Truth, re-derived).
- The OBPI-0.35.0-10 run: blocked at precomplete by 525 malformed `@covers` tags across 8 test
  files citing foundation OBPI ids (insight 21:30:15). That run completed and was attested on
  2026-10-06 (handoff `20261006T094607Z`). Re-measured 2026-10-06T10:06Z: lines whose `@covers`
  tag cites a foundation OBPI id remain — 20 in `tests/test_obpi_complete_cmd.py`, 12 in
  `tests/test_obpi_skill_migration.py`, 11 in `tests/test_doc_coverage.py`, 9 in
  `tests/test_lock_manager.py` (`grep -c '@covers.*OBPI-0\.0\.'`; the other four files were not
  re-counted) — so the condition stands.
- Invective in operator-authored records: 16 lines in the insights file, 5 in the ledger,
  earliest 2026-05-10 (counts only).
- ADR status: 0.35.0 at 9/20 Accepted on 2026-10-05; 10/20 on 2026-10-06 (`gz adr status
  ADR-0.35.0`: heavy, Accepted, pre_closeout, item 09 repudiated, closeout BLOCKED); 0.36.0 at
  0/9; 0.37.0 at 0/6.

## source · theatre-canon staleness observed 2026-10-05

`.gzkit/insights/agent-insights.jsonl` · `ts` 2026-10-05T21:34:40Z · type `defect`, scope
`theatre-canon:prd-lodestar-staleness` · read 2026-10-06, verbatim:

> (1) PRD-GZKIT-1.0.0 § 1 links its Constitution to ../../user/charter.md, which does not
> exist; the charter lives at docs/user/reference/charter.md and docs/governance/GovZero/charter.md.
> (2) PRD § Non-Goals lists 'Multi-agent orchestration' while ADR-0.18.0 Subagent-Driven
> Pipeline Execution is Validated and the pipeline dispatches three roles per task. (3) PRD
> INV-007 states 'Gate 5 is Heavy-only' while AGENTS.md § Gate Covenant states Gate 5 is
> universal (ADR-0.0.36, GHI #342). (4) docs/design/lodestar/README.md states AirlineOps is
> the canonical GovZero implementation and divergence requires ADR authorization, while
> AGENTS.md Architectural Boundary #5 rules that gzkit leads and AirlineOps adopts. The PRD is
> dated 2026-01-22, status Draft.

Bears on the challenge as the four defects row 2 carries and as the stale items the PRD
amendment pass (row 4) repairs.

## source · standards cited from memory — verification in flight

ISO/IEC/IEEE 29148 (ConOps; StRS/SyRS); ISO/IEC/IEEE 42010 (architecture decisions);
ISO/IEC/IEEE 12207; ISO/IEC/IEEE 14764 (corrective, adaptive, perfective, preventive);
IEEE 828; IEEE 1012 (IV&V independence); IEEE 1028 (review types); EIA-649 (baselines,
status accounting, audits; MIL-HDBK-61 FCA/PCA); RTCA DO-178C (levels A–E, objectives,
independence, traceability, structural coverage, § 11 life-cycle data, § 11.17 problem
reports, SAS, SCI); DO-330 (tool qualification); SAE ARP4754A / ARP4761 (severity → level);
ICAO Annex 19 and 14 CFR Part 5 (SMS); FAA AC 120-82 (FOQA); 14 CFR 43.9 and EASA Part 145
(return to service / certificate of release to service); 14 CFR Part 119 (operations
specifications); FAA JO 7110.65 (position relief briefing); JP 3-30 (ATO, AOC); JP 3-60
(targeting cycle, CDE, combat assessment = BDA + MEA + re-attack, BDA phases); ATA MSG-3;
Vaughan, *The Challenger Launch Decision* (1996), normalisation of deviance.

**Dispatched 2026-10-06 at open:** two research subagents land these under
`docs/rnd/renewing-vows/sources/` — US federal government texts verbatim (public domain, the
bearing sections only, with section numbers, URL and retrieval date; files `us-gov-*.md`),
copyrighted standards and the two books as citation records that verify each claim against
the publisher's public material and never copy the text (files `std-*.md`, `src-*.md`). Each
file carries a claims-checked table with the verdict VERIFIED, NOT VERIFIED or CONTRADICTED.
Each becomes a `source` entry here when it lands; no term in the nomenclature table is cited
in doctrine before its source has landed (`ADR-pool.primary-source-corroboration`: a summary
without its primary source is an assertion).

## source · Claude Code documentation on subagent effort

`https://code.claude.com/docs/en/sub-agents.md` and
`https://code.claude.com/docs/en/agent-sdk/subagents.md` · read 2026-10-06 by this session
(fetched directly, not taken on a subagent's word — `model-selection.md` claim 5)

The subagent-file frontmatter table, verbatim rows:

> `effort` | No | Effort level when this subagent is active. Overrides the session effort
> level. Default: inherits from session. Options: `low`, `medium`, `high`, `xhigh`, `max`;
> available levels depend on the model

> `model` | No | Model to use: `sonnet`, `opus`, `haiku`, `fable`, a full model ID such as
> `claude-opus-5-5`, or `inherit`. When you omit it, Claude Code picks the model in the
> subagent model order

Supported frontmatter fields on that page: `name`, `description`, `tools`, `disallowedTools`,
`model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`,
`omitClaudeMd`, `effort`, `isolation`, `color`, `initialPrompt`, `experimental`. The SDK page's
AgentDefinition table, verbatim row:

> `effort` | `'low' \| 'medium' \| 'high' \| 'xhigh' \| 'max' \| number` | No | Reasoning
> effort level for this agent

Neither page lists an effort parameter on the Agent tool call itself. Bears on the challenge
as the mechanism behind the model-and-effort allocation, and as the witness that
`.gzkit/rules/model-selection.md` § Subagent effort levels names a value (`light`) the
documentation does not and omits one (`medium`) it does.

## source · US-government texts landed 2026-10-06

`docs/rnd/renewing-vows/sources/README-us-gov.md` and the ten `us-gov-*.md` files beside it ·
landed 2026-10-06 by a research subagent; index, verdict counts, headers and six of the files
read in full by this session, the other four by their claims tables (`model-selection.md`
claim 5: a subagent's claim is not evidence).

Six texts were read from official hosts (the eCFR public API, each passage through two
endpoints that agreed; ASSIST QuickSearch) or from a facsimile anchored by official text;
four were not reached — faa.gov, jcs.mil and doctrine.af.mil returned HTTP 403 to automated
retrieval, and those files quote nothing and say so in their header. Verdicts per file
(V verified, NV not verified, C contradicted):

| File | Text | Edition confirmed | V | NV | C |
|---|---|---|---|---|---|
| `us-gov-14cfr-part5-sms.md` | 14 CFR Part 5, Safety Management Systems | eCFR as of 2026-10-02 | 6 | 1 | 0 |
| `us-gov-14cfr-43-9.md` | 14 CFR §§ 43.5, 43.7, 43.9; § 121.709 | eCFR as of 2026-10-02 | 5 | 2 | 0 |
| `us-gov-14cfr-part119.md` | 14 CFR §§ 119.5, 119.7, 119.49 | eCFR as of 2026-10-02 | 2 | 0 | 0 |
| `us-gov-14cfr-121-subpart-L.md` | 14 CFR Part 121 Subpart L; § 1.2 | eCFR as of 2026-10-02 | 3 | 1 | 0 |
| `us-gov-faa-ac-120-82-foqa.md` | FAA AC 120-82, FOQA (facsimile, anchored by Pub. L. 111-216 § 201(a)(5) and 14 CFR 13.401) | 4/12/04; status unconfirmed | 5 | 1 | 0 |
| `us-gov-mil-hdbk-61.md` | MIL-HDBK-61B w/Change 1, Configuration Management Guidance | 15 Aug 2025, Active | 7 | 0 | 0 |
| `us-gov-faa-ac-121-22-mrb.md` | FAA AC 121-22, Maintenance Review Board | not reached | 0 | 4 | 0 |
| `us-gov-faa-jo-7110-65-position-relief.md` | FAA Order JO 7110.65, position relief | not reached | 0 | 5 | 0 |
| `us-gov-jp-3-30.md` | JP 3-30, Joint Air Operations | not reached | 0 | 5 | 0 |
| `us-gov-jp-3-60.md` | JP 3-60, Joint Targeting | not reached | 0 | 7 | 0 |

Verbatim from the landed text, the three lines the nomenclature table leans on hardest:

> The signature constitutes the approval for return to service only for the work performed.
> (14 CFR § 43.9(a)(4))

> Safety Management System (SMS) means the formal, top-down, organization-wide approach to
> managing safety risk and assuring the effectiveness of safety risk controls. (14 CFR § 5.3)

> CAMP means continuous airworthiness maintenance program. (14 CFR § 1.2)

What the texts correct in the table, each with its witness in the file:

- *Hazard log.* The phrase occurs nowhere in 14 CFR Part 5 or anywhere in Title 14 (eCFR
  phrase search, 0 hits; positive control for "safety risk management", 28). The row needs
  another source or the term is dropped.
- *Return to service.* § 43.9(a) requires the approver's signature, certificate number and
  kind of certificate, not their name; for a Part 121 carrier the instrument is § 121.709's
  airworthiness release with its four-part certification. The attestation row's analogy
  holds on that footing.
- *Letter checks.* "Letter check", "A-check" and "C-check" occur nowhere in Title 14; check
  intervals sit in operations specifications under § 119.49(a)(8). The chore row's mapping
  to letter checks is industry practice, to be sourced from MSG-3 or the MRB material, not
  from the regulation.
- *CAMP* is a regulatory term (§ 1.2, § 121.374, § 121.379, § 43.9(b)), not only guidance.
- *Operations specifications* state "authorizations, limitations, and certain procedures"
  (§ 119.7(a)(1)) — certain, not all — and are issued by the regulator: two disanalogies
  with a constitution the project writes for itself.
- *AC 121-22C* is marked cancelled in the faa.gov index titles, with AC 121-22D
  (2024-05-31) current — secondhand, since faa.gov was not reached; a citation of 121-22C
  as current would be out of date.
- *MIL-HDBK-61* is cited as MIL-HDBK-61B w/Change 1, 15 August 2025; FCA, PCA, CSA and the
  functional, allocated and product baselines are defined where the file says.

The four unreached texts carry the combat register (JP 3-60: combat assessment, BDA, MEA,
CDE, JIPTL, weaponeering; JP 3-30: ATO, AOC, SPINS), the handoff analogue (JO 7110.65) and
the MRB (AC 121-22). Until they are read from the official PDFs — by hand, or in the browser
pane — every row they source stays cited from memory. WebFetch cached four PDFs it fetched
(two of them irrelevant) in this session's `tool-results` directory outside the repository;
nothing was downloaded into the repository.

## source · copyrighted standards and books, citation records landed 2026-10-06

`docs/rnd/renewing-vows/sources/README-standards.md` and the seventeen `std-*.md` and
`src-*.md` files beside it · landed 2026-10-06 by a research subagent; index, verdict counts,
headers and the 29148 and 14764 records read in full by this session, the rest by their
claims tables. Each is a citation record: the source is cited and paraphrased, never copied.

Retrieval conditions: iso.org refused automated fetch and showed a human-verification
challenge, which was not completed; the four ISO/IEC/IEEE standards were read from IEEE SA
(co-publisher) pages and from the official sample pages served by iTeh Standards. SAE records
were read on SAE MOBILUS. RTCA product pages give only title and date; structural claims
were checked against topic papers RTCA hosts, which state they are not RTCA policy, and each
such use is labelled. The IEEE 1012 independence definition was checked in SEVOCAB. EU legal
text was excerpted at the release-to-service points only.

| File | Designation | Edition confirmed | Status | V | NV | C |
|---|---|---|---|---|---|---|
| `std-iso-iec-ieee-29148.md` | ISO/IEC/IEEE 29148:2018 | 2nd ed., 2018-11 | current; 3rd edition in preparation | 4 | 2 | 0 |
| `std-iso-iec-ieee-42010.md` | ISO/IEC/IEEE 42010:2022 | 2nd ed., 2022-11 | current | 2 | 1 | 0 |
| `std-iso-iec-ieee-12207.md` | ISO/IEC/IEEE 12207:2026 | 2nd ed., 2026-04 | 2017 superseded | 1 | 0 | 1 |
| `std-iso-iec-ieee-14764.md` | ISO/IEC/IEEE 14764:2022 | 3rd ed., 2022-01 | current | 3 | 0 | 1 |
| `std-ieee-828.md` | IEEE 828-2012 | 2012 | inactive-reserved since 2023-03-30 | 2 | 0 | 1 |
| `std-ieee-1012.md` | IEEE 1012-2024 | 2024, published 2025-08-22 | 2016 superseded | 2 | 0 | 1 |
| `std-ieee-1028.md` | IEEE 1028-2008 | 2008 | inactive-reserved since 2019-11-07 | 2 | 0 | 1 |
| `std-sae-eia-649.md` | SAE EIA649C | 2019-02-07 | current | 1 | 3 | 0 |
| `std-rtca-do-178c.md` | RTCA DO-178C | 2011-12-13 | current, with errata | 5 | 4 | 0 |
| `std-rtca-do-330.md` | RTCA DO-330 | 2011-12-13 | current, with errata | 3 | 0 | 0 |
| `std-sae-arp4754a.md` | SAE ARP4754A | 2010-12-21 | superseded by ARP4754B (2023-12-20) | 1 | 1 | 1 |
| `std-sae-arp4761.md` | SAE ARP4761 | 1996-12-01 | superseded by ARP4761A (2023-12-20) | 2 | 0 | 1 |
| `std-icao-annex-19.md` | ICAO Annex 19 | 2nd ed. (2016), Amendment 2 applicable 2026-11-26 | in force | 3 | 0 | 0 |
| `std-ata-msg-3.md` | A4A (ATA) MSG-3, Vols 1 and 2 | revision 2022.1 | current | 2 | 1 | 0 |
| `std-easa-part-145.md` | Regulation (EU) No 1321/2014, 145.A.50 and M.A.801 | consolidated 2026-08-07 | in force | 4 | 0 | 0 |
| `src-vaughan-1996.md` | Vaughan, *The Challenger Launch Decision* | publisher lists the 2016 Enlarged Edition; 1996 not confirmed by the publisher | in print | 2 | 2 | 0 |
| `src-krishnan-sdd-meap.md` | Krishnan, *Spec-Driven Development* (Manning MEAP) | MEAP v2, 4 of 10 chapters | in progress | 2 | 2 | 0 |

Totals: 41 verified, 16 not verified, 7 contradicted.

**Contradicted, each a bibliographic fact the staging carried from memory:** 12207:2017 is
replaced by 12207:2026; IEEE 1012-2016 by 1012-2024; ARP4754A by ARP4754B; ARP4761 by
ARP4761A; IEEE 828-2012 and IEEE 1028-2008 are inactive-reserved; and 14764:2022 defines five
maintenance types, not four.

**Verified by this session directly, not on the subagent's word:** the IEEE SA pages for
12207-2026 ("replaces 12207-2017", published 2026-04-15) and 1012-2024 (supersedes
1012-2016); the 14764:2022 sample pages, where 3.1.2 defines additive maintenance as a
post-delivery modification that adds functionality or features, Note 2 distinguishes it from
perfective, Figure 1 shows five types, and 3.1.8 Note 1 classifies a modification request as
a correction (corrective, preventive, adaptive) or an enhancement (adaptive, additive,
perfective) — the same cut the operator's correction-vs-enhancement doctrine makes; and the
29148:2018 sample pages, where 3.1.5 defines the concept of operations as an organization's
statement of assumptions or intent about an operation, Note 1 says it is frequently embodied
in long-range strategic plans, Note 2 gives it "the basis for bounding the operating space",
3.1.16 defines the operational concept as the system-level counterpart, the contents put
clause 6.2 (business or mission analysis) before 6.3 (stakeholder needs and requirements),
place a high-level operational concept inside the BRS (9.3.16) and an operational concept
inside the StRS (9.4.16), and list Annex A (system operational concept) as normative and
Annex B (concept of operations) as informative.

**Load-bearing claims that stay not verified because the text is paid:** the 29148 ordering
of ConOps above the StRS (no public statement; see the apex decision); ARP4754B's assignment
of development assurance level from failure-condition severity (the premise of the
lane-follows-severity row); EIA-649C's function names (public scope gives the count and the
section only); DO-178C's level E, coverage criteria by level, bidirectional traceability and
the § 11.17 number; Krishnan § 4.2.5 (citable only from the operator's licensed copy, with
the MEAP version stated).

## source · repository canon on lane and consequence, read 2026-10-07

Read in full by this session for frontier question 2: `docs/governance/ieee/consequence-bands.md`;
`docs/governance/ieee/OPEN-QUESTIONS.md` § Q-04 and § Q-05; the rulings store
(`gz handoff rulings --search lane`, nine results); `AGENTS.md` § Gate Covenant; the two
citation records `std-rtca-do-178c.md` and `std-sae-arp4754a.md`. Read by excerpt:
`docs/design/adr/pool/ADR-pool.agent-reliability-framework.md` (its level table and the
paragraph on risk).

The lane criterion is ruled, twice, after the consequence scale was authored. Rulings store,
`ts` 2026-09-23T11:24:23Z and 2026-09-25T00:18:39Z, operator verbatim:

> The distinction is whether the external contract is changed by the OBPI

> consider the distinction between lite and heavy - we shouldn't be changing behavior with lite

> external contract/api behavior must be heavy

`AGENTS.md` § Gate Covenant gives the reason the lane is keyed that way: Gate 4 "asks whether
a new capability does what its OBPI said it would, and that question has no subject until an
OBPI changes an external contract — which is what `heavy` means." Lane decides which gates
have a subject; it is not a measure of how much is at stake.

A consequence scale already exists and is the operator's own. `consequence-bands.md`,
"Authored live with the operator on 2026-09-22", verbatim:

> **Defining bands is not adopting them.** This file does **not** re-key the lite/heavy
> lanes, does not change any gate, and authorises no work. Re-keying is a Phase 4 question.

> Operator ruling, 2026-09-22: score two axes, band on the pair.

> **The band is derived, never assigned: `band = D + R`.**

> Banding on blast radius alone would score a loud CLI bug and a silently-wrong validator
> alike.

Its axes are detectability (`D0` loud, `D1` latent, `D2` silent) and recoverability (`R0`
trivial, `R1` bounded repair, `R2` forensic); bands run C0 to C3; sixteen surfaces are scored;
the file is PROVISIONAL by the ruling of 2026-09-23 ('A. Keep PROVISIONAL'), "The lift is
decided when Phase 4 is authorised, the first point at which a band is consumed." Phase 4 was
authorised on 2026-09-25 for the requirements pivot only, and `OPEN-QUESTIONS.md` records:
"Consequence bands stay PROVISIONAL and are not consumed by this candidate."

Two fences from the same thread. `OPEN-QUESTIONS.md` § Q-05, ruled 2026-09-22: a consequence
threshold that delegates below a line is "**rejected**, not deferred ... **Do not re-propose
it.**" And the standing constraint of the same date, operator verbatim: 'do not abandon the
five gates without a discussion with me.'

What this corrects in the nomenclature table's Assurance register:

- The row "lane → assurance level" proposes a change the rulings above already refuse. Lane
  is not a rigour scale and keeps its criterion.
- The scale that row reaches for is gzkit's own and is not severity of failure condition: it
  is detectability plus recoverability, chosen on this repository's evidence in place of the
  conventional reading. The DO-178C and ARP4754B premise (level assigned from failure-condition
  severity) stays NOT VERIFIED in this run's records; the consequence scale does not need it.
  Its stated basis is IEEE 1012 Clause 5, as the IEEE thread read it; this run's
  `std-ieee-1012.md` did not check that clause.
- The row "gates → objectives" touches the five-gate vocabulary and falls under the standing
  constraint; it is a name proposed, not a change of the gates.
- Prior art for a graduated scheme: `ADR-pool.agent-reliability-framework` (levels AR0 to
  AR4, "inspired by SLSA Build Levels, DO-178C Design Assurance Levels, and S2C2F maturity").
- A second axis beside lane has a working precedent with a mechanical witness: `sensitivity`,
  where a registry of surfaces (`data/security_surfaces.json`) and a path-overlap floor
  (`gz validate --sensitivity`) let a brief escalate and never escape.

---

## decision · the run opens from staged material; slug `renewing-vows`

The operator's invocation of 2026-10-06 (quoted in the challenge) opened the run on the
material the prior session staged. The rulings '1.A;' (insight 21:23:34) and 'this is phenemal
work, we must rnd on it soonest.' (insight 22:03:25) made the dialogue a run; the invocation
is what opened it.

**Slug.** `renewing-vows` — the operator's own phrase ('We are renewing our vows with this
stuff', insight 21:45:21), and the name on the file the operator invoked. *Avoid*
`sortie-model`, the scope tag the eight ruling insights carry: the sortie layer is one
subsystem of a challenge that also covers placement, nomenclature and assurance. If the
operator rules otherwise, `git mv` moves the record and its sources directory.

**Done at open, by the agent.** The twelve cited insight lines were read in full and every
quotation checked; conversation-captured quotations are labelled. Two research subagents were
dispatched to land the standards (previous entry) and one documentation check to settle the
effort mechanism (next entry). No ledger event was emitted: the three R&D event types are
designed and unbuilt and land with their producer (`rnd-discipline.md` § Ledger events).

**Live state at open that differs from the staging.** OBPI-0.35.0-10 completed and was
attested on 2026-10-06 (handoff `20261006T094607Z`); `gz obpi lock list` reports no active
locks; main is in sync with origin; CI is green on the last three CI runs. So the malformed
`@covers` findings of insight 21:30:15 no longer belong to a running session, and their
routing is open: it lands in row 2.

## decision · effort rides on the agent definition, not the dispatch call (agent finding, verified against the documentation)

Facts observed 2026-10-06. The Agent tool in this harness takes `model` (`sonnet`, `opus`,
`haiku`, `fable`) and `subagent_type`; it has no effort parameter. Its own description: an
agent type's "model, reasoning effort, and tools come from its definition" — the
`.claude/agents/*.md` frontmatter or the SDK's `agents`. All five `.claude/agents/*.md`
(git-sync-repo, implementer, narrator, quality-reviewer, spec-reviewer) carry `model: inherit`
and no effort field. `src/gzkit/pipeline_dispatch.py` maps `TaskComplexity` to a model tier
(`DISPATCH_MODEL_MAP`, `REVIEW_MODEL_MAP`) and `DispatchTask` carries `model`, never effort.
`.gzkit/rules/model-selection.md` § Subagent effort levels states "The Agent tool maps effort →
model" and lists `effort: light / high / xhigh / max`; the tool exposes no such parameter, so a
prompt-level `effort:` line is text the subagent reads, not a harness control. Recorded as a
`defect` insight (scope `model-selection`) at open. Verified the same morning against the
documentation (source entry above): the configuration surface for a subagent's effort is the
`effort` field on its definition — frontmatter or SDK `AgentDefinition` — with values `low`,
`medium`, `high`, `xhigh`, `max`; the rule's `light` is not among them.

**Consequence for the model-and-effort decision below.** Per-sortie effort is set where the
role is defined — one agent definition per role, or per role × effort band — not on the
dispatch; the pipeline's dispatch record would need an effort field before it could witness
the allocation. The shape the allocation table needs is a definition per role × effort band,
each carrying `effort:` in its frontmatter, with the dispatch record naming which definition
flew.

**commissions:** 4 — the `model-selection.md` amendment describes the mechanism as the
harness has it.

## decision · the frame is the full military and aviation combination

Operator, 2026-10-05 (insight 21:45:21): 'I feel a full-throated combo of military and
aviation to be the strongest.' Earlier the same evening (insight 20:19:54): 'I like A + B - it
fits ME more', correcting the agent's three-co-equal-communities reading: 'the military parts
are about overall approach, the test pilot stuff doesn't negate that.' Reasoning accepted:
operations, airworthiness, certification, safety management, flight test, configuration
management and crew discipline are departments of one air force; every metaphor circled is
one department seen alone; every noun has a standard behind it; its central problem (no
individual holds the whole, high tempo, catastrophic error cost) is gzkit's. The direction
the frame serves (insight 20:19:54, verbatim): 'currently so much of the bloat is trying to
universally constrain the model by treating every model/agent like it is omniscient and
omnipotent, a series of much smaller, and much more focused agents, being orchestrated, often
by skill-driven workflow, is a better goal.' CRM is the forty-five-year-old answer to that.

**commissions:** 4 — the concept of operations, drafted on the operator's go.

## decision · the combat register stands at full strength

The agent named "nobody strikes their own fleet" as a strain and offered a civil softening.
Operator (insight 22:03:25): 'have you not seen how many curses I have invected into the
insights and ledger?' Measured: 16 lines and 5 lines. Softening withdrawn; combat assessment,
weaponeering, tasking and the rest are used at their JP 3-60 strength.

## decision · placement is the apex, not a sidecar

Operator (insight 22:03:25): 'also, yes to sidecar vs. apex' — read by the agent as apex; the
operator confirms or corrects (frontier). Reasoning as staged: in ISO/IEC/IEEE 29148 the
concept of operations is the information item from which stakeholder requirements derive, so
it sits above the PRD; constitution, PRD and campaign plan are renewed from it. **Corrected
2026-10-06 on the landed source:** 29148 states no such ordering; that part is the agent's
inference. What the standard does say (sample pages, read by this session): the concept of
operations is an organization-level statement of assumptions or intent, frequently embodied
in long-range strategic plans, giving "the basis for bounding the operating space" (3.1.5 and
its notes); the operational concept is its system-level counterpart (3.1.16; normative
Annex A); the business or mission analysis process (6.2) is listed before stakeholder needs
and requirements definition (6.3), an order of processes rather than a derivation rule; and
the nearest analogue of a PRD in 29148 terms is the business requirements specification
(3.1.4) or the stakeholder requirements specification (3.1.29), each of which carries an
operational-concept section of its own (9.3.16, 9.4.16). So the apex reading rests on the
ConOps's organization-level, bounding role and on the operator's words, not on a ranking the
standard makes. A sharpening the operator can rule with the confirmation: the gzkit document
is a ConOps in 29148's sense (how the organisation intends to employ its human and agent
resources) with an operational concept of the runtime beneath it. The lodestar is its home as
doctrine; the campaign plan names it as companion on republish. The operator's earlier
framing *(conversation-captured)* offered both readings: 'a converged and guiding sidecar, or
binary star, to the magna carta' or 'drastically update the constitution, lodestar, PRD'.

**Ruled 2026-10-07: apex under the constitution.** The question was put with three
placements: apex over the PRD and the campaign plan with the constitution above it; full
apex as a new root; sidecar to the campaign plan. Operator selection, verbatim: 'Apex under
constitution (Recommended)'. What the ruling fixes, and what it corrects in the reasoning
above:

- The sentence above, "constitution, PRD and campaign plan are renewed from it", went further
  than the insight it rests on (22:03:25: "above the PRD, not a sidecar to the campaign
  plan") and collided with a ruling the active campaign plan carries in § 9a (operator,
  2026-06-14, as booked in `build-to-1.0-campaign-2026-06-10.md`): the Constitution is "the
  enduring normative charter, **root by stability gradient** (amendment cadence)", the tree
  "ordered by *rate of change*". That ruling stands. The constitution is not renewed from the
  concept of operations.
- The concept of operations ranks above the PRD and the campaign plan. Its seat between the
  constitution and the PRD is the agent's inference from the booked ranking rule (it changes
  at a reconceptualisation: slower than a per-major PRD, faster than a charter of
  invariants), accepted by the selection; canon does not state it.
- The campaign plan keeps sequencing authority (its § 8: "The campaign rules sequencing").
  The lodestar is the document's home as doctrine.
- Facts read 2026-10-07 that the placement rests on: `docs/design/constitutions/` holds only
  `.gitkeep`, so the root the 2026-06-14 ruling names still has no document; the PRD is
  `status: Draft`, dated 2026-01-22; `docs/governance/ieee/01-engineering-method-2026-09-22.md`
  records the PRD as "Superseded in practice by the campaign plan"; the campaign register
  carries 'sidecar' as "advisory sidecars, not steering surfaces".

*Avoid* "apex" unqualified: it reads as root, which the ruling refuses.

**commissions:** 4 — the concept of operations in the doctrine library, seated above the PRD
and the campaign plan and under the constitution; the campaign plan republished naming it; a
PRD amendment pass. The constitution and the PRD are corrected where they contradict it (the
four stale items), not rewritten from it.

## decision · green keeps local cleanup

Ruled 2026-10-05; insight 20:19:54 records it as '(1) Green keeps local cleanup' without
quoting the operator's words (the staging rendered it as "A, green keeps local cleanup").
Wider refactor is its own traversal (four-phases doctrine). No commission.

## decision · chase and damage assessment are two roles

Ruled 2026-10-05; insight 20:19:54 records it as '(3) Chase and damage assessment are two
roles' without quoting the operator's words. Chase confirms a test pass from the black box;
damage assessment is target effect, munitions effectiveness and collateral, and the collateral
question has no owner today.

**commissions:** 1 — propose a combat-assessment engineering order (collateral owner; one
assessment record) after briefs 15–20.

## decision · the constraints sortie is a Design act

Operator (insight 20:19:54, verbatim): 'these are the prior contracts and understandings of
the system (Design by Contract) - these are invariants and other constraints that the model
must obey'. Contracts (interface control documents, invariants, stubs) land before any red;
the red witness then classifies on assertion rather than on a missing symbol (207 of 282
receipts were `error` on 2026-10-05).

**commissions:** 1 — propose the crew-split engineering order (constraints, red, green; CRM
pilot-flying / pilot-monitoring separation) after briefs 15–20.

## decision · general orders exist and are tiny

Operator (insight 22:07:45, recorded late, verbatim): 'A, general orders exist and tiny -
raise effort. I just changed models and raised effort.' Three candidates, the agent's draft
and not operator wording: report truthfully; call knock-it-off when lost or blocked; never
forge evidence. Everything else rides on the tasking order, in the loadout, or is enforced by
an interlock.

**commissions:** 4 — the general orders as the universal contract's irreducible core.

## decision · routing: this dialogue is an R&D run

Operator (insight 21:23:34): '1.A;'. The run is opened by the operator through `gz-rnd`;
decisions already ruled enter with their insight-line provenance rather than being
reconstructed. Discharged by the invocation of 2026-10-06.

## decision · weaponeering: the REQ kind fixes the sortie set, with evidence-cited subtraction and free addition

Operator (insights 21:23:34, 21:28:16): '2. A (but what about C?)' then 'A with
evidence-cited subtraction and free addition'. BEHAVIOR flies constraints, red and green;
SUPPORT one documentary sortie; STRUCTURAL-FENCE none, audited at closeout. An order may add
sorties freely. A standard sortie is skipped only when its product already exists on the
ledger and the order cites it (red: an assertion-class red receipt for the REQ on the base
tree; constraints: the contract exists and the brief names the symbol). Green and assessment
are never waived. Planner discretion is refused; the runtime checks the rule, the planner
never decides it.

**commissions:** 4 — the rule text; 1 — propose, with the crew-split order.

## decision · model and effort are allocated by echelon and role, with the regeneration test as falsifier

Operator (insight 21:23:34): '3. A (so model + effort)'. Strongest model: headquarters
synthesis and the constraints sortie at high effort; elicitation at low to medium; execution
sorties mid-tier at low; assessment strong at high; cross-vendor IV&V and security-sensitive
assessment at max; the regeneration test mid-tier at low. Triangulated by Krishnan (ch. 4),
Shihipar, and the system-card note in `CLAUDE.md`. Mechanism: see *effort rides on the agent
definition* above.

**commissions:** 4 — amend `.gzkit/rules/model-selection.md`; `harness-lab` as host for the
regeneration test.

## decision · the tasking order is an L2 ledger event

Operator (insight 21:23:34): '4. A'. Completes the chain tasked → dispatched (GHI #886) →
outcome (brief 18) → position (brief 15); the mission card is its L3 rendering; the sortie
matrix is an L3 view with rows from L1 and cells from L2.

**commissions:** 1 — propose, after briefs 15 and 18 land; changes neither.

## decision · ultimate nomenclature for the artifact ladder

Operator (insight 22:03:25): 'A'. Change proposal (`ECP-<slug>`) for the pool; engineering
order (`EO-0.35.0-<slug>`) for the feature bundle the "(m)ADR" was standing in for; work
package (`WP-0.35.0-10-<slug>`) for the OBPI; task card (keep `TASK-`); ADR reserved for
architecture decisions (`ADR-<n>`), the closed 0.0.x series kept as gzkit's certification
basis; block for the release. Identifiers migrate at IOC through the `gz migrate-semver`
precedent; aliases bridge.

**commissions:** 4 — terms held here until the glossary home is named; 5 — the identifier
migration program at IOC.

## decision · ultimate nomenclature, the rest (terms held here until the glossary home is named)

Each row's source is cited from memory until its file lands under `sources/`; see the
standards entry above.

| Register | gzkit term | Ultimate name | Source |
|---|---|---|---|
| Guidance | lodestar | doctrine library | joint doctrine publications |
| | constitution | constitution (standing constraints) | 29148 constraints; Part 119 OpSpecs as analogue |
| | PRD | functional baseline of a major version | EIA-649; 29148 |
| | new apex | concept of operations | 29148 ConOps |
| | campaign amendments | fragmentary orders, folded on republish | OPORD practice |
| | sequenced campaign items | prioritised target list | JP 3-60 JIPTL |
| CM | ledger | configuration status accounting; flight data recorder | EIA-649 |
| | receipts | objective evidence; life-cycle data | ISO 9000; DO-178C § 11 |
| | closeout | functional and physical configuration audit | MIL-HDBK-61B; EIA-649C |
| | attestation | return to service | 14 CFR 43.9; EASA Part 145 CRS |
| | repudiate | release withdrawn | same |
| | `--distribution` | configuration index | DO-178C SCI |
| Operations | orchestrating session | operations centre; duty officer | JP 3-30 |
| | pipeline run | mission | JP 3-30 |
| | dispatch | launch | sortie generation |
| | `HandoffResult` | mission report (MISREP) | — |
| | spec, quality, collateral review | combat assessment: BDA (physical, functional), MEA, re-attack | JP 3-60 |
| | Step 4b adversary | independent verification and validation | IEEE 1012-2024 |
| | airlock in / out | last-chance check with CDE / safing and FOD walk | EOR practice; JP 3-60 |
| | seam-map | interface control documents; zones affected | ICD practice |
| | lock | custody | — |
| | session, handoff | watch, position relief briefing | FAA JO 7110.65 |
| | allowed/denied paths, tool grants | rules of engagement, loadout, special instructions | ATO SPINS |
| | implementer, reviewers, narrator | pilot flying, pilot monitoring, assessor, briefer | CRM |
| Airworthiness | chores, registry, `gz mx` | MSG-3 tasks, maintenance planning document, MRO visit | MSG-3 |
| | `gz check`, CI | preflight; functional check flight | — |
| | GHI | squawk; problem report | tech log; DO-178C § 11.17 |
| | operator hold | deferred defect (MEL item) | MEL practice |
| | direct repair, ghi-close | rectification, sign-off | — |
| Safety | governance of governance | safety management system | Annex 19; Part 5 |
| | failure-mode taxonomy | hazard log | SMS |
| | insights file | occurrence reports | ASRS as model |
| | finding-rate panel | flight operational quality assurance | AC 120-82 |
| | V.I.B.E.S. | normalisation of deviance | Vaughan |
| Assurance | lane | lane (unchanged; ruled 2026-10-07) | operator rulings 2026-09-23 and 2026-09-25 |
| | consequence bands C0 to C3 | assurance level | `consequence-bands.md`; IEEE 1012 Clause 5 as the IEEE thread read it |
| | gates | objectives | DO-178C Annex A |
| | `@covers` | bidirectional traceability; requirements-based testing | DO-178C |
| | gating validators | qualified tools | DO-330 |
| | hooks | interlocks | — |
| | rules | standing instructions | — |
| | skills | procedures; challenge-and-response checklists | CRM |
| | fix, refactor, chores, vendor alignment; feature work (agent proposal) | corrective, perfective, preventive, adaptive; additive | ISO/IEC/IEEE 14764:2022 (five types) |
| Fielding | 1.0 | initial operational capability | acquisition practice |
| | adopter `gz init` | entry into service | — |
| | AirlineOps | lead wing | Boundary #5 |

Verification status on 2026-10-06 (source entry *US-government texts landed*): rows sourced
to 14 CFR 43.9, Part 5 (the SMS definition), Part 119, Part 121 Subpart L (CAMP), AC 120-82
and MIL-HDBK-61 stand on landed text; the hazard-log and letter-check rows are not grounded in
the regulation and need another source; rows sourced to JP 3-30, JP 3-60, JO 7110.65 and
AC 121-22 remain cited from memory until those texts are read. From the standards entry: the
edition years in the Source column are corrected above (12207:2026, IEEE 1012-2024, ARP4754B,
ARP4761A, EIA-649C, MIL-HDBK-61B); IEEE 828-2012 and 1028-2008 are inactive-reserved and are
cited as such; the 14764 row gains additive maintenance, to which "feature work" is the
agent's proposed mapping; rows whose claim lives only in paid text (the lane row's
severity-to-level premise, DO-178C's clause numbers and coverage criteria, EIA-649C's function
names) carry "clause unverified" until a licensed copy is read.

Three rows change doctrine rather than name it and each needs a witness: assurance level as
the lane criterion (ruled 2026-10-07: refused as a lane criterion, commissioned as a second
axis — decision *assurance level is a second axis beside lane*);
weaponeering as a rule (ruled); the tasking event (ruled). Facts on the lane row, gathered
2026-10-06: `lane` is a required `lite | heavy` field in `src/gzkit/schemas/adr.json`,
`obpi.json` and `obpi_brief_structure.json`; nothing in `src/gzkit` infers a lane from the
paths a change touches; the criterion lives in prose (`AGENTS.md` § Gate Covenant) and in the
interview prompt "heavy = external contracts" (`src/gzkit/interview.py`). An assurance-level
criterion would need its own witness before it could replace that prose.

## decision · assurance level is a second axis beside lane

Frontier question 2 asked whether assurance level replaces the external-contract lane
criterion. Canon answered the first half before the question was put (source entry
*repository canon on lane and consequence*): the lane criterion is ruled twice and stands, so
"replaces" was not offered. What was put, 2026-10-07, with two answers: a consequence axis
beside lane, proposed only; or the name alone, not pursued in this run. Operator selection,
verbatim: 'Second axis, propose only (Recommended)'.

What the ruling fixes:

- Lane keeps its name and its criterion. The table row is corrected.
- "Assurance level" is the ultimate name for the consequence bands the operator ruled on
  2026-09-22: detectability plus recoverability, `band = D + R`, C0 to C3. It is not severity
  of failure condition, and it rests on no DO-178C or ARP4754B text.
- It is an axis independent of lane, as `kind` and `sensitivity` already are.
- The witness follows the `sensitivity` precedent: a registry of scored surfaces and a
  path-overlap floor under which a brief may escalate and may not escape. That is the shape
  only; its specification is diamond 2.
- Two fences bind the proposal, both ruled 2026-09-22: a level adds rigour and never lowers
  the attestation or initiation floor (`OPEN-QUESTIONS.md` § Q-05, "Do not re-propose it");
  and the five gates are not abandoned or renamed by it.

What it does not settle: the band scores are PROVISIONAL, and the lift is the operator's at
the first point a band is consumed, which this proposal would be. Three rows have no finding
behind them and four rest on findings that are open or disputed.

*Avoid* "assurance level" for lane, and *avoid* "severity" for the scale.

**commissions:** 1 — propose an engineering order for the assurance-level axis, after briefs
15 to 20, conditional on the operator lifting PROVISIONAL; 4 — the corrected nomenclature rows.

## decision · corrections booked during the dialogue

Insights 20:01:34, 20:04:41, 21:01:04, 21:07:34: the agent led with critique of the source
and compressed the proposal ('you are glossing over too much'; also 'i like the agent
separation', 'even if mirror, i like the framing'); dropped the command structure ('so much of
my military sortie stuff is left out, are you getting it?'); omitted the assessment column
from the echelon ladder ('echelons and artifacts misses bda'); mapped chores to letter checks
by depth only ('No, for chores, I meant this:'). Each is repaired in the material above. The
operator also said 'i am behind in your questions' (21:01:04); this run asks one question at
a time, each with a recommendation.

## decision · the accounting (agent finding, accepted by the operator continuing)

The operator asked (insight 21:01:04, verbatim): 'should i stop using gzkit to build gzkit
and jus craft it on the side with high-powered models?' The agent's answer, the accounting:
the spine of the remedy — the operations centre becoming the runtime (briefs 15–20), the
airlock bite (ADR-0.37.0), the second opinion at the convergence moment (ADR-0.36.0), the
flight-test verb (ADR-0.38.0) — is in flight or authored next, in the ruled order. The sortie
layer is new only as an assembly: its parts are pool nominations (`sandboxed-delegation`,
`tool-permission-classifier`, `execution-memory-graph`, `workflow-specification`,
`workflow-substrate-adoption`, `structured-prompt-architecture`, `tdd-receipt-stream`,
`review-receipt-taxonomy`, `harness-fitness-report`, `attestation-quality-measurement`,
`harness-lab`, `chores-system-maturity-absorption`, `fenced-prototype-spike-skill`,
`change-isolation-workspace`, `spec-delta-markers`, `rulings-as-first-class-events`;
`skill-runtime-authority-inversion` to amend). Nothing in flight is wasted; the new layer
cannot start before the spine lands. Operator *(conversation-captured)*: 'If nearly all of the
remedy is in planned work, then I can hold on.'

## decision · the method is a battle rhythm (agent proposal, not yet ruled — frontier)

Each watch: read the picture, not the story; declare the writer; one order in effect; one
decision brief; the account, not a handoff. Each week: republish the order with amendments
folded; one maintenance visit (`ghi-triage`, due checks together in `gz mx`). Each operation:
closeout, a flown sortie on a substrate, release to service. Held by hand until briefs 15–20
land, then mechanical.

## decision · the IOC set (agent proposal, for the PRD amendment, not yet ruled — frontier)

ADR-0.35.0 complete; ADR-0.36.0 with lit doors; ADR-0.37.0 flipped; ADR-0.38.0 with S1 flown
on a non-gzkit substrate; the Movement C reductions ruled pre-1.0; the four theatre-canon
staleness items repaired. Everything not named is post-IOC by default.

---

## Disposition map

<!-- All six rows always present. State is `commissioned` or `not pursued` — there is no
     third state. The states below are the agent's draft; the operator rules each row at
     the close, and no row executes before the operator's go on that row. -->

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | commissioned | Proposed only, after briefs 15–20: engineering orders for the crew split (constraints, red, green) with the tasking event and the sortie matrix; the assurance-level axis beside lane (the consequence bands, with a surface registry and overlap floor as witness), conditional on the operator lifting PROVISIONAL on the bands; combat assessment with a collateral owner and one assessment record; the maintenance logbook to L2; identifier migration at IOC. | Each passes the admission question — hard to reverse, surprising without this record, a real trade-off; each depends on the spine. The operator initiates, or not (IRON LAW). |
| 2 | GHI / direct fix | commissioned | (a) The four theatre-canon staleness items (insight 21:34:40: dead constitution link; stale non-goal; INV-007 vs ADR-0.0.36; lodestar README vs Boundary #5) via `ghi-author`. (b) Routing of the malformed `@covers` tags insight 21:30:15 recorded (525 findings on 2026-10-05; re-measured 2026-10-06, still present): one GHI for direct repair of foundation-era tags to REQ ids, or a parser rule for OBPI-id tags — the operator picks. (c) Nothing lints Markdown under `docs/`: `run_pymarkdown` has no caller, the `lint()` docstring names a linter that never runs, and pymarkdown is not installed or declared (insight 2026-10-06T10:49:46Z; found in passing by the research pass, verified by the session). Route: a direct fix of the docstring and the dead function, or a dependency decision under STDLIB-FIRST — the operator picks. | Defects by the PRIME DIRECTIVE, each tracked by an insight line today. Item 10's run has completed and no lock is held, so (b) is no longer another session's. Filing waits on the operator's go on this row. |
| 3 | chore | commissioned | Advise only: sort per-flight conformance checks off the interval board into `gz check`; package due interval tasks into named visits (letter checks). | The board's 35 overdue of 40 (measured 2026-10-05) is the signature of per-flight work on an interval board. The operator directs admission. |
| 4 | control surface, rule, doc, skill, hook | commissioned | The concept of operations in the doctrine library; the campaign plan republished naming it; a PRD amendment pass (the four stale items, the IOC set); the weaponeering rule text; the model-and-effort table in `model-selection.md`, describing the mechanism as the harness has it; the general orders; the nomenclature terms, held here until the glossary home is named. | The deliverable of this run; the operator's go on this row is the fund. The placement is ruled (2026-10-07: apex under the constitution), so the first two are no longer gated by it; the standards must land before any term is cited in doctrine. |
| 5 | one-shot refactoring | commissioned | Identifier migration ECP / EO / WP via `gz migrate-semver`, aliases before, timed to IOC. | Ruled 'A' (insight 22:03:25); the PRD-per-major rule puts it at the major boundary. Proposed as a program; the operator selects its route. |
| 6 | no action | commissioned | Do not build: an `issue-ato` CLI verb from the dialogue; an AST radar as a separate tool; "halt after N amnesiac turns"; a civil softening of the combat register. | The airlock already parses; `BLOCKED` to the operator is the better escalation; the softening was withdrawn by the operator (insight 22:03:25). |

## Close

**Challenge restated.** <Deliberately restated at the close. The run is open.>

**Frontier.** Open at 2026-10-06, in the order the run asks them, one at a time:

1. *Closed 2026-10-07 by ruling* (decision *placement is the apex, not a sidecar*): apex
   under the constitution.
2. *Closed 2026-10-07 by ruling* (decision *assurance level is a second axis beside lane*):
   lane keeps its criterion; the consequence bands are proposed as a second axis.
3. Whether chore runs and findings become ledger events (moves rows 1 and 3).
4. The battle rhythm (agent proposal; moves row 4).
5. The IOC set for the PRD amendment (agent proposal; moves row 4).
6. The standards verification pass — both halves have landed (27 files). Open remainder:
   JP 3-30, JP 3-60, JO 7110.65 and AC 121-22, unreached by automated retrieval, to be read
   from the official PDFs by hand or in the browser pane; and the paid-text claims (29148
   ordering, ARP4754B severity-to-level, EIA-649C function names, DO-178C clause numbers and
   coverage criteria), readable only from licensed copies the operator may hold.
7. The slug — decided by the agent as `renewing-vows`, open to the operator's veto.
8. The operator's go on each row, at the close.
9. Whether a doctrine row may rest on an inference from a standard's public structure where
   its text is paywalled, or must wait for the licensed copy under the primary-source rule
   (moves row 4's drafting rule for the concept of operations).

Closed by fact on 2026-10-06: the effort mechanism (decision *effort rides on the agent
definition*).

**Sign-off.** <Operator's verbatim words> — <kill | fund>

## What this record does not license

No ADR, OBPI or chore is started by this run. Rows 1–5 await the operator's go on each row;
row 6 names what is not built. No ledger event was emitted for the run. The licensed book is
cited, never copied; copyrighted standards land as citation records only. The operator's
identity is recorded as g0 and no personal address appears. The staging file in the prior
session's scratch directory is superseded by this record and carries no authority of its own.
