# Attested REQ Whose Subject a Later Ruling Retired

*Canonical expansion for the binding bullet in
`AGENTS.md` § OBPI Acceptance Protocol (in `governance-core.md` § Non-negotiable
rules until that rule was folded into the root contract, 2026-09-17). Authored under GHI #823 after the transition had been
resolved correctly twice from first principles and recorded nowhere an agent
would find it. Home ruled by the operator 2026-08-18: the binding bullet lives
in `governance-core.md` (then) because it was the only rule whose `paths:` scope
(`**/*`) loads for both known instances — one edited `tests/**`, the other
edited a JSON data file, and a `tests/**`-scoped rule would have missed the
second by construction.*

## The transition

An attested REQ asserts something about a surface. A later doctrine ruling
retires that surface's subject. The REQ's parent ADR is **terminal** and
cannot be amended.

The population is bounded and non-empty: every terminal ADR carrying attested
REQs whose subject a later ruling can retire. `ADR-0.0.37` alone produced two
instances in sixteen days.

## Why the usual repair is unavailable

Ordinary doctrine drift is repaired by amending the artifact that carries the
claim. Here that move is unavailable **by construction** — a terminal ADR
(`ADR-0.0.37` § Terminal Disposition, "Split-and-Supersede", 2026-07-18)
cannot accept an amendment, and its permanently-withdrawn OBPIs cannot accept
new work. So the disposition has to live somewhere other than the ADR, which
is what makes this a distinct class rather than an instance of doc drift.

Note where an agent is actually standing when this fires: in `tests/`, or in
`data/`, or wherever the retired surface lives — **not** in
`docs/design/adr/**`. Nobody edits a terminal ADR, because it is terminal.
A rule scoped to the ADR tree would never load.

## The two wrong answers

Both are locally plausible, which is why this needs writing down:

| Wrong answer | Why it fails |
|---|---|
| **Delete the covering test / retire the file** | Orphans an attested REQ. The attestation record then claims proof that no longer exists — the record is falsified, not updated. |
| **Keep it unchanged** | The surface now asserts retired doctrine. The suite fails, or the fence encodes a claim the codebase has ruled against. |

## The disposition (binding)

1. **Read what the REQ *literally* asserts** — not what its surface currently
   demonstrates, and not what you assume it was for. These routinely differ,
   and the difference is the whole procedure.
2. **Repair the surface so that literal assertion stays true.** The surface is
   repairable; the attested assertion is the invariant.
3. **Preserve the proof-channel binding.** The `@covers` tag, the ledger
   citation, or the `## Boundary Invariants` entry stays attached. Moving or
   dropping it is the delete answer wearing a repair's clothes.
4. **Record the amendment and its reason at the surface** — the test docstring,
   the file, the commit body. A silent repair leaves the next reader deriving
   this again, which is the failure GHI #823 was filed on.

## The discriminator — when this does NOT apply

The procedure works because in both known instances the REQ's literal
assertion was **doctrine-neutral**: it survived the ruling untouched, and only
the surface underneath it was stranded.

If a REQ *literally* asserts the retired doctrine, step 2 has nothing to
repair toward — no rewriting of the surface can make a retired claim true.
**No procedure is claimed for it.** The honest disposition is operator
escalation: the attestation is a true historical record of what was decided on
its date, the ruling is a true statement of what is decided now, and
reconciling two true records on an unamendable artifact is a governance
decision rather than an editing task. Do not stretch the procedure above to
cover it. Five instances have been escalated and ruled (§ Worked examples 3,
4, 5 and 6); each ruling decided its own case and none is a procedure for the next one.

## Worked example 1 — four `@covers` tests (GHI #819, `da935dc35`, 2026-08-17)

`TestPerVendorTemperatureRouting` carried four `@covers` tests for
`REQ-0.0.37-15-01` through `-04`, naming codex and claude as `AgentContract`
consumers — which `OBPI-0.35.0-09` retired. The commit body records the
reasoning verbatim:

> They cover REQ-0.0.37-15-01 through -04 on ADR-0.0.37, which is TERMINAL and
> cannot be amended, so the tests are repaired rather than deleted -- deleting
> them would orphan attested REQs.
>
> The assertions were doctrine-neutral all along; only the vendor names were
> stranded

Step 1 is visible in that second sentence: the REQ asserted that the resolver
routes, not that `AgentContract` routes per-vendor. `REQ-15-01` was repointed
to exercise two content types — `Rule` (genuinely per-vendor) and
`AgentContract` (root-only) — proving the mechanism without asserting the
retired claim.

Step 4 is visible too. `REQ-15-04`'s docstring had reserved space for *"the
intended future where codex and claude are tuned to diverge"*; the amendment
records that the future is foreclosed rather than quietly deleting the
sentence.

## Worked example 2 — a JSON invariant seed file (2026-08-02)

The `foundation-adr-registers-invariant` entry in
`data/constitutional_invariant.json` declared a structural witness that never
existed, and the Foundation Sunset froze its subject set permanently. The
reasoning, verbatim from
`docs/governance/build-to-1.0-campaign-2026-08-16.md`:

