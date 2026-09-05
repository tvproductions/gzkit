"""Behavior tests for the surface-delivery witness (GHI #712, GHI #580 witness half).

The witness answers a question no gate previously asked: *does the rendered
per-turn agent-contract surface still arrive intact at the vendor that consumes
it?*  Rendered ``AGENTS.md`` was measured 560 B below Codex's then-unraised
32,768 B ``project_doc_max_bytes`` with ``uv run gz check`` green (a dated 2026-07
record; gzkit now sets that cap -- GHI #962), so the tail of the
file — including ``operator-doctrine-verbatim-canon`` — could be silently
dropped without any surface going red.

Two severities, deliberately different mechanisms:

* **Fail-closed** (returned ``ValidationError``) for declaration/surface
  incoherence.  The survival declaration is gzkit's own artifact, so gating on
  it couples nothing to a vendor.
* **Warning** (stderr side effect, exit code unchanged) for everything measured
  against the vendor cap.  Operator ruling 2026-07-06 decoupled the core budget
  from the adapter limit; fail-closing on a vendor's byte cap would re-couple
  them.  ``ValidationError`` carries no severity field and every returned entry
  changes the exit code, so a non-gating finding *must* be a side effect
  (the rule stated at ``trust_audits/complexity_thresholds.py`` docstring).
"""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits.surface_delivery_witness import (
    _MAX_ADVISORY_CHARS,
    _PREFIX,
    audit_surface_delivery_witness,
)
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_surface(root: Path, sections: list[tuple[str, int]]) -> int:
    """Write a fixture surface with controlled section sizes; return its byte size.

    The size is returned rather than re-read from disk so distance assertions
    derive from what the fixture *built*, not from a second measurement of the
    same file taken the same way the audit takes it.

    `newline="\\n"` is load-bearing for exactly that property: the default
    translates each `\\n` to `os.linesep`, so on Windows the file on disk is one
    byte per line larger than the count returned here and every byte-distance
    assertion drifts by the fixture's line count.
    """
    parts = ["# Fixture\n\nPurpose line.\n\n"]
    for title, body_bytes in sections:
        parts.append(f"## {title}\n\n{'x' * body_bytes}\n\n")
    text = "".join(parts)
    (root / "AGENTS.md").write_text(text, encoding="utf-8", newline="\n")
    return len(text.encode("utf-8"))


def _write_declaration(
    root: Path,
    ranked_ids: list[str],
    must_survive_through_rank: int,
    *,
    ranks: list[int] | None = None,
) -> None:
    order = ranks if ranks is not None else list(range(1, len(ranked_ids) + 1))
    payload = {
        "surfaces": {
            "AGENTS.md": {
                "content_type": "AgentContract",
                "must_survive_through_rank": must_survive_through_rank,
                "sections": [
                    {"rank": rank, "id": section_id, "basis": "fixture"}
                    for rank, section_id in zip(order, ranked_ids, strict=True)
                ],
            }
        }
    }
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "agents_md_survival_declaration.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )


def _write_manifest(root: Path, caps: dict[str, int] | None) -> None:
    # One route, because ``AgentContract`` has exactly one destination — root
    # AGENTS.md (REQ-0.35.0-09-02/-08). The two-route shape stood here until
    # 2026-08-21 as the last of the 20 sites this OBPI's blast radius named: a
    # fixture asserting a shape the manifest fence now refuses is a fixture
    # teaching the next reader the doctrine this OBPI exists to undo.
    payload: dict[str, object] = {"content_type_routes": {"AgentContract": ["root"]}}
    if caps is not None:
        payload["content_type_delivery_caps"] = {"AgentContract": caps}
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "vendor-manifest.json").write_text(json.dumps(payload), encoding="utf-8")


def _run(root: Path) -> tuple[list, str]:
    """Run the witness, returning (fail-closed findings, stderr prose)."""
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        errors = audit_surface_delivery_witness(root)
    return errors, stderr.getvalue()


