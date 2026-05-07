<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Token-Block Doctrine — Lock-Release Coupled to Handoff Register Entry

**Source ADR:** [ADR-0.0.41 — Token-Block Lock Discipline](../design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md)

**Companion rule:** `.gzkit/rules/token-block-discipline.md` (authored under OBPI-0.0.41-01)

**Purpose:** Establish the canonical reference for gzkit's lock-and-handoff primitive, name its direct intellectual debt to nineteenth-century railway absolute-block working, and give every agent and operator a vocabulary that resists drift.

---

## Acknowledgement — Direct Importation, Not Coincidence

The doctrine that governs OBPI locks and handoffs in gzkit is **not coincidentally similar** to railway absolute-block working — it is **deliberately imported** from it. The vocabulary (*token*, *register entry*, *traversal*, *abandonment*, *reaping*), the structural invariants (mutual exclusion via physical instrument, audit-coupling via paired register entry, fail-closed surrender), and the operator override semantics (`--abandon` as a deliberate analogue of lost-token procedures) are taken from the railway corpus because the railway corpus solved the problem first, solved it under conditions of life-or-death consequence, and refined the solution across roughly a century of operational practice and accident-driven regulation.

This document gives credit where it is owed. Agents and operators reading the gzkit canon should know that **token-block discipline is a railway concept** before it is a software concept; that it was forged by signal engineers, accident inspectors, and rule-book authors whose names appear below; and that the gzkit implementation is a small, faithful reading of their work projected onto a software-governance problem. The smallest-vibing-surface framing of `AGENTS.md § Anti-vibing mantra` is itself a re-statement of why railway operating rules survive: they removed the room for *"I think I remember what happened in that section"* and replaced it with a bound book and a physical token.

---

## Brief History — How Railways Arrived at the Token-Block Invariant

The British railway industry, between roughly 1840 and 1900, developed absolute-block working as a structural answer to the problem of two trains occupying the same single-track section. The progression is well-documented in standard railway-safety historiography (see *References*); a short summary establishes the canonical lineage.

### Stage 1: Time-interval working (failed)

Early UK railways operated on time-interval rules: a train was permitted to follow a preceding train after a fixed interval (typically five minutes). The discipline depended on assumed-correct timekeeping, no obstruction in the section, and no train failure. All three assumptions failed regularly, with predictable consequences. Time-interval working was the railway equivalent of *"the agent will pause and write a handoff when appropriate"* — an unfunded judgment call whose cost was paid in collisions.

### Stage 2: The train staff (1840s onward)

The earliest mechanical answer was the **train staff** — a wooden or metal baton, one per single-track section, in the personal possession of the driver. No staff, no entry to the section. Two staffs cannot exist in one section. The staff is the authority. Mutual exclusion was now structural, not procedural. The staff system worked, but rigidly: only one direction of traffic at a time was possible per section, since the staff had to physically travel with each train.

### Stage 3: Staff and ticket (mid-19th century)

To allow multiple trains in one direction, the **staff and ticket** system added paper tickets issued at the signal box. The driver received a ticket but did not take the staff (which remained at the box) unless their train was the last in the sequence in that direction. This relaxed the rigid one-train-at-a-time constraint without sacrificing exclusion, but it depended heavily on signal-box discipline — a misissued ticket reproduced the time-interval failure mode.

### Stage 4: Tyer's Electric Train Tablet (1878)

**Edward Tyer** (1830–1912), the British signal engineer, patented the electric train tablet in 1878 — an interlocked instrument at each end of a section that issued *tablets* (metal discs) only when both ends agreed via a galvanic-circuit interlock. The interlock physically prevented the issue of a second tablet anywhere in the system while one was outstanding. The tablet was the authority; the instruments were the signalmen's structural insurance against their own errors. Tyer's tablet is the canonical ancestor of every modern token-block instrument.

### Stage 5: Webb–Thompson Electric Train Staff (1888)

**F. W. Webb**, Chief Mechanical Engineer of the London and North Western Railway at Crewe, working with **Alfred Thompson**, refined the principle into the **Electric Train Staff** (1888). Where Tyer's instrument issued discrete tablets per traversal, the Webb–Thompson instrument issued metal staffs from a magazine and re-absorbed them at the receiving end. The instruments were heavier, more robust to abuse, and became the dominant single-line token-block instrument on British and Commonwealth railways.

### Stage 6: Armagh and the regulatory floor (1889)

The **Armagh disaster** of 12 June 1889 — a runaway portion of a divided passenger excursion train colliding with a following train, eighty fatalities — drove Parliament to the **Regulation of Railways Act 1889**. The Act mandated absolute-block working, continuous brakes, and interlocked points and signals on UK passenger lines. Block-token discipline ceased to be a competitive advantage and became a regulatory floor. From that point onward, the token-and-register-entry pairing was not a railway company's choice; it was the state's price of admission to passenger operation.

