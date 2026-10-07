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

## source · repository canon on placement, read 2026-10-07

Read by this session for frontier question 1, after re-entry.
`docs/governance/build-to-1.0-campaign-2026-09-20.md`: the header through the opening of § 5
and §§ 7 to 9a read in full (lines 1–230 and 479–613); § 6 and § Amendments by heading only.
`build-to-1.0-campaign-2026-06-10.md`: the three amendments of 2026-06-14 (lines 62–118).
`docs/design/lodestar/README.md`: in full. `docs/design/prd/PRD-GZKIT-1.0.0.md`: frontmatter
through the opening of § 2. `docs/governance/ieee/01-engineering-method-2026-09-22.md`: the
PRD and Constitution rows of its object table, found by search; the file was not read.
Insight 22:03:25: in full. The rulings store was searched for "apex", "concept of
operations", "sidecar" and "constitution"; a search is not a read of 1418 rulings.

The root is ruled. 06-10 edition, amendment of 2026-06-14, verbatim, with the operator's
words inside it:

> Operator: *"this seems to stand in place longer than the advance of major versions of any
> given product"*

> **Constitution** = the enduring normative charter, **root by stability gradient**
> (amendment cadence); **PRD** = per-major-release child (release cadence). The tree is
> ordered by *rate of change* — Constitution → PRD → ADR → OBPI

The active plan carries it. § 9a: "**CARRIED, amended 2026-09-25.** Constitution → PRD
product grounding stands." § 3: "Constitution → PRD (one per major) grounds durable product
requirements." `AGENTS.md` § Pattern Discovery: "Constitution → PRD grounds product intent;
ADRs remain subject to both."

The plan's own authority, § 8, verbatim:

> The campaign rules sequencing; handoffs and triage **advise**.

> No work stream runs outside it except `emergency`-labeled interrupts.

"Sidecar" has a booked meaning in the plan, § 9 (06-23 amendment, CARRIED): "Harness
loop-engineering + OKF notes are advisory sidecars, not steering surfaces".

