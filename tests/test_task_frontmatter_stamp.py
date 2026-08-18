"""Producer-stamp the brief `tasks:` frontmatter channel (GHI #752).

GHI #731 fixed Signature (c)'s key mismatch and repaired the commit-trailer
channel at its producer. It left the other half declared but unfixed: two of the
four discovery channels named by `.gzkit/rules/task-discovery.md` produce ZERO
keys repo-wide, so only `ledger` x `commit_trailer` can ever pair and the gate
compares 7 of 534 OBPIs.

The two dead channels are not symmetric. `@advances` marks the function an author
judges materially advances a TASK — no runtime knows which function that is, which
is why it is demoted to advisory rather than rescued. `tasks:` is different:
`task_start_cmd` already resolves `(task_id, obpi_id, adr_id)`, so it holds the
OBPI id at the exact moment the TASK is minted. The declaration is producer-known,
and asking an author to restate it is the same dead convention the trailer channel
already proved decays (~15% adherence, GHI #731).

Independence is the point, not merely population. Since `4b9db759` the trailer
channel is stamped FROM the ledger's active TASK set, so `ledger` x
`commit_trailer` are partly the same source and their agreement is partly
tautological. A brief-authored `tasks:` channel restores a genuinely independent
witness — which is why the remedy is to populate this channel rather than to
narrow the envelope's declaration to the two that already pair.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from gzkit.commands.closeout_form import _append_frontmatter_list_value
from gzkit.commands.task import (
    _find_brief_path,
    _stamp_brief_task_declaration,
    task_start_cmd,
)
from gzkit.commands.validate_task_envelope import _frontmatter_channel_map
from tests.commands.common import CliRunner, _quick_init

_OBPI_ID = "OBPI-0.0.64-02-advances-decorator-and-discovery-convention"


def _brief(root: Path, obpi_id: str = _OBPI_ID, *, tasks_line: str = "") -> Path:
    """Write a brief where the envelope reader actually looks for one."""
    briefs = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.64" / "obpis"
    briefs.mkdir(parents=True, exist_ok=True)
    path = briefs / f"{obpi_id}.md"
    path.write_text(
        f"---\nid: {obpi_id}\nparent: ADR-0.0.64\nstatus: Active\n{tasks_line}---\n\n# Brief\n",
        encoding="utf-8",
    )
    return path


def _parsed_tasks(content: str) -> object:
    """Return the `tasks:` value as the envelope reader would parse it."""
    end = content.find("\n---\n", 4)
    return (yaml.safe_load(content[4:end]) or {}).get("tasks")


class TestFrontmatterListAppend(unittest.TestCase):
    """The helper accumulates a list; it never replaces one."""

    def test_creates_the_key_when_absent(self) -> None:
        """A brief with no `tasks:` gains one carrying the declaration."""
        out = _append_frontmatter_list_value("---\nid: X\n---\n\nbody\n", "tasks", "TASK-A")

        self.assertEqual(_parsed_tasks(out), ["TASK-A"])

    def test_accumulates_rather_than_replacing(self) -> None:
        """A second TASK joins the first.

        An OBPI mints one TASK per REQ, so a replacing writer would leave the
        channel declaring only the most recent — under-declaration, which is the
        exact drift Signature (c) exists to catch.
        """
        out = _append_frontmatter_list_value("---\nid: X\n---\n", "tasks", "TASK-A")
        out = _append_frontmatter_list_value(out, "tasks", "TASK-B")

        self.assertEqual(_parsed_tasks(out), ["TASK-A", "TASK-B"])

    def test_is_idempotent(self) -> None:
        """Re-stamping the same TASK does not duplicate it.

        `gz task start` accepts a blocked -> in_progress resume, so the same
        declaration legitimately arrives twice.
        """
        out = _append_frontmatter_list_value("---\nid: X\n---\n", "tasks", "TASK-A")
        out = _append_frontmatter_list_value(out, "tasks", "TASK-A")

        self.assertEqual(_parsed_tasks(out), ["TASK-A"])

    def test_joins_an_existing_block_at_its_own_indentation(self) -> None:
        """An appended item matches the indentation of the block it joins.

        A YAML block sequence must agree on depth, so emitting a fixed two-space
        item into a column-zero block both reformats every sibling line and risks
        a brief that no longer parses. Column-zero is the shape OBPI briefs are
        authored in -- `allowlist:` on the live briefs sits flush (GHI #825).
        """
        content = "---\nid: X\nallowlist:\n- src/a.py\n- src/b.py\nstatus: Active\n---\n\nbody\n"
        out = _append_frontmatter_list_value(content, "allowlist", "src/c.py")

        end = out.find("\n---\n", 4)
        fm = yaml.safe_load(out[4:end])
        self.assertEqual(fm["allowlist"], ["src/a.py", "src/b.py", "src/c.py"])
        self.assertIn("\n- src/c.py", out)
        self.assertNotIn("\n  - src/c.py", out)
        # The siblings are untouched, so the diff is one line rather than three.
        self.assertIn("\n- src/a.py\n- src/b.py\n", out)

    def test_preserves_sibling_frontmatter_keys(self) -> None:
        """Stamping one key must not disturb the rest of the brief's envelope."""
        out = _append_frontmatter_list_value(
            "---\nid: X\nparent: ADR-0.0.64\nstatus: Active\n---\n", "tasks", "TASK-A"
        )
        end = out.find("\n---\n", 4)
        fm = yaml.safe_load(out[4:end])

        self.assertEqual((fm["id"], fm["parent"], fm["status"]), ("X", "ADR-0.0.64", "Active"))


class TestBriefTaskDeclarationStamp(unittest.TestCase):
    """The producer writes what the envelope reader consumes."""

    def test_stamped_declaration_populates_the_frontmatter_channel(self) -> None:
        """The channel `_frontmatter_channel_map` reads is non-empty after a stamp.

        This is the REQ, asserted against the CONSUMER rather than the file: the
        defect in #752 is not "briefs lack a field", it is "the frontmatter
        discovery channel yields zero keys repo-wide". A test asserting only that
        the file gained a line would pass while the channel stayed dead.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _brief(root)

            _stamp_brief_task_declaration(root, _OBPI_ID, "TASK-0.0.64-02-01-01")

            self.assertEqual(
                _frontmatter_channel_map(_collect(root)),
                {_OBPI_ID: {"TASK-0.0.64-02-01-01"}},
            )

    def test_missing_brief_is_a_silent_no_op(self) -> None:
        """A TASK whose brief cannot be found must never break `gz task start`.

        Negative control: attribution is a governance nicety, minting the TASK is
        the operator's actual work. A raising producer would make an unfindable
        brief block the pipeline.
        """
        with TemporaryDirectory() as tmp:
            self.assertIsNone(
                _stamp_brief_task_declaration(Path(tmp), _OBPI_ID, "TASK-0.0.64-02-01-01")
            )

    def test_repeated_starts_declare_each_distinct_task_once(self) -> None:
        """Two REQs under one OBPI both surface; a resumed start does not duplicate."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _brief(root)

            _stamp_brief_task_declaration(root, _OBPI_ID, "TASK-0.0.64-02-01-01")
            _stamp_brief_task_declaration(root, _OBPI_ID, "TASK-0.0.64-02-02-01")
            _stamp_brief_task_declaration(root, _OBPI_ID, "TASK-0.0.64-02-01-01")

            self.assertEqual(
                _frontmatter_channel_map(_collect(root))[_OBPI_ID],
                {"TASK-0.0.64-02-01-01", "TASK-0.0.64-02-02-01"},
            )


class TestTaskStartDeclaresIntoTheBrief(unittest.TestCase):
    """The wiring, exercised rather than inspected."""

    def test_starting_a_task_declares_it_in_the_brief(self) -> None:
        """`gz task start` populates the frontmatter channel end to end.

        The helper being correct is not the REQ — the REQ is that the channel is
        producer-fed. Asserting the call site by reading its source would pass on
        a call that was present and broken, which `.gzkit/rules/tests.md` § 6f
        forbids: if the behavior changed but the text did not, the test must
        still fail. So drive the real command and read the real channel.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            root = Path.cwd()
            _quick_init()
            _brief(root)

            task_start_cmd("TASK-0.0.64-02-01-01")

            self.assertIn(
                "TASK-0.0.64-02-01-01",
                _frontmatter_channel_map(_collect(root)).get(_OBPI_ID, set()),
            )


def _collect(root: Path) -> dict[str, dict[str, object]]:
    from gzkit.commands.validate_task_envelope import _collect_obpi_brief_frontmatter

    return _collect_obpi_brief_frontmatter(root)


if __name__ == "__main__":
    unittest.main()


class TestBriefResolutionIsAnchored(unittest.TestCase):
    """`_find_brief_path` resolves a governance id against canon, not the tree (GHI #824).

    The stamp's own contract makes this failure mode invisible at the call site:
    `_stamp_brief_task_declaration` is best-effort, so writing to the WRONG file is
    indistinguishable from success. The REQ is therefore about WHICH file the
    resolver returns, not about whether a write happened.

    Measured on this repo at filing time: 164 of 542 short OBPI ids resolved to a
    file outside `docs/design/adr/` — one `.claude/plans/OBPI-<id>-<slug>.md` per
    OBPI that ever passed the plan-audit gate, and `.claude/` sorts before `docs/`.
    """

    def test_a_plan_file_never_shadows_the_brief(self) -> None:
        """The observed cause: an `OBPI-*.md` outside the ADR tree sorting first.

        `.claude/plans/` is the canonical plan-file home and `gz obpi pipeline`
        names its files `OBPI-<id>-<slug>.md` itself, so this collision is
        structural rather than incidental.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = _brief(root)
            plan = root / ".claude" / "plans" / f"{_OBPI_ID}.md"
            plan.parent.mkdir(parents=True, exist_ok=True)
            plan.write_text("# Plan\n", encoding="utf-8")

            self.assertEqual(_find_brief_path(root, _OBPI_ID), brief)

            _stamp_brief_task_declaration(root, _OBPI_ID, "TASK-0.0.64-02-01-01")

            # The consumer-level assertion: the governance channel is fed and the
            # plan file is left exactly as authored, with no frontmatter grafted on.
            self.assertEqual(
                _frontmatter_channel_map(_collect(root)),
                {_OBPI_ID: {"TASK-0.0.64-02-01-01"}},
            )
            self.assertEqual(plan.read_text(encoding="utf-8"), "# Plan\n")

    def test_an_id_mentioned_inside_another_briefs_slug_is_not_a_match(self) -> None:
        """Latent cause: `needle in candidate.name` is a substring test, not an id test.

        A slug that references another OBPI's id (`migrate-0.1.0-01-artifacts`) is
        ordinary kebab-case authoring. Anchoring the match to the stem's own id
        segment is what makes a mention stop reading as an identity.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            obpis = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.1" / "obpis"
            obpis.mkdir(parents=True, exist_ok=True)
            # Sorts BEFORE the real brief, and its slug contains the needle.
            decoy = obpis / "OBPI-0.0.1-01-migrate-0.1.0-01-artifacts.md"
            decoy.write_text("---\nid: OBPI-0.0.1-01\n---\n", encoding="utf-8")
            real = _brief(root, "OBPI-0.1.0-01-real-target")

            self.assertEqual(_find_brief_path(root, "OBPI-0.1.0-01"), real)

    def test_two_real_briefs_sharing_a_short_id_stay_ambiguous(self) -> None:
        """Ambiguity resolves to None, never to whichever name sorts first.

        Same stance `_canonical_obpi_id` already takes one function up — *"Two REAL
        briefs stay ambiguous — guessing would write a confidently wrong obpi_id."*
        A silent lexical tiebreak is the identical failure wearing a different hat.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _brief(root, "OBPI-0.1.0-01-alpha-slug")
            _brief(root, "OBPI-0.1.0-01-beta-slug")

            self.assertIsNone(_find_brief_path(root, "OBPI-0.1.0-01"))

    def test_an_exact_full_slug_id_still_resolves(self) -> None:
        """Regression guard for `_canonical_obpi_id`'s on-disk existence probe.

        That caller passes full artifact-graph keys and reads only `is not None`,
        so an over-tight matcher would silently re-break GHI #653's disambiguation
        rather than fail loudly here.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = _brief(root)

            self.assertEqual(_find_brief_path(root, _OBPI_ID), brief)
