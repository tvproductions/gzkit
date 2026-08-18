# gz content

Authoring CLI for the canonical content model substrate (ADR-0.0.34). The
`gz content` command group lets operators import, list, inspect, render, and
edit per-turn agent control surface files (rules, skills, personas, chores,
handoffs, scenarios, bullets, agent contracts) as canonical Pydantic models.

## Synopsis

```bash
gz content <subcommand> [OPTIONS]
```

## Description

`gz content` is the operator surface for the ADR-0.0.34 rendering substrate.
Per the headless-CMS doctrine, every per-turn agent control surface file is
rendered byte-stably from a canonical Pydantic model via a Jinja2 template.
Operators interact with these models through `gz content`; output is
human-readable prose by default, machine-readable JSON behind `--json`.

The content type registry exposes eight model types:

| Type | Surface |
|------|---------|
| `AgentContract` | `AGENTS.md`, `CLAUDE.md` |
| `Rule` | `.gzkit/rules/*.md` |
| `Skill` | `.gzkit/skills/*/SKILL.md` |
| `Chore` | `.gzkit/chores/*/CHORE.md` |
| `Persona` | `.gzkit/personas/*.md` |
| `Handoff` | `.gzkit/handoffs/*.md` |
| `Scenario` | BDD scenario records |
| `Bullet` | Single-bullet evidence rows |

Round-trip fidelity is binding: `model == parse(render(model))` for every type.

## Subcommands

### import

Read a hand-authored or canonical markdown file, parse it into a Pydantic
content model, and emit JSON to stdout. Optionally re-render the canonical
form to a target path.

```bash
gz content import <file> --as <type> [--write <path>]
```

`--write` persists the re-rendered canonical form to the named path; useful
for the OBPI-0.0.34-03 reverse-parse migration workflow.

### list

Enumerate the registered content model types from the `CONTENT_MODELS`
registry. Default output is a human-readable two-column table; `--json`
emits a machine-readable array.

```bash
gz content list [--type <content-type>] [--json]
```

`--type` filters output to a single type (e.g. `gz content list --type Rule`).

### show

Parse a canonical content file and display a prose summary (type, title,
field-by-field breakdown). The operator-facing surface is always
human-readable; pass `--json` for the canonical `model_dump_json()` form.

```bash
gz content show <file> --as <type> [--json]
```

### render

Parse a canonical content file and emit the re-rendered markdown to stdout.
Output is byte-identical to `gzkit.content.render.render(model, vendor)` for
the same input (round-trip stability per OBPI-0.0.34-02).

```bash
gz content render <file> --as <type> [--vendor <vendor>]
```

`--vendor` defaults to `claude`; other vendors render their respective
templates.

### edit

Open the canonical-form file in `$EDITOR` (or `$VISUAL`). On editor save,
the temp file is re-parsed and re-validated. **Invalid input aborts with
the validator diagnostic and never writes a partial file.** On successful
validation, the original file is atomically replaced with the re-rendered
canonical form via `Path.replace()`.

```bash
gz content edit <file> --as <type> [--vendor <vendor>]
```

The atomic-replace contract means a failed validation (or a non-zero editor
exit) leaves the original file byte-identical to its pre-edit state. There
is no partial-write state.

### remember

Append one addressed, provenanced entry to a surface's **append-only corpus**
store at `.gzkit/corpus/<surface>.jsonl` and emit a `corpus_entry_appended`
ledger event. This is the write path of the ADR-0.0.37 corpus pipeline
(`corpus → compress → rendition → playback`): capture grows the source of
truth; deterministic playback remains the sole writer of rendered surfaces.
**`remember` NEVER edits a rendered surface** (`AGENTS.md`, `CLAUDE.md`, or
any mirror) — that is its load-bearing invariant.

```bash
gz content remember <surface> --section <id> --text <text> \
  [--tier invariant|compressible] \
  [--classification Mechanical|Promotable|Judgment|Ambiguous] \
  [--origin <provenance>]
```

