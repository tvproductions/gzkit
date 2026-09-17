# Recommendation — 2026-09-17 (operator-on-demand run)

A dated record. Nothing below has been applied; every row waits on the operator's ruling (CHORE § 4).
Byte figures are measured from `AGENTS.md` at HEAD `096e6bda3` with `section_coverage` /
`generate_candidate`; "after" figures are estimates until the candidate is drafted.

## Surface 1 — root `AGENTS.md` (48,511 B)

### What bounds it

| Quantity | Bytes | Source |
|---|---|---|
| Rendered today | 48,511 | `wc -c AGENTS.md` == `root.md` |
| `tier: invariant` floor, 71 live entries | 25,006 | `invariant_entries(load_corpus(...))` |
| of which the 17 entries ≥ 500 B | 17,208 | same |
| Generated-mode candidate (corpus entries + structure + unowned carried forward) | 31,902 | `generate_candidate(root, 'AGENTS.md', 'root')`, nothing written |
| Rendered text no live corpus entry carries | ~22,600 | 48,511 − 25,360 − structure |
| Hard lower bound under the verbatim floor (every non-corpus line deleted, 22 headings kept) | ~25,900 | floor + headings + separators — deletes witnessed rules; not a target |

Generated mode is not usable as the landing path today: it drops 16,609 B of rendered text inside
sections declared `corpus-owned`, including the Gate Covenant table, the canonical-invocations
table, the defect-fix threshold table, Behavior Rules Always #5/#6/#11–#16 and the mechanical-scopes
list. Those rules have no corpus entry. The landing path is an EXPLICIT candidate (`--candidate`).

No section can be removed: `load_declaration` refuses a declared section absent from the surface and
names no governed recovery (`ownership.py` `_refuse_section_coverage_drift`). All 22 H1/H2 headings stay.

### Conflict to rule on (quoted, not resolved)

- CHORE.md § 3: *"Never include a `tier: invariant` entry as a candidate. Never include a bullet
  scoring Mechanical or Promotable — those are the load-bearing per-turn payload and their retention
  is gated on the scorecard, not author judgment."*
- Operator directive, this session: *"Rule with a mechanical witness (a scorecard Mechanical row, a
  hook, a gz validate scope): keep one line plus the witness name. Delete the explanatory prose from
  the per-turn surface; lift it to docs/governance/ if it is not already there."*

Rows marked **[M]** below compress the wording around a Mechanical bullet while keeping the bullet
and its witness. `gz validate --bullet-retention` requires each Mechanical/Promotable scorecard row's
rule text to remain a substring of the per-turn surface, so each [M] row moves its scorecard row in
the same commit. No row below touches a `tier: invariant` entry.

### Rows (non-corpus text only — valid under any ruling on the floor)

| # | Paragraph | Now B | Class | Disposition | Save B | Lifted text lands |
|---|---|---|---|---|---|---|
| 1 | § Persona — intro + 6-row table | 1,165 | Provenance/reference | Keep the rule sentence ("Every agent frame MUST include a Persona… never generic expertise claims"), the `main-session` line, `gz personas list`. Drop the five subagent rows | ~745 | Already canonical at `.gzkit/personas/`; no lift |
| 2 | § Prime Directive #2 — four "→" sub-bullets | 346 | Worked examples (map-doctrine prohibited shape ii) | Lift | 346 | `agent-contract-rationale.md` § Prime Directive |
| 3 | § Do It Right — closing See-pointer | 264 | Pointer | Tighten to one line | ~110 | — |
| 4 | § Operator Economy — claims 1–6, lead blockquote, See-pointer | 1,502 | Judgment | Keep each bold rule + one clause | ~650 | `agent-contract-rationale.md` § Operator economy (exists) |
| 5 | Behavior Always #11 (insights) | 678 | Promotable | One line + pointer; CLI shape lives in the `gz-insights-remember` skill | ~450 | `agent-contract-rationale.md` § Rule 11 (exists) |
| 6 | Behavior Always #5, #13; Never #5, #7 | 1,178 | Judgment / Redundant (#7 restates Architectural Boundary 6 and governance-core) | One line each | ~490 | `behavior-rules.md` (exists for #13) |
| 7 | **[M]** Behavior Always #12 (`Eval-feedback-source:` trailer) | 316 | Mechanical — `gz validate --commit-trailers` | One line + witness | ~125 | `behavior-rules.md` |
| 8 | § Pattern Discovery | 345 | Redundant with § Execution Rules (`gz state`, `gz status`) | Keep the workflow line and "follow the brief / link to parent" | ~235 | — |
| 9 | § Skills — mirror list + protocol | 600 | Redundant with § Skills First; **defect:** lists `Copilot skill mirror: .github/skills`, a vendor dropped under GHI #921 whose directory does not exist | Keep canonical path, `gz skill list`, sync line | ~400 | — |
| 10 | **[M]** § Kinds — "Mechanical enforcement" 4 bullets | 701 | Redundant — the invariant `foundation CLOSED` entry directly above already names `gz plan create`, `gz adr promote`, `gz validate --taxonomy` | Keep one line for the schema enum + `--taxonomy` assertions | ~550 | `gate-covenant` rationale in `agent-contract-rationale.md` |
| 11 | § Universal OBPI Attestation subsection | ~990 | Redundant ×4 — restates § OBPI Acceptance ¶1, Never #1/#8, governance-core "Do not bypass Gate 5", gate5-covenant Do-Not #3 | One line for the three-axes statement + the third-axis pointer | ~630 | `docs/governance/obpi-attestation.md` (named as a lift target in `agents-md-doctrine.md`, never created) |
| 12 | **[M]** REQ-coverage gate ¶ + Pipeline mandate ¶ | 941 | Mechanical (`gz obpi complete` refusal) / Judgment | One line + witness each | ~375 | same page as row 11 |
| 13 | § Execution Rules — `git add -A` ¶ | 266 | Mechanical — `--reuse-verified` | Two lines | ~125 | — |
| 14 | § Attestation — "Locked by…" + See-pointer | 486 | Mechanical — `CANONICAL_STEP_COMMANDS`, `gz arb validate` | Tighten; table stays whole | ~210 | — |
| 15 | § Local Agent Rules — PII bullet, attestation-enrichment bullet, semver-ordering bullet | 1,089 | PII: Judgment + incident narrative; enrichment: Redundant with § Attestation Pattern; ordering: Judgment | PII → prohibition + `g0` + noreply + "overrides contrary templates"; delete enrichment bullet; tighten ordering | ~600 | incident → `agent-contract-rationale.md` |
| 16 | § Governance doctrine surfaces — intro + **[M]** REQ-kind bullet | 748 | Pointer / Mechanical — `--req-kind-discipline` | Tighten; other ten scope bullets are already rule + witness and stay | ~295 | `tests.md` § REQ Scope Discipline already carries the long form |
| 17 | § Control Surfaces — `Updated: 2026-06-14` | 25 | Value in prose (governance-core: illustrative, never authoritative) | Delete the line | 25 | — |

