"""Terminal-partition assertion for the foundation sunset (ADR-0.34.0 / OBPI-03).

The closed-kind assertion (OBPI-01) proves a foundation is *declared*. It says
nothing about whether that foundation is *finished*. This gate closes the second
hole: every grandfathered foundation must be terminal, witnessed by a Layer-2
``foundation_grandfathered`` ledger event — never by frontmatter, which the
ADR-0.0.37 investigation proved can lie about repudiated OBPIs.

Each test builds its own temp project root; none depends on the real
repository's foundation set, manifest, or ledger.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits.taxonomy import audit_foundation_closure
from gzkit.traceability import covers

_FOUNDATION_ADR = """---
id: {adr_id}
status: {status}
kind: foundation
semver: {semver}
lane: heavy
---

# {adr_id}: Test Foundation
"""


def _write_foundation_adr(root: Path, adr_id: str, semver: str, status: str = "Pending") -> None:
    """Write a minimal ``kind: foundation`` ADR package under ``root``."""
    pkg = root / "docs" / "design" / "adr" / "foundation" / adr_id
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / f"{adr_id}.md").write_text(
        _FOUNDATION_ADR.format(adr_id=adr_id, semver=semver, status=status),
        encoding="utf-8",
    )


def _write_manifest(root: Path, adr_ids: list[str]) -> None:
    """Declare ``adr_ids`` in the grandfather manifest under ``root``."""
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    entries = [
        {
            "id": adr_id,
            "title": "Test Foundation",
            "semver": adr_id.removeprefix("ADR-").split("-")[0],
            "frozen_at": "2026-07-19",
        }
        for adr_id in adr_ids
    ]
    (data_dir / "foundation_grandfather.json").write_text(
        json.dumps(entries, indent=2), encoding="utf-8"
    )


def _write_ledger(root: Path, events: list[dict[str, str]]) -> None:
    """Write ``events`` as the project's Layer-2 ledger."""
    gz_dir = root / ".gzkit"
    gz_dir.mkdir(parents=True, exist_ok=True)
    (gz_dir / "ledger.jsonl").write_text(
        "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8"
    )


def _grandfathered(adr_id: str) -> dict[str, str]:
    return {"event": "foundation_grandfathered", "id": adr_id, "ts": "2026-07-29T00:00:00Z"}


def _seed_declared_foundation(root: Path, adr_id: str, *, status: str = "Pending") -> None:
    """Seed a foundation that is on disk AND declared — isolating the limbo check.

    Both containment families (``foundation_kind_closed``,
    ``grandfather_dangling``) are satisfied by construction, so any finding the
    audit returns is attributable to the terminal-partition assertion alone.
    """
    _write_foundation_adr(root, adr_id, adr_id.removeprefix("ADR-").split("-")[0], status=status)
    _write_manifest(root, [adr_id])


