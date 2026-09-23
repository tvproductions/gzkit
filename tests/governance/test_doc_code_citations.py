"""Governance prose citing a `src/gzkit/` module must cite one that exists (GHI #1083).

`audit_skill_code_citations` (GHI #896) resolves exactly these citations over
``.gzkit/skills/**/SKILL.md``, and declined to widen its population without
measuring first, citing GHI #854. The measurement arrived: when this arm landed,
``docs/governance/**`` cited 123 distinct ``src/gzkit/`` paths and six did not
resolve. Two of the six -- ``src/gzkit/cli.py`` and
``src/gzkit/governance/trust_audits.py`` -- are paths GHI #896 REPAIRED in the
skills population and left rotting in this one, because the arm it built could
not see here. ``uv run gz check`` was green throughout.

Governance prose differs from skill prose in one way that shapes the arm:
it legitimately cites a path that does not resolve. Three shapes were measured
at #1083 -- a dated audit record citing a path correct at its date; corrective
prose quoting a superseded path beside its replacement; and an unexecuted
campaign spec naming a module it proposes to build. The third is why the
invariant is not simply "every cited path resolves":
``src/gzkit/governance/vocabulary.py`` has never existed in git history, and its
document is headed *PREPARED -- NOT YET EXECUTED*.

Scope is the existence half only, as in the sibling arm. Whether a cited LINE
still holds drifts on every edit to the cited file and is not claimed here.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_doc_code_citations

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_MARKER = "<!-- gz-validate-skip: code-citation -->"


def _write_doc(root: Path, *, name: str, body: str) -> Path:
    docs = root / "docs" / "governance"
    docs.mkdir(parents=True, exist_ok=True)
    doc = docs / name
    doc.write_text(f"# {name}\n\n{body}\n", encoding="utf-8")
    return doc


def _write_module(root: Path, relpath: str) -> None:
    target = root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("", encoding="utf-8")


class DocCodeCitationBehavior(unittest.TestCase):
    """The arm fails closed on a cited module that does not exist."""

    def test_dangling_citation_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(root, name="runbook.md", body="- Implementation: `src/gzkit/gone.py`")
            errors = audit_doc_code_citations(root)

        self.assertEqual(len(errors), 1, f"expected one error, got {errors}")
        self.assertEqual(errors[0].type, "doc_code_citation")
        self.assertIn("src/gzkit/gone.py", errors[0].message)

    def test_resolving_citation_is_not_flagged(self) -> None:
        """The valid control: 117 of the 123 measured citations are this shape."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_module(root, "src/gzkit/here.py")
            _write_doc(root, name="runbook.md", body="- Implementation: `src/gzkit/here.py`")
            self.assertEqual(audit_doc_code_citations(root), [])

    def test_package_split_recovery_names_the_package(self) -> None:
        """A module that became a package is the shape that produced this defect twice."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_module(root, "src/gzkit/thing/__init__.py")
            _write_doc(root, name="runbook.md", body="- Implementation: `src/gzkit/thing.py`")
            errors = audit_doc_code_citations(root)

        self.assertEqual(len(errors), 1)
        self.assertIn("src/gzkit/thing/", errors[0].message)

    def test_marked_item_is_exempt(self) -> None:
        """Historical, corrective and prospective citations are exempted by the marker."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(
                root,
                name="record.md",
                body=f"{_MARKER}\n- As it stood: `src/gzkit/gone.py`",
            )
            self.assertEqual(audit_doc_code_citations(root), [])

    def test_exemption_does_not_leak_to_the_sibling_item(self) -> None:
        """The marker exempts ONE item, not the contiguous list it sits in.

        A Markdown list has no blank line between its items, so scoping the
        marker to the next blank line would exempt every sibling. The amendment
        log of a living register is exactly this shape: one corrective entry
        quoting a superseded path, surrounded by entries that must still be
        checked.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(
                root,
                name="amendments.md",
                body=(
                    f"{_MARKER}\n"
                    "- Corrected: `src/gzkit/old.py` is now elsewhere.\n"
                    "- Unrelated later entry citing `src/gzkit/also_gone.py`.\n"
                ),
            )
            errors = audit_doc_code_citations(root)

        self.assertEqual(len(errors), 1, f"the sibling item must still be checked: {errors}")
        self.assertIn("src/gzkit/also_gone.py", errors[0].message)

    def test_marker_exempts_a_wrapped_paragraph_through_its_continuation_lines(self) -> None:
        """Governance prose is hard-wrapped, so a citation sits mid-paragraph."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(
                root,
                name="prose.md",
                body=(
                    f"{_MARKER}\n"
                    "Did not resolve as cited: the path below was wrong and is\n"
                    "recorded here as `src/gzkit/gone.py` beside its replacement.\n"
                ),
            )
            self.assertEqual(audit_doc_code_citations(root), [])

    def test_citation_inside_a_fenced_block_is_not_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(
                root,
                name="example.md",
                body="```bash\ncat src/gzkit/gone.py\n```",
            )
            self.assertEqual(audit_doc_code_citations(root), [])

    def test_citation_reports_its_line_number(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = _write_doc(root, name="runbook.md", body="filler\n\n- `src/gzkit/gone.py`")
            errors = audit_doc_code_citations(root)
            lineno = int(errors[0].artifact.rsplit(":", 1)[1])
            self.assertEqual(
                doc.read_text(encoding="utf-8").splitlines()[lineno - 1].strip(),
                "- `src/gzkit/gone.py`",
            )


class DocCodeCitationRepoClean(unittest.TestCase):
    """The repository's own governance prose satisfies the arm."""

    def test_repo_governance_docs_cite_only_modules_that_exist(self) -> None:
        errors = audit_doc_code_citations(_PROJECT_ROOT)
        self.assertEqual(errors, [], f"unresolved citations: {[e.artifact for e in errors]}")


if __name__ == "__main__":
    unittest.main()
