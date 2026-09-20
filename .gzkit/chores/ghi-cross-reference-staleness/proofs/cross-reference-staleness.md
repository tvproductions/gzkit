# Proof — GHI cross-reference staleness

First run at landing, 2026-09-20. Read-only scan; nothing was edited.

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
