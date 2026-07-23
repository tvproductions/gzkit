"""Self-referential fidelity-assertion guard (GHI #702).

A fidelity row whose command invokes the fidelity gate itself
(``gz adr fidelity``) is tautological: the gate must reach the row to run it, so
the row can never be red while it is being evaluated. Its subject is the parser,
not the ADR's thesis — it inflates the witness count without exercising the
delivered surface (the ``copy-vs-self`` theater signature #699 names).

These tests pin the guard at every consumer of the parse chokepoint:

* ``parse_fidelity_assertions`` raises ``PolicyBreachError`` (exit 3, *not* a
  ``ValueError`` — so the absence handlers in ``assert_fidelity_for_ceremony``
  and ``adr_fidelity_cmd`` cannot silently downgrade it to "no block").
* ``assert_fidelity_for_ceremony`` hard-blocks (closeout + audit consumers).
* ``audit_fidelity_presence`` reports a ``fidelity-self-reference`` finding, so
  ``gz check`` fails closed on any ADR that re-introduces the row.
* No ADR shipped in the tree carries the row (the sweep is pinned).

Direct-fix work under GHI #702 — no covering REQ, so no ``@covers``.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path


class TestIsSelfReferentialCommand(unittest.TestCase):
    """The detector recognizes `gz adr fidelity` and nothing else."""

    def test_flags_check_form(self) -> None:
        from gzkit.fidelity import is_self_referential_command

        self.assertTrue(
            is_self_referential_command(
                "uv run gz adr fidelity ADR-0.0.37-constitutional-invariant-composition --check"
            )
        )

    def test_flags_run_form(self) -> None:
        from gzkit.fidelity import is_self_referential_command

        self.assertTrue(is_self_referential_command("uv run gz adr fidelity ADR-0.0.9"))

    def test_flags_bare_gz_prefix(self) -> None:
        from gzkit.fidelity import is_self_referential_command

        self.assertTrue(is_self_referential_command("gz adr fidelity ADR-0.0.9 --check"))

    def test_ignores_unittest_command(self) -> None:
        from gzkit.fidelity import is_self_referential_command

        self.assertFalse(
            is_self_referential_command(
                "uv run -m unittest tests.commands.test_validate_frontmatter"
            )
        )

    def test_ignores_other_gz_verbs(self) -> None:
        from gzkit.fidelity import is_self_referential_command

        self.assertFalse(is_self_referential_command("uv run gz status"))
        # `gz adr audit` is a sibling verb — NOT the fidelity gate.
        self.assertFalse(is_self_referential_command("uv run gz adr audit ADR-0.0.9"))

    def test_malformed_command_is_not_self_referential(self) -> None:
        from gzkit.fidelity import is_self_referential_command

        # Unbalanced quote → shlex.split raises; a command we cannot tokenize is
        # not self-referential (the downstream runner already handles it).
        self.assertFalse(is_self_referential_command('uv run gz adr fidelity "unterminated'))


_ADR_SELF_REF = textwrap.dedent("""\
    ---
    id: ADR-selfref
    ---

    # ADR Self Ref

    ## Decision

    Text.

    ## Fidelity Assertions

    | Claim | Command | Expected exit |
    |-------|---------|---------------|
    | Real delivered surface exercised. | uv run gz status | 0 |
    | Block parseable by the gate. | uv run gz adr fidelity ADR-selfref --check | 0 |

    ## Evidence
    """)


class TestParseRejectsSelfReferential(unittest.TestCase):
    """The parse chokepoint rejects a self-referential row with a hard breach."""

    def _write(self, content: str) -> Path:
        tmp = tempfile.mkdtemp(prefix="gzkit-selfref-")
        path = Path(tmp) / "ADR-selfref.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_parse_raises_policy_breach(self) -> None:
        from gzkit.core.exceptions import PolicyBreachError
        from gzkit.fidelity import parse_fidelity_assertions

        adr_path = self._write(_ADR_SELF_REF)
        with self.assertRaises(PolicyBreachError):
            parse_fidelity_assertions(adr_path)

    def test_breach_is_not_a_value_error(self) -> None:
        """The breach must NOT be a ValueError — the absence handlers catch that.

        ``assert_fidelity_for_ceremony`` and ``adr_fidelity_cmd`` both wrap parse
        in ``except ValueError`` to model an *absent* block as a warning. If the
        self-reference breach were a ValueError it would be silently downgraded to
        "no block" and never block the ceremony — the exact bypass this guard
        exists to close.
        """
        from gzkit.fidelity import parse_fidelity_assertions

        adr_path = self._write(_ADR_SELF_REF)
        with self.assertRaises(Exception) as ctx:  # noqa: B017 — asserting the type below
            parse_fidelity_assertions(adr_path)
        self.assertNotIsInstance(ctx.exception, ValueError)


class TestCeremonyGateBlocksSelfReferential(unittest.TestCase):
    """Both ceremony consumers hard-block on a self-referential row."""

    def test_ceremony_gate_raises_policy_breach(self) -> None:
        from gzkit.core.exceptions import PolicyBreachError
        from gzkit.fidelity import assert_fidelity_for_ceremony

        tmp = tempfile.mkdtemp(prefix="gzkit-selfref-ceremony-")
        adr_path = Path(tmp) / "ADR-selfref.md"
        adr_path.write_text(_ADR_SELF_REF, encoding="utf-8")
        with self.assertRaises(PolicyBreachError):
            assert_fidelity_for_ceremony(adr_path, "ADR-selfref")


class TestPresenceAuditFlagsSelfReferential(unittest.TestCase):
    """`gz validate --fidelity-presence` reports self-reference as a finding.

    The presence audit parses every non-pool ADR Decision; a self-referential
    row must surface as a ``fidelity-self-reference`` ValidationError (fail-closed
    at ``gz check``) rather than crash the walk with an uncaught breach.
    """

    def _adr_tree(self, content: str) -> Path:
        root = Path(tempfile.mkdtemp(prefix="gzkit-selfref-presence-"))
        pkg = root / "docs" / "design" / "adr" / "foundation" / "ADR-selfref"
        pkg.mkdir(parents=True)
        (pkg / "ADR-selfref.md").write_text(content, encoding="utf-8")
        return root

    def test_audit_emits_self_reference_error(self) -> None:
        from gzkit.governance.trust_audits.fidelity_presence import audit_fidelity_presence

        root = self._adr_tree(_ADR_SELF_REF)
        errors = audit_fidelity_presence(root, grandfather=frozenset())
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "fidelity-self-reference")

    def test_clean_block_passes(self) -> None:
        from gzkit.governance.trust_audits.fidelity_presence import audit_fidelity_presence

        clean = textwrap.dedent("""\
            ---
            id: ADR-selfref
            ---

            # ADR Clean

            ## Decision

            Text.

            ## Fidelity Assertions

            | Claim | Command | Expected exit |
            |-------|---------|---------------|
            | Real delivered surface exercised. | uv run gz status | 0 |

            ## Evidence
            """)
        root = self._adr_tree(clean)
        errors = audit_fidelity_presence(root, grandfather=frozenset())
        self.assertEqual(errors, [])


class TestCorpusHasNoSelfReferentialRow(unittest.TestCase):
    """No shipped ADR Decision carries the tautological parseability row.

    Pins the GHI #702 sweep: a regression that re-adds the row to any ADR reddens
    here (and, live, at `gz validate --fidelity-presence`).
    """

    def test_no_adr_decision_ships_self_reference(self) -> None:
        # Extract command cells DIRECTLY from the block, independent of
        # parse_fidelity_assertions — which now *raises* on exactly these rows, so
        # a parse-based scan would skip the files it must catch (a false green).
        from gzkit.fidelity import (
            _extract_fidelity_block,
            _strip_inline_code,
            is_self_referential_command,
        )

        repo_root = Path(__file__).resolve().parents[2]
        adr_root = repo_root / "docs" / "design" / "adr"
        offenders: list[str] = []
        for adr_file in adr_root.rglob("ADR-*.md"):
            # Decision files only (stem == parent dir); skip AUDIT sidecars, which
            # legitimately *document* the tautology finding in prose.
            if adr_file.stem != adr_file.parent.name:
                continue
            block = _extract_fidelity_block(adr_file.read_text(encoding="utf-8"))
            for line in block:
                if not line.strip().startswith("|") or set(line.strip()) <= set("|- :"):
                    continue
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) < 3:
                    continue
                if is_self_referential_command(_strip_inline_code(cells[1])):
                    offenders.append(adr_file.relative_to(repo_root).as_posix())
        self.assertEqual(
            offenders, [], f"self-referential fidelity rows still present: {offenders}"
        )


if __name__ == "__main__":
    unittest.main()
