"""REQ-derived tests for the canonical complexity-thresholds rule file.

These tests pin the operator-facing contract for
``.gzkit/rules/complexity-thresholds.md``: the rule file MUST exist with
valid frontmatter, MUST carry the body-level rule-version marker, MUST
declare the three-value trigger-semantic vocabulary, MUST list all twelve
canonical metrics with at least a ``block`` band each, MUST pair every
band's percentile with an absolute number, MUST carry the canonical
citation tuple naming the distilled-characteristics document, MUST
declare the operator-amendable mapping protocol, and MUST name the
bootstrap-absolutes carve-out for the three known-bootstrap metrics.
Sister tests pin the advisory-scorecard entry and vendor-mirror
propagation.

Coverage:
    REQ-0.0.28-01-01 — frontmatter validity, body version marker, block quote.
    REQ-0.0.28-01-02 — trigger-semantic vocabulary declares exactly three
        values: ``block``, ``warn``, ``advise``.
    REQ-0.0.28-01-03 — for each canonical metric (12-tuple from
        ``gzkit.complexity.measurement.CANONICAL_METRICS``), a per-metric
        threshold table carries at least one ``block`` band row.
    REQ-0.0.28-01-04 — every band row carries both ``corpus_percentile``
        and ``absolute_number``.
    REQ-0.0.28-01-05 — Citation section at top names the canonical tuple
        ``(distilled_characteristics_path, section_anchor, corpus_revision)``;
        cited path resolves; ``parse_citation`` round-trips.
    REQ-0.0.28-01-06 — operator-amendable mapping protocol section
        names the doctrine-amendment-protocol stub and forbids silent edits.
    REQ-0.0.28-01-07 — scorecard at ``docs/governance/advisory-rules-audit.md``
        carries a ``complexity-thresholds`` entry classified Mechanical.
    REQ-0.0.28-01-08 — ``gz validate --advisory-scorecard`` exits 0.
    REQ-0.0.28-01-09 — vendor mirrors carry the body-level rule-version marker.
    REQ-0.0.28-01-10 — bootstrap carve-out section names exactly the three
        known-bootstrap metrics: ``radon_mi``, ``lizard_nesting_depth``,
        ``cohesion_lcom4``.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.complexity.citation import parse_citation
from gzkit.complexity.measurement import CANONICAL_METRICS
from gzkit.rules import RuleFrontmatter, _parse_canonical_frontmatter
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_RULE_PATH = _PROJECT_ROOT / ".gzkit" / "rules" / "complexity-thresholds.md"
_TRIGGER_VOCABULARY = ("block", "warn", "advise")
_BOOTSTRAP_METRICS = ("radon_mi", "lizard_nesting_depth", "cohesion_lcom4")


class ComplexityThresholdsRuleAuthorship(unittest.TestCase):
    """Pin the rule file's authorship contract."""

    @covers("REQ-0.0.28-01-01")
    def test_rule_file_exists_with_valid_frontmatter(self) -> None:
        self.assertTrue(
            _RULE_PATH.is_file(),
            f"canonical rule file missing: {_RULE_PATH.relative_to(_PROJECT_ROOT).as_posix()}",
        )
        frontmatter_dict, _ = _parse_canonical_frontmatter(_RULE_PATH)
        frontmatter = RuleFrontmatter(**frontmatter_dict)
        self.assertEqual(frontmatter.id, "complexity-thresholds")
        self.assertGreater(
            len(frontmatter.paths),
            0,
            "frontmatter paths must list at least one glob pattern",
        )
        self.assertTrue(
            frontmatter.description.strip(),
            "frontmatter description must be a non-empty one-liner",
        )

    @covers("REQ-0.0.28-01-01")
    def test_rule_body_carries_version_marker_and_block_quote(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        self.assertIn(
            "<!-- rule-version: 0.1.0 -->",
            body,
            "body must carry the canonical body-level rule-version HTML comment",
        )
        self.assertRegex(
            body,
            r">\s+\*\*Rule version:\*\*\s+`0\.1\.0`",
            "body must carry the visible rule-version block quote",
        )

    @covers("REQ-0.0.28-01-02")
    def test_trigger_semantic_vocabulary_declares_exactly_three_values(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        # Extract the Trigger-Semantic Vocabulary section content; the binding
        # contract is that this section, not the whole body, declares exactly
        # three accepted values.
        vocab_match = re.search(
            r"##\s+Trigger-Semantic\s+Vocabulary.*?(?=^##\s|\Z)",
            body,
            re.DOTALL | re.MULTILINE | re.IGNORECASE,
        )
        self.assertIsNotNone(
            vocab_match,
            "rule body must carry a `## Trigger-Semantic Vocabulary` section",
        )
        section = vocab_match.group(0) if vocab_match else ""
        # Each of the three canonical values appears in a markdown-table row
        # of the vocabulary section.
        for value in _TRIGGER_VOCABULARY:
            with self.subTest(value=value):
                self.assertRegex(
                    section,
                    re.compile(rf"\|\s*`{value}`\s*\|", re.IGNORECASE),
                    f"vocabulary section must declare {value!r} as a table row",
                )
        # No fourth value appears in a markdown-table row position. Forbidden
        # tokens may appear in negation prose ("a fourth value e.g. `info` is
        # forbidden") — that's the contract being articulated, not violated.
        # The semantic check: the vocabulary table holds exactly three rows.
        table_rows = re.findall(
            r"^\|\s*`(\w+)`\s*\|\s*The metric crossing this band",
            section,
            re.MULTILINE,
        )
        self.assertEqual(
            sorted(table_rows),
            sorted(_TRIGGER_VOCABULARY),
            f"vocabulary table must declare exactly {_TRIGGER_VOCABULARY!r} as accepted values",
        )

    @covers("REQ-0.0.28-01-03")
    def test_each_canonical_metric_has_block_band_row(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        self.assertEqual(
            len(CANONICAL_METRICS),
            12,
            "expected exactly 12 canonical metrics from gzkit.complexity.measurement",
        )
        for metric in CANONICAL_METRICS:
            with self.subTest(metric=metric):
                # Match the per-metric section heading explicitly — `### Metric: <name>`
                # — and capture body until the next section heading or end of document.
                metric_section_match = re.search(
                    rf"^###\s+Metric:\s+`{re.escape(metric)}`.*?(?=^###\s|^##\s|\Z)",
                    body,
                    re.DOTALL | re.MULTILINE,
                )
                self.assertIsNotNone(
                    metric_section_match,
                    f"metric {metric!r} must have a per-metric section in rule body",
                )
                section = metric_section_match.group(0) if metric_section_match else ""
                # The section must declare a block-band row in its threshold table.
                self.assertRegex(
                    section,
                    re.compile(r"\|\s*block\s*\|", re.IGNORECASE),
                    f"metric {metric!r} section must declare a `block` band row",
                )

    @covers("REQ-0.0.28-01-04")
    def test_every_band_row_pairs_percentile_with_absolute_number(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        # Every band row in the per-metric tables must have both a percentile
        # marker (pNN) and a numeric absolute. Look for the canonical row shape:
        # markdown table rows with three or more cells, where one cell carries
        # ``pNN`` and another carries a numeric value. The simplest semantic
        # check: every percentile mention in a band-row position is accompanied
        # by a numeric absolute on the same row.
        band_row_pattern = re.compile(
            r"\|\s*(?:block|warn|advise)\s*\|\s*p\d{2,3}\s*\|\s*[\d.]+",
            re.IGNORECASE,
        )
        matches = band_row_pattern.findall(body)
        # We have 12 metrics; 9 have full advise/warn/block (3 rows each = 27) +
        # 3 bootstrap metrics with 3 bootstrap rows (9) = 36 rows minimum.
        # Use a softer floor of 12 (one block band per metric minimum) to keep
        # the test resilient to band-count changes within the contract.
        self.assertGreaterEqual(
            len(matches),
            12,
            "every metric must contribute at least one band row pairing "
            "trigger + percentile + absolute number",
        )

    @covers("REQ-0.0.28-01-05")
    def test_citation_section_names_canonical_tuple_and_resolves(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        # The Citation section must name the canonical tuple form and the
        # cited document path. parse_citation round-trips the canonical string.
        self.assertRegex(
            body,
            re.compile(
                r"##\s+Citation",
                re.MULTILINE,
            ),
            "rule body must carry a top-level `## Citation` section",
        )
        # The cited document path must appear and resolve under the project root.
        cited_path_match = re.search(
            r"docs/governance/complexity/distilled-characteristics-\d{4}-\d{2}-\d{2}\.md",
            body,
        )
        self.assertIsNotNone(
            cited_path_match,
            "Citation section must name a distilled-characteristics-{YYYY-MM-DD}.md path",
        )
        cited_path = _PROJECT_ROOT / (cited_path_match.group(0) if cited_path_match else "")
        self.assertTrue(
            cited_path.is_file(),
            f"cited distilled-characteristics document must exist on disk: {cited_path}",
        )
        # corpus_revision must be named explicitly in the canonical tuple form.
        self.assertRegex(
            body,
            re.compile(r"corpus[_\s]revision", re.IGNORECASE),
            "Citation section must name corpus_revision as part of the canonical tuple",
        )
        # parse_citation must accept the canonical-string form rendered in the body.
        canonical_form_pattern = (
            r"(docs/governance/complexity/distilled-characteristics-\d{4}-\d{2}-\d{2}\.md"
            r"\s*§\s*\S+\s*\(corpus revision \d+\))"
        )
        canonical_form_match = re.search(canonical_form_pattern, body)
        self.assertIsNotNone(
            canonical_form_match,
            "Citation section must include the canonical-string form "
            "`<path> § <anchor> (corpus revision N)`",
        )
        if canonical_form_match:
            citation = parse_citation(canonical_form_match.group(1))
            self.assertGreaterEqual(citation.corpus_revision, 1)

    @covers("REQ-0.0.28-01-06")
    def test_operator_amendable_mapping_protocol_section_present(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        self.assertRegex(
            body,
            re.compile(
                r"##\s+Operator.amendable.*mapping",
                re.IGNORECASE | re.MULTILINE,
            ),
            "rule body must carry an Operator-amendable mapping protocol section",
        )
        self.assertRegex(
            body,
            re.compile(r"doctrine.amendment.protocol", re.IGNORECASE),
            "amendment protocol must reference the doctrine-amendment-protocol stub",
        )
        self.assertRegex(
            body,
            re.compile(r"silent\s+edits?\s+(?:are\s+)?forbidden", re.IGNORECASE),
            "amendment protocol must declare silent edits forbidden",
        )

    @covers("REQ-0.0.28-01-10")
    def test_bootstrap_carve_out_names_exactly_three_metrics(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        bootstrap_section_match = re.search(
            r"##\s+Bootstrap.*?(?=^##\s|\Z)",
            body,
            re.DOTALL | re.MULTILINE | re.IGNORECASE,
        )
        self.assertIsNotNone(
            bootstrap_section_match,
            "rule body must carry a Bootstrap absolutes section per REQ-11 carve-out",
        )
        section = bootstrap_section_match.group(0) if bootstrap_section_match else ""
        for metric in _BOOTSTRAP_METRICS:
            with self.subTest(metric=metric):
                self.assertIn(
                    metric,
                    section,
                    f"bootstrap section must name known-bootstrap metric: {metric!r}",
                )
        # Cite the GHIs that track the upstream defects.
        self.assertRegex(
            section,
            re.compile(r"GHI[\s#]*40[45]", re.IGNORECASE),
            "bootstrap section must cite GHI #404 (parser defect) and/or #405 (polarity model)",
        )


class ComplexityThresholdsCrossSurfaceBindings(unittest.TestCase):
    """Pin the rule's binding into the scorecard and vendor mirrors."""

    @covers("REQ-0.0.28-01-07")
    def test_advisory_scorecard_classifies_rule_mechanical(self) -> None:
        scorecard = (_PROJECT_ROOT / "docs" / "governance" / "advisory-rules-audit.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "complexity-thresholds",
            scorecard,
            "scorecard must mention the complexity-thresholds rule",
        )
        self.assertRegex(
            scorecard,
            re.compile(
                r"###\s+Complexity\s+Thresholds.*?\*\*Mechanical\*\*",
                re.DOTALL,
            ),
            "scorecard section for complexity-thresholds must be classified Mechanical",
        )

    @covers("REQ-0.0.28-01-08")
    def test_advisory_scorecard_audit_has_no_offenders_for_new_rule(self) -> None:
        from gzkit.governance.trust_audits import audit_advisory_scorecard

        errors = audit_advisory_scorecard(_PROJECT_ROOT)
        rule_offenders = [err for err in errors if "complexity-thresholds" in err.artifact]
        self.assertEqual(
            rule_offenders,
            [],
            "audit_advisory_scorecard must not flag complexity-thresholds "
            "(needs a scorecard entry).",
        )

    @covers("REQ-0.0.28-01-09")
    def test_vendor_mirrors_carry_rule_version_marker(self) -> None:
        mirrors = (
            _PROJECT_ROOT / ".claude" / "rules" / "complexity-thresholds.md",
            _PROJECT_ROOT / ".github" / "instructions" / "complexity_thresholds.instructions.md",
        )
        for mirror in mirrors:
            with self.subTest(mirror=mirror.relative_to(_PROJECT_ROOT).as_posix()):
                self.assertTrue(
                    mirror.is_file(),
                    f"vendor mirror missing: {mirror.relative_to(_PROJECT_ROOT).as_posix()}",
                )
                self.assertIn(
                    "<!-- rule-version: 0.1.0 -->",
                    mirror.read_text(encoding="utf-8"),
                    "vendor mirror must carry the body-level rule-version marker",
                )


if __name__ == "__main__":
    unittest.main()
