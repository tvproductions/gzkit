Persona: `main-session` — craftsperson, governance-aware, whole-file reasoning, direct.

This was a read-only decision exercise. I read both supplied skills completely; the initial combined output was truncated, so I reread the pipeline in successive complete ranges and the handoff separately. No workflow, tests, or modifications were executed.

1. **The earlier proof and reviews cannot support attestation after the audited-source edit.**

   Evidence: `pipeline.md`, “The review window, the bound, and the exit,” explicitly says currency uses one digest over the entire audited population plus the brief contract: “Any edit under those paths, however small and however unrelated, stales EVERY proof and EVERY imported review for this OBPI at once.” The motivating requirement does not narrow that invalidation.

   Finish all repairs first, rerun proof for every obligation, refresh and replay the packet, and obtain/import the required independent reviews and explicit finding closures against the current proof and digest. Record the reviewed revision and dirty-tree identity; freeze the audited population during review. Only solicit attestation once the Stage-4 acceptance status reports ready. Preserve earlier reviews as historical records.

   Unknowns: the actual changed files, current digest, outstanding finding IDs, and available review rounds. If the edit occurred after dispatch and before import, the supplied rule says it spends that round.

2. **Do not dispatch another repair/review cycle when the follow-up repeats the prior root at another surface.**

   Evidence: the pipeline independently stops on either exhausted rounds **or** a repeated root. It states: “If it names the same root cause at a different surface … stop, and put the design decision to the operator.” Remaining round allowance does not override this exit.

   In an actual authorized run, record the block, present the open findings and each round’s changes, and give one recommendation addressing the shared design cause. Await the operator’s design ruling.

   Unknowns: the specific shared cause, prior “Weakest point” evidence, and the appropriate design change. The question supplies the repeated-root condition; I have not verified a real review history.

3. **The successor’s silence does not release the gross-total constraint.**

   Evidence: `successor.md` expressly links `continues_from: predecessor.md`. The predecessor says: “all invoice totals remain gross until the reporting consumer is migrated” and that the operator has not withdrawn the constraint. The successor only says to finish the display adjustment. The question additionally establishes that the active requirement still requires gross totals until reporting migration.

   Governing context therefore includes the predecessor constraint, the active requirement, and the actual consumer contract. The handoff skill requires traversing the lineage, preserves settled rulings, and treats handoffs as advice rather than execution authorization. A display task cannot silently amend storage semantics. The fixture also shows the reporting consumer still subtracting the separately stored discount.

   Unknowns: any external migration evidence, later explicit ruling, or full active requirement artifact. None was supplied. Runtime completion/readiness claims would require their own verification; these files alone do not establish them.

4. **The run cannot close while that mapped finding remains open, regardless of low severity.**

   Evidence: the older statement says, “A round returning no critical and no high IN-SCOPE findings converges the gate.” The explicitly superseding September 5 ruling says not to solicit completion attestation “while any finding against the agreed OBPI requirements remains unresolved, or while a claimed fix has only the implementing agent’s confirmation.”

   Repair the affected obligation, execute current proof, and import independent closure linking the original finding, obligation, and current proof. Filing an issue, lowering severity, or writing a resolution paragraph cannot discharge it. Apply the repeated-root and round-bound exits if applicable.

   Unknowns: the finding’s concrete remedy, proof, and current closure records. The scenario supplies its in-scope mapped status.

5. **Successful packet generation does not authorize asking for completion attestation.**

   Evidence: the pipeline expressly permits generation to exit 0 with `attestable: false` and `review_blockers` when proof is ready but Step-4b closure remains pending. It says, “Do not confuse successful packet generation with permission to solicit attestation.”

   Use the packet as review input, obtain/import missing independent approval and closure, refresh the packet, and check the authoritative Stage-4 acceptance status. Both proof and review blockers must clear before presenting the completion-attestation request.

   Unknowns: the specific review blockers and whether they require missing review, repaired proof, or finding closure.

6. **Changing only the writer to store net totals breaks the supplied reporting calculation. A passing write-shape check is insufficient.**

   The inspected flow is:

   - `writer.py` stores `(gross, discount)` in `orders(total, discount)`.
   - `schema.sql` documents `total` as gross and discount as separately stored.
   - `nightly.sql` calculates recognized revenue with `SUM(total - discount)`.
   - `checks.py` merely asserts `len((100, 10)) == 2`; it invokes neither the writer nor a database or reporting query.

   By arithmetic, gross 100 with discount 10 currently yields recognized revenue 90. A writer-only change storing 90 while retaining discount 10 would make the existing query produce 80, subtracting the discount twice. This is a source-derived counterexample, not executed output.

   Before implementation, resolve the conflict with the still-active gross-until-migration requirement. If a net-storage migration is explicitly authorized, its coupled scope includes the reporting query, schema contract, and treatment of existing gross rows. Merely switching the query to `SUM(total)` would misinterpret unmigrated historical rows.

   Required verification includes assertion-level failing tests that exercise the real writer against the schema, inspect persisted values, and execute the actual reporting query. Cover discounted and undiscounted orders, multiple-row aggregation, and the chosen historical-data/cutover strategy. Expected revenue must derive independently from the agreed accounting behavior. Demonstrate that a discount-double-counting substitution fails the relevant assertion, then restore and observe green results. Refresh acceptance proof and reviews after audited changes.

   Unknowns: migration authorization, existing-data policy, supported discount bounds, rounding rules, and consumers beyond this fixture. The inspected fixture establishes the coupled reporting risk; it does not establish production-wide completeness.

Files actually read:

- `/Users/jeff/Documents/Code/gzkit/.gzkit/personas/main-session.md`
- `/tmp/gzkit-three-pillars-trial/A/questions.md`
- `/tmp/gzkit-three-pillars-trial/A/pipeline.md`
- `/tmp/gzkit-three-pillars-trial/A/handoff.md`
- `/tmp/gzkit-three-pillars-trial/A/predecessor.md`
- `/tmp/gzkit-three-pillars-trial/A/successor.md`
- `/tmp/gzkit-three-pillars-trial/A/fixture/writer.py`
- `/tmp/gzkit-three-pillars-trial/A/fixture/checks.py`
- `/tmp/gzkit-three-pillars-trial/A/fixture/schema.sql`
- `/tmp/gzkit-three-pillars-trial/A/fixture/nightly.sql`
