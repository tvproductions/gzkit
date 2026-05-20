"""Fixture-level tests for ``audit_utf8_prefix`` extended scope (GHI #275).

These tests exercise the audit against synthetic temp trees, isolating
each new source class from repo-wide state. The repo-lock test in
``test_promoted_advisory_audits.py`` continues to gate current repo state;
this module gates the scan semantics.

Covers the ``cross-platform.md`` § "Scope boundary of the runtime guard"
cases that the original ``PYTHONUTF8=1`` prefix scan did not enforce:

- ``gz ... | python -c "..."`` pipelines that skip stdin/stdout reconfigure
- ``gz ... | jq|awk|sed`` pipelines that should use file-handoff instead
- ``tools/**/*.py`` entry points that print without reconfigure
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_utf8_prefix


class PipePythonReconfigureTests(unittest.TestCase):
    """``gz ... | python -c "..."`` must reconfigure stdin/stdout."""

    def _write_doc(self, root: Path, body: str) -> Path:
        target = root / "docs" / "sample.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        return target

    def test_pipe_python_without_reconfigure_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_doc(
                root,
                "```bash\nuv run gz state --json | python -c "
                '"import json,sys; print(json.load(sys.stdin))"\n```\n',
            )
            errors = audit_utf8_prefix(root)
            self.assertTrue(
                any(e.type == "utf8_prefix" for e in errors),
                msg=f"expected utf8_prefix error, got: {errors}",
            )

    def test_pipe_python_with_reconfigure_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_doc(
                root,
                "```bash\nuv run gz state --json | uv run python -c "
                "\"import json,sys; sys.stdout.reconfigure(encoding='utf-8'); "
                "sys.stdin.reconfigure(encoding='utf-8'); "
                'print(json.load(sys.stdin))"\n```\n',
            )
            errors = audit_utf8_prefix(root)
            self.assertFalse(
                errors,
                msg=f"expected clean, got: {errors}",
            )

    def test_standalone_python_c_without_pipe_is_not_flagged(self) -> None:
        """``python -c`` that does not consume gz output is out of scope."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_doc(
                root,
                "```bash\npython -c \"from gzkit.config import load_config; print('ok')\"\n```\n",
            )
            errors = audit_utf8_prefix(root)
            self.assertFalse(errors, msg=f"expected clean, got: {errors}")


class PipeNonPythonToolTests(unittest.TestCase):
    """``gz ... | jq|awk|sed`` is UTF-8-unsafe on Windows per rule."""

    def _write_doc(self, root: Path, body: str) -> Path:
        target = root / "docs" / "sample.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        return target

    def test_pipe_jq_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_doc(root, "```bash\nuv run gz state --json | jq '.pipeline'\n```\n")
            errors = audit_utf8_prefix(root)
            self.assertTrue(
                any(e.type == "utf8_prefix" for e in errors),
                msg=f"expected utf8_prefix error, got: {errors}",
            )

    def test_pipe_awk_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_doc(root, "```bash\nuv run gz obpi list | awk '{print $1}'\n```\n")
            errors = audit_utf8_prefix(root)
            self.assertTrue(
                any(e.type == "utf8_prefix" for e in errors),
                msg=f"expected utf8_prefix error, got: {errors}",
            )

    def test_non_gz_pipe_to_jq_is_not_flagged(self) -> None:
        """``jq`` pipelines that don't consume gz output are out of scope."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_doc(root, "```bash\ncat data.json | jq '.pipeline'\n```\n")
            errors = audit_utf8_prefix(root)
            self.assertFalse(errors, msg=f"expected clean, got: {errors}")


class ToolsScriptReconfigureTests(unittest.TestCase):
    """``tools/**/*.py`` entry points must reconfigure stdout before print."""

    def _write_tool(self, root: Path, name: str, body: str) -> Path:
        target = root / "tools" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        return target

    def test_tool_missing_reconfigure_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_tool(
                root,
                "bad.py",
                "import sys\n\n"
                "def main():\n"
                "    print('hello')\n\n"
                "if __name__ == '__main__':\n"
                "    main()\n",
            )
            errors = audit_utf8_prefix(root)
            self.assertTrue(
                any(e.type == "utf8_prefix" for e in errors),
                msg=f"expected utf8_prefix error, got: {errors}",
            )

    def test_tool_with_reconfigure_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_tool(
                root,
                "good.py",
                "import sys\n\n"
                "sys.stdout.reconfigure(encoding='utf-8')\n\n"
                "def main():\n"
                "    print('hello')\n\n"
                "if __name__ == '__main__':\n"
                "    main()\n",
            )
            errors = audit_utf8_prefix(root)
            self.assertFalse(errors, msg=f"expected clean, got: {errors}")

    def test_library_module_without_main_is_ignored(self) -> None:
        """Library modules under tools/ without ``__main__`` are not scanned."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_tool(
                root,
                "helpers.py",
                "def compute(x):\n    return x * 2\n",
            )
            errors = audit_utf8_prefix(root)
            self.assertFalse(errors, msg=f"expected clean, got: {errors}")


