<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-8 specification — the in-flight work disposed

**2026-10-25. Status: specified; every open question ruled the same day.** Operator: **g0**. Repair order RO-8 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders). The operator rules; the session drafts.

## Already ruled in the record

- R4 (2026-10-17): *"R4 ADR-0.35.0 frozen, no further OBPI completions"*; § What is suspended: *"No OBPI is initiated or completed under safe mode"*.
- § What does not change: *"TOPMOST remains `ADR-0.35.0` until RO-8 disposes of it; the drydock works inside the campaign, which sequences what follows."*
- § Exit 9: *"The handback amendment is ratified: every drydock commit listed, kept or reverted; this passage log carried; the suspended rules restored. Civil rule resumes on the ratification."* Updating the campaign plan is civil rule's work (operator, 2026-10-25).
- Requirements model: *"Legacy ADR checklists and OBPIs stay as frozen history behind the aliases"* (line 138); *"nothing legacy is backfilled"* (line 184); ADR-0.35.0 items 1–14 map to family C (6 and 11 to G), 15–20 to R3 (line 302).
- RO-4 ruling 6: *"legacy ADR work is not a member and is not backfilled."* RO-11: pool entries are intentions, pulled on demand.

## Current state (research of 2026-10-25)

- **ADR-0.35.0**: Accepted, 11 of 20, closeout blocked. Attested 01–08, 10, 14, 15 (15 flagged "completion receipt was captured from a dirty worktree"; 03's body still says attestation pending while the ledger says attested). 09 repudiated (2026-10-01). 11–13 and 16–20 pending; 11 and 12 carry open GHIs #922 and #921. No OBPI lock held.
- **Briefs 17 and 20**: the work landed in pilot acts and the 2026-10-17 disclosures were ruled; the ledger still shows both pending (*"Attestation of 17 and 20 still awaits the operator's words"*; *"the attestation completing OBPI-0.35.0-20 must name S2-080"*).
- **Brief 19, Requirement 8**: still an open `[ ]` REQ in the brief; its supersession by the never-evict ruling is recorded only in the contract.
- **Campaign Movements A–F**: still read as before the drydock (TOPMOST ADR-0.35.0, then ascending ADR order: 0.36.0, 0.37.0, 0.39.0).
- **Kept-or-reverted list**: not yet written.
- **Other partial state**: ADR-0.0.24 (3 of 4) and ADR-0.0.26 (4 of 5) each hold a repudiated OBPI; ADR-0.34.0 holds 4 of 5.

## The ADR-0.34.0 ordering conflict

On 2026-10-01 the operator repudiated OBPI-0.34.0-02 (its REQ-02-05 had no red receipt before completion, GHI #849), leaving ADR-0.34.0 at 4 of 5 although it shipped as v0.34.0 and reads `Validated`. The campaign's rule "honor the lowest feature ADR with unlanded work" then puts 0.34.0 ahead of TOPMOST 0.35.0, while the same amendment holds *"A Validated ADR is never reopened"*. Every handoff since 2026-10-02 carries the re-completion of OBPI-0.34.0-02 as unruled.

## Rulings of 2026-10-25

1. **ADR-0.35.0's unfinished work is absorbed, not jettisoned** (operator, verbatim: *"well, when we leave drydock, the new system will be in place, so it won't be possible to do them the old way, they need to be absorbed into the new system, but not jettisoned. in fact they will form that next 0.35.0 release package (the sum of that adr's obpis). When we get to the requirements and release packages, and everything related, we need to review it VERY CAREFULLY. For now, this is me agreeing with "A" above."*). Each unlanded brief's REQs become catalog REQs under the outcome the requirements model maps them to (items 1–14 to C, 6 and 11 to G, 15–20 to R3); the brief is withdrawn as superseded through `gz obpi withdraw`, naming where its REQs went; the work is finished as work packages, and together they form the 0.35.0 Release Package. Consequences, settled by this ruling: briefs 17 and 20, whose work landed in pilot acts, are not attested as OBPIs; their obligations, S2-080 included for 20, are carried to the outcome's Gate 5. The carry lives in the catalog.

**For the careful review the operator called for:** RO-4 ruling 6 holds that *"legacy ADR work is not a member and is not backfilled"*, while this ruling makes the 0.35.0 Release Package *"the sum of that adr's obpis"*, which includes the eleven OBPIs already attested. The two are reconciled in that review, not here. *Reconciled 2026-10-29* (operator, verbatim: *"A"*; the contract's § Rulings of 2026-10-29): the 0.35.0 Release Package's members are the outcomes of all twenty items; the eleven attested items enter the catalog with their attestations carried as legacy evidence through the alias layer, not re-attested; `release_recorded` names the new work packages and the legacy OBPI completions; RO-4 ruling 6's no-backfill rule stands with 0.35.0 as its one exception.

2. **The repudiated OBPIs are absorbed the same way** (selection *"A"*): OBPI-0.34.0-02, OBPI-0.0.24-04, OBPI-0.0.26-02 and OBPI-0.35.0-09 have their REQs carried to catalog REQs, their proof recorded fresh under the new system (0.34.0-02's missing red receipt for REQ-02-05 becomes a REQ proof, not an OBPI re-completion), and each is withdrawn as superseded. The ADR-0.34.0 ordering conflict dissolves: work selection no longer runs by ADR order, and no Validated ADR is reopened.
3. **Brief 19's Requirement 8 is not carried, settled by ruling 1:** REQ-0.35.0-19-08 is superseded by the 2026-10-18 never-evict ruling (landed under RO-5), and brief 19's withdrawal names that supersession; the frozen brief is not hand-edited.
4. **The handback does not rewrite the Movement boxes, settled by the operator's ruling** that updating the campaign plan is civil rule's work: the handback names TOPMOST ADR-0.35.0 as disposed by rulings 1 and 2, and points civil rule at the re-sequencing.
5. **The kept-or-reverted list becomes the compliance register** (operator: *"yes, that is fine, it works well; you've captured the scope well"*): the contract's § Punch list, one section per repair order, each item with its disposition and authority, closed through Gate 5 after restoration; exit condition 9 amended to match.

## Acts (for the contractor)

**Amended 2026-10-30** (operator, verbatim: *"A"*, twice; the contract's § Rulings of 2026-10-30): the catalog is empty at the handback. In the drydock RO-8 freezes ADR-0.35.0, books the disposition plan of acts 1 to 3 and runs act 4; acts 1, 2 and 3 run in that order at the transfer of custody, on the operator's word, as the first work under civil rule.

The contractor stops and waits on every structural question.

1. **Carry.** For each of ADR-0.35.0's nine unlanded briefs and the four repudiated OBPIs, the REQs written as catalog REQs under the outcome the requirements model maps them to, with fresh proof where the work already landed (briefs 17 and 20; 0.34.0-02's red receipt).
2. **Withdraw.** Each brief withdrawn as superseded through `gz obpi withdraw`, naming where its REQs went (brief 19 also naming the never-evict supersession).
3. **Release Package.** The 0.35.0 Release Package drafted with the outcomes of all twenty items as members, the eleven attested items carrying their attestations as legacy evidence (reconciled with RO-4 ruling 6 on 2026-10-29).
4. **Handback.** The compliance register closed (ruling 5), TOPMOST named as disposed (ruling 4).

## Witness

The handback amendment: the compliance register with every RO-8 line cleared, and `gz adr status ADR-0.35.0` showing no pending brief.
