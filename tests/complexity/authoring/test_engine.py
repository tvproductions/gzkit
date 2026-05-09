"""Tests for the authoring-time hint engine (OBPI-0.0.30-03).

REQ-IDs in this module map to the brief Acceptance Criteria:

- REQ-05: clean file -> empty tuple
- REQ-06: file with advise crossings -> hints
- REQ-07: precedence_band classification (upper vs lower)

The engine wraps the ADR-0.0.29-02 ``DiagnosisEngine``, so we set up a
synthetic project root with a fixture distilled-characteristics doc and a
threshold table the loader can read.
"""

from __future__ import annotations

import json
import os
import tempfile
import textwrap
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from gzkit.complexity.authoring.engine import (
    _classify_precedence_band,
    analyze,
)
from gzkit.complexity.thresholds import load_threshold_table
from gzkit.traceability import covers

_PRACTITIONER_EYE_SENTINEL = "Refactor signal: extract the responsibility seam and re-test."


def _distilled_doc(metric: str = "radon_cc") -> str:
    return textwrap.dedent(
        f"""\
        ---
        corpus_revision: 1
        ---

        # Distilled complexity characteristics — synthetic fixture

        ## Metric: `{metric}`

        Across the corpus, synthetic distribution applies.

        **Doctrinal frame:** Martin (Clean Code) — function decomposition signal.

        ### Practitioner-eye observation

        {_PRACTITIONER_EYE_SENTINEL}
        """
    )


def _threshold_payload(
    metric: str,
    distilled_path: Path,
    anchor: str,
    *,
    advise: float = 4.0,
    warn: float = 7.0,
    block: float = 11.0,
) -> str:
    return json.dumps(
        {
            "corpus_revision": 1,
            "citation": {
                "distilled_characteristics_path": distilled_path.as_posix(),
                "section_anchor": anchor,
                "corpus_revision": 1,
            },
            "bands": [
                {
                    "metric": metric,
                    "corpus_percentile": 75,
                    "absolute_number": advise,
                    "trigger_semantic": "advise",
                },
                {
                    "metric": metric,
                    "corpus_percentile": 90,
                    "absolute_number": warn,
                    "trigger_semantic": "warn",
                },
                {
                    "metric": metric,
                    "corpus_percentile": 95,
                    "absolute_number": block,
                    "trigger_semantic": "block",
                },
            ],
        }
    )


@contextmanager
def _synthetic_root(metric: str = "radon_cc") -> Iterator[Path]:
    """Yield the threshold-rule path under a temp project root with cwd switched."""
    with tempfile.TemporaryDirectory() as raw_root:
        root = Path(raw_root)
        complexity_dir = root / "docs" / "governance" / "complexity"
        complexity_dir.mkdir(parents=True)
        distilled_path = complexity_dir / "distilled-characteristics-synthetic.md"
        distilled_path.write_text(_distilled_doc(metric), encoding="utf-8")
        rule_path = root / "thresholds.json"
        anchor = metric.replace("_", "-")
        rule_path.write_text(
            _threshold_payload(metric, distilled_path.relative_to(root), anchor),
            encoding="utf-8",
        )
        prior = Path.cwd()
        os.chdir(root)
        try:
            yield rule_path
        finally:
            os.chdir(prior)


def _write_py_source(root: Path, name: str, source: str) -> Path:
    path = root / name
    path.write_text(source, encoding="utf-8")
    return path


_CLEAN_SOURCE = "def trivial():\n    return 1\n"

# Cyclomatic complexity ~5 (>= advise 4, < warn 7) — lands in lower portion of
# advise (midpoint between 4 and 7 is 5.5, so 5 is "approaching").
_ADVISE_LOWER_SOURCE = textwrap.dedent(
    """\
    def lower_advise(x):
        if x == 1:
            return 1
        if x == 2:
            return 2
        if x == 3:
            return 3
        if x == 4:
            return 4
        return 0
    """
)


