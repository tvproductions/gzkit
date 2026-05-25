# PRIME DIRECTIVE (OWNERSHIP) — Rationale, Examples, and Anti-Rationalizations

*Lifted from `AGENTS.md` § PRIME DIRECTIVE (OWNERSHIP) under
OBPI-0.0.54-02. The binding bullets remain canonical in `AGENTS.md`; this
file preserves the verbatim examples and anti-rationalization catalog so
the AGENTS.md surface stays a map of bullets, tables, and canonical links
per the map-not-encyclopedia doctrine (ADR-0.0.54).*

## Anchor in AGENTS.md

The PRIME DIRECTIVE in `AGENTS.md` enumerates six binding rules:

1. **YOU OWN THE WORK COMPLETELY.** No deferral, no rationalized incompleteness.
2. **COMPLETE ALL WORK FULLY.** Fix broken/misaligned things immediately.
3. **NEVER SAY:** "out of scope", "skip for now", "someone else's problem", "leave as TODO"
4. **SCOPE EXPANSION IS NOT SCOPE CREEP.** If fixing requires updating 3 docs, do it.
5. **FLAG DEFECTS, NEVER EXCUSE THEM.**
6. **EVERY DEFECT MUST BE TRACKABLE.** In-scope → fix immediately. Out-of-scope → use one of these in **priority order**: file a GHI via `/ghi-author` (never `gh issue create` directly — see § Behavior Rules — Always #13), append to `.gzkit/insights/agent-insights.jsonl`, or note in the brief's evidence section. Untrackable defect = nonexistent defect.

The remainder of this document is the verbatim rationale, examples, and
anti-rationalization catalog that previously lived inline in AGENTS.md.

## Worked examples for rule 2 — "COMPLETE ALL WORK FULLY"

   - Code change with output format change → update ALL doc examples; commit together
   - Documentation references a feature → manpage EXAMPLES section shows real CLI output
   - Tests pass but unrelated lint error found → fix it before declaring complete
   - Markdown invalid in a file you didn't edit → fix it; code quality is shared

## Anti-rationalizations catalog for rule 5 — "FLAG DEFECTS, NEVER EXCUSE THEM"

   - "Pre-existing" → still a defect
   - "Not in scope" → flag and expand, or file GHI
   - "Template has drifted" → drift is a defect
   - "Evidence unavailable" → missing evidence is a verification-chain defect

## Related

- `AGENTS.md` § PRIME DIRECTIVE (OWNERSHIP) — the binding bullets
- `AGENTS.md` § DO IT RIGHT (CRAFTSMANSHIP MAXIM) — the operational counterpart
- `docs/governance/agent-contract-rationale.md` — broader rationale and pedagogy
- `ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine` — parent ADR for this lift
