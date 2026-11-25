"""The harness's identity and session variables are read in one place (GHI #1360).

GHI #484 corrected Claude Code's session variable in ``lock_manager`` while three
hooks kept their own copy of the read and kept the wrong variable, so every row
they wrote under Claude Code carried no session. A second copy of the read is the
failure mechanism, so this fence refuses one: outside ``lock_manager.py`` no Python
source under the scanned roots may hold a quoted literal of any of these names.
Any read spelled with a literal is caught that way, whatever its form
(``getenv``, a wrapped ``environ.get``, ``in``, ``setdefault``, ``pop``, an
alias), and so is a hook script gzkit renders from a template string. A name
assembled at run time is not caught.
"""

import re
import tempfile
import unittest
from pathlib import Path

from gzkit import lock_manager
from gzkit.hooks import core as hooks_core

REPO = Path(__file__).resolve().parents[2]
ROOTS = (
    REPO / "src" / "gzkit",
    REPO / "scripts",
    REPO / ".gzkit" / "skills",
    REPO / ".gzkit" / "chores",
)
HOME = REPO / "src" / "gzkit" / "lock_manager.py"
HARNESS_VARIABLES = (
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_SESSION_ID",
    "COPILOT_SESSION_ID",
    "CLAUDECODE",
    "CLAUDE_CODE",
    "CODEX_SANDBOX",
)
_LITERAL = re.compile(rf"""["'](?:{"|".join(HARNESS_VARIABLES)})["']""")

# One module body per literal read form the fence must see.
_READ_FORMS = {
    "get.py": 'os.environ.get("CLAUDE_SESSION_ID")\n',
    "subscript.py": "os.environ['CLAUDE_CODE_SESSION_ID']\n",
    "getenv.py": 'os.getenv("CLAUDE_CODE_SESSION_ID")\n',
    "wrapped.py": 'os.environ.get(\n    "CLAUDE_SESSION_ID"\n)\n',
    "membership.py": '"CLAUDECODE" in os.environ\n',
    "setdefault.py": 'os.environ.setdefault("CODEX_SANDBOX", "")\n',
    "alias.py": 'env = os.environ\nenv.pop("COPILOT_SESSION_ID", None)\n',
    "template.py": 'SCRIPT = """\nos.getenv("CLAUDE_CODE")\n"""\n',
}


def harness_variable_literals(roots: tuple[Path, ...], home: Path) -> list[str]:
    """Return every quoted harness-variable literal outside *home*, as path:line."""
    found: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if path == home:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if _LITERAL.search(line):
                    found.append(f"{path.relative_to(root.parent).as_posix()}:{number}")
    return found


class TestHarnessVariablesAreReadInOnePlace(unittest.TestCase):
    def test_only_lock_manager_names_the_harness_variables(self):
        offenders = harness_variable_literals(ROOTS, HOME)
        self.assertEqual(
            offenders,
            [],
            "read the harness identity and session through gzkit.lock_manager "
            "(resolve_agent, harness_session_id): " + ", ".join(offenders),
        )

    def test_the_fence_sees_every_literal_read_form(self):
        # given: one module per read form, beside the home module
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pkg"
            root.mkdir()
            home = root / "lock_manager.py"
            home.write_text('os.environ.get("CLAUDE_CODE_SESSION_ID")\n', encoding="utf-8")
            for name, body in _READ_FORMS.items():
                (root / name).write_text(body, encoding="utf-8")
            # when: the fence scans the tree
            hits = harness_variable_literals((root,), home)
        # then: every form is reported, and the home module is not
        self.assertEqual({hit.split(":")[0] for hit in hits}, {f"pkg/{n}" for n in _READ_FORMS})


class TestTheTemplatesImportResolves(unittest.TestCase):
    def test_hooks_core_exposes_lock_managers_reader(self):
        # The generated hooks import harness_session_id from gzkit.hooks.core and
        # swallow ImportError, so a missing re-export would silently stop them
        # recording any edit at all.
        self.assertIs(hooks_core.harness_session_id, lock_manager.harness_session_id)


if __name__ == "__main__":
    unittest.main()
