# Proof — GHI cross-reference staleness

## 2026-10-10 — maintenance visit A

Read-only scan; no issue body was edited.

```
transcribed sibling-state annotations: 7
decayed (body asserts OPEN, sibling CLOSED): 3  -> rate 43%
  #799 asserts #533 is open; it is closed
  #930 asserts #929 is open; it is closed
  #969 asserts #889 is open; it is closed
```

Population down from 10 to 7 and decayed from 5 to 3 because GHI #894 closed on 2026-09-29;
its two annotations left the open queue with it. Per the baseline's own rule ("Removing an
entry from this list is correct when its issue closes"), the two #894 entries were removed from
`data/ghi_cross_reference_baseline.json` and `baseline_count` in
`data/waiver_ratchet_registry.json` was decremented 5 → 3, so the shrink-only bound follows the
population down instead of leaving two phantom slots. `gz validate --waiver-ratchet` exit 0;
the chore gate exit 0. No new annotation appeared: the authoring convention produced no fresh
debt since 2026-09-20, which is the result the subtractive remedy predicts.

The rate (43%) is still the finding. The three survivors are the same three: two decoration
(#799, #930) and one **load-bearing** — #969 (open) argues its named remedy is compromised
because #889 reports a defect in it, and #889 has been closed since 2026-09-14. Re-reading
#969's argument against what #889 landed is judgment work this chore surfaces and does not
perform; it is carried to the operator again.

## 2026-09-20 — first run at landing

Read-only scan; nothing was edited.

```
transcribed sibling-state annotations: 10
decayed (body asserts OPEN, sibling CLOSED): 5  -> rate 50%
  #799 asserts #533 is open; it is closed
  #894 asserts #883 is open; it is closed
  #894 asserts #877 is open; it is closed
  #930 asserts #929 is open; it is closed
  #969 asserts #889 is open; it is closed
```

All five are disclosed in `data/ghi_cross_reference_baseline.json`, which is
registered shrink-only in `data/waiver_ratchet_registry.json`. Negative control run
the same day: a sixth entry makes `gz validate --waiver-ratchet` exit 3; removing it
exits 0.

Four of the five are decoration — a Related-list mention the issue's argument does not
rest on. One is load-bearing and is surfaced, not resolved: **#969 argues its named
remedy is compromised because #889 reports a defect in it, and #889 is now closed.**
Re-reading that argument against what #889 landed is judgment work this chore does not
perform.