Estimated total: **~6,400 B → AGENTS.md ≈ 42,100 B** with the verbatim floor untouched.

Judgment call inside row 16: three scope bullets (authoring-guide envelope, `AdvisorDiagnosis.proof`,
complexity exemplar corpus — 441 B) bind one code surface each and steer nothing on an ordinary turn.
(A) keep them in root — recommended this run; (B) move each to its path-scoped rule file, which still
satisfies `--bullet-retention` because `.claude/rules/**` counts as per-turn surface; (C) defer to the
next run.

### The floor decision (one decision)

17 invariant entries ≥ 500 B hold 17,208 B — 69% of the floor and 35% of the file. Twelve of them are
§ Operator Doctrine.

| Option | Lands at (est.) | What changes | Route |
|---|---|---|---|
| **A** keep the verbatim floor | ~42,100 B | Non-corpus rows above only | This session |
| **B** amend the floor: corpus keeps verbatim, rendition carries rule + pointer for invariant entries | ~29,700 B (17 entries at ~280 B each) | `--rendition-floor-coherence` and `assert_invariant_verbatim` learn a pointer form; the pointer target is mechanically checked | Validator runtime contract → OBPI under ADR-0.35.0, operator-initiated. No live brief owns the floor rule today (grep of the six live 0.35.0 briefs: -07 cites the module docstring only; -08 consumes `is_graded_rendition`) |
| **C** re-tier by split (existing verbs only) | ~29,700 B | Per entry: `retire` the invariant row, `remember` the same verbatim text as `compressible`, `remember` a one-line rule as `invariant`. 17 attested removals + 34 attested additions | This session, but the long form loses every witness: nothing checks the lifted copy against the corpus, and the floor then guards an agent-drafted line instead of the operator's words |

Δ between A and B/C: ~12,400 B. Neither reaches the 15,000-char destination; that needs whole sections
moved off the per-turn surface by path scope (Gate Covenant/Kinds/OBPI protocol → `docs/design/adr/**`,
Attestation table → the ARB skill), a separate decision.

Recommendation: **A now, B as the correction the operator initiates.** A is a strict subset of B and C,
so nothing landed under A is redone. C buys the bytes today by spending 51 canon changes to route around
a validator — the smallest-vibing-surface test goes against it.

## Findings that need code to move (out of this run's fence — routed, not fixed)

1. **Claude double delivery.** GHI #923 (closed 2026-08-31) added nested `CLAUDE.md` → `@AGENTS.md`
   on the premise that nested rules reached Codex only. Claude already received those rules through
   path-scoped `.claude/rules/*.md`. Measured this session: the same rule text now arrives twice on the
   first edit under a path (e.g. `src/gzkit/commands/**`: nested 47,686 B + mirrors 56,937 B;
   `cross-platform.md` arrives three times). Generator lives in `src/gzkit/rules/__init__.py`.

## Carried to the rules surface (in fence — a rule-file edit, presented with Surface 4)

- `task-discovery.md` is scoped `src/gzkit/**`, `docs/design/adr/**`, `.gzkit/**` while its own
  version note says *"Scoped `src/gzkit/**`"*. 13.9 KB loads on every `.gzkit/` edit.
