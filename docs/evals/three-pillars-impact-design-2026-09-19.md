# Bounded impact assistance: design draft

Dated 2026-09-19, baseline `d6bc23d0ebef83a1b3391c521e35931f5f8013b6`.
Persona: main-session — craftsperson, governance-aware, whole-file reasoning,
direct. Parent: [implementation plan](three-pillars-implementation-plan-2026-09-19.md).
This is an advisory feature proposal, not an initiated ADR or a changed gate.

## Pool disposition — 2026-09-19

Operator g0: **"pool, not feature."** The registered destination is
[ADR-pool.bounded-advisory-impact](../design/adr/pool/ADR-pool.bounded-advisory-impact.md),
under GHI #1053. The design below remains an unimplemented proposal; its
measurements and review are evidence for the proposal, not shipped behavior.
Earlier routing statements below are the dated pre-ruling record. Promotion
and implementation are not initiated by this disposition. Broad proof currency
was separately retained under GHI #1029.

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

The recorded explicit-`src` default lead has now been reproduced and routed to
[GHI #1054](https://github.com/tvproductions/gzkit/issues/1054). Default source
indexing, orphan detection and unified projection ignore configured `lib` source;
an empty decoy `src` even receives complete/fresh fidelity. The earlier measurement
passed its root explicitly and remains valid. #1054 is the bounded correction
to default population selection, separate from #1053's new relationship types.

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

## Concrete product contract — GHI #1053

This section is the proposed design for decision and implementation routing,
not a claim that the command or adapters already exist. It replaces the earlier
three-section sketch with explicit behavior and acceptance boundaries.

### Interface and user workflow

The proposed interface accepts one or more explicit project-relative changed
Python paths. The first release does not infer a Git range or an OBPI allowlist:
those are different selection authorities and would obscure which inputs the
operator actually asked to inspect. Normalize one optional leading `./`, reject
paths escaping the project and identify paths outside the configured scan roots.

Proposed command shape (unbuilt):

<!-- gz-validate-skip: command-shape -->
```text
gz impact <path> [<path> ...] [--depth 1|2] [--json]
```

Depth applies to incoming source/test import expansion: the default is one
import hop, with two import hops explicitly requested and their chain retained.
The known-registry section always includes the mapping plus recognized direct
invocation witnesses, because both are necessary to explain the observed dispatch
relationship. It preserves their two distinct edges; it neither flattens them
into a direct import nor changes import-depth accounting. Text output lists all selected seeds, section
counts, package groups and full consumer-file detail. JSON is the same complete
record, not a different scan or a lossy subset. Ordinary quiet/verbose/debug
handling and exit-code behavior must follow the existing CLI contract when the
feature is authored; this draft does not introduce a second convention.

The operator selects a changed file, inspects found consumers and gaps, then
chooses which surfaces to read or test. The report neither selects proof scope
nor says a change is safe. A command that completed its scan with known gaps
reports those gaps explicitly; a failed or unstable capture cannot emit a
successful report for that seed. Missing/deleted seeds are coverage gaps in the
first release, not claims that deleted code had no consumers. Historical import
resolution would require a separately specified baseline mode.

### Producers and relationship meaning

Build from current bytes rather than a persisted index. Read the configured
source and test roots once, enumerate both populations, hash every input and
verify their membership and bytes again after capture. Include the registry and
producer implementation identities in that snapshot. Discard mixed captures.
Neither filesystem timestamps nor Git HEAD alone identify an uncommitted tree.
Do not import project modules or execute test code merely to discover a link.

| Section | Producer and evidence | Meaning and limit |
|---|---|---|
| Source imports | Existing source parser/coupling assembler, with exact importer location and resolved target | Importer may depend on imported unit. File membership is not proof that every change affects it. Relative/unresolved/dynamic imports remain explicit gaps unless supported and tested. |
| Known CLI registration | Parse the explicit handler-to-module mapping and literal handler uses in CLI parser source | Registry entry → handler module, and invocation site → registered handler. Preserve both witnesses in the chain. Arbitrary strings are not edges; unknown registration shapes are reported. |
| Test consumers | Parse configured test files for resolvable imports and literal subprocess module invocations | Test imports a target or invokes its module entry point. Indirect import chains are depth-labeled. A string appearing in an assertion or fixture alone is not a subprocess invocation. Unknown command construction is a gap. |
| Declared links | Existing explicitly bound requirement anchors or reviewed links with their own provenance | Traceability, not execution dependency. Do not infer document obligations from keyword proximity. Non-code links from the study oracle remain reference evidence until a producer is actually specified. |

Test imports resolve against the same source-module identity map as production
imports. Parsing the test root as an isolated module universe would classify
`gzkit` imports as external and reproduce the omission. Source/test module-name
collisions are reported, not resolved by silently preferring one. Record each
witness's original file-relative location: concatenated CLI source offsets are
not valid locations in an original file.

Subprocess recognition initially accepts only a statically resolved subprocess
call with a determinate interpreter / `-m` / module prefix. Respect imported
aliases and shadowing; unknown working-directory or Python-path changes leave
target resolution uncertain. Recognize actual invocation nodes, never a matching
argument list in fixture data. Parse/read failure in any potential consumer file
is a coverage gap even when the selected source file parses successfully.

Direction is always consumer → consumed subject. The impact query starts at a
changed subject and follows incoming links. A registry mapping and its caller
must remain separate edges, even when rendered together. A caller reached via
an import route does not prove the distinct semantic registry relation was
resolved. The same rule applies to re-exports and subprocess invocation.

### Record model

Use immutable Pydantic models under the standing models rule. No new runtime
dependency is proposed: reuse Pydantic and the existing parser; use stdlib for
hashing, paths, static AST inspection and deterministic serialization.

| Object | Required fields and semantics |
|---|---|
| Capture | Schema/producer version, root configuration, exact seed roster, complete input roster and hashes, capture outcome, parser identities and per-file parse failures |
| Relationship | Consumer path, consumed subject, typed relation, one or more source locations and witness hashes, producer identity; no free-standing claim without a witness |
| Reach result | Seed identity, scan state, direct relationships, optional two-hop chains, unique consumer-file and package counts, complete file list |
| Coverage gap | Population/seed, unsupported or failed relationship class, reason, affected path when known; never silently coerce unknown to an empty success |
| Declared link | Separate origin and kind, artifact identity, source location and freshness basis; never silently mixed into import closure |

Unknown fields are rejected. Relation names and scan outcomes have a closed
vocabulary tied to implemented producers; a future producer versions the
contract when needed. Hashes establish what was read, not whether discovery is
complete. There is no `safe`, `complete_dependencies`, acceptance key or gate
result in this record.

### Display example and boundedness

Design preview for the measured config-path case, not observed runtime output:

```text
Selected: src/gzkit/commands/config_paths.py
Source imports: 0 found within configured production-source population
CLI registration: handler mapping and parser invocation chain witnessed
Tests: direct test-module import witnessed
Other obligations: reviewed manpage/skill/chore links retained separately
Coverage gaps: arbitrary dynamic loading, computed subprocess arguments,
               semantic configuration/data dependencies, external consumers
```

Each positive line expands to the actual paths, locations and relation types.
The first line cannot be reduced to “0 consumers”: other sections contain real
consumers, and unknown classes remain unknown. High-fanout results retain every
file. Package counts summarize navigation; they are not a guarantee of cheap
review and do not hide a truncated tail.

### Semantic acceptance matrix

The following are implementation obligations, not test results from this draft.
Use isolated fixtures whose expected relationships are specified independently
of the discovery implementation, then retain the four real repository cases as
integration evidence.

| Input/change | Required observed result | Negative control |
|---|---|---|
| Literal absolute import, including function-local import | Correct incoming file and exact witness; duplicate symbol edges do not inflate file count | Unrelated module and look-alike string produce no import edge |
| Explicit handler mapping plus literal invocation | Both registry and call-site witnesses lead to the actual target | Unregistered handler name and arbitrary module-looking string produce no verified chain |
| Direct test import | Consumer is found under configured test root | Stale default test tree is outside the configured population |
| Literal subprocess module invocation | Entry-point consumer and invocation witness are reported | Module name occurring only in expected-output text is not an invocation |
| Unsupported relative/import/command construction | Coverage gap remains visible; no completeness claim | Failed parse cannot become a successful empty scan |
| Add, rename or delete a consumer | Roster and resulting relationships change accordingly | Reusing old cached bytes cannot satisfy snapshot identity |
| Producer/config/source/test changes during capture | Mixed capture is discarded or refused | Stable capture returns the same full semantic result |
| High-fanout shared helper | All files retained; package and file counts independently reconstruct | Removing a tail member fails display-accounting verification |
| Multiple distinct selected seeds | Distinct results remain attributed to their seeds | A constant artifact ancestor chain cannot satisfy the query |
| JSON versus text rendering | Same seeds, relationships, gaps and full populations | Renderer omission is caught independently of producer tests |

### Alternatives and forced decisions

1. **Import-only view:** rejected as the whole product because the actual
   config-path dispatch case is absent. Retain it as one evidence section.
2. **All-purpose semantic graph:** rejected for this increment. Arbitrary dynamic
   loading, runtime data and cross-tool relationships have no complete independent
   discovery authority here; claiming one would recreate the blind spot.
3. **Typed bounded report:** recommended. Explicit registry and test witnesses
   repair demonstrated omissions in the proposed report while preserving limits.
4. **Narrow acceptance currency with this report:** rejected. Advisory relationship
   evidence cannot certify inputs safe to exclude from a proof or review subject.

The main failure risk is treating a short report as a safety certificate. The
countermeasure is typed evidence and visible missing coverage, not an extra
approval gate. Reversing this feature removes an advisory query; no completion
history or proof identity must be rewritten. The minimum useful release contains
source, registry and test sections plus snapshot/gap accounting together; shipping
only imports would reproduce the already measured false-empty case.

Implementation authoring must decide the registered parent, release placement
and decomposition without bypassing campaign order. Future generic dynamic/data
adapters and any proof-currency authority are separate decisions. No new pool
ADR, orphan OBPI or pipeline stage is created by this design document.

### Review of the validation constraint

Independent review under #1053 distinguished two obligations. ADR-0.37.0
Alternative 2 requires a measured reviewable bound; it does not prescribe a
human timing pilot, participant count or timing threshold. This draft and #1053
subsequently proposed human review-effort measurement as an acceptance criterion.
It is not an immutable ADR requirement and must not be cited as a reason to halt
concrete design or repair work. It also cannot be claimed complete using only
file counts. Its actual observation or explicit disposition remains visible in
the validation work; no timing benefit has been measured.

The validation protocol presents the same four changed-source cases with the
complete import-only and typed reports. Preserve the independent oracle before
review. Record found/missed witnessed consumers, unsupported links identified,
files opened, review elapsed time and the reviewer's final scope decision.
Compare on the same captured bytes, disclose ordering/learning effects, and
report each case separately instead of hiding a missed dispatch chain in an
aggregate score. The high-fanout case must retain every file, so a smaller first
screen cannot manufacture a smaller review population. This is a protocol ready
for observation, not an experiment that has already run.