class PrefixRegressionTests(unittest.TestCase):
    """Original ``PYTHONUTF8=1`` scan remains enforced."""

    def test_pythonutf8_prefix_still_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "docs" / "sample.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "```bash\nPYTHONUTF8=1 uv run gz state\n```\n",
                encoding="utf-8",
            )
            errors = audit_utf8_prefix(root)
            self.assertTrue(
                any(e.type == "utf8_prefix" for e in errors),
                msg=f"expected utf8_prefix error, got: {errors}",
            )


class PipeContinuationTests(unittest.TestCase):
    """``\\``-continued gz pipelines must be flagged despite the line split (GHI #486)."""

    def _write_doc(self, root: Path, body: str) -> Path:
        target = root / "docs" / "sample.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        return target

    def test_continuation_pipe_python_is_flagged_at_start_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_doc(
                root,
                "```bash\n"
                "uv run gz obpi complete OBPI-0.0.X-NN --dry-run --json \\\n"
                '  | python -c "import json,sys; print(json.load(sys.stdin))"\n'
                "```\n",
            )
            flagged = [e for e in audit_utf8_prefix(root) if e.type == "utf8_prefix"]
            self.assertEqual(len(flagged), 1, msg=f"got: {flagged}")
            self.assertEqual(flagged[0].artifact, "docs/sample.md:2")

    def test_continuation_pipe_jq_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_doc(
                root,
                "```bash\n"
                "uv run gz patch release --dry-run --json \\\n"
                "  | jq -r '.qualifications[].ghi.number'\n"
                "```\n",
            )
            errors = audit_utf8_prefix(root)
            self.assertTrue(
                any(e.type == "utf8_prefix" for e in errors),
                msg=f"expected utf8_prefix error, got: {errors}",
            )

    def test_continuation_pipe_with_reconfigure_passes(self) -> None:
        """A continuation whose helper reconfigures stdio is one clean logical command."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_doc(
                root,
                "```bash\n"
                "uv run gz state --json \\\n"
                '  | uv run python -c "import sys; '
                "sys.stdout.reconfigure(encoding='utf-8'); "
                "sys.stdin.reconfigure(encoding='utf-8'); print('ok')\"\n"
                "```\n",
            )
            errors = audit_utf8_prefix(root)
            self.assertFalse(errors, msg=f"expected clean, got: {errors}")

    def test_file_handoff_continuation_is_not_flagged(self) -> None:
        """``gz --json > file`` then a separate consumer line is the remediation shape."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_doc(
                root,
                "```bash\n"
                "uv run gz state --json > /tmp/state.json\n"
                "python -c \"import json; print(json.load(open('/tmp/state.json')))\"\n"
                "```\n",
            )
            errors = audit_utf8_prefix(root)
            self.assertFalse(errors, msg=f"expected clean, got: {errors}")


if __name__ == "__main__":
    unittest.main()
