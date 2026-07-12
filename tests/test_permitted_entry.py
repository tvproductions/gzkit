"""Unit tests for the permitted-entry airlock door (OBPI-0.33.0-05).

The third airlock door — the ad-hoc/spurious entry (reconnaissance for
comprehension, light repair at most). It CONSUMES the SHARED primitive extracted
by OBPI-02/03 (``gzkit.airlock.enter.airlock_enter`` /
``gzkit.airlock.exit.airlock_exit``), never forking a private variant, and closes
the silent-bypass hole: an ad-hoc entry that formerly crossed NO membrane now
leaves an ``airlock_in`` / ``airlock_out`` L2 record.

Diagnostic-only tracer at permissive intent (parent ADR option-c reconcile): the
acknowledge-and-decide gate LOGS its decision; per-door ceremony-weight calibration
and brief-less DECLARE richness are the attested deferred frontier.

REQ-0.33.0-05-01..06 are BEHAVIOR REQs proven by the ``@covers`` methods below.
REQ-0.33.0-05-07 is STRUCTURAL-FENCE (parent-ADR ## Boundary Invariants #3,
audited at ADR closeout) — no ``@covers`` test, by proof channel (ADR-0.0.59).
"""

from __future__ import annotations

import inspect
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit.airlock.exit import Door
from gzkit.commands import permitted_entry
from gzkit.commands.permitted_entry import RepairScope, classify_repair
from gzkit.traceability import covers
from tests.commands.common import SilencedConsoleTestCase


def _mk_root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root


def _mk_target(root: Path, relpath: str = "notes.txt", body: str = "original content\n") -> str:
    target = root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return relpath


def _events(root: Path, event_type: str) -> list[dict]:
    p = root / ".gzkit" / "ledger.jsonl"
    if not p.exists():
        return []
    out: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("event") == event_type:
            out.append(ev)
    return out


class TestGateAlwaysFires(SilencedConsoleTestCase):
    """REQ-0.33.0-05-01: the door ALWAYS calls the shared primitive — the gate fires."""

    @covers("REQ-0.33.0-05-01")
    def test_bare_recon_entry_books_airlock_in(self) -> None:
        # The gate is realized by the door CALLING the primitive; a bare recon entry
        # produces a gate decision (an airlock_in L2 encounter).
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            target = _mk_target(root)
            permitted_entry.permitted_entry_cmd(target=target, recon=True, project_root=root)
            self.assertEqual(
                len(_events(root, "airlock_in")),
                1,
                "a bare recon entry must fire the gate (book one airlock_in)",
            )

    @covers("REQ-0.33.0-05-01")
    def test_no_entry_variant_reaches_exit_without_firing_the_gate(self) -> None:
        # BI-2: the reason/door selects ceremony weight, never WHETHER the gate fires.
        # Every entry variant (recon, light repair, beyond-ceiling) must call airlock_enter.
        variants = (
            {"recon": True},
            {"repair": "fix a typo"},
            {"repair": "refactor the schema"},
        )
        for kwargs in variants:
            with TemporaryDirectory() as tmp:
                root = _mk_root(tmp)
                target = _mk_target(root)
                with patch.object(
                    permitted_entry, "airlock_enter", wraps=permitted_entry.airlock_enter
                ) as spy:
                    permitted_entry.permitted_entry_cmd(target=target, project_root=root, **kwargs)
                self.assertEqual(
                    spy.call_count, 1, f"the gate must fire for entry variant {kwargs!r}"
                )