### Stage 7: Tyer's No. 6 and persistence (1912 onward)

The **Tyer's No. 6 token instrument** (1912) and its successors institutionalised the discipline for the rest of the steam era and into the diesel age. Heritage railways and some operational rural lines continue to use Tyer's-pattern instruments today; the British rule book (currently GE/RT8000 and its predecessors) preserves the procedural canon — including specific lost-token procedures, the *"T"* form for written authorities when the token system fails, and the train register book that accompanies every signal box.

The mechanism we are importing into gzkit is therefore not a curiosity. It is the load-bearing primitive of nineteenth- and twentieth-century railway safety, refined under regulatory and operational pressure by named engineers across roughly seventy years.

---

## The Invariant, Stated Plainly

> **A token cannot be surrendered without a register entry.**

This is the binding form of the doctrine. Every other rule in this document and in `.gzkit/rules/token-block-discipline.md` derives from it.

The dual phrasing — *the register entry is required at every signal box, not only at the train's terminal station* — names the per-traversal granularity that defeats the most common attempts to weaken the discipline. A single OBPI may span multiple lock claim/release cycles across sessions, and intermediate handovers without register entries lose intent at exactly the boundaries the doctrine exists to protect.

---

## Mapping — Railway to gzkit

| Railway primitive | gzkit primitive |
|---|---|
| Token (tablet, staff, key token) | OBPI lock instrument |
| Token issue at signal box | `obpi_lock_claimed` ledger event |
| Train register entry on issue | First handoff CREATE following claim (or chained from prior session) |
| Token surrender at exit signal box | `obpi_lock_released` ledger event |
| Train register entry on surrender | Handoff CREATE before lock release — fail-closed |
| Bound book (the train register itself) | `.gzkit/ledger.jsonl` (append-only) |
| Section / block | An OBPI under active implementation |
| Two trains, two signal boxes | Two agents, lock-claim and lock-release boundaries |
| Lost-token procedure | `--abandon <category>:<reason>` with auditable category enum |
| Reaping a forgotten / abandoned token | `lock_manager.py:reap_expired_locks` emitting an `abandoned_by_reaper` register entry |
| "T" written-authority form | (no current gzkit analogue — would correspond to a manual ledger amendment under operator attestation, intentionally not provided) |
| Rule Book (GE/RT8000) | AGENTS.md + `.gzkit/rules/**` |
| Signal-engineering interlock (galvanic circuit between instruments) | The fail-closed precondition in `obpi_lock_release_cmd` |
| Railway Inspector's accident report | `gz validate --lock-handoff-coupling` ledger replay |

The mapping is intentionally precise. Where the railway corpus provides a primitive we have not imported (the *"T"* form), the absence is deliberate — the gzkit doctrine refuses to provide the manual-amendment escape hatch that, in railway practice, depends on a signed authority and signalman-to-signalman phone confirmation that has no software-governance analogue worth the abuse surface.

---

## Why the Importation Works

Software governance and single-line railway operation share three structural properties that make the railway invariant a faithful import rather than a forced metaphor:

1. **Exclusive authority is the actual problem.** Two trains in one block kill people; two agents working an OBPI without coordination corrupt the artifact graph. In both cases the cost of getting it wrong is catastrophic, the cost of preventing it is small, and the prevention mechanism is the same shape: a physical (or logical) instrument that exists in exactly one copy and travels with the work.
2. **Memory is structurally unreliable.** Drivers forget, operators forget, agents pattern-match from training memory and produce confident-but-wrong narratives. The token + register entry pair removes the room for memory-as-evidence by binding the authority transfer to a written artifact that the next holder of the authority must produce before taking possession.
3. **The audit trail is itself a primitive, not a derivative.** A railway train register is not a derived view of train movements — it *is* the canonical record of train movements. Likewise the gzkit ledger plus its register entries is the canonical record of OBPI traversals, not a Layer-3 reconstruction of activity logs. The state-doctrine Layer-2 status of the ledger is the same status the railway rule book gives the train register.

---

## Extension Surfaces — Deliberate Non-Imports (For Now)

Real railway operation layers four primitives at the section boundary: token-block (section-occupancy), signals (movement-authority), interlocked points (routing), and continuous brakes (movement-validity). This doctrine imports the first deliberately and partially. The other three are *extension surfaces* — scope statements, not strain on the existing doctrine. Naming them keeps future doctrine work legible: it will join gzkit's existing railway lineage rather than appearing as a fresh metaphor.

