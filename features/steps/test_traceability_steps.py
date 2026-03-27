"""BDD steps for test traceability / coverage reporting scenarios."""

from __future__ import annotations

from pathlib import Path

from behave import given

from gzkit.config import GzkitConfig


@given("an OBPI brief with one REQ and a decorator-covered test exists")
def step_brief_with_decorator_covered_test(_context) -> None:  # type: ignore[no-untyped-def]
    """Create an OBPI brief and a test that uses @covers decorator syntax."""
    config = GzkitConfig.load(Path(".gzkit.json"))
    obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
    obpi_path.parent.mkdir(parents=True, exist_ok=True)
    obpi_path.write_text(
        "---\n"
        "id: OBPI-0.1.0-01-demo\n"
        "parent: ADR-0.1.0\n"
        "item: 1\n"
        "lane: Lite\n"
        "status: Accepted\n"
        "---\n"
        "\n"
        "# OBPI-0.1.0-01: Demo\n"
        "\n"
        "## Acceptance Criteria\n"
        "\n"
        "- [ ] REQ-0.1.0-01-01: Demo criterion.\n",
        encoding="utf-8",
    )

    test_dir = Path("tests")
    test_dir.mkdir(exist_ok=True)
    (test_dir / "test_demo.py").write_text(
        "from gzkit.traceability import covers\n"
        "import unittest\n"
        "\n"
        "class TestDemo(unittest.TestCase):\n"
        '    @covers("REQ-0.1.0-01-01")\n'
        "    def test_pass(self) -> None:\n"
        "        pass\n",
        encoding="utf-8",
    )
