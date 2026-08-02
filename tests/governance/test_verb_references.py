"""One `gz <verb>` extractor, shared by every governed verb-checker (GHI #748).

gzkit carried two extractors. `hooks/obpi.py` read fenced blocks, multi-word
chains, and a speculative-skip marker; `trust_audits/cli.py` read none of the
three and guarded the wider surface — the operator-doc corpus. Each gap had
already been reported separately (#745 fenced blocks, #588 multi-word, #748 the
marker), which is the signature of a capability implemented once and
reimplemented weakly elsewhere.

These tests pin the shared module's contract so the next gap is fixed once
rather than per copy.
"""

from __future__ import annotations

import unittest

from gzkit.verb_references import (
    DOC_BARE_SEGMENTS,
    DOC_SEGMENTS,
    SPECULATIVE_MARKER,
    VerbReference,
    extract_verb_references,
    verify_gz_chain,
)


def _chains(content: str, **kwargs) -> list[tuple[str, ...]]:
    return [ref.chain for ref in extract_verb_references(content, **kwargs)]


class MultiWordChainTests(unittest.TestCase):
    """A chain is the unit of resolution, not its first token.

    `.gzkit/rules/governance-core.md` § Operator-doc verb resolution binds it:
    "Multi-word subcommands count (`gz adr status`, `gz obpi complete`), not
    just top-level verbs." The weak extractor captured `group(1)` — one word —
    so `gz adr bogus` resolved as `adr` and passed (GHI #588).
    """

    def test_inline_code_yields_the_whole_chain(self) -> None:
        self.assertEqual(_chains("Run `gz adr status` to check."), [("adr", "status")])

    def test_three_level_chain_is_preserved(self) -> None:
        self.assertEqual(_chains("`gz obpi lock claim`"), [("obpi", "lock", "claim")])

    def test_uv_run_prefix_is_tolerated(self) -> None:
        self.assertEqual(_chains("`uv run gz obpi complete`"), [("obpi", "complete")])

    def test_prose_mention_is_not_a_reference(self) -> None:
        """Descriptive prose is not a prescriptive invocation — by design."""
        self.assertEqual(_chains("Agents transcribe gz commands into briefs."), [])


class FencedBlockTests(unittest.TestCase):
    """The runnable form operators copy is the form that must be checked.

    Before GHI #745 the fenced block — the only form a reader can paste — was
    the one form that escaped checking entirely.
    """

    def test_fenced_command_is_extracted(self) -> None:
        content = "```bash\nuv run gz adr status\n```"
        self.assertEqual(_chains(content), [("adr", "status")])

    def test_tilde_fences_count(self) -> None:
        content = "~~~\ngz state\n~~~"
        self.assertEqual(_chains(content), [("state",)])

    def test_transcript_prompt_prefix_is_tolerated(self) -> None:
        content = "```\n$ gz status\n```"
        self.assertEqual(_chains(content), [("status",)])

    def test_chained_invocation_inside_a_fence_is_seen(self) -> None:
        """`&& gz …` is a real prescribed invocation, not line noise.

        The weak extractor anchored at line start, so the second half of a
        compound command was invisible to it.
        """
        content = "```bash\ngz lint && gz test\n```"
        self.assertEqual(_chains(content), [("lint",), ("test",)])


class SpeculativeMarkerTests(unittest.TestCase):
    """The escape hatch `governance-core.md` promises must actually exist here.

    The rule's recovery instruction — "mark the reference as speculative so the
    check skips it" — was unfollowable on the operator-doc surface, because the
    marker was implemented only in the brief checker (GHI #432 built it; #748
    found the second call site never adopted it).
    """

    def test_marker_suppresses_the_following_inline_reference(self) -> None:
        content = f"{SPECULATIVE_MARKER}\nRun `gz storybook derive` (planned)."
        self.assertEqual(_chains(content), [])

    def test_marker_suppresses_an_entire_fenced_block(self) -> None:
        content = f"{SPECULATIVE_MARKER}\n```bash\ngz ruling record\ngz ruling list\n```"
        self.assertEqual(_chains(content), [])

    def test_marker_scope_ends_with_its_block(self) -> None:
        """Suppression is local — the next block is checked normally."""
        content = f"{SPECULATIVE_MARKER}\n```\ngz unbuilt verb\n```\n\n`gz state`"
        self.assertEqual(_chains(content), [("state",)])

    def test_marker_suppresses_a_whole_table(self) -> None:
        """Placement must stay OUTSIDE the table.

        An HTML comment written between two table rows splits the table in the
        rendered page — a silent regression no validator here catches. Block
        granularity is what lets the marker sit above the table instead.
        """
        content = (
            f"{SPECULATIVE_MARKER}\n"
            "| id | note |\n"
            "|----|------|\n"
            "| A | renamed to `gz unbuiltverb` |\n"
            "| B | second row |\n"
        )
        self.assertEqual(_chains(content), [])

    def test_marker_suppresses_a_whole_blockquote(self) -> None:
        content = f"{SPECULATIVE_MARKER}\n> rerun\n> `gz unbuiltverb derive` to refresh\n"
        self.assertEqual(_chains(content), [])

    def test_suppression_ends_when_the_run_ends(self) -> None:
        """A block marker is not a file-level off switch."""
        content = (
            f"{SPECULATIVE_MARKER}\n| A | `gz unbuiltverb` |\n| B | second row |\n\n`gz state`\n"
        )
        self.assertEqual(_chains(content), [("state",)])


