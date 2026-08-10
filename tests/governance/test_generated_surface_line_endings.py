r"""Every generated-surface writer pins `newline="\n"` (GHI #681).

WHY: `.claude/rules/cross-platform.md` holds "Windows, macOS, Linux — co-equal",
and `gz validate --surfaces` / `--distribution` compare generated surfaces by RAW
BYTES. With `newline` unset, Python translates `\n` to `os.linesep` on write
(documented behavior), so a writer emits CRLF on Windows and LF elsewhere — two
byte strings for one logical surface, and a byte-comparison gate that fails on one
platform only.

This suite exists because the GHI #681 fix was scoped to a MODULE while the defect
is a CLASS: that issue enumerated "8 write sites in `src/gzkit/sync_surfaces.py`",
which were fixed, while four other surface writers were left translating. It
resurfaced 28 days later as 43 self-inflicted drift errors and a validator that
dirtied a clean tree. Per `AGENTS.md` § DO IT RIGHT #1 — fix the class.

The scan lives in `src/gzkit/governance/trust_audits/cross_platform.py` beside
`audit_subprocess_errors`, following that audit's precedent: the detector is
production code and these tests assert its BEHAVIOR. Reading the source tree from
inside the test instead would make the assertions filesystem-shaped, which is the
co-occurrence `gz validate --tautological-test-audit` flags and the shape
`.gzkit/rules/tests.md` § The discriminator rejects.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits.cross_platform import (
    _SURFACE_WRITER_MODULES,
    audit_generated_surface_newlines,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _fixture_root(source: str, rel: str = "sync_surfaces.py") -> TemporaryDirectory:
    """Build a throwaway tree carrying EVERY surface-writer module.

    All of them, not just the one under probe: the audit reports an absent module
    as a finding (so a rename cannot buy silence), so a fixture holding one module
    would return that finding four times over and drown the signal being asserted.
    The modules not under probe get a benign pinned write.
    """
    tmp = TemporaryDirectory()
    for name in _SURFACE_WRITER_MODULES:
        target = Path(tmp.name) / "src" / "gzkit" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        body = source if name == rel else 'p.write_text(x, newline="\\n")\n'
        target.write_text(body, encoding="utf-8", newline="\n")
    return tmp


class GeneratedSurfaceWritesArePlatformInvariantTests(unittest.TestCase):
    """A generated surface must be byte-identical on every co-equal platform."""

    def test_the_repository_has_no_unpinned_surface_write(self) -> None:
        """The live guard: every in-scope writer pins LF today."""
        findings = audit_generated_surface_newlines(_REPO_ROOT)
        self.assertEqual(
            [],
            [f.artifact for f in findings],
            msg="A generated-surface writer stopped pinning newline='\\n' (GHI #681).",
        )

    def test_an_unpinned_write_text_is_flagged(self) -> None:
        """Negative control — without this the audit could pass while blind."""
        with _fixture_root('p.write_text(x, encoding="utf-8")\n') as root:
            findings = audit_generated_surface_newlines(Path(root))
        self.assertEqual(1, len(findings), "an unpinned write_text must flag")
        self.assertEqual("generated_surface_newlines", findings[0].type)
        self.assertIn("sync_surfaces.py", findings[0].artifact)

    def test_a_pinned_write_text_is_not_flagged(self) -> None:
        """The pin is what satisfies the audit — nothing else."""
        with _fixture_root('p.write_text(x, encoding="utf-8", newline="\\n")\n') as root:
            self.assertEqual([], audit_generated_surface_newlines(Path(root)))

    def test_binary_writes_are_exempt(self) -> None:
        """`write_bytes` and `open(..., "wb")` perform no newline translation.

        Flagging them would push authors toward a meaningless kwarg and would
        wrongly condemn `sync_parity._restore`, which is correct as written.
        """
        for source in ("p.write_bytes(b)\n", 'open(p, "wb")\n'):
            with self.subTest(source=source), _fixture_root(source) as root:
                self.assertEqual([], audit_generated_surface_newlines(Path(root)))

    def test_text_mode_open_is_covered_too(self) -> None:
        """`open(p, "w")` translates exactly as `write_text` does."""
        with _fixture_root('open(p, "w")\n') as root:
            self.assertEqual(1, len(audit_generated_surface_newlines(Path(root))))
        with _fixture_root('open(p, "w", newline="\\n")\n') as root:
            self.assertEqual([], audit_generated_surface_newlines(Path(root)))

    def test_a_renamed_module_fails_loudly_rather_than_scanning_nothing(self) -> None:
        """Silence must not be reachable by deleting the thing under audit."""
        with TemporaryDirectory() as empty:
            findings = audit_generated_surface_newlines(Path(empty))
        self.assertTrue(findings, "an absent surface-writer module must be reported")


if __name__ == "__main__":
    unittest.main()