class TestEngineCleanFile(unittest.TestCase):
    @covers("REQ-0.0.30-03-05")
    def test_clean_file_returns_empty_tuple(self) -> None:
        with _synthetic_root() as rule_path:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".py", delete=False, dir=rule_path.parent, encoding="utf-8"
            ) as fh:
                fh.write(_CLEAN_SOURCE)
                src = Path(fh.name)
            try:
                table = load_threshold_table(rule_path)
                hints = analyze(src, table=table)
                self.assertEqual(hints, ())
            finally:
                src.unlink(missing_ok=True)

    @covers("REQ-0.0.30-03-05")
    def test_warn_band_crossing_excluded(self) -> None:
        """A crossing in warn band must NOT produce an authoring hint."""
        warn_source = textwrap.dedent(
            """\
            def at_warn(x):
                if x == 1:
                    return 1
                if x == 2:
                    return 2
                if x == 3:
                    return 3
                if x == 4:
                    return 4
                if x == 5:
                    return 5
                if x == 6:
                    return 6
                if x == 7:
                    return 7
                return 0
            """
        )
        with _synthetic_root() as rule_path:
            src = _write_py_source(rule_path.parent, "warn_src.py", warn_source)
            table = load_threshold_table(rule_path)
            hints = analyze(src, table=table)
            self.assertEqual(hints, ())


class TestEngineAdviseCrossings(unittest.TestCase):
    @covers("REQ-0.0.30-03-06")
    def test_advise_crossing_yields_hint(self) -> None:
        with _synthetic_root() as rule_path:
            src = _write_py_source(rule_path.parent, "lower.py", _ADVISE_LOWER_SOURCE)
            table = load_threshold_table(rule_path)
            hints = analyze(src, table=table)
            self.assertEqual(len(hints), 1)
            hint = hints[0]
            self.assertEqual(hint.metric, "radon_cc")
            self.assertEqual(hint.file_path, str(src))
            self.assertGreaterEqual(hint.start_line, 1)
            self.assertGreaterEqual(hint.end_line, hint.start_line)
            self.assertIn(
                hint.precedence_band,
                ("approaching", "approaching_warn"),
            )


class TestPrecedenceBandClassification(unittest.TestCase):
    @covers("REQ-0.0.30-03-07")
    def test_lower_portion_classifies_as_approaching(self) -> None:
        with _synthetic_root() as rule_path:
            table = load_threshold_table(rule_path)
            # advise = 4.0, warn = 7.0, midpoint = 5.5; value 5.0 < 5.5 -> lower
            band = _classify_precedence_band(table, "radon_cc", 5.0)
            self.assertEqual(band, "approaching")

    @covers("REQ-0.0.30-03-07")
    def test_upper_portion_classifies_as_approaching_warn(self) -> None:
        with _synthetic_root() as rule_path:
            table = load_threshold_table(rule_path)
            # value 6.0 >= 5.5 -> upper portion
            band = _classify_precedence_band(table, "radon_cc", 6.0)
            self.assertEqual(band, "approaching_warn")

    @covers("REQ-0.0.30-03-07")
    def test_value_at_midpoint_classifies_as_approaching_warn(self) -> None:
        with _synthetic_root() as rule_path:
            table = load_threshold_table(rule_path)
            # boundary case: value == midpoint -> upper (>=)
            band = _classify_precedence_band(table, "radon_cc", 5.5)
            self.assertEqual(band, "approaching_warn")

    @covers("REQ-0.0.30-03-07")
    def test_no_warn_band_returns_approaching(self) -> None:
        """When the metric has no warn band, classification falls back to lower."""
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            complexity_dir = root / "docs" / "governance" / "complexity"
            complexity_dir.mkdir(parents=True)
            distilled_path = complexity_dir / "distilled.md"
            distilled_path.write_text(_distilled_doc("radon_cc"), encoding="utf-8")
            rule_path = root / "thresholds.json"
            payload = json.dumps(
                {
                    "corpus_revision": 1,
                    "citation": {
                        "distilled_characteristics_path": distilled_path.relative_to(
                            root
                        ).as_posix(),
                        "section_anchor": "radon-cc",
                        "corpus_revision": 1,
                    },
                    "bands": [
                        {
                            "metric": "radon_cc",
                            "corpus_percentile": 75,
                            "absolute_number": 4.0,
                            "trigger_semantic": "advise",
                        },
                        {
                            "metric": "radon_cc",
                            "corpus_percentile": 95,
                            "absolute_number": 11.0,
                            "trigger_semantic": "block",
                        },
                    ],
                }
            )
            rule_path.write_text(payload, encoding="utf-8")
            prior = Path.cwd()
            os.chdir(root)
            try:
                table = load_threshold_table(rule_path)
                band = _classify_precedence_band(table, "radon_cc", 5.0)
                self.assertEqual(band, "approaching")
            finally:
                os.chdir(prior)


if __name__ == "__main__":
    unittest.main()
