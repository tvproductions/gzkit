"""REQ-derived tests for the complexity-thresholds validator (OBPI-0.0.28-03).

The validator at
``src/gzkit/governance/trust_audits/complexity_thresholds.py``
runs OBPI-0.0.28-02's ``load_threshold_table`` against
``.gzkit/rules/complexity-thresholds.md``, asserts each canonical metric
has at least one band, asserts every band's percentile + absolute pairing
is well-formed (delegated to the loader's Pydantic model), asserts the
citation tuple parses, and skips portability checks for rows under the
bootstrap-absolutes carve-out (emitting a "bootstrap-mode" warning to
operator-facing diagnostic).

Coverage:
    REQ-0.0.28-03-01 — well-formed threshold rule body validates clean
        (exit 0, empty error list).
    REQ-0.0.28-03-02 — rule body where any metric lacks a ``block`` band
        fails with a named error listing the metric.
    REQ-0.0.28-03-03 — band with ``corpus_percentile=80`` (off the
        ``{50,75,90,95,99}`` enum) fails with a named error.
    REQ-0.0.28-03-04 — citation tuple that does not parse against
        ``parse_citation`` fails with a named error.
    REQ-0.0.28-03-05 — rule body declaring the bootstrap-absolutes
        carve-out section emits a "bootstrap-mode" warning to operator
        diagnostic; portability checks are skipped for bootstrap rows.
    REQ-0.0.28-03-06 — ``gz validate --all`` and ``gz check`` both fire
        the new validator as part of the aggregate run.
    REQ-0.0.28-03-07 — the command doc and runbook each carry the
        ``--complexity-thresholds`` section / entry.
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.complexity_thresholds import (
    BOOTSTRAP_MODE_NOTICE_PREFIX,
    validate_complexity_thresholds,
)
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_rule_body(body: str) -> Path:
    """Write the rule body into a tempdir mirroring the canonical layout."""
    temp_root = Path(tempfile.mkdtemp())
    rule_dir = temp_root / ".gzkit" / "rules"
    rule_dir.mkdir(parents=True, exist_ok=True)
    rule_path = rule_dir / "complexity-thresholds.md"
    rule_path.write_text(body, encoding="utf-8")
    return temp_root


def _well_formed_body(*, include_bootstrap: bool = False) -> str:
    """Synthetic well-formed rule body covering all 12 canonical metrics."""
    metrics_with_bands = [
        ("radon_cc", "radon-cc", 4.0, 7.0, 11.0),
        ("radon_mi", "radon-mi", 85.0, 70.0, 50.0),
        ("radon_hal_volume", "radon-hal-volume", 946.89, 2740.93, 5549.80),
        ("radon_hal_difficulty", "radon-hal-difficulty", 8.13, 11.54, 12.46),
        ("radon_hal_effort", "radon-hal-effort", 7975.79, 30805.01, 74805.40),
        ("radon_raw_nloc", "radon-raw-nloc", 311.75, 733.20, 1031.90),
        ("radon_raw_lloc", "radon-raw-lloc", 238.25, 518.00, 811.70),
        ("lizard_nloc", "lizard-nloc", 13.0, 25.0, 37.0),
        ("lizard_param_count", "lizard-param-count", 3.0, 4.0, 5.0),
        ("lizard_nesting_depth", "lizard-nesting-depth", 2.0, 3.0, 4.0),
        ("lizard_ccn", "lizard-ccn", 4.0, 8.0, 11.0),
        ("cohesion_lcom4", "cohesion-lcom4", 2.0, 4.0, 8.0),
    ]
    sections = []
    for metric, anchor, advise, warn, block in metrics_with_bands:
        sections.append(
            f"### Metric: `{metric}`\n\n"
            f"Citation: `docs/governance/complexity/distilled-characteristics-2026-05-04.md "
            f"§ {anchor} (corpus revision 1)`\n\n"
            "| Trigger | Corpus percentile | Absolute number | Cited section |\n"
            "|---------|-------------------|-----------------|---------------|\n"
            f"| advise  | p75               | {advise}        | {anchor}      |\n"
            f"| warn    | p90               | {warn}          | {anchor}      |\n"
            f"| block   | p95               | {block}         | {anchor}      |\n"
        )
    bootstrap_section = ""
    if include_bootstrap:
        bootstrap_section = (
            "\n## Bootstrap absolutes (REQ-11 carve-out — one-shot)\n\n"
            "- `radon_mi` — bootstrap (GHI #405)\n"
            "- `lizard_nesting_depth` — bootstrap (GHI #404)\n"
            "- `cohesion_lcom4` — bootstrap (GHI #404)\n"
        )
    return (
        "---\n"
        "id: complexity-thresholds\n"
        "paths:\n"
        '  - ".gzkit/rules/complexity-thresholds.md"\n'
        "description: test\n"
        "---\n\n"
        "<!-- rule-version: 0.1.0 -->\n\n"
        "# Complexity Thresholds\n\n"
        "## Citation\n\n"
        "`docs/governance/complexity/distilled-characteristics-2026-05-04.md "
        "§ radon-cc (corpus revision 1)`\n\n"
        "## Per-metric tables\n\n" + "\n".join(sections) + bootstrap_section
    )


class WellFormedRuleBody(unittest.TestCase):
    """Well-formed rule body validates clean."""

    @covers("REQ-0.0.28-03-01")
    def test_well_formed_body_returns_no_errors(self) -> None:
        project_root = _write_rule_body(_well_formed_body())
        errors = validate_complexity_thresholds(project_root)
        self.assertEqual(
            errors,
            [],
            f"well-formed body produced unexpected errors: {errors!r}",
        )


class MissingBlockBand(unittest.TestCase):
    """Rule body where any metric lacks a block band fails closed."""

    @covers("REQ-0.0.28-03-02")
    def test_missing_block_band_fails_named(self) -> None:
        # Strip every `radon_cc` block-band row regardless of whitespace
        # padding (fixture template's column alignment is not load-bearing).
        body = re.sub(
            r"^\|\s*block\s*\|\s*p95\s*\|\s*[\d.]+\s*\|\s*radon-cc\s*\|\s*\n",
            "",
            _well_formed_body(),
            count=1,
            flags=re.MULTILINE,
        )
        project_root = _write_rule_body(body)
        errors = validate_complexity_thresholds(project_root)
        self.assertGreater(len(errors), 0)
        joined = " ".join(e.message for e in errors)
        self.assertIn("radon_cc", joined)


class OffEnumPercentile(unittest.TestCase):
    """Band with off-enum percentile fails closed."""

    @covers("REQ-0.0.28-03-03")
    def test_off_enum_percentile_fails(self) -> None:
        body = _well_formed_body().replace(
            "| advise  | p75               | 4.0        | radon-cc      |",
            "| advise  | p80               | 4.0        | radon-cc      |",
        )
        project_root = _write_rule_body(body)
        errors = validate_complexity_thresholds(project_root)
        self.assertGreater(len(errors), 0)


class UnparseableCitation(unittest.TestCase):
    """Citation tuple that does not parse fails closed."""

    @covers("REQ-0.0.28-03-04")
    def test_malformed_citation_fails(self) -> None:
        body = _well_formed_body().replace(
            "## Citation\n\n"
            "`docs/governance/complexity/distilled-characteristics-2026-05-04.md "
            "§ radon-cc (corpus revision 1)`\n\n",
            "## Citation\n\n`malformed-citation-no-canonical-form`\n\n",
        )
        project_root = _write_rule_body(body)
        errors = validate_complexity_thresholds(project_root)
        self.assertGreater(len(errors), 0)


class BootstrapMode(unittest.TestCase):
    """Rule body with bootstrap section emits bootstrap-mode notice via stdout."""

    @covers("REQ-0.0.28-03-05")
    def test_bootstrap_section_emits_notice_to_stdout(self) -> None:
        import contextlib
        import io

        project_root = _write_rule_body(_well_formed_body(include_bootstrap=True))
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            errors = validate_complexity_thresholds(project_root)
        self.assertIn(
            BOOTSTRAP_MODE_NOTICE_PREFIX,
            buffer.getvalue(),
            f"expected stdout notice prefixed with {BOOTSTRAP_MODE_NOTICE_PREFIX!r}, "
            f"got: {buffer.getvalue()!r}",
        )
        # Notice must NOT be in the returned error list (CLI exit-code logic
        # treats every list entry as an error).
        self.assertEqual(
            errors,
            [],
            f"bootstrap-mode notice leaked into error list: {errors!r}",
        )

    @covers("REQ-0.0.28-03-05")
    def test_bootstrap_mode_does_not_block_well_formed(self) -> None:
        project_root = _write_rule_body(_well_formed_body(include_bootstrap=True))
        errors = validate_complexity_thresholds(project_root)
        self.assertEqual(
            errors,
            [],
            f"bootstrap-mode body produced unexpected errors: {errors!r}",
        )


class RealRuleBody(unittest.TestCase):
    """The actual landed rule body validates clean (warnings via stdout only)."""

    @covers("REQ-0.0.28-03-01")
    def test_real_rule_body_returns_no_errors(self) -> None:
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            errors = validate_complexity_thresholds(_PROJECT_ROOT)
        self.assertEqual(
            errors,
            [],
            f"real rule body produced unexpected errors: {errors!r}",
        )


class ValidateAndCheckAggregation(unittest.TestCase):
    """gz validate explicit-scope dispatch + gz check aggregator both fire the validator."""

    @covers("REQ-0.0.28-03-06")
    def test_explicit_scope_runner_wires_complexity_thresholds(self) -> None:
        from gzkit.commands.validate_cmd import _explicit_scope_runners

        runners = _explicit_scope_runners(_PROJECT_ROOT)
        self.assertIn(
            "complexity_thresholds",
            runners,
            "_explicit_scope_runners must wire the complexity_thresholds scope",
        )

    @covers("REQ-0.0.28-03-06")
    def test_resolve_scopes_includes_complexity_thresholds_when_requested(self) -> None:
        from gzkit.commands.validate_cmd import _resolve_scopes

        scopes = _resolve_scopes({"complexity_thresholds": True})
        self.assertIn(
            "complexity_thresholds",
            scopes,
            "_resolve_scopes must include complexity_thresholds when its check flag is set",
        )

    @covers("REQ-0.0.28-03-06")
    def test_check_aggregator_fires_complexity_thresholds_audit(self) -> None:
        from gzkit.commands.quality import _build_check_steps

        step_labels = [label for label, _ in _build_check_steps()]
        self.assertIn(
            "Complexity-thresholds",
            step_labels,
            "gz check aggregator must include the Complexity-thresholds step",
        )


class CommandDocAndRunbook(unittest.TestCase):
    """Command doc and runbook carry the --complexity-thresholds section."""

    @covers("REQ-0.0.28-03-07")
    def test_command_doc_documents_flag(self) -> None:
        path = _PROJECT_ROOT / "docs" / "user" / "manpages" / "validate.md"
        self.assertTrue(path.is_file())
        content = path.read_text(encoding="utf-8")
        self.assertIn("--complexity-thresholds", content)

    @covers("REQ-0.0.28-03-07")
    def test_runbook_lists_complexity_thresholds_verb(self) -> None:
        path = _PROJECT_ROOT / "docs" / "user" / "runbook.md"
        self.assertTrue(path.is_file())
        content = path.read_text(encoding="utf-8")
        self.assertIn("--complexity-thresholds", content)


if __name__ == "__main__":
    unittest.main()
