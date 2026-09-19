# Bounded impact assistance: design draft

Dated 2026-09-19, baseline `d6bc23d0ebef83a1b3391c521e35931f5f8013b6`.
Persona: main-session — craftsperson, governance-aware, whole-file reasoning,
direct. Parent: [implementation plan](three-pillars-implementation-plan-2026-09-19.md).
This is an advisory feature proposal, not an initiated ADR or a changed gate.

## Proposed product

Given explicitly selected changed source paths, show separately attributed
static importing files, known CLI handler registrations and test consumers. Group
importing files by package with the complete underlying edge list available.
Show declared requirement and document links separately. State what was
scanned, what failed to parse, and which relationship types are unsupported.
The result answers “which relationships were found for these changes?” It cannot
certify that every affected consumer was found.

The initial interface should remain an assessment artifact until the bounding
question is answered and a successor ADR is ruled. Do not add a new CLI command,
airlock gate or acceptance dependency key merely to expose this draft.

## Existing components to reuse

`ontology/source.py` already supplies `CodeCouplingEdge` with importing
`source_path`, `target`, `target_is_unit`, relation and optional symbol.
`SourceAnchorIndex` supplies anchors, coupling edges and parse failures.
`build_source_anchor_index(source_root=..., write=False)` can build from current
bytes without persisting an index. Pass the configured root explicitly: the
helper's own default currently assumes `src`.

For a changed target, select internal edges whose `target` equals its
source-root-relative path. Group by importing file and retain all contributing
relations and symbols. Do not reverse the direction accidentally: imports are
recorded importer → imported unit. Requirement anchors describe source → REQ;
those are declared traceability evidence rather than import dependencies.

`ontology/unified.py` expressly excludes code-coupling edges from its object/link
model. Therefore `reach` on the unified graph is not interchangeable with this
query. No new graph engine is needed to price a direct-consumer view.

Read coverage for this draft: source models and builder/default-root/read helpers,
shared coupling assembly interface, unified module boundary, and ADR-0.37.0's
Alternatives Considered. Independent review additionally confirmed known limits in the parser helpers:
both adapters skip relative imports, the builder scans `*.py`, and its default
adapter is `TreeSitterSourceParser`. Fidelity on the intended population still
requires evaluation; existing adapter availability does not establish complete
import resolution. These limits must appear in the proposed report.

## Required record and display

The proposed artifact must bind:

- Input selection: exact changed paths, configured source root and content
  snapshot identity, including the scanned file roster.
- Producer: parser implementation/version, build outcome and parse failures.
- Relationships: direction, source/target paths, relation and symbol. Validate
  each reported edge against current source before presenting it as a witness.
- Display accounting: unique consumer-file count, package count, displayed count
  and omitted count, with access to the full result. Grouping is presentation,
  not deletion of underlying evidence.
- Limits: dynamic imports, resource files, generated consumers, external tools,
  tests or documents outside the scanned source root, and unresolved targets.

Freshly build for the first evaluation. A persisted index would need a producer
fingerprint and a current-roster check; a timestamp or schema-valid JSON alone
cannot establish currentness. If the tree changes during capture, discard that
capture. No “no consumers” conclusion is allowed for an unscanned changed path
or failed parse.

## Bounding decision and acceptance

ADR-0.37.0 Alternative 2 permits a successor only after the bounding question is
answered. Its 2026-08-15 measurements are historical, not today's result. Price
three views on the same real changes: direct importing files, direct importing
packages with expandable file detail, and two-hop importing files. Measure
result sizes, omissions and reviewer effort; report the full population rather
than choosing a display cap and calling that a bound.

Use the repaired mirror validator and source-root collector as concrete change
seeds, plus a shared high-fanout utility and a source unit with no resolved
internal consumers. The acceptance oracle is an independently read set of
actual consumers, including any indirect consumers intentionally omitted by a
direct view. Compare with the artifact-graph adjacency that ADR-0.37.0 names as
the standing alternative. This is a code-derived comparison, not another model
prompt trial.

| Case | Required observation |
|---|---|
| Different changed units | Different evidence-backed consumer results where actual imports differ; a constant ancestor chain fails. |
| Renamed, added or deleted importing source | Fresh result reflects the new roster; stale cache cannot silently pass. |
| Import through re-export or relative package import | Either correctly resolve the consumer or visibly classify the unsupported relation; never imply complete coverage. |
| Parse failure or change outside scan root | State the affected coverage gap instead of returning a reassuring empty result. |
| Large fanout | Preserve full count/list and compare grouping effort; a hidden truncated tail does not satisfy boundedness. |
| Data/config/test consumer not represented by imports | Retain it in the independent oracle and score the omission; do not quietly redefine impact to exclude it. |

Original recommendation: evaluate package-grouped direct consumers first, with
full file detail retained. The dated measurement below now replaces that next
action; do not repeat the experiment as though it were unperformed. Do not wire it into airlock accounting or use it to preserve proof
currency. Those grant authority that this advisory view cannot establish.

## Routing and recorded residuals

The feature remains within the successor-design condition recorded by
ADR-0.37.0, subject to existing campaign order and operator initiation. The
current repair GHIs close only their two demonstrated defects. This draft
supplies a concrete design and acceptance population for the next authorized
analysis; it does not claim the successor exists or that the feature is built.

The explicit `src` default in the source-index builder is a recorded follow-up
lead. Whether default invocation violates its owner contract requires reading
its callers and original requirements; this draft avoids assuming a new defect
and passes configuration explicitly in its proposed evaluation. It is not
silently folded into the config-path audit repair.

## Measured revision — 2026-09-19

[GHI #1052 measurement](three-pillars-impact-2026-09-19/report.md), on source
baseline `08655b31b854e2f016b53bd638e3423e71936c13`, found direct file counts
9 / 0 / 95 / 0 for the four selected units, reduced to 5 / 0 / 11 / 0 package
groups. Two-hop counts were 27 / 0 / 127 / 0. Full lists are retained. Both
adapters missed the config-path command's live dynamic registry chain; the
source-root scan also excludes test consumers. Package grouping alone therefore
does not meet the intended omission-reduction benefit.

Revise the proposed first product to three typed advisory sections: static
imports, known handler-registry relationships and test consumers. Reuse
`cli/parser_handler_manifest.py`'s explicit module mapping for the second;
resolve actual witnesses rather than assuming arbitrary strings are imports.
For tests, distinguish direct imports from subprocess entry-point witnesses;
retain uncertain semantic/data relationships explicitly. This is a proposed
capability, not an implemented adapter or an assertion of complete coverage.

Acceptance must recover the measured config-path dispatch chain and module-entry
subprocess test witnesses, preserve full high-fanout detail, and expose unsupported
relations. File and package counts are review-burden proxies only. An operator
pilot must still measure review time and actual omissions avoided before the
successor's boundedness claim is accepted. No display cap supplies that proof.

Recommended ruling: approve this revised advisory design direction, retain broad
proof currency, and preserve campaign sequencing. No ADR is booked and no OBPI
is initiated by this draft or its measurement. #1029's design decision and the
#1028 production observation remain separately tracked.