class TestFoundationLimboGate(unittest.TestCase):
    """A grandfathered foundation with no terminal ledger witness is in limbo."""

    @covers("REQ-0.34.0-03-01")
    def test_declared_foundation_without_ledger_event_is_flagged(self) -> None:
        """A manifest entry lacking foundation_grandfathered emits foundation_limbo.

        Semantics, not string-matching: the manifest declares *membership* of
        the closed set; the ledger event witnesses *terminality*. A foundation
        that is a member but has no terminal witness is exactly the
        Pending-with-attested-work limbo ADR-0.34.0 forbids — the partition is
        only provable if every member is terminal.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_declared_foundation(root, "ADR-0.0.99-limbo")
            _write_ledger(root, [])

            errors = audit_foundation_closure(root)

            self.assertEqual(
                [e.type for e in errors],
                ["foundation_limbo"],
                "a declared foundation with no foundation_grandfathered event "
                "must emit exactly one foundation_limbo finding",
            )
            self.assertIn("ADR-0.0.99-limbo", errors[0].artifact + errors[0].message)

    @covers("REQ-0.34.0-03-01")
    def test_terminal_ledger_event_clears_the_finding(self) -> None:
        """A covering foundation_grandfathered event makes the foundation terminal.

        The negative control that gives the assertion above its meaning:
        without this, a check that flagged every manifest entry
        unconditionally would pass the test above while witnessing nothing.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_declared_foundation(root, "ADR-0.0.99-terminal")
            _write_ledger(root, [_grandfathered("ADR-0.0.99-terminal")])

            self.assertEqual(audit_foundation_closure(root), [])

    @covers("REQ-0.34.0-03-01")
    def test_frontmatter_status_cannot_clear_the_finding(self) -> None:
        """Terminal state is computed from Layer-2, so frontmatter cannot flip it.

        The load-bearing negative control. ADR-0.0.37 proved frontmatter lies
        about repudiated OBPIs, so a gate that consulted ``status:`` could be
        hand-edited green. Marking the ADR ``status: Validated`` — the most
        terminal-looking string available — must leave the finding standing,
        because the ledger still carries no witness.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_declared_foundation(root, "ADR-0.0.99-liar", status="Validated")
            _write_ledger(root, [])

            self.assertEqual(
                [e.type for e in audit_foundation_closure(root)],
                ["foundation_limbo"],
                "frontmatter `status: Validated` must not satisfy the terminal "
                "check — the gate reads the ledger, never frontmatter",
            )

    @covers("REQ-0.34.0-03-01")
    def test_undeclared_foundation_is_not_double_reported(self) -> None:
        """An undeclared foundation is closed-kind only, never also limbo.

        The predicate ranges over manifest entries, not on-disk packages. A
        foundation absent from the manifest is already a membership breach; also
        calling it non-terminal would double-count one defect and make the
        finding census unreadable at migration scale.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_foundation_adr(root, "ADR-0.0.99-undeclared", "0.0.99")
            _write_manifest(root, [])
            _write_ledger(root, [])

            self.assertEqual(
                [e.type for e in audit_foundation_closure(root)],
                ["foundation_kind_closed"],
            )

    @covers("REQ-0.34.0-03-01")
    def test_dangling_manifest_entry_is_not_double_reported(self) -> None:
        """A dangling manifest entry is dangling only, never also limbo.

        The mirror of the check above, and the one a naive
        ``declared - witnessed`` predicate gets wrong: an entry naming no
        on-disk package has nothing to be terminal *about*. Terminality ranges
        over genuine members — declared AND present — so each containment
        breach is reported exactly once.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "design" / "adr" / "foundation").mkdir(parents=True)
            _write_manifest(root, ["ADR-0.0.98-ghost"])
            _write_ledger(root, [])

            self.assertEqual(
                [e.type for e in audit_foundation_closure(root)],
                ["grandfather_dangling"],
            )


class TestFoundationLimboLedgerRobustness(unittest.TestCase):
    """A hostile or malformed ledger must not crash the gate."""

    @covers("REQ-0.34.0-03-01")
    def test_non_object_ledger_line_does_not_crash(self) -> None:
        """A valid-JSON non-object line is skipped, not dereferenced.

        `json.loads` happily returns a list, string, or number for a
        well-formed line that is not an event object. Guarding only against
        `JSONDecodeError` leaves those decoded values flowing into `.get`,
        which raises `AttributeError` and takes the whole validator down —
        a crash, not a finding. A gate that dies on one bad ledger line
        cannot report the 74 real ones.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_declared_foundation(root, "ADR-0.0.99-hostile")
            (root / ".gzkit").mkdir(parents=True, exist_ok=True)
            (root / ".gzkit" / "ledger.jsonl").write_text(
                '[]\n"a string"\n42\nnull\n', encoding="utf-8"
            )

            errors = audit_foundation_closure(root)

            self.assertEqual(
                [e.type for e in errors],
                ["foundation_limbo"],
                "non-object ledger lines must be skipped, leaving the "
                "foundation unwitnessed rather than crashing the audit",
            )

    @covers("REQ-0.34.0-03-01")
    def test_non_object_lines_do_not_mask_a_real_witness(self) -> None:
        """Skipping junk lines must not skip the real event beside them.

        The negative control: a guard that bailed out of the whole replay on
        the first bad line would satisfy the test above while silently losing
        every witness that followed it.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_declared_foundation(root, "ADR-0.0.99-mixed")
            (root / ".gzkit").mkdir(parents=True, exist_ok=True)
            (root / ".gzkit" / "ledger.jsonl").write_text(
                "[]\n" + json.dumps(_grandfathered("ADR-0.0.99-mixed")) + "\n",
                encoding="utf-8",
            )

            self.assertEqual(audit_foundation_closure(root), [])


class TestFoundationLimboExitContract(unittest.TestCase):
    """The finding must reach the operator as exit 3, not exit 1."""

    @covers("REQ-0.34.0-03-01")
    def test_limbo_is_registered_as_a_policy_breach(self) -> None:
        """`foundation_limbo` routes to exit 3, the policy-breach code.

        REQ-0.34.0-03-01 mandates exit 3, and in this CLI the exit code is
        conferred by membership in ``_POLICY_BREACH_ERROR_TYPES``: an
        unregistered finding type falls through to ``SystemExit(1)``
        (validate_cmd.py:1168) and only a registered one reaches
        ``SystemExit(3)`` (line 1170). Its two sibling closure findings are
        registered for exactly this reason.

        This is asserted at the registry rather than by scraping console
        output because the registry IS the mechanism — and because the live
        repo currently carries 74 registered `foundation_kind_closed`
        findings, which make the real command exit 3 for someone else's
        reason and mask this one entirely.
        """
        from gzkit.commands.validate_cmd import _POLICY_BREACH_ERROR_TYPES

        self.assertIn(
            "foundation_limbo",
            _POLICY_BREACH_ERROR_TYPES,
            "foundation_limbo must be a registered policy breach or the "
            "finding renders and then exits 1, violating REQ-0.34.0-03-01",
        )

    @covers("REQ-0.34.0-03-01")
    def test_taxonomy_scope_dispatch_surfaces_the_finding(self) -> None:
        """`--taxonomy`'s runner actually reaches the limbo assertion.

        Covers the link the printer test cannot: with scope dispatch broken,
        an assertion-plus-printer test still passes while the real command
        reports nothing. This drives `_taxonomy_runner` — the function the
        `--taxonomy` scope entry invokes — so a severed wiring fails here.
        """
        from gzkit.commands.validate_cmd import _taxonomy_runner

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_declared_foundation(root, "ADR-0.0.99-dispatch")
            _write_ledger(root, [])

            self.assertIn(
                "foundation_limbo",
                [e.type for e in _taxonomy_runner(root)],
                "the --taxonomy scope runner must surface foundation_limbo",
            )

    @covers("REQ-0.34.0-03-01")
    def test_isolated_limbo_finding_exits_three(self) -> None:
        """A limbo-only validation raises SystemExit(3) end-to-end.

        The negative control on the registry assertion above: it exercises
        the real renderer with ONLY a limbo finding, so nothing else can
        supply the exit code. Without the registration this observed exit 1.
        """
        from gzkit.commands.validate_cmd import _print_validation_result

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_declared_foundation(root, "ADR-0.0.99-exit")
            _write_ledger(root, [])
            findings = audit_foundation_closure(root)

        self.assertEqual([e.type for e in findings], ["foundation_limbo"])
        with self.assertRaises(SystemExit) as raised:
            _print_validation_result(findings, ["taxonomy"])

        self.assertEqual(raised.exception.code, 3)


class TestFoundationLimboProse(unittest.TestCase):
    """The finding must tell a consuming agent how to recover."""

    def _limbo_message(self, root: Path) -> str:
        """Return the sole ``foundation_limbo`` message for a seeded fixture.

        Asserts the finding exists before indexing it. Indexing straight into
        ``[0]`` would raise ``IndexError`` when the assertion is absent — a
        weak RED that proves only that a list was empty, never that the prose
        contract was violated (GHI #642 ``failure_class=error``).
        """
        _seed_declared_foundation(root, "ADR-0.0.99-prose")
        _write_ledger(root, [])
        findings = [e for e in audit_foundation_closure(root) if e.type == "foundation_limbo"]

        self.assertEqual(
            len(findings), 1, "fixture must produce exactly one foundation_limbo finding"
        )
        return findings[0].message

    @covers("REQ-0.34.0-03-02")
    def test_prose_states_it_reads_the_ledger_not_frontmatter(self) -> None:
        """The message says the check reads the ledger, so status: cannot pass it.

        Per .gzkit/rules/guardrail-feedback-prose.md part (b): the "why
        forbidden" must be cited, not implied. Here the citation carries
        operational weight — an agent that believes the gate reads frontmatter
        will try to hand-edit ``status:`` and burn a cycle on a fix that cannot
        work.
        """
        with TemporaryDirectory() as tmp:
            message = self._limbo_message(Path(tmp)).lower()

            self.assertIn("ledger", message, "must state it reads the ledger")
            self.assertIn("frontmatter", message, "must state it does NOT read frontmatter")

    @covers("REQ-0.34.0-03-02")
    def test_prose_names_both_governed_next_steps(self) -> None:
        """The message names gz closeout and gz adr demote as the recoveries.

        Part (c) of the three-part bar. Both verbs are required because the
        finding has two legitimate resolutions — finish the foundation, or drop
        it to pool — and naming only one would push every operator toward it.
        """
        with TemporaryDirectory() as tmp:
            message = self._limbo_message(Path(tmp))

            self.assertIn("gz closeout", message)
            self.assertIn("gz adr demote", message)

    @covers("REQ-0.34.0-03-02")
    def test_prose_names_what_failed(self) -> None:
        """Part (a): the message identifies the ADR and the missing witness."""
        with TemporaryDirectory() as tmp:
            message = self._limbo_message(Path(tmp))

            self.assertIn("ADR-0.0.99-prose", message)
            self.assertIn("foundation_grandfathered", message)


if __name__ == "__main__":
    unittest.main()
