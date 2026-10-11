# Skill trigger report — 2026-10-10

Chore `skill-trigger-testing`, maintenance visit E. The first report this chore has written; its proofs held only run logs before today.

## Method

A goal basket of 134 synthetic operator goals: for each of the 62 model-invocable skills one true-positive goal and one edge goal, written in operator vocabulary without the skill's name, plus 10 negatives (6 ordinary requests no skill should fire on, 4 goals whose owning skill is user-invoked only and so absent from an agent's listing). The basket was shuffled and given, with the 62 names and descriptions and nothing else, to an independent reviewer that was told to read that one file only and pick one skill or none per goal. Picks were scored mechanically against the key. The eleven user-invoked skills (`disable-model-invocation: true`) are not triggerable by an agent and were not tested as targets.

Every goal's true negatives are the other 61 skills: a wrong pick is a false positive for the skill picked. The CHORE asks for three to five goals per skill; this run used two and says so.

## Result

| Measure | Value |
|---|---|
| True-positive goals picked correctly | 62 of 62 |
| Edge goals picked correctly | 62 of 62 |
| Negatives answered `none` | 9 of 10 |
| Skills graded Strong / Weak / Miss | 62 / 0 / 0 |

**Read the 124 of 124 as a ceiling, not a clean bill.** The goals were written by a session that had just read every description, and one reviewer answered once. An instrument that returns no miss at all is not discriminating at this difficulty. What it does establish: no description is so far from its skill's purpose that a plainly worded goal lands elsewhere. The useful signal is in the reviewer's confidence and its list of pairs it could not tell apart.

## Look-alike pairs (the reviewer's own list, with the goals that exposed them)

| Pair | Goals | What the descriptions fail to say |
|---|---|---|
| `gz-plan` / `gz-adr-create` | G061 (low), G121 (medium) | both say they create ADR artifacts; neither says which handles a pool ADR or a lone ADR without briefs |
| `gz-adr-sync` / `gz-obpi-sync` | G019, G069 (medium) | both reconcile ledger state and an ADR table; ADR-level against brief-level is only implied |
| `gz-state` / `gz-ontology` | G016, G037 (medium) | both claim lineage; "artifact relationships" and "governance shape" read as one graph |
| `gz-adr-audit` / `gz-adr-emit-receipt` | G074 (medium) | the audit description names no trigger beyond "Gate-5 audit templates" |
| `gz-init` / `gz-mx` | G047, G120 (medium) | both claim repair of governance surfaces; neither says when repair means re-initialising and when it means the hangar |

One negative missed: G049, "Governance feels wobbly lately…", belongs to the user-invoked `gz-health-audit`; the reviewer picked `gz-intent-trace` at low confidence. An agent given that goal would reach for a neighbouring skill, since the owning one is not in its listing.

## Per skill

Alignment is the grade above; Confidence is the lower of the reviewer's two confidences for the skill's goals. Contract is a heading census, not a verdict: whether the body has a heading naming its output or terminal state. Regression is empty because this is the first report.

