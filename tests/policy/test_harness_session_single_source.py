"""The harness session id is read from the environment in one place (GHI #1360).

GHI #484 corrected Claude Code's session variable in ``lock_manager`` while three
hooks kept their own copy of the read and kept the wrong variable, so every row
they wrote under Claude Code carried no session. A second copy of the read is the
failure mechanism; this fence refuses one. The scan reads raw source text, so the
hook scripts gzkit renders from template strings are covered with the modules.
"""

import re
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "gzkit"
_HOME = SRC / "lock_manager.py"
_DIRECT_READ = re.compile(
    r"""environ(?:\.get\(|\[)\s*["'](?:CLAUDE_CODE_SESSION_ID|CLAUDE_SESSION_ID|COPILOT_SESSION_ID)["']"""
)


def direct_session_reads(root: Path, home: Path) -> list[str]:
    """Return every place outside *home* that reads a harness session variable."""
    found: list[str] = []
    for path in sorted(root.rglob("*.py")):
        if path == home:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if _DIRECT_READ.search(line):
                found.append(f"{path.relative_to(root).as_posix()}:{number}")
    return found


class TestHarnessSessionIsReadInOnePlace(unittest.TestCase):
    def test_only_lock_manager_reads_the_session_variables(self):
        offenders = direct_session_reads(SRC, _HOME)
        self.assertEqual(
            offenders,
            [],
            "read the harness session through gzkit.lock_manager.harness_session_id: "
            + ", ".join(offenders),
        )

    def test_the_fence_sees_a_direct_read(self):
        # given: a scratch tree holding one direct read and the home module
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lock_manager.py").write_text(
                'os.environ.get("CLAUDE_CODE_SESSION_ID")\n', encoding="utf-8"
            )
            (root / "hook.py").write_text(
                'session = os.environ.get("CLAUDE_SESSION_ID")\n', encoding="utf-8"
            )
            # when / then: only the non-home read is reported
            self.assertEqual(direct_session_reads(root, root / "lock_manager.py"), ["hook.py:1"])


if __name__ == "__main__":
    unittest.main()