The root has no document at its configured path. `.gzkit/manifest.json` and `.gzkit.json`
name `docs/design/constitutions`, which holds only `.gitkeep`; the ledger schema declares
`constitution_created` and the ledger carries no such event (`grep -c`, 0). The 06-10
amendment observed the same: "the root that observation shows does **not yet exist**". The
IEEE object table: "**Constitution** | Declared but unpopulated". Two charters exist
elsewhere: `docs/governance/GovZero/charter.md` ("the **sole authority** for GovZero gate
definitions and semantics") and `docs/user/reference/charter.md`; the PRD names "gzkit
Charter" as its constitution through the dead link insight 21:34:40 records. The rulings
store holds a constitution lifecycle (GHI #1134, closed: "canonical states
Draft/Ratified/Amended/Superseded") for a document that is not yet written.

The PRD: `status: Draft`, `date: 2026-01-22`. The IEEE object table's row for it: "Original
product intent, frozen" and "Superseded in practice by the campaign plan".

The lodestar, `README.md`: "This directory contains the **foundational canon** for
gzkit-governed projects." and "They are not suggestions—they are invariants."

What the apex reading rests on. Insight 22:03:25 carries the operator's words as 'also, yes
to sidecar vs. apex' and marks the rest as the agent's: "(read by the agent as: the concept
of operations is the apex information item per ISO/IEC/IEEE 29148, above the PRD, not a
sidecar to the campaign plan)". No ruling in the store matches "apex" or "concept of
operations".

Bears on the challenge in two ways. The sentence in the placement decision below,
"constitution, PRD and campaign plan are renewed from it", goes further than that insight and
against the root ruling. And a placement of the concept of operations as a new root is
closed by canon, so the question put to the operator does not offer it.

## source · repository canon on lane and consequence, read 2026-10-07

Read by this session for frontier question 2. In full:
`docs/governance/ieee/consequence-bands.md`; `docs/governance/ieee/OPEN-QUESTIONS.md` from its
head through § Q-07 (lines 1–145); `.gzkit/rules/security-sensitivity.md`; the citation
records `std-ieee-1012.md` and `std-sae-arp4754a.md`; `AGENTS.md` § Gate Covenant. By
excerpt: `OPEN-QUESTIONS.md` § Q-17 (lines 530–542);
`docs/design/adr/pool/ADR-pool.agent-reliability-framework.md` (its level table, lines
145–162). The rulings store was searched for "lane" (nine results, all read).

The lane criterion is ruled, twice, after the consequence scale was authored. Rulings store,
operator verbatim:

> The distinction is whether the external contract is changed by the OBPI

> consider the distinction between lite and heavy - we shouldn't be changing behavior with lite

> external contract/api behavior must be heavy

`AGENTS.md` § Gate Covenant gives the reason the lane is keyed that way: Gate 4 "asks whether
a new capability does what its OBPI said it would, and that question has no subject until an
OBPI changes an external contract — which is what `heavy` means." Lane decides which gates
have a subject. It does not measure what is at stake.

A consequence scale exists and is the operator's own. `consequence-bands.md`, "Authored live
with the operator on 2026-09-22", verbatim:

> **Defining bands is not adopting them.** This file does **not** re-key the lite/heavy
> lanes, does not change any gate, and authorises no work. Re-keying is a Phase 4 question.

> Operator ruling, 2026-09-22: score two axes, band on the pair.

> **The band is derived, never assigned: `band = D + R`.**

> A failure that crashes costs time. A failure that reports success costs truth.

Its axes are detectability (`D0` loud, `D1` latent, `D2` silent) and recoverability (`R0`
trivial, `R1` bounded repair, `R2` forensic); bands run C0 to C3; sixteen surfaces are scored,
ten of them `D2`. The file says of its own choice of axis: "Not the conventional reading of
1012, and chosen on this repository's own evidence." It is PROVISIONAL by the ruling of
2026-09-23 ('A. Keep PROVISIONAL'): "The lift is decided when Phase 4 is authorised, the
first point at which a band is consumed." Three rows have no finding behind them, F-022 is
`OPEN` and F-021 is `DISPUTED`. `OPEN-QUESTIONS.md` § Q-17, on the pivot accepted
2026-09-25: "Consequence bands stay PROVISIONAL and are not consumed by this candidate."

The same file argues against the lane as a rigour scale: lanes are "keyed to **surface
kind** ... which is a proxy for consequence, not a measure of it", and the `D2` count is "the
strongest argument in this file for why rigour keyed to surface *kind* mis-ranks this
system." The two lane rulings quoted above postdate that argument and keep the criterion.

Two fences from the same thread. § Q-05, ruled 2026-09-22: a consequence threshold that
delegates below a line is "**rejected**, not deferred ... **Do not re-propose it.**" § Q-07,
standing constraint of the same date, operator verbatim: 'do not abandon the five gates
without a discussion with me.'

What the standards records carry. `std-sae-arp4754a.md`: the premise that a development
assurance level is assigned from failure-condition severity is NOT VERIFIED, "the analogy has
no publicly verifiable anchor in SAE's text". `std-ieee-1012.md`: 1012's own term for the
scale that sets V&V rigour is *integrity level* ("V&V life cycle requirements are set by
integrity level"); that record did not check Clause 5, the clause `consequence-bands.md`
names as its basis.

A second axis beside lane has a working precedent with a mechanical witness.
`security-sensitivity.md`: "The axis is additive: heavy lane, foundation kind, and security
sensitivity each independently determine which gates fire"; a registry of surfaces
(`data/security_surfaces.json`), a path-overlap floor and "Escalate-not-escape" under
`gz validate --sensitivity`. Its costs are on the same page: 87 briefs grandfathered at the
cutover for incidental overlap, a direct-fix path the floor does not reach, and a demotion to
advisory inside the MX hangar.

Prior art for graduated levels in the pool: `ADR-pool.agent-reliability-framework`, levels
AR0 to AR4, "inspired by SLSA Build Levels, DO-178C Design Assurance Levels, and S2C2F
maturity". Those grade the provenance of a piece of work; the bands grade the surface it
touches.

Bears on the challenge: the nomenclature table's row "lane → assurance level" proposes a
change two rulings refuse, on a premise (severity of failure condition) that this run's
records could not verify and that gzkit's own scale does not use. "Replaces the lane
criterion" is closed by canon and is not offered.

## source · repository canon on chore run records, read 2026-10-07

Read by this session for frontier question 3. In full:
`src/gzkit/commands/chores_staleness.py`; `docs/governance/state-doctrine.md`. By section:
`docs/governance/chore-class-system.md` — its head through § Operator directives (lines
1–118), § Staleness (831–965), § Implementation order and § What this record does not license
(1294–1422); the other 1,100 lines were not read. By search: `chores_exec.py` for its log
writer and for any ledger call (none found by `grep`, which is not a read); the ledger and
its schema for chore event types; `us-gov-14cfr-43-9.md` for the two quoted lines. The
rulings store was searched for "chore run", "logbook" and "parallel register" (no match).

Where a run is recorded today. `chores_staleness.py`, module docstring, verbatim:

> The run witness is the timestamped PASS block ``gz chores run`` appends to
> ``CHORE-LOG.md``. A FAIL block records that the verb ran, never that the chore
> was done, and a hand-written heading records authorship, never a run (GHI #935).

The board reads it with a regular expression over that Markdown file (`_RUN_HEADING`). An
elapsed-time chore that declares `staleness.artifacts` is dated by a scan record's commit
date instead. The ledger schema declares one chore event type,
`chore_decommission_processed`; the ledger carries it 5 times; no event records that a chore
ran.

The ratified design chose against a second register. `chore-class-system.md` ("design
record, operator-ratified 2026-09-12"; ratification verbatim: 'I ratify, with great
enthusiasm, the entire plan.'), § Derive last-run from the artifact:

> Generalize it. Do not build a parallel register — node_exporter's
> `node_textfile_mtime_seconds` is the precedent: derive the last-run signal from the
> proof artifact itself. One fewer thing to keep honest.

Staleness does not gate. § Indicator, not gate, operator verbatim:

> indicators, chores shouldn't have a bunch of gates like the adr/obpi system

with one exception stated beside it: "The one exception is Currency, where staleness makes
the chore assert something false; that class may gate." The record says of itself: "It is a
design record, not canon". Its § Implementation order step 2 records that the landed witness
already left the proof's commit date for the PASS block, because the log's commit date
"moves on a FAIL run too".

Two canon lines pull the other way. `AGENTS.md` § Governance doctrine surfaces: "Execution
reads thresholds, budgets, rosters and state from JSON or code." `state-doctrine.md` Layer 2:
the ledger "records every governance event — completions, attestations, receipts, audits,
and reconciliations" and "Defines *what has happened*"; Rule 5: "Only L1 (canon) and L2
(events) can be gate evidence." A run log is in neither layer's examples, and the one class
the design lets gate on staleness reads its date from that log or from a scan record's
commit.

On findings. Operator, 2026-09-12 (`chore-class-system.md` § Operator directives): "A chore
doesn't always need to make a GHI and should do so sparringly and in consultation with the
operator." Operator, 2026-10-05 (insight 21:01:04): 'squawks are line-discovered issues
(ghis)'. A finding has no structured form today: a run's log holds each criterion's captured
output as text.

The vocabulary fence: an event type lands with the code that emits it
(`rnd-discipline.md` § Ledger events; the `ledger-vocabulary-inertness` chore).

The aviation text, landed and verified (`us-gov-14cfr-43-9.md`): 14 CFR § 43.9(a) requires
"Maintenance record entries" from "each person who maintains, performs preventive
maintenance, rebuilds, or alters", carrying "(2) The date of completion of the work
performed." The entry is per work performed; it is not a register of defects found.

Measured 2026-10-07 (a dated record; `gz chores status --json`): 35 overdue, 3 unmeasured,
2 current of 40; 6 chores have no last run on record. GHI #935 and GHI #936 are closed;
GHI #1009 (accumulated-work declares no counter) is open.

## source · the campaign plan on rhythm and on the 1.0 set, read 2026-10-07

Read by this session for frontier questions 4 and 5, from
`docs/governance/build-to-1.0-campaign-2026-09-20.md`, each in full: § 5 and § 6 (lines
230–478); § Amendments 2026-10-05, 2026-10-04 (3) and 2026-10-04 (2) (635–794); the two
2026-07-18 amendments on disposition and rhythm (2746–2797); § Workflow fronts (2904–2950).
With the earlier entry that makes lines 1–613 read in full; of § Amendments, 41 of 46 dated
entries were read by heading only. Also read: the *Objective* of each of briefs
`OBPI-0.35.0-15` to `-20`, not the briefs.

**A rhythm is already ratified.** § Amendments 2026-07-18, operator verbatim:

> AGENTS.md -> how we work; magna carta -> what we are working on. handoff -> what we were
> doing last. airlock -> a sortie into the environment. handoff -> a market [marker] for
> when we leave the session. That should be our rhythm.

with a binding consequence stated beside it: "the Magna Carta MUST carry the story and the
executive summary." The same day's disposition ruling, CARRIED: "Re-entry cost is the metric
being minimized."

**The handoff's model is already the position relief briefing.** § 6 Movement D, scope
change of 2026-08-17, operator verbatim: 'a handoff is there to orient a new session from
the prior session - it is an advisory shift change orientation'; "The governing model for the
handoff half is operator-supplied and external: the **FAA Position Relief Briefing**
(JO 7110.65 App A; JO 7210.3)"; scope added there includes "a per-project schema-validated
**Position Relief Checklist**" and "the campaign body as a rendered Layer-3 view". Binding:
"every beat is advisory and gates nothing". So the nomenclature row "session, handoff →
watch, position relief briefing" names what the operator already supplied, and the row's
source text (JO 7110.65) is among the four this run has not reached.

**The plan's own amendment rule.** § 8: amendments are "**appended to § Amendments** — never
interleaved", and "a successor edition MUST carry § Rulings Register forward with every
ruling explicitly **carried** or **withdrawn**." The header: "Slim by design — and this time
it is enforced." Measured 2026-10-07: 46 dated amendment headings, 18 of them dated on or
after this edition's own date, 7 dated October; the file is 252,469 bytes against 186,315 for
the 08-16 edition and 106,955 for 07-18. Six editions exist, created on operator direction at
intervals of ten days to five weeks; none was created on a calendar.

**The 1.0 set is ruled, and ruled closed to shrinking.** § 5 lists ten gates: the floor
holds; the facade is drained as of a dated census; both engines operate; the membrane is on
the real doors (Movement B); the accretion is reduced (Movement C); one external forcing
function exists (a flight-test sortie on a non-gzkit substrate, `ADR-0.38.0`, Movement E);
the five contemporary-stack layers are built; one config system governs every setting
(Movement F, `ADR-0.39.0`); the release line is healthy; v1.0.0 is released. Operator
verbatim, 2026-08-17, on what comes out of 1.0 to fund an enlargement:

> Nothing — move the date instead.

§ 9 register: "**Nothing comes out of 1.0** ... target ≈2027-08 **by declaration, never by
slippage**". § Amendments 2026-07-18, CARRIED: "Set-shrinking moves (bounding gates by dated
census, declaring items "explicitly NOT 1.0 gates", deferral rulings) are no longer the
instrument of progress. Items are *sequenced*, not *excluded*." Operator verbatim, 2026-09-20,
on the config system: "we need to adopt this as a pre-requisite for 1.0."

**The first sortie.** § 6 Movement E: "**0 of 6 sorties have ever flown**"; S1 is blocked on
the verification vocabulary moving to the project; "**The debrief is an input to the
remaining Movements, not a closing formality.**" The accepted cost of its place in the order:
the forcing function "**certifies rather than informs**".

Bears on the challenge in two ways. The staged battle rhythm restates a ratified rhythm in
new words and departs from it twice ("the account, not a handoff"; "read the picture, not
the story"); canon rules both the other way. And the staged IOC set, read as the 1.0 set,
drops four of § 5's gates under "Everything not named is post-IOC by default", which two
carried rulings refuse.

## source · initial and full operational capability — not reached, 2026-10-07

The nomenclature table sources "1.0 → initial operational capability" to "acquisition
practice", from memory. Attempted 2026-10-07 by this session: the Defense Acquisition
University's Adaptive Acquisition Framework page `https://aaf.dau.edu/mca/ioc-foc/` answered
301 to `https://aaf.waru.edu/mca/ioc-foc/`, which answered HTTP 403 to automated retrieval.
Nothing was read from an official host and nothing is quoted.

What reached this session is secondhand: a web search's own summary of its results (the
result list named that page, two Wikipedia articles and three commercial glossaries). In that
summary, initial operational capability is attained when *some* of the units scheduled to
receive a system have it and can employ and maintain it, and full operational capability
when *all* of them do. That agrees with the agent's memory and is NOT VERIFIED against a
primary text. The primary texts to land are the acquisition glossary entry and the governing
instruction it cites, read by hand or in the browser pane; they join frontier item 6.

Bears on the challenge: if the ordering holds, the term the table gives to 1.0 names the
earlier of two milestones, and § 5's ten-gate set reads as the later one.

## source · repository canon on the unwritten constitution, read 2026-10-07

Read by this session for frontier item 10. In full: `docs/user/reference/charter.md`. By
excerpt: `docs/governance/GovZero/charter.md` (its head and § Gate 5, with a search of the
rest for lane scope); `docs/design/adr/pool/ADR-pool.constitution-invariants.md` (lines
1–70); the body of GHI #1134. Carried from the earlier entries: the 2026-06-14 amendment and
§ 6 Movement C.

What canon books for the root. The 06-10 edition, amendment of 2026-06-14, scoped it to an
ADR that was never authored: it "instantiates the Constitution charter (the root that
observation shows does **not yet exist** ...), wires `PRD.parent → Constitution`, bridges
those 73 ADRs, adds PRD + Constitution lifecycle state machines". The same amendment fixes
how the charter relates to what already exists: "the charter is authored, the
constitutional-invariant registry (ADR-0.0.37 CMS) + AGENTS.md are its mechanical render".
The active plan's open box, § 6 Movement C, *Render the stability-gradient spine*: "This box
remains open for the remaining all-surface reconciliation."

A pool nomination exists: `ADR-pool.constitution-invariants` (2026-03-08, `lane: lite`),
intent verbatim: "Formalize `gz constitute` to produce a `CONSTITUTION.md` that declares
immutable project invariants — rules that never change regardless of which ADR is active."

The artifact type is ready and unused. GHI #1134 (closed 2026-09-29) reconciled the
constitution's states and path across registry, transitions, model and schema; `gz
constitute` writes `<paths.constitutions>/CONSTITUTION-<SLUG>-<semver>.md`; the configured
directory holds only `.gitkeep` and the ledger carries no `constitution_created` event.

Two charters stand where a constitution would, both `Status: Active`, both in the published
navigation. `docs/user/reference/charter.md`: "Authority: Canon (sole authority for covenant
definitions)"; its four principles, verbatim: "The human is index zero." "Agents present
evidence; humans decide." "Ceremony must earn its place." "Silence is not attestation."
`docs/governance/GovZero/charter.md`: "the **sole authority** for GovZero gate definitions
and semantics", last reviewed 2026-01-08.

A defect found in that reading, recorded as insight 2026-10-07T09:27:46Z (scope
`theatre-canon:charter-gate5-scope`): the GovZero charter states of Gate 5 "**Applies to:**
Heavy lane only (required for ADR closeout)" and the user charter's gate table gives Gate 5
the scope "Heavy lane", against `AGENTS.md` § Gate Covenant, where Gate 5 is universal
(ADR-0.0.36). Two issue searches found no GHI for it. It joins row 2(a) as a fifth
theatre-canon staleness item.

Bears on the challenge: the concept of operations is seated under a root that exists as a
ruling, a ready artifact type, a pool nomination and two stale charters, and not as a
document. This run already holds content for it: the general orders.

## source · the operator's standards corpus, and what is still unread — 2026-10-07

Opened by the operator's course-correction (insight 2026-10-07T09:40:29Z), verbatim:

> wait for what texts? we have dropped several in for the IEEE work, which others do you
> need?

Read 2026-10-07: `docs/governance/ieee/README.md` § Standards corpus (lines 527–552); one row
of `docs/governance/ieee/01-engineering-method-2026-09-22.md` (line 137) and its Method line
(31), found by search.

The operator holds twenty-four licensed standards, "read at clause level" by the IEEE series
and not vendored. Among them, the four this run labelled paid or unverified on 2026-10-06:
ISO/IEC/IEEE 29148:2018, 12207:2026, 42010:2022 and IEEE 1012-2024. The corpus folder is
outside the repository, at the path piece 01 names; this session's attempt to list it
returned "Operation not permitted", so nothing was read from it today.

One claim is already verified in the repository from the licensed text. Piece 01, verbatim:

> **1012-2024 Clause 5** (***shall***) — "The degree of rigor and intensity… **shall** be
> commensurate with the integrity level"

So "integrity level" stands on Clause 5 as the IEEE series read it, and the nomenclature
row's "clause unverified" is withdrawn.

What today's rulings made no longer load-bearing: the 29148 ordering of the concept of
operations above the StRS (the placement was ruled on the operator's words and the stability
gradient, not on the standard); ARP4754B's severity-to-level rule and ARP4761A (the
integrity-level ruling dropped severity); EIA-649C's function names (MIL-HDBK-61B is landed,
verified 7 of 7, and defines configuration status accounting, the audits and the baselines,
so those rows are re-sourced to it).

What is still unread and still carries a row:

| Text | Rows it carries | Standing |
|---|---|---|
| JP 3-60, *Joint Targeting* | combat assessment, BDA, MEA, CDE, the prioritised target list, weaponeering | public; refused automated retrieval |
| JP 3-30, *Joint Air Operations* | tasking order, operations centre, special instructions | public; refused automated retrieval |
| FAA Order JO 7110.65, Appendix A | watch, position relief briefing | public; refused automated retrieval; the campaign plan already carries it as operator-supplied (§ Amendments 2026-08-17 C) |
| FAA AC 121-22 (current revision D, secondhand) | maintenance review board; the letter-check mapping | public; refused automated retrieval |
| The acquisition glossary entries for IOC and FOC | the two Fielding rows | public; refused automated retrieval |
| RTCA DO-178C | clause numbers only: § 11 life-cycle data, § 11.17 problem reports, Annex A objectives, the configuration index | paid; not in the IEEE corpus list |
| A4A MSG-3 | task and interval vocabulary | paid; 2 of 3 claims verified from public material |

Useful when the concept of operations is drafted, and not needed to close this run:
29148:2018 Annex B, the informative outline of a concept of operations, from the operator's
corpus at a path the session can read.

## source · Parasoft's overview of DO-178C, supplied by the operator 2026-10-07

`docs/rnd/renewing-vows/sources/src-parasoft-do-178c-overview.md` · the operator's whole
message, in answer to the list above, was the URL
`https://www.parasoft.com/learning-center/do-178c/what-is/` · fetched and read by this
session 2026-10-07 (HTTP 200; the passages were read from the downloaded page text).

A secondary source: a tool vendor's section-by-section overview, undated and unsigned. It
cannot verify a claim against RTCA's text; it shows what a practitioner account says. Two
lines, verbatim:

> Level A was the most stringent and Level E meant no safety requirement.

> Section 11 discusses artifacts like the data and documentation produced during the
> software life cycle.

What it supports, as secondary: levels A to E; a level assigned from failure-condition
severity (catastrophic "would be classified as software level A"); Section 11 as the life
cycle data; problem reports, the software configuration index and the software
accomplishment summary as items of that data; objectives tabulated in Annex A tables;
bidirectional traceability whose depth "varies based on the software level";
requirements-based testing; tool qualification in DO-330.

What it leaves where it was: the number § 11.17; any count of objectives; which coverage
criterion binds at which level; anything on independence beyond the word.

What it adds: "Configuration status accounting" and "Problem reporting, tracking, and
corrective action" are listed as DO-178C configuration-management activities, so the
ledger row's term has an aviation source beside MIL-HDBK-61B; and control categories 1 and
2, for which this run has no row.

Where it differs from the publisher: it dates DO-178C "January 2012" against RTCA's
2011-12-13, and it names ARP4754A, not ARP4754B.

Bears on the challenge: of the seven unread texts, DO-178C's rows now stand on a secondary
source for their terms and on nothing for their clause numbers. And the page states the
severity model in plain words, which is the model the integrity-level decision says gzkit's
scale does not use.

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

**Ruled 2026-10-07: under the constitution, above the PRD.** Put with three seats: under the
constitution and above the PRD and the campaign plan; a binary star to the campaign plan with
no rank over the PRD; written into the constitution itself. A new root was not offered,
because canon closes it (source entry *repository canon on placement*). Operator selection,
verbatim: 'Under constitution, above PRD (Recommended)'. What the ruling fixes, and what it
corrects above:

- The sentence "constitution, PRD and campaign plan are renewed from it" is withdrawn as to
  the constitution. The 2026-06-14 ruling stands: the constitution is the root by stability
  gradient and is not renewed from the concept of operations.
- The concept of operations ranks above the PRD and the campaign plan. Canon's tree names
  Constitution → PRD and no tier between them; the seat is new, proposed by the agent on the
  booked ranking rule (it changes at a reconceptualisation, which is rarer than a major
  release) and accepted by the selection.
- The campaign plan keeps sequencing (§ 8: "The campaign rules sequencing"). The concept of
  operations rules concept and vocabulary, never order of work.
- The lodestar is its home as doctrine.
- It is seated under a root that has no document (`docs/design/constitutions/` holds only
  `.gitkeep`). Until one is written, the concept of operations is the highest authored
  statement of intent, which is a fact about the tree and not a rank. What this run does
  about the unwritten root is a new frontier item.

*Avoid* "apex" unqualified: it reads as root, which canon refuses. *Avoid* "sidecar": in the
campaign plan's register it means advisory and non-steering.

**commissions:** 4 — the concept of operations in the doctrine library, seated under the
constitution and above the PRD and the campaign plan; the campaign plan republished naming
it; a PRD amendment pass that corrects the PRD where it contradicts the concept of operations
(the four stale items, the IOC set) and does not rewrite it from scratch.

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

**Timing restated 2026-10-07, by carry-forward and not by a new ruling.** The ruling's "at
IOC" was given when IOC named 1.0, and its recorded reason is the major boundary. The IOC
ruling of 2026-10-07 moved the word to a waypoint and did not move this decision: the
migration stays timed to 1.0, now named full operational capability, so that 1.0.0 ships
carrying the ultimate identifiers and no later major is spent on a rename. Frontier item 11
is closed on that footing; the operator may re-rule it with the go on row 5.

**What this ruling moves in the IEEE record** (read 2026-10-07:
`docs/governance/ieee/OPEN-QUESTIONS.md` § Q-18 in full; two rows of
`design-candidates.md` found by search). § Q-18, ruled 2026-10-04, the day before:
"Names are chosen later", and "It selects no name, schema or migration". The candidates
table: "No replacement name selected" and "“Brief” is accepted as the work-package role;
executable names, identifier migration, and “sortie” terminology remain open". The ladder
ruling chooses those names, so both surfaces now trail it; and it agrees with the accepted
role, the work package being the assignment and the brief its document. Campaign plan
§ Amendments 2026-10-04 (3) carries the same "no replacement name is selected". Recording
the selection at those three sites is row 4 work, on the operator's go.

**commissions:** 4 — terms held here until the glossary home is named; the selection
recorded at § Q-18, the candidates table and the campaign amendment; 5 — the identifier
migration program, timed to 1.0.

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
| | consequence bands C0 to C3 | integrity level (ruled 2026-10-07) | IEEE 1012-2024 Clause 5, as quoted in IEEE piece 01; `consequence-bands.md` |
| | gates | objectives | DO-178C Annex A |
| | `@covers` | bidirectional traceability; requirements-based testing | DO-178C |
| | gating validators | qualified tools | DO-330 |
| | hooks | interlocks | — |
| | rules | standing instructions | — |
| | skills | procedures; challenge-and-response checklists | CRM |
| | fix, refactor, chores, vendor alignment; feature work (agent proposal) | corrective, perfective, preventive, adaptive; additive | ISO/IEC/IEEE 14764:2022 (five types) |
| Fielding | 1.0 | full operational capability (ruled 2026-10-07) | acquisition practice (not verified) |
| | `ADR-0.35.0`–`0.38.0` landed and S1 flown | initial operational capability (ruled 2026-10-07) | acquisition practice (not verified) |
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
the lane criterion (ruled 2026-10-07: refused as a lane criterion, proposed as a second axis
named integrity level — decision *the consequence bands are a second axis beside lane*);
weaponeering as a rule (ruled); the tasking event (ruled). Facts on the lane row, gathered
2026-10-06: `lane` is a required `lite | heavy` field in `src/gzkit/schemas/adr.json`,
`obpi.json` and `obpi_brief_structure.json`; nothing in `src/gzkit` infers a lane from the
paths a change touches; the criterion lives in prose (`AGENTS.md` § Gate Covenant) and in the
interview prompt "heavy = external contracts" (`src/gzkit/interview.py`). An assurance-level
criterion would need its own witness before it could replace that prose.

## decision · the consequence bands are a second axis beside lane, proposed only

Frontier question 2 asked whether assurance level replaces the external-contract lane
criterion. Canon answered that half before it was put (source entry *repository canon on
lane and consequence*): the criterion is ruled twice and stands, so "replaces" was not
offered. Put 2026-10-07 with two answers: the bands as a second axis, proposed only; or the
name alone, with no axis pursued in this run. Operator selection, verbatim: 'Second axis,
propose only (Recommended)'.

What the ruling fixes:

- Lane keeps its name and its criterion. The table row is corrected.
- The scale the row reached for is the one the operator ruled on 2026-09-22: detectability
  plus recoverability, `band = D + R`, C0 to C3. It is not severity of failure condition and
  rests on no DO-178C or ARP4754B text.
- It is proposed as an axis independent of lane, as `kind` and `sensitivity` already are.
- The witness follows the `sensitivity` precedent: a registry of scored surfaces and a
  path-overlap floor under which a brief may escalate and may not escape. That is the shape
  only. Its specification is diamond 2, and whoever writes it inherits the precedent's
  recorded costs: grandfathering at cutover, no reach on the direct-fix path, demotion in
  the MX hangar.
- Two fences bind the proposal, both ruled 2026-09-22: a level adds rigour and never lowers
  the attestation or initiation floor (`OPEN-QUESTIONS.md` § Q-05, "Do not re-propose it");
  and the five gates are neither abandoned nor renamed by it (§ Q-07).

Admission question for disposition 1: hard to reverse (a declared field on every brief and a
registry that briefs are checked against); surprising without this record (two briefs in one
lane held to different rigour); a real trade-off (more ceremony on silent-failure surfaces
against the ten of sixteen that fail by reporting success). All three hold.

What it does not settle: the band scores are PROVISIONAL, and the lift is the operator's at
the first point a band is consumed, which this proposal would be.

**The name, ruled 2026-10-07: integrity level.** Put with three answers: integrity level;
assurance level; keep "consequence band". Operator selection, verbatim: 'Integrity level
(Recommended)'. Reasoning: it is IEEE 1012's own term for the scale that sets V&V rigour
(`std-ieee-1012.md`, scope: "V&V life cycle requirements are set by integrity level"), and
1012 Clause 5 is the basis `consequence-bands.md` names, so the name follows the lineage. As
first recorded here the clause was marked unverified; corrected the same day (source entry
*the operator's standards corpus*): IEEE piece 01 quotes Clause 5 from the operator's
licensed copy. The costs accepted with it: the word is IEEE's in a frame ruled military and
aviation, and "ledger integrity" already uses "integrity" for a different thing, so the two
are never shortened to the bare word. The bands C0 to C3 are the levels; `D` and `R` stay the
only digits maintained.

*Avoid* "assurance level": in DO-178C and ARP4754B a level is assigned from failure-condition
severity, a model this scale does not use and this run could not verify from public text.
*Avoid* "assurance level" or "integrity level" for lane. *Avoid* "severity" for the scale.

**commissions:** 1 — propose an engineering order for the integrity-level axis, after briefs
15 to 20, conditional on the operator lifting PROVISIONAL; 4 — the corrected nomenclature
rows.

## decision · a chore run is a ledger event; a chore finding is not

Frontier question 3 asked whether chore runs and findings become ledger events. Two canon
lines disagree on it (source entry *repository canon on chore run records*): the ratified
chore design refuses a parallel register and derives last-run from the artifact; `AGENTS.md`
and the state doctrine put state in JSON or code and what has happened in the ledger. Put
2026-10-07 with three answers: runs yes and findings no; both; neither. Operator selection,
verbatim: 'Runs yes, findings no (Recommended)'.

What the ruling fixes:

- A chore run becomes one ledger event. That event replaces the PASS block in `CHORE-LOG.md`
  as the run witness, so one register remains; the log stays as the readable transcript.
- This amends one line of the 2026-09-12 chore design, § Derive last-run from the artifact.
  The amendment keeps that section's reason ("One fewer thing to keep honest") and changes
  which artifact is the one.
- A finding does not become a ledger event. It keeps its present routes: fixed in the run, or
  a GHI "sparringly and in consultation with the operator". No structured finding object is
  commissioned.
- Staleness still announces and does not gate. The event is a record in the sense of the
  14 CFR § 43.9(a) entry: one per work performed.
- The event type lands with the code that emits it, never before.

Admission question for disposition 1: hard to reverse (a ledger event type is permanent
vocabulary and the board's reader moves to it); surprising without this record (the ratified
design says no parallel register); a real trade-off (one more event type against run state
read by regular expression from Markdown). All three hold.

What it does not do: it does not move the board. 35 of 40 overdue is cadence, which row 3
carries.

**Term (agent proposal, held here until the glossary home is named):** *maintenance record
entry* for the event, the phrase § 43.9(a) uses. *Avoid* "logbook", which rows 1 and 3 of
this record used from memory and no landed text carries.

**commissions:** 1 — propose the chore run event (the maintenance record entry), after
briefs 15 to 20; 4 — on that proposal's landing, the amended line in
`chore-class-system.md`.

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

## decision · the method is a battle rhythm (staged as an agent proposal; ruled 2026-10-07)

As staged 2026-10-05: Each watch: read the picture, not the story; declare the writer; one
order in effect; one decision brief; the account, not a handoff. Each week: republish the
order with amendments folded; one maintenance visit (`ghi-triage`, due checks together in
`gz mx`). Each operation: closeout, a flown sortie on a substrate, release to service. Held
by hand until briefs 15–20 land, then mechanical.

**What canon had already settled** (source entry *the campaign plan on rhythm and on the 1.0
set*), so it was not put: the watch tier. The operator ratified a per-session rhythm on
2026-07-18 and supplied the position relief briefing as the handoff's model on 2026-08-17.
The concept of operations carries that rhythm as ruled. Two phrases of the staging are
withdrawn because canon rules the other way: "the account, not a handoff" (the handoff
stands, advisory, as session memory) and "read the picture, not the story" (the plan "MUST
carry the story"; what the phrase reached for is the existing practice of checking a handoff
against live state). Three more need no new doctrine: "one order in effect" is
`data/active_campaign.json`; "declare the writer" is the single-writer ruling of 2026-09-27;
"one decision brief" is content for Movement D's Position Relief Checklist (the rulings the
operator still owes, presented first), not a new artifact.

**Ruled 2026-10-07: two slower tiers, each triggered by a signal.** Put with three answers:
two slower tiers that come due on an announced signal; the session tier only; the calendar
cadence as staged. Operator selection, verbatim: 'Two slower tiers, signal-triggered
(Recommended)'. What the ruling fixes:

- **Plan republish.** A new edition of the campaign plan folds its amendments into the body
  and the rulings register. It comes due on accumulated amendments, announced, never on a
  calendar. Reasoning: § 8 appends amendments and never interleaves them, six editions were
  each cut on the operator's direction, and "Re-entry cost is the metric being minimized"
  while the active edition has grown to 46 dated amendments. The fold keeps § 8's rule that
  every ruling is carried or withdrawn explicitly.
- **Maintenance visit.** Due chores and issue triage are flown together as one named visit.
  It comes due when the chore board announces it. The operator keeps the frequency
  (2026-09-12: 'I maintain frequency').
- **Neither gates.** Both follow the ratified chore posture: "Staleness **announces**."
- **The operation tier adds nothing.** Closeout and then release are canon. A flown sortie
  per operation is withdrawn: the sortie is the one § 5 gate Movement E carries, behind
  `ADR-0.38.0`.
- **"Held by hand" is withdrawn.** Until a signal is built, each tier is advice in the
  concept of operations and says so in its own text. A cadence declared with no witness is
  the family the campaign's Movement C box exists to close.

Known dependency for whoever specifies the signals: the accumulated-work signal reads
`unmeasured` today (GHI #1009, open).

*Avoid* "weekly" and "each week" for either tier. *Avoid* "the account" for the handoff.

**commissions:** 4 — the rhythm section of the concept of operations (the session tier as
ruled 2026-07-18, the two slower tiers as advisory until signalled); 3 — advise the two
announcements (republish due, visit due) for admission to the chore estate.

## decision · the IOC set (staged as an agent proposal; ruled 2026-10-07)

As staged 2026-10-05: ADR-0.35.0 complete; ADR-0.36.0 with lit doors; ADR-0.37.0 flipped;
ADR-0.38.0 with S1 flown on a non-gzkit substrate; the Movement C reductions ruled pre-1.0;
the four theatre-canon staleness items repaired. Everything not named is post-IOC by default.

**What canon had already settled** (source entry *the campaign plan on rhythm and on the 1.0
set*), so it was not put: the staged set cannot be the 1.0 set. § 5 lists ten gates, the
operator ruled 'Nothing — move the date instead' on 2026-08-17, and the 2026-07-18
disposition retires set-shrinking: "Items are *sequenced*, not *excluded*." The sentence
"Everything not named is post-IOC by default" is withdrawn wherever IOC is read as 1.0.

**Ruled 2026-10-07: IOC is a waypoint before 1.0.** Put with three answers: a waypoint
before 1.0; IOC is 1.0 and its set is § 5; drop the term. Operator selection, verbatim: 'A
waypoint before 1.0 (Recommended)'. What the ruling fixes:

- **Initial operational capability** is a named point on the route: `ADR-0.35.0` through
  `ADR-0.38.0` landed, S1 flown on a non-gzkit substrate (§ 6 Movement E item 3), and the
  four theatre-canon staleness items repaired. Each condition is read from the ledger or
  from a closed issue, never from prose.
- **1.0 is full operational capability.** § 5's ten gates are untouched, and nothing is
  post-anything by default.
- It sequences and excludes nothing, so it does not collide with the two rulings above.
- It makes the first external sortie the near target. The plan names the missing external
  forcing function as "the **root cause of non-convergence**", and says of S1: "The debrief
  is an input to the remaining Movements, not a closing formality."
- Two items of the staged set are not IOC conditions and stay where § 5 has them: the lit
  `AskUserQuestion` door of `ADR-0.36.0`, which lands dark by that ADR's staged delivery, and
  Movement C's reductions. "Flipped", the staging's word for `ADR-0.37.0`, is not carried:
  IOC reads that ADR's ledger state, and its own closeout says what landing requires.
- A waypoint is sequencing, so its home is the campaign plan, not the PRD. The PRD amendment
  pass keeps the four stale items only.

What it does not settle: the IOC-before-FOC ordering is NOT VERIFIED against a primary text
(source entry *initial and full operational capability*); and the identifier migration was
ruled "at IOC" on 2026-10-05, when IOC meant 1.0, so its timing is a new frontier item.

*Avoid* "IOC" for 1.0. *Avoid* "post-IOC by default".

**commissions:** 4 — the IOC waypoint drafted as a campaign-plan amendment, carried in the
republish; the Fielding rows corrected.

## decision · the constitution is drafted small, with the concept of operations

Frontier item 10 was opened by the placement ruling: the concept of operations sits under a
root that has no document (source entry *repository canon on the unwritten constitution*).
Put 2026-10-07 with three answers: draft it small with row 4; propose it as an engineering
order; leave it where canon books it. Operator selection, verbatim: 'Draft it small, with
row 4 (Recommended)'.

What the ruling fixes:

- Row 4 gains a constitution in `Draft`, created through `gz constitute` and ratified by the
  operator through that artifact's own lifecycle. It is small by design: the general orders
  (decision *general orders exist and are tiny*), the four principles the user charter
  carries, and a pointer to the never-relax floor (`gate5_invariants`, a code constant). It
  restates no value that code or JSON holds.
- The tree is not rewired here. `PRD.parent`, the bridging of ADRs that name the PRD as
  parent, and the rendering of the spine across surfaces stay with § 6 Movement C's open box.
- The 2026-06-14 coupling binds the draft: "the charter is authored, the
  constitutional-invariant registry ... + AGENTS.md are its mechanical render". The drafted
  text must agree with that registry, and where they differ the difference is put to the
  operator, not settled in the draft.
- The general orders move home. Their commission was "the universal contract's irreducible
  core"; they are authored in the constitution, and `AGENTS.md` carries them as its render,
  through the corpus and never by direct edit.
- The two charters are not retired or absorbed by this ruling. Their Gate 5 defect is row
  2(a); whether the constitution supersedes either charter is put when the draft exists.

Why row 4 and not row 1, by the admission question: the decision is surprising without
context and a real trade-off, but a `Draft` the operator has not ratified is cheap to
reverse, so it does not need an ADR to exist. The wiring that would be hard to reverse is
left where the campaign plan already books it.

The three candidate orders remain the agent's draft and not operator wording: report
truthfully; call knock-it-off when lost or blocked; never forge evidence.

**commissions:** 4 — a constitution in `Draft` through `gz constitute`, for the operator's
ratification, drafted with the concept of operations.

## decision · the public texts are supplied before their rows are drafted

Frontier item 9 asked whether a doctrine row may rest on an inference where a standard's
text is unread, or must wait. It was first put 2026-10-07 with a list that wrongly counted
the operator's own IEEE corpus as unread; the operator corrected it (source entry *the
operator's standards corpus*) and the question was put again over the seven texts that
remain, with three answers: A, label and proceed; B, the operator supplies the five public
documents first, before any row they carry is drafted, while DO-178C and MSG-3 stay
labelled; C, wait for all seven. Operator, verbatim: 'b'.

What the ruling fixes:

- Five texts are read before the rows they carry are drafted into doctrine: JP 3-60 (combat
  assessment, BDA, MEA, CDE, the prioritised target list, weaponeering); JP 3-30 (tasking
  order, operations centre, special instructions); FAA Order JO 7110.65 Appendix A (watch,
  position relief briefing); FAA AC 121-22 (maintenance review board, letter checks); and
  the acquisition glossary's entries for IOC and FOC (the two Fielding rows).
- The operator supplies them. They are public U.S. government documents whose hosts refuse
  automated retrieval, and the session does not work around that refusal. The IEEE series'
  precedent for a public government text is to vendor it with provenance and a checksum
  (`docs/governance/ieee/references/`); each lands under `docs/rnd/renewing-vows/sources/`
  with a `source` entry here when it arrives.
- Rows carried by DO-178C and MSG-3 may be drafted with their labels: a term is used as
  gzkit's own word, a claim about the standard needs a VERIFIED row, and a secondary source
  is cited as secondary (`src-parasoft-do-178c-overview.md`).
- The rest of row 4 is not held: the concept of operations' frame, placement, rhythm and
  integrity-level rows, the constitution draft, the weaponeering rule, the model-and-effort
  table and the corrections to the IEEE record rest on text already read.
- Rulings already made on rows these texts carry stand as rulings (the combat register at
  full strength, the IOC waypoint). What waits is their wording in doctrine.

This closes frontier item 6 with it: the verification pass has no open decision left, and
its remainder is this condition on row 4.

**commissions:** 4 — as a condition on that row, not a new item.

## decision · re-entry on 2026-10-07, on the operator's invocation

Operator g0, invocation of 2026-10-07 (09:10Z), verbatim:

> /gz-rnd docs/rnd/renewing-vows.md.

The run re-enters open and at its state of 2026-10-06: no frontier item ruled, no row given
a go, no sign-off.

**What happened between the open and this re-entry.** A session on 2026-10-07 resumed the
run from a handoff without the skill being invoked, put frontier questions 1 to 3 to the
operator and wrote three decision entries, two source entries and changed rows into this
record. The operator course-corrected (insight 2026-10-07T08:56:56Z, verbatim: 'If you are
"phantom" running that skill now, then I want to do it properly. What is going on?') and
directed the revert (commit `40ec9248e`, verbatim: 'revert today's edits to the renewing-vows
record so i can start correctly'). The record was restored to its content at `e00f12c77`;
checked at re-entry, before any edit (`git diff --quiet e00f12c77 HEAD --
docs/rnd/renewing-vows.md`, exit 0).

**Standing of the reverted material.** The edits stay in history (`176d1e5a2`, `bb711d52a`,
`af728b61d`) and were read at re-entry as a 302-line diff. They carry no authority in this
run. The three selections made there are not rulings of this run: the operator withdrew them
with the revert, and none is in the rulings store or the insights file. The canon that
session cited is re-read by this session before it is relied on. Each of the three questions
is asked again, one at a time, with the operator's earlier selection named beside the
options so that the operator rules with it in view.

**Not this run's.** The handoff the session-start hook surfaced
(`20261007T065152Z`) advises four other steps; this invocation is the R&D run only. The gap
that let a run be resumed without its skill (insight 2026-10-07T08:56:56Z, scope
`rnd-discipline:offer-and-resume`: no seated offer rule, no resume step in the skill, no
handoff line naming the invocation) is tracked by that insight and is not a row of this run
unless the operator adds it.

No ledger event was emitted.

---

## Disposition map

<!-- All six rows always present. State is `commissioned` or `not pursued` — there is no
     third state. The states below are the agent's draft; the operator rules each row at
     the close, and no row executes before the operator's go on that row. -->

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | commissioned | Proposed only, after briefs 15–20: engineering orders for the crew split (constraints, red, green) with the tasking event and the sortie matrix; the integrity-level axis beside lane (the consequence bands, witnessed by a scored-surface registry and an overlap floor), conditional on the operator lifting PROVISIONAL on the bands; combat assessment with a collateral owner and one assessment record; the maintenance record entry (one ledger event per chore run, replacing the PASS block as the run witness; findings are not events — ruled 2026-10-07). The identifier migration is row 5 and is timed to 1.0. | Each passes the admission question — hard to reverse, surprising without this record, a real trade-off; each depends on the spine. The operator initiates, or not (IRON LAW). |
| 2 | GHI / direct fix | commissioned | (a) The four theatre-canon staleness items (insight 21:34:40: dead constitution link; stale non-goal; INV-007 vs ADR-0.0.36; lodestar README vs Boundary #5) via `ghi-author`, and a fifth of the same class found 2026-10-07 (insight 2026-10-07T09:27:46Z: both published charters scope Gate 5 to the heavy lane against ADR-0.0.36). (b) Routing of the malformed `@covers` tags insight 21:30:15 recorded (525 findings on 2026-10-05; re-measured 2026-10-06, still present): one GHI for direct repair of foundation-era tags to REQ ids, or a parser rule for OBPI-id tags — the operator picks. (c) Nothing lints Markdown under `docs/`: `run_pymarkdown` has no caller, the `lint()` docstring names a linter that never runs, and pymarkdown is not installed or declared (insight 2026-10-06T10:49:46Z; found in passing by the research pass, verified by the session). Route: a direct fix of the docstring and the dead function, or a dependency decision under STDLIB-FIRST — the operator picks. | Defects by the PRIME DIRECTIVE, each tracked by an insight line today. Item 10's run has completed and no lock is held, so (b) is no longer another session's. Filing waits on the operator's go on this row. |
| 3 | chore | commissioned | Advise only: sort per-flight conformance checks off the interval board into `gz check`; package due interval tasks into named visits (letter checks); two announcements for admission — the campaign plan's republish coming due on accumulated amendments, and the maintenance visit coming due from the board (ruled 2026-10-07). | The board's 35 overdue of 40 (measured 2026-10-05 and again 2026-10-07) is the signature of per-flight work on an interval board. Both announcements follow the ratified posture: they announce and gate nothing. The operator directs admission. |
| 4 | control surface, rule, doc, skill, hook | commissioned | The concept of operations in the doctrine library, seated under the constitution and above the PRD and the campaign plan, with its rhythm section (the session tier as ruled 2026-07-18; two slower tiers, advisory until signalled); the campaign plan republished naming it and carrying the IOC waypoint as an amendment; a PRD amendment pass (the four stale items); the weaponeering rule text; the model-and-effort table in `model-selection.md`, describing the mechanism as the harness has it; a small constitution in `Draft` through `gz constitute` (the general orders, the four charter principles, a pointer to the floor), for the operator's ratification; the ladder's name selection recorded at IEEE § Q-18, the candidates table and campaign § Amendments 2026-10-04 (3); the nomenclature terms, held here until the glossary home is named. | The deliverable of this run; the operator's go on this row is the fund. The placement is ruled (2026-10-07: under the constitution, above the PRD), so the first two no longer wait on it. Source condition (ruled 2026-10-07, 'b'): rows carried by JP 3-60, JP 3-30, JO 7110.65 Appendix A, AC 121-22 and the IOC and FOC glossary entries are not drafted into doctrine until the operator supplies those texts and they are read; rows carried by DO-178C and MSG-3 are drafted with their labels; everything else in this row rests on text already read. |
| 5 | one-shot refactoring | commissioned | Identifier migration ECP / EO / WP via `gz migrate-semver`, aliases before, timed to 1.0 (full operational capability). | Ruled 'A' (insight 22:03:25) "at IOC" when IOC named 1.0; the PRD-per-major rule puts it at the major boundary, and the 2026-10-07 IOC ruling moved the word, not the timing. Proposed as a program; the operator selects its route. |
| 6 | no action | not pursued | Do not build: an `issue-ato` CLI verb from the dialogue; an AST radar as a separate tool; "halt after N amnesiac turns"; a civil softening of the combat register. Withdrawn on 2026-10-07, each in its decision entry: assurance level as the lane criterion; the concept of operations as a new root above the constitution; chore findings as ledger events; a calendar cadence held by hand, and a flown sortie per operation; a shortened 1.0 set under the name IOC; a handoff replaced by "the account". | The airlock already parses; `BLOCKED` to the operator is the better escalation; the softening was withdrawn by the operator (insight 22:03:25). The 2026-10-07 items are each closed by a carried ruling or by the operator's selection that day: the lane rulings of 2026-09-23 and 2026-09-25; the 2026-06-14 root ruling; 'Runs yes, findings no'; 'Two slower tiers, signal-triggered'; 'Nothing — move the date instead' (2026-08-17); the 2026-07-18 rhythm. A rejected idea here is re-opened only by the operator. |

## Close

**Challenge restated.** Restated on purpose, 2026-10-07, with the frontier empty. It is the
agent's wording for the operator to accept or replace at sign-off.

The operator asked for a mid-stream reconceptualisation of gzkit to be converged, in a
military and aviation frame, with ultimate names and an honest account of how much of the
remedy is already planned. As the run leaves it: gzkit's trouble is not a shortage of
controls. It is that every control addresses every agent as though that agent could hold
the whole. The direction, in the operator's words, is 'a series of much smaller, and much
more focused agents, being orchestrated, often by skill-driven workflow'. Nearly all of the
machinery that direction needs is in flight or queued in the ruled order: the runtime that
holds a run's position (briefs 15 to 20), the second opinion (`ADR-0.36.0`), the airlock's
bite (`ADR-0.37.0`) and the first flight test (`ADR-0.38.0`). What was missing is the
statement those pieces answer to, and its seat.

So the problem this run defines is a missing document and the six things it has to settle:
a concept of operations seated under a small written constitution and above the PRD and the
campaign plan; the names, with the artifact ladder migrating at 1.0; a second axis, integrity
level, for how much rigour a surface deserves; a ledger record for maintenance performed; a
rhythm whose slower beats come due on a signal and not on a calendar; and a near waypoint,
the first sortie flown on someone else's substrate, ahead of a 1.0 from which nothing is
removed. The run defines these and builds none of them.

**Frontier.** Open at 2026-10-06, in the order the run asks them, one at a time. Re-entered
2026-10-07 with all nine open (decision *re-entry on 2026-10-07*):

1. *Closed 2026-10-07 by ruling* (decision *placement is the apex, not a sidecar*): under
   the constitution, above the PRD and the campaign plan.
2. *Closed 2026-10-07 by ruling* (decision *the consequence bands are a second axis beside
   lane*): lane keeps its criterion; the bands are proposed as a second axis, named
   integrity level.
3. *Closed 2026-10-07 by ruling* (decision *a chore run is a ledger event; a chore finding
   is not*).
4. *Closed 2026-10-07 by ruling* (decision *the method is a battle rhythm*): the session
   tier as ratified 2026-07-18, plus two slower tiers that come due on a signal.
5. *Closed 2026-10-07 by ruling* (decision *the IOC set*): IOC is a waypoint before 1.0;
   1.0 is full operational capability with § 5 untouched.
6. *Closed 2026-10-07 with item 9* (decision *the public texts are supplied before their rows
   are drafted*): the pass has no open decision; its remainder is a condition on row 4. Five
   public texts wait on the operator; DO-178C and MSG-3 stay labelled; the operator's IEEE
   corpus already holds the four standards this item called paid.
7. *Closed 2026-10-07 by fact*: the slug is `renewing-vows`. The operator invoked the run by
   that name twice (the staging file on 2026-10-06, this record's path on 2026-10-07) and
   vetoed neither time.
8. *Not a frontier decision; restated 2026-10-07.* The go on each row is the consultation
   point the skill pre-declares for executing that row. It follows sign-off and is not a
   condition of it. No row has a go.
9. *Closed 2026-10-07 by ruling* (same decision): 'b' — the operator supplies the five
   public texts before the rows they carry are drafted.
10. *Opened and closed 2026-10-07 by ruling* (decision *the constitution is drafted small,
    with the concept of operations*): the root gets a small `Draft` under row 4; the tree's
    rewiring stays with Movement C.
11. *Opened and closed 2026-10-07 by carry-forward* (decision *ultimate nomenclature for the
    artifact ladder*): the migration was ruled "at IOC" when IOC meant 1.0; it stays timed
    to 1.0. Not a new ruling; the operator may re-rule it with the go on row 5.

Closed by fact on 2026-10-06: the effort mechanism (decision *effort rides on the agent
definition*).

**Sign-off.** 'Fund (Recommended)' — fund. Operator g0, 2026-10-07, selecting between fund
and kill with the mechanical condition met: the frontier empty, the challenge restated above,
and all six rows carrying a decision. The restatement was put with the question and was not
replaced. Diamond 1 is closed. The sign-off gives no row its go: rows 1 to 5 each wait for
the operator's go on that row, and no ledger event was emitted, because the run's event
types land with their producer.

## What this record does not license

No ADR, OBPI or chore is started by this run, funded or not. Rows 1–5 await the operator's go on each row;
row 6 names what is not built. No ledger event was emitted for the run. The licensed book is
cited, never copied; copyrighted standards land as citation records only. The operator's
identity is recorded as g0 and no personal address appears. The staging file in the prior
session's scratch directory is superseded by this record and carries no authority of its own.