| Skill | Version | Goals Tested | Alignment | Confidence | Contract | Regression |
|---|---|---|---|---|---|---|
| `airlineops-parity-scan` | 1.2.0 | 2 | Strong | high | no heading | first report |
| `ghi-author` | 1.11.0 | 2 | Strong | medium | no heading | first report |
| `ghi-close` | 2.12.0 | 2 | Strong | medium | no heading | first report |
| `ghi-triage` | 5.4.0 | 2 | Strong | high | heading present | first report |
| `gz-adr-audit` | 6.15.0 | 2 | Strong | medium | no heading | first report |
| `gz-adr-closeout-ceremony` | 7.19.0 | 2 | Strong | high | no heading | first report |
| `gz-adr-create` | 6.12.0 | 2 | Strong | high | heading present | first report |
| `gz-adr-emit-receipt` | 1.1.1 | 2 | Strong | high | no heading | first report |
| `gz-adr-evaluate` | 6.8.2 | 2 | Strong | high | no heading | first report |
| `gz-adr-map` | 1.2.2 | 2 | Strong | high | no heading | first report |
| `gz-adr-promote` | 1.8.1 | 2 | Strong | high | no heading | first report |
| `gz-adr-status` | 1.13.1 | 2 | Strong | high | heading present | first report |
| `gz-adr-sync` | 7.1.2 | 2 | Strong | medium | no heading | first report |
| `gz-advisor-qc` | 0.2.0 | 2 | Strong | high | no heading | first report |
| `gz-agent-sync` | 1.3.0 | 2 | Strong | high | no heading | first report |
| `gz-airlock` | 1.2.0 | 2 | Strong | high | heading present | first report |
| `gz-arb` | 1.4.0 | 2 | Strong | high | heading present | first report |
| `gz-check` | 1.6.1 | 2 | Strong | high | no heading | first report |
| `gz-check-config-paths` | 0.2.1 | 2 | Strong | high | no heading | first report |
| `gz-chore-runner` | 1.5.2 | 2 | Strong | high | heading present | first report |
| `gz-cli-audit` | 0.2.0 | 2 | Strong | high | no heading | first report |
| `gz-competitor-radar` | 1.1.0 | 2 | Strong | medium | no heading | first report |
| `gz-complexity-advisor` | 0.2.3 | 2 | Strong | high | heading present | first report |
| `gz-complexity-distill` | 0.3.2 | 2 | Strong | high | heading present | first report |
| `gz-complexity-guide` | 0.2.2 | 2 | Strong | medium | heading present | first report |
| `gz-constitute` | 0.3.0 | 2 | Strong | high | no heading | first report |
| `gz-content-compose` | 1.1.0 | 2 | Strong | high | heading present | first report |
| `gz-content-remember` | 0.2.0 | 2 | Strong | high | no heading | first report |
| `gz-context-diet` | 1.1.2 | 2 | Strong | high | no heading | first report |
| `gz-deps-upgrade` | 1.3.0 | 2 | Strong | high | no heading | first report |
| `gz-design` | 1.9.0 | 2 | Strong | high | no heading | first report |
| `gz-flighttest` | 0.1.1 | 2 | Strong | high | no heading | first report |
| `gz-foundation-triage` | 1.0.3 | 2 | Strong | high | heading present | first report |
| `gz-how` | 1.0.1 | 2 | Strong | high | no heading | first report |
| `gz-implement` | 0.2.0 | 2 | Strong | high | no heading | first report |
| `gz-init` | 6.4.0 | 2 | Strong | medium | no heading | first report |
| `gz-insights-remember` | 0.1.1 | 2 | Strong | high | no heading | first report |
| `gz-intent-trace` | 1.0.2 | 2 | Strong | high | no heading | first report |
| `gz-issue-file` | 1.0.3 | 2 | Strong | high | heading present | first report |
| `gz-justify` | 6.4.0 | 2 | Strong | high | no heading | first report |
| `gz-migrate-semver` | 0.2.0 | 2 | Strong | high | no heading | first report |
| `gz-mx` | 1.1.1 | 2 | Strong | medium | no heading | first report |
| `gz-obpi-brief-drift` | 0.8.0 | 2 | Strong | high | no heading | first report |
| `gz-obpi-lock` | 6.3.1 | 2 | Strong | high | no heading | first report |
| `gz-obpi-pipeline` | 6.66.0 | 2 | Strong | high | no heading | first report |
| `gz-obpi-simplify` | 6.1.1 | 2 | Strong | high | no heading | first report |
| `gz-obpi-specify` | 1.9.2 | 2 | Strong | high | heading present | first report |
| `gz-obpi-sync` | 3.4.0 | 2 | Strong | high | no heading | first report |
| `gz-ontology` | 0.1.1 | 2 | Strong | medium | heading present | first report |
| `gz-patch-release` | 1.11.1 | 2 | Strong | high | no heading | first report |
| `gz-plan` | 1.8.0 | 2 | Strong | low | no heading | first report |
| `gz-plan-audit` | 6.5.0 | 2 | Strong | high | heading present | first report |
| `gz-prd` | 0.3.0 | 2 | Strong | high | no heading | first report |
| `gz-pythonic-pattern-apply` | 1.1.0 | 2 | Strong | high | heading present | first report |
| `gz-pythonic-pattern-detect` | 1.1.1 | 2 | Strong | high | heading present | first report |
| `gz-session-handoff` | 7.6.1 | 2 | Strong | high | heading present | first report |
| `gz-skill-review` | 1.0.0 | 2 | Strong | high | no heading | first report |
| `gz-state` | 0.2.0 | 2 | Strong | medium | no heading | first report |
| `gz-status` | 1.7.0 | 2 | Strong | high | no heading | first report |
| `gz-tech-debt-review` | 1.4.0 | 2 | Strong | high | no heading | first report |
| `gz-tidy` | 1.3.0 | 2 | Strong | high | no heading | first report |
| `gz-validate` | 0.2.0 | 2 | Strong | high | no heading | first report |

## Output contracts

44 of 62 model-invocable skills have no heading that names an output, a deliverable or a terminal state. `skill-authoring.md` § What a skill carries says every skill states where it ends. This is a heading census: a skill may state its terminal state under another heading. It is a candidate list for the next skill-body review, not a finding per skill.

## Descriptions with no stated trigger

14 of 62 descriptions carry no "Use when", "Use for" or "Triggers on" clause: `airlineops-parity-scan`, `ghi-author`, `gz-adr-audit`, `gz-adr-closeout-ceremony`, `gz-adr-create`, `gz-adr-evaluate`, `gz-adr-map`, `gz-adr-status`, `gz-adr-sync`, `gz-competitor-radar`, `gz-foundation-triage`, `gz-obpi-sync`, `gz-patch-release`, `gz-session-handoff`. `skill-authoring.md` asks for a one-line description "that says when to reach for the skill and what it produces".

## Proposed description text (step 5; skills are operator-only repair, nothing was edited)

- `gz-plan`: "Record one ADR for a planned change with `gz plan create`: a pool entry, or a lone ADR with no briefs yet. Use when parking or recording architecture intent; use `gz-adr-create` when the ADR's OBPI briefs are authored and booked with it."
- `gz-adr-sync`: lead with "ADR-level reconciliation" and name what it does not touch (brief bodies). `gz-obpi-sync`: lead with "Brief-level reconciliation".
- `gz-state`: "Query parent links and readiness for artifacts with `gz state`". `gz-ontology`: keep, and add "the typed graph, not the readiness view".
- `gz-adr-audit`: "Audit an attested, completed ADR: re-verify its evidence with receipts and emit the validated receipt. Use after the operator has attested the ADR." The present text calls the audit "Gate-5", a name the root contract reserves for the operator's attestation.
- `gz-init`: say "repairing missing scaffolding by re-running init", so that guard-relaxed repair reads as the hangar's.

## Also found

- `gz-deps-upgrade` has frontmatter a strict YAML parser rejects (an unquoted `: ` inside `description:`). gzkit's reader accepts it. If a consumer of skill frontmatter parses strictly, the skill's description does not load and the skill cannot trigger. Not tested against any consumer.

## Limits

One reviewer, one run, two goals per skill, goals authored by a session familiar with the catalog. The next run should source goals from operator phrasing in session transcripts, which the `session-correction-mining` chore already reads, and should repeat picks to measure variance. The basket, the key and every pick are in `trigger-basket-2026-10-10.json`.
