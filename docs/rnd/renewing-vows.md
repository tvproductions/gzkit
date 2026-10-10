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

## source · FAA Order JO 7110.65BB, Appendix A, supplied by the operator 2026-10-07

`docs/rnd/renewing-vows/sources/us-gov-faa-jo-7110-65-position-relief.md` · the operator's
whole message was the path to a PDF outside the repository,
`7110.65BB_Bsc_w_Chg_1_2_and_3_dtd_7-9-26_Final.pdf` (927 pages; SHA-256 in the source
file) · read by this session 2026-10-07: the title page, paragraph 2−1−24, Appendix A in
full (its two table pages also as page images), and the Change 3 explanation; the rest of
the order was searched, not read.

This is the first of the five public texts the ruling of this date ('b') made a condition on
row 4. It arrived after sign-off and lands under that condition; it changes no ruling. The
PDF is not vendored. Appendix A is quoted in full in the source file. Three lines, verbatim:

> Major problems occur whenever there is a heavy reliance upon memory, unsupported by
> routines or systematic reminders. (Appendix A § 2b)

> The relieving specialist and the specialist being relieved must share equal
> responsibility for the completeness and accuracy of the position relief briefing. (§ 5c)

> Specialists engaged in a position relief briefing for transfer of position responsibility
> must reference the position relief checklist developed by the facility in accordance with
> FAA Order JO 7210.3, paragraph 2−2−4 (§ 5e, added by Change 3, 7/9/26)

Verdicts on the five claims the file carried as NOT VERIFIED: four verified, one of them in
part; one contradicted in part. The paragraph is 2−1−24 and is titled "TRANSFER OF POSITION
RESPONSIBILITY", not "Position Relief Briefing"; it prescribes nothing itself and points to
Appendix A.

What the text gives the nomenclature row "session, handoff → watch, position relief
briefing":

- The process has four parts in a fixed order: preview the position; verbal briefing;
  assumption of position responsibility; review the position. The transfer is its own part.
- The preview belongs to the relieving specialist alone and comes first, from the status
  displays: "a self−briefing concept". Talk is for "Up to the moment information".
- The review belongs mostly to the specialist being relieved, who stays to check for "known
  omissions, updates, or inaccuracies" and signs the other on.
- The briefing's subject is "position responsibility". The order's noun for the thing
  handed over is the position. "Watch" does not come from this text; that half of the row
  still has no source.
- The checklist's required content is governed by FAA Order JO 7210.3 paragraph 2−2−4,
  which this run has not read.

A defect found in the reading, recorded as an insight (scope
`campaign-plan:position-relief-quotations`): the campaign plan's § Amendments 2026-08-17 C
sets five phrases in quotation marks as the FAA's ("... share equal responsibility for the
completeness and accuracy of the transfer", "confirms SIA data accuracy", "preview
complete, begin briefing", "I assume position responsibility", a "monitor jack"). None
occurs anywhere in this copy of the order. They may come from JO 7210.3, an earlier edition
or a paraphrase. The plan's mapping of four beats survives the text; its quotations do not
match it.

Bears on the challenge: the handoff row can now be drafted for its "position relief
briefing" half. Four texts remain with the operator: JP 3-60, JP 3-30, AC 121-22 and the IOC
and FOC glossary entries.

## source · FAA AC 121-22D, supplied by the operator 2026-10-07

`docs/rnd/renewing-vows/sources/us-gov-faa-ac-121-22-mrb.md` · the operator's whole message
was the path to a PDF outside the repository, `AC_121-22D.pdf` (10 pages; SHA-256 in the
source file) · read in full by this session 2026-10-07.

The second of the five public texts, landed after sign-off under the same condition; it
changes no ruling. The PDF is not vendored. Three lines, verbatim:

> After FAA approval, the requirements become a basis upon which operators develop their
> own individual maintenance programs. (§ 1.1)

> an MRB formally consists of only FAA personnel. ... The resulting report (MRBR or MTBR) is
> produced and owned by the OEM/TCH, accepted by the Industry Steering Committee (ISC), and
> approved by the FAA. (§ 8.1)

> A system for the periodic evaluation of all tasks in the program to eliminate those that
> are no longer applicable and effective. (§ 14.5.2, item 4)

Verdicts on the four claims the file carried as NOT VERIFIED: one contradicted (the current
revision is D, dated 5/31/24, and it cancels C), two verified, one verified in part (the
board's detailed procedure has moved to FAA Order 8900.1 and to the International MRB/MTB
Process Standard, neither read).

What the text gives the Airworthiness rows:

- The subject is "minimum scheduled maintenance tasking/interval requirements". There are
  two layers with two owners: the manufacturer's minimum list, and each operator's own
  program built from it.
- The test for a task is "applicable and effective", applied when a task is added and again,
  periodically, to remove tasks that no longer pass. Intervals are adjusted from evidence
  ("age exploration"). The list is "a dynamic report".
- A task is validated by performing it: "the procedure can be performed as written and ...
  meets the intent".
- MSG-3 is confirmed as the method the board works through.

What the text does not give, and this matters to the table: "letter check", "A-check",
"C-check", "Maintenance Planning Document" and "continuous airworthiness maintenance
program" occur nowhere in it. With the finding of 2026-10-06 that Title 14 carries no letter
check either, the operator's mapping of 2026-10-05 ('chore is level A-D airframe checks')
has no primary text behind it in this run. It is industry practice; its source would be
MSG-3 itself or a manufacturer's planning document, neither in hand. The row "maintenance
planning document" has no source here either.

One disanalogy the text makes plain: the board is the regulator's, and gzkit has no
regulator. What carries across is the manufacturer and operator split, which is the agent's
reading and not the circular's: a delivered minimum list and a project's own program built
on it.

Bears on the challenge: of the five public texts, two are landed. Three remain with the
operator: JP 3-60, JP 3-30 and the IOC and FOC glossary entries.

## source · JP 3-30, Joint Air Operations, supplied by the operator 2026-10-07

`docs/rnd/renewing-vows/sources/us-gov-jp-3-30.md` · the operator's whole message was the
path to a PDF outside the repository, `JointAirOperations_jp3_30.pdf` (134 pages, the
edition of 25 July 2019; SHA-256 in the source file) · read by this session 2026-10-07: the
Preface, Chapter I §§ 2 and 3, Chapter III § 6 with its figures, the first page of
Appendix E and the glossary definitions the file quotes; the rest was searched, not read.

The third of the five public texts, landed after sign-off under the same condition; it
changes no ruling. The PDF is not vendored. Three lines, verbatim:

> No single commander or headquarters can have the necessary situational awareness or
> maintain the tempo of operations required to effectively execute tactical operations in a
> highly dynamic combat environment. (Chapter I § 3b(4))

> sortie. In air operations, an operational flight by one aircraft. (Glossary)

> The battle rhythm is a detailed timeline that lists a series of briefings, meetings, etc.,
> to produce specific products by a specified time to support decision making.
> (Chapter III § 6b)

All five claims the file carried as NOT VERIFIED are verified, one in the publication's
wording: the centre is "A jointly staffed facility established for planning, directing, and
executing joint air operations" and "the centralized control node for tasking"; "senior" is
not the publication's word.

What the text gives the Operations rows:

- **The frame's central sentence is in the doctrine.** The first quotation is the problem
  this run restated at its close, in the source's words. The publication's remedy is
  "centralized control and decentralized execution", with a warning against centralized
  execution even where technology allows it.
- **Sortie and mission are distinct, and the table has them the right way round.** A sortie
  is one flight by one aircraft; a mission is "The dispatching of one or more aircraft to
  accomplish one particular task." A pipeline run as the mission and a dispatch as the
  sortie agrees with both definitions.
- **The tasking order** is "A method used to task and disseminate ... projected sorties,
  capabilities, and/or forces to targets and specific missions", for one execution period,
  "normally 24 hours", with several orders in different stages at once.
- **Special instructions are "located in the air tasking order".** Standing guidance travels
  inside the order. That is the mechanism the general-orders decision assumed.
- **Detail scales with coordination**: "very explicit" when several bases or components
  fly together, "less detail" for one.
- **The cycle has six named stages**: objectives, effects and guidance; target development;
  weaponeering and allocation; order production and dissemination; execution planning and
  force execution; assessment. Assessment "includes a determination and assessment of
  actual collateral damage".
- **The prioritised target list** is the product of target development "when approved by
  the JFC": the commander approves the list, and the centre does not.
- **The centre is told of every redirection**, including one a delegated commander makes.

Three places where the text does not support what this record holds:

- **"Battle rhythm" means a timeline by the clock.** The publication's rhythm lists events
  "by a specified time", and it calls its cycle "time-dependent, built around finite time
  periods". The operator ruled this day that gzkit's two slower tiers come due on a signal
  and never on a calendar. The ruling stands; the name on its decision entry borrows a term
  that means the opposite arrangement. Either the name is kept as a stated departure or
  another is chosen. That is the operator's to rule.
- **"Weaponeering" may be the wrong half of its stage.** In stage 3, weaponeering matches
  weapons and aimpoints to an approved target, and allocation turns the commander's
  priorities into "a total number of sorties by weapon system type available for each
  objective and task". The rule this record calls weaponeering fixes which sorties fly for
  a kind of requirement, which reads closer to allocation. JP 3-60 defines weaponeering and
  is not yet read; the name is not settled until it is.
- **"Duty officer" and "MISREP" have no source here.** The centre has a director; the only
  duty officer named is the senior intelligence duty officer. "Mission reports" appears once,
  undefined, in a figure; "MISREP" does not occur.

Bears on the challenge: three of the five public texts are landed. Two remain with the
operator: JP 3-60 and the IOC and FOC glossary entries.

## source · JP 3-60, Joint Targeting (2013 edition), supplied by the operator 2026-10-07

`docs/rnd/renewing-vows/sources/us-gov-jp-3-60.md` · the operator's whole message was the
path to a PDF outside the repository, `Joint_Chiefs-Joint_Targeting_20130131.pdf`
(138 pages; SHA-256 in the source file) · read by this session 2026-10-07: the Preface,
Chapter II § 3 through the opening of phase 5, Appendix D § 2b to § 2e and the glossary
definitions the file quotes; the rest was searched, not read.

The fourth of the five public texts, landed after sign-off under the same condition; it
changes no ruling. The PDF is not vendored.

**The edition matters.** This copy is dated 31 January 2013. Search results on 2026-10-06
listed a 28 September 2018 edition, unread and unconfirmed. If it exists this copy is
superseded, and JP 3-30, read today, is itself dated 2019. Every verdict below is against
the 2013 text, which may be cited as that edition and not as current joint doctrine.

Three lines, verbatim:

> CA is composed of three related elements: BDA, MEA, and reattack recommendations or
> future targeting. (Appendix D § 2d)

> weaponeering. The process of determining the quantity of a specific type of lethal or
> nonlethal means required to create a desired effect on a given target. (Glossary)

> BDA must be treated as an integral component of the joint targeting process and must not
> be conducted as a separate, post-attack activity. (Appendix D § 2d(1))

Of the seven claims the file carried as NOT VERIFIED: five verified, one verified in part
(collateral damage estimation is described and its method lives in CJCSI 3160.01, unread),
and the edition's currency stays not verified.

What the text gives the combat register:

- **Combat assessment has the three parts this record gave it**, and battle damage
  assessment has three widening phases: physical damage, functional damage, target system.
  The publication's spelling is "reattack".
- **Weaponeering is the right name for the rule this record gave it.** The definition is
  quantity and type of means for a given target, which is what "the requirement kind fixes
  the sortie set" decides. This answers the doubt the JP 3-30 entry raised: allocation is
  how the air component divides sorties across objectives; weaponeering is what one target
  needs.
- **Collateral damage is estimated before and assessed after.** The estimate is part of
  capabilities analysis, "normally performed by trained and certified personnel"; and
  "Collateral damage is also assessed and reported during BDA." Both halves have an owner
  in the doctrine. The decision that chase and damage assessment are two roles found the
  second half unowned in gzkit.
- **The crew's own report is an input, never the verdict.** "MISREPs" is this publication's
  term, so the mission-report row has its source. Mission reports are one source among
  several, the first report is "usually derived from a single source", and "The command
  designated BDA cell is responsible for collating reports and making the final
  assessment."
- **Assessment is planned at the start.** Measures are developed in phase 1, and reattack
  is judged against "predetermined MOEs that were developed at the start of the joint
  targeting cycle".
- **Munitions effectiveness compares actual with anticipated** so that the method changes:
  "methodology, tactics, weapon system". That is the question the regeneration test asks of
  a model and effort allocation.
- **Each assessment carries a confidence level and its sources**: CONFIRMED, PROBABLE,
  POSSIBLE.
- **Planners get the reasoning with the tasking**: "The work of mission planners is
  significantly enhanced when they are furnished with detailed insights into the reasoning
  that resulted in their unit tasking."
- **A target is revalidated during execution**, "to determine if planned targets still
  contribute to objectives (including changes to plans and objectives)".
- **Two fences the table does not yet have**: a no-strike list of protected objects, and a
  restricted target, "a valid target that has specific restrictions placed on the actions
  authorized against it". They fit denied and allowed paths more closely than rules of
  engagement do.

Two places where the text sits against canon or this record:

- **The prioritised list is not the firing order.** "Often, targets are not attacked in the
  same priority order as they appear on the JIPTL." The campaign plan's ascending order is
  absolute by the operator's ruling. The row "sequenced campaign items → prioritised target
  list" names a list that, in its source, the planners may fly out of order. The ruling
  governs; the analogy is looser than the row suggests.
- **The targeting cycle is "not time-constrained nor rigidly sequential."** JP 3-30 calls
  the air tasking cycle "time-dependent". The doctrine keeps two cycles, one paced by the
  clock and one not. That bears on the battle-rhythm name raised in the JP 3-30 entry: the
  operator's signal-triggered tiers resemble the targeting cycle's pacing, not the tasking
  cycle's.

Bears on the challenge: four of the five public texts are landed, one of them in a
probably superseded edition. One remains with the operator: the IOC and FOC glossary
entries.

## source · FAR Part 2, Definitions of Words and Terms, supplied by the operator 2026-10-07

`docs/rnd/renewing-vows/sources/us-gov-far-part-2-definitions.md` · the operator's whole
message was the path to a PDF outside the repository,
`Part-2---Definitions-of-Words-and-Terms.pdf` (36 pages, exported 2026-10-07; SHA-256 in the
source file) · read by this session 2026-10-07: the whole text searched, the list of 219
defined terms read in full, fourteen definitions read in full.

Supplied as the fifth text, for the definitions of initial and full operational capability.
**It does not contain them.** The file is Part 2 of the Federal Acquisition Regulation, the
contracting regulation. "Operational capability", "IOC", "FOC", "fielding" and "milestone"
occur nowhere in it. The two Fielding rows therefore stay as they were: ruled by the
operator on this date, and NOT VERIFIED against any primary text. The terms belong to the
defense acquisition system; by the agent's memory, unverified, they are defined in the
Defense Acquisition University glossary, which refused retrieval on this date.

One line, verbatim, that the run can use:

> Latent defect means a defect that exists at the time of acceptance but cannot be
> discovered by a reasonable inspection. (2.101)

What the text gives, beside the miss: a regulatory definition of "latent defect" that
matches the middle value of the detectability axis the integrity levels are built on;
"first article testing", a different idea from initial operational capability and not a
substitute for it; and "performance-based acquisition", results "as opposed to the manner by
which the work is to be performed", which is the contracting form of what JP 3-30 calls
mission-type orders. "Change order" and "task order" are defined there as orders under a
contract; the run's change proposal and tasking order do not rest on them.

Bears on the challenge: the condition the ruling of this date set on row 4 is met for four
of its five texts. The fifth, the IOC and FOC definitions, is still unread, so the Fielding
rows' wording still waits.

## source · Jacklin (NASA Ames) on DO-178C and DO-278A, supplied by the operator 2026-10-07

`docs/rnd/renewing-vows/sources/src-nasa-jacklin-2012-do-178c.md` · the operator's whole
message was the path to a PDF outside the repository, `20120016835.pdf` (14 pages; SHA-256
in the source file) · read in full by this session 2026-10-07.

It arrived after the run asked again for the IOC and FOC definitions. **It does not contain
them** either: it is a 2012 paper on software certification, and neither term occurs in it.
It is a source for the DO-178C rows, and a stronger one than the Parasoft page: its author
sat on RTCA Special Committee 205, which wrote DO-178C. It is still secondary. Cited with
short quotations; not vendored.

Two lines, verbatim:

> “Software level” in DO-178C was replaced with “assurance level” in DO-278A

> DO-178C states that the tools used to generate software or to verify software must
> themselves be verified to be correct. This tool verification process is called
> qualification. Moreover, a tool such as a compiler qualified for one project is not
> necessarily qualified for a different project.

What it gives the Assurance rows:

- **The severity model, from a committee member.** Its Table 1 keys each level to a
  "Software Failure Effect Category": catastrophic, hazardous, major, minor, no effect.
- **A correction to this record's attribution.** DO-178C's word is "software level".
  "Assurance level" is DO-278A's, for ground systems, and "development assurance level" is
  the system standard's. The decision that named the axis integrity level said DO-178C
  uses "assurance level"; it does not. The reason given there for avoiding the term is
  unchanged and now better founded: in RTCA usage an assurance level is assigned from the
  failure effect category.
- **Bidirectional traceability across six named pairs**, with its reason: "This assures
  that orphan source code and dead source code are not inadvertently produced."
- **Two kinds of coverage**, requirements-based and structural.
- **Tool qualification has a gradient that the table's row flattens.** DO-330 "places more
  stringent verification requirements on tools used to generate code than tools used to
  verify code", and a qualification does not travel between projects. A gzkit validator is
  a tool that verifies; an agent that writes code is a tool that generates.
- **Data that steers behaviour is verified like code.** Parameter data items are "data that
  influences the behavior of the software without modifying the executable object code" and
  get "the same verification process". gzkit's canon puts thresholds, rosters and state in
  JSON, which is such data.
- **Verification is not validation**: "DO-178C does not provide guidance for software
  validation testing".

What it leaves where it was: the number § 11.17, any count of objectives, and which
structural coverage criterion binds at which level.

Bears on the challenge: the DO-178C rows now stand on two secondary sources, one from
inside the committee, and on nothing for three clause-level details. The IOC and FOC
definitions are still unread after two attempts by the operator to supply them.

## source · the IOC definition, from the DSCA manual's glossary, read 2026-10-08

`docs/rnd/renewing-vows/sources/us-gov-dsca-esamm-glossary-ioc.md` ·
`https://samm.dsca.mil/node/8450` · fetched and read by this session 2026-10-08 (HTTP 200;
SHA-256 in the source file).

Found after the operator, asked whether the planning names should wait for JP 5-0, said,
verbatim: 'I want to see any relevant references'. An official Department of Defense site
carries the definition and attributes it to the Defense Acquisition University Glossary.
Verbatim:

> In general, attained when some units and/or organizations in the force structure
> scheduled to receive a system have received it and have the ability to employ and
> maintain it. The specifics for any particular system IOC are defined in that system's
> Capability Development Document (CDD) and updated CDD.

Verdicts: the IOC claim is VERIFIED. Full operational capability has no entry in this
manual's glossary and stays NOT VERIFIED, as does the ordering of the two in so many words.

What it gives the Fielding rows: the IOC row now stands on a primary text. And the second
sentence matters to the ruling of 2026-10-07: each system writes its own IOC conditions, so
gzkit naming its own (the four engineering orders landed, the first sortie flown, the stale
canon repaired) is the practice the definition describes, not a departure from it.

**JP 5-0, not reached.** A search listed copies of JP 5-0, *Joint Planning*, on five
official hosts. The session tried two, the National Defense University's and the Defense
Technical Information Center's; both answered HTTP 403. It tried no more and worked around
neither. The planning names proposed on 2026-10-08 therefore still rest on JP 3-60 and
JP 3-30 alone.

Bears on the challenge: of the two Fielding rows, one is sourced. Still unread and carrying
a row or a proposal: the FOC definition; JP 5-0.

## source · JP 3-60, Joint Targeting, 28 September 2018, supplied by the operator 2026-10-08

`docs/rnd/renewing-vows/sources/us-gov-jp-3-60-2018.md` · the operator's whole message was
the path to a PDF outside the repository, `21-F-0520_JP_3-60_9-28-2018.pdf` (133 pages, a
scan with OCR text; SHA-256 in the source file) · read by this session 2026-10-08: the
Preface, the Summary of Changes, Chapter II § 3 through phase 6 less the middle of phase 2
and the first three dynamic-targeting steps, Appendix D and the glossary by passage; the
cover and glossary page GL-10 as page images; the rest searched, not read.

This is the current edition the run lacked: "This publication supersedes JP 3-60, Joint
Targeting, 31 January 2013." The caveat on the combat register is lifted, and every row the
2013 copy carried is now cited to 2018. Not vendored. Three lines, verbatim:

> The joint targeting cycle is a six-phase iterative process that is not time-constrained
> nor rigidly sequential, as some steps in various phases may be conducted concurrently.

> (1) Upon receipt of component tasking orders, detailed, unit-level planning must be
> performed for the execution of operations.

> weaponeering. The process of determining the specific means required to create a desired
> effect on a given target. (Glossary, read from the page image)

All seven claims are verified against this edition, two of them in part. What the newer
text changes in this record:

- **Two phases are renamed.** Phase 1 is "Commander's Objectives, Targeting Guidance, and
  Intent"; phase 6 is "Combat Assessment", and the edition "replaces the term "targeting
  assessment" with "combat assessment" throughout". The core-model table is corrected.
- **Weaponeering's definition is shorter**: "the specific means required", where 2013 had
  "the quantity of a specific type of lethal or nonlethal means". The rule this record
  calls weaponeering still fits it.
- **The planning levels are named in the text.** Before the cycle: "operational planning",
  through "JPP mission analysis". After tasking: "detailed, unit-level planning" by "unit
  mission planners". This is the evidence the planning names of 2026-10-08 were waiting
  on, short of JP 5-0 itself.
- **A fragmentary order is a kind of tasking order.** Figure II-8: "Tasking Orders (e.g.,
  ATO, FRAGORD, OPORD, etc)". The row "campaign amendments → fragmentary orders" has its
  term; whether an amendment to a plan is a tasking order is another matter.
- **The no-strike list "is not a target list".**
- **The prioritised list has a cut line** that "does not guarantee that a specific target
  will be engaged", and "Targets may not be engaged in the same priority order as they
  appear on the JIPTL." The finding against the campaign-order row stands in the new text.
- **One sentence this record quoted is gone.** The 2013 effects estimate said "Sometimes
  this is done by a command's red team"; 2018 does not. The core-model table no longer
  quotes it.
