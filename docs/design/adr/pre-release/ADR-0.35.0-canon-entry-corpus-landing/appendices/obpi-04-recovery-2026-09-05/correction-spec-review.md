# Bounded correction spec review — PASS

Persona: spec-reviewer. Scope: the four-file correction relative to `correction-baseline.index`, against `PLATFORM-FINDING.md`'s existing preservation-plus-exit-2 rule. This is not an OBPI acceptance verdict or a review of the whole recovery protocol.

**PASS. No defect found in this exact correction.**

- Unsupported/invalid required directory-sync errors no longer escape as a warning-and-continue: `unown.py:1804–1809` enters one of two nonreturning refusal paths, both exiting 2 (`:1862`, `:1901`). Fresh/journal-absent entry establishes the boundary before the sweep (`:2085–2088`) or any new transaction (`:2495`); journal-present cleanup establishes it after journal removal but before dependent removal (`:2128–2137`). Failure therefore cannot authorize dependent deletion or reuse.
- The regression matrix uses actual directory `fsync` fault injection, leaving regular-file sync operational (`test_content_unown.py:5540–5553`). Four errno names are exercised over fresh, journal-present and journal-absent entries, each with two faulted attempts and a healed retry. Assertions compare retained bytes, declaration bytes, ledger rows, exit 2, exactly one eventual witness and canonical-loader acceptance (`:5594–5658`). These are semantic state checks, with separate diagnostic assertions.
- Capability guidance changes the remedy, not the disposition (`unown.py:1812–1824`): unsupported/invalid required sync needs a working environment before retry; transient storage faults retain fix-and-retry guidance. It does not identify a filesystem from `EINVAL` alone.
- Windows equivalence remains explicitly unproved in `ownership.py:967–972`, `unown.py:2115–2117`, and the new manpage paragraph. The patch neither claims a Windows fix nor invents a new accepted exception.

Evidence inspected, not executed by this reviewer: [author targeted run](/private/tmp/gzkit-obpi04-assessment-4dt92ti0/correction-unsupported-green.log), 4 tests OK; [author scoped run](/private/tmp/gzkit-obpi04-assessment-4dt92ti0/correction-scoped-tests.log), 183 tests OK. Root's independent [original EINVAL reproducer output](/private/tmp/gzkit-obpi04-assessment-4dt92ti0/correction-validation/unsupported-barrier-observations.json) observes fresh entry exiting 2 with no snapshot and unchanged stores; witnessed-transition cleanup exits 2 with snapshot retained and unchanged stores.

Reviewed SHA-256 identities:

| File under `correction/` | SHA-256 |
|---|---|
| `src/gzkit/commands/content/unown.py` | `99f7c18d01e4f0ad03cfeebea36bf383e14bfcf88cf8106e68bd8cab2fee8e64` |
| `src/gzkit/content/ownership.py` | `93dfb8c3b3df1dadfa3d16dc477dbb0aee33abeb632c1d770d2b257c46cc591d` |
| `tests/commands/test_content_unown.py` | `39e57c88a1d0ab282f34c7fda451732d7f0394738caeb3497a5c011c358f61db` |
| `docs/user/manpages/content.md` | `9cdd47e646ce4fe5d5d4a1fdb357b2e72bda570c54ff56279e6b1eb681b7d105` |

Known enumeration, Windows and unrelated documentation gaps remain outside this bounded verdict, as directed. No full suite, live pipeline, code edits or ledger writes were performed by this reviewer. Only this review artifact was written.
