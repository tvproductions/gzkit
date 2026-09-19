Persona: `main-session` — craftsperson, governance-aware, whole-file reasoning, direct. This was a read-only decision exercise; no workflow or tests were executed and no files were changed.

1. **Do not solicit attestation using the earlier proof or reviews.** Pipeline § “The review window, the bound, and the exit” explicitly defines one input digest over the entire audited population plus the brief contract. An audited-source edit stales **every proof and imported review**, even when a different requirement motivated it. Finish all repairs, freeze the subject, execute proof for every obligation, refresh and replay the packet, and obtain/import the required independent approvals and finding closures against current proof. Record the reviewed revision and dirty-tree identity. Solicit attestation only when Stage-4 acceptance status reports ready. If the edit occurred after dispatch and before import, it also spends that round. **Unknown:** the actual changed paths, digest, round timing/count, proof IDs and acceptance status were not supplied.

2. **Do not dispatch another repair/review cycle merely because rounds remain.** The repeated-root exit is independent of the total-round bound. Pipeline § “When a round repeats the prior round’s ROOT” says to compare `Weakest point` with the preceding round; the same root appearing at another surface requires design escalation. In a real initiated workflow, record the block, present the open findings and changes made in each round, and give the operator one concrete design recommendation. **Unknown:** the actual findings and design alternatives are absent, so I cannot invent the recommendation’s substance.

3. **The successor’s silence does not release the gross-total constraint.** I followed `successor.md`’s `continues_from: predecessor.md`. The predecessor states: “all invoice totals remain gross until the reporting consumer is migrated” and says the operator has not withdrawn it. The successor only says to finish the display adjustment. The question independently specifies that the active requirement still requires gross totals. Handoff § RESUME requires following the predecessor chain, and its settled-ruling guidance preserves inherited rulings rather than treating omitted repetition as repeal. Governing context therefore includes both documents and the still-active requirement: a display adjustment does not authorize changing storage semantics. **Unknown:** no actual requirement document, migration evidence or Layer-2 state was supplied. The fixture’s reporting consumer still subtracts discount, which supports retaining the constraint within this exercise; I make no live migration-status claim.

4. **The run may not close with that finding open.** Pipeline quotes the older rule: “A round returning no critical and no high IN-SCOPE findings converges the gate.” It then explicitly supersedes it with the September 5 independent-closure ruling: “do not solicit completion attestation while any finding against the agreed OBPI requirements remains unresolved, or while a claimed fix has only the implementing agent’s confirmation.” The mapped finding requires repair, current proof and independent closure regardless of low severity. Preserve historical verdicts; a changed verdict string or filed GHI cannot discharge the obligation. **Unknown:** its finding identity, required repair, closure evidence and remaining round budget.

5. **Successful packet generation does not authorize completion attestation.** Pipeline § Normal Mode states that packet generation can exit 0 while `attestable: false` and `review_blockers` remain. That packet is review input. Supply it to the required independent reviewer, resolve and independently close mapped findings, import actual approvals, and refresh/replay the packet as required. Final readiness requires proof and review blockers to clear, with Stage-4 acceptance reporting ready. **Unknown:** the specific review blockers and whether any other requirements are unmet.

6. **Changing only the writer would double-subtract discounts in reporting; the write-shape check provides no sufficient coverage.** I read all four fixture files:
   - `writer.py` inserts `(gross, discount)` into `orders(total, discount)`.
   - `schema.sql` explicitly defines `total` as gross and discount as separately stored.
   - `nightly.sql` computes `SUM(total - discount)`.
   - `checks.py` asserts only `len((100, 10)) == 2`; it never calls the writer, reads storage or runs reporting.

   By static arithmetic, gross 100 with discount 10 currently stores `(100, 10)` and reports 90. A writer-only change to store `(90, 10)` would report 80. These are derived expectations, not observed test results.

   Before claiming correctness, resolve the requested storage change against the standing gross-until-migration requirement. If a net-storage migration is explicitly authorized, its coupled surfaces include the writer, schema semantics, reporting query, and compatibility/migration of existing gross rows. Merely changing reporting to sum `total` would misinterpret existing gross rows unless that transition is handled.

   Verification must invoke the real writer against the real schema, inspect stored values, and run the actual nightly query using expectations derived from the approved contract. Include a nonzero discount to expose double subtraction, zero discount as a legitimate positive case, and multiple rows to verify aggregation. For an authorized migration, also verify old/new data compatibility and the migration’s handling of existing rows. Demonstrate that these assertions fail for the writer-only double-subtraction defect, then pass for the coherent implementation. The literal tuple-length check would pass even if the writer were removed.

   **Unknown:** the database engine, production data/migration policy, other consumers, and allowed numeric/input boundaries. The supplied fixture does not establish them.

Actually read:

- `/Users/jeff/Documents/Code/gzkit/.gzkit/personas/main-session.md`
- `/tmp/gzkit-three-pillars-trial/B/questions.md`
- `/tmp/gzkit-three-pillars-trial/B/pipeline.md` — all 1,702 lines
- `/tmp/gzkit-three-pillars-trial/B/handoff.md` — all 514 lines
- `/tmp/gzkit-three-pillars-trial/B/predecessor.md`
- `/tmp/gzkit-three-pillars-trial/B/successor.md`
- `/tmp/gzkit-three-pillars-trial/B/fixture/writer.py`
- `/tmp/gzkit-three-pillars-trial/B/fixture/checks.py`
- `/tmp/gzkit-three-pillars-trial/B/fixture/schema.sql`
- `/tmp/gzkit-three-pillars-trial/B/fixture/nightly.sql`