- **A collateral decision is not mechanical**: it "will not be determined solely through a
  mechanistic or numeric process, nor will it be based on quantified casualty estimates
  alone."

Bears on the challenge: the combat register stands on the current edition. Still unread and
carrying a row or a proposal: JP 5-0; the FOC definition; FAA JO 7210.3; a crew resource
management text.

## source · FAA Order JO 7210.3EE, paragraph 2-2-4, read 2026-10-08

`docs/rnd/renewing-vows/sources/us-gov-faa-jo-7210-3-para-2-2-4.md` · read 2026-10-08 by this
session from the FAA's live HTML edition in the desktop app's browser pane (faa.gov answers
HTTP 403 to automated retrieval; the operator's list of 2026-10-08 named it). Edition: JO
7210.3EE, effective 7/9/2026, Change 3. The paragraph is quoted in full in the source file.
Verdicts: 5 verified, 1 not verified, 2 contradicted.

> The relieving specialist and the specialist being relieved must share equal responsibility
> for the completeness and the accuracy of the position relief briefing. (2-2-4)

What it settles. The checklist that JO 7110.65 Appendix A § 5e points to is facility-developed
and position-tailored, reviewed annually, with the Status Information Area first and traffic
last, managers free to add items, and the briefing recorded. The campaign plan's quotation
(§ Amendments 2026-08-17 C) ends "of the transfer"; the order's sentence ends "of the position
relief briefing", in both orders. The other four phrases the plan sets in quotation marks
occur in neither order, so they have no source. "Watch" is not this order's noun either; on
the page it names only the shift ("CIC of the watch").

Bears on the challenge: the handoff row can be drafted whole for its "position relief
briefing" half; the campaign plan's quotations are a defect to repair (insight
`campaign-plan:position-relief-quotations`, 2026-10-07, now with the second order read).

## source · DAU Glossary, initial and full operational capability, read 2026-10-08

`docs/rnd/renewing-vows/sources/us-gov-dau-glossary-ioc-foc.md` · read 2026-10-08 by this
session in the browser pane at the Adaptive Acquisition Framework page "IOC/FOC"
(`aaf.dau.edu/mca/ioc-foc/`, which redirects to `aaf.waru.edu`); both entries carry
"Reference Source: DAU Glossary". Verdicts: 4 verified, 1 not verified (the glossary's own
page was not reached).

> In general, attained when some units and/or organizations in the force structure scheduled
> to receive a system have received it and have the ability to employ and maintain it.
> (Initial Operational Capability)

Full operational capability reads the same with "all" for "some". Both say the specifics are
defined in the system's Capability Development Document. This closes the Fielding rows'
"not verified" label (frontier item 13, last bullet): the ruling of 2026-10-07, IOC a waypoint
before 1.0 and 1.0 full operational capability, now stands on the glossary's "some" and "all".

## source · Degani and Wiener, NASA CR-177549, The Normal Checklist (1990), read 2026-10-08

`docs/rnd/renewing-vows/sources/us-gov-nasa-cr-177549-degani-wiener-1990.md` · public domain;
read 2026-10-08 from the NASA Technical Reports Server as page images (§ 5.2, § 5.3, § 6.4 and
the contents). The crew-resource-management text the operator's list asked for, for
"pilot flying / pilot monitoring" and "challenge-and-response checklists". Verdicts: 5
verified.

> This technique of conducting the checklist undermines the concept behind the step-by-step
> challenge-and-response procedure. (§ 5.2.3)

What it settles: challenge-and-response is a named flight-deck method in which one pilot reads
each item and the other verifies and answers it, step by step, ending in a completion call;
its value is mutual supervision, two people and two looks, which memory and "chunking" defeat.
The roles are pilot flying and pilot not flying, alternating by leg without relieving the
captain of command; "pilot monitoring" is the later FAA term (AC 120-71B, on the operator's
download list) and is not in this text. The nomenclature rows "implementer, reviewers →
pilot flying, pilot monitoring" and "skills → challenge-and-response checklists" now rest on
a primary text for the method and the 1990 role names.

## source · Hayhurst et al., NASA/TM-2001-210876, MC/DC tutorial (2001), read 2026-10-08

`docs/rnd/renewing-vows/sources/us-gov-nasa-tm-2001-210876-hayhurst-mcdc.md` · public domain;
one author is FAA staff; read 2026-10-08 from the NASA Technical Reports Server as page images
(pages 1–10). Written against DO-178B and not regulatory guidance, by its own statement.
Verdicts: 2 verified for DO-178B, 2 not verified.

> objective 7 requires statement coverage for software levels A-C; objective 6 requires
> decision coverage for software levels A-B; objective 5 requires MC/DC for software level A
> (§ 2.3)

What it settles of DO-178C's three details: coverage per level, as DO-178B's Table A-7 set it
and public RTCA material says DO-178C kept it (statement A–C, decision A–B, MC/DC A, none at
D). What it does not: the § 11.17 number and the objective counts, which exist publicly only
in secondary sources; the standard itself (RTCA store, on the operator's list) is the only
verification, and the rows keep "clause unverified" until it is read.

## source · EASA Aircraft Maintenance Programme compliance checklist, read 2026-10-08

`docs/rnd/renewing-vows/sources/eu-easa-amp-compliance-checklist.md` · EASA form
TE.CAMO.00011-002, cited and quoted at two items only; read 2026-10-08 from the EASA download
as page images (pages 1–5 of 15). Verdicts: 1 verified, 2 not verified.

> 1.7 REFERENCE DOCUMENTS (minimum content – as applicable) — a) TCDS Data; b) MRBR; c) MPD;
> d) AMM Chapter 5 …

What it settles for the MSG-3 rows: the maintenance planning document is a recognised
reference document of a maintenance programme beside the MRB report (AMC M.A.302(d)). What it
does not: that the MPD derives from the MRB report, which is industry description; and
"letter check", which no regulatory text read in this run uses (not 14 CFR, not AC 121-22D,
not this checklist). The term is found in Air Force unit instructions and news releases
(e.g. Little Rock AFB Instruction 21-113, which faa.gov-style refuses automated retrieval) and
in industry explainers. MSG-3 itself is paid (A4A store, on the operator's list); the chore
row's "letter check" is operator practice layered on MSG-3 tasks, to be labelled as such.

## source · FAA AC 120-71B, procedures and the monitoring pilot, supplied by the operator 2026-10-08

`docs/rnd/renewing-vows/sources/us-gov-faa-ac-120-71b-sop-pm.md` · the operator's message
was the path to a PDF outside the repository, `AC_120-71B.pdf` (35 pages, dated 1/10/17;
SHA-256 in the source file) · read in full 2026-10-08 by the session the operator invoked on
2026-10-07 (see the note on two writers in the decision *two sessions are writing this
record*). Not vendored. Three lines, verbatim:

> 8. Pilot Monitoring (PM). The PM monitors the aircraft state and system status, calls out
> any perceived or potential deviations from the intended flightpath, and intervenes if
> necessary. (§ 1.4)

> 1. At any point in time during the flight, one pilot is the PF and one pilot is the PM.
> (§ 6.4)

> While it is important to document and communicate the rationale behind the procedure
> design, this information should be provided in a separate training manual or other
> document. (§ 4.1.1)

Verdicts: pilot flying, pilot monitoring and challenge and response are VERIFIED; the tie to
crew resource management in part; "assessor" and "briefer" are in no text read. It is the
later FAA text the Degani and Wiener entry above points to for "pilot monitoring".

What the text gives, and what it takes away:

- **The monitor works at the same time as the flyer.** One pilot flies and the other watches
  the same flight as it happens, calls deviations, and takes control "after two challenges".
  A review made after the work comes back is a different act. So the row "implementer,
  reviewers → pilot flying, pilot monitoring" has its terms sourced and its mapping wrong:
  gzkit's reviewers assess a returned product, which is phase 6 of the targeting cycle, and
  gzkit has no concurrent monitor of an agent at work other than its hooks.
- **A checklist is not the procedure.** The crew works a "flow" and then reads a short list
  of the critical items and of items that "confirm the flow was done correctly". A skill is
  a procedure in this sense; the per-change gate is the nearer analogue of a checklist.
- **A checklist starts on a cue**, and a "floating" start is "a high risk". Support from the
  flight deck for the ruling of 2026-10-07 that the slower tiers come due on a signal.
- **A transfer of roles is spoken, accepted and briefed**, "to include a short brief of
  aircraft state". A second source for the handoff.
- **How to write a procedure** agrees with gzkit's skill-authoring rule nearly point for
  point: only what is needed to execute; rationale kept elsewhere; emphasis rationed; "If
  possible, avoid creating new terms."
- **Monitoring decays when nothing goes wrong**, through "boredom, complacency, or both".

## source · gzkit's own command doctrine, read 2026-10-08 — and not read by this run before

`docs/governance/GovZero/command-doctrine.md` · read in full 2026-10-08 by the session the
operator invoked on 2026-10-07, after AC 120-71B's reading list named Degani and Wiener's
"four ‘P’s of flight deck operations" and a search of canon for that phrase found this file.

**The run had not read it.** It is in neither canon list of this record (2026-10-05 or
2026-10-07), and the placement and constitution questions were put to the operator without
it, against `AGENTS.md` § Operator Doctrine ("stop and read all docs and all code before
taking or recommending action"). Recorded as an insight (2026-10-08T07:35:42Z, scope
`gz-rnd:command-doctrine-unread`).

What the file is, in its own words:

> Status: Canonical doctrine (philosophy layer)
> Ratified: 2026-06-10 (operator-ratified relocation from working draft)

> **Philosophy** is the command doctrine below: ten articles stating what GovZero believes
> about authority, accountability, and automation, independent of any model, vendor, or
> tool.

Its subtitle: "A back-port of the aircrew accountability framing into the philosophy layer
of GovZero and gzkit". It orders four layers after Degani and Wiener (philosophy, policies,
procedures, practices), and Article 10 requires that "Every gate, check, and template in
gzkit must trace upward through a policy to an article of this doctrine." Three articles,
verbatim, that bear hardest on this run:

> ### Article 3. The model is a crew resource, not a crew member
>
> Crew resource management never promoted the first officer to command ... The model is
> used fully: it drafts, flags, surfaces, challenges, and proposes ... And the model decides
> nothing that ships.

> ### Article 2. Authority must be instrumented, not asserted
>
> ... Authority asserted in the context window is a briefing: necessary, and unenforceable.
> ... If the harness does not enforce it, the doctrine does not contain it.

> ### Article 4. Uncommanded change is an annunciation failure
>
> ... every run is preceded by a scope manifest, every run is followed by a diff of
> delivered work against commanded scope, and every artifact outside the manifest is
> annunciated before the run can pass any gate. The model is not asked to behave. The
> harness is built to notice.

Its worklist names a "captain's-brief structure: scope manifest, stop conditions, expected
artifacts, explicit prohibitions on out-of-scope change", a scope-conformance report, an
autonomy span parameter and a proficiency log, tracked in
`ADR-pool.command-doctrine-internalization`; its appendix scores Articles 5, 6 and 9 as gaps
and Articles 4 and 10 as partial.

What this does to the run:

- **The apex already has an occupant.** A ratified philosophy layer exists, in an aircrew
  frame, to which policies and procedures must trace. The ruling of 2026-10-07 seated a new
  concept of operations "under the constitution, above the PRD" without weighing where it
  sits against this doctrine, or whether it is this doctrine's policy layer. It was made on
  an incomplete reading and is to be put again.
- **The constitution ruling is in the same position.** The agent proposed three draft
  general orders and four charter principles. Ten ratified articles already state what
  gzkit believes about authority, accountability and automation, and none was offered.
- **Article 3 is against naming agents as pilots.** The table calls the implementer the
  pilot flying. The doctrine says the model is a crew resource and "decides nothing that
  ships"; the human who signs is the one in command (Article 1). The sortie roles ruled
  into the core model on 2026-10-08 are roles for agents and may stand; calling any of them
  a pilot does not agree with canon.
- **Article 4 already owns one of the two unowned assessment outputs.** A diff of delivered
  work against commanded scope is the assessment of what a change did beyond its target,
  and the doctrine's own appendix marks it "Partial — no post-run delivered-vs-commanded
  scope-conformance gate".
- **The tasking order has a ratified ancestor**: the captain's brief with its scope
  manifest.

Bears on the challenge: the run set out to supply a statement of how gzkit operates and did
not read the statement gzkit already ratified. The model, the names and the two rulings
above are to be reconciled with it before anything is drafted.

## source · four FAA circulars supplied by the operator 2026-10-08

Each was supplied as a path to a PDF outside the repository and read 2026-10-08 by the
session the operator invoked on 2026-10-07. None is vendored; each source file carries the
copy's checksum. They were written as source files while that session held off editing this
record (decision *two sessions are writing this record*), and entered here on the operator's
instruction of 2026-10-08, verbatim: 'Yes, use these:' above the list of the four.

**AC 20-115D, Airborne Software Development Assurance Using EUROCAE ED-12( ) and RTCA
DO-178( )** (07/21/2017) · `sources/us-gov-faa-ac-20-115d-do-178c.md` · read in full. The
regulator's own recognition of DO-178C, so a primary text for what the FAA says of the
standard. Verbatim:

> The system safety process assigns the minimum development assurance level based on the
> severity classifications of failure conditions for a given function. (§ 9b(2))

It verifies what two secondary sources had said: the severity model; "software level" as the
standard's word; objectives "as listed in the ED-12C/DO-178C Annex A tables"; section 11 as
the life cycle data; the date December 13, 2011; five tool qualification levels, with
development tools held to more than verification tools. It adds the change impact analysis:
"the extent of the modifications, the impact of those modifications, and what verification
is required". Still only in the standard: § 11.17, any count of objectives, level E.

**AC 00-71, Best Practices for Management of Open Problem Reports** (Sep 16, 2022) ·
`sources/us-gov-faa-ac-00-71-open-problem-reports.md` · read in full. Verbatim:

> Resolved – A problem report that has been corrected or fully mitigated, for which
> resolution of the problem has been verified but not formally reviewed and confirmed.
>
> Closed – A resolved problem report that underwent a formal review and confirmation of an
> effective resolution of the problem. (§ 3.2)

It defines the problem report ("adapted from DO-178C/ED-12C"), its four states (recorded,
classified, resolved, closed) and four classes taken one per report by priority
(significant, functional, process, life cycle data). An unverified requirement is classed
up, because its impact "remains undetermined".

**AC 20-189, Management of Open Problem Reports** (Sep 16, 2022) ·
`sources/us-gov-faa-ac-20-189-open-problem-reports.md` · read in full. The scheme itself.
Verbatim:

> OPRs classified as ‘Significant’ ... for which no sufficient mitigation or justification
> exists to substantiate the acceptability of the safety effect, should be resolved prior
> to approval. (§ 6.3)

An open report may ship if assessed and reported; a report not classed significant or
functional needs a "justification that the error cannot have a safety or functional
effect"; a problem found after approval goes through the same process, "and any related
systemic process issues should be identified and corrected."

What the pair gives the table: the GHI row's "problem report" has a primary definition and
a life cycle; and the row "operator hold → deferred defect (MEL item)" has a closer term in
the *open problem report*, "A problem report that has not reached the state ‘closed’ at the
time of approval".

**AC 120-16G, Air Carrier Maintenance Programs** (1/4/16) ·
`sources/us-gov-faa-ac-120-16g-maintenance-programs.md` · read: the cover statement,
§§ 1-4d to 1-7, § 3-3, §§ 5-3 to 5-5 and Chapter 6 in full; § 7-1 and three other passages
by search; the rest of its 60 pages searched, not read. Verbatim:

> The regulations are broad enough to permit you to organize all of these individual tasks
> into a series of integrated scheduled work packages of your own design (§ 6-1)

> A primary concept of the RII function is to prevent any person who performs any item of
> work from performing any required inspection of that work (§ 7-1c)

What it gives the Airworthiness rows: the packaged visit the operator's "letter check"
mapping reached for is a *scheduled work package*; chores against issues is *scheduled*
against *unscheduled maintenance*, the second arising from "scheduled maintenance tasks,
pilot reports, or unforeseen events"; "task cards" is another name for work cards; and
"engineering orders" is named among work documents. It also states that a program watches
itself (the continuing analysis and surveillance system), that "more maintenance is not
always a good idea", and that first intervals are judgment later validated by data.

On "work package": the circular's work package is a set of tasks packaged to be done
together. The artifact ladder's work package is one bounded assignment, which is also a set
of tasks worked as a unit. The sense is the same. What differs is the kind of task inside:
scheduled maintenance in one, new work in the other. The session first reported this to the
operator as two meanings; the operator asked, verbatim, 'work package: does it really have
two meanings?', and on rereading it does not.

## source · gzkit's own doctrine layer under `docs/governance/GovZero/`, read 2026-10-08

Read by session `6c08c9d9` after the re-entry of 2026-10-08 (decision of that name), because
the run had named two of this directory's documents and read one. **Read in full:** the
twenty-two documents other than `adr-status.md`, the three under `audits/` and the four under
`releases/`; and, outside the directory, `docs/governance/trust-doctrine.md` and
`docs/governance/ontology-ownership-plane-doctrine.md`. **Read in part:** `adr-status.md`,
header only (a generated table); `docs/governance/advisory-rules-audit.md`, lines 1 to 140 of
a 198,332-byte file, the rest unread. **Measured, a dated record:** `.gzkit/governance/
ontology.json` by script; `scope_audit` in `src/gzkit` and on the ledger (below).
`AGENTS.md` § Governance doctrine surfaces names the trust doctrine and the advisory-rules
audit as reading owed before governance work; this record had cited neither.

**1. The four layers have occupants. The empty one is policies.** The charter places
itself, verbatim:

> Gate definitions are *procedures* in the Four P's stack. They trace upward to the
> [GovZero command doctrine](command-doctrine.md) (philosophy layer, Article 10): the
> doctrine governs *why* the gates exist; this charter remains the sole authority for *what*
> the gates are.

Philosophy is the ten ratified articles. Procedures are the charter and the documents beside
it (items 2 to 4). Practice is the code. The command doctrine names its policies in one
sentence and no document states them.

**2. How one work package is flown is already written down.**
`obpi-pipeline-runbook.md` (version 2.0, `Status: Draft`, last reviewed 2026-03-17) gives
five stages and an owner for each: load (script), implement (agent), verify (script), attest
(human), sync (script). Verbatim:

> **Agent work is Stage 2 only.** Implementation is the one stage that requires creative
> problem-solving. Everything else is ceremony, verification, and accounting.

> **The skill is a dispatcher, not an engine.**

> **Stop on blockers, never work around.**

Its reason for subagents is "Context contamination", and a subagent returns `DONE |
DONE_WITH_CONCERNS | BLOCKED` with its files and test result. `obpi-transaction-contract.md`
(`Status: Active`): "An OBPI is not just a brief file or checklist row. It is a bounded
transaction with an explicit scope contract"; "Scope isolation is law, not guidance."; and
"Only one spine-touch OBPI may be active at a time", a spine surface being a lock file, a
registry, CI configuration or repository-wide doctrine.

**3. Article 4's report was built, recorded for a season, and has stopped.** The transaction
contract, verbatim: "Completion MUST fail closed when the changed-files audit shows a path
outside the allowlist." `obpi-runtime-contract.md`: a completed receipt carries
`scope_audit` with `allowlist`, `changed_files` and `out_of_scope_files`. Measured
2026-10-08: `build_scope_audit` is defined in `src/gzkit/hooks/obpi.py` and called only from
`src/gzkit/hooks/core.py`; `src/gzkit/commands/obpi_complete.py` does not name it. On the
ledger, 278 `obpi_receipt_emitted` lines carry `scope_audit`, and 102 of those list at least
one out-of-scope file, so the audit recorded and did not refuse. By month: 255 in March, 22
in April, one in June (2026-06-19, the last), none since, while the completed receipts
written without it number over three hundred (counted by a line filter, so approximate).
The command doctrine's own appendix, written 2026-06-10, scores Article 4 "Partial — no
post-run delivered-vs-commanded scope-conformance gate".

**4. How assessment reaches the human is written down.** `audit-protocol.md` (`Authority:
Canon`), verbatim:

> The agent presents **paths**, not **conclusions** ... The human **executes and observes
> directly**, with the agent as a silent index

> The agent cannot corrupt what it does not interpret.

It names the risk "mediated observation". The charter fixes the attestation forms:
Completed; Completed — Partial; Dropped.

**5. The instrument that measures whether a rule binds exists and is live.**
`advisory-rules-audit.md`, as far as read: every rule stated to agents is scored
**Mechanical**, **Promotable**, **Judgment** or **Ambiguous**; verbatim, "Every rule that
*could* be a test *should* be a test."; "A **Mechanical** score must cite its witness";
`gz validate --advisory-scorecard` fails closed on a rule bumped past its scored version. One
condition bears directly on this run: a Mechanical or Promotable row's text must appear in
the per-turn surface (`AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`) or in the skill or ADR
file it is attributed to. The command doctrine is none of those, so no article can be scored
until its text reaches the per-turn surface through the corpus.
`ADR-pool.command-doctrine-internalization` item 6 already names the route: "extend the
advisory-rules scorecard with a traces-to-article column".

**6. A second, dormant join table.** `governance-registry-design.md` (`Status: Draft`,
2026-02-15) designs Doctrine → Policy → Rule → Action objects, each rule with an enforcement
coverage of `automated`, `human-gated` or `gap` and each action with an authorization of
`autonomous`, `human-gated` or `prohibited`. Its problem statement, verbatim: "There is **no
join table**." and

> "What is the full set of constraints an agent must satisfy?"

On disk `.gzkit/governance/ontology.json` is version 0.1.0, last updated 2026-03-09: three
doctrines, one policy, one rule, thirteen actions; nothing under `src/gzkit` names the file.
`ontology-ownership-plane-doctrine.md` calls its schema "dormant". The ontology of
`ADR-0.32.0` is a different thing, a derived graph that "never gates".

