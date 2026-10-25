<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-8 specification — the in-flight work disposed

**2026-10-25. Status: DRAFT; research recorded, questions not yet put.** Operator: **g0**. Repair order RO-8 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders). The operator rules; the session drafts.

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

## Open questions, in the order they will be put

1. What "frozen" means for ADR-0.35.0's nine unlanded briefs and one repudiated brief.
2. Whether briefs 17 and 20 are ever attested.
3. Where "carried into the catalog" lives.
4. The ADR-0.34.0 conflict, with the repudiated OBPI-0.0.24-04, OBPI-0.0.26-02 and OBPI-0.35.0-09.
5. Brief 19's Requirement 8.
6. What the handback says about the Movement boxes.
7. The kept-or-reverted list's form and drafter.