The `--section` value is normalized to the surface's kebab-case section id
(so `"Behavior Rules"` resolves to `behavior-rules`). The command **fails
closed** (non-zero exit, no entry written) when the surface is unknown or the
section resolves to no template-defined section of that surface — an
unaddressable entry is never stored. `--tier invariant` marks entries emitted
verbatim at every compression setpoint; `--tier` defaults to `compressible`.

### retire

Retire a superseded corpus entry by appending a **retraction row** whose
`retires` field names the id it supersedes, and emit a `corpus_entry_retired`
ledger event. The corpus has exactly one mutation — append — and no delete, so
before this verb a superseded operator directive bound the invariant floor
permanently and the only escape was hand-editing the append-only store.

```bash
gz content retire <surface> --entry <id> --reason <text> [--origin <provenance>]
```

**Nothing is deleted.** The retired row stays on disk with its provenance
intact; `tier_policy.invariant_entries` simply stops returning it, so a
rendition no longer has to carry its text verbatim.

**Retirement only ever shrinks the invariant floor.** A rendition that
satisfied the floor before a retirement still satisfies it after — retirement
removes requirements, never adds them — so **committed renditions stay valid
and no recomposition is implied**. `retire` never touches a rendered surface.

The command **fails closed** (exit 1, nothing written) when `--entry` names no
row in the surface's corpus, or when that row is already retired. Double
retirement refuses rather than appending a second retraction, so the ledger
carries exactly one witness per retirement.

### compose

Validate and stage a **candidate rendition** from the corpus. This is the
**compress** stage of the ADR-0.0.37 CMS pipeline
(`corpus → compress → rendition → playback`): the agent wielding the
`gz-content-compose` skill supplies the candidate text; the tool validates
invariant-tier verbatim preservation, computes per-tier byte evidence, writes
the candidate to `.gzkit/renditions/<surface>/<consumer>.candidate.md`, and
emits a `composition_candidate_emitted` ledger event.

**`compose` is deterministic** — NO LLM call, NO network I/O. The
drop/combine/rewrite compression judgment is the agent's.
**`compose` NEVER writes a rendered surface** (`AGENTS.md`, `CLAUDE.md`,
or any mirror) — only the candidate artifact and ledger change.

```bash
gz content compose <surface> --consumer <vendor> --candidate <file>
gz content compose AGENTS.md --consumer codex --candidate /tmp/candidate.md
cat /tmp/candidate.md | gz content compose AGENTS.md --consumer codex
```

The command **fails closed** (non-zero exit, no candidate written) when:
- the corpus store for `<surface>` does not exist,
- the `(surface, consumer)` setpoint is undeclared in `data/vendor-manifest.json`, or
- the candidate drops or rewrites any `tier: invariant` corpus entry (0-Kelvin floor).

### commit

Promote a staged **candidate** to the durable **committed rendition** under
operator attestation. This is the governed candidate→committed seam of the
ADR-0.0.37 CMS pipeline: `compose` stages `<consumer>.candidate.md`; `commit`
writes `<consumer>.md` AND freezes the corpus content-fingerprint in a
provenance sidecar `<consumer>.corpus.json`, then emits a `rendition_committed`
ledger event.

**`commit` is operator-attested (corpus attestation, NOT Gate 5)** — `--attestor` and `--attestation-text`
are required and **fail closed when empty**; promotion is explicit, never
automatic. The operator's verbatim `--attestation-text` IS the corpus attestation (mirrors
`gz obpi repudiate`). The frozen fingerprint is exactly what
`gz validate --rendition-freshness` compares the live corpus against: when the
corpus drifts from the committed rendition, the freshness gate flags it and the
recovery is to recompose and re-commit.

```bash
gz content commit <surface> --consumer <vendor> --attestor "<name>" --attestation-text "<verbatim>"
gz content commit AGENTS.md --consumer codex \
  --attestor "g0" --attestation-text "attest completed"
```