- **Signal primitive — movement-authority within an active lock.** Future work that wants attestation gates, intermediate review, or staged advancement *while a lock is held* would borrow the signal — joining the semaphore lineage documented in *Sibling descendants* below. The token grants section-occupancy; the signal would grant intra-section advancement. (Closest current analogue: Gate 2 / Gate 4 attestation milestones within an OBPI's lifecycle. A richer importation would make these structurally signal-shaped rather than checklist-shaped.)
- **Interlocked-points primitive — routing.** Future work that needs to choose between competing implementation paths under coordination would borrow the interlock-between-routes shape. (No current gzkit need.)
- **Brake-continuity primitive — movement-validity.** Future work on detecting structural breakage *during* held authority would borrow the continuous-brake check. (Closest current analogue: `gz check` invoked on every commit; a richer version would be live-monitored throughout an active lock, not only at OBPI completion.)

The token primitive imported here stands on its own. The time-bound discipline of railway operation (failed-train-in-section procedures, lost-token recovery, reaping protocols) is *part of* the token primitive itself in railway practice and is therefore part of this doctrine, specified in OBPI-0.0.41-01 (TTL canon, reaping cadence, attestation requirements for reaping). Atomic interlock between paired instruments — the load-bearing safety property of Tyer's 1878 patent — is *part of* the token primitive itself and is specified in OBPI-0.0.41-02 (exclusive-creation in the claim sequence). Where the gzkit implementation is incomplete relative to the railway primitive being imported, the gap is named in the ADR Checklist as work to do, not here as analogy strain.

## What the Importation Does Not Claim

Three honest negative claims, since the credit-where-credit-is-due posture cuts both ways:

- **gzkit is not running trains.** The consequence model is artifact corruption, not loss of life. The railway invariants are imported because their structural shape is correct; the seriousness with which the railway corpus enforces them (statutory law, accident inquiries, criminal liability for rule violations) is not imported and would be disproportionate.
- **The railway corpus is not the only source.** Any rigorous concurrent-systems treatment of mutual exclusion with audit (database transaction logs, distributed systems consensus protocols with operation logs) reaches structurally similar conclusions. The railway corpus is the canonical reference because it is *operationally* refined — the rules survived contact with humans under load, regulatory scrutiny, and a century of post-incident review — not because it is uniquely correct in the abstract.
- **The mapping is not a costume.** Naming an enforcement primitive after a railway primitive does not make the enforcement work; the work is done by the fail-closed CLI verb, the ledger payload coupling, and the validator. The vocabulary serves comprehension and resistance to drift, not enforcement.

---

## References

The following works are the canonical English-language sources for the railway material in this doctrine. They are listed for the reader who wants to verify, deepen, or argue with the importation; the gzkit canon does not require reading them, but operators and agents who do will see the doctrine more clearly.

### Primary historical and engineering references

- **L. T. C. Rolt**, *Red for Danger: A History of Railway Accidents and Railway Safety*. First published 1955; multiple subsequent editions (David & Charles; Sutton Publishing; The History Press). The canonical UK railway-safety history. The chapters on early single-line working, Tyer's tablet, and the Armagh disaster are the standard reference; a single re-read makes the gzkit importation feel obvious rather than novel.
- **Adrian Vaughan**, *Obstruction Danger: Significant British Railway Accidents 1890–1986*. Patrick Stephens, 1989 (later editions extant). Case-study collection; the block-token failure modes documented across these cases are the empirical basis for why the discipline must be fail-closed, not advisory.
- **O. S. Nock**, *Historic Railway Disasters*. Ian Allan, 1966. A working historian's overview; complementary to Rolt for the operating-rule perspective.

### Sibling-lineage references

- **Edsger W. Dijkstra**, *Cooperating Sequential Processes* (EWD-123, 1965; published in *Programming Languages*, F. Genuys ed., Academic Press, 1968). The original semaphore paper; railway-signal etymology made explicit.
- **IEEE Standard 802.5** (Token Ring Access Method, IBM-led, 1984–1985 onward). The token-passing network standard; the canonical computing borrowing of the *token* primitive at the network-arbitration layer.

### Primary engineering / patent material

- **Edward Tyer**, electric train tablet patents and instrument documentation (UK, from 1878). Tyer's instruments are well-documented in railway-engineering archives; the British Patent Office record and the National Railway Museum (York) archives are the primary-source homes.
- **F. W. Webb and Alfred Thompson**, Electric Train Staff (LNWR, Crewe Works, 1888). The Webb–Thompson instrument is documented in LNWR engineering records, Railway Magazine contemporaneous coverage, and standard signal-engineering textbooks of the period.

### Regulatory / operational

- **Regulation of Railways Act 1889** (United Kingdom). The statute that mandated absolute-block working, continuous brakes, and interlocked points and signals on passenger lines. Followed the Armagh disaster of 12 June 1889. Available via UK legislation archives.
- **Rule Book GE/RT8000** (Rail Safety and Standards Board, current editions). The operational successor to the historical UK Rule Books; the modern home of the train-register and lost-token procedures whose structural shape gzkit imports. Predecessor editions (the British Railways Rule Book, the various pre-grouping company rule books) are available in railway-historical archives.

### Sibling descendants — semaphores and token-passing networks

The gzkit token-block discipline is not the first or only computing primitive borrowed from the railway corpus. Two sibling lineages descend from the same source, and naming them precisely situates this doctrine within the broader family of railway-derived concurrency-control work.

**Semaphores (Dijkstra, 1965).** Edsger W. Dijkstra coined the computing term *semaphore* in *Cooperating Sequential Processes* (1965; the EWD-123 manuscript, subsequently published in *Programming Languages*, F. Genuys ed., Academic Press, 1968) and explicitly invoked the railway-signal mental model. Dijkstra borrowed from the railway **signal** — the arm-or-light at the section boundary that grants *movement authority*. The P and V operations on a semaphore modelled "wait until the signal is clear, then proceed." Semaphores are the canonical computing answer for movement-authority across concurrent processes.

**Token-passing networks (IBM Token Ring, 1984–1985; IEEE 802.5).** The Token Ring local-area-network protocol, and the broader family of token-passing arbitration protocols (FDDI, ARCNET in some configurations), borrowed from the railway **token** — the physical instrument that grants *section-occupancy authority*. Only the host holding the circulating token could transmit; the token's exclusion property prevented frame collisions. This is the same railway primitive gzkit imports, projected onto a different problem (network arbitration) at a different abstraction layer.

**gzkit's borrowing in this family.** Token-block discipline (this doctrine) borrows the **token**, not the signal — the same primitive as Token Ring, at a different layer (governance artifacts rather than network frames). It is *not* redundant with semaphores in computing: the two address different concurrency-control aspects.

| Primitive | Railway source | Computing lineage | Aspect |
|---|---|---|---|
| Signal (arm / light at section boundary) | Movement authority — "you may proceed" | Dijkstra's semaphore (1965) | Permission to advance |
| Token (tablet / staff / key token) | Section-occupancy authority — "only you may occupy this section" | Token Ring (1984), gzkit token-block (this doctrine) | Mutual exclusion with audit |
| Train register entry | Audit-coupling — written record of every issue and surrender | (no broad computing analogue; gzkit imports it directly into the ledger) | Replayable history of authority transfers |

In railway operating practice these primitives are *layered*: a driver holding a token still needs the home signal clear to enter the section. The token grants exclusion; the signal grants permission. Future gzkit work that wants a movement-authority equivalent (for example, attestation gates *within* an active lock) would borrow the signal primitive, joining the semaphore lineage while remaining compatible with this doctrine's token primitive — exactly as railway operation layers the two.

The third entry in the table — the train register — is the one gzkit imports most directly. Most computing concurrency primitives borrow the *exclusion* property and leave the audit-coupling implicit (the runtime knows who holds the lock; the program does not produce a written record). Railway practice never made that simplification: every token transfer is recorded in a bound book at every signal box, by rule. gzkit takes that posture literally — the ledger plus its register entries is the canonical audit trail, not a derivative of it.

### Acknowledgement of further indirect debt

The treatment of the audit trail as a Layer-2 primitive in gzkit's state doctrine (`docs/governance/state-doctrine.md`) is consistent with — and informally informed by — the database-systems and distributed-systems treatment of operation logs (write-ahead logging, replicated state machines, transaction-log-as-canonical-state). The railway analogue is foregrounded here because it is the more accessible mental model for a governance audience and because the operational practice is what gives the discipline its weight; the database-systems literature is a complementary, not contradictory, source.

---

## Cross-references within gzkit

- [ADR-0.0.41 — Token-Block Lock Discipline](../design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/ADR-0.0.41-token-block-lock-discipline.md) — the source decision record.
- [`docs/governance/state-doctrine.md`](state-doctrine.md) — Layer-2 source-of-truth doctrine; this doctrine extends Layer-2 with audit-coupling.
- [ADR-0.0.9 — State Doctrine and Source-of-Truth Hierarchy](../design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md) — parent doctrine.
- `.gzkit/rules/token-block-discipline.md` — the binding-bullets rule file (authored under OBPI-0.0.41-01); this document is its pedagogical companion.
- `.gzkit/skills/gz-session-handoff/SKILL.md` — the agent-facing skill whose CREATE workflow produces the register entry; trigger semantics rewritten under OBPI-0.0.41-05.
- [GHI #410](https://github.com/tvproductions/gzkit/issues/410) — the surfacing observation; closed `superseded` against ADR-0.0.41.
- [GHI #326](https://github.com/tvproductions/gzkit/issues/326) — the SessionStart auto-load (read-side counterpart whose mechanical-floor presence exposed the asymmetry this doctrine closes).
