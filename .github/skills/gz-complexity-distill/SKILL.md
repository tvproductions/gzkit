---
name: gz-complexity-distill
description: Run a complexity distillation pass against the exemplar corpus to refresh distilled-characteristics doctrine. Use when the operator says "run distillation", "refresh complexity corpus", or "distill complexity" — and at the cadence triggers below (annual calendar, advisor verdict-frequency drift > 25% from baseline, or operator judgment for a ground-breaking project).
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-05
metadata:
  skill-version: "0.2.0"
  govzero-framework-version: "v6"
  govzero_layer: "Layer 3 - File Sync"
gz_command: complexity distill
model: opus
---

# gz-complexity-distill

Operator-runnable skill that produces a dated distilled-characteristics
document by measuring the gzkit exemplar corpus and joint-authoring the
output with the operator. The skill is the canonical operator surface for
the four-ADR complexity-doctrine cluster's distillation cadence
(ADR-0.0.27 → ADR-0.0.28 → ADR-0.0.29 → ADR-0.0.30).


> **Self-Escalation (opus-tier).** Spawn an `Agent` with `model="opus"` to execute this skill. Pass the operator's request verbatim, any relevant context (ADR IDs, OBPI IDs, design topic, prior decisions), and instruct the subagent to read `.gzkit/skills/gz-complexity-distill/SKILL.md` for the full workflow. Relay the subagent's output to the operator.

## When to Use

Three triggers, any of which fires a distillation pass:

1. **Annual calendar (default).** Re-distillation runs once per year.
   Rationale from ADR-0.0.27 § Decision Cadence: the Python ecosystem
   evolves on roughly annual cycles; semi-annual is over-eager,
   biennial risks doctrine staleness.
2. **Drift signal — advisor verdict-frequency drift > 25% from the
   baseline of the last distillation.** Minimum re-distillation interval
   of 6-month to prevent thrashing. The drift comparison is against the
   distilled-characteristics baseline, not the raw measurement
   distributions.
3. **Operator judgment.** The operator may also trigger ad-hoc when a
   ground-breaking project emerges that warrants corpus amendment.

The cadence is itself amendable per OBPI-0.0.27-01's protocol; this skill
mechanizes the cadence the parent ADR codifies.

## Corpus

The corpus list, per-project path filters, pinned commit SHAs, and
rationale for inclusion are the single source of truth at
`data/exemplar_corpus.json`. This skill does not duplicate that content —
it cites the file by path and lets the destination CLI verb load the
canonical model (`gzkit.models.exemplar.load_corpus`).

The corpus is operator-curated against the auditable selection
methodology codified at `.gzkit/rules/complexity-doctrine.md`. Per-project
path filters declare which paths enter the measurement set and which are
excluded with rationale (strategically-complex modules — Django ORM
query compiler, mypy unification core — are correctly excluded).

## Methodology

Distillation is an **agent-drafted, operator-attested ceremony**, not a
black-box pipeline. The seam is canonical to gzkit's Operator Economy of
Effort doctrine: the agent produces the substantive draft against
observed evidence; the operator audits, adds the practitioner-eye
observation per metric, and attests at Gate 5.

The six-step joint authoring sequence (binding, from ADR-0.0.27
§ Decision):

1. Agent runs the measurement pipeline against the pinned-SHA corpus and
   loads the resulting baseline artifact at
   `docs/governance/complexity/baselines/{YYYY-MM-DD}/baseline.json`.
2. Agent drafts metric-aggregate prose per canonical metric (median,
   p75, p90, p95, p99 with inter-project variance commentary).
3. Operator adds the **Practitioner-eye observation** per metric. The
   agent never fabricates this block — it is the OEE seam.
4. Together, agent + operator author the per-metric triple: numeric
   boundary (percentile-of-corpus + absolute-number-at-that-percentile),
   qualitative band (comfortable craft / investigate / refactor),
   doctrinal frame (Fowler / Martin / Page-Jones / Constantine).
5. Agent proposes classifier rule-table updates against the new
   percentiles; operator audits.
6. Agent narrates the diff against the prior distillation (no-op on
   first run) — any boundary that moved > 10% gets explicit operator
   narration.

The output document conforms to the **OBPI-0.0.27-04** brief shape: a
dated distilled-characteristics document at
`docs/governance/complexity/distilled-characteristics-{YYYY-MM-DD}.md`
with frontmatter (`corpus_revision`, `baseline_artifact_path`,
`distillation_date`, `prior_distillation_path`), a per-metric section for
each canonical metric, a "Diff against prior distillation" section, and a
"Citation form" section quoting the citation contract. Previous
distillations are never overwritten — every run produces a new dated
document.

## Output Contract

The destination CLI verb writes a new dated distilled-characteristics
document under `docs/governance/complexity/`. Form on stdout: a
human-readable progress summary naming the corpus revision under
measurement, the baseline artifact path produced, the destination
document path written, and the count of per-metric sections rendered.
Exit 0 on a clean run; exit 3 (policy breach) when the run would
overwrite an existing same-date document (REQ-0.0.27-04-05 no-overwrite
guard); exit 1 on user/config error; exit 2 on system/IO error.

The destination document conforms to OBPI-04's contract: frontmatter,
per-metric triples, cold-start or diff section, citation form. Downstream
foundation ADRs (0.0.28 / 0.0.29 / 0.0.30) cite the document — not the
raw distributions and not the corpus directly — by `(file path, section
anchor, corpus_revision)` tuple.

## Workflow

The operator runs:

```bash
uv run gz complexity distill --corpus data/exemplar_corpus.json
```

The verb composes the OBPI-0.0.27-03 measurement pipeline with the
OBPI-0.0.27-04 distillation render and writes a dated
`distilled-characteristics-{YYYY-MM-DD}.md` under
`docs/governance/complexity/`. Operator follow-up at Gate 5 fills the
per-metric **Practitioner-eye observation** placeholders the verb
leaves intact (REQ-0.0.27-04-10 — the OEE seam, the agent never
fabricates that block).

Common invocations (full options + exit codes in the
[`gz-complexity-distill` manpage](../../docs/user/manpages/complexity-distill.md)):

```bash
uv run gz complexity distill                    # default run against canonical corpus
uv run gz complexity distill --no-prior         # cold-start (skip prior auto-detect)
uv run gz complexity distill --allow-dated-sibling   # write -1 sibling on collision
```

The verb closed the OBPI-0.0.27-06 waiver path tracked by GHI #400.

## References

- **Parent ADR:** ADR-0.0.27 — Exemplar Corpus Doctrine
  (`docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/`)
- **Brief:** OBPI-0.0.27-06-distill-skill
- **Producer brief:** OBPI-0.0.27-04-distillation-pass — defines the
  output document shape this skill is bound to produce
- **Engine:** `src/gzkit/complexity/distillation.py` — the distillation
  rendering surface (frozen Pydantic models + render functions)
- **Corpus:** `data/exemplar_corpus.json` — the pinned-SHA corpus
- **Doctrine rule:** `.gzkit/rules/complexity-doctrine.md` — selection
  methodology, cadence, citation contract
- **Vendor mirror sync:** `.gzkit/rules/skill-surface-sync.md` — edit
  this canonical file; vendor mirrors at `.claude/skills/`,
  `.agents/skills/`, `.github/skills/` are emitted by
  `gz agent sync control-surfaces`
- **Output Contract invariant:** `.gzkit/rules/tool-skill-runbook-alignment.md`
  Invariant 3 — destination verb's default form must honor this skill's
  Output Contract section