> The **file is retained, not deleted** — `REQ-0.0.37-01-03` (attested,
> OBPI-0.0.37-01) asserts only that the three seed files exist, load via
> `load_invariants`, and validate against the schema, never that the claim
> text is true; rewriting `claim` + `structural_witness` preserves attested
> canon exactly, deleting the file would falsify it.

This is the instance that fixes the rule's home. It touched a JSON data file,
not a test — so the `@covers` side of the transition was not where an agent
was standing, and a `tests/**`-scoped rule would have been silent.

Note also *"asserts only that … never that the claim text is true"*. That is
step 1 performed explicitly, and it is the sentence to imitate.

## Worked example 3 — a REQ that literally asserts the retired claim (GHI #1103, 2026-09-26)

The first instance of the discriminator case. `REQ-0.0.29-02-06` (attested,
`OBPI-0.0.29-02`, Completed) read: *"Given no archetype rule matches a metric
crossing, when the engine runs, then `archetype=long_parameter_list` (default)
is bound and `recommended_move` is populated from the distilled-characteristics
document, never from a fabricated string."* The default named a real archetype
for every unmatched crossing — 1178 of 2193 diagnoses over `src/gzkit`,
one-parameter functions labelled Long Parameter List — so no repair of the
surface could keep the literal assertion true and fix the defect. Step 2 had
nothing to repair toward.

It was escalated with three choices: amend the REQ in place, leave the REQ as
history and drop its `@covers` binding, or hold the fix. The operator ruled,
verbatim: *"fix 1103 with an explicit unclassified archetype"* and *"Amend in
place (Recommended)"*. So:

- the REQ line keeps its attested text and gains a dated `Amended 2026-09-26`
  note quoting the ruling — the record of 2026-05-06 is not rewritten;
- the covering test keeps `@covers("REQ-0.0.29-02-06")` and asserts the amended
  behaviour, with its docstring recording why;
- the REQ's second clause (`recommended_move` never fabricated) was
  doctrine-neutral and kept its original covering test unchanged — step 1
  applied clause by clause.

## Worked example 4 — REQs that name a command line (GHI #1166 and #1167, 2026-10-04)

Two more discriminator cases, found the same day while repairing defects in the
pipeline skill. In each, an attested REQ under a Validated ADR named a literal
command that a later ruling had made inert or refused.

**GHI #1166.** `ADR-0.18.0` carried four attested REQs naming the
`--no-subagents` flag of `gz obpi pipeline` (`REQ-0.18.0-05-11`, `-06-06`,
`-07-08`, `-08-07`), for example *"`--no-subagents` flag MUST bypass dispatch
and execute inline"*. The flag was parsed and read by no code; since GHI #886 a
single-session run is permitted only when declared on the ledger with
`gz obpi dispatch --single-driver --reason`. Escalated with three choices:
remove the flag and amend the REQs, wire the flag so the REQs became true as
written, or hold. The operator ruled, verbatim: *"Remove the flag
(Recommended)"* and *"Remove, amend REQs in place (Recommended)"*.

**GHI #1167.** `REQ-0.0.14-03-07` (`ADR-0.0.14`) read *"Abort/handoff instructs
`gz obpi lock release --force`"*, and its covering test required that string in
the pipeline skill. `ADR-0.0.41` made that command exit 3 on a held lock.
Escalated with three choices: amend in place, keep `--force` beside `--abandon`
so the text stayed literally true, or revert the fix. The operator ruled,
verbatim: *"Amend in place (Recommended)"*.

So, in both:

- each REQ line keeps its attested text and gains a dated `Amended 2026-10-04`
  note quoting the ruling and naming the surviving route;
- where a covering test existed it keeps its `@covers` binding and asserts the
  amended instruction, with its docstring recording why; the four `ADR-0.18.0`
  REQs had no covering test, so no binding moved;
- the ADR bodies, which name the same commands, are terminal and are left as
  written.

What these add to example 3: neither conflict was found by reading the REQ
first. The #1166 choice was put to the operator before the owning ADR was read,
and had to be put again; the #1167 conflict surfaced only when the unit tier
failed on the covering test. Before removing or rewording a command an
operator-facing surface names, search the ADR tree and the tests for REQs that
name it.

## Worked example 5 — a REQ kept true by routing the work (2026-10-11)

`REQ-0.0.27-04-07` (attested, `OBPI-0.0.27-04`, under Validated `ADR-0.0.27`)
reads: *"Given the OEE-binding requirement, when the document is parsed, then
each metric's "Practitioner-eye observation" subsection exists and is
operator-attested at Gate 5."* The ADR adds *"Distillation pass is
foundation-kind ceremony at every recurrence."* Later canon reads *"Gate 5 names
completed OBPI/ADR work only"* (`AGENTS.md` § Attestation, GHI #822), the
foundation kind closed, and the ADR became terminal. A recurring pass run from
the `gz-complexity-distill` skill would then be attested "at Gate 5" with no
OBPI completing. The REQ was true of the one document that existed, attested at
the OBPI's own Gate 5; whether it bound later passes was the question. Found by
the skill-to-rule audit of 2026-10-10 (row B21). A first edit renamed the
attestation in the skill and was withdrawn before push, because that edit
decided the question.

