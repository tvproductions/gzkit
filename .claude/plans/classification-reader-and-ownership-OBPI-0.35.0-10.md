# Plan — OBPI-0.35.0-10-classification-reader-and-ownership

Brief: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md`
Parent: ADR-0.35.0-canon-entry-corpus-landing, Decision item 9, checklist item 10, BI-04. Lane: Heavy.

**Written 2026-10-05, after the implementation.** The code landed on main at commit 4893b7321
on 2026-10-03 under the operator-ruled single-session trial, which skipped plan mode. This file
records what was built and plans the stages that remain. It is not a pre-implementation plan
and does not claim to be one. Entry point: the pipeline at its recorded resume point, verify.

## Context

The classification field of a corpus entry was schema-required, part of the baseline identity fingerprint,
and read by nothing. The binding copy of the same concept was the hand-maintained scorecard.
Decision item 9 gives the field one reader: bullet retention resolves a row's class from the
corpus where the corpus owns the section, and from the scorecard elsewhere. The brief's
2026-09-29 amendment (GHI #939, operator-ruled) adds source-aware retention: a row attributed
to a skill or ADR source is retained against that source's text.

State on 2026-10-05, measured: the OBPI is in progress, not complete, not attested. No lock
is held (reaped 2026-10-05T18:15Z). The acceptance record holds ten proofs and no reviews;
every proof is stale on both contract and inputs. Precomplete exits 3 on lock, ARB receipts,
plan audit and adversarial validation. Two commits have touched the brief's surfaces since
the trial: 4893b7321 itself and c9cb95cb2.

## Files

Already changed by 4893b7321, all inside the brief's allowlist:

- `src/gzkit/governance/trust_audits/bullet_retention.py` — the resolver, the owned-mapping fence, the Ambiguous fence, the source-aware retention arm.
- `tests/governance/test_bullet_retention.py` — covering tests for REQ-01 to REQ-05, REQ-08, REQ-09.
- `src/gzkit/content/models/corpus.py` — docstring only.
- `features/classification_ownership.feature`, `features/steps/classification_ownership_steps.py` — Gate 4 scenarios.
- `docs/user/manpages/validate.md`, `docs/governance/advisory-rules-audit.md` — the narrowed authority, the source-aware scope, and a source attribution in the Notes column of every scorecard row.

Still to change:

- The brief: the REQ-0.35.0-10-10 witness clause (operator decision 2 below), a Change Log under Evidence, and the evidence sections at completion.
- `docs/governance/advisory-rules-audit.md` — only if operator decisions 3 or 4 change a mapping or a class.
- `.gzkit/corpus/AGENTS.md.jsonl`, `.gzkit/renditions/AGENTS.md/`, `AGENTS.md` — only if operator decision 4 reclassifies corpus entries, and then only through governed retire, remember and land. Not edited by hand.

No new source or test file is planned. A finding from review that needs code is repaired
inside the files above.

## Operator decisions this plan depends on

Each is put to the operator as one bounded choice before the step that needs it.

1. **ADR text.** The parent ADR's Decision item 9 and checklist item 10 do not mention the
   retention scope the brief gained on 2026-09-29. Decide whether the ADR is amended to carry
   it before the work proceeds.
2. **REQ-0.35.0-10-10 witness clause.** It reads "citing both paths". The support resolver
   takes the word after "citing" as the path, so the proof returns unproven. Proposed repair:
   cite `docs/user/manpages/validate.md` in the clause; the scorecard half is already
   witnessed by REQ-0.35.0-10-06. This changes the contract, so it needs a ruling.
3. **Mapping review.** The brief says the row-to-entry mapping "is reviewed during
   implementation planning". The trial mapped 31 scorecard rows to corpus entries by hand,
   made the source attribution mandatory on every row once a project declares ownership, and
   attributed two rows to the scorecard itself. None of it has been reviewed. The mapping is
   put to the operator as a before and after table.
4. **Six disagreeing rows.** Five owned rows are Mechanical in the scorecard and Judgment in
   the corpus, so they are no longer retention-enforced; one is the reverse and is newly
   enforced. Decide: reclassify the corpus entries by attested retire and remember, rescore
   the scorecard rows, or leave the advisory standing.

## Steps

### Task 1 — Enter the pipeline (Stage 1)

1. Plan audit to a pass on this file.
2. Claim the lock for the OBPI.
3. Launch the pipeline from verify. The launch rewrites the two stale pipeline markers, which
   is what clears the CI Preflight failure.
4. Reuse the acceptance record; do not re-initialize the obligation roster.
5. The single-driver declaration of 2026-10-03 stands. No implementer is dispatched because
   no implementation remains.

### Task 2 — Contract repair (after decision 2)

1. Amend the REQ-0.35.0-10-10 witness clause as ruled and record the ruling in the brief's Change Log.
2. Confirm the brief still passes authored validation and the REQ-kind discipline scope.

### Task 3 — Verify (Stage 3)

1. Baseline under ARB: lint, typecheck, the full unit suite, the strict docs build, the scoped behave run, and the documents validation. Read each receipt's exit status; pipe nothing.
2. The brief's own verification list, every command, with observed output kept.
3. REQ to covers parity for the seven BEHAVIOR requirements.
4. The RED witness for each BEHAVIOR requirement on the reconstructed base. An error class there is inconclusive and is reported as such.

### Task 4 — Executed proof for all ten obligations

One proof specification per requirement, re-authored because the trial's were session-local
and are gone. The ledger's earlier proof records name the mutation each used.

| REQ | Kind | What is proven | Where it lives |
|-----|------|----------------|----------------|
| 01 | behavior | an owned row binds its cited corpus entry, not the scorecard class | resolver |
| 02 | behavior | an unowned row reads the scorecard; every prior row identity and source survives | population contract |
| 03 | behavior | on disagreement the corpus value binds and the disagreement is reported | advisory |
| 04 | behavior | an owned section with a live Ambiguous entry fails closed with three-part prose | fence |
| 05 | behavior | reconciliation is an append; the old-prefix fingerprint is unchanged | fixture walk |
| 06 | support | the scorecard states its narrowed authority | ledger event and documents validation |
| 07 | structural-fence | one reader, one surface per bullet | parent ADR BI-04 |
| 08 | behavior | skill- and ADR-sourced rows are retained against their source | retention arm |
| 09 | behavior | a missing source or absent text fails closed, naming row, path, rule and next step | retention arm |
| 10 | support | the manpage and the scorecard state the source-aware scope | ledger event and documents validation |

Every behavior proof names its production source, its covering test ids and a behavioral
substitution, and is run through the acceptance prove command. Requirement 8 of the brief
(stay inside the allowlist) is checked by diffing the two commits against the allowlist.

### Task 5 — Present evidence (Stage 4)

1. Finish every edit first. Freeze the tree. Re-run all ten proofs.
2. Build the evidence packet and replay it.
3. Independent review by Codex, tier 1, in a disposable writable checkout, prompted to
   confirm correctness with probing in both directions. Import the review by its receipt.
4. A finding against a requirement goes back through repair, proof and one focused follow-up.
   Two follow-up rounds is the limit; after that the OBPI is blocked and the decision goes to
   the operator.
5. Present the packet, its replay verdict and the review together, and wait for the
   operator's attestation. The human-review judgment and the attestation are the operator's
   words and are never authored.

### Task 6 — Sync and account (Stage 5)

Precomplete to exit 0, the closure narrative shown before it is written (it quotes Decision
item 9 verbatim), completion with the operator's attestation, the Step 4b section in the
brief, marker cleanup, two syncs with a brief-to-receipt check between them, and a handoff.

## Verification

```bash
uv run -m unittest tests.governance.test_bullet_retention
uv run -m behave features/classification_ownership.feature
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --bullet-retention
uv run gz validate --advisory-scorecard
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run mkdocs build --strict
```

## Notes

**Destination in mind.** Before writing this plan the conclusion was already formed, and not
by this session: the code exists, and three earlier sessions each named the same remaining
steps. This plan orders those steps and adds the mapping review the brief requires at
planning, which no earlier session ran.

**Alternatives rejected.** Leave the plan audit red and complete without it: rejected, the
operator ruled on 2026-10-05 that the audit is re-run to a pass. Clear the stale markers with
the preflight cleanup: rejected by the same ruling. Split REQ-0.35.0-10-10 into two
requirements, one per path: rejected as the larger contract change; one path already has its
own witness in REQ-0.35.0-10-06. Widen the support resolver to accept two paths: rejected,
it is outside the allowlist and changes a parser other briefs depend on. Revert the trial and
re-implement through dispatched implementers: rejected, the operator ruled the trial
implementation stays on main.

**Known limits.** The source module is about 670 lines against a 600 line authoring guidance
that nothing gates. The brief's third Demo command cannot run as written. Both were recorded
as insights on 2026-10-03 and are raised at review, not silently carried.