The command **fails closed** (non-zero exit, nothing written) when:
- `--attestor` or `--attestation-text` is empty or whitespace (corpus attestation),
- no staged candidate exists for `(surface, consumer)`, or
- no corpus store exists for `<surface>` (nothing to fingerprint).

### advise-rendition

Record an advisory **information-retained-per-byte** verdict for a candidate
rendition. This is the **advisor-QC** stage of the ADR-0.0.37 CMS pipeline
(`corpus → compress → advisor-QC → operator attest → committed rendition → playback`):
the agent wielding the `gz-advisor-qc` skill judges how much information the
candidate retains per byte, and records that verdict as an ARB receipt the
operator cites at Gate 5.

**`advise-rendition` is deterministic** — NO LLM call, NO network I/O. The
LLM-as-judge read is the agent's; the tool validates the verdict shape
(explanation-before-verdict), writes the `arb-step-judge-<hash>` ARB receipt,
and emits a `rendition_advisor_verdict` ledger event.

**`advise-rendition` is advisory, never gating** (ADR-0.0.39 Evidentiary
invariant): ANY score is recorded and the command exits 0 — a low retention
score is evidence for the operator, never a fail-closed gate.

```bash
gz content advise-rendition <surface> [--consumer <vendor>] --score <0.0-1.0> --explanation "<reasoning>"
gz content advise-rendition AGENTS.md --consumer codex --score 0.94 \
  --explanation "All Mechanical bullets retained; two Promotable bullets combined without information loss."
```

The command **fails closed** (non-zero exit, no receipt written) only when the
`--explanation` is empty or whitespace — a structurally malformed verdict. The
verdict value itself is never the fail-closed trigger.

## Options

| Flag | Applies To | Description |
|------|-----------|-------------|
| `--as <type>` | import, show, render, edit | Content type name (required for these subcommands) |
| `--type <type>` | list | Filter list output to a single registered type |
| `--json` | list, show | Emit JSON to stdout instead of human-readable prose |
| `--write <path>` | import | Write re-rendered canonical form to this path |
| `--vendor <vendor>` | render, edit | Target vendor template for re-rendering (default: `claude`) |
| `--section <id>` | remember | Target section id or title; normalized to the surface's kebab-case Pillar id (required) |
| `--text <text>` | remember | The entry prose to remember (required) |
| `--tier <tier>` | remember | `invariant` (verbatim at every setpoint) or `compressible` (default) |
| `--classification <c>` | remember | Advisory-scorecard class: `Mechanical`/`Promotable`/`Judgment`/`Ambiguous` (default `Ambiguous`) |
| `--origin <provenance>` | remember | Provenance of the capture, e.g. a GHI or session id (default `cli:content-remember`) |
| `--consumer <vendor>` | compose, commit, advise-rendition | Target vendor consumer (e.g. `codex`, `claude`); optional for advise-rendition (surface-wide when omitted) |
| `--candidate <file>` | compose | Path to the candidate rendition file (reads from stdin when omitted) |
| `--attestor <name>` | commit | Operator attesting the corpus delta this promotion renders; empty fails closed (required) |
| `--attestation-text <text>` | commit | Operator's verbatim corpus-attestation token; empty fails closed (required) |
| `--score <float>` | advise-rendition | Information-retained-per-byte verdict value; advisory, never gates (required) |
| `--explanation <text>` | advise-rendition | The advisor's reasoning, recorded before the verdict; empty value fails closed (required) |
| `--quiet`, `-q` | global | Suppress non-error output |
| `--verbose`, `-v` | global | Enable verbose output |
| `--debug` | global | Enable debug mode with full tracebacks |
| `--help`, `-h` | global | Show help and exit |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error (unknown type, missing `$EDITOR`, parse error, validation error, missing file) |
| 2 | System/IO error (filesystem unreadable, atomic-replace failed) |
| 3 | Policy breach (reserved; not currently emitted by `gz content`) |