It was escalated with four choices: rename the attestation of a recurring pass,
run each recurring pass as an OBPI, make distillation an exception to the naming
rule, or hold. The operator ruled, verbatim: *"B"*, the option worded *"Gate 5,
kept literal. Each recurring pass runs as an OBPI you initiate under a feature
ADR."* So:

- the REQ, the ADR and the naming rule keep their text, and no amendment note is
  added, because none of the three is contradicted;
- the skill (`0.4.0`) says a cadence trigger makes a pass due and that the pass
  is OBPI work the operator initiates under a feature ADR;
- the attestation of a recurring pass is that OBPI's Gate 5, recorded on the
  ledger.

This is the first of the escalations resolved without amending a REQ: the work
was routed so that the literal assertion stays true.

## Worked example 6 — REQs that assert reaping, after "never evict" (2026-10-18)

The operator ruled that expiry is never an eviction, for the token block as for the
hangar (*"at worst, we book a status at least expiry and notify"*). Six attested
BEHAVIOR REQs under Validated `ADR-0.0.14` and `ADR-0.0.41` literally assert reaping
(`REQ-0.0.14-01-06`, `-01-08`, `REQ-0.0.41-03-02`, `-03-03`, `-03-04`, `-05-02`), and
two SUPPORT REQs name it in documents (`-01-04`, `-03-06`). No surface repair could
keep "stale locks are auto-reaped" true.

It was escalated with three choices, on the worked example 3 precedent: amend in place,
leave as history and drop the `@covers` bindings, or hold the fix. The operator ruled,
verbatim: *"Amend in place (Rec.)"*. So:

- each REQ line keeps its attested text and gains a dated `Amended 2026-10-18` note
  quoting the ruling;
- the covering tests keep their `@covers` tags and assert book-and-announce. Where a
  REQ still holds for the one lock that is reaped, the orphan `mx-session` lock, its
  test was moved onto that lock, so `-03-04`'s fail-closed ordering is still exercised
  and not left passing vacuously;
- `REQ-0.0.41-05-01` (the 50 % warning) and `REQ-0.0.14-01-05` ("exits 0 when held")
  were doctrine-neutral and kept their text: an expired lock is still held;
- `REQ-0.0.41-05-01` and `-05-02` had no `@covers` binding at all (the covering test
  `-05-02` named never existed); the binding was added with the amendment.

## Worked example 7 — a precondition a later rule removed (2026-10-18)

`gz task` resolved a short OBPI id by raw prefix, so a *parked* sibling made it
ambiguous and `gz task start` booked the short form. GHI #1162 had already ruled
that parked and withdrawn siblings are not candidates, and the launcher and
`gz obpi status` follow that rule. Aligning `gz task` with it (the RO-2 inventory's
finding) stranded two tests covering `REQ-0.35.0-15-02` under Completed
`OBPI-0.35.0-15`. They seeded a parked sibling and asserted, as a precondition, that
the short form reached the recorder, then proved the recorder lands on the launch id.

The REQ asserts that a boundary is readable however its command spelled the OBPI, and
that is doctrine-neutral: it still holds. Only the fixture's way of producing the
short form was gone. Brought to the operator because the ADR is frozen, it was ruled,
verbatim: *"Re-seat the fixture (Rec.)"*. So:

- both tests seed an *active* sibling with its brief on disk, the case GHI #653 still
  refuses to guess between, and keep asserting the short form reaches the recorder and
  lands on the launch id;
- their `@covers("REQ-0.35.0-15-02")` bindings, the brief and the REQ text are untouched;
- the reason is recorded in the fixture helper's docstring
  (`tests/test_pipeline_position.py`, `_seed_an_active_sibling`).

## What this is not

- **Not GHI #611** (open) — that covers undoing agent or human *error*. Here
  the attestation was **correct when made**; a later ruling retired its
  subject. Nothing needs undoing. Same neighbourhood — append-only
  corrections to attested canon — different premise.
- **Not `gz obpi repudiate` or `gz obpi withdraw`.** Per
  `AGENTS.md` § Gate Covenant (withdraw vs repudiate), repudiate is for
  a fraudulent or invalid completion and withdraw is for an OBPI that is no
  longer needed. This completion was neither.
- **Not an ADR amendment.** The ADR is terminal. That is the premise, not an
  obstacle to route around.

## Related

- GHI #823 — the class; this document is its discharge
- GHI #819 — closed 2026-08-18; the instance the class was named in
- GHI #611 — open; adjacent, see § What this is not
- GHI #804 — open; adjacent on attested-REQ lifecycle (an attested deferred
  frontier with no owner)
- `ADR-0.0.37-constitutional-invariant-composition` § Terminal Disposition —
  terminal 2026-07-18; the source of both known instances
- [`docs/governance/req-scope-discipline.md`](req-scope-discipline.md) — REQ
  kinds and proof channels at authoring time; this document covers the
  post-attestation case that one does not
