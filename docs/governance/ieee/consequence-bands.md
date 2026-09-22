<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Consequence bands

> **Tier: operator-ruled input. Canonical within the investigation; not doctrine.**
> Authored live with the operator on 2026-09-22 in answer to
> [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md) `Q-04`. It is the input IEEE 1012
> Clause 5 requires before any proportionality question can be answered.
>
> **Defining bands is not adopting them.** This file does **not** re-key the
> lite/heavy lanes, does not change any gate, and authorises no work. Re-keying
> is a Phase 4 question.
>
> **The five gates are untouched and are not in scope here** (standing operator
> constraint, 2026-09-22).

## Why bands at all

IEEE 1012 Clause 5 makes it normative that verification rigour scale to
**consequence**, assigned so that high-consequence parts are segregated. gzkit's
lite/heavy lanes are a two-level scheme keyed to **surface kind** — CLI, API and
schema are heavy — which is a proxy for consequence, not a measure of it
(F-019, `Q-04`).

## The two axes

Operator ruling, 2026-09-22: score two axes, band on the pair.

**Detectability — how a failure surfaces.**

| | Meaning |
|---|---|
| `D2` | **Silent.** Reports success while wrong |
| `D1` | **Latent.** Reports nothing either way; found when something else breaks |
| `D0` | **Loud.** Fails visibly at the point of use |

**Recoverability — cost to undo once found.**

| | Meaning |
|---|---|
| `R2` | **Forensic.** Reconstruct from history; may be unrecoverable |
| `R1` | **Bounded repair.** Fix and re-run |
| `R0` | **Trivial.** Edit and move on |

**The band is derived, never assigned: `band = D + R`.**

| D + R | Band |
|:-:|:-:|
| 4 | **C3** |
| 3 | **C2** |
| 2 | **C1** |
| 0–1 | **C0** |

Only the two digits are maintained per surface. There is no band table to keep in
sync, and no scored pair can disagree with its own band — which is the specific
maintenance burden F-032 warns this project keeps inventing.

## Why detectability is one of the axes

Not the conventional reading of 1012, and chosen on this repository's own
evidence. Every expensive failure recorded here was a **silent** one:

- `enforcement-claim-nc-audit-2026-07-18.md:50` — *"32 of 47 claims do not prove
  what they assert"*, immediately followed by *"`gz check` reports 47/47
  verified."*
- Gate 5 in `gz gates` is `return True`; Gate 2 has been satisfied by lint and
  typecheck runs (F-019).
- `@covers` blinded the tautology audit over 220 of 290 operations (F-021).

A failure that crashes costs time. A failure that reports success costs truth.
Banding on blast radius alone would score a loud CLI bug and a silently-wrong
validator alike.

## Scored surfaces

| Surface | D | R | Band | Anchor |
|---|:-:|:-:|:-:|---|
| Ledger writes (L2) | 2 | 2 | **C3** | `Ledger.get_post_validation_failed_gates` exists because the effective view launders failures to pass (GHI #411) |
| Attestation / completion events | 2 | 2 | **C3** | mechanical content is `attestation_text.strip()` non-empty; 15 agent-attested, 3 flagged `human_attestation: True` |
| `gz adr demote` | 2 | 2 | **C3** | `obpi_lifecycle.py:256-260`, its own comment: *"A hollow exit 0"* |
| ARB receipt durability | 2 | 2 | **C3** | 391 receipts exist only on the authoring machine; `artifacts/` is gitignored |
| ARB receipt binding | 2 | 1 | **C2** | `arb/validator.py:279` returns `None` for 5 of 9 step names |
| Gate logic | 2 | 1 | **C2** | `gates.py:256-258` |
| Validators / `gz check` | 2 | 1 | **C2** | the 47/47 result above |
| Hooks | 2 | 1 | **C2** | `.claude/hooks/pipeline-gate.py:156-158` continues past an out-of-allowlist path |
| `@covers` binding | 2 | 1 | **C2** | `tautological_tests.py:108-134` |
| Schemas | 1 | 2 | **C2** | data already admitted to L1/L2 must be reconstructed |
| Distribution / `gz init` | 2 | 1 | **C2** | we report a successful release; the adopter finds the break |
| Handoffs | 1 | 2 | **C2** | sole custodian of cross-module facts with zero hits elsewhere in the repo |
| Other state-mutating `gz` verbs | 1 | 1 | **C1** | — |
| Control surfaces (`AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`) | 1 | 1 | **C1** | composition drift fails closed under `gz validate --invariant-coherence` |
| Briefs / ADRs as documents | 1 | 1 | **C1** | deletion is scored under `gz adr demote`, not here |
| Read-only `gz` verbs, derived views, docs, manpages | 0 | 0 | **C0** | regenerate from source |

### Three rows the operator ruled against the drafted score

- **ARB receipts split into two rows.** Drafted as one surface at C2, scoring the
  repairable binding defect. Ruled: score the **realised loss** — evidence that
  cannot be retrieved is not evidence — so durability is C3 and binding stays C2.
  This is the first surface the scheme needed two rows for, which is itself a
  signal that receipts are two things.
- **Handoffs raised C1 → C2.** Sole-custodian facts are forensic to lose.
  **This score is expected to fall back to C1 on its own** once `Q-06`'s
  sequencing lands and durable facts have a home — the score tracks the fix
  rather than freezing the accident.
- **Control surfaces held at C1.** Byte-coherence proves the rendition matches
  the corpus, not that a rule is right; a coherent-but-wrong rule was argued as
  `D2`. Ruled C1: that is a judgment failure, not a mechanical one, and the
  mechanical surface fails closed.

## What fell out of the scoring

**The CLI does not band as one surface.** Read-only verbs score C0; state-mutating
verbs score C1–C3. Any Phase 4 proposal that bands "the CLI" as a unit is scoring
a category that does not behave as one.

**`gz adr demote` scored C3 from D and R alone**, with no input from F-003. The
scheme reproduced the severity of the largest measured loss in the repository
without being told about it. That is the main evidence the axes are the right
ones.

**Nine of sixteen rows are `D2`.** Over half the scored surfaces fail by
reporting success. That is F-021 restated as a distribution, and it is the
strongest argument in this file for why rigour keyed to surface *kind* mis-ranks
this system.

## Amendments

- **2026-09-22 — Authored live with the operator.** Axes ruled (two, scored
  together), band derivation ruled (`D + R`), sixteen surfaces scored, three rows
  ruled against the drafted score.