class DeclarationCoherenceFailsClosed(unittest.TestCase):
    """The declaration is gzkit's own artifact, so incoherence with it gates."""

    def test_coherent_declaration_yields_no_findings(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Alpha", 10), ("Beta", 10)])
            _write_declaration(root, ["beta", "alpha"], 1)
            _write_manifest(root, {"codex": 32768})
            errors, _ = _run(root)
        self.assertEqual(errors, [])

    def test_rendered_section_absent_from_declaration_gates(self) -> None:
        """A newly authored section must not silently inherit an undeclared rank."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Alpha", 10), ("Beta", 10), ("Gamma", 10)])
            _write_declaration(root, ["beta", "alpha"], 1)
            _write_manifest(root, {"codex": 32768})
            errors, _ = _run(root)
        self.assertTrue(errors, "an undeclared rendered section must fail closed")
        self.assertIn("gamma", " ".join(e.message for e in errors))

    def test_declared_section_absent_from_surface_gates(self) -> None:
        """A renamed/removed section must not leave a dangling must-survive rank."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Alpha", 10)])
            _write_declaration(root, ["beta", "alpha"], 1)
            _write_manifest(root, {"codex": 32768})
            errors, _ = _run(root)
        self.assertTrue(errors, "a declared section that no longer renders must fail closed")
        self.assertIn("beta", " ".join(e.message for e in errors))

    def test_non_contiguous_ranks_gate(self) -> None:
        """``must_survive_through_rank`` is meaningless over a gapped rank sequence."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Alpha", 10), ("Beta", 10)])
            _write_declaration(root, ["beta", "alpha"], 1, ranks=[1, 3])
            _write_manifest(root, {"codex": 32768})
            errors, _ = _run(root)
        self.assertTrue(errors, "gapped ranks must fail closed")

    def test_must_survive_rank_outside_declared_range_gates(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Alpha", 10), ("Beta", 10)])
            _write_declaration(root, ["beta", "alpha"], 5)
            _write_manifest(root, {"codex": 32768})
            errors, _ = _run(root)
        self.assertTrue(errors, "a must-survive cut line past the last rank must fail closed")

    def test_absent_declaration_is_not_a_finding(self) -> None:
        """Adopter projects with no declaration are unaffected by this audit."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Alpha", 10)])
            _write_manifest(root, {"codex": 32768})
            errors, output = _run(root)
        self.assertEqual(errors, [])
        self.assertEqual(output, "")

    def test_malformed_declaration_gates(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Alpha", 10)])
            (root / "data").mkdir(exist_ok=True)
            (root / "data" / "agents_md_survival_declaration.json").write_text(
                "{not json", encoding="utf-8"
            )
            _write_manifest(root, {"codex": 32768})
            errors, _ = _run(root)
        self.assertTrue(errors, "a corrupt declaration must fail closed")


class DeliveryCapIsObservedNeverGated(unittest.TestCase):
    """Everything measured against the vendor cap warns; nothing gates on it."""

    def test_headroom_is_reported_with_byte_distance(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            actual = _write_surface(root, [("Alpha", 10), ("Beta", 10)])
            _write_declaration(root, ["beta", "alpha"], 1)
            _write_manifest(root, {"codex": 4096})
            errors, output = _run(root)
        self.assertEqual(errors, [])
        self.assertIn("codex", output)
        self.assertIn(str(4096 - actual), output)

    def test_surface_over_cap_warns_but_does_not_gate(self) -> None:
        """Fail-closing here would re-couple the core to an adapter limit."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            actual = _write_surface(root, [("Alpha", 400), ("Beta", 400)])
            _write_declaration(root, ["beta", "alpha"], 1)
            _write_manifest(root, {"codex": 200})
            errors, output = _run(root)
        self.assertEqual(errors, [], "the vendor cap must never change the exit code")
        self.assertIn(str(actual - 200), output)

    def test_must_survive_section_past_cap_is_named(self) -> None:
        """The severe case: declared-unrecoverable canon is not delivered at all."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Alpha", 400), ("Beta", 10)])
            # Beta is must-survive (rank 1) but renders after Alpha, past the cap.
            _write_declaration(root, ["beta", "alpha"], 1)
            _write_manifest(root, {"codex": 200})
            errors, output = _run(root)
        self.assertEqual(errors, [])
        self.assertIn("beta", output)

    def test_must_survive_section_straddling_the_cap_is_named(self) -> None:
        """A section that BEGINS under the cap but RUNS PAST it is not delivered.

        The predicate used to ask whether the heading offset was past the cap,
        which is a weaker question than whether the section survives. The
        straddling case is both the one the committed tree actually hits —
        AGENTS.md § Architectural Boundaries begins at 32558 against a 32768 B
        codex cap and runs to 33153, losing boundaries 3 through 6 — and the
        one a heading-offset test cannot see.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Beta", 400), ("Alpha", 10)])
            # Beta is must-survive (rank 1) and renders FIRST, so its heading is
            # under the cap while its body is not.
            _write_declaration(root, ["beta", "alpha"], 1)
            _write_manifest(root, {"codex": 200})
            errors, output = _run(root)
        self.assertEqual(errors, [], "the vendor cap must never change the exit code")
        self.assertIn("beta", output)
        self.assertIn("at risk", output)

    def test_must_survive_section_within_cap_is_not_named_at_risk(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Alpha", 10), ("Beta", 10)])
            _write_declaration(root, ["beta", "alpha"], 1)
            _write_manifest(root, {"codex": 4096})
            _, output = _run(root)
        self.assertNotIn("at risk", output)

    @covers("REQ-0.35.0-09-10")
    def test_witness_measures_against_the_smallest_cap_and_names_its_vendor(self) -> None:
        """The WITNESS — not the helper — binds the strictest declared cap.

        REQ-0.35.0-09-10 says "when the surface-delivery witness runs, then it
        measures the single delivered surface against the minimum declared cap and
        names the vendor that sets it". Until 2026-08-21 both covering tests lived
        on `vendors.binding_delivery_cap`, so they proved the helper computes the
        right answer while proving nothing about whether the witness USES it — the
        Step 4b adversary (receipt
        `arb-step-codexadversary-fc821cac161042538c772cb58d0433a6`, 2026-08-18)
        demonstrated the gap by feeding the resolver a deliberately wrong result
        and watching both tests stay green.

        Every other cap test in this class declares ONE cap, which cannot separate
        "smallest" from "only". Two competing caps are what make the REQ
        falsifiable: the surface sits over the strict cap and far under the roomy
        one, so a witness taking the max, or naming the wrong vendor, fails here.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            actual = _write_surface(root, [("Alpha", 400), ("Beta", 400)])
            _write_declaration(root, ["beta", "alpha"], 1)
            _write_manifest(root, {"codex": 200, "spacious": 1_000_000})
            errors, output = _run(root)

        self.assertEqual(errors, [], "a delivery cap never changes the exit code")
        self.assertIn(
            "codex",
            output,
            "the witness must name the vendor whose cap BOUND — an operator who "
            "is not told which harness truncates cannot act on the warning",
        )
        self.assertIn(
            str(actual - 200),
            output,
            "the over-cap distance must be measured against the SMALLEST cap; "
            "measuring against the roomiest one reports headroom that no harness "
            "actually has",
        )
        self.assertNotIn(
            "spacious",
            output,
            "the roomier cap is not binding and naming it would tell the operator "
            "to trim for a harness that was never the constraint",
        )

    def test_vendor_without_declared_cap_is_not_measured(self) -> None:
        """An undeclared cap means *no known limit* — never a fabricated one."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_surface(root, [("Alpha", 10), ("Beta", 10)])
            _write_declaration(root, ["beta", "alpha"], 1)
            _write_manifest(root, None)
            errors, output = _run(root)
        self.assertEqual(errors, [])
        self.assertEqual(output, "")


class CommittedTreeIsCoherent(unittest.TestCase):
    """The witness runs clean against the real repository."""

    def test_committed_surface_and_declaration_agree(self) -> None:
        errors, _ = _run(_PROJECT_ROOT)
        self.assertEqual(
            [e.message for e in errors],
            [],
            "committed AGENTS.md and its survival declaration must agree",
        )

    def test_committed_surface_is_observed_against_its_vendor_cap(self) -> None:
        """The distance GHI #712 filed as unobserved is now actually measured.

        Asserted as behavior rather than as "the declaration file exists": if
        the declaration were deleted or stopped covering AGENTS.md, the witness
        would fall silent and this observation would disappear.
        """
        _, output = _run(_PROJECT_ROOT)
        self.assertIn("AGENTS.md", output)
        self.assertIn("codex", output)


class DeliveryRemediationOutputContract(unittest.TestCase):
    """The delivery advisory transcribes no issue state (GHI #815).

    Output-form carve-out declared: for a guardrail surface the recovery prose
    *is* the contract (``.gzkit/rules/guardrail-feedback-prose.md`` § Invariant),
    and this asserts what the prose may not contain rather than its wording.
    """

    def test_delivery_advisory_transcribes_no_issue_number(self) -> None:
        # output-contract: the advisory instructs the reader to resolve the
        # current tracker; an issue number written into it is a state claim that
        # goes stale silently.  Observed twice on this one string: it named a
        # GHI as the live record (fixed 01daaf8ae), then named one as closed --
        # false 88 minutes later when GHI #815 was reopened, and printed on
        # every `gz check` until this test.  Cite the resolver, not the record.
        _, output = _run(_PROJECT_ROOT)
        delivery = [
            line for line in output.splitlines() if "delivery cap" in line or "must-survive" in line
        ]
        self.assertTrue(delivery, "the committed surface must still emit a delivery advisory")
        self.assertNotRegex(
            "\n".join(delivery),
            r"GHI #\d+",
            "the delivery advisory must name no issue number -- a transcribed "
            "record decays when its state changes under the string",
        )

    def test_delivery_advisory_reminds_rather_than_lectures(self) -> None:
        # output-contract: this scope is a `gz check` step, so every sentence is
        # paid on every run by every session -- and trimming is not the running
        # session's job (operator ruling 2026-08-17: "let the chore manage the
        # limits ... I can't be stopping to trim them at every turn").  The
        # remedy catalogue moved to the chore; without a bound it grows back one
        # justified sentence at a time, which is how it reached ~900 chars twice
        # per run.  The number is the contract, not the wording.
        _, output = _run(_PROJECT_ROOT)
        for line in output.splitlines():
            if _PREFIX not in line:
                continue
            self.assertLessEqual(
                len(line),
                _MAX_ADVISORY_CHARS,
                f"advisory line is {len(line)} chars, over the "
                f"{_MAX_ADVISORY_CHARS}-char reminder budget -- route detail to "
                f"the chore rather than the per-turn surface: {line[:120]}...",
            )


if __name__ == "__main__":
    unittest.main()
