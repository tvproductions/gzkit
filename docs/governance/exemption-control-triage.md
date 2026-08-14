# Exemption-control triage (GHI #797 drain, 2026-08-14)

Companion to `data/exemption_control_grandfather.json`. That file counts the
disclosed absence of an `exempts` declaration; this file records **what was found
when the gates behind those absences were actually read**, so the next drain pass
starts from a reading rather than from a scan.

Authored under the operator ruling of 2026-08-14: *triage all 71, declare only the
honest `'none'`s.* Writing exemption controls was explicitly **not** in scope —
that remains the enrollment the 2026-08-12 inventory-not-enrollment ruling
declined, and the `advisory-rules-audit.md` § Recommended promotion order freeze
still governs (*"a new mechanical check is added only when a specific, observed
drift instance justifies it"*).

## Result

| | seed | pass 1 | pass 2 |
|---|---|---|---|
| Claims declaring `exempts` | 5 | 13 | **21** |
| Disclosed undeclared | 71 | 63 | **55** |
| `baseline_count` (shrink-ratchet) | 71 | 63 | **55** |

Sixteen claims have now been read end-to-end, found to carry no exemption surface,
declared `exempts='none'`, surrendered from the accepted list, and the ratchet
baseline decremented in the same commit as each pass.

**Pass 2 (2026-08-14) cleared the Tier-B backlog: every claim in this inventory has
now been read.** The 17 unreached claims resolved 8 declarable and 9 with a located
admit path. Nothing is left in the "absence of a located surface, but not a reading"
state — the remaining 55 are all *enrollment* debt (each owes a differential control),
never reading debt. That distinction is the point of this file: the next pass cannot
find cheap declarations here, and should not go looking.

Three of pass 2's eight declarations register **outside** `_qc_negative_controls` —
`gate5-ledger` and `gate5-attestation-absence` in `gzkit.mx.invariants`, `grader-gaming`
in `gzkit.mx.proxy_reality`. Declaring them in `_QC_CLAIM_EXEMPTS` alone left
`--exemption-controls` failing on all three, because that map only feeds
`register_qc_negative_controls`. They carry `exempts=EXEMPTS_NONE` at their own
`enforces(...)` call sites instead. A future declaration must check where its claim
actually registers; the map is not the only inlet.

## The bar applied

A claim was declared `'none'` only when **no input makes the gate admit an item it
has judged in violation**. Qualifying admit paths — any one of these means the
gate has an exemption and stays disclosed:

- a waiver / grandfather table (`data/*_waivers.json`, `data/*_grandfather*.json`)
- an `excluded` / allowlist entry
- an escape marker or skip token in the scanned content
- an opt-in arm that is off by default, or an opt-out config that disables the check
- an authorization booking (the resume-gate shape)

**Not** exemption surfaces, and deliberately so: scope predicates (which artifacts
the gate examines), threshold parameters (a budget defines what a violation *is*),
artifact-absent returns (nothing to compare), and error-path returns.

### The severity line (added by pass 2)

Eight of the seventeen Tier-B gates turned on a case the five bullets do not settle:
**a gate that finds something and does not exit non-zero on it.** The separator is
*who controls the admission*.

- A finding the gate classifies advisory/non-blocking by a **fixed code property** —
  a separate finding type, a `required: False` in an in-code check table, a question
  declaring no validator — is OUTSIDE the judged set. The gate never claimed to
  enforce it, so there is nothing to admit.
- A finding the gate WOULD fail on, admitted by a **project-controllable input** — an
  off-by-default flag, a manifest entry, a config value, a data file, a marker, a
  ledger booking — is an exemption, however well justified.

That line is what separates `readiness-audit` (in-code `required` bits plus a score
threshold — declared `'none'`) from `skill-audit` (an identical blocking/non-blocking
split, but gated on `--strict`, which is off by default — disclosed). Justification is
irrelevant to membership: `enforcement-floor`'s exclusion is deliberate and ADR-backed
and is still an exemption, because this list is an inventory, not an accusation.

This bar is calibrated against the two pre-existing declared exemplars, which are
the only place the line had been drawn before this pass:
`handoff-resume-unauthorized-{write,bash}` name the booking claim as their
exemption, and `verifier-pipe-gate` names the `pipefail`/`PIPESTATUS` escape. Both
controls assert the **differential** — refuse-without and permit-with, in one
function — which is the shape any control written from this triage owes.

## Declared `'none'` (16 — surrendered)

Pass 1 (2026-08-14, first eight):

| Claim | Why nothing is owed |
|---|---|
| `adr-status-freshness` | Diffs on-disk ADR canon against the derived index; every drift entry is a finding and nothing suppresses one. |
| `instructions-files-budget` | Per-file char budget. Project-overridable, but a threshold defines the violation rather than admitting one. |
| `invariant-coherence` | Byte-compares rendition playback against committed `AGENTS.md`. Only non-finding return is "no committed rendition exists". |
| `kind-invariance` | Requires a substantive `## Why foundation tier?` on every foundation ADR. The sidecar filter selects which files are ADRs; it admits no failing ADR. |
| `line-endings` | Two fail-closed arms (`.gitattributes` LF directive; no tracked text surface committed CRLF). No per-file waiver. |
| `orientation-freshness` | Asserts the SessionStart hook stays wired in both harnesses. Every arm yields a finding; a missing script is an error, not a pass. |
| `waiver-ratchet-closed-set-lock` | Per-surface mechanism check. The registry's `excluded` list is consulted **only** by the unregistered-file scan, never here. |
| `waiver-ratchet-dated-cutover` | Same. |

Pass 2 (2026-08-14, the Tier-B eight):

| Claim | Why nothing is owed |
|---|---|
| `agents-md-map-conformance` | Criteria (a)–(d) over the AGENTS.md template and rendered file. Table rows and fenced blocks are excluded from paragraph counting because neither *is* a paragraph; the budget overlay is a threshold; the prohibited-title match is case-insensitive **deliberately**, so authoring case is not an escape. The `_advisory` finding type is a separate heuristic ADR-0.0.54 reserves from hard rejection, not a downgrade of a/b/c/d. |
| `gate5-ledger` | Schema/shape conformance over ledger lines. Unreadable line, non-object entry, **unknown event type**, missing ledger, and missing schema are each findings — every shape that would otherwise be the skip. Gate 5 is never demoted by the MX marker. |
| `gate5-attestation-absence` | `_requires_human_obpi_attestation` returns `True` unconditionally (ADR-0.0.36 collapsed the branching, so there is no arm to take); the field validator fails closed on placeholder attestor, non-true `human_attestation`, empty text, and malformed date. |
| `grader-gaming` | A detector, not a judge-then-admit gate: reports every `obpi_completion_repudiated` whose cause is model-induced fabrication. The cause filter selects which events *are* the signal. |
| `dispatch-absorption-marker` | One frontmatter marker on one pool ADR. Both arms exit 3 — a **missing** pool ADR is a finding, so even the artifact-absent path fails closed. |
| `preflight` | Stale markers, orphan receipts, expired locks. An unreadable receipt is reported as an orphan and an unreadable lock as expired: the error paths accuse rather than excuse. `--apply` cleans up, never suppresses. |
| `readiness-audit` | Exits non-zero on any required failure or a sub-2.0 score. The `required` bit is fixed per check in an in-code table and the floor is a threshold — neither is project-settable, and every failure is reported in `issues` regardless. See § The severity line. |
| `pool-interview-schema` | Grammar + completeness over committed pool records. A record the audit **cannot read** is a finding by explicit design (the GHI #736 correction). `question.required` and the validator set are fixed in `ADR_QUESTIONS`, the same authority the CLI loader reads. |

## Exemption surface located — control owed (Tier A)

Each of these was read or its admit path located and named. None can honestly
declare `'none'`; each owes a control asserting the refuse/permit differential
across the named surface.

| Claim | Admit path |
|---|---|
| `waiver-ratchet`, `waiver-ratchet-silent-bypass` | registry `excluded` list |
| `handoff-documents`, `handoff-documents-populated-sections` | `data/handoff_section_grandfather.json` + pre-cutover legacy tolerance |
| `authorship-policy` | opt-in `authorship.required_email_suffix`; unset ⇒ whole audit is a no-op |
| `insights-shape` | `_INSIGHTS_SHAPE_WAIVERS`, keyed by content hash |
| `fidelity-presence` | `data/fidelity_presence_grandfather.json` |
| `persona-witness` | `data/persona_grandfather.json` |
| `rendition-floor-coherence`, `rendition-freshness` | MX hangar checkpoint downgrades the gate to advisory when the marker is present |
| `brief-structure` | `is_terminal_brief_status` carve-out — an authored `status:` flips a brief from judged to admitted |
| `module-size` | grandfathered roster (the control's own `expect_output` is `"not grandfathered"`) |
| `adr-taxonomy` | `data/foundation_grandfather.json` |
| `adversarial-validation` | `data/adversarial_validation_grandfather.json` |
| `advisory-scorecard-coverage`, `-summary-drift`, `-ruff-reachability` | `advisory_scorecard_grandfather.json`, `mechanical_witness_grandfather.json` |
| `closeout-proof` | `data/behave_coverage_waivers.json` |
| `complexity-doctrine-links` | `<!-- gz-validate-skip: complexity-doctrine-links -->` marker |
| `complexity-thresholds` | a declared "Bootstrap absolutes" section skips portability checks |
| `gate-callers` | `data/uncalled_gate_grandfather.json` |
| `status-writer-coverage` | `_DATACLASS_WAIVERS` |
| `qc-binding`, `theater-signature-scan` | `_SELF_EXCLUSION` set |
| `receipt-shape` | `data/historical_self_close_waivers.json` |
| `red-parity` | dated `CUTOVER` — pre-cutover completions skipped |
| `lock-exchange-coupling` | dated enforcement cutover grandfathering the warning-only transition |
| `unscoped-rules` | manifest `rules.unscoped_allowlist` |
| `session-green-gate` | `check_delivery` arm is opt-in and off by default |
| `smoke-tier` | empty tier passes unless the project declares `smoke.required` |
| `transcribed-adr-counts` | opt-in surface registry + `<!-- historical-count -->` opt-out marker |
| `req-kind-discipline` | all-untagged brief ⇒ legacy/grandfathered pass |
| `interview-transcripts` | `data/interview_transcript_waivers.json` |
| `tautological-test-audit` | waivers + self-exclusion + baseline |
| `validate-default-scopes` | `is_adr_shape_grandfathered` + waiver counting |
| `surface-fidelity-surface-weight`, `surface-fidelity` | `data/surface_weight_waivers.json` (the composite inherits it) |
| `exemption-controls` | its own `accepted_claims` list — this inventory is exempted by the surface it inventories |
| `lint`, `format`, `typecheck`, `test`, `behave` | the **external tool's** escape: `# noqa`/`per-file-ignores`, `# fmt: skip`, `# ty: ignore[...]`, `@unittest.skip`, skip tags |
| `task-envelope-coherence`, `-layer-drift`, `-obpi-divergence`, `-subdivision` | `_OBPI_ID_CANONICAL_CUTOVER` + per-signature grandfather sets + `req_atomic` exemption |

Added by pass 2, from the former Tier B. **None of these carries a
waiver/grandfather/excluded token anywhere in its module** — a token scan clears all
nine, which is exactly why the predecessor's grep located nothing and left them
unread. Each admit path below was found by reading the gate.

| Claim | Admit path |
|---|---|
| `surface-fidelity-bullet-retention` | `CorpusEntry.tier == "compressible"` + a `rendition_advisor_verdict` booking. A bullet absent from the surface, which the invariant arm fails, is **admitted** on the receipt. The error message concedes it: *"not an **unconditional** escape from retention."* |
| `surface-fidelity` (composite) | Inherits the above **and** `data/surface_weight_waivers.json` (already recorded). Both arms, not one. |
| `airlock-in-unaccounted-seam` | A live (non-revoked) `CaptainOverride` in `_decide`. The docstring states it: *"the only way past a NO-GO."* The authorization-booking shape, same family as `handoff-resume-*`. |
| `enforcement-floor` | `_GATE5_NAMED_NOT_ENFORCED` — `unenrolled_gate5_members` iterates `GATE5_INVARIANTS - _GATE5_NAMED_NOT_ENFORCED`, so `secrets` and `operator-pii` are subtracted from the floor's own declared population. The code's own word is *"exempt by design."* Deliberate and ADR-backed, and still an exemption. |
| `docs-build` | `mkdocs.yml` `validation:` downgrades. This repo currently sets `links.not_found: ignore`, so a dead link raises no warning for `--strict` to promote — see § Observations 5. |
| `skill-audit` | `_skill_audit_success` passes non-blocking warnings unless `--strict`, which is **off by default** and off in the control's own invocation. |
| `cli-audit` | Manifest `surfaces.manpage: false` — the per-command loop `continue`s past the manpage, heading, and index checks for any command carrying it. |
| `parity-check` | `enforced = template_path.exists() or bool(report_paths)`; when both are absent the gate returns `valid: True` and exits 0. The discriminator is **itself** a member of `required_files`, so removing the surfaces both disables the check and hides the removal. |
| `obpi-lifecycle-coherence` | The disposition set excluded from the orphan census (`terminal` / `completed` / `parked`) is reachable by writing a ledger event. Only the `parked` arm has a truthfulness re-check (`park_coherence_violations`, GHI #774); `terminal` and `completed` do not. |

## Tier B — cleared

**Empty as of pass 2.** All 17 were read: 8 declared `'none'` above, 9 moved into Tier A
with their admit path named. No claim in this inventory is now in the
"absence of a located surface, but not a reading" state.

## Observations (none of these is a defect)

Recorded because they shape what a future drain costs — **not** as tracked
defects. Read them as pricing, not as a backlog.

**1. The control-writing side is where the cost is.** All 71 claims have now been
read: 16 were declarable and 55 carry a real admit path. The drain is not gated on
judgment — the judgment is done and recorded — it is gated on writing 55
differential controls. That is the enrollment the 2026-08-12 ruling declined, and
this triage does not reverse it; it prices it. **The price is now exact rather than
approximate,** which is the one thing pass 2 bought that pass 1 could not.

**2. Five claims inherit their exemption from an external tool.** `lint`,
`format`, `typecheck`, `test`, and `behave` gate on ruff / ty / unittest / behave,
whose escapes (`# noqa`, `# fmt: skip`, `# ty: ignore`, `@skip`) are not gzkit
surfaces. A control for these asserts that gzkit's *invocation* still refuses
without the escape and admits with it — worth deciding once as a family rather
than five times.

**3. `gz validate --type-ignores` is the one Tier-A row whose control already
exists in substance** — it polices the `typecheck` gate's `# ty: ignore[...]`
escape (`.claude/rules/pythonic.md` § Type-check suppression syntax), which is the
refuse/permit differential an exemption control owes. It carries no enforcement
claim, so `typecheck` cannot name it.

> **Do not read that as a singular hole.** Measured 2026-08-14: the QC registry
> holds 56 steps (55 `bound`, 1 `advisory`) and `type-ignores` is not in it at
> all, but neither are `class-size`, `cli-alignment`, `commit-trailers`,
> `distribution`, `sensitivity`, `skill-alignment`, or `utf8-prefix` — dozens of
> explicit-only `gz validate` scopes carry no claim, and `type-ignores` is not in
> the `validate-default-scopes` blanket either (the default tier is 13 scopes).
> `--qc-binding` passes green over all of it because it audits only *enrolled*
> steps. That is the single-membership blindness
> `exemption_controls.py` already names one level up — a known posture, not a
> discovery, and enrolling one scope does not change it.

**4. `_ep_fidelity_presence` deliberately zeroes its own exemption, and this is
correct.** The control calls `audit_fidelity_presence(root, grandfather=frozenset())`
so the refuse arm genuinely fires against an unwaived corpus — a stronger control
than most in the table. It is recorded here only as a worked illustration of the
disclosed GHI #797 class (the admit half of a two-claim gate goes unexercised),
never as a criticism of the control.

**5. `docs-build`'s admit path is live in this repo, and it is worth an operator
ruling rather than a silent Tier-A row.** `run_mkdocs`'s own docstring states the
gate exists so that *"broken nav and dead links fail closed."* This repository's
`mkdocs.yml` § `validation` currently sets `links.not_found: ignore`, which
suppresses the warning entirely — so `--strict` has nothing to promote and dead
links do **not** fail closed today. `nav.omitted_files`, `absolute_links`,
`unrecognized_links`, and `anchors` are all set to `info` on the same block.

Recorded here rather than repaired: changing those settings is a behavior change to
a live gate, outside the ruled scope of this pass (*read the 17, declare the honest
`'none'`s*), and it would very likely surface a backlog of existing dead links in one
step. It is a **coupled-surface incoherence** — a docstring asserting an enforcement
the config withdraws — not merely an exemption, which is why it is called out rather
than left as a table cell. Routing is the operator's.

## Verification

```bash
uv run gz validate --exemption-controls   # 76 inventoried, 21 declared, 55 disclosed
uv run gz validate --waiver-ratchet       # baseline_count 55 matches the live list
jq '.accepted_claims | length' data/exemption_control_grandfather.json   # 55
```
