"""Forbid ``# type: ignore[<code>]`` directives naming no ty rule (GHI #197).

Unit-test entry to the audit; the canonical logic lives in
``gzkit.governance.trust_audits.audit_type_ignores`` and is also exposed as
``gz validate --type-ignores``.

Two defects shaped this file. The first was **scope**: the audit read ``src``
alone while 188 dead markers accrued under ``tests`` and 324 under ``features``
— a guard scoped away from a surface reads as covering it, so
``TypeIgnoreAuditScopeTests`` now proves each declared root is genuinely walked.
The second was **predicate**: the audit matched any bracketed
``type: ignore[``, which flags the two interop forms ty actually honors. Widening
the first without fixing the second would have propagated a false-positive class
across four more trees, so ``TypeIgnoreDiscriminationTests`` pins both
directions — what must fail, and what must not.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_type_ignores
from gzkit.governance.trust_audits.code_quality import _TYPE_IGNORE_AUDIT_ROOTS

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

_OFFENDER = "x = 1  # type: ignore[misc]\n"


def _write_at(project_root: Path, parts: tuple[str, ...], body: str) -> Path:
    """Write a fixture module into an arbitrary tree of a fake project root."""
    target = project_root.joinpath(*parts)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "fixture_mod.py"
    path.write_text(body, encoding="utf-8")
    return path


def _failure_message(findings: list[str]) -> str:
    """Three-part recovery prose: what failed, why it is forbidden, the next step."""
    return (
        "Bracketed `# type: ignore[...]` directives naming no `ty:`-prefixed code "
        "suppress nothing — ty skips foreign codes, so the diagnostic still fires "
        "(.claude/rules/pythonic.md § Type-check suppression syntax).\n"
        "Rewrite each as `# ty: ignore[<ty-code>]`, or keep the foreign code and add "
        "ty's beside it — `# type: ignore[<mypy-code>, ty:<ty-code>]`. Verify with "
        "`uv run ty check . --exclude features`.\n" + "\n".join(f"  {f}" for f in findings)
    )


class TypeIgnoreSyntaxPolicy(unittest.TestCase):
    """The real tree carries no inert suppression marker, in any scanned root."""

    def test_real_tree_has_no_inert_type_ignores(self) -> None:
        errors = audit_type_ignores(_PROJECT_ROOT)
        self.assertEqual(errors, [], msg=_failure_message([e.artifact for e in errors]))


class TypeIgnoreDiscriminationTests(unittest.TestCase):
    """Teeth and negative controls — the predicate must discriminate, not blanket-match."""

    def _scan(self, body: str) -> list[str]:
        """Scan ``body`` planted as a module inside a throwaway project root."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_at(root, ("src",), body)
            return [e.artifact for e in audit_type_ignores(root)]

    def test_foreign_code_only_is_flagged(self) -> None:
        """Teeth: a directive ty cannot read is found and located by file:line."""
        self.assertEqual(self._scan(f"x = 0\n{_OFFENDER}"), ["src/fixture_mod.py:2"])

    def test_ty_prefixed_code_in_type_ignore_is_not_flagged(self) -> None:
        """`# type: ignore[ty:<rule>]` is a WORKING suppression — flagging it is the bug.

        Verified against ty 0.0.69: this form suppressed an `invalid-assignment`
        error that `# type: ignore[misc]` left standing.
        """
        self.assertEqual(self._scan("x = 1  # type: ignore[ty:invalid-assignment]\n"), [])

    def test_interop_form_is_not_flagged(self) -> None:
        """One comment may serve two checkers; ty skips the foreign code and reads its own.

        Deleting the foreign half to satisfy a naive gate would break the other
        checker — which is why the predicate keys on absence of a `ty:` code
        rather than presence of a bracket.
        """
        scanned = self._scan("f(1)  # type: ignore[arg-type, ty:invalid-argument-type]\n")
        self.assertEqual(scanned, [])

    def test_bare_type_ignore_is_not_flagged(self) -> None:
        """Bare `# type: ignore` is valid per pythonic.md's form table — leave it alone."""
        self.assertEqual(self._scan("x = 1  # type: ignore\n"), [])

    def test_native_ty_form_is_not_flagged(self) -> None:
        """The corrected form is the fix, so it must never be reported as the defect."""
        self.assertEqual(self._scan("x = 1  # ty: ignore[invalid-assignment]\n"), [])

    def test_string_literal_containing_the_pattern_is_not_flagged(self) -> None:
        """No false positive: only COMMENT tokens count.

        Load-bearing — real fixtures under ``tests/`` carry the literal pattern
        inside string bodies to exercise the audit itself. A line-regex scan
        would flag those and force them to be corrupted to pass.
        """
        self.assertEqual(self._scan('SAMPLE = "x = 1  # type: ignore[misc]"\n'), [])

    def test_message_is_actionable(self) -> None:
        """Finding prose names both fixes and cites the governing rule."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_at(root, ("src",), _OFFENDER)
            findings = audit_type_ignores(root)

        self.assertEqual(len(findings), 1)
        message = findings[0].message
        self.assertIn("# ty: ignore[<ty-code>]", message, "must name the direct fix")
        self.assertIn("ty:<ty-code>", message, "must name the interop fix")
        self.assertIn("pythonic.md", message, "must cite the governing rule")

    def test_aggregate_failure_message_is_actionable(self) -> None:
        """The suite-level prose repeats the same three parts for a multi-site failure."""
        message = _failure_message(["tests/fixture_mod.py:2"])
        self.assertIn("tests/fixture_mod.py:2", message)
        self.assertIn("# ty: ignore[<ty-code>]", message)
        self.assertIn("pythonic.md", message)
        self.assertIn("uv run ty check", message)


class TypeIgnoreAuditScopeTests(unittest.TestCase):
    """Scanning ``src`` alone was the defect, not merely a limitation.

    512 inert markers accumulated in trees this audit declined to open, which is
    how the form the rule forbids became the repo's most common suppression
    shape. Table-driven over the declared tuple so adding a root without wiring
    it — or dropping one — fails here.
    """

    def test_every_declared_root_is_actually_scanned(self) -> None:
        """Each declared root must really be walked, not merely listed.

        Asserts scanning BEHAVIOR — a planted marker is found and named by
        relative path — rather than that the directory exists on disk, which
        would prove content rather than behavior.
        """
        for parts in _TYPE_IGNORE_AUDIT_ROOTS:
            rendered = "/".join(parts)
            with self.subTest(root=rendered), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _write_at(root, parts, _OFFENDER)
                findings = audit_type_ignores(root)
                self.assertEqual(len(findings), 1, f"declared root {rendered} is not scanned")
                self.assertIn(f"{rendered}/fixture_mod.py", findings[0].artifact)

    def test_an_unscanned_sibling_tree_is_not_swept_in(self) -> None:
        """Negative control: scope is the declared tuple, not "every .py in the repo".

        Without this, the positive cases above are equally satisfied by an audit
        that walks the whole project — which would flag the generated vendor
        mirrors under ``.agents``/``.github``, where a marker cannot be fixed
        because the file is a copy. ``docs/`` stands in for any tree outside the
        tuple.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_at(root, ("docs",), _OFFENDER)
            self.assertEqual(audit_type_ignores(root), [])


if __name__ == "__main__":
    unittest.main()