class TestReconIsTheDefault(SilencedConsoleTestCase):
    """REQ-0.33.0-05-02: recon default — no mutation, non-empty comprehension report."""

    @covers("REQ-0.33.0-05-02")
    def test_recon_mutates_nothing_and_reports(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            target = _mk_target(root, body="untouched\n")
            with patch.object(permitted_entry.console, "print") as pr:
                permitted_entry.permitted_entry_cmd(target=target, recon=True, project_root=root)
            self.assertEqual(
                (root / target).read_text(encoding="utf-8"),
                "untouched\n",
                "a recon-only entry performs NO file mutation",
            )
            printed = " ".join(str(c.args[0]) for c in pr.call_args_list if c.args)
            self.assertTrue(printed.strip(), "recon yields a non-empty comprehension report")
            self.assertIn(target, printed, "the report names the reconnoitered target")

    @covers("REQ-0.33.0-05-02")
    def test_reconnaissance_is_the_default_with_no_flag_and_no_repair(self) -> None:
        # Codex Step-4b (GHI #678): the prior test passed recon=True, so it never
        # exercised the TRUE default. With neither --recon nor --repair, the door must
        # still behave as reconnaissance: no mutation, a comprehension report, no
        # ceiling/fresh-transit verdict.
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            target = _mk_target(root, body="default recon\n")
            with patch.object(permitted_entry.console, "print") as pr:
                permitted_entry.permitted_entry_cmd(target=target, project_root=root)
            printed = " ".join(str(c.args[0]) for c in pr.call_args_list if c.args).lower()
            self.assertEqual(
                (root / target).read_text(encoding="utf-8"),
                "default recon\n",
                "the no-flag default performs no mutation",
            )
            self.assertIn("recon", printed, "the no-flag default yields a comprehension report")
            self.assertNotIn("ceiling", printed, "no repair intent → no ceiling verdict")

    @covers("REQ-0.33.0-05-02")
    def test_recon_and_repair_are_mutually_exclusive_fail_fast(self) -> None:
        # --recon (recon-only) and --repair (a change intent) are contradictory. The
        # door FAILS FAST rather than silently dropping the repair — a silent drop would
        # let a beyond-ceiling intent evade the ceiling (REQ-03) and routing (REQ-04) by
        # adding --recon (Codex Step-4b, GHI #678). No beyond-ceiling repair can vanish.
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            target = _mk_target(root, body="untouched\n")
            with self.assertRaises(SystemExit) as ctx:
                permitted_entry.permitted_entry_cmd(
                    target=target,
                    recon=True,
                    repair="rewrite the module to eliminate the deadlock",
                    project_root=root,
                )
            self.assertEqual(ctx.exception.code, 1, "the conflicting invocation fails fast, exit 1")
            self.assertEqual(
                (root / target).read_text(encoding="utf-8"),
                "untouched\n",
                "the rejected invocation performs no mutation",
            )
            self.assertEqual(
                _events(root, "airlock_in"),
                [],
                "the rejected invocation never enters the airlock — the repair cannot be smuggled",
            )


class TestLightRepairCeiling(SilencedConsoleTestCase):
    """REQ-0.33.0-05-03: light repair is the CEILING — within accepted, beyond refused."""

    @covers("REQ-0.33.0-05-03")
    def test_classify_within_and_beyond_ceiling(self) -> None:
        self.assertIs(classify_repair(None), RepairScope.NONE)
        self.assertIs(classify_repair("   "), RepairScope.NONE)
        self.assertIs(classify_repair("fix typo in badge line"), RepairScope.LIGHT)
        self.assertIs(classify_repair("refactor event schema"), RepairScope.BEYOND)
        self.assertIs(classify_repair("rewrite the ledger module"), RepairScope.BEYOND)
        # De-leaked structural verbs (adversary caveat 2): clearly-heavy intents that
        # name a structural verb trip the tripwire, not slip through as LIGHT.
        self.assertIs(classify_repair("delete the ledger module"), RepairScope.BEYOND)
        self.assertIs(classify_repair("implement a new database backend"), RepairScope.BEYOND)
        self.assertIs(classify_repair("replace the whole auth layer"), RepairScope.BEYOND)
        # Punctuation/quoting/bracketing/hyphenation around a structural verb must not
        # let it evade the ceiling (Codex Step-4b, GHI #678) — tokens normalize to their
        # alphanumeric core, so all of these still trip BEYOND.
        self.assertIs(classify_repair('"rewrite" the module'), RepairScope.BEYOND)
        self.assertIs(classify_repair("[rewrite] the module"), RepairScope.BEYOND)
        self.assertIs(classify_repair("re-write the module"), RepairScope.BEYOND)
        self.assertIs(classify_repair("ReWrItE the module"), RepairScope.BEYOND)

    @covers("REQ-0.33.0-05-03")
    def test_operator_repair_text_cannot_inject_or_crash_rich_markup(self) -> None:
        # Operator-controlled repair text is escaped before entering Rich markup: a
        # malformed tag must NOT crash, and bracketed text must render verbatim, not be
        # swallowed as markup (Codex Step-4b, GHI #678).
        from rich.console import Console  # noqa: PLC0415

        for intent in ("[/rewrite] the module", "[rewrite] the module", "[bold]x[/bold] rewrite"):
            with TemporaryDirectory() as tmp:
                root = _mk_root(tmp)
                target = _mk_target(root)
                buffer = io.StringIO()
                cons = Console(file=buffer, force_terminal=False)
                with patch.object(permitted_entry, "console", cons):
                    permitted_entry.permitted_entry_cmd(
                        target=target, repair=intent, project_root=root
                    )
                # No traceback (the call returned) and the literal text is present verbatim.
                self.assertIn(intent, buffer.getvalue(), f"repair text {intent!r} renders verbatim")

    @covers("REQ-0.33.0-05-03")
    def test_beyond_ceiling_is_refused_for_inline_execution(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            target = _mk_target(root, body="keep me\n")
            with patch.object(permitted_entry.console, "print") as pr:
                permitted_entry.permitted_entry_cmd(
                    target=target, repair="refactor event schema", project_root=root
                )
            self.assertEqual(
                (root / target).read_text(encoding="utf-8"),
                "keep me\n",
                "a beyond-ceiling intent is REFUSED for inline execution — no mutation",
            )
            printed = " ".join(str(c.args[0]) for c in pr.call_args_list if c.args)
            self.assertIn(
                "ceiling", printed.lower(), "the refusal names the exceeded light-repair ceiling"
            )


class TestTripToFreshTransit(SilencedConsoleTestCase):
    """REQ-0.33.0-05-04: beyond-ceiling trips a fresh transit naming the routed door."""

    @covers("REQ-0.33.0-05-04")
    def test_beyond_ceiling_presents_both_doors_without_an_authoritative_pick(self) -> None:
        # Codex Step-4b (GHI #678): the door does NOT authoritatively guess the door
        # from free text — an open-ended keyword list always misroutes some corrective
        # phrasing. It presents BOTH doors with their criteria; the captain chooses.
        # Verified across intentional AND corrective phrasings that a keyword heuristic
        # would have split — both must present the same both-doors menu.
        for intent in (
            "refactor the event schema",  # intentional
            "rewrite the module to eliminate the deadlock",  # corrective (Codex probe)
            "replace the parser because it emits malformed output",  # corrective (Codex probe)
        ):
            with TemporaryDirectory() as tmp:
                root = _mk_root(tmp)
                target = _mk_target(root, body="stable\n")
                with patch.object(permitted_entry.console, "print") as pr:
                    permitted_entry.permitted_entry_cmd(
                        target=target, repair=intent, project_root=root
                    )
                printed = " ".join(str(c.args[0]) for c in pr.call_args_list if c.args)
                self.assertIn(Door.PIPELINE.value, printed, f"pipeline door offered for {intent!r}")
                self.assertIn(Door.MX.value, printed, f"mx door offered for {intent!r}")
                # No authoritative primary: the word "recommended door" must NOT appear —
                # the captain picks, so a corrective intent is never silently misrouted.
                self.assertNotIn(
                    "recommended door",
                    printed.lower(),
                    f"no authoritative door pick for {intent!r} (both offered, captain chooses)",
                )
                self.assertEqual(
                    (root / target).read_text(encoding="utf-8"),
                    "stable\n",
                    "no inline mutation — the work is routed as a fresh transit, never smuggled",
                )


class TestNoPrivateFork(SilencedConsoleTestCase):
    """REQ-0.33.0-05-05: consume the SHARED primitive; no private airlock (BI-3)."""

    @covers("REQ-0.33.0-05-05")
    def test_imports_airlock_from_the_single_extracted_source(self) -> None:
        import gzkit.airlock.enter as enter_mod
        import gzkit.airlock.exit as exit_mod

        self.assertIs(
            permitted_entry.airlock_enter,
            enter_mod.airlock_enter,
            "the door imports airlock_enter from gzkit.airlock.enter (single source)",
        )
        self.assertIs(
            permitted_entry.airlock_exit,
            exit_mod.airlock_exit,
            "the door imports airlock_exit from gzkit.airlock.exit (single source)",
        )

    @covers("REQ-0.33.0-05-05")
    def test_door_declares_no_local_airlock_reimplementation(self) -> None:
        src = inspect.getsource(permitted_entry)
        self.assertNotIn("def airlock_enter", src, "no local airlock_enter fork")
        self.assertNotIn("def airlock_exit", src, "no local airlock_exit fork")
        self.assertNotIn("class SeamMap", src, "no local SeamMap fork — consume the shared model")


class TestSilentBypassCloses(SilencedConsoleTestCase):
    """REQ-0.33.0-05-06: the ad-hoc entry now books airlock_in AND airlock_out to L2."""

    @covers("REQ-0.33.0-05-06")
    def test_ad_hoc_entry_leaves_an_accountable_transit_record(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            target = _mk_target(root)
            permitted_entry.permitted_entry_cmd(target=target, recon=True, project_root=root)
            self.assertEqual(
                len(_events(root, "airlock_in")),
                1,
                "the formerly membrane-less ad-hoc entry now books airlock_in",
            )
            self.assertEqual(
                len(_events(root, "airlock_out")),
                1,
                "the co-equal exit membrane books airlock_out — the transit is accountable",
            )

    @covers("REQ-0.33.0-05-06")
    def test_blank_target_books_no_anonymous_transit(self) -> None:
        # An empty/whitespace target is rejected BEFORE any airlock entry — it would
        # otherwise book anonymous, misbound airlock_in/airlock_out records with an
        # empty id, defeating REQ-06 accountability (Codex Step-4b, GHI #678).
        for blank in ("", "   "):
            with TemporaryDirectory() as tmp:
                root = _mk_root(tmp)
                with self.assertRaises(SystemExit) as ctx:
                    permitted_entry.permitted_entry_cmd(target=blank, recon=True, project_root=root)
                self.assertEqual(ctx.exception.code, 1)
                self.assertEqual(
                    _events(root, "airlock_in"), [], "a blank target books no airlock_in"
                )
                self.assertEqual(
                    _events(root, "airlock_out"), [], "a blank target books no airlock_out"
                )

    @covers("REQ-0.33.0-05-06")
    def test_wildcard_target_does_not_select_an_unrelated_artifact(self) -> None:
        # Glob metacharacters in the target are escaped so a wildcard cannot select an
        # unrelated ADR by injection; the transit id stays the literal target (Codex
        # Step-4b, GHI #678). A real ADR sits on disk to prove it is NOT matched.
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            adr = root / "docs" / "design" / "adr" / "pre-release" / "ADR-DECOY"
            adr.mkdir(parents=True)
            (adr / "ADR-DECOY.md").write_text("# decoy\n\n## Allowed Paths\n\n- `x`\n", "utf-8")
            with patch.object(permitted_entry.console, "print") as pr:
                permitted_entry.permitted_entry_cmd(target="*", recon=True, project_root=root)
            printed = " ".join(str(c.args[0]) for c in pr.call_args_list if c.args)
            self.assertIn("permitted-entry:*", printed, "the transit id is the literal target")
            self.assertNotIn("ADR-DECOY", printed, "wildcard target does not select the decoy ADR")
            self.assertEqual(
                [e["id"] for e in _events(root, "airlock_in")],
                ["permitted-entry:*"],
                "the booked transit id is the literal target, never empty or misbound",
            )

    @covers("REQ-0.33.0-05-06")
    def test_ambiguous_target_prefix_synthesizes_rather_than_misbinding(self) -> None:
        # A vague/partial target must NOT silently bind to an arbitrary real artifact by
        # prefix-glob (the old matches[0] misbinding). Resolution is EXACT-id-only, so a
        # partial "ADR" synthesizes with the literal target as its footprint — never a
        # forged declaration of an unrelated ADR (Codex Step-4b, GHI #678).
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            adr = root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.0.1-real"
            adr.mkdir(parents=True)
            (adr / "ADR-0.0.1-real.md").write_text(
                "# real\n\n## Allowed Paths\n\n- `src/secret.py`\n", "utf-8"
            )
            with patch.object(permitted_entry.console, "print") as pr:
                permitted_entry.permitted_entry_cmd(target="ADR", recon=True, project_root=root)
            printed = " ".join(str(c.args[0]) for c in pr.call_args_list if c.args)
            self.assertIn("permitted-entry:ADR", printed, "id is the literal synthesized target")
            self.assertNotIn("src/secret.py", printed, "a partial target does not bind a real ADR")
            self.assertEqual(
                [e["id"] for e in _events(root, "airlock_in")],
                ["permitted-entry:ADR"],
                "the transit binds the literal target, never a misbound artifact",
            )

    @covers("REQ-0.33.0-05-06")
    def test_distinct_targets_keep_distinct_lossless_identity(self) -> None:
        # Target identity is LOSSLESS: a target that cannot be represented exactly (a
        # backtick/newline) is REJECTED, not lossy-rewritten — otherwise `src/a`b.py`
        # and `src/ab.py` would collapse to one id, destroying accountability (Codex
        # Step-4b, GHI #678).
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            with self.assertRaises(SystemExit):
                permitted_entry.permitted_entry_cmd(
                    target="src/a`b.py", recon=True, project_root=root
                )
            self.assertEqual(
                _events(root, "airlock_in"), [], "an unrepresentable target books no transit"
            )
        # Two DISTINCT representable targets keep DISTINCT declared bodies + ledger ids.
        ids = []
        for tgt in ("src/ab.py", "src/a-b.py"):
            with TemporaryDirectory() as tmp:
                root = _mk_root(tmp)
                permitted_entry.permitted_entry_cmd(target=tgt, recon=True, project_root=root)
                ids.append(_events(root, "airlock_in")[0]["id"])
        self.assertEqual(
            ids,
            ["permitted-entry:src/ab.py", "permitted-entry:src/a-b.py"],
            "distinct targets never collapse to one transit identity",
        )

    @covers("REQ-0.33.0-05-06")
    def test_synthetic_declare_cannot_be_markdown_injected(self) -> None:
        # Operator repair/target text is sanitized before it enters the synthetic DECLARE,
        # so newline+bullet or backtick injection cannot forge a declared footprint
        # (Codex Step-4b, GHI #678). Only the literal target is a declared body.
        from gzkit.governance.brief_path_validity import extract_allowed_paths  # noqa: PLC0415

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            declare_id, brief_path, tmp_root = permitted_entry._resolve_declare(
                "src/real.py", "rewrite\n- `injected.py`\n- `evil2.py`", root
            )
            try:
                self.assertEqual(
                    extract_allowed_paths(brief_path),
                    ["src/real.py"],
                    "the injected markdown bullets do not become declared bodies",
                )
            finally:
                if tmp_root is not None:
                    import shutil  # noqa: PLC0415

                    shutil.rmtree(tmp_root, ignore_errors=True)

    @covers("REQ-0.33.0-05-06")
    def test_gate_is_never_a_completion_attestation(self) -> None:
        # REQ-07 (STRUCTURAL-FENCE) reinforcement: the door books airlock encounter
        # events only — never a completion-attestation event (BI-3, sacred word reserved).
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            target = _mk_target(root)
            permitted_entry.permitted_entry_cmd(target=target, recon=True, project_root=root)
            self.assertEqual(
                _events(root, "obpi_completed"),
                [],
                "the acknowledge-and-decide gate is never recorded as a completion attestation",
            )


class TestCeilingCannotBeSmuggledViaCliFlags(SilencedConsoleTestCase):
    """REQ-0.33.0-05-03: no CLI-flag path lets a beyond-ceiling repair evade classification.

    The smuggling invariant is closed at the argparse layer (Codex Step-4b, GHI #678):
    every invocation yields either NO repair (reconnaissance) or exactly ONE classified
    repair — never a beyond-ceiling intent silently dropped before the ceiling gate.
    """

    @staticmethod
    def _parse(argv: list[str]) -> None:
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        _build_parser().parse_args(["permitted-entry", *argv])

    @covers("REQ-0.33.0-05-03")
    def test_recon_and_repair_together_rejected_at_parse(self) -> None:
        # --recon + --repair is mutually exclusive: a repair can't ride alongside recon.
        with self.assertRaises(SystemExit):
            self._parse(["--target", "README.md", "--recon", "--repair", "rewrite the schema"])

    @covers("REQ-0.33.0-05-03")
    def test_duplicate_repair_rejected_at_parse(self) -> None:
        # Repeated --repair must not collapse to the last value (which would drop an
        # earlier BEYOND intent past classification). Both duplicate shapes fail fast.
        beyond = "rewrite the deadlock"
        with self.assertRaises(SystemExit):
            self._parse(["--target", "README.md", "--repair", beyond, "--repair", ""])
        with self.assertRaises(SystemExit):
            self._parse(["--target", "README.md", "--repair", beyond, "--repair", "fix typo"])

    @covers("REQ-0.33.0-05-03")
    def test_single_repair_is_accepted(self) -> None:
        # The valid single-intent path parses cleanly (no false rejection).
        self._parse(["--target", "README.md", "--repair", "fix typo", "--dry-run"])
