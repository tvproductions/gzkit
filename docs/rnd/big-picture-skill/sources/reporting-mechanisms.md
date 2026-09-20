# Existing reporting, retention, and ledger mechanisms

Research date: 2026-09-19. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct. Provenance: R&D run `big-picture-skill`. This report records source inspection, not execution or a design ruling. No report producer, retention command, OBPI, or ledger mutation was run. Only this research source was written.

## Findings

### 1. A dated report series already has a useful local precedent

The canonical competitor-radar skill says:

> “`artifacts/reports/competitor-radar/registry.json` and monthly scan JSON files govern the Markdown. Markdown reports under `artifacts/reports/competitor-radar/` are generated projections and must not be hand-edited.”

Source: [competitor-radar skill](../../../../.gzkit/skills/gz-competitor-radar/SKILL.md), read 2026-09-19.

I read its complete [radar.py](../../../../.gzkit/skills/gz-competitor-radar/scripts/radar.py). It implements monthly scan JSON, stable monthly report names, a generated index, a SHA-256-derived source checksum, and exact comparison of rendered Markdown against current JSON. `new_scan()` refuses an existing monthly source unless overwrite is explicitly requested. `render_all()` regenerates every historical report from its scan and the CURRENT registry. It performs no ledger append and has no publication or archival event producer.

Interpretation: reuse the separation of authored material, rendering, and index; do not claim this is immutable publication history. Updating its shared registry changes regenerated past reports. A big-picture report that preserves what was believed at a particular time needs its historical interpretation and supporting context preserved deliberately.

### 2. The radar is explicitly not an adopter-ready implementation

Its frontmatter says:

> “Withheld from delivery: this radar judges candidates by whether they name a gzkit-relevant strength and recommends gzkit governance moves, and the wheel ships only `src/gzkit/skills/**/*.md`, so its scripts never arrive (GHI #915).”

Source: [competitor-radar skill](../../../../.gzkit/skills/gz-competitor-radar/SKILL.md), read 2026-09-19. The package-data declaration in [pyproject.toml](../../../../pyproject.toml) includes `src/gzkit/skills/**/*.md`.

The skill is marked `project_local: true`. Its code has gzkit-specific destination fields and project-root assumptions. It is a design precedent, not a portable publication service that can simply be invoked by the proposed skill. This delivery constraint is already tracked by the cited GHI; this research makes no new defect finding or assertion about that issue's live state.

### 3. Retention code supplies safety precedents, not a generic report rotator

I read the complete [handoff archive runtime](../../../../src/gzkit/handoff_archive.py), [command adapter](../../../../src/gzkit/commands/handoff_archive.py), and [ARB archive runtime](../../../../src/gzkit/arb/archive.py).

Handoff archive declares:

> “Selects handoffs older than a threshold that are safe to relocate from `.gzkit/handoffs/` into `.gzkit/handoffs/archive/`, honoring guards so the audit trail is preserved by relocation, never removal”

The implementation protects both ends of handoff chains, recorded lock-release citations, undatable files, and occupied destinations. It classifies first, then uses a no-clobber link/unlink relocation. Its documented owner is ADR-0.0.65, OBPI-05. Its command adapter supports dry-run and JSON output, and does not append an archive event.

ARB archive declares:

> “never archive a receipt whose id is cited anywhere in the ledger.”

And:

> “Age is read from the receipt's own `timestamp_utc` field, never `mtime`”

Its documented owner is GHI #594. It protects foreign receipt types and cited evidence, skips undatable records, and moves rather than deletes. Its retention functions read ledger citations but do not emit ledger events.

Interpretation: stable identity, preserved citations, authored timestamps, and non-destructive history are useful precedents. These implementations have domain-specific paths and guards. They cannot be called on arbitrary narrative reports. An index that advances the prominent report while leaving historical reports in place could avoid physical relocation entirely; that remains a design choice, not an existing generic facility.

### 4. Existing automatic ledger edit recording does not cover arbitrary report paths

I read [commit_ledger.py](../../../../src/gzkit/hooks/commit_ledger.py) in full, the `GOVERNANCE_PATTERNS` and `is_governance_artifact()` definitions in [hooks/core.py](../../../../src/gzkit/hooks/core.py), and the `artifact_edited_event()` factory in [ledger_events.py](../../../../src/gzkit/ledger_events.py).

The commit recorder describes its coverage limit:

> “A write that is never committed stays invisible — the commit is the state this observes, and an uncommitted edit has no state to observe.”

Its classifier accepts selected PRD, constitution, ADR and OBPI Markdown directories plus root AGENTS.md and CLAUDE.md. Neither `docs/rnd/` nor `artifacts/reports/` matches those declared patterns. The recorder deduplicates against prior tool-locus events, then appends an `artifact_edited` row with the path and optionally commit/session. This event witnesses an edit; it does not encode a reporting period, publication identity, predecessor, or report-content digest.

Consequently a saved report must not be described as ledger-published merely because it was committed. This is a concrete design constraint for the user's ledger requirement, not grounds to widen the classifier silently.

The inspected `audit_generated_event()` and `audit_receipt_emitted_event()` factories are ADR-specific. Their fields and semantics are not a generic narrative-report publication mechanism. This research has not established a suitable existing generic publication producer; it does not prove that no such mechanism exists anywhere in the repository.

### 5. The reporter package is a rendering utility, not this narrative capability

I read the complete package entry point, presets, panels, [reporter architecture documentation](../../../user/concepts/reporter-architecture.md), and [reporter pool ADR](../../../design/adr/pool/ADR-pool.reporter-rendering-infrastructure.md).

The implemented package states:

> “Pure rendering layer: data in, Rich renderables out. No IO, no ledger, no business logic.”

It provides four concrete Rich table/panel functions. The pool document names a wider migration program, but its frontmatter remains `status: Pool`; the existence of some rendering code is not evidence that the whole pool program completed. Nothing about a high-altitude narrative skill requires initiating that pool work.

### 6. Ledger-backed provenance and narrative truth are different claims

[State doctrine](../../../governance/state-doctrine.md) says:

> “Authority: Defines *what has happened* — the runtime truth for status and completion.”

It describes Layer 3 as:

> “Caches, indexes, markers, and computed artifacts that are derived from L1 and L2. Deletable and rebuildable.”

A saved model interpretation is not reproducible merely by rerunning the model. Preserving the exact report permits later examination of what it claimed. A current-report index can be rebuilt; an earlier assessment needs retained source content. A ledger event can witness that content's publication without certifying the architectural judgment as correct. These are design implications of the observed mechanisms, not a new state-doctrine ruling.

## Consequences for the design discussion

A skill/docs outcome is a valid independent R&D disposition. It can define the perspective, evidence practices, narrative format, and report-history expectations without assuming an ADR or initiating one. The operator has already supplied that direction.

The persistent reporting lifecycle and ledger requirement should remain explicit in the problem definition. Existing mechanisms offer reusable patterns, but none inspected supplies the whole combination of portable narrative skill, retained assessments, rotation, and publication provenance. Avoid disguising an ADR attestation as report publication, claiming automatic ledger coverage that does not apply, or copying the project-local radar wholesale. Any eventual mechanism choice must be evaluated separately against its actual scope and existing owners.