## Examples

```bash
# Enumerate registered content types (human-readable table)
uv run gz content list

# Filter to a single type
uv run gz content list --type Rule

# Machine-readable form
uv run gz content list --json

# Inspect a rule file (prose summary)
uv run gz content show .gzkit/rules/tests.md --as Rule

# Machine-readable inspection
uv run gz content show .gzkit/rules/tests.md --as Rule --json

# Render the canonical form of a file to stdout
uv run gz content render AGENTS.md --as AgentContract

# Render against a specific vendor template
uv run gz content render .gzkit/rules/tests.md --as Rule --vendor claude

# Edit a rule with validation guard (invalid edits never land)
EDITOR=vim uv run gz content edit .gzkit/rules/tests.md --as Rule

# Reverse-parse a hand-authored file and write canonical output (OBPI-0.0.34-03)
uv run gz content import AGENTS.md --as AgentContract --write /tmp/agents-canonical.md

# Capture a compressible note into the AGENTS.md corpus (never touches AGENTS.md itself)
uv run gz content remember AGENTS.md --section "Behavior Rules" \
  --text "Prefer stdlib JSONL for append-only stores." --tier compressible

# The append landed in the corpus store, not the rendered surface:
#   .gzkit/corpus/AGENTS.md.jsonl  ← new entry
#   AGENTS.md                       ← byte-unchanged

# Record an advisory info-retained-per-byte verdict for a candidate rendition (advisory, never gating)
uv run gz content advise-rendition AGENTS.md --consumer codex --score 0.94 \
  --explanation "All Mechanical bullets retained; two Promotable bullets combined without information loss."

# The verdict is witnessed in the ledger and written as an ARB receipt cited at Gate 5:
grep "rendition_advisor_verdict" .gzkit/ledger.jsonl
```

## Files

| Path | Role |
|------|------|
| `src/gzkit/content/models/` | Canonical Pydantic model definitions (`AgentContract`, `Rule`, `Skill`, …) |
| `src/gzkit/content/templates/` | Jinja2 templates per (content type × vendor) |
| `src/gzkit/content/render.py` | Render pipeline (OBPI-0.0.34-02) |
| `src/gzkit/content/parse.py` | Reverse-parse pipeline (OBPI-0.0.34-03) |
| `src/gzkit/commands/content/` | Operator CLI surface (this OBPI-0.0.34-04) |
| `src/gzkit/content/corpus_store.py` | Append-only per-surface corpus persistence (`remember`, OBPI-0.0.37-19) |
| `.gzkit/corpus/<surface>.jsonl` | Append-only corpus store written by `gz content remember` |
| `src/gzkit/content/advisor_qc.py` | Deterministic advisor-QC verdict-record engine (`advise-rendition`, OBPI-0.0.37-24) |
| `artifacts/receipts/arb-step-judge-<hash>.json` | Advisor-QC verdict ARB receipt cited at Gate 5 |

## Related

- ADR-0.0.34 — Agent Control Surface Rendering Substrate (`docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/`)
- Doctrine — `docs/governance/agent-control-surface-rendering-substrate.md`
- OBPI-0.0.34-01 — Content model registry generalization
- OBPI-0.0.34-02 — Rendering pipeline
- OBPI-0.0.34-03 — Reverse-parse migration tooling
- OBPI-0.0.34-04 — Authoring CLI (this manpage)
- OBPI-0.0.34-05 — Light TUI affordances (forthcoming)
- OBPI-0.0.34-06 — Validation hooks (forthcoming)
- ADR-0.0.37 — Constitutional Invariant Composition; the `remember` corpus-capture write path (OBPI-0.0.37-19)
- `.gzkit/skills/gz-content-remember/SKILL.md` — the capture skill that wields `gz content remember`
