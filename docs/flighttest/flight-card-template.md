# Flight-Card Template

> One card per **sortie**. Author it **before** the flight and freeze it at go.
> The card *is* the pre-registered falsifier — filling in expected observables
> after flying is a doctrine violation (README §2.1). Copy the block below into
> the campaign flight log and fill every field before requesting go.

```
FLIGHT CARD — SORTIE <N> : <short name>
════════════════════════════════════════════════════════════
ENVELOPE POSITION   : <center | expansion | corner>
DESIGN CLAIM        : <the one-sentence design property this sortie asserts holds>
SYSTEMS UNDER TEST  : <list every gz system this sortie exercises>
SUBSTRATE           : <repo + starting state; must satisfy README §7 criteria>
DEPENDS ON          : <sorties that must have passed first, or "none">

────────────────────────────────────────────────────────────
ENTRY CONDITIONS (go/no-go — all must hold to open the sortie)
  - <substrate state, e.g. clean tree / no active locks>
  - <prior-sortie evidence required>
  - <Test director authorization recorded>

────────────────────────────────────────────────────────────
TEST POINTS (maneuvers, in flight order — the chain)
  #    GOVERNED PATH (skill / gz verb)        EXPECTED OBSERVABLE
  1    <skill or `gz ...`>                    → <what the black box must show>
  2    <skill or `gz ...`>                    → <...>
  ...  (chain continues; each point's output feeds the next)

────────────────────────────────────────────────────────────
INSTRUMENTATION (the black-box signature of a PASS)
  ledger    : <event kinds + counts + key fields that MUST appear, in order>
  receipts  : <receipt name prefixes that MUST be emitted, e.g. arb-ruff-, obpi-receipt->
  state     : <gz state / gz status assertions that MUST hold at exit>
  artifacts : <files that MUST exist with the right frontmatter/linkage>

────────────────────────────────────────────────────────────
PRE-REGISTERED FALSIFIERS (any ONE ⇒ FAIL)
  - <observed behavior that proves the design claim false>
  - <missing ledger event / receipt that proves the workflow did not hold>
  - <a test point that only passed by leaving the governed path (README §2.4)>

────────────────────────────────────────────────────────────
ABORT CRITERIA (halt-not-fail conditions)
  - <blocking hook fires for a legitimate missing-evidence reason>
  - <substrate corruption unrelated to the workflow under test>

────────────────────────────────────────────────────────────
CHASE (independent confirmation)
  - observer   : <spec-reviewer | quality-reviewer | operator>
  - reads      : <the exact ledger slice / receipts handed to the Chase>
  - verdict    : <PASS/FAIL, authored by the Chase from evidence alone>

────────────────────────────────────────────────────────────
DEBRIEF & FEEDBACK
  - black box vs card : <what matched, what diverged>
  - squawks           : <each anomaly + its disposition (README §5)>
  - design signal     : <sound | awkward-but-correct | wrong — with the why>
  - routed to         : <GHI # | design-feedback entry | corpus | card amendment>
  - re-fly needed?    : <yes/no; if the sortie prompted a gzkit design change>
════════════════════════════════════════════════════════════
```

## Filling guidance

- **DESIGN CLAIM** is the falsifiable heart of the card. Write it so a single
  observation could disprove it ("a completed OBPI with no Gate-5 ledger event
  is impossible to produce"), never as a vibe ("attestation works").
- **EXPECTED OBSERVABLE** per test point must be a *black-box* fact — a ledger
  event, a receipt ID, a `gz state` assertion — not "the command succeeded."
- **INSTRUMENTATION** is authored from the workflow's *design*, not from a prior
  run of the command. Deriving expected events by running the command first and
  transcribing its output is the assertion-from-a-run anti-pattern (AGENTS.md
  DO-IT-RIGHT §6).
- **FALSIFIERS** must include the "passed only by leaving the governed path"
  case for every sortie — it is the anti-vibing tripwire.
- **CHASE reads the black box cold.** Hand the Chase the ledger slice and
  receipts, not your narrative. If the Chase cannot reach PASS from evidence
  alone, the sortie has not passed.