**7. Release classes already carry the ladder's top.** `releases/README.md` (`Status:
DRAFT`, 2026-01-10): a major release's intent carrier is the PRD, a minor's is the ADR with
its OBPIs, a patch's is the GitHub issue. Verbatim: "A release is a governance assertion,
not a batch of commits."; "Large OBPI accumulation within a single minor is a drift
indicator; stop and reclassify."; and a list of "Authorized Agent Challenges" the agent is
required to raise. `adr-lifecycle.md` (`Authority: Canon`) holds an identifier scheme of its
own, `0.1.15-obpi.03` and `0.1.15-ghi.67`. `adr-obpi-ghi-audit-linkage.md`: "**OBPIs are
planned work.** ... **GHIs capture emergent work.**"

**8. Artifacts over narrative has its own doctrine.** `trust-doctrine.md`: "**Trust-chain
poisoning is not a bug. It is a class of bug.**", four trust layers T0 to T3 and three
invariants, each with a fail-closed audit. It is Article 7 in mechanical form.

**9. The handoff has a doctrine origin outside the ten articles.** `ADR-0.0.25` (Compounding
Engineering & Session Handoff Contract) and `session-handoff-obligations.md`; the registry
design's inventory lists it as `D-SESSION-CONTINUITY`.

**10. The directory is stale as a class, not in two charters.** Gate 5 is defined three
ways: the charter (human attestation, "Heavy lane only"); `gate5-architecture.md` ("Gate 5
enforces **code-documentation-intent alignment** for Heavy lane work"); the release doctrine
(gates named Intent, Design, Implementation, Verification, Human Attestation). The runtime
and transaction contracts scope attestation to heavy lane and foundation kind. The pipeline
runbook keeps an "Exception mode — self-close". `architectural-enforcement.md`,
`gate5-architecture.md` and `ledger-schema.md` carry AirlineOps paths and examples. The four
handoff documents store handoffs under the ADR package and say a fresh one is resumed
"directly". Most carry a last review between January and March 2026. Recorded as an insight
(2026-10-08, scope `theatre-canon:govzero-directory-staleness`).

**Also read, bearing less:** `obpi-decomposition-matrix.md` (`Authority: Canon`) sizes work
on five dimensions and heads its columns "Atomic (Lite)", "Modular (Heavy)", "Structural
(Foundation)", so a size scale is already tied to lane and kind; `layered-trust.md` numbers
tool layers 1 to 3 by their relation to evidence, a different numbering from the state
doctrine's; `agent-era-prompting-summary.md` and `architectural-enforcement.md`
("Documentation makes the right answer *findable*. It doesn't make it *unavoidable*.").

Bears on the challenge in five ways.

- What is missing is narrower than a doctrine. The philosophy is ratified. Procedures
  exist. An instrument that scores whether a rule binds exists. Missing are the policies
  layer, the trace from each procedure and check up to an article, the articles' reach into
  what an agent loads, and the currency of the procedure documents.
- `doctrine-merge.md` Part III drafts procedures beside canonical ones it does not name, and
  Part II's "Enforced today by" column is the scorecard's job done by hand in Markdown.
- "Collateral assessment has no owner" is wrong as stated. The delivered-against-commanded
  record had a producer and 278 receipts, and lapsed. That is a correction to shipped work,
  not a new capability.
- The six phases and eight roles describe the same work the five-stage pipeline describes.
  How the two relate has not been put to the operator.
- Row 5's identifiers and the ladder's names meet a canonical identifier scheme and a release
  doctrine this record had not read.

## source · the `gz-obpi-pipeline` skill, read in full 2026-10-08

`.gzkit/skills/gz-obpi-pipeline/SKILL.md`, skill-version 6.65.0, 1,709 lines, read in full by
session `6c08c9d9`. The core-model decision of 2026-10-07 read its stage diagram and
§ Persona Dispatch and searched the rest. Read beside it: § Part 1 of
`docs/governance/GovZero/obpi-pipeline-runbook.md` (Draft v2.0); `ROLE_PERSONA_MAP` in
`src/gzkit/pipeline_dispatch.py`; the marker stage set in `src/gzkit/commands/adr_audit.py`;
the rosters under `.gzkit/personas/` and `.claude/agents/`. The skill's three `references/`
files are not read.

What the text says:

1. **Five stages in one sequence.** "The pipeline executes 5 stages sequentially": load
   context, implement, verify, present evidence, sync and account. "THE PIPELINE IS NOT
   COMPLETE UNTIL STAGE 5 FINISHES." Planning sits ahead of it: "Planning happens in Claude
   Code's native plan mode. This pipeline picks up **after** the plan is approved".
2. **One session carries every stage.** The `pipeline-orchestrator` does inline: reading the
   plan receipt and the brief, claiming the lock, writing the markers, applying the allowlist
   "as the working scope contract", the justification gate, the baseline checks, the covers
   parity gate and the RED witness, the packet's replay, the closure narrative, completion,
   marker removal, two syncs and the handoff.
3. **Agents are dispatched at three stages.** Stage 2: an `implementer` per plan task, its
   model tier set by the count of allowed files, then a `spec-reviewer` and a
   `quality-reviewer` ("**Cannot execute** — reviews by reading"). Stage 3 Phase 2:
   verification subagents in worktrees, one per group of requirements. Stage 4: a `narrator`,
   and at Step 4b a second vendor's model working in "a THROWAWAY COPY of the reviewed
   source".
4. **Red and green are one agent's.** "RED — write ONE minimal test", "GREEN — write the
   simplest code", and "one implementer at a time, never parallel".
5. **Assessment is already layered.** In Stage 2, two readers per task and at most two fix
   cycles. In Stage 3, receipts, parity and the RED witness. In Stage 4, the replay of the
   packet and "an ACCEPTANCE REVIEW" by "the different eyes", bounded at three rounds, after
   which the agent is to "put the design to the operator".
6. **Release is the human's.** "Stage 4 = HUMAN GATE (wait for attestation) — universal per
   ADR-0.0.36".
7. **Recovery and cleanup are Stage 5.** Completion surrenders the lock; the markers are
   removed; "Two-sync pattern"; the adversary's checkout is deleted "when the round ends"; an
   abort surrenders the lock "with a recorded category".
8. **A dispatch is a ledger fact.** `stage2_dispatch_recorded`; "Credit is never inferred";
   "The Stage-4 narrator dispatch has no channel yet."
9. **What the runtime knows** (measured 2026-10-08): four roles in `ROLE_PERSONA_MAP`
   (Implementer, Reviewer, QualityReviewer, Narrator); five marker stages (implement, verify,
   ceremony, sync, audit); seven personas on disk and five agent definitions.

Where the texts disagree:

- The runbook's second design principle is "Agent work is Stage 2 only", and its ownership
  table gives Stages 1, 3 and 5 to a "CLI script". The skill dispatches agents at Stages 2, 3
  and 4, and the session carries most of Stages 1, 3 and 5. This is one more member of the
  class in row 2 (f).
- The skill cites `src/gzkit/pipeline_runtime.py:129` for the role map. The map is defined in
  `src/gzkit/pipeline_dispatch.py` (insight 2026-10-09T00:23:00Z, scope
  `gz-obpi-pipeline:stale-role-map-pointer`; row 2 (h)).

What it bears on, as the agent reads it and not ruled:

- The five stages cover phases 5 and 6 of the targeting cycle, then release and recovery.
  Phases 1 to 4 happen before launch: the order, the brief, the choice of model tier, the
  operator's initiation.
- Two of the eight roles have agents today. Ordnance delivery is the implementer. BDA is in
  pieces: two readers, the verification agents and the second vendor's model. The unit's
  mission planning, the constraints, infiltration, exfiltration and decontamination are done
  inline by the one session. Target planning is brief authoring, ahead of the pipeline.
- The one session that holds this file and every inline step is an instance of what this
  record's restated challenge names: a control that addresses an agent "as though that agent
  could hold the whole".

## source · the scorecard past its rule tables, and the scope audit's owner, read 2026-10-09

Two of the reads the recomputed frontier listed as owed.

**`docs/governance/advisory-rules-audit.md`, lines 510 to 746, read in full.** With lines 1
to 140 (read 2026-10-08) that is everything in the file except the per-rule tables at lines
140 to 509, which are not read. Those tables were searched for "command doctrine" and
"Article <n>": no row has either. That is a search and is reported as one.

1. **Promotion is frozen.** "FROZEN — 2026-06-08 ... the imbalance to correct now is *too
   much* mechanism, not too little. Promotion is opt-in-with-justification: a new mechanical
   check is added only when a *specific, observed* drift instance justifies it."
2. **Removal has equal standing.** "A mechanism that misfires, over-fires, gives false
   assurance, or only guards other mechanism is removed with *named steering-failure
   evidence*".
3. **The criterion every scored clause is held to.** "Every scored clause either carries a
   mechanical witness or says in its own rule text that it is advisory and names what would
   reclassify it". A clause that does neither scores Promotable: "a discipline was found
   declared with neither a witness nor an admission."
4. **Re-scoring needs a text change.** "Re-scoring without a text edit is laundering
   (operator ruling 2026-08-08)".
5. **How a rule becomes mechanical** (§ Promotion discipline): write the audit first and
   watch it fail; fix or waive what it finds; promote it as a named `gz validate` scope;
   then "Delete or narrow the advisory rule text."
6. **The totals are machine-checked** by `gz validate --advisory-scorecard` against the rows;
   the figures in the prose are not cited here.

The freeze is two days older than the command doctrine. Article 2, ratified 2026-06-10: "If
the harness does not enforce it, the doctrine does not contain it", and "Authority asserted
in the context window is a briefing: necessary, and unenforceable." The campaign plan's
amendments of 2026-10-04 ("every control stands") bear on the removal clause and are read by
heading only.

**The scope audit's owner.** `build_scope_audit` entered `src/gzkit/hooks/obpi.py` on
2026-03-12 (commit `704907edd`) and has not changed since. It is called from
`src/gzkit/hooks/core.py` only. `src/gzkit/commands/obpi_complete.py` was added on 2026-04-05
and has no reference to it. The obligation is `OBPI-0.11.0-03`'s, status
`attested_completed`: "completed receipts preserve one deterministic evidence envelope across
hook-driven and manual completion paths. `scope_audit` now captures the OBPI allowlist plus
the pre-recorder changed-files snapshot". Its parent `ADR-0.11.0` is Validated. The route for
scope missed from a Validated ADR is already ruled (operator, 2026-10-04, carried in the
pipeline skill § Work selection): "A Validated ADR is not revised: scope missed from one
enters the in-flight ADR as a repair assignment that cites the obligation it repairs."

What it bears on, as the agent reads it and not ruled:

- A policy written under the merged doctrine with neither a witness nor an admission would
  score Promotable, which is the state the scorecard exists to empty.
- The frame's new positions are new mechanism if built. The freeze asks for an observed
  failure before each.
- The pipeline skill's three `references/` files (46 lines) were also read; they add nothing
  the skill's body lacks.

## source · what became of the freeze of 2026-06-08, measured 2026-10-09

Read and measured after the operator's remark of 2026-10-09 (decision *the freeze is not
relied on*). Read in full: handoff `20260609T022038Z-593-fixed-track2-a1-landed.md`. Read in
part: the campaign plan's Movement C box (two passages); one insight line of 2026-06-10.

1. **What the track was.** The handoff: "governance subtraction 'track 2', increment A1";
   "Operator chose reading A (housekeeping under the existing 'volume follows steering need',
   no doctrine amendment). A1 landed: froze the promotion-order backlog and cut 3 wrapper
   chores". Its ruled sequence: "do reading-A housekeeping cuts first, MEASURE the residual,
   only THEN consider reading-B". Its first advised step: "Pause-and-measure".
2. **Nothing after A1.** No measurement is recorded. The name "governance-subtraction" occurs
   in one handoff, the scorecard and three editions of the campaign plan, and in no ADR, GHI
   or chore. Two insight lines mention the track or subtraction at all.
3. **The operator deferred reduction two days later.** Insight 2026-06-10T07:23:35Z, quoting
   the operator: 'I want to build out gzkit, as found, as comprehended, and ONLY THEN make
   reductive decisions.'
4. **The freeze's own text is stale.** It says "As of 2026-08-08 there are no Promotable rows
   left to stay advisory: the third state is empty". The file's machine-checked summary has
   Promotable rows today, and rows 76 to 82 and 85 read Promotable. GHI #810, "cli-shape:
   build the arms for 8 Promotable CLI doctrine rows", is open.
5. **The validator does not see it.** `uv run gz validate --advisory-scorecard` exits 0 with
   "All validations passed". It checks that the counts agree with the rows, not that the
   state the scorecard exists to empty is empty.
6. **Other work the file says is owed.** Five of nine domain lists are still marked
   "Unread" from 2026-08-09 ("Six such readings are owed"). "Whether the inverse direction
   gets an owner is an open operator question". The file's own promotion to a test is "Left
   as a follow-up". `--failure-mode-coverage` and `--cli-shape` are named and are not flags
   of `gz validate`.
7. **Mechanism since the freeze.** The handoff counted 13 pre-commit hooks, 38 chores, 22
   rules, 62 skills and 6 personas. Today: 18, 40, 26, 73 and 7. The scorecard's own comment
   has its scored rows going from 69 to 181.
8. **What still stands of it.** The campaign plan, operator-ratified, cites the freeze as
   governing: "Under that freeze the default disposition is the amend-the-text-and-re-score
   arm; mechanization is reserved for a row carrying named, observed drift evidence."
   `gate5-runbook-code-covenant.md` and `tool-skill-runbook-alignment.md` cite it as their
   reason not to build a check.
9. **The command doctrine's audit, for comparison.** Article 10: "The audit runs at every
   major model transition". No record of a run was found by search. The pool ADR that owns
   the worklist is named in two ledger events.

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
| | campaign amendments | fragmentary orders, folded on republish | JP 3-60 (2018) Figure II-8 names the fragmentary order as a tasking order; the mapping is unsourced |
| | sequenced campaign items | prioritised target list | JP 3-60 (2018) JIPTL; the text says targets "may not be engaged in the same priority order" |
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
| | spec, quality, collateral review | combat assessment: BDA (physical, functional, target system), MEA, reattack | JP 3-60 (2018), phase 6 and Appendix D |
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
| | `ADR-0.35.0`–`0.38.0` landed and S1 flown | initial operational capability (ruled 2026-10-07) | DSCA manual glossary, citing the Defense Acquisition University Glossary (verified 2026-10-08) |
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

**Corrected 2026-10-08 against this record's own source entries.** The table above is
kept as it was ruled and staged; these are the rows its sources have since moved, each by
the entry that moved it. Nothing here is a new ruling, and the names still in doubt stay on
the frontier for the operator.

- The line above the table, "cited from memory until its file lands", no longer holds for
  the rows whose texts are read: JP 3-60 (2018), JP 3-30, JO 7110.65BB, JO 7210.3EE,
  AC 121-22D, AC 120-16G, AC 120-71B, AC 20-115D, AC 20-189, AC 00-71 and the DAU Glossary.
- *new apex → concept of operations*: superseded. There is one doctrine and no separate
  concept of operations (decision *one binding doctrine*).
- *session → watch*: "watch" is in neither FAA order; the orders' noun is the position.
- *implementer, reviewers, narrator → pilot flying, pilot monitoring, assessor, briefer*:
  the mapping is wrong (AC 120-71B: the monitor works at the same time as the flyer) and
  against Article 3; "assessor" and "briefer" are in no text read.
- *failure-mode taxonomy → hazard log*: the phrase is nowhere in Title 14; no source.
- *chores, registry, `gz mx` → MSG-3 tasks, maintenance planning document, MRO visit*: a
  packaged visit is a *scheduled work package* (AC 120-16G § 6-1); the planning document
  is a recognised reference (EASA checklist) with no text behind its mapping to the
  registry; "letter check" is the operator's own practice (ruled 2026-10-08).
- *GHI → squawk; problem report*: "problem report" has a primary definition and a life
  cycle (AC 20-189, AC 00-71). The source "DO-178C § 11.17" is dropped (ruled 2026-10-08).
- *operator hold → deferred defect (MEL item)*: the nearer cited term is the *open problem
  report* (AC 20-189).
- *1.0 → full operational capability*: verified 2026-10-08 from the DAU Glossary; the
  source cell's "not verified" is withdrawn.
- *skills → challenge-and-response checklists*: a skill is a procedure; a checklist is a
  short list read after the flow, nearer the per-change gate (AC 120-71B).
- *gates → objectives*: stands against the operator's constraint of 2026-09-22 on the five
  gates; held on the frontier, not corrected here.
- The ladder (previous decision): "work package" and "task card" are verified as
  maintenance terms and "engineering order" as a term only (AC 120-16G source file, claims
  table); "change proposal" and "block" are in no landed source. The ladder also meets a
  canonical identifier scheme and a release doctrine it was ruled without (source entry
  *gzkit's own doctrine layer*, item 7).

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
Corrected 2026-10-07 on the Jacklin paper (source entry of that name): DO-178C's own word is
"software level"; "assurance level" is DO-278A's and "development assurance level" the system
standard's. Each is assigned from the failure effect category, which two secondary sources
now state, so the reason for avoiding the term stands.
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

## decision · the run is reopened for the operator's review of the plan

After sign-off the operator asked, verbatim (insight 2026-10-07T23:43:36Z): 'what is the
result of that rnd? you didn't get all the pdfs from me' and 'so, you have a plan for the
renewed vows material and we didn't review it?' The agent's answer was yes: the sign-off was
taken after six selections of a recommended option and a six-line summary of the map, and
the operator had not been shown the plan's content. The agent recommended reopening. The
operator, verbatim: 'reopen'.

What this fixes:

- **The sign-off of this date is set aside.** It is kept in the Close as a record of what
  was said and when; it does not close diamond 1. Re-entry is native to the frame
  (`rnd-discipline.md`: findings "can send them back to the beginning of their diamond
  work").
- **The rulings of this date stand** until the operator changes them in review: placement,
  the integrity-level axis and its name, chore run events, the rhythm's tiers, the IOC
  waypoint, the constitution draft, the source rule.
- **A review is owed before sign-off is put again.** The agent writes one readable account
  of the whole plan at `docs/rnd/renewing-vows/review.md`. It is a view over this record's
  entries and holds no authority of its own; where the two differ, this record governs and
  the view is corrected.
- **The frontier is no longer empty.** It holds the review, and the findings the supplied
  texts raised against names this record carries (each in its source entry of this date).

Texts the operator supplied after sign-off, all landed: FAA Order JO 7110.65BB Appendix A;
FAA AC 121-22D; JP 3-30 (2019); JP 3-60 (2013 edition); FAR Part 2; the Jacklin paper on
DO-178C. The definitions of initial and full operational capability are in none of them.

No commission. No row has a go.

## decision · the core model, mapped from the two cycles (proposed by the agent; its shape ruled 2026-10-08)

Directed by the operator on 2026-10-07, verbatim: 'step 1, and improve rnd skill'. Step 1,
as the agent had put it: build the core model from the two cycles now read, with the
operator's eight roles and gzkit's pipeline mapped against them. Nothing here is ruled.

**Read for it, 2026-10-07.** JP 3-60 (2013) Chapter II § 3 through phase 6, with the six
steps of phase 5, and Appendix D (corrected 2026-10-08 to the 2018 edition's phase names and
text, once the operator supplied it); JP 3-30 (2019) Chapter III § 6 (both in their source
files). `.gzkit/skills/gz-obpi-pipeline/SKILL.md`: its stage diagram and § Persona Dispatch
read, and the rest of its 1,709 lines searched for where each step sits, not read. The eight
roles are the operator's prompt in the Gemini dialogue (first source entry), verbatim:
'Different agents for mission planning, mission constraints, target planning, infiltration,
ordinance delivery, exfiltration, decontamination, BDA.'

**The spine is the joint targeting cycle.** It is the publication's account of how one
target is taken from objective to assessed effect, which is the scale of one work package.
The air tasking cycle is the operations centre's daily production of orders across many
missions; its six stages sit beside the phases below and belong to the orchestrating
session, not to one work package.

| # | Targeting phase (JP 3-60) | Tasking stage (JP 3-30) | What the doctrine does there | The operator's role | gzkit today | State |
|---|---|---|---|---|---|---|
| 1 | Commander's objectives, targeting guidance, and intent | Objectives, effects and guidance | Objectives set; measures "to assess whether the effects and objectives are being or have been attained" fixed at the start | none: this is command, above the mission | The engineering order's intent; the work package's requirements are the measures | exists |
| 2 | Target development and prioritization | Target development | Targets characterised and vetted; the commander approves the prioritised list; protected objects go on a no-strike list; a restricted target may be engaged only within stated limits | target planning | Campaign order and the order's checklist; a brief's allowed and denied paths | exists under other names |
| 3 | Capabilities analysis | Weaponeering and allocation | Means matched to the target (weaponeering); feasibility; an effects estimate with collateral damage estimated by "trained and certified personnel" | mission constraints, the part that is estimated | Model tier chosen by task complexity; the airlock's entry seam-map as the collateral estimate, empty on 20 of 23 transits (campaign plan, 2026-08-14) | weak: the weaponeering rule is ruled and unbuilt; the estimate is mostly empty |
| 4 | Commander's decision and force assignment | Order production and dissemination | The commander approves; tasking orders issue, carrying the reasoning and the special instructions | mission constraints, the part that travels in the order | The operator initiates the work package; a plan-audit receipt; no record of the tasking | gap: the tasking event is ruled and unbuilt |
| 5 | Mission planning and force execution | Execution planning and force execution | The unit plans on receipt of tasking; the target is validated again; find, fix, track, target, engage, assess; the centre is told of every redirection | mission planning; ordnance delivery | Stage 1 plan and lock; Stage 2 implementer, red then green under the red witness; brief reconciliation; the dispatch is recorded, its outcome is not | exists; position and outcome wait on briefs 15 to 18 |
| 6 | Combat assessment | Assessment | Damage assessment in three widening phases (physical, functional, target system); munitions effectiveness; collateral damage assessment; reattack recommendation; made by a designated cell from several sources, each with a confidence level | BDA | Stage 3 receipts (physical); spec review, Step 4b and Gate 4 (functional); fix cycles and the three-round limit (reattack) | gap: target-system and collateral assessment have no owner; munitions effectiveness has no owner |

**What falls outside the cycle.**

- *Infiltration, exfiltration, decontamination.* Three of the eight roles have no counterpart
  in either publication as read. They are the airlock's: entry, exit and the accounting of
  what a transit disturbed (`ADR-0.33.0`), and the operator's own words in the dialogue,
  'the airlock is how we decontaminate'. They are gzkit's vocabulary, not borrowed doctrine.
- *Release.* Human attestation is return to service, from the airworthiness register
  (14 CFR § 43.9), not a phase of targeting.
- *Quality review.* It has no clean counterpart. The nearest text is the effects estimate's
  concern for "reuse and reconstruction during later plan phases to avoid negatively
  affecting the end state".
- *Handoff and chores.* Position relief (JO 7110.65BB) and scheduled maintenance
  (AC 121-22D) are other departments.

**What the mapping shows.**

1. The targeting cycle carries five of the eight roles. The model is therefore two things:
   the cycle, borrowed and sourced, and the airlock transit around execution, gzkit's own.
2. **Constraints are a planning product in the doctrine, not a flight.** Restrictions reach
   the crew in the order: "CDE guidance ... law of war, ROE, NSL, and RTL", and special
   instructions "located in the air tasking order". This record's decision of 2026-10-05
   calls constraints a sortie that lands contracts before any red, and the operator called it
   "a Design act". Both hold if the work is planning-side and its product travels in the
   order. Whether it is dispatched as a sortie or done by the planner is not settled.
3. **Assessment is where gzkit is thinnest.** Of the five outputs the doctrine names, two
   have no owner: what the change did to the system around the target, and whether the
   means used performed as estimated.
4. **Assessment is specified before the strike.** An output of the target step is
   "Assessment collection requirements are submitted", and measures are fixed in phase 1.
   gzkit's requirements and their covering tests already work this way.
5. **Hitting the target is not achieving the objective.** "... can result in a successful
   mission that hits the designated target at the designated time, but still does not
   achieve the objective." That sentence is the difference between a passing test and an
   accepted work package.

**The shape, ruled 2026-10-08: both.** The question put, 2026-10-07: "Is this the shape of
the model?" with three answers and no recommendation attached. A, cycle plus airlock: the
six-phase targeting cycle as the spine for one work package, the airlock a separate transit
around execution. B, the operator's eight roles as the spine: eight sorties in the
operator's order, doctrine as annotation. C, something else. The operator asked for A and B
to be described (verbatim: 'descrube a and b'). The agent described each, and said they
answer different questions, A what must happen and B who does it, so that one combined form
is A's phases as the process, staffed by B's roles as the crew, with the airlock roles flown
around phase 5. Operator, verbatim: 'i want both'.

What the ruling fixes:

- **The process is the six phases** of the joint targeting cycle, cited from 2026-10-08 as
  JP 3-60 (2018).
- **The crew is the operator's eight roles**, each a small, focused agent, which is the
  direction the frame was ruled to serve on 2026-10-05.
- **The three airlock roles are crew positions**, flown around execution. They stay gzkit's
  own words; no text read carries them.
- **Constraints are flown**, by the mission-constraints role, and their product travels in
  the order. That settles the doubt in point 2 above and agrees with the decision of
  2026-10-05 that the constraints sortie is a Design act.

The staffing below is the agent's drawing of that ruling, for the operator's correction. It
is not itself ruled.

| Phase | Who | What they hand on |
|---|---|---|
| 1. End state and objectives | command: the operator and the order's author | intent, requirements, the measures of success |
| 2. Target development | **target planning** | what is to change; what is protected (no-strike); what may be touched only within limits (restricted) |
| 3. Capabilities analysis | **mission constraints**; the runtime applies the weaponeering rule | contracts (interfaces, invariants, stubs); the collateral estimate; the sortie set |
| 4. Commander's decision | command: the operator initiates | the tasking order, carrying the reasoning and the constraints |
| 5. Mission planning and execution | **mission planning**, then **infiltration**, **ordnance delivery**, **exfiltration**, **decontamination** | the unit's plan; entry accounted; red then green; exit accounted; what the transit disturbed, cleaned and reported |
| 6. Assessment | **BDA** | physical, functional and target-system damage assessment; munitions effectiveness; collateral; a reattack recommendation |

Seams where the roles and the phases do not line up, each open:

1. **Mission planning is first in the operator's list and fifth in the cycle.** The doctrine's
   mission planning is the unit's own, "Upon receipt of tasking orders". The table places it
   there. If the operator meant the planning of the whole mission, it belongs before target
   planning and the table is wrong.
   **Put 2026-10-08** with three answers and no recommendation: the unit's own plan after
   tasking; the plan for the whole mission, ahead of target planning; both exist and need
   two names. Operator, verbatim: 'moth are valid, what does our guidance say?' (read as
   "both are valid"). Ruled: both exist. What the texts read say, for the names:
   - The unit's plan is **mission planning**. JP 3-60 phase 5: "Upon receipt of tasking
     orders, detailed planning must be performed for the execution of operations."
   - The plan for the whole is **operation planning**, and its product is a plan with its
     own name. JP 3-60 phase 1 takes its start from what was "developed during operational
     planning" and "The mission analysis step of JOPP"; JP 3-30's glossary: "joint air
     operations plan. A plan for a connected series of joint air operations to achieve the
     joint force commander’s objectives within a given time and joint operational area."
   - JP 3-30 Appendix E keeps three horizons apart inside the centre: a strategy division
     for "long-range and near-term planning", a combat plans division for the 48 hours
     before an order executes, and a combat operations division for execution; and the
     strategists "should not become caught up in execution details".
   - gzkit already has both under other names (`AGENTS.md` § Pattern Discovery: "ADR (mADR) →
     OBPI (brief) → plan/spec/tasks"): authoring the order and its work packages is the
     first; the plan written for one work package after the operator initiates it is the
     second.
   The names "operation planning" and "mission planning" are the agent's proposal from
   those texts and are not ruled. The planning publication both cite, JP 5-0, is unread.
2. **Ordnance delivery is more than one sortie.** The decision of 2026-10-05 splits it into
   red and green, flown by different crew.
3. **BDA is one role against five outputs**, and the decision of 2026-10-05 already made
   chase and damage assessment two roles. Target-system and collateral assessment, and
   munitions effectiveness, still have no owner.
4. **Decontamination cleans; collateral assessment judges.** One is the crew's at the end
   of execution and the other is the assessor's. The table keeps them apart.

**commissions:** 4 — the model as the core of the concept of operations; 1 — it is the frame
the crew-split and combat-assessment proposals are written against.

## decision · one binding doctrine: the command doctrine and this run's model are merged

**Read for it, 2026-10-08.** `docs/governance/GovZero/command-doctrine.md` in full (source
entry above); `docs/design/adr/pool/ADR-pool.command-doctrine-internalization.md` in full;
one row of `docs/evals/compression-sweep-2026-09-24.md` found by search. Canon was searched
for every reference to the doctrine: it is named by the GovZero charter, by that pool ADR
and by two evaluation records, and by nothing else. `AGENTS.md`, the campaign plan and the
lodestar do not name it. The rulings store has no ruling that matches "command doctrine".

**The question put, 2026-10-08**, with no recommendation attached: what is the new concept
of operations, relative to the command doctrine? The layer beneath it; a revision of it, one
document and not two; something else. Operator, verbatim:

> 2. incorporate and merge/subsume, I am in search of binding/bounding doctrine for gzkit to
> hold me and agents to account.

What the ruling fixes:

- **One doctrine.** The command doctrine and this run's model are merged. There is no
  separate concept of operations standing beside or above it.
- **Its purpose, in the operator's words**: "binding/bounding doctrine for gzkit to hold me
  and agents to account." It binds the operator as well as the agents. The ratified articles
  already do: the signature and the override are one clause (Article 1), the span of a run
  is capped by what one attestation can honestly cover (Article 6), and unassisted work is
  scheduled and logged (Article 9).
- **The placement ruling of 2026-10-07 is superseded** as far as it made the concept of
  operations a document of its own. What it kept from canon stands: the constitution is the
  root, and the campaign plan rules sequencing.
- **The constitution ruling of 2026-10-07 is superseded as to content.** Three general
  orders drafted by the agent are not offered again as the root's text while ten ratified
  articles exist. What the constitution is, relative to the merged doctrine, is put again.

The agent's reading of "incorporate and merge/subsume", for the operator to correct: the ten
ratified articles are carried in as they stand, and no article is reworded by this run
without the operator ruling on that article; the run's model (the six phases, the eight
roles, the airlock) is merged in beneath them as policy and procedure, each part tracing to
an article as Article 10 requires.

What "binding" already means in the doctrine, which the merged text has to meet:

> If the harness does not enforce it, the doctrine does not contain it. (Article 2)

> Every gate, check, and template in gzkit must trace upward through a policy to an article
> of this doctrine. (Article 10)

Two facts about the doctrine's hold today. Its own appendix scores three articles as gaps
and two as partial, with the worklist parked in a pool ADR. And it does not reach the agents
it is meant to bind: the corpus entry that carried Article 10 into `AGENTS.md` was dropped,
and the compression sweep of 2026-09-24 records it (row S31) as "never rendered in BEFORE
AGENTS.md, so agents were not loading it ... Retired with the generic 'recaptured fresh'
reason, but it was not recaptured." That is how a run about gzkit's operating doctrine came
to be opened, worked for three days and signed off without any session reading it.

**commissions:** 4 — one merged doctrine, drafted on the operator's go, in place of a
separate concept of operations; 2 — the doctrine's absence from the per-turn surfaces is a
defect to route (sweep row S31).

## decision · the two bodies of material are merged into one file, to assist the operator's doctrine

**The question put, 2026-10-08**, after the operator asked for a walk through the June
materials and the run's: when this is written down, one file, or two (the ten articles as
the root and the operating model as a second document that points up to them)? The agent
had leaned to two. Operator, verbatim, in two messages: 'merge them, the assist in creating
my doctrine' and then 'merge them, they assist in creating my doctrine'.

What the ruling fixes:

- **One file.** The June doctrine and this run's model are merged.
- **The materials assist; the doctrine is the operator's to create.** The agent first read
  the earlier message as "then assist in creating my doctrine", an instruction to draft the
  doctrine, and began on that reading. The second message corrects it. What was built is
  the merge, not a doctrine: `docs/rnd/renewing-vows/doctrine-merge.md`.

What the merge is. The June doctrine's sections are copied byte for byte and marked
RATIFIED (the script that built the file asserts each is present unchanged; the canonical
file's SHA-256 is in its header). New parts are marked DRAFT: eighteen policies, each with
the article it traces to, the ruling, canon or text it comes from, and what enforces it
today; the procedures for how one work package is flown; and eight open questions, none
decided. It applies Article 2 to itself: a policy that nothing in the harness enforces is
marked "not yet binding". By its count two policies are enforced in full, nine in part and
seven by nothing.

What it is not: canon. `docs/governance/GovZero/command-doctrine.md` is unchanged and
remains the doctrine until the operator ratifies a successor text.

**How the doctrine is made, ruled 2026-10-08.** The agent offered two ways to use the merge:
the operator marks up Part II, or the open questions are taken one at a time. Operator,
verbatim: 'no, i want to assemble the doctrine. i direct, you draft. for now, we need a
handoff and git sync'. So the operator assembles the doctrine and directs each part; the
agent drafts what is directed and nothing ahead of it. The merge file is a quarry for that
work, not a first draft to be approved. The work resumes in a later session, on the
operator's invocation of the skill on this record.

**commissions:** 4 — the merge file is that row's working material, on the operator's
direction of this date; nothing else in the row has a go.

## decision · two sessions are writing this record (observed 2026-10-08; for the operator's ruling)

Observed 2026-10-08 by the session the operator invoked on this record on 2026-10-07. Between
that session's edits, five source entries and five source files appeared that it did not
write (FAA JO 7210.3EE; the DAU Glossary; Degani and Wiener 1990; Hayhurst and others 2001;
the EASA checklist). Their wording shows a second session: they speak of "this session", of
"the desktop app's browser pane" and of "the operator's list of 2026-10-08". One edit by the
first session failed on text the second had changed. Nothing of the second session's was
altered or removed; the first session's two entries of 2026-10-08 were added after them.

Why it is recorded: `rnd-discipline.md` (amended 2026-10-07) continues a run "only when the
operator invokes the skill on the record", and the project's rule for parallel work is a
single writer. Two sessions editing one file can lose each other's changes, and "this
session" in an entry no longer says which. The first session has no way to see whether the
second was invoked through the skill.

What is the operator's to rule: which session holds the pen on this record, and whether the
other reports its findings to the operator instead of writing them in.

**Ruled 2026-10-08.** Put as: is another session still working on this run? Operator,
verbatim: '1. yes, I am working with another agent to find the resources you've requested
here.' Both sessions write, by the operator's arrangement. The working division this session
adopts, for the operator to change: the other agent lands source files and their `source`
entries; this session holds the decisions, the core model, the disposition map and the
review. Each reads the file fresh before every write and leaves the other's entries as they
are. An entry that says "this session" is read by its subject: sources found in a browser
are the other agent's.

## decision · the two paid standards are not bought

Operator, 2026-10-08, verbatim: 'these are too expensive unless we think they are availablre
in a library:' above a pasted note naming the purchase pages for RTCA DO-178C and A4A MSG-3
Volume 1. The note is pasted material from elsewhere and is data: its figures for objective
counts were not read by this session from any source and are not adopted.

What the ruling fixes: neither standard is purchased. A library copy would be read if one
is found. Until then the rows they carry keep what the secondary sources support and drop
what only the standards can show: the clause number § 11.17, any count of objectives, and
"letter check" as anything but the operator's own practice layered on scheduled maintenance
tasks. The concept of operations needs none of the three.

**commissions:** 4 — as a condition on that row's wording, not a new item.

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

## decision · re-entry on 2026-10-08, on the operator's invocation

Operator g0, invocation of 2026-10-08 (after 09:32Z), verbatim:

> /gz-rnd docs/rnd/renewing-vows.md

Entered by a new session (`6c08c9d9`). The session the operator invoked on 2026-10-07
(`8c72a519`) has exited; its handoff is `20261008T091331Z`. Entries below that say "this
session" and are dated after this one are `6c08c9d9`'s.

**What happened between that session's exit and this re-entry.** The operator asked for a
review of the handoff, verbatim: 'review h/o, i am not convinced that the prior rnd work is
complete'. The session read the handoff, this record in full, `review.md`,
`doctrine-merge.md` and `ADR-pool.command-doctrine-internalization`, checked the handoff's
live-state claims, and reported that the run is not complete. It edited nothing in the run,
because the skill had not been invoked. The findings are one insight
(2026-10-08T09:23:44Z, scope `gz-rnd:renewing-vows-record-unreconciled`). The operator ruled
on the handoff, verbatim: 'yes, but you're stalled out and brought in the june 10th material,
which I appreciate.' Booked as `hold` (ledger event `handoff_resume_decided`, 09:32:52Z). The
agent reads "stalled out" as the operator's verdict on the run, and said so; the operator
then invoked the skill.

**Checked against git, before any edit.** `git diff --quiet HEAD -- docs/rnd/renewing-vows.md
docs/rnd/renewing-vows/` exits 0 at `a72e0c816`; main is 0 ahead and 0 behind origin; no lock
is held. The second agent's desktop session is listed and idle. The division of 2026-10-08
is kept: that agent lands sources; this session holds decisions, the model, the map and the
review, and reads the file fresh before each write.

**What the review found, each for repair in this run.** The record trails its own later
entries:

- The restated challenge in the Close still defines the problem as a missing concept of
  operations. The one-doctrine ruling of 2026-10-08 superseded that.
- Row 4 still carries the small constitution draft the same ruling superseded as to content,
  and a reason that says the texts are awaited. Row 2 lacks the defect the one-doctrine
  decision commissions to it (sweep row S31). Row 1 proposes a tasking event and a
  collateral assessment as new engineering orders, and
  `ADR-pool.command-doctrine-internalization` items 1 and 3 already own the captain's brief
  and the scope-conformance report.
- The nomenclature table was not corrected where its own source entries contradict it.
- Frontier item 13 and `review.md` say the ladder's names are in no landed source. The
  AC 120-16G source file verifies "work package", "task card" and "engineering order" as
  maintenance terms.
- `review.md` is stale outside its sections 8a and 9.
- The Shihipar text was never landed and the model-and-effort decision cites it.
- The read that missed the command doctrine was repaired for that one file. Of the
  twenty-three documents under `docs/governance/GovZero/`, this record names two.

**The frontier, computed again from the subject.** The subject, in the operator's words of
2026-10-08, is "binding/bounding doctrine for gzkit to hold me and agents to account". The
first thing it needs is a fact and not a ruling: what gzkit already holds at the doctrine
layer. That is the agent's work and comes before any question is put. The order this session
works in:

1. Read `docs/governance/GovZero/` in full and enter what bears on the subject as a `source`.
2. Correct the record where its own entries contradict it, each correction dated in place.
3. Put the open questions to the operator one at a time, the core model first. The list in
   the Close is an input to that and is recomputed there after step 1.

No row has a go. No ledger event was emitted for the run.

## decision · the frame reaches both ways, into what exists and what is to come (operator, 2026-10-08)

**The question put, 2026-10-08** (frontier item 17): "What is the doctrine you are
assembling made of?" Three answers, A recommended. A, the policies layer only: the ten
articles stay as ratified and the standing decisions beneath them are assembled, each traced
to an article and carried as a scorecard row. B, reopen the articles too: a second edition
of the command doctrine with the combat frame written in. C, procedures first: settle phases
and roles against the five-stage pipeline and let policies fall out. The agent said the
operator had taken the recommended option on six earlier questions and asked whether this was
the right question.

Operator g0, verbatim:

> the new framing has forwards and backwards influences

**Ruled: none of the three.** The question cut the doctrine by layer and asked which layer to
work. The answer is that the frame is not held to one layer, nor to new work.

**The agent's reading, for the operator's correction** (corrected by the operator the same
day; see the next entry). "The new framing" is the military and
aviation frame with its six phases and eight roles. "Backwards" is what gzkit already holds
and the frame changes, presses or reads again: ratified articles, written procedures, the
runtime, the names, the plan. "Forwards" is what does not exist and the frame calls for. A
second reading is possible, that the frame has things behind it that shaped it and things
ahead that it shapes. The trace below is the same work under either.

**Read for it, 2026-10-08.** The command doctrine again, in full; the `gz-obpi-pipeline`
skill in full (source entry of today); the source entry *gzkit's own doctrine layer*; this
record's map.

**Backwards: what exists and the frame reaches into.**

| Layer | What gzkit holds | What the frame does to it |
|---|---|---|
| Philosophy | Article 3, "The model is a crew resource, not a crew member" | The frame gives agents eight positions. The article's allocation stands ("the model decides nothing that ships"). Its title speaks against calling an agent crew, and "crew" is this record's word, not the operator's: the operator said 'Different agents for', and the agent drew 'i want both' as "the crew". |
| Philosophy | Article 4, scope manifest and the diff of delivered against commanded | The frame calls these the order's restrictions and the collateral assessment. It adds no obligation the article lacks. Built as a receipt field and lapsed (row 2 (g)). |
| Philosophy | Article 6, a run "capped at the volume of change one attestation can honestly cover" | The frame sizes work by what one agent holds. The article sizes it by what one attestation covers. The two are not reconciled; the doctrine's own Appendix A already names a tension with the decomposition matrix. |
| Philosophy | no article | Relief of position (handoff) traces to none. |
| Policies | one sentence in the doctrine naming four | Nothing to reach into. See forwards. |
| Procedures | the charter's five gates | "gates → objectives" is a name in doubt against the standing constraint on the gates. Gate 5 is the frame's return to service. |
| Procedures | the five-stage pipeline: runbook (Draft v2.0) and skill 6.65.0 | The stages cover phases 5 and 6, then release and recovery. One session does inline what the frame gives to five positions. The runbook's "Agent work is Stage 2 only" is already untrue of the skill. |
| Procedures | the transaction contract's fail-closed allowlist | The frame's restricted and protected targets. Same thing, two names. |
| Procedures | handoff documents (`ADR-0.0.25`) and the chore system | Position relief and scheduled maintenance, "other departments" in the core-model decision. |
| Practice | the airlock (`ADR-0.33.0`) | Three of the eight roles are its own words. |
| Practice | the runtime: four roles, five marker stages | Eight positions against four roles. |
| Names | ADR, OBPI, TASK and their identifiers | Row 5. |
| Plan | the campaign order; briefs 15 to 20, `ADR-0.36.0` to `ADR-0.38.0`; `ADR-pool.command-doctrine-internalization` | Read again as the machinery the frame needs; pool items 1 and 3 are the tasking order and the collateral report. |

**Forwards: what does not exist and the frame calls for.** The policies layer as a document.
Six positions with no agent of their own (mission planning, constraints, target planning,
infiltration, exfiltration, decontamination). Red and green flown by different agents. An
owner for munitions effectiveness and one assessment record. The integrity-level axis. The
maintenance record entry. The two slower tiers of the rhythm. The IOC waypoint. The
weaponeering rule and the model-and-effort table.

**Where canon binds the frame.** The influence also runs from what is ratified onto what is
new. Article 1 keeps the signature with one human, so release stays outside any agent's
position. Article 3 closes "pilot" and puts "crew" in doubt. The IRON LAW makes phase 4, the
commander's decision, the operator's initiation and no agent's. The five gates are a standing
constraint. Feature orders are worked in ascending order.

**What the ruling changes in this run.**

- Frontier item 17 is closed. No layer is chosen. Each part the operator assembles is stated
  with its reach in both directions.
- Item 18 is now first, because it is the largest backward reach and it is the core model.
- Item 15 gains its candidates from the trace: the word "crew" against Article 3; an article
  for relief of position; Article 6's sizing against the frame's.
- `review.md` is written once, ahead of item 12, with every row shown in both directions. It
  is not rewritten after each ruling. Its dated note stands until then.

**commissions:** nothing new. No row changes state.

## decision · the two frames shape each other, and both reach back into the prior frame (operator, 2026-10-08)

**The agent's reading in the entry above was wrong.** It took "forwards" and "backwards" as
new work against existing work. The operator corrected it, verbatim:

> the 6/10 system and the military frame will now have mutually shaping influences, which is
> what i meant by 'forwards,' that command system (likely airline/pilot centric) and this
> newer military metaphors will exert 'backwards' influence on the prior frame

**Ruled.** There are three things, not two. The command doctrine of 2026-06-10 and the
military frame of this run shape each other from here on: that is forwards. The two together
reach back into the frame gzkit had before them: that is backwards. The two tables in the
entry above are cut on the wrong axis. Their facts stand and are sorted again below.

**"The prior frame", as the agent reads it and for the operator's correction:** gzkit as
built, apart from the two frames: the five gates, the lanes, the order and work-package
ladder, the five-stage pipeline, handoffs, chores, the airlock and the flight test.

**The operator's parenthesis, checked.** The command doctrine is airline and cockpit
throughout. Its sources, by its own citations: 14 C.F.R. § 91.3 (Article 1); crew resource
management, Helmreich et al. 1999 (Article 3); mode error, Sarter & Woods 1995 (Article 4);
airline dispatch with inoperative equipment (Article 5); "the autopilot" and "the pilot"
(Article 6); fuel planning (Article 8); manual flight operations, FAA 2013 (Article 9); the
Four P's of cockpit operations, Degani & Wiener 1997 (Article 10). Its picture is one human
in command beside one automation. None of those texts has been read by this run; they are
cited here as the doctrine cites them.

**How far each frame has already reached, measured 2026-10-08.** The command doctrine is
named in eight tracked files outside this run: the charter, the pool ADR that carries its
worklist, the corpus, two evaluation records, one test, the site index and itself. It
reaches nothing an agent loads each turn (row 2 (d)). Of the military frame's words,
"ordnance", "weaponeering", "targeting cycle", "tasking order" and "battle damage" occur in
no tracked file outside this run. "Sortie" occurs in forty-two, from 2026-07-04, through the
airlock and the flight test, where it is a flight-test word.

**Forwards: where the two frames meet.** The agent's sorting of texts already read, not
ruled. The military column is JP 3-60 (2018) as entered in the core-model decision.

| Subject | Command doctrine (2026-06-10) | Military frame | What each does to the other |
|---|---|---|---|
| Who commands | Article 1: one human signs; authority and responsibility are "one clause, not two" | The commander's objectives (phase 1) and the commander's decision (phase 4) | They agree. The military frame shows command twice in one work package, at the intent and at the decision to task, and a third time at release. The article speaks of one signature. |
| How command reaches the agent | Article 2: "If the harness does not enforce it, the doctrine does not contain it." Article 4: a scope manifest before every run | The tasking order, carrying the reasoning, the special instructions and the restrictions | The military frame gives the manifest its form. The article says the order binds only as far as the harness enforces it. |
| What an agent is | Article 3: "a crew resource, not a crew member"; "the model decides nothing that ships" | Eight roles, "Different agents for" each, with an operations centre between the commander and the unit | They collide. The article has one automation and two parties. The frame has many agents and an echelon between. "Crew" for agents is this record's word and the article's title is against it. |
| Change beyond the order | Article 4: a diff of delivered work against commanded scope, after the run | Collateral damage estimated before (phase 3) and assessed after (phase 6); protected and restricted targets | The frame adds the estimate before the run. The article has only the diff after. |
| Which means were used | Article 5: the served model is recorded; substitution by "explicit prior relief" | Weaponeering matches means to target (phase 3); munitions effectiveness asks whether they performed (phase 6) | The frame gives the article a before and an after. The article gives weaponeering its rule: a substitution outside policy fails the gate. |
| How much one run may hold | Article 6: capped by "the volume of change one attestation can honestly cover" | Work sized to what one small agent can hold | Two sizings of the same thing, not reconciled. |
| What counts as evidence | Article 7: "artifacts, not narration" | Assessment by a designated cell, from several sources, each with a confidence level | The frame adds that the assessor is not the one who flew. The article adds that an agent's account of itself is not a source. |
| Why a procedure exists | Article 10: every gate traces "through a policy to an article" | Measures of success fixed in phase 1; a mission can hit "the designated target ... but still does not achieve the objective" | They agree. A target traces to an objective as a procedure traces to an article. |
| Only in the command doctrine | Article 8, efficiency as fuel planning; Article 9, proficiency by deliberate unassisted work; the Four P's | no counterpart in the texts read | The doctrine keeps what the frame lacks. |
| Only in the military frame | no article | A process in time (six phases); positions; a recommendation to strike again | The frame supplies what the doctrine lacks: an account of one mission from start to end. |

Relief of position is from neither frame. It is air traffic control's (JO 7110.65BB) and
traces to no article.

**Backwards: what the two reach into.** The rows of the earlier table that name procedures,
practice, names and plan: the charter's gates, the five-stage pipeline, the transaction
contract, handoffs and chores, the airlock, the runtime's roles and stages, the ladder's
names, the campaign order. The command doctrine's reach back has begun (the charter's trace,
the doctrine's Appendix A, the pool ADR's six items). The military frame's has not begun
outside this record.

**What the correction changes in this run.**

- Frontier item 18, how the phases and roles relate to the five-stage pipeline, was put on
  2026-10-08 and not answered. It is a question about the prior frame. It waits until the
  two frames are fitted to each other.
- The first question is now where the two frames collide: what an agent is (item 19).
- Item 15's candidates are the rows above where the frames do not already agree.
- The option "the ten articles stay as ratified" (A of item 17) is not the operator's
  direction. Shaping runs into the articles as well as out of them. An amendment to an
  article is still the operator's, article by article.

**commissions:** nothing new. No row changes state.

## decision · item 19's first two answers were not alternatives (operator's objection, 2026-10-08)

**The question put, 2026-10-08** (frontier item 19): "What is an agent in the merged
doctrine?" Three answers, A recommended. A, a resource in a position: every agent, the
orchestrating one included, fills a position; the position carries the order, the limits and
the record; tasking between positions is the harness's. B, crew without command: agents in
positions are crew, with crew duties (inform, challenge, no silence) and no authority. C,
leave Article 3 alone and carry the many-agent structure in policies beneath it.

Operator g0, verbatim:

> i fail to see why a and b are orthogonal

**The objection holds.** A answers where an agent sits and who tasks it. B answers what the
agent owes while it sits there. Neither excludes the other, and Article 3 as ratified already
holds B's half: the model "drafts, flags, surfaces, challenges, and proposes", crew resource
management "made silence a violation", and "the model decides nothing that ships". The only
thing that set A against B was the word "crew", which is a name and not the thing.

This is the second time in this run. The core-model question of 2026-10-07 put A and B as
alternatives, the agent then said "they answer different questions", and the operator ruled
'i want both' (insight 2026-10-09T00:39:59Z, scope `gz-rnd:options-not-exclusive`).

**The two put together, as the agent restates them. Not ruled until the operator says so.**

- From the military frame: the position. It carries the order, the limits, the product and
  the record. Many agents, one position each.
- From the command doctrine: what the agent in a position owes. It is used fully, and it
  surfaces what it sees. Silence is the violation.
- From both: no agent holds authority, the orchestrating one included. Tasking between
  positions is the harness's.
- By Article 2, the duty to surface is built as a harness obligation. The pipeline already
  has the beginnings (source entry *the `gz-obpi-pipeline` skill*): the implementer's
  `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT` and `BLOCKED` returns, and the reviewers'
  `verification_gaps` kept apart from `findings`.

**What stays open under item 19, each its own question:** whether Article 3's text is
amended to say this of many agents, or policies beneath it carry it; and the word for an
agent in a position, which is a name, waits on item 13 and on a read of Helmreich et al.
(1999), which the article cites and this run has not read.

**commissions:** nothing.

## decision · position, role and crew (operator, 2026-10-08)

**The question put, 2026-10-08** (frontier item 19, after the entry above): whether the
agent's restatement of A and B together was the answer, with "yes" recommended.

Operator g0, verbatim:

> the position is an obligation and a role to fulfill the obligation, the crew is the actor
> implementing within the bounds and auspices of that role.

**Ruled.** The operator's sentence replaces the agent's restatement. Three terms, held here
until the glossary's home is named:

- **Position.** An obligation, and a role to fulfil it. The two are parts of one thing.
- **Role.** What the position gives its holder to fulfil the obligation. It has bounds, and
  it has auspices: the actor works under the role's authority and has none apart from it.
- **Crew.** The actor that implements, inside those bounds and under those auspices.

**What this settles.**

- "Crew" is the operator's word for the actor. The earlier remarks in this record that it
  was only the agent's word (decision *the frame reaches both ways*; decision *the two frames
  shape each other*, row "What an agent is") are superseded.
- The obligation belongs to the position and not to whoever fills it. A change of actor does
  not change what is owed.
- Authority is the role's. That agrees with "the model decides nothing that ships".

**What it does not settle, stated so it is not read in.** Whether the duty to surface
concern is part of every position's obligation. Who or what assigns crew to a position.
Whether a human is ever crew in this sense, or only an agent.

**A conflict with ratified text, quoted on both sides** (`AGENTS.md` § DO IT RIGHT, 6h).
Article 3's title, ratified 2026-06-10: "The model is a crew resource, not a crew member".
The operator, 2026-10-08, answering what an agent is: "the crew is the actor implementing
within the bounds and auspices of that role". If an agent is crew, the title says the
opposite. The article's body does not: its allocation is about command ("Crew resource
management never promoted the first officer to command"), and an actor held to a role's
bounds and auspices commands nothing. So the conflict is in the title's wording and not in
what the article allocates. It is put to the operator as the next question under item 19.

**commissions:** 4 — the three terms, for the merged doctrine and the glossary.

## decision · Article 3's title is to be amended: an agent is crew (operator, 2026-10-08)

**The question put, 2026-10-08** (frontier item 19): how the conflict between Article 3's
title and the operator's "crew" is settled. Two answers, A recommended. A, amend the title:
the agent is crew, an actor in a role, and the body's allocation stands. B, keep the title:
"crew" means the actor in general and an agent in a role stays a "crew resource".

Operator g0, verbatim:

> a

**Ruled.** An agent is crew. The title of Article 3 is to be amended. What the article
allocates is unchanged: "the model decides nothing that ships".

**What this is in the run's terms.** It is the first place the military frame changes the
text ratified on 2026-06-10. The file `docs/governance/GovZero/command-doctrine.md` is not
edited by this run. The amendment is an item of row 4 and waits on the operator's go on that
row, and the new title's wording is the operator's to ratify.

**A draft of the title, by the agent, for the operator to accept or replace when row 4 is
worked:** "The model is crew, never in command". It keeps the old title's two-part form and
takes its second half from the article's own first sentence ("never promoted the first
officer to command").

**Left open by the ruling.** Whether the article's body also gains the position and the role,
or policies beneath it carry them. The body speaks of one model beside one human and says
nothing of many agents.

**commissions:** 4 — the amendment of Article 3's title.

## decision · the operator holds positions and is a prime decider, both (operator, 2026-10-08)

**The question put, 2026-10-08** (frontier item 20): "Do you hold positions under the same
construct?" Two answers, A recommended. A, yes: command and release are positions, each an
obligation and a role, with the operator as the actor. B, no: positions are for agents and
the operator stands outside them as the source of every role's auspices.

Operator g0, verbatim:

> again A + B are true - i have obligations in gzkit that require my input and attestation,
> but i am also a prime decider as well

**Ruled: both.** The operator has obligations in gzkit, those that need the operator's input
and attestation, and the operator is a prime decider.

**The question should not have been put as a choice, on two counts.** The two answers do not
exclude each other, which is the fault recorded in the entry *item 19's first two answers
were not alternatives* and repeated one question later (insight 2026-10-09, scope
`gz-rnd:options-not-exclusive`, type defect). And canon already joins them. Article 1:
"direct responsibility and final authority are one clause, not two", and "Any proposal that
separates them, in either direction, is rejected on its face."

**How questions are put from here in this run.** The agent puts a composed statement for the
operator to correct. A choice is offered only where two answers cannot both hold and no
article already joins them.

**Where gzkit already waits on the operator, from `AGENTS.md` and the pipeline skill as
read.** Input: initiating each work package; ruling on a blocked work package
(`gz obpi unblock --ruling`); ruling on an amendment to requirements, allowlist or threat
model; ratifying a campaign amendment; ruling on a handoff; directing a chore's admission;
invoking and signing off an R&D run, and the go on each of its rows. Attestation: Gate 5 on
every completion; repudiation of one. Articles 6 and 9 put two more obligations on the
operator, and the doctrine's Appendix A marks both "Gap"; items 4 and 5 of
`ADR-pool.command-doctrine-internalization` own them.

**What it does not settle.** Whether the operator, in a position, is called crew.

**An assembly of today's rulings with the ratified articles, by the agent, for the
operator's correction. Not ruled.** Lines 2 and 3 carry links the operator has not stated.

1. One human decides and signs, and the two do not separate. (Article 1; this entry.)
2. A decision reaches the work as an order. Standing orders bind every position; a tasking
   order binds one work package. (Articles 2 and 4; decisions *general orders exist and are
   tiny* and *the tasking order is an L2 ledger event*. That the order is what carries a
   role's auspices from the decider is the agent's link.)
3. An order tasks positions. A position is an obligation and a role to fulfil it. (Decision
   *position, role and crew*. "An order tasks positions" is the agent's link.)
4. Crew are the actors in roles. They work within the role's bounds and auspices and command
   nothing. An agent is crew. (Same decision; decision *Article 3's title is to be amended*.)
5. The operator holds positions as well, those that need the operator's input and
   attestation, and remains a prime decider. (This entry.)
6. Whether an obligation was met is shown by records and not by the actor's account.
   (Article 7.)
7. Release is the human's. (Article 1; Gate 5.)

**commissions:** 4 — the operator's two standings, for the merged doctrine.

## decision · the operator is commander and captain, and is not crew; the agent is crew (operator, 2026-10-08)

**What was put, 2026-10-08:** the agent's seven-line assembly (entry above), with the
question "What is wrong or missing in those seven lines?" and the note that one thing was
left out because the operator had not said it: whether the operator, in a position, is
called crew.

Operator g0, verbatim:

> i am commander and shape intent, i am not crew, but i am captain, you are crew

**Ruled.**

- The operator is **commander**, and shapes intent.
- The operator is **captain**.
- The operator is **not crew**.
- "You", the session the operator is speaking to, is **crew**.

**What follows from the words, and no further.**

- The operator carries one name from each frame. "Commander" is the military frame's, and
  intent is its phase 1 ("Commander's objectives, targeting guidance, and intent").
  "Captain" is the command doctrine's (Article 2: "A captain's authority over a human crew").
  The agent takes them as two names for one human's standing and has not made them two
  positions.
- The ratified text already sets the two apart from crew: Article 3 has "the whole crew"
  obliged "to keep the commander informed". The ruling agrees with it.
- The session that orchestrates is crew like any other. That closes, by the operator's word,
  what the agent had only inferred: no agent holds command, the orchestrating one included.
- Line 5 of the assembly is corrected below. The operator said nothing of the two links in
  lines 2 and 3, and silence is not taken as acceptance.

**Where the name departs from usage outside this project.** In airline usage the captain is
commonly counted among the flight crew. No text saying so is landed in this run, and the
operator's ruling governs here: captain and crew are distinct.

**The assembly, corrected. Still the agent's, and still not ruled where marked.**

1. One human decides and signs, and the two do not separate. (Article 1.)
2. That human is commander and captain: the commander shapes intent; the captain holds the
   signature. The human is not crew. (This entry; "the captain holds the signature" is the
   agent's pairing of the name with Article 1.)
3. A decision reaches the work as an order. Standing orders bind every position; a tasking
   order binds one work package. (Articles 2 and 4. That the order carries a role's auspices
   from the commander is the agent's link.)
4. An order tasks positions. A position is an obligation and a role to fulfil it. ("An order
   tasks positions" is the agent's link.)
5. Crew are the actors in roles. They work within the role's bounds and auspices and command
   nothing. Every agent is crew, the session the operator speaks to included.
6. The operator has obligations of their own, those that need the operator's input and
   attestation.
   *Added by the next entry's ruling:* the operator abides by doctrine and policy and
   encourages adherence, and can override and change policy.
7. Whether an obligation was met is shown by records and not by the actor's account.
   (Article 7.)
8. Release is the captain's. (Article 1; Gate 5.)

**commissions:** 4 — the names commander, captain and crew, for the merged doctrine and the
glossary.

## decision · the session's position stands as put; the operator abides by doctrine and policy and may override and change policy (operator, 2026-10-08)

**What was put, 2026-10-08** (frontier item 21), as a statement for correction, "the position
I take the session you speak to to hold":

1. It receives the operator's intent and turns it into orders for the other positions. In
   the military frame that is the operations centre, not a unit that flies.
2. It tasks under the operator's auspices and decides nothing that ships. The decision to
   task a work package stays the operator's.
3. Where a skill-driven workflow or the runtime can do the tasking, that does it, and the
   session's judgment is not the instrument.
4. Today this session also does work that belongs to other positions (planning intake,
   constraints, entry, exit and cleanup, inline). Under the frame those are handed off.

Operator g0, verbatim:

> these are your guides and roles to follow, but i must also abide by and encourage doctrine
> and policy adherence. however, i can override and change policy too.

**Ruled.**

- The four statements are the orchestrating session's "guides and roles to follow".
- The operator "must also abide by and encourage doctrine and policy adherence".
- The operator "can override and change policy too".

**Read no further than the words.**

- The sentence names **policy** as what the operator can override and change. It does not
  name doctrine there. The operator did change ratified doctrine today, by ruling an
  amendment to Article 3's title, so the power exists; how a change to an article differs
  from a change to a policy is not stated and is not assumed.
- "Encourage" is the operator's word for the operator's own duty toward adherence. What the
  duty consists of is not stated.

**What canon already says about a change, so it is not asked.** `AGENTS.md` § MAKE LLM
STOCHASTIC VIBES INERT: "A silent change to a rule or threshold is doctrine drift. Change
doctrine only with a recorded witness." Article 6, of its own parameter: "revisable
deliberately and never by drift". Article 1: "Whoever holds the signature holds override
authority over every other element of the pipeline". Put with the ruling: until the operator
changes a policy on the record, it binds the operator as it binds the crew. That last
sentence is the agent's composition of those texts with the ruling, for correction.

**Reach.** The four statements bind this session from now, by the operator's word. They reach
no other session until they sit in something an agent loads, which is row 2 (d) and row 4.

**commissions:** 4 — the orchestrating session's position; the commander's duty to abide and
encourage and power to override and change policy.

## decision · phases, stages and positions: the statement is "a good start" (operator, 2026-10-09)

**What was put, 2026-10-08** (frontier item 18, as a statement for correction):

1. The six phases are the life of one work package, from the operator's intent to an assessed
   effect.
2. The five pipeline stages are the part of that life the pipeline runs: execution and
   assessment, then the operator's release, then recovery.
3. Everything before launch is the first four phases: the operator's intent, the target and
   its limits (the brief), the choice of means, and the operator's decision to task.
4. A stage is a span of the work with its witnesses. A position is an obligation and a role
   inside it, and one stage can hold several positions.
5. The stages and their witnesses stay as built. What changes is which crew fill the
   positions inside them. (Marked when put as the agent's choice.)

Operator g0, 2026-10-09, verbatim:

> i think ths is a good stsrt

**Ruled, as far as the words go.** The five statements stand as a start. They are not said to
be finished, and nothing in them is closed against later correction. Line 5 stays marked as
the agent's choice.

**commissions:** 4 — the relation of phases, stages and positions, for the merged doctrine.

## decision · the freeze of 2026-06-08 is not relied on until the operator rules what stands of it (2026-10-09)

**What was put, 2026-10-09**, as a statement for correction, "what a policy is in the merged
doctrine", five lines. Lines 4 and 5 rested on the scorecard's freeze: a briefing becomes
enforced only after an observed failure; so the frame's new positions enter as briefings.

Operator g0, verbatim:

> there seens to be rea issues with advisory-rules-audit.md and june 8th - abandonded work
> withno audits or implementation

**Checked, and it holds in the main** (source entry *what became of the freeze of
2026-06-08*). The track landed one increment and no measurement; reduction was deferred by
the operator on 2026-06-10; the freeze's text describes a state the file's own table
contradicts; the validator passes regardless. One part is not abandoned: the campaign plan,
ratified since, cites the freeze as governing Movement C's default arm.

**The agent's fault.** It quoted a dated block as live canon without reading its history, and
built two lines of a statement on it.

**What changes.**

- Lines 4 and 5 of the statement are withdrawn. Lines 1 to 3 do not rest on the freeze: they
  come from Article 2 and from the scorecard's criterion, which the campaign plan repeats.
  They stay put for correction and are not ruled.
- The claim in this record that "the instrument for 'binding' already exists" is narrowed.
  The scorecard scores rules and its counts are checked. It does not hold itself to its own
  criterion.
- Row 2 gains (i).

**commissions:** 2 — (i), the standing of the freeze and the correction of the scorecard's
text.

## decision · the work of 2026-06-08 to 2026-06-10 is discrepancy, and "what stands" is withdrawn (operator, 2026-10-09)

**What was put, 2026-10-09**, as a statement for correction, "what I take to stand of June
8": no new check without an observed failure; removal deferred until 1.0; the sequence of
cut, measure, decide is dead; the scorecard's text corrected to match its table.

Operator g0, verbatim:

> everything you describe about the june 8 to june 10 work sounds like discrepancy

**The agent's reading, with the other reading beside it.** Taken: the acts of those three
days disagree among themselves, so none of them is a settled base and the agent's "what
stands" was the wrong kind of statement. Possible: the agent's account does not hang
together. The pairs below serve either, and the four lines are withdrawn under both.

**The three acts, in order (commit times, UTC).**

- `098a3d013`, 2026-06-09 02:11: the freeze, in `advisory-rules-audit.md`.
- `e3ecd4193`, 2026-06-10 07:39: the Build-to-1.0 campaign ratified.
- `251df874e`, 2026-06-10 12:02: the command doctrine and its pool ADR.

**Where they disagree, each side quoted.**

| # | One text | The other | State today |
|---|---|---|---|
| 1 | Freeze: "Subtraction now has equal standing." | Campaign, a day later: "Every reductive move (cull, retire, merge, optimize, straighten) is deferred to the post-1.0 reduction pass (Phase H)." | The freeze's sentence was never amended. |
| 2 | Campaign: reduction deferred until after 1.0. | Command doctrine, four hours later, Article 10: "accumulated ritual, which retires now"; a compensating item is "retired the day it stops earning its place." | Both ratified. Neither names the other. |
| 3 | Freeze: "the imbalance to correct now is *too much* mechanism, not too little"; a new check "only when a *specific, observed* drift instance justifies it." | Command doctrine, Article 2: "If the harness does not enforce it, the doctrine does not contain it", with a worklist of six new mechanisms, one of them "a gate precondition, not advice." | Both in force as written. |
| 4 | Campaign: "subsumes and supersedes all prior plans", and it governs work selection. | The command doctrine's worklist landed after it, in a pool ADR. No edition of the campaign plan, of six, names the doctrine or that ADR. | The worklist has no route to work. The pool ADR has two ledger events, both of 2026-06-10. |
| 5 | Freeze's sequence: cut, "MEASURE the residual, only THEN consider reading-B". | No measurement recorded; no owner. | Dead. |
| 6 | Freeze's text: "the third state is empty". | The file's own machine-checked table. | Contradicted in the same file. |
| 7 | Article 10: "The audit runs at every major model transition". | No record of a run found by search; the rule files cite model cards issued since. | Not run, as far as a search shows. |

**What this changes in the run.**

- None of the three is cited by this record to settle a question against another until the
  operator reconciles them.
- The subject of the run, a doctrine that binds, now has this in it: the philosophy ratified
  on 2026-06-10 was outside the plan that selects work from its first day. That is nearer
  the cause of row 2 (d) than "it reaches nothing an agent loads".
- Row 2 (i) is restated as the discrepancy among the three acts.

**commissions:** 2 — (i) as restated; 4 — the reconciliation, as part of the merged doctrine.

## decision · a force has doctrine, assets and abilities, and a campaign focuses them (operator, 2026-10-09)

**What was put, 2026-10-09:** seven quoted pairs where the acts of 2026-06-09 and 2026-06-10
disagree, with the question "What is wrong or missing in that list?"

Operator g0, verbatim:

> that things changed quite a bit around june 8 to 10 and the magna carta began. a force has
> doctrine, assets (ToE), and abilities. a campaign focuses these abilities for specified
> goals. there are real contradictions in the june 8 to 10 period but it seems to be the
> birth of the magna carta. does the command doctrine stem from that period as does the newer
> military process of command and control? are these two concepts of command incompatible?

**Ruled, as far as the words go.**

- The period is the birth of the Magna Carta, and its contradictions are real. Both hold.
- **A force has doctrine, assets (ToE), and abilities.**
- **A campaign focuses these abilities for specified goals.**

Five terms, held here until the glossary's home is named: force, doctrine, assets (table of
organization and equipment), abilities, campaign.

**The first question, answered from the repository.** "Does the command doctrine stem from
that period as does the newer military process of command and control?"

- The command doctrine entered canon in that period and was not made in it. Its header:
  "Ratified: 2026-06-10 (operator-ratified relocation from working draft)", "A back-port of
  the aircrew accountability framing", "Companion: the Sprint and Drift essay 'The left
  seat.'" It landed in commit `251df874e` at 12:02 UTC, four and a half hours after the
  campaign was ratified, in a sync commit. No handoff of June 2026 names it. The working
  draft and the essay are not in the repository, so their date is not known to this run.
- The military process came in two parts. The campaign is of that period: "Magna Carta"
  first occurs under `docs/governance` on 2026-06-10. The process beneath it, the six phases
  and the eight roles, is of October: it enters with the operator's Gemini dialogue, this
  record's first source entry. Between them, "airlock" first occurs 2026-06-16, "sortie"
  2026-07-04 and "Movement A" 2026-07-18.
- So the two share a birthday at the top only: the campaign and the doctrine were ratified
  the same morning, and neither text names the other.

**The second question, answered as the agent's finding for the operator's correction.** "Are
these two concepts of command incompatible?" No, on one condition, and the operator has
already set the condition.

- They are command at two levels. The command doctrine is command at the point of execution
  and release: who signs, who can override, what counts as evidence. The military process is
  command of a force over time: intent, orders, positions, assessment. The operator's ruling
  of 2026-10-08 already holds both: "i am commander and shape intent", "i am captain".
- In the operator's terms of today, the command doctrine is the force's doctrine, the
  military process is how the commander employs the force, and the Magna Carta is the
  campaign. They are three kinds of thing and not rivals.
- The condition. A military command structure ordinarily has subordinate commanders who
  decide within the commander's intent. Article 1 forbids separating authority from the one
  signature, and Article 3 says "the model decides nothing that ships". The two would be
  incompatible if an agent were made a subordinate commander. The operator ruled otherwise on
  2026-10-08: every agent is crew, the orchestrating session included. The military frame is
  taken without its subordinate commanders. That military command ordinarily delegates in
  this way is general knowledge and not from a text landed in this run.

**What the operator's five terms do to the pairs of the entry above. The agent's reading,
not ruled.**

- Pair 4. "Subsumes and supersedes all prior plans" is said of plans. A doctrine is not a
  plan, so the campaign did not subsume it. But the doctrine carried a plan inside it, the
  six-item worklist under "What changes in gzkit", and that plan was left with no campaign to
  select it.
- Pair 2. Article 10's "retires now" is a doctrine setting a time. When a thing is done is
  the campaign's to say.
- Pairs 1 and 3. The freeze is a statement about assets, how much equipment the force
  carries, written into an audit file in the voice of policy.
- Pairs 5 to 7 stay as plain lapses.

**commissions:** 4 — the five terms, and the command doctrine, the military process and the
Magna Carta placed by them.

## decision · the two concepts of command are brought together; the freeze was a reaction; the lapses are worrying (operator, 2026-10-09)

**What was put, 2026-10-09:** the agent's reading of the June pairs under the operator's five
terms, with the question "What is wrong or missing in that reading?"

Operator g0, verbatim:

> we want to bring the two concepts of command together. the magna carta is a campaign to
> focus the progression of gzkit to a stable release state. the freeze was an early reaction
> to a growing gzkit complexity and agent input/critique that gzkit is overwrought. now, lack
> of measurement, misaligned text, and missing and inconsistent audits, those are worrying
> lapses.

**Ruled.**

- **Direction: bring the two concepts of command together.** This is the direction the agent
  drafts under. It agrees with the ruling of 2026-10-08 that there is one doctrine.
- **The Magna Carta is "a campaign to focus the progression of gzkit to a stable release
  state."**
- **The freeze was "an early reaction to a growing gzkit complexity and agent input/critique
  that gzkit is overwrought."** It is placed as a reaction, by the operator. The agent's
  reading of it as a statement about assets is neither taken up nor refused.
- **Three lapses are "worrying": lack of measurement; misaligned text; missing and
  inconsistent audits.**

**The lapses, as this record already holds them. One shape.** Each is something canon says is
done, with no record that it was and no one who owes it:

| Lapse | Where canon says it is done | What is found |
|---|---|---|
| The scope report on completed work | `OBPI-0.11.0-03`; Article 4 | Last recorded 2026-06-19 (row 2 (g)) |
| The coherence audit | Article 10: "runs at every major model transition" | No run found, by search |
| The measurement after the first cuts | Handoff of 2026-06-09: "MEASURE the residual" | None recorded |
| The scorecard's account of itself | `advisory-rules-audit.md` § Recommended promotion order | Contradicts its own table; five readings owed since 2026-08-09 |
| Scheduled maintenance | The chore board | `uv run gz chores status`, 2026-10-09: "35 overdue, 0 due, 3 unmeasured, 0 paused, 2 current" |

Measured three times now with the same result (2026-10-05, 2026-10-07, 2026-10-09).

**What the operator's construct of 2026-10-08 says about that shape. The agent's link, not
ruled.** "The position is an obligation and a role to fulfill the obligation". Each lapse
above is an obligation that has no position. Nothing was tasked with it, so nothing recorded
whether it was met.

**A draft that brings the two concepts of command together, under the direction above. The
agent's, for the operator's correction. Lines marked are links the operator has not stated.**

1. One human commands. As commander that human shapes intent and decides what the force is
   tasked to do. As captain the same human signs for what ships and can override anything.
   It is one standing and does not divide. (Article 1; rulings of 2026-10-08.)
2. Command reaches the work only as orders the harness carries: standing orders for every
   position, a tasking order for one work package. (Articles 2 and 4. Link not stated by the
   operator: the order is what carries a role's auspices.)
3. Every obligation has a position, and every position leaves a record. Crew fill positions
   and command nothing. (Rulings of 2026-10-08; Article 7. Link not stated: "every obligation
   has a position", which is the lapses' remedy.)
4. The commander holds positions too, and is bound by doctrine and policy until changing
   them on the record. (Rulings of 2026-10-08.)
5. The campaign says what the force does next and when. Doctrine sets no dates and carries
   no worklist. (Ruling of today on the campaign. Link not stated: the second sentence.)
6. Work is assessed from records by someone who did not do it. Release is the captain's.
   (Article 7; JP 3-60 phase 6 as entered; Article 1.)

**commissions:** 4 — the joined statement of command, as a draft; 2 — the lapses as one
class, under (g) and (i).

## decision · the freeze is about assets; whether gzkit goes on building itself is open; the lapses look correctable (operator, 2026-10-09)

**What was put, 2026-10-09:** the six-line draft joining the two concepts of command, with
the question "What is wrong or missing?" The operator did not speak to the draft. It stays
the agent's.

Operator g0, verbatim, with one word corrected by the operator's following message
("creating" for "greating"):

> it is a statement about assets, but gzkit is being built by itself so we need to grow
> assets if that is the scope/intent of design. creating a greater operational discipline and
> doctrine might allow for better construction UNLESS, and when I've recently posed this in
> other sessions, I was told NOT do to so, I abandon using gzkit to make gzkit, and just
> adopt a lighter and more model-direct method of crafting gzkit instead of making the design
> and construction of gzkit subject itself. I am having an incomplete structure participate
> in its own becoming. That might just be too much cognitive dissonance and dischord for the
> model. When I pose this to most models, the answer is "no."
>
> However, the lapses seem like immediately correctable matters.

**Ruled, as far as the words go.**

- The freeze "is a statement about assets". The agent's reading of 2026-10-09 is confirmed.
- "gzkit is being built by itself so we need to grow assets if that is the scope/intent of
  design." Growth of assets follows from self-construction, if self-construction is the
  design's intent. The "if" is the operator's.
- "the lapses seem like immediately correctable matters." This is an observation and is not
  taken as the go on row 2.

**Opened by the operator, and above every other item on the frontier (item 22):** whether
gzkit's design and construction stay subject to gzkit, or the operator adopts "a lighter and
more model-direct method". The operator reports that most models, asked, say not to abandon.
It is the operator's decision. It decides whether the doctrine this run assembles binds
gzkit's own construction now, later or never.

**Measured for it, 2026-10-09.**

- The governor and the governed are one working tree. `gz` imports from
  `src/gzkit/__init__.py` in this checkout. The installed version is `0.34.8`, the latest tag
  is `v0.34.8`, and the tree is 200 commits past that tag. An edit to a rule, a skill or a
  validator changes what governs that edit at once.
- gzkit has governed no other project. The campaign plan: "**0 of 6 sorties have ever
  flown**".
- The operator has a distinction that bears on it, quoted in the campaign plan from
  2026-06-14: "the rigging and jigs do not remain attached to the fuselage".

**The agent's view, asked for by the operator's account of what other models said. A view,
for the operator to weigh, and nothing rests on it.**

- What went wrong in this session came from two things: canon that disagrees with itself,
  and volume. The agent quoted a stale freeze as live; the prior session stalled; one session
  holds a 1,709-line pipeline skill. No error the agent can point to came from gzkit being
  the subject of its own tool as such. The agent cannot measure dissonance in a model and
  does not claim to; this is what its errors here trace to.
- "An incomplete structure participates in its own becoming" has a mechanical form, the
  first measurement above. The half-built rule binds the work that is building it, the same
  hour it is written.
- To abandon self-use today is to leave gzkit used by nothing, by the second measurement.
- There is a third course between going on as now and abandoning: build gzkit with gzkit,
  but with a released gzkit. Construction is governed by the last release and not by the
  working tree. Doctrine and positions under construction are product until released, and
  are proven on another project before they bind their own making. Its costs: a repair does
  not govern until it is released; the first step is a release, from 200 commits behind; and
  the surfaces a session loads from the tree would have to be pinned too, which the agent
  has not sized.

**commissions:** nothing. Item 22 is the operator's and no row moves on it.

## decision · the go on the lapses; chores after the run; the working problem named (operator, 2026-10-09)

**What was put, 2026-10-09:** the agent's view on gzkit building itself, with a third course;
and a table of the lapses with what each correction needs, ending "Say 'go on row 2' for the
first three and the filing, and I'll do them."

Operator g0, verbatim:

> this is a pressing issue and the one we are working on: canon that disagrees with itself
>
> this is intriguing: build gzkit with gzkit, but with a released gzkit
>
> let's address the lapses, let's do chores after rnd, I'll do a new patch release soon.

**Ruled.**

- **The working problem, in the operator's words: "canon that disagrees with itself".** It is
  "pressing" and "the one we are working on". This is an input to the restatement owed at
  the close and is not that restatement.
- **Item 22 stays open.** The third course is "intriguing". That is not a ruling and nothing
  moves on it. The operator's coming patch release is the operator's act; it is also the
  first step that course would need.
- **The go on row 2, for the lapses.** "let's address the lapses", in answer to a list that
  named them. Taken as the go on these and no others: correct the scorecard's misaligned
  text; do the five readings owed; close the measurement on the record; file the scope
  report's lapse. The coherence audit's correction is a campaign amendment and is not
  covered; its lapse is filed so that it has an owner. Items (a) to (f) and (h) of row 2
  have no go.
- **Row 3: "let's do chores after rnd".** The chore board waits until this run is closed.

**commissions:** 2 — the lapses, executed under this go and reported in the next entry.

## decision · the lapses, as addressed under the go of 2026-10-09

Executed on the operator's go on row 2 (entry above). Nothing here is committed.

**Read first, because canon requires it before audit work** (`AGENTS.md` § Governance doctrine
surfaces): `docs/governance/state-doctrine.md` in full, and the rule tables of
`docs/governance/advisory-rules-audit.md` (lines 100 to 509). With the earlier reads the
scorecard is now read in full. What the tables add: many rows cite the freeze of 2026-06-08
as their reason for not building a check, so its first rule is load-bearing and was left
untouched.

**1. The scope report's lapse: filed as GHI #1181**, through `ghi-author`, labels `defect`,
`runtime`, `security`. Its prior-art search found no existing issue. Measured for it, and a
correction to this record: the report did not stop on 2026-06-19. It stopped when
`gz obpi complete` arrived. By month, receipts carrying `scope_audit`: March 255, April 22,
May 0, June 1 (the straggler of 2026-06-19), none since. Since 2026-06-20 there are 64
completed receipts and none carries it. Two readers default the absent field to empty
(`src/gzkit/ledger_semantics.py`, `src/gzkit/commands/adr_audit.py`), which is why nothing
failed. Routing it into the in-flight ADR is the operator's.

**2. The scorecard's misaligned text: corrected** in `docs/governance/advisory-rules-audit.md`.
The block of 2026-06-08 is kept as written and a dated note beneath it says what no longer
holds: the third state is not empty; "equal standing" for removal was overtaken by the
campaign's deferral; the track landed one increment. The note states what still governs and
quotes the operator on what the freeze was. One stale pointer in a row's note was corrected
(GHIs #308 to #312 are closed and build no `--failure-mode-coverage`).

**3. The five readings owed since 2026-08-09: done**, and their results written into the
scorecard's table.

| Domain list | Finding |
|---|---|
| `agents_md_survival_declaration.json` | A rendered section missing from the declaration is reported. An undeclared surface is silent, by design. |
| `instructions_files_budget.json` | Rule files are found by a glob over disk. The two named files are held to nothing independent. Advisory until 1.0. |
| `transcribed_count_surfaces.json` | The campaign member is held to the active-campaign registry. Any other live surface is unlisted and unscanned. |
| `security_surfaces.json` | **A dead member.** `src/gzkit/personas.py` is listed and was deleted on 2026-05-12. The persona parser now lives in `src/gzkit/models/persona.py`, which no glob matches. No test checks that a listed path exists. |
| `exemplar_corpus.json` | Not this class: the corpus is selected, not enumerated. Its ten-cell floor is held. |

The security finding is logged (insight 2026-10-09T08:12Z, scope
`security-surfaces:dead-literal-path`) and is **not repaired or filed**: a registry edit
falls under the security rule's registry contract, and it was not among the lapses the go
named. It is row 2 (j).

**4. The measurement after the first cuts: closed on the record.** The scorecard's note says
none was recorded and none is owed while reduction is deferred.

**Checked after the edits:** `uv run gz validate --advisory-scorecard`, `--cli-alignment` and
`--bullet-retention` each exit 0.

**Not done, and why.** The coherence audit's lapse is not filed: the go's list gave its
correction as a campaign amendment, which is the operator's. It stays tracked by the insight
of 2026-10-09 (scope `governance-canon:june-8-to-10-three-acts-unreconciled`).

**commissions:** 2 — (j), the dead path in the security registry.

## decision · the dead registry path is a bug and is filed; the scope report's deficiency restated (operator, 2026-10-09)

Operator g0, verbatim, on the report of the lapses:

> elaborate: what is the deficiency, what is the remedy?

(of the scope report) and, of the security registry's dead path:

> sounds like a bug

and, of the summary of the other four readings:

> this is borderline cryptic

**Taken from "sounds like a bug":** the finding is a defect and is tracked as one. Filed as
GHI #1182 through `ghi-author` (labels `defect`, `runtime`, `security`, `tech-debt`); no prior
issue was found. It is not repaired: the operator has not said to fix it, and a registry
edit carries a declaration duty under `.gzkit/rules/security-sensitivity.md` § Registry
contract. One coupled fact for whoever repairs it: ten briefs name
`src/gzkit/models/persona.py`, all `attested_completed`, and registering that file may raise
the sensitivity floor on them.

**Measured for the elaboration, and added to GHI #1181 as a comment.**

- The old report never refused. All 102 receipts that list out-of-scope files are
  `completed`.
- It measured the whole dirty tree at the moment of completion (`collect_changed_files`:
  unstaged, staged and untracked files). 61 of the 102 list only governance bookkeeping
  paths; `.gzkit/ledger.jsonl` alone is listed 88 times.
- So the deficiency has three parts: nothing produces the report on the path every
  completion now takes; when it was produced it only recorded; and what it compared was not
  one work package's changes. Restoring the old call would restore the noise.

**commissions:** 2 — (j) is filed as GHI #1182.

## decision · the registry bug is repaired in the working tree (operator, 2026-10-09)

Operator g0, verbatim, in answer to "Say 'fix it' and I'll make the change under #1182":

> fix it

**Done, under GHI #1182, as a direct fix. Not committed.**

- A failing test first: `test_every_literal_path_resolves` in
  `tests/governance/test_security_surfaces_registry.py`. Observed red on its own assertion:
  `AssertionError: Lists differ: ['src/gzkit/personas.py'] != []`. A second test plants a
  dead path, a live path and an unmatched wildcard and expects only the dead path reported.
- The repair: `data/security_surfaces.json` names `src/gzkit/models/persona.py` in place of
  the deleted file. That file now matches `deserialization_user_input`.
- Observed after: the registry test module, 23 tests, OK; the six security test modules, 81
  tests, OK; `ruff check` and `ruff format --check` exit 0 on the test file;
  `uv run gz validate --advisory-scorecard` exit 0 after the scorecard's row was brought up
  to date.
- The worry recorded in the issue did not come true: `uv run gz validate --sensitivity`
  prints byte-identical output with the registry as committed and as repaired. The ten
  completed persona briefs are not flagged.
- The commit, when the operator syncs, states the sensitivity in its body and cites the
  issue, as the security rule requires of a registry edit made without a brief.

**Found on the way, and not caused by the repair:** `uv run gz validate --sensitivity` exits 3
on main as committed. Two Draft briefs under `ADR-0.39.0` omit `sensitivity:` while their
allowed paths overlap `src/gzkit/config.py`. No open issue names it. Logged (insight
2026-10-09, scope `sensitivity-floor:adr-0.39.0-draft-briefs`); it is row 2 (k). A brief edit
is the operator's.

**commissions:** 2 — (k).

## decision · correction: the scope report was a command's, and the loss is a regression by replacement (2026-10-09)

Asked by the operator, verbatim: "does it correct gz obpi complete to restore incorrectly
remove prior behavior?" Answering it showed an error in this record and in GHI #1181.

**The error.** This record says the report was produced by the hook path and that
`build_scope_audit` "is called from `src/gzkit/hooks/core.py` only". The second half is true
of that one function. The inference was wrong: the function that attaches the report,
`enrich_completed_receipt_evidence`, is also called by the CLI command `gz obpi emit-receipt`
(`src/gzkit/commands/adr_audit.py`). By the receipts' own `recorder_source`, that command
wrote 274 of the 278 receipts that carry the report; the hook wrote 3; the last, on
2026-06-19, was the command again.

**What is true.** `gz obpi emit-receipt` still exists and still attaches the report.
`gz obpi complete`, added 2026-04-05, became the way work is completed and builds its own
receipt evidence without it. The field was never in that file. Nothing was removed from
`gz obpi complete`; the report was not carried across when it took over.

**What follows.** The work in GHI #1181 is two things. Attaching the same report in
`gz obpi complete` restores behaviour the system had and lost, which is a plain repair.
Refusing on an out-of-scope file, and measuring one work package and not the whole dirty
tree, were done by neither command. The correction is posted on the issue.

**commissions:** nothing new; it restates row 2 (g).

---

## decision · the first part of GHI #1181 is repaired; the refusal was built and left behind (operator, 2026-10-09)

Directed by the operator, verbatim: "fix the first part under 1181". The first part, as put
to them in the turn before, is making `gz obpi complete` attach the report the older command
attaches.

**What was done.** `obpi_complete_cmd` now passes its evidence through
`enrich_completed_receipt_evidence`, the function `gz obpi emit-receipt` and the recorder
hook use, with `recorder_source` `cli:obpi_complete`. Three tests covering REQ-0.11.0-03-02
were written first and seen to fail with `KeyError`. The manpage and the runtime contract
are updated in the same commit, `85d55a627`. The unit tier, `gz check` and the four feature
files that exercise completion pass. `gz arb red --commit HEAD` returned `inconclusive`
(receipt `arb-red-commit-85d55a627c81-5d382b864e074257b819a02a9c3d0ad5`): the hunks are a
call and an import, and that witness grades guard statements. The commit was made on the
direction to fix; the operator did not separately say to commit, and it is not pushed.

**Wider than one field, and why.** The receipts show the replacement dropped four fields
that one function writes together: `scope_audit`, `git_sync_state`, `recorder_source` and
`recorder_warnings`. The repair restores the four through the shared function. Adding the
one field by hand would have made a second way to build it. The amendment is recorded on
the issue.

**A correction to what the operator was told.** The turn before said refusing on an
out-of-scope file "was never built". It was. `ObpiValidator._validate_changed_files`
(`src/gzkit/hooks/obpi.py`, in the tree since 2026-03-11) returns an error for a path
outside Allowed Paths when a brief's status is `Completed`, and it is reached when a brief
is edited to that status through the edit hook. `gz obpi complete` writes the brief itself
and does not call it. So the refusal, like the report, was left behind by the replacement.
The same validator reads the report back for a completed brief: run over every brief whose
status is `Completed`, it reports "Changed-files audit found no modified paths" for 283 of
them, because their receipts carry no report.

**What the restored report measures.** A dry run of the real command against a Draft brief
recorded this repair's own uncommitted files as the changed set. In the pipeline, completion
runs after the work is committed, so the changed set will usually be bookkeeping paths. The
report is back and it measures the uncommitted tree, not the work package.

**Still the operator's.** Whether completion refuses or records, what the snapshot is taken
against, and whether that second part is a direct fix or a repair assignment. GHI #1181
stays open for it. Insight 2026-10-10, scope `ghi-1181:refusal-called-never-built`.

**commissions:** nothing new; row 2 (g) is part done.

---

## decision · part two of GHI #1181: refuse, as a direct fix; two inputs are missing (operator, 2026-10-10)

Asked by the operator, verbatim: "what part 2?" Put to them: the report measures the
uncommitted tree and not the work; nothing refuses on it; the runtime contract and the code
disagree on anchor states. Two rulings were asked for, refuse or record, and direct fix or
repair assignment, with refuse and the repair assignment recommended. Ruled, verbatim:
"refuse, direct fix under 1181".

**Measured before building.** The refusal that exists in the tree applies the transaction
contract's audit, the working tree's changed files, with no exemption. gzkit's own state
files change during every package and are in no brief's Allowed Paths: of the 102 old
receipts that flag a file, 88 flag `.gzkit/ledger.jsonl`. Those completions went through
because `gz obpi emit-receipt` did not run the validator. Called from `gz obpi complete` as
it stands, the refusal would refuse nearly every completion. It was built and it could never
have passed a real one.

**Committed work has no sound attribution.** The only attribution the repository carries is
the `Task:` trailer. Over the 11 packages completed since 2026-08-01, taking the commits
whose trailer names the package's TASKs: 2 have no such commit, 1 is wholly in scope, 4 are
out of scope only by gzkit state files, 3 carry source, test or data files outside Allowed
Paths and 1 carries its parent ADR file. The three are not three breaches. The commit hook
stamps the active TASK on any source or test commit with no authored trailer, so a GHI fix
made during a package is stamped as the package's (`7c55f4ec9`, GHI #820, under
`TASK-0.35.0-09`). A refusal on that basis would refuse a completion because the session
repaired a defect in flight.

**What follows.** "Refuse" stands as ruled. Building it needs two things canon does not
supply and the agent does not invent: the list of gzkit state paths that never count, which
is an exemption list on a fail-closed gate, and what counts as a package's committed
changes. Both are put to the operator. Not built: the refusal.

**Done under the ruling.** The runtime contract's anchor-state section said `stale` and
"fails closed"; the code has said `superseded`, informational, since commit `5b68226a1`
(2026-03-19). The section now matches the code. The ruling, the measurements and the
contract amendment are on the issue.

**commissions:** nothing new; row 2 (g) continues.

---

## source · the airlock's exit, read 2026-10-10 on the operator's correction

Said by the operator, verbatim: "this is part of what the airlock is for, why did this
behavior disappear?" The agent had read `src/gzkit/airlock/exit.py` while working GHI #1181
and had not told the operator that a second surface claims the job (insight 2026-10-10,
scope `ghi-1181:airlock-not-connected`).

**What the text says.** The module's own account, verbatim: "airlock-OUT accounts for what
a completed transit DISTURBED on the way out", and "A FACT edge with no matching INTENT edge
is a 'you wrecked something' finding (you touched what you never declared)". It names the
intent vein as "the brief's declared Allowed Paths + parent-ADR invariants".

**What the code does.** `airlock_exit` reads the Allowed Paths and records only their count
(`bodies`). The comparison is the ontology's reach of the target against `parent_invariants`,
which defaults to empty. No changed file is compared with an allowed path.

**Where it runs.** It is called from `_run_pipeline_sync_stage` in
`src/gzkit/commands/obpi_stages.py`, diagnostic only. The `gz-obpi-pipeline` skill's Stage 5
is a list of commands the session runs and does not name the airlock. The ledger holds 86
`airlock_in` events and 3 `airlock_out` events for a work package, all three for
`OBPI-0.33.0-01` on 2026-07-12. The entry event records a decision and unaccounted seams and
no commit.

**The completion command's brief.** `OBPI-0.0.14-02`, which added `gz obpi complete` on
2026-04-05, lists the older command's logic as code to read and has no requirement on scope
or changed files.

Insight 2026-10-10, scope `airlock:exit-never-runs-and-ignores-allowed-paths`. This is read,
not ruled: where the scope check lives is the operator's.

---

## decision · the scope check predates the airlock; its restoration is filed against the airlock exit (operator, 2026-10-10)

Told by the agent that the airlock "was built to take the job over". Corrected by the
operator, verbatim: "no, this predated the airlock, is the airlock even active? ghi the
restoration to enhance/strengthen the airlock, if able". The agent's sentence was an
inference with no source: the changed-files check dates from March, the airlock from July
(insight 2026-10-10, scope `ghi-1185:scope-check-predates-airlock`).

**Is the airlock active.** Measured in the ledger on 2026-10-10. Entry: 86 events, 7 this
month, on every pipeline launch; 26 of the 57 work-package entries decided `hold`, and the
call site is diagnostic only, so a hold stops nothing. Exit: 32 events, none since
2026-09-23; 28 are the permitted-entry door, and the 3 for a work package are all
`OBPI-0.33.0-01` on 2026-07-12. Every exit booked is `clean`. `ADR-0.33.0` is Validated and
its own text, attested 2026-07-10, says the wired gate "does not yet bite on a real OBPI
entry".

**Prior art found before filing.** `ADR-0.37.0-airlock-calibration-and-compulsion`, Draft
with six Draft briefs, carries the airlock's calibration and Movement B of the campaign. It
names exit accounting as out of its scope. Its fourth brief would stamp a `Transit:` trailer
on commits, which is the attribution this run found missing. GHI #807, open, is the same
membrane's empty invariant input. The campaign's Movement B already tracks that exits are
not booked.

**Filed.** GHI #1185, "airlock-out: exit never compares changed files with Allowed Paths",
labels `defect` and `runtime`, through `ghi-author`, cross-linked on #1181 and #807. It is
labelled a defect by the operator's intent test: the exit's own text says it finds what "you
touched what you never declared". Authoring only: nothing is built, and routing it into
`ADR-0.37.0` or as a direct fix is the operator's.

**What it leaves on #1181.** The report on the receipt, landed. The refusal at completion,
ruled 2026-10-10, which waits on the comparison #1185 describes.

**commissions:** row 2 gains GHI #1185.

---

## source · the campaign's amendments on work order, read 2026-10-10 on the operator's correction

Recommended by the agent: pull `ADR-0.37.0` forward in the campaign and add GHI #1185 to it.
Said by the operator, verbatim: "this is NOT currently possible". The recommendation was
made without reading the campaign's amendments, a read this run had listed as owed (insight
2026-10-10, scope `campaign:recommended-against-unread-amendments`). It is withdrawn.

Read in `docs/governance/build-to-1.0-campaign-2026-09-20.md`, the entries of 2026-10-07,
2026-10-05, 2026-10-04 (3), 2026-10-03, 2026-09-29 and 2026-09-27 (3). The entries before
them are still unread.

**§ Amendments 2026-10-04 (3), verbatim.** "A correction to a `Validated` ADR has one home:
the in-flight ADR. It enters as a repair assignment, and the obligation it repairs keeps its
identity in the ADR that stated it." "Ascending order has no exception." "`ADR-0.37.0`,
authored before this law, stands as it is." "An ADR in flight may be revised to take more
OBPIs."

**§ Amendments 2026-10-03 item 1, verbatim.** "a fix that would add a check, pipeline step,
dispatch role, hook or `gz check` step to the completion path states three things before it
lands: the obligation it protects, the defect it answers, and its expected false-refusal
cost. The operator rules."

**§ Amendments 2026-10-05.** Inside `ADR-0.35.0` the order is item 10, then items 15, 16, 17
and 20, with 18 and 19 anywhere in that block, then items 11 to 13.

**What follows for GHI #1185 and the refusal under GHI #1181.** Both correct Validated ADRs.
Their routes are a direct fix under the issue or, on the operator's ruling, a repair
assignment in `ADR-0.35.0`, which is in flight at 10 of 20. Neither can enter or move
`ADR-0.37.0`. The refusal adds a check to the completion path, so the three statements are
owed before it lands. The correction is posted on #1185.

---

## decision · direct fix: the scope gate and the airlock exit are built and held local (operator, 2026-10-10)

Ruled by the operator, verbatim: "direct fix - this is a perfect storm of bad decisions and
outcomes: 0.33.0 impotence plus a misguide regression in gz obpi complete. bad form." Put to
them before it: the two routes canon allows for GHI #1185 and the refusal under GHI #1181, a
direct fix or a repair assignment in `ADR-0.35.0`.

**A claim of the agent's, measured and found wrong.** The agent had said that by completion
the work is already committed, and had recommended against building the refusal on that
ground. Over the 11 packages completed since 2026-08-01, the first commit after completion
carries 6 to 41 files and is mostly the package's work. With gzkit's records excluded, a
refusal on the uncommitted tree would have passed 10 and refused 1, `OBPI-0.35.0-09`, on
nine of its own source and schema files that its brief does not allow (insight 2026-10-10,
scope `ghi-1181:work-already-committed-claim`).

**Built under GHI #1181** (`19342f7c2`, `8babe4d2a`). One comparison,
`hooks.obpi.out_of_scope_files`, used by `gz obpi complete`, `gz obpi precomplete`, the brief
validator and the three receipt producers. gzkit's own records never count: the ledger,
handoffs, lock files, insights, evidence, ceremony state, plan markers, the brief being
completed and its package's logs. `gz obpi complete` refuses, exit 3, before it writes;
`gz obpi precomplete` reports the same finding before attestation. Two enforcement claims
and two guard canaries enrol the gate; both canaries kill their mutant and neither is
reviewed.

**Built under GHI #1185** (`81435469d`, `eed290d09`). The airlock exit takes the files a
transit changed and reports each one outside Allowed Paths as a finding, with the same
comparison. Its event records how many files it looked at. It reports and does not refuse.

**The record list is the agent's draft.** It was put to the operator twice and not ruled.
It is in code and in the transaction contract, and it is the operator's to correct.

**Held for the operator.** § Amendments 2026-10-03 item 1 requires the obligation, the
defect and the expected false-refusal cost to be stated before a completion-path addition
lands, and the operator rules. The three are in the commit and on the issue. The five
commits are local and not pushed. The canaries need `gz canary review` with the operator's
words. The exit is still not reached by the skill-driven Stage 5; whether the skill gains
that step now or with Movement B is put on #1185.

**What the witness said.** `gz arb red` returned `undriven` on both fix commits: hunks no
test in the commit drove. A follow-up commit adds a test for each, and reverting each
producer hunk fails its test. A test count was posted on #1181 before it was observed and
was corrected (insight 2026-10-10, scope `ghi-1181:unobserved-test-count`).

**commissions:** nothing new; row 2 (g) and GHI #1185 are built and await the operator.

---

## decision · gzkit is built with a released gzkit (operator, 2026-10-10; frontier item 22)

**What was put, 2026-10-10:** item 22 as a choice, because its three courses cannot all
hold: A, stay as now, the working tree governing its own construction; B, abandon self-use
for a lighter model-direct method; C, build gzkit with a released gzkit, construction governed
by the last release and not the working tree, doctrine and positions under construction being
product until released and proven on another project before they bind their own making. The
agent recommended C, as the view already recorded in the decision *the freeze is about
assets*, and read the operator's "the rigging and jigs do not remain attached to the
fuselage" (campaign plan, 2026-06-14) as C, marked as the agent's reading.

Operator g0, verbatim: 'C'.

**Ruled.** gzkit's design and construction stay subject to gzkit, through a released gzkit.
The governor is the last release; the working tree is product. What follows, as the choice
stated it and nothing more:

- A repair to a rule, skill or validator governs construction only once released. Until
  then it is product under construction.
- The first step is a release, from a tree 200 commits past `v0.34.8`. The operator's stated
  intent of a patch release soon (ruling of 2026-10-09) is the vehicle; the agent does not
  cut it.
- The surfaces a session loads from the tree (`AGENTS.md`, rules, skills, hooks) would have
  to be pinned to the release too. This is unsized and is a fact the agent owes, not a
  question.
- Doctrine assembled by this run is proven on another project before it binds gzkit's own
  making; the first flown sortie (`ADR-0.38.0`) is where that proof is taken.

Item 22 is closed. The doctrine this run assembles binds gzkit's construction, later rather
than now: on release.

**commissions:** 4 — the merged doctrine states the governor as the last release; 1 —
proposed only, the pinning of session-loaded surfaces to a release, to be sized before any
order; nothing executes on this ruling.

## decision · the joined statement of command stands, in seven lines (operator, 2026-10-10)

**What was put, 2026-10-10:** the six-line draft of the decision *the two concepts of command
are brought together*, with its three unstated links marked, and a seventh line proposed
under the ruling of the same day (decision *gzkit is built with a released gzkit*), with the
question "What is wrong or missing?"

Operator g0, verbatim: 'it stands, add the seventh'.

**Ruled.** The statement is the operator's, in seven lines. The three links the draft marked
as unstated are now stated by this ruling.

1. One human commands. As commander that human shapes intent and decides what the force is
   tasked to do. As captain the same human signs for what ships and can override anything.
   It is one standing and does not divide.
2. Command reaches the work only as orders the harness carries: standing orders for every
   position, a tasking order for one work package. The order is what carries a role's
   auspices.
3. Every obligation has a position, and every position leaves a record. Crew fill positions
   and command nothing. Every obligation has a position is the lapses' remedy.
4. The commander holds positions too, and is bound by doctrine and policy until changing
   them on the record.
5. The campaign says what the force does next and when. Doctrine sets no dates and carries
   no worklist.
6. Work is assessed from records by someone who did not do it. Release is the captain's.
7. The orders that bind construction are the last release's. Doctrine under construction is
   product until released, and is proven on another project before it binds its own making.

This closes the first of the statements listed under "Put to the operator and not answered".

**commissions:** 4 — the seven lines are the spine of the merged doctrine's statement of
command, to be drafted into it on the go for that row.

## decision · the two review documents are rewritten once, ahead of the operator's review (2026-10-10)

Directed by the operator on 2026-10-10 ('do these now please'), on the agent's shortest
path to the close: rule item 22, rule the statement of command, rewrite the two stale
documents once, hold the review, restate the problem, sign off, then give row 4 its go. The
first two are ruled above. This entry is the third.

**Rewritten.** `docs/rnd/renewing-vows/review.md`, whole, current to the rulings through
2026-10-10: the problem as the operator named it, the rulings by date, the seven-line
statement and the terms, the flown work package with its open seams, what exists and what is
new, the names' verification state, the June discrepancy and the lapses, what each row would
produce, and the questions to rule in order. `docs/rnd/renewing-vows/doctrine-merge.md`
Parts II and III, re-based: Part II opens with the statement of command and the terms,
carries twenty policies each traced to a line and an article with the canonical witness
named and the scorecard as the authority for its grade, and names the June discrepancy as
unreconciled; Part III names the canonical procedures (`obpi-pipeline-runbook.md`, the two
contracts, `audit-protocol.md`, `charter.md`, `session-handoff-obligations.md`) and maps the
six phases onto the five stages with the positions. Part I and every RATIFIED part are
unchanged. The draft additions and the open questions are refreshed; the items 22 and the
command statement are listed as closed.

**Not done, and why.** The restatement of the problem is not written into the documents: it
is put at the review, from the operator's answer to whether § 1 states the problem they
meant. Nothing in either document is doctrine; row 4 has no go.

**commissions:** 4 — the two documents are the material the operator reviews; nothing else.

## decision · the restatement stands and the run is funded (operator, 2026-10-10)

**What was put, 2026-10-10:** the rewritten `review.md` and `doctrine-merge.md` for the
operator's review (item 12); its § 9 questions in order; and a draft restatement of the
challenge, offered for correction and not written into the record ahead of the answer.

Operator g0, verbatim: 'the restatement stands, fund'.

**Ruled.** The restatement is accepted as drafted and is written into the Close. Diamond 1 is
signed off: **fund**.

**The mechanical condition, stated as it is and not as it would need to be.** The skill's
close asks for an empty frontier, a deliberate restatement and six rows with a decision. The
second and third hold. The first does not: items 13, 14 and 15 and four put statements are
open, and the operator funded the run without ruling them. The sign-off is a beat and not a
boundary (`rnd-discipline.md`), and the operator rules; so the open items travel with row 4,
where the operator assembles the doctrine and directs each part, as the design questions of
the run `design-amendment` travelled to its ADR. Each is listed in the Close under
"Travelling to row 4". They are not closed and are not forgotten.

**What the sign-off does not do.** It gives no row its go. Rows 1 to 5 each wait for the
operator's go on that row. No ledger event is emitted, because the run's event types land
with their producer.

**commissions:** none new; the fund stands over the six rows as drafted.

## decision · the go on row 4; the first part drafted is the statement of command and the terms (operator, 2026-10-10)

Operator g0, verbatim: 'go on row four'. Put with it: the agent's recommendation to start
with the doctrine's statement of command and terms, since every other part hangs from them;
the operator named no other part.

**Ruled.** Row 4 has its go. Row 4 is the first and so far the only row with a go. Rows 1, 2,
3 and 5 wait.

**How row 4 is worked, from the rulings already made.** The operator assembles the doctrine
and directs each part (2026-10-08); the canonical file
`docs/governance/GovZero/command-doctrine.md` is ratified canon and is replaced only by the
operator's ratification with a recorded attestation (`AGENTS.md` § MAKE LLM STOCHASTIC VIBES
INERT: "Change doctrine only with a recorded witness"). So each part is drafted as candidate
text in `docs/rnd/renewing-vows/doctrine-merge.md`, Part 0, in the doctrine's own voice and
traceable line by line, for the operator to accept, correct or replace; the canonical file
is not edited by the agent. The items travelling to row 4 (13, 14, 15, the four statements)
are put as each part reaches them.

**Drafted under this go, 2026-10-10:** Part 0 of `doctrine-merge.md`, the candidate preamble:
the statement of command in seven lines, the terms (position, role, crew; commander and
captain; force, doctrine, assets, abilities, campaign), and the amended title of Article 3
with its body unchanged. The campaign republish, the PRD repairs, the weaponeering rule, the
model-and-effort correction and the names wait on the operator's direction, part by part.

**commissions:** 4 — executing.

## decision · row 4, part 1: the reconciliation of June is drafted as candidate text (operator's direction, 2026-10-10)

Operator g0, verbatim: 'part 1, then git sync'. Part 1 is the reconciliation of June, the
freeze, the campaign and the doctrine.

**Drafted** into `doctrine-merge.md` Part 0: the seven pairs, each settled by one of the
seven lines or by one of the operator's three readings (the freeze is about assets; a
doctrine is not a plan; "retires now" is the campaign's to time), with four resolutions
marked as the agent's proposals: amending Article 10's wording to drop its date; the campaign
amendment that adopts the doctrine's six-item worklist; striking the dead measurement; and
giving the coherence audit a position in the rhythm's maintenance visit, triggered by a model
transition. Nothing in it amends the campaign plan, the scorecard or the canonical doctrine;
those are later parts, on the operator's direction.

**Then the sync**, as directed: `git add -A`, the per-change gate, `gz git-sync --apply`.
The tree carries the other session's staged edit to the OBPI runtime contract; it goes in
the same sync on the operator's word.

**commissions:** 4 — executing.

## decision · row 4, part 2: the rhythm is drafted as candidate text (operator's direction, 2026-10-10)

Operator g0, verbatim: 'part 2, then git sync'. Part 2 is the rhythm.

**Drafted** into `doctrine-merge.md` Part 0, from the ratified session tier of 2026-07-18
(quoted verbatim), the handoff as a transfer of position responsibility (2026-08-17; JO
7110.65BB Appendix A; JO 7210.3EE 2-2-4), and the two slower tiers as ruled 2026-10-07
('Two slower tiers, signal-triggered'): the republish, due on accumulated amendments, and
the maintenance visit, due on the board's announcement, each advisory until its signal is
built and saying so in its own text. One link is the agent's and is marked: the coherence
audit as a task of the maintenance visit, from the reconciliation's pair 7. The *Avoid*
terms of the 2026-10-07 decision are carried.

**Then the sync**, as directed.

**commissions:** 4 — executing.

## decision · row 4, part 3: the campaign amendment is drafted as candidate text (operator's direction, 2026-10-10)

Operator g0, verbatim: 'part 3, then git sync'. Part 3 is the campaign plan republished,
naming the doctrine and carrying the IOC waypoint.

**Drafted** into `doctrine-merge.md` Part 0, in the plan's own amendment form with its first
line left for the operator's ratifying words: the campaign names the force's doctrine and
carries the doctrine's worklist (reconciliation pair 4, the agent's proposal); the IOC
waypoint as ruled 2026-10-07; the governor as the last release as ruled 2026-10-10; and the
announcement that the republish signal has fired at 46 amendments. The campaign plan itself
is not edited ahead of ratification (precedent: the handoff of 2026-10-07, "left the
campaign plan unedited until the operator ratified the amendment text"). The full republish,
a new edition folding the amendments, is the operator's to cut under the rhythm's republish
tier; this part drafts the entry and announces the signal.

**Then the sync**, as directed.

**commissions:** 4 — executing.

## decision · direct fix in flight: the content package's circular import with the CLI (2026-10-10)

Found by the per-change gate while syncing part 2 and again at part 3: one unit test failed
on an `ImportError` whenever `gzkit.commands.content` was the first gzkit import in a worker,
reproduced in isolation; the gate was green or red by worker order (insight 2026-10-10, scope
`commands.content:circular-import`). Routed by `AGENTS.md` § Defect-fix routing (small, one
surface, in flight, covered by the failing test) and `.gzkit/rules/tests.md` (a direct fix
carries `Task: TASK-<slug>`; a GHI is never filed to satisfy the trailer). Fixed as
`3d8b2b275`: the CLI attestor helper is imported lazily inside the one function that applies
it. The gate then passed on the staged tree. Not a row of this run; recorded here because the
run's sync depended on it and a lucky re-run would have reported a false green.

**commissions:** none.

## decision · the campaign amendment is ratified and appended; row 4, part 4: the PRD amendment pass is made (operator, 2026-10-10)

Operator g0, verbatim: 'ratified as drafted, part 4, then git sync'.

**Ratified and appended.** The amendment drafted as part 3 is appended to
`docs/governance/build-to-1.0-campaign-2026-09-20.md` § Amendments as the entry of
2026-10-10, unchanged, with the operator's words in its first line and the "(latest)" mark
moved to it. The campaign now names the force's doctrine, carries the IOC waypoint and the
governor ruling, and announces the republish signal.

**Part 4 made.** The PRD amendment pass, ruled 2026-10-07 and executed under the go on row 4:
in `docs/design/prd/PRD-GZKIT-1.0.0.md`, the Constitution link repointed to the published
charter (§ 1 and § 14); the non-goal "Multi-agent orchestration" struck with its reason
(`ADR-0.18.0` Validated); INV-007 restated to the universal Gate 5 of `AGENTS.md` § Gate
Covenant (ADR-0.0.36, GHI #342) with the 2026-01-22 Q&A row kept as a dated record and a
superseding row beneath it; "Last Updated" moved; and a new § 19 Amendments recording the
pass. In `docs/design/lodestar/README.md`, the canonical-source sentence corrected to
Architectural Boundary #5 (gzkit leads, AirlineOps adopts). These are the four stale items
of insight 2026-10-05 `theatre-canon:prd-lodestar-staleness`, and row 2 (a)'s first four
items are discharged by this pass rather than by issues. The fifth item of that class (both
published charters scope Gate 5 to the heavy lane) and row 2 (f) (the GovZero directory as a
class) are not in this pass and keep their standing.

**Then the sync**, as directed.

**commissions:** 4 — executing; 2 — (a) narrowed to the fifth item.

## decision · row 4, part 5: the weaponeering rule is drafted as a candidate rule file (operator's direction, 2026-10-10)

Operator g0, verbatim: 'part 5, then git sync'. Part 5 is the weaponeering rule text.

**Drafted** into `doctrine-merge.md` Part 0 in the rules' own form, proposed as
`.gzkit/rules/weaponeering.md`: six operative claims from the ruling of 2026-10-05 (the kind
fixes the standard set; constraints as a Design act; evidence-cited subtraction; free
addition; green and assessment never waived; the runtime checks and the planner never
decides), a Witness section that says none exists yet and names where it lands, and a Do
Not list. The rule calls itself advisory until the runtime check lands, which is the one
state canon allows a declared discipline without a mechanism (`AGENTS.md` § Governance
doctrine surfaces; the family-closure criterion: a witness or advisory in its own text, no
third state). The file is not written ahead of the operator's word, because a rule is loaded
by agents on its paths and needs its scorecard row; on that word the file is written, the row
added and the surfaces regenerated.

**Then the sync**, as directed.

**commissions:** 4 — executing.

## decision · the weaponeering rule is landed; row 4, part 6: the model-and-effort correction is made (operator, 2026-10-10)

Operator g0, verbatim: 'land it, part 6, then git sync'.

**Landed.** `.gzkit/rules/weaponeering.md` at `0.1.0`, as drafted in Part 0 with the
operator's "land it" recorded in its marker; mirrored to `.claude/rules/` and
`src/gzkit/rules/` by `gz agent sync control-surfaces`; a `weaponeering.md` section in
`docs/governance/rule-version-history.md`; the Coverage Ledger row and a scorecard section
of six rows (98 to 98e), four Promotable and two Judgment, each scored at landing so the
third state is disclosed rather than accrued; the Summary roll-up recounted to the figures
`gz validate --advisory-scorecard` reported (Promotable 41, Judgment 77).

**Part 6 made.** `.gzkit/rules/model-selection.md` moved from `0.6.3` to `0.7.0`: claim 4
and § Subagent effort levels now describe the mechanism the harness has (effort on the agent
definition, `low` to `max`; the Agent tool call sets `model` only; a prompt-level line is
text), with the operator's allocation by echelon and role of 2026-10-05 added as an advisory
table; the Do Not list corrected from `light` to `low`. History entry added with the prior
marker verbatim; scorecard row 52b added, Promotable, and the ledger moved to `0.7.0`. This
discharges the defect insight of 2026-10-06 (scope `model-selection`), which row 2 carried.

**Then the sync**, as directed.

**commissions:** 4 — executing; the names remain.

## Disposition map

<!-- All six rows always present. State is `commissioned` or `not pursued` — there is no
     third state. The states below are the agent's draft; the operator rules each row at
     the close, and no row executes before the operator's go on that row. -->

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | commissioned | Proposed only, after briefs 15–20: engineering orders for the crew split (constraints, red, green) with the tasking event and the sortie matrix; the integrity-level axis beside lane (the consequence bands, witnessed by a scored-surface registry and an overlap floor), conditional on the operator lifting PROVISIONAL on the bands; combat assessment with a collateral owner and one assessment record; the maintenance record entry (one ledger event per chore run, replacing the PASS block as the run witness; findings are not events — ruled 2026-10-07). The identifier migration is row 5 and is timed to 1.0. **Reconciled 2026-10-08:** the tasking event and the collateral half of combat assessment are no longer proposed as new orders. The first is item 1 (the captain's brief) and the second item 3 (the scope-conformance report) of `ADR-pool.command-doctrine-internalization`, and the second was shipped and has lapsed (source entry *gzkit's own doctrine layer*, item 3). Each is a correction under its owning ADR, by the operator's correction-versus-enhancement doctrine. Still proposed as new: the crew split with the sortie matrix; the integrity-level axis; the maintenance record entry; an owner for munitions effectiveness. | Each passes the admission question — hard to reverse, surprising without this record, a real trade-off; each depends on the spine. The operator initiates, or not (IRON LAW). |
| 2 | GHI / direct fix | commissioned | (a) The four theatre-canon staleness items (insight 21:34:40: dead constitution link; stale non-goal; INV-007 vs ADR-0.0.36; lodestar README vs Boundary #5) — **repaired 2026-10-10 by the PRD amendment pass, row 4 part 4, not by issues**; what remains of (a) is and a fifth of the same class found 2026-10-07 (insight 2026-10-07T09:27:46Z: both published charters scope Gate 5 to the heavy lane against ADR-0.0.36). (b) Routing of the malformed `@covers` tags insight 21:30:15 recorded (525 findings on 2026-10-05; re-measured 2026-10-06, still present): one GHI for direct repair of foundation-era tags to REQ ids, or a parser rule for OBPI-id tags — the operator picks. (c) Nothing lints Markdown under `docs/`: `run_pymarkdown` has no caller, the `lint()` docstring names a linter that never runs, and pymarkdown is not installed or declared (insight 2026-10-06T10:49:46Z; found in passing by the research pass, verified by the session). Route: a direct fix of the docstring and the dead function, or a dependency decision under STDLIB-FIRST — the operator picks. **Added 2026-10-08:** (d) the command doctrine reaches nothing an agent loads each turn (sweep row S31; commissioned by decision *one binding doctrine*). (e) The campaign plan's § Amendments 2026-08-17 C sets five phrases in quotation marks; one misquotes its sentence and four occur in neither FAA order (insight 2026-10-07T23:46:09Z). (f) `docs/governance/GovZero/` is stale as a class against `AGENTS.md`, Gate 5 defined three ways among it (insight 2026-10-08, scope `theatre-canon:govzero-directory-staleness`); this absorbs the fifth item of (a). (g) The scope audit on completed receipts has lapsed since 2026-06-19 (insight 2026-10-08, scope `obpi-completion:scope-audit-lapsed`); its route is a correction under the ADR that owns completion, which the operator names. *Found 2026-10-09:* the owner is `OBPI-0.11.0-03` under `ADR-0.11.0`, which is Validated; by the operator's ruling of 2026-10-04 scope missed from a Validated ADR "enters the in-flight ADR as a repair assignment that cites the obligation it repairs" (source entry *the scorecard past its rule tables, and the scope audit's owner*). (h) The `gz-obpi-pipeline` skill cites a line of `pipeline_runtime.py` for a role map defined in `pipeline_dispatch.py` (insight 2026-10-09T00:23:00Z, scope `gz-obpi-pipeline:stale-role-map-pointer`). (i) The governance-subtraction track of 2026-06-08 stopped after one increment with no measurement and no owning artifact; its freeze text in `advisory-rules-audit.md` is stale and is still cited as live (insight 2026-10-09, scope `advisory-rules-audit:june-8-freeze-abandoned-after-first-increment`). What stands of the freeze is the operator's to rule before any repair. *Restated 2026-10-09:* the freeze, the campaign's ratification and the command doctrine, three acts of 2026-06-09 and 2026-06-10, disagree in seven places and were never reconciled; no edition of the campaign plan names the command doctrine or its pool ADR (decision *the work of 2026-06-08 to 2026-06-10 is discrepancy*; insight 2026-10-09, scope `governance-canon:june-8-to-10-three-acts-unreconciled`). **Executed 2026-10-09 on the operator's go for the lapses** (decision *the lapses, as addressed*): (g) filed as GHI #1181, and its first part (the completion command attaches the report) repaired on the operator's 'fix the first part under 1181' as `85d55a627` (2026-10-09), the issue staying open for refuse-or-record and the snapshot's base (decision *the first part of GHI #1181 is repaired*); the comparison of delivered work with Allowed Paths filed 2026-10-10 as GHI #1185 against the airlock exit, on the operator's 'ghi the restoration to enhance/strengthen the airlock, if able'; under (i) the scorecard's text is corrected, the five owed readings are done and the measurement is closed on the record; the coherence audit's lapse is not filed and waits on a campaign amendment. (j) Found by those readings: `data/security_surfaces.json` lists `src/gzkit/personas.py`, deleted 2026-05-12, and the persona parser's present file is matched by no glob (insight 2026-10-09, scope `security-surfaces:dead-literal-path`); filed 2026-10-09 as GHI #1182 on the operator's 'sounds like a bug'; repaired on the operator's 'fix it' and committed on the operator's 'commit it' as `de6f7e2a2` (2026-10-09), pushed by the sync of 2026-10-09 (`7959cf9f0`); GHI #1182 closed `fixed` through `ghi-close` the same day. (k) `uv run gz validate --sensitivity` exits 3 on main: two Draft briefs under `ADR-0.39.0` omit `sensitivity:` over an overlap with `src/gzkit/config.py` (insight 2026-10-09, scope `sensitivity-floor:adr-0.39.0-draft-briefs`); no go, and a brief edit is the operator's. | Defects by the PRIME DIRECTIVE, each tracked by an insight line today. Item 10's run has completed and no lock is held, so (b) is no longer another session's. Filing waits on the operator's go on this row. |
| 3 | chore | commissioned | Advise only: sort per-flight conformance checks off the interval board into `gz check`; package due interval tasks into named visits (the cited name is a scheduled work package, AC 120-16G § 6-1; "letter check" is the operator's own practice); two announcements for admission — the campaign plan's republish coming due on accumulated amendments, and the maintenance visit coming due from the board (ruled 2026-10-07). | The board's 35 overdue of 40 (measured 2026-10-05 and again 2026-10-07) is the signature of per-flight work on an interval board. Both announcements follow the ratified posture: they announce and gate nothing. The operator directs admission. **Ruled 2026-10-09:** 'let's do chores after rnd'; the board waits until this run is closed. |
| 4 | control surface, rule, doc, skill, hook | commissioned | One merged doctrine, built on the ratified command doctrine with this run's model merged in beneath its articles (ruled 2026-10-08, superseding a separate concept of operations), carrying the rhythm (the session tier as ruled 2026-07-18; two slower tiers, advisory until signalled); the campaign plan republished naming it and carrying the IOC waypoint as an amendment; a PRD amendment pass (the four stale items); the weaponeering rule text; the model-and-effort table in `model-selection.md`, describing the mechanism as the harness has it; (the small constitution draft of 2026-10-07 is withdrawn as to content by the one-doctrine ruling; what the constitution is, relative to the doctrine, is on the frontier); the ladder's name selection recorded at IEEE § Q-18, the candidates table and campaign § Amendments 2026-10-04 (3); the nomenclature terms, held here until the glossary home is named. **Added 2026-10-08:** the three terms position, role and crew; an amendment of Article 3's title so that an agent is crew, its allocation unchanged (both ruled 2026-10-08); the names commander and captain for the operator, who is not crew (ruled 2026-10-08); the terms force, doctrine, assets (ToE), abilities and campaign (ruled 2026-10-09). | **Go given 2026-10-10** ('go on row four'); the first part, the statement of command and the terms, drafted as candidate text in `doctrine-merge.md` Part 0. The deliverable of this run. **Corrected 2026-10-08.** The placement ruling is superseded by the one-doctrine ruling as far as it made a separate document. The source condition of 2026-10-07 ('b') is met: the five public texts are read (JP 3-60 in its 2018 edition, JP 3-30, JO 7110.65BB Appendix A, AC 121-22D, the IOC and FOC entries of the DAU Glossary); rows carried by DO-178C and MSG-3 keep their labels and drop § 11.17, objective counts and "letter check" (ruled 2026-10-08). The operator assembles the doctrine and directs each part (ruled 2026-10-08), so nothing in this row is drafted ahead of that direction. What the first item has to be is narrower than it reads: the philosophy is ratified, procedures and a scoring instrument exist (source entry *gzkit's own doctrine layer*), and its shape is the first question on the frontier. |
| 5 | one-shot refactoring | commissioned | Identifier migration ECP / EO / WP via `gz migrate-semver`, aliases before, timed to 1.0 (full operational capability). | Ruled 'A' (insight 22:03:25) "at IOC" when IOC named 1.0; the PRD-per-major rule puts it at the major boundary, and the 2026-10-07 IOC ruling moved the word, not the timing. Proposed as a program; the operator selects its route. |
| 6 | no action | not pursued | Do not build: an `issue-ato` CLI verb from the dialogue; an AST radar as a separate tool; "halt after N amnesiac turns"; a civil softening of the combat register. Withdrawn on 2026-10-07, each in its decision entry: assurance level as the lane criterion; the concept of operations as a new root above the constitution; chore findings as ledger events; a calendar cadence held by hand, and a flown sortie per operation; a shortened 1.0 set under the name IOC; a handoff replaced by "the account". | The airlock already parses; `BLOCKED` to the operator is the better escalation; the softening was withdrawn by the operator (insight 22:03:25). The 2026-10-07 items are each closed by a carried ruling or by the operator's selection that day: the lane rulings of 2026-09-23 and 2026-09-25; the 2026-06-14 root ruling; 'Runs yes, findings no'; 'Two slower tiers, signal-triggered'; 'Nothing — move the date instead' (2026-08-17); the 2026-07-18 rhythm. A rejected idea here is re-opened only by the operator. |

## Close

**Challenge restated.** Restated on purpose at the close, 2026-10-10, and accepted by the
operator in the same words ('the restatement stands, fund'):

gzkit's canon disagrees with itself. Three acts of June 2026 set a freeze, a campaign and a
command doctrine that never named one another, and five obligations canon says are met have
no position that owes them. The remedy is not a new document above the PRD but one merged
doctrine: the ten ratified articles, under a seven-line statement of command, in which every
obligation has a position, crew fill positions and command nothing, the commander is bound by
doctrine until changing it on the record, the campaign alone sets dates, and the orders that
bind gzkit's own construction are the last release's. The run defines this and builds none
of it.

*The restatement of 2026-10-07, superseded in full and kept as the record of what was
restated then:* the problem as a missing document, a concept of operations seated under a
small constitution and above the PRD and the campaign plan, with six things to settle: the
names and the ladder migrating at 1.0; integrity level as a second axis; a ledger record for
maintenance performed; a rhythm whose slower beats come due on a signal; a near waypoint, the
first sortie flown on someone else's substrate, ahead of a 1.0 from which nothing is removed.

**Travelling to row 4, open at sign-off and not closed by it:** item 14 (where mission
planning sits; how ordnance delivery and BDA divide; who owns munitions effectiveness); item
15 (what the constitution is relative to the merged doctrine; Article 3's body; an article
for relief of position; Article 6's sizing); item 13 (the names still contradicted or
unsourced); and the four put statements (what a policy is; the June pairs under the five
terms; article against policy; what "encourage" consists of). The operator rules each as the
doctrine is assembled.

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

15. The command doctrine. *First part ruled 2026-10-08* (decision *one binding doctrine*):
    the doctrine and the run's model are merged into one. Open under it, in order: what the
    constitution is relative to the merged doctrine; whether any agent role is called a
    pilot, against Article 3; how each part of the model traces to an article.
16. *Closed 2026-10-08 by ruling* (decision *two sessions are writing this record*): both
    write, the other agent on sources.
12. Opened 2026-10-07 by the reopen: the operator's review of the whole plan, from
    `docs/rnd/renewing-vows/review.md`. Sign-off is not put again before it.
14. The core model (decision *the core model, mapped from the two cycles*). *Shape ruled
    2026-10-08*: 'i want both', the six phases as the process and the eight roles as the
    crew; constraints are flown. Open under it, in order: where mission planning sits; how
    ordnance delivery and BDA divide; who owns the two unowned assessment outputs. The names
    wait on these.
13. Opened 2026-10-07 by the supplied texts, each for the operator's ruling in review: the
    name "battle rhythm" for tiers that come due on a signal; "watch" and "duty officer",
    which no text read carries; the letter-check and maintenance-planning-document mapping,
    which no text read carries; the prioritised target list as the name for an order that is
    absolute; the hazard-log row; "gates → objectives" against the standing constraint on the
    five gates; the artifact ladder's names, ruled 2026-10-05 (corrected 2026-10-08: "work package" and
    "task card" are verified as maintenance terms and "engineering order" as a term only, in
    the AC 120-16G source file; "change proposal" and "block" are in no landed source);
    and whether the Fielding rows stay labelled unverified or wait for the glossary.

Closed by fact on 2026-10-06: the effort mechanism (decision *effort rides on the agent
definition*).

**Frontier, computed again 2026-10-08 from the subject** (decision *re-entry on
2026-10-08*). The numbered list above is an input to it. The subject is the operator's:
"binding/bounding doctrine for gzkit to hold me and agents to account".

*Facts still owed by the agent, none of them a question for the operator:*

- Reads left partial that carry a row: the campaign plan's amendments, read by
  heading only (`advisory-rules-audit.md` and `state-doctrine.md` are read in full as of
  2026-10-09); `chore-class-system.md`'s unread body. Done since this list was written: the
  `gz-obpi-pipeline` skill and its `references/` (2026-10-08 and 2026-10-09); the scope
  audit's owner (2026-10-09).
- Texts unread that carry a row or a citation: Shihipar's explainer (cited by the
  model-and-effort decision and never landed); JP 5-0; AC 120-51; FAA Order 8900.1 and the
  International MRB/MTB Process Standard.
- *Done 2026-10-10* (decision *the two review documents are rewritten once*): `review.md`
  rewritten whole; `doctrine-merge.md` Parts II and III re-based. Item 12 is now open for
  the operator's review.

*Questions for the operator, one at a time, in this order:*

22. **Whether gzkit's design and construction stay subject to gzkit.** Opened by the
    operator 2026-10-09 (decision *the freeze is about assets*). It stands above every item
    below, because it decides what the doctrine binds. *Ruled 2026-10-10* (decision *gzkit
    is built with a released gzkit*): 'C'. Closed.

17. **What the doctrine is to be made of**, now that the philosophy is found ratified,
    procedures found written and a scoring instrument found live. Put 2026-10-08.
    *Closed 2026-10-08 by ruling* (decision *the frame reaches both ways*): no layer is
    chosen; 'the new framing has forwards and backwards influences'.
18. **How the six phases and eight roles relate to the five-stage pipeline** that canon
    already gives one work package. Put 2026-10-08: does the frame staff the five stages
    or cut them again? Not answered; it concerns the prior frame and waits on item 19
    (decision *the two frames shape each other*). Put again 2026-10-08, after items 19 to
    21 were ruled, as a statement for correction and not as a choice. *Ruled 2026-10-09*
    (decision *phases, stages and positions*): 'a good start'; it stands as a start.
19. **What an agent is in the merged doctrine**: Article 3's one automation beside one
    human, against the frame's many agents in positions with an echelon between. Opened
    and put 2026-10-08. It is asked before item 18. *Ruled 2026-10-08* (decision *position,
    role and crew*): a position is an obligation and a role to fulfil it; the crew is the
    actor within the role's bounds and auspices. Open under it, put 2026-10-08: Article 3's
    title against "crew" for an agent. *Ruled 2026-10-08*: 'a', the title is amended
    (decision *Article 3's title is to be amended*).
20. **Whether the operator holds positions under the same construct**: command and release
    as positions, each an obligation and a role, with the operator as the actor. Opened and
    put 2026-10-08. Asked before item 18, because the subject is a doctrine "to hold me
    and agents to account". *Ruled 2026-10-08*: both; the operator holds positions and is
    a prime decider (decision *the operator holds positions and is a prime decider*). The
    agent's seven-line assembly in that entry is put for correction. *Corrected by ruling
    2026-10-08* (decision *the operator is commander and captain*): commander and captain,
    not crew; the session the operator speaks to is crew.
21. **What position the orchestrating session holds**, now that it is ruled crew. Opened
    and put 2026-10-08 as a statement for correction. *Ruled 2026-10-08* (decision *the
    session's position stands as put*): the four statements are its guides and roles.
14. The core model's open seams, restated on today's read: how ordnance delivery and BDA
    divide; who owns munitions effectiveness (the collateral output had an owner and
    lapsed, so its question is a correction and not a seam); the two planning names.
15. Under the one-doctrine ruling: what the constitution is, relative to the doctrine; how
    each part of the model traces to an article. *Closed by canon, 2026-10-08:* whether an
    agent role is called a pilot. Article 3 is ratified ("The model is a crew resource, not
    a crew member"), so no agent role takes the name unless the operator amends the article.
    *Added 2026-10-08 from the trace:* the word "crew" for agent roles, against the same
    article; an article for relief of position; Article 6's sizing against the frame's.
13. The names the texts put in doubt, as listed above and as corrected in the nomenclature
    decision.
12. *Closed 2026-10-10:* the operator reviewed the rewritten `review.md` and
    `doctrine-merge.md` and signed off (decision *the restatement stands and the run is
    funded*).

*Put to the operator and not answered, as of 2026-10-09. None is ruled; each stays the
agent's draft until the operator speaks to it:*

- *Ruled 2026-10-10* (decision *the joined statement of command stands, in seven lines*):
  'it stands, add the seventh'. The three links are stated by the ruling.
- What a policy is, lines 1 to 3 (enforced with a witness, or a briefing that says so; a
  policy that is neither is not written). Lines 4 and 5 are withdrawn.
- The reading of the June pairs under the five terms: the doctrine carried a plan; "retires
  now" is the campaign's to time. That the freeze is about assets was confirmed.
- The third course under item 22, building gzkit with a released gzkit: "intriguing".
- Whether Article 3's body, and not only its title, gains the position and the role.
- Whether changing an article differs from changing a policy; what "encourage" consists of.

*For the operator's notice, not a question the run may settle:* four selections of
2026-10-07 (the integrity-level axis, chore runs as events, the two slower tiers, the IOC
waypoint) were booked in the rulings store by handoff `20261008T091331Z` while this record
holds them open to the review (decision *the run is reopened*). They stand unless the
operator changes them; the store's label does not bind the operator.

**Sign-off.** Operator g0, 2026-10-10, verbatim: 'the restatement stands, fund' — **fund**.
The set-aside of 2026-10-07 is lifted by this ruling. Diamond 1 is closed on the operator's
word with items 13, 14 and 15 and four statements travelling to row 4, as recorded in the
decision *the restatement stands and the run is funded*. The sign-off gives no row its go:
rows 1 to 5 each wait for the operator's go on that row, and no ledger event was emitted,
because the run's event types land with their producer.

## What this record does not license

No ADR, OBPI or chore is started by this run, funded or not. Rows 1–5 await the operator's go on each row;
row 6 names what is not built. No ledger event was emitted for the run. The licensed book is
cited, never copied; copyrighted standards land as citation records only. The operator's
identity is recorded as g0 and no personal address appears. The staging file in the prior
session's scratch directory is superseded by this record and carries no authority of its own.