class SegmentSelectionTests(unittest.TestCase):
    """Call sites differ in which prose contexts count as an invocation.

    Briefs quote commands in backticks. Feature files carry them in quoted step
    fixtures. Sharing one core does not mean pretending those are the same
    surface — the segments are a parameter, so neither call site inherits the
    other's false positives.
    """

    def test_quoted_invocations_are_ignored_by_default(self) -> None:
        self.assertEqual(_chains('Assert the output is "gz state ran"'), [])

    def test_doc_segments_read_quoted_invocations(self) -> None:
        refs = _chains('Run "gz adr status" first.', segments=DOC_SEGMENTS)
        self.assertIn(("adr", "status"), refs)

    def test_step_fixtures_carry_a_bare_chain(self) -> None:
        """The real shape in `features/**`: the verb is outside the quotes.

        `When I run the gz command "justify GHI-232"` — no `gz` inside the
        quotes. A recognizer requiring a literal `gz` there matches nothing and
        drops every `.feature` file from the audit while still reporting green.
        """
        refs = _chains(
            'When I run the gz command "issue file --title T"',
            bare_segments=DOC_BARE_SEGMENTS,
        )
        self.assertEqual(refs, [("issue", "file")])

    def test_bare_chain_stops_at_the_first_argument(self) -> None:
        refs = _chains(
            "the gz command \"justify --draft 'pre-decision text' --save\"",
            bare_segments=DOC_BARE_SEGMENTS,
        )
        self.assertEqual(refs, [("justify",)])


class CorpusFalsePositiveTests(unittest.TestCase):
    """Shapes the real corpus contains that are NOT prescribed invocations.

    Each was a live false hit on the first run of the converged extractor over
    gzkit's own docs. A verb-checker that cries wolf on ordinary prose gets
    marker-suppressed everywhere until it checks nothing.
    """

    def test_english_prose_inside_a_fenced_transcript_is_not_an_invocation(self) -> None:
        """`docs/user/manpages/handoff-authorize.md:80` — captured stderr.

        Fenced blocks hold output as often as commands. "no file mutation / gz
        ceremony / migration" is English; only a line that OPENS with the
        invocation is a command line.
        """
        content = "```\nWHY: ... no file mutation / gz ceremony / migration until ruled.\n```"
        self.assertEqual(_chains(content), [])

    def test_a_command_line_still_yields_every_invocation_on_it(self) -> None:
        """The anchor selects the line; it does not stop at the first command."""
        self.assertEqual(_chains("```\ngz lint && gz test\n```"), [("lint",), ("test",)])

    def test_a_version_template_in_backticks_is_not_a_verb(self) -> None:
        """`docs/user/runbook.md:306` — a rendered output template, not a command.

        "Filed from <slug> running gz vX.Y.Z" reads as a verb `v` when the whole
        backtick span is scanned. Operator docs get the anchored recognizer;
        briefs keep the unanchored one, which they need to catch a command
        embedded mid-span.
        """
        line = "The wrapper stamps `Filed from <consumer-repo-slug> running gz vX.Y.Z`"
        self.assertEqual(_chains(line, segments=DOC_SEGMENTS), [])
        self.assertEqual(_chains("`then run gz obpi complete`"), [("obpi", "complete")])

    def test_a_version_string_mid_quote_is_not_a_verb(self) -> None:
        """`features/issue_file.feature:15` — "…running gz v" is a version prefix.

        Six hits for a verb `v` came from scanning inside quotes that do not
        open with the command.
        """
        refs = _chains('the output contains "Filed from acme/widget running gz v"')
        self.assertEqual(refs, [])


class LineAttributionTests(unittest.TestCase):
    """A finding the operator cannot locate is a finding they cannot fix."""

    def test_lineno_is_one_indexed_and_accurate(self) -> None:
        content = "intro\n\n`gz state`\n"
        self.assertEqual(
            extract_verb_references(content), [VerbReference(chain=("state",), lineno=3)]
        )


class ChainResolutionTests(unittest.TestCase):
    """Resolution walks the real parser tree — the shared resolver's whole point."""

    def test_registered_multi_word_chain_resolves(self) -> None:
        ok, _ = verify_gz_chain(["adr", "status"])
        self.assertTrue(ok)

    def test_unregistered_subcommand_fails_closed(self) -> None:
        ok, reason = verify_gz_chain(["adr", "definitely-not-a-verb"])
        self.assertFalse(ok)
        self.assertIn("definitely-not-a-verb", reason)

    def test_positional_arguments_after_a_leaf_resolve(self) -> None:
        """`gz obpi status OBPI-1.2.3-04` — the id is an argument, not a verb."""
        ok, _ = verify_gz_chain(["obpi", "status", "obpi-1"])
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
