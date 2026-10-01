# Record — gate witness audit, 2026-09-30

> **This is a dated record, measured 2026-09-30.** It states measurements and their methods;
> it amends no plan, rules on nothing and repudiates nothing. The figures are the record of
> one pass, not a live value. Re-run the evidence scripts rather than transcribing a number
> from this file. Evidence and re-run instructions:
> [`artifacts/audits/gate-witness-audit-2026-09-30/`](https://github.com/tvproductions/gzkit/tree/main/artifacts/audits/gate-witness-audit-2026-09-30) (raw reports, scripts and data; see its `README.md`).

## Why this was taken

The v0.34.8 release closed a set of gates that had reported green without holding. The
operator asked three questions in the release session:

- Did any earlier completion go through one of those gaps while it was open?
- Why are such gates so pervasive?
- Which greens can be believed?

This record holds the four measurements taken to answer them. Their conclusions are routed
to GHI #1154 (test shape), GHI #1155 (enrollment) and the v0.34.8 release notes' Known issues.

## Reading this record

Two claims in the same session were stated without measurement and then retracted
("most of the release", and "almost nothing fed the gates a known-bad input"). The
measurements below answer different questions over **different populations**, so their
numbers are not comparable with each other:

| Measurement | Population | Question |
|---|---|---|
| 1. Attestation audit | Completions, closeouts and releases inside each gap's open window | Did the gap let something through? |
| 2. Pre-fix test shape | The 12 gates already known to be hollow, selected because they failed | What did their tests feed them? |
| 3. Gate map | The 98 registered enforcement claims at `c0aa6467b` | Does each control depend on its gate? |
| 4. Registered at parent | The same 12 hollow gates, at each fix commit's parent | Were they under a registered control? |

A finding marked **verified** was re-read against the ledger, receipts, code or git in the
main session. **Reported** means it comes from a delegated agent's report and was not re-checked.

## 1. Attestation audit (reports `auditA`–`auditD`)

Each gap's open window was taken from its fix commit. The population was every completion,
closeout or release recorded inside it. Each item was classified EXPLOITED, EXPOSED-CLEAN or
UNDETERMINABLE, with evidence.

**Verified:**

- OBPI-0.0.24-04 (heavy lane) completed with a failed unittest receipt on record:
  `arb-step-unittest-e3b0f66d…`, `uv run -m unittest -q`, exit 1, 18 minutes before
  completion. Its attestation (ledger line 4524) cites no unittest receipt. (#889)
- OBPI-0.0.22-05: its full-suite receipt `f0aba782…` shows exit 1, five minutes before
  completion. The attestation cites a scoped run and mentions "Out-of-scope drift filed as
  GHI #359". (#889)
- OBPI-0.0.28-03: the key_proof pairs a scoped unittest command with receipt `a7295197…`,
  which recorded the full suite (exit 0). (#942)
- Three completions on a standing refutation, each disclosed in the attested record:
  OBPI-0.35.0-02 (ledger L15504, "The adversary's own check was NOT re-run"),
  OBPI-0.34.0-03 (L14160, REQ-03/04 tests "still bypassable"), and OBPI-0.34.0-05 (L14463,
  "Unresolved and disclosed, not waived"). (#960)
- OBPI-0.35.0-09: at completion (2026-08-21T08:23:56Z), the latest red receipt for REQs
  01/02/04/05/06/10 was `none`. The `error` receipts that now stand were written 10 minutes
  later. OBPI-0.34.0-02: REQ-02-05 had no red receipt before completion. (#849)
- The #1057 example OBPI-0.0.26-01: commit `32adb990c` modified `commands/adr_promote.py`,
  `events.py` and `ledger.py`, none of them in the brief's Allowed Paths. That allowlist is
  itself hedged ("or wherever the evaluate command lives").
- `mkdocs.yml:229` at `d266be9ff^` carried `links: not_found: ignore`. (#803)
- `57a94bd58`, a `tests/` commit with no `Task:` trailer, reached origin through the
  `--reuse-verified` pre-push skip. The cause was read in code and fixed under #1017
  (`b22353885`, `c0aa6467b`).

**Reported, not re-checked:** #889 284 completions (2 exploited, 56 clean, 226
undeterminable); #942 606 (1 / 1 / 604); #994 2 (0 / 2 / 0); #1093 53 (3 / 48 / 2); #959
7 clean; #960 20 (3 exploited / 7 clean / 10 undeterminable); #985 458 (0 / 1 / 457); #996
8 clean; #1057 307 replayable PASS receipts (56 exploited, 10 more on `__init__.py` only,
15 undeterminable, 223 clean); #849 22 (2 / 20 / 0); #927 599 `fix(` commits, all
undeterminable; #995 7 clean; #1124 4 clean, 1 undeterminable; #803 every release since
v0.3.1, by historical rebuild; #1017 280 trailer-less code commits reached origin.

**Unconfirmable:** OBPI-0.35.0-05's Demo runs `gz content compose`, and a
`composition_candidate_emitted` row exists before its completion, but no record ties the
row to the Demo. OBPI-0.0.65-03's demo handoff was never committed.

## 2. Pre-fix test shape (`pretest-shape.md`, plus three main-session reads)

For each of the 12 hollow gates, the tests at the fix commit's parent were read for the
inputs they fed the gate. Main session: #889, #996, #995. Delegated: the other nine, with
#960 and #803 spot-checked.

Only #803 was happy-path-only. Eleven had negative tests. What they lacked was an input
**present but false**: in five the negatives were absence-only, in four a test asserted the
defect itself, and in three the passing fixture was a stand-in the test declared sufficient
(`"{}"` as a receipt, `"Rationale here."` as a walkthrough). Per-gate table: GHI #1154.

## 3. Gate map (`gatemap.py`, `gatemap-final.json`)

For each of the 98 registered enforcement claims at `c0aa6467b`, every guard statement in
the gate functions the claim names was replaced with `pass`, one at a time, in a detached
worktree. That claim's own control was then re-run through `gzkit.mutation_witness`: 662
mutants, 235 killed, 427 survived.

| Result | Claims |
|---|---:|
| Control fails when at least one guard is removed | 92 (31 catch all removals, 8 at least half, 53 fewer than half) |
| Control passes with every guard removed | 1 (`population-controls-disclosed`, an admit control whose refuse partner is load-bearing) |
| Not measured | 5 (`module-size`, `tautological-debt`: the derived gate target is a helper and the real gate runs behind a subprocess; `readiness-audit`, `tautological-debt-waived`: the shared `run_command` cannot be mutated by the sweep; `cli-usage-error-exit-two`: no in-process function) |

24 of the 98 claims pin the reason they expect (`expect`); 74 accept any failure. The bar is
low: one caught removal counts as load-bearing. The 427 survivors are **unreviewed**. One
read in the smoke run (`if not drift: return []`) was equivalent.

## 4. Registered at parent (`registered_at_parent.py`, `.json`)

The criterion, fixed before running: at the fix commit's parent, does any registered
enforcement claim name, in its `source_fn` or `gate_targets`, a `src/gzkit` function the fix
modified? Each parent's registry was dumped from its own code.

**9 of 12 had no such claim:** #889, #996, #995, #960, #959, #888, #932, #933, #1124. In
five of them, a keyword pass found a nearby claim on the same surface naming a different
function. #851 (`session-green-gate`) and #803 (`docs-build`) were registered. #1007 is a
literal hit only because it shares fix commit `1edf9dc1b` with #851.

## Errata — report claims that did not survive checking

| Report | Claim | Finding |
|---|---|---|
| `auditC.md` | Only 2 of the 4 survived hunks in the 73aaab093 receipt are driven by `57a94bd58` | False: all four mutants fail that commit's tests, including 127-127, run separately |
| `auditD.md` | `61eb84194` is a trailer-less code commit | False: it carries `Task: TASK-deps-upgrade-ty-0.0.84` |
| predecessor handoff and insight | The undriven guard in `92f64debc` is the seen-dedupe | False: the receipt's `618-619` is the event-type filter; removing the dedupe is already killed |
| drafted release entry (#959) | None of the 13 completed refutations carried a resolution | False: all 13 refuted `adversarial_validation` rows carry a non-empty `resolution` |
| `auditC.md` | names the plan-audit verb with a hyphen (`plan-audit`) | No such verb: it is `gz plan audit`. Corrected in the report before it landed; the claim it carried is unchanged |

## What this record does not establish

- How many of today's gates (64 `gz check` steps, 100 `gz validate` scopes, 12
  `gz obpi precomplete` checks, plus the completion and closeout gates) lack a registered
  control. That population was not mapped. Its enumeration is GHI #1155's contract.
- What caused the pattern. The 2026-09-24 integrity audit found production and tests in
  the same commit in 9 of 9 sampled OBPI increments, which is consistent with co-authoring
  but does not establish it.
- Whether any completion above should be repudiated. That is an operator ruling and has not
  been made.
