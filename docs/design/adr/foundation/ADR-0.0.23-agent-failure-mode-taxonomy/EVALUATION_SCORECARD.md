ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.23-agent-failure-mode-taxonomy
Evaluator: main-session (manual scorecard supersedes deterministic CLI pre-screen)
Date: 2026-04-30

--- CLI Pre-Screen (traceability only) ---

| Source | Verdict | Weighted Total |
|--------|---------|----------------|
| `gz adr evaluate ADR-0.0.23` (deterministic) | GO | 3.25 / 4.0 |

CLI flagged Dim 1 = 1 ("no before/after language in Intent") and Dim 8 = 1
("no source file path references / exemplar language / anti-pattern guidance
in ADR"). Both are heuristic false negatives; reconciliation per dimension
below. Manual scorecard authoritative.

--- ADR-Level Scores (manual, authoritative) ---

| # | Dimension | Weight | Score (1-4) | Weighted | Rationale |
|---|-----------|--------|-------------|----------|-----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | Intent names the gap concretely ("each new rule re-invents the failure shape it backstops, and `gz validate --advisory-scorecard` cannot score new rules against a canonical catalogue") and Consequences § Positive states the after state. CLI heuristic looked for literal before/after framing in Intent and missed it; the content exists, distributed across Intent + Consequences. Not 4 because the before/after is not quantified (no metric on rule re-invention rate). |
| 2 | Decision Justification | 15% | 4 | 0.60 | Five numbered decisions. Items 1-3 trace to the canonical-rule + cross-link + mirror-sync doctrine. Item 4 explicitly justifies the lane lift to heavy by citing `.gzkit/rules/cli.md` (new CLI verb trigger). Item 5 lands inside item 4's heavy envelope without further lift, justified explicitly. Alternatives Considered names three rejected paths (inline in AGENTS.md, docs-only page, defer until third source) with specific reasons. Internally consistent. |
| 3 | Feature Checklist Completeness | 15% | 4 | 0.60 | Five items, each maps 1:1 to an OBPI brief with no gaps in numbering. Each item is independently valuable: 01 the rule, 02 visibility, 03 mirror reach, 04 closes GHI #316, 05 closes GHI #309. Granularity consistent. 1:1 ADR↔OBPI sync mandate honored. |
| 4 | OBPI Decomposition Quality | 15% | 3 | 0.45 | Boundaries clean: 01-03 form a tight authoring chain, 04 and 05 are independent operationalizations of two of the six patterns. Dependency graph acyclic (01 → 02 → 03; 04 and 05 stand alone modulo soft dependency on 01's taxonomy rule). Numbering has no gaps. Reduced from 4 to 3 because OBPI-04 and OBPI-05 each carry full Heavy-lane envelope (new CLI verb + manpage + BDD + module + unit tests + threshold-data + Pydantic schema), pushing both beyond the 1-3 day work-unit target — a justified compromise (the work cannot meaningfully split further without amputating the heuristic from its threshold config or the wrapper from its provenance trailer), but it costs a point. |
| 5 | Lane Assignment Correctness | 10% | 4 | 0.40 | 01-03 Lite (rule authoring, doc cross-link, surface sync — none touch external contracts). 04 Heavy (new `gz issue file` verb — `cli.md` § New Subcommand trigger). 05 Heavy (new `--strict` flag + `data/audit_thresholds.json` — `cli.md` § New Flag trigger), additionally carrying `sensitivity: security` (audit-check is the validator surface for trust assertions; ADR-0.0.22 third-axis applies). Foundation-kind brief-level Gate 5 acknowledged in every OBPI per the (kind × lane × sensitivity) matrix. ADR § Decision item 4 explicitly justifies the lane lift. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | Each OBPI has explicit Allowed Paths and Denied Paths. Cross-OBPI scope is crisp: 01 owns the rule, 02 owns AGENTS.md and the scorecard row, 03 owns mirrors, 04 owns gh-cli.md + issue_cmd.py + manpage + BDD, 05 owns adr_audit.py + threshold-config + schema. Three explicit non-goals in Alternatives Considered. ADR is self-contained; future revisions explicitly land under follow-up GHIs (#308-#312), preventing scope creep. |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | Every OBPI has a Verification section with executable commands and a REQ-mapped Acceptance Criteria block. Heavy OBPIs (04, 05) explicitly enumerate Gate 3/4/5 commands (`mkdocs build --strict`, `behave features/`, ATTEST). REQ IDs follow `REQ-<semver>-<obpi_item>-<criterion_index>` discipline. ARB receipt citation requirements named in REQ-04-08 and REQ-05-11. |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | ADR body cites doctrine surfaces (AGENTS.md § DO IT RIGHT, .gzkit/rules/, gz validate --advisory-scorecard) and names integration patterns (vendor mirror sync, ARB receipts, foundation-kind × lane matrix). OBPIs densely cite source paths (`src/gzkit/commands/adr_audit.py`, `src/gzkit/commands/issue_cmd.py`, `src/gzkit/cli/parser_*.py`, `src/gzkit/schemas/audit_thresholds.json`) and reference local precedents (ADR-0.0.22 third-axis pattern, GHI #272 cosmetic-backfill anti-pattern, GHI #149/#151 citation discipline). CLI heuristic scored 1 because it inspected the ADR document only and missed the OBPIs' density of path citations. Reduced from 4 to 3 because the ADR body itself is comparatively thin on direct source-path references — operators reading the ADR alone (without descending into OBPIs) get less file-level grounding than the strongest exemplars in this repo provide. |

WEIGHTED TOTAL: 3.60 / 4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- CLI ↔ Manual Reconciliation ---

| # | CLI | Manual | Heuristic Mismatch / Justification |
|---|-----|--------|-------------------------------------|
| 1 | 1 | 3 | False negative. Heuristic looks for literal before/current-state and after/target-state language inside § Intent. The ADR distributes the before across Intent (rule re-invention, scorecard cannot resolve) and the after across Consequences § Positive (shared vocabulary, scorable rules, anchored rationale). Content exists; framing differs from heuristic shape. |
| 4 | 4 | 3 | False positive. Heuristic counts OBPIs and checks numbering continuity; both pass. But OBPIs 04 and 05 each exceed the 1-3 day work-unit target by carrying full Heavy-lane envelope. Manual score reflects the size compromise. |
| 8 | 1 | 3 | False negative. Heuristic scans the ADR document only for source-path references and "exemplar"/"precedent" language. The ADR cites doctrine surfaces by section anchor; the OBPIs (which the heuristic does not inspect) are dense with `src/gzkit/**` paths and named local precedents (ADR-0.0.22, GHI #272, GHI #149/#151). The ADR-level citation is real but lighter than the strongest local exemplar. |

Dimensions 2, 3, 5, 6, 7 unchanged from CLI score; rationale provided above for traceability.

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01-author-failure-modes-rule | 4 | 4 | 4 | 4 | 4 | 4.0 |
| 02-cross-link-and-scorecard | 3 | 4 | 3 | 4 | 4 | 3.6 |
| 03-sync-mirrors | 3 | 4 | 3 | 4 | 4 | 3.6 |
| 04-cross-repo-defect-filing | 4 | 4 | 4 | 2 | 4 | 3.6 |
| 05-audit-check-covers-backfill-heuristic | 4 | 4 | 4 | 2 | 4 | 3.6 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any dimension must be revised.

All five OBPIs are above the 3.0 floor. No OBPI scored 1 on any dimension.

OBPI Notes:

- **01:** Foundation OBPI for the entire ADR. Six-pattern enumeration and ordering pinned in REQ-01-01. The taxonomy rule's existence is what makes 02 and 03 meaningful and is the doctrinal anchor 04 and 05 operationalize against.
- **02:** Independence reduced to 3 because OBPI-02 has a hard dependency on OBPI-01 (the cross-link cannot resolve until the rule file exists). Value 3 because the cross-link is necessary but small in isolation.
- **03:** Independence reduced to 3 because OBPI-03 depends on both OBPI-01 (canonical rule) and OBPI-02 (AGENTS.md cross-link to propagate via mirrors). Value 3 (mirror sync is mechanical).
- **04:** Size 2 reflects the substantial Heavy-lane envelope: doctrine subsection + new `gz issue file` verb + provenance auto-stamp + gzkit-surface guard + manpage + BDD scenario + unit tests with mocked subprocess boundary. Realistic estimate is 4-6 days. Value 4 (closes GHI #316 with a structurally enforced behavior).
- **05:** Size 2 reflects the substantial Heavy-lane envelope: temporal heuristic + threshold-data + Pydantic schema + same-commit + N-commit + D-day matching + lite/heavy/strict branching + fixture pair + BDD scenario + manpage. Realistic estimate is 5-7 days. Value 4 (closes GHI #309 by mechanizing the GHI #272 anti-pattern at audit time). Carries `sensitivity: security` and inherits the ADR-0.0.22 third-axis walkthrough at completion.

--- Red-Team Challenges ---

Not invoked (no `--red-team` flag). The ADR's structural quality (3.60 weighted) clears the GO threshold without adversarial review; the operator may run `--red-team` selectively before promotion if desired.

| # | Challenge | Result | Notes |
|---|-----------|--------|-------|
| 1-10 | (Skipped) | n/a | Re-run with `/gz-adr-evaluate ADR-0.0.23 --red-team` to engage. |

--- Overall Verdict ---

[x] GO — Ready for proposal/defense review
[ ] CONDITIONAL GO
[ ] NO GO

Manual weighted total 3.60 / 4.0 clears the GO threshold (>= 3.0). All OBPIs
average >= 3.0; no dimension scored 1. The ADR is structurally ready for
proposal/defense; the two manual reductions (Dim 4 OBPI Decomposition, Dim 8
Architectural Alignment) flag observations, not blockers.

ACTION ITEMS (advisory, not GO-blocking):

1. Consider whether OBPI-04 and OBPI-05 should split. Current shape is
   defensible (the heuristic and its threshold config cannot meaningfully
   amputate; the wrapper and its provenance auto-stamp form one capability),
   but execution will run beyond the 1-3 day target. If split is desired,
   candidate seams: 04 → (a) doctrine subsection + manpage scaffold,
   (b) wrapper + provenance + BDD; 05 → (a) threshold schema + config file,
   (b) heuristic + lite/heavy/strict branching + fixtures.
2. Consider one round of OBPI-01 review against the strongest existing
   `.gzkit/rules/*.md` exemplar (e.g. `tool-skill-runbook-alignment.md`)
   before authoring, to lock the rule's shape and citation discipline.
3. The ADR body cites doctrine surfaces; the OBPIs cite source paths.
   No-op in this evaluation, but ADR authors landing future foundation-kind
   ADRs may want to lift one or two source-path citations from the OBPIs
   into the ADR body to satisfy the Architectural Alignment rubric's
   ADR-document-only inspection more directly.
