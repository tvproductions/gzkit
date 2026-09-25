"""Retention map and validation tests (ADR-0.35.0 Decision 10, OBPI-0.35.0-14).

Tests the block splitter, removed-block delta, sentence splitter, RetentionMap models,
total validator, and sidecar path helper.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.content.retention import (
    Condition,
    NonBinding,
    RemovedBlock,
    RetentionMap,
    RetentionViolation,
    removed_blocks,
    retention_path,
    split_blocks,
    split_sentences,
    validate_retention,
)
from gzkit.traceability import covers


class TestRemovedBlocksCandidateNormalization(unittest.TestCase):
    """Defect 2 (Requirement 2): the candidate is normalized the same way prior blocks are."""

    def test_crlf_and_trailing_whitespace_only_difference_yields_no_removed_blocks(
        self,
    ) -> None:
        """A candidate identical to prior except CRLF endings/trailing spaces removes nothing."""
        prior = "## Heading\n\nSome paragraph text.\n\n- Item one\n- Item two"
        candidate = (
            "## Heading   \r\n\r\nSome paragraph text.   \r\n\r\n- Item one\r\n- Item two   "
        )

        self.assertEqual(removed_blocks(prior, candidate), [])


class TestRetentionPathHelper(unittest.TestCase):
    """Test the retention_path sidecar path helper."""

    def test_retention_path_layout(self) -> None:
        """Return path: .gzkit/renditions/<surface>/<consumer>.retention.json"""
        root = Path("/repo")
        expected = root / ".gzkit" / "renditions" / "AGENTS.md" / "root.retention.json"
        self.assertEqual(retention_path(root, "AGENTS.md", "root"), expected)


class TestRetentionMapModelsImmutability(unittest.TestCase):
    """Test that RetentionMap and related models are frozen and forbid extra fields."""

    def test_retention_map_frozen(self) -> None:
        """RetentionMap is frozen and cannot be mutated after construction."""
        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="ReviewerAgent",
            mapped_by="AuthorAgent",
            blocks=[],
        )
        with self.assertRaises(ValidationError):
            map_obj.surface = "OTHER.md"  # type: ignore

    def test_retention_map_forbids_extra_fields(self) -> None:
        """RetentionMap forbids extra fields not in the schema."""
        with self.assertRaises(ValidationError):
            RetentionMap(
                surface="AGENTS.md",
                consumer="root",
                extracted_by="ReviewerAgent",
                mapped_by="AuthorAgent",
                blocks=[],
                extra_field="should_fail",
            )

    def test_condition_frozen(self) -> None:
        """Condition is frozen and cannot be mutated after construction."""
        cond = Condition(id="C1", quote="some text", disposition="kept", span="some text")
        with self.assertRaises(ValidationError):
            cond.id = "C2"  # type: ignore

    def test_non_binding_frozen(self) -> None:
        """NonBinding is frozen and cannot be mutated after construction."""
        nb = NonBinding(quote="some text", reason="not binding")
        with self.assertRaises(ValidationError):
            nb.reason = "other reason"  # type: ignore


class TestConditionIdConstraint(unittest.TestCase):
    """Brief Requirement 6: condition ids are short, human-typable tokens.

    An unconstrained ``id`` lets a DROPPED condition with id "" be "attested"
    by ANY text -- ``_id_in_attestation("", text)`` matches everywhere, so the
    empty id silently bypasses the DROPPED-id-must-be-attested check. The
    pattern constraint makes that id unconstructable.
    """

    @covers("REQ-0.35.0-14-02")
    def test_empty_id_raises_validation_error(self) -> None:
        """An empty id is not a human-typable token and must fail construction."""
        with self.assertRaises(ValidationError):
            Condition(id="", quote="some text", disposition="dropped", reason="why")

    def test_id_with_space_raises_validation_error(self) -> None:
        """A space is not part of a short, human-typable token."""
        with self.assertRaises(ValidationError):
            Condition(id="C 1", quote="some text", disposition="dropped", reason="why")

    def test_ordinary_id_still_constructs(self) -> None:
        """A normal id like 'C1' is unaffected by the constraint."""
        cond = Condition(id="C1", quote="some text", disposition="dropped", reason="why")
        self.assertEqual(cond.id, "C1")


class TestValidateRetentionAllViolations(unittest.TestCase):
    """REQ-0.35.0-14-02: validator returns ALL violations, never the first only."""

    @covers("REQ-0.35.0-14-02")
    def test_validator_returns_all_violations(self) -> None:
        """When multiple violations exist, validate_retention returns every one."""
        # Setup: a removed block with multiple violations
        removed = ["## First Block\n\nText about feature X."]
        candidate = "## Other Block\n\nSomething else."

        # Map with multiple violations:
        # 1. Condition C1: KEPT span "other stuff" is not in the candidate
        # 2. Condition C2: DROPPED condition with empty reason
        # 3. Condition C3: quote is not in the removed block
        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="feature X",
                            disposition="kept",
                            span="other stuff",  # Not in candidate - VIOLATION
                        ),
                        Condition(
                            id="C2",
                            quote="Text about",
                            disposition="dropped",
                            reason="",  # Empty reason - VIOLATION
                        ),
                        Condition(
                            id="C3",
                            quote="nonexistent text not in block",
                            disposition="kept",
                            span="something",  # Not in removed block - VIOLATION
                        ),
                    ],
                )
            ],
        )
        attestation = "approved drop C2"

        violations = validate_retention(removed, candidate, map_obj, attestation)

        # Should have at least 3 violations
        self.assertGreaterEqual(len(violations), 3)
        # Verify each violation is a RetentionViolation with kind and message
        for v in violations:
            self.assertIsInstance(v, RetentionViolation)
            self.assertTrue(v.kind)
            self.assertTrue(v.message)

    @covers("REQ-0.35.0-14-02")
    def test_validator_detects_missing_block_mapping(self) -> None:
        """Validator detects a removed block with no map entry."""
        removed = ["## Missing Block\n\nNo mapping for this."]
        candidate = "## Other content"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[],  # No blocks in map
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        missing = [
            v for v in violations if "missing" in v.kind.lower() or "mapped" in v.kind.lower()
        ]
        self.assertTrue(missing, "Should have a 'missing' or 'unmapped' violation")

    @covers("REQ-0.35.0-14-02")
    def test_validator_detects_condition_quote_not_in_removed_block(self) -> None:
        """Validator detects when a condition quote is not a substring of its removed block."""
        removed = ["## Block\n\nText here."]
        candidate = "## Block\n\nText here."

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="this quote is not in the removed block",
                            disposition="kept",
                            span="Text here",
                        )
                    ],
                )
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        quote_violations = [
            v for v in violations if "quote" in v.kind.lower() or "substring" in v.message.lower()
        ]
        self.assertTrue(quote_violations, "Should detect quote not in removed block")

    @covers("REQ-0.35.0-14-02")
    def test_validator_detects_kept_span_not_in_candidate(self) -> None:
        """Validator detects when a KEPT span is not a substring of the candidate."""
        removed = ["## Block\n\nOriginal text."]
        candidate = "## Block\n\nNew text."

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Original text",
                            disposition="kept",
                            span="Original text",  # Not in candidate
                        )
                    ],
                )
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        span_violations = [
            v for v in violations if "span" in v.kind.lower() or "span" in v.message.lower()
        ]
        self.assertTrue(span_violations, "Should detect span not in candidate")

    @covers("REQ-0.35.0-14-02")
    def test_validator_detects_dropped_condition_with_empty_reason(self) -> None:
        """Validator detects when a DROPPED condition has an empty reason."""
        removed = ["## Block\n\nSome text."]
        candidate = "## Block\n\nOther text."

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Some text",
                            disposition="dropped",
                            reason="",  # Empty reason
                        )
                    ],
                )
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        reason_violations = [
            v for v in violations if "reason" in v.kind.lower() or "reason" in v.message.lower()
        ]
        self.assertTrue(reason_violations, "Should detect empty reason on dropped condition")

    @covers("REQ-0.35.0-14-02")
    def test_validator_valid_map_has_no_violations(self) -> None:
        """When a retention map is valid, validate_retention returns no violations.

        Meaningful-character coverage requires every non-whitespace,
        non-markup character to be marked, including the heading label
        "Block" and the trailing period — an overlap-only quote for the
        paragraph sentence would leave both unmarked, so a second condition
        names them (Change Log 2026-09-24, meaningful-character coverage).
        """
        removed = ["## Block\n\nSome text to keep."]
        candidate = "## Block\n\nSome text to keep.\n\nNew paragraph."

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Block",
                            disposition="kept",
                            span="Block",
                        ),
                        Condition(
                            id="C2",
                            quote="Some text to keep.",
                            disposition="kept",
                            span="Some text to keep.",
                        ),
                    ],
                )
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        self.assertEqual(len(violations), 0, f"Should have no violations, got: {violations}")


class TestValidateRetentionIndependenceCheck(unittest.TestCase):
    """REQ-0.35.0-14-03: validator checks extracted_by and mapped_by independence."""

    @covers("REQ-0.35.0-14-03")
    def test_validator_rejects_empty_extracted_by(self) -> None:
        """Validator detects when extracted_by is empty."""
        removed = []
        candidate = ""

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="",  # Empty
            mapped_by="Author",
            blocks=[],
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        empty_violations = [
            v for v in violations if "empty" in v.kind.lower() or "empty" in v.message.lower()
        ]
        self.assertTrue(empty_violations, "Should detect empty extracted_by")

    @covers("REQ-0.35.0-14-03")
    def test_validator_rejects_empty_mapped_by(self) -> None:
        """Validator detects when mapped_by is empty."""
        removed = []
        candidate = ""

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="",  # Empty
            blocks=[],
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        empty_violations = [
            v for v in violations if "empty" in v.kind.lower() or "empty" in v.message.lower()
        ]
        self.assertTrue(empty_violations, "Should detect empty mapped_by")

    @covers("REQ-0.35.0-14-03")
    def test_validator_rejects_identical_extracted_and_mapped(self) -> None:
        """Validator detects identical extracted_by and mapped_by."""
        removed = []
        candidate = ""

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="  SameAgent  ",  # After case-fold/trim same as mapped_by
            mapped_by="sameagent",
            blocks=[],
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        independence_violations = [
            v
            for v in violations
            if "independent" in v.kind.lower()
            or "independent" in v.message.lower()
            or "different" in v.message.lower()
        ]
        self.assertTrue(independence_violations, "Should detect identical ids")


class TestValidateRetentionAttestationCheck(unittest.TestCase):
    """REQ-0.35.0-14-04: validator checks dropped condition ids are in attestation text."""

    @covers("REQ-0.35.0-14-02")
    def test_validator_detects_dropped_condition_id_missing_from_attestation(self) -> None:
        """Validator detects when a DROPPED condition's id is not in attestation text."""
        removed = ["## Block\n\nSome text."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Some text",
                            disposition="dropped",
                            reason="Not needed anymore",
                        )
                    ],
                )
            ],
        )
        attestation = "approved some changes"  # Does not mention C1

        violations = validate_retention(removed, candidate, map_obj, attestation)
        attestation_violations = [
            v for v in violations if "attestation" in v.kind.lower() or "id" in v.message.lower()
        ]
        self.assertTrue(
            attestation_violations, "Should detect dropped condition id not in attestation"
        )

    @covers("REQ-0.35.0-14-02")
    def test_validator_accepts_dropped_condition_id_in_attestation(self) -> None:
        """Validator accepts when a DROPPED condition's id appears in attestation text."""
        removed = ["## Block\n\nSome text."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Some text",
                            disposition="dropped",
                            reason="Not needed anymore",
                        )
                    ],
                )
            ],
        )
        attestation = "approved drop C1"  # Contains C1

        violations = validate_retention(removed, candidate, map_obj, attestation)
        # May have other violations, but not about C1 missing from attestation
        attestation_violations = [
            v for v in violations if "C1" in v.message and "attestation" in v.kind.lower()
        ]
        self.assertFalse(attestation_violations, "Should not detect C1 in attestation")


class TestValidateRetentionEmptyQuoteBypass(unittest.TestCase):
    """Defect 1: an empty/whitespace-only quote or span must not satisfy validation.

    ``"" in s`` is always True, so an empty condition/non_binding quote or KEPT
    span silently covers every sentence and passes the substring checks. Each
    of these must itself be a violation and must never count toward coverage.
    """

    @covers("REQ-0.35.0-14-02")
    def test_empty_condition_quote_is_itself_a_violation(self) -> None:
        """A whitespace-only condition quote is flagged, not silently accepted."""
        removed = ["## Block\n\nFirst sentence. Second sentence."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="   ",
                            disposition="dropped",
                            reason="testing empty quote",
                        )
                    ],
                )
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "approved drop C1")
        empty_quote_violations = [v for v in violations if v.kind == "empty-quote"]
        self.assertTrue(
            empty_quote_violations, "An empty/whitespace-only condition quote must be a violation"
        )

    @covers("REQ-0.35.0-14-02")
    def test_empty_kept_span_is_itself_a_violation(self) -> None:
        """A whitespace-only KEPT span is flagged, not silently accepted."""
        removed = ["## Block\n\nSome sentence text."]
        candidate = "## Block\n\nSome sentence text."

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Some sentence text",
                            disposition="kept",
                            span="   ",
                        )
                    ],
                )
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        empty_span_violations = [v for v in violations if v.kind == "empty-span"]
        self.assertTrue(
            empty_span_violations, "An empty/whitespace-only KEPT span must be a violation"
        )

    @covers("REQ-0.35.0-14-02")
    def test_empty_non_binding_quote_is_itself_a_violation(self) -> None:
        """A whitespace-only non_binding quote is flagged, not silently accepted."""
        removed = ["## Block\n\nSome sentence text."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[],
                    non_binding=[NonBinding(quote="  ", reason="testing empty quote")],
                )
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        empty_quote_violations = [v for v in violations if v.kind == "empty-quote"]
        self.assertTrue(
            empty_quote_violations,
            "An empty/whitespace-only non_binding quote must be a violation",
        )

    @covers("REQ-0.35.0-14-02")
    def test_empty_quote_never_counts_toward_sentence_coverage(self) -> None:
        """An empty condition quote must not silently cover every sentence via `"" in s`."""
        removed = ["## Block\n\nAn entirely uncovered sentence here."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="",
                            disposition="dropped",
                            reason="empty quote should not cover anything",
                        )
                    ],
                )
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "approved drop C1")
        uncovered = [v for v in violations if v.kind == "uncovered-sentence"]
        self.assertTrue(
            uncovered,
            "An empty condition quote must not count as covering the block's sentence",
        )


class TestValidateRetentionDropIdTokenBoundary(unittest.TestCase):
    """Defect 3: attestation id matching must not find 'C1' inside 'C10'."""

    def _map_with_dropped_c1(self) -> RetentionMap:
        removed_block = "## Block\n\nSome text."
        return RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed_block,
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Some text",
                            disposition="dropped",
                            reason="dropped for testing",
                        )
                    ],
                )
            ],
        )

    @covers("REQ-0.35.0-14-02")
    def test_c1_substring_of_c10_in_attestation_is_not_a_match(self) -> None:
        """A drop C1 with attestation naming only C10 is still a violation."""
        removed = ["## Block\n\nSome text."]
        candidate = "## Other"
        map_obj = self._map_with_dropped_c1()

        violations = validate_retention(removed, candidate, map_obj, "approve C10")
        attestation_violations = [v for v in violations if v.kind == "dropped-id-not-attested"]
        self.assertTrue(
            attestation_violations,
            "C1 must not be considered attested merely because C10 appears in the text",
        )

    @covers("REQ-0.35.0-14-02")
    def test_c1_at_a_token_boundary_in_attestation_is_a_match(self) -> None:
        """A drop C1 with attestation naming C1 at a token boundary passes."""
        removed = ["## Block\n\nSome text."]
        candidate = "## Other"
        map_obj = self._map_with_dropped_c1()

        violations = validate_retention(removed, candidate, map_obj, "approve C1.")
        attestation_violations = [v for v in violations if v.kind == "dropped-id-not-attested"]
        self.assertFalse(
            attestation_violations, "C1 at a token boundary must be recognized as attested"
        )


class TestValidateRetentionDuplicateConditionIds(unittest.TestCase):
    """Defect 5 (Requirement 6): condition ids must be unique within the whole map."""

    @covers("REQ-0.35.0-14-02")
    def test_duplicate_condition_id_across_blocks_is_a_violation_not_a_crash(self) -> None:
        """A duplicate id across two different blocks is flagged, never raises."""
        removed = ["## Block A\n\nText A.", "## Block B\n\nText B."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Text A",
                            disposition="dropped",
                            reason="dropped A",
                        )
                    ],
                ),
                RemovedBlock(
                    removed=removed[1],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Text B",
                            disposition="dropped",
                            reason="dropped B",
                        )
                    ],
                ),
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "approve C1")
        duplicate_violations = [v for v in violations if v.kind == "duplicate-condition-id"]
        self.assertTrue(
            duplicate_violations, "A condition id repeated in the map must be a violation"
        )

    @covers("REQ-0.35.0-14-02")
    def test_unique_condition_ids_across_blocks_do_not_trigger_duplicate_violation(
        self,
    ) -> None:
        """Distinct ids across blocks never trigger a duplicate-condition-id violation."""
        removed = ["## Block A\n\nText A.", "## Block B\n\nText B."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Text A",
                            disposition="dropped",
                            reason="dropped A",
                        )
                    ],
                ),
                RemovedBlock(
                    removed=removed[1],
                    conditions=[
                        Condition(
                            id="C2",
                            quote="Text B",
                            disposition="dropped",
                            reason="dropped B",
                        )
                    ],
                ),
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "approve C1 and C2")
        duplicate_violations = [v for v in violations if v.kind == "duplicate-condition-id"]
        self.assertFalse(
            duplicate_violations, "Distinct condition ids must never trigger this violation"
        )


class TestValidateRetentionMapLevelViolationPrefix(unittest.TestCase):
    """A violation that belongs to no single block says so: message starts 'map-level:'.

    ``duplicate-condition-id``, ``empty-extracted-by``, ``empty-mapped-by`` and
    ``non-independent-mapping`` are properties of the WHOLE map, never of one
    removed block; without a marker, their message reads like a per-block
    finding and a refusal naming several violations does not say which ones
    are map-wide.
    """

    _MAP_LEVEL_KINDS = frozenset(
        {
            "empty-extracted-by",
            "empty-mapped-by",
            "non-independent-mapping",
            "duplicate-condition-id",
        }
    )

    def test_all_four_map_level_kinds_are_prefixed(self) -> None:
        """A map triggering all four map-level kinds prefixes every one of them."""
        removed = ["## Block A\n\nText A."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="",  # empty-extracted-by
            mapped_by="",  # empty-mapped-by
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(id="C1", quote="Text A", disposition="dropped", reason="dup 1"),
                        Condition(id="C1", quote="Text A", disposition="dropped", reason="dup 2"),
                    ],
                ),
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "approve C1")
        seen_kinds = {v.kind for v in violations if v.kind in self._MAP_LEVEL_KINDS}
        self.assertEqual(
            seen_kinds,
            self._MAP_LEVEL_KINDS - {"non-independent-mapping"},
            "expected empty-extracted-by, empty-mapped-by and duplicate-condition-id",
        )
        for violation in violations:
            if violation.kind in self._MAP_LEVEL_KINDS:
                self.assertTrue(
                    violation.message.startswith("map-level:"),
                    f"{violation.kind} message must start with 'map-level:': {violation.message!r}",
                )

    def test_non_independent_mapping_is_prefixed(self) -> None:
        """extracted_by == mapped_by (non-independent) is also map-level."""
        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Same Agent",
            mapped_by="same agent",  # identical after case-fold + trim
            blocks=[],
        )

        violations = validate_retention([], "", map_obj, "")
        non_independent = [v for v in violations if v.kind == "non-independent-mapping"]
        self.assertTrue(non_independent, "expected a non-independent-mapping violation")
        self.assertTrue(non_independent[0].message.startswith("map-level:"))


class TestSplitBlocksBoundaries(unittest.TestCase):
    """Defect 4 (Requirement 2): heading / paragraph / list item / table row / fence boundaries."""

    def test_full_document_splits_into_exact_expected_blocks(self) -> None:
        """One document exercising every block boundary rule, asserted exactly."""
        document = (
            "# Heading One\n"
            "\n"
            "A plain paragraph of text.\n"
            "\n"
            "**Bold-led** paragraph is not a list item.\n"
            "\n"
            "- Bullet one\n"
            "- Bullet two\n"
            "- Bullet three\n"
            "\n"
            "1. Item one\n"
            "2. Item two\n"
            "   continuation of item two\n"
            "\n"
            "| A | B |\n"
            "| - | - |\n"
            "\n"
            "```python\n"
            "# not a heading, inside the fence\n"
            "\n"
            "print('hi')\n"
            "```\n"
        )

        expected = [
            "# Heading One",
            "A plain paragraph of text.",
            "**Bold-led** paragraph is not a list item.",
            "- Bullet one",
            "- Bullet two",
            "- Bullet three",
            "1. Item one",
            "2. Item two\n   continuation of item two",
            "| A | B |",
            "| - | - |",
            "```python\n# not a heading, inside the fence\n\nprint('hi')\n```",
        ]

        self.assertEqual(split_blocks(document), expected)

    def test_dash_led_paragraph_without_space_is_not_a_list_item(self) -> None:
        """A '---' rule paragraph is not misread as a list-marker start."""
        document = "---\nThis line follows a bare dash rule, not a list marker.\n"
        blocks = split_blocks(document)
        self.assertEqual(len(blocks), 1)
        self.assertIn("---", blocks[0])

    def test_fence_line_inside_a_list_item_does_not_break_the_item(self) -> None:
        """A fence marker on an indented continuation line stays inside the list item."""
        document = "- Bullet with embedded fence\n  ```\n  code inside bullet\n  ```\n"
        blocks = split_blocks(document)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(
            blocks[0],
            "- Bullet with embedded fence\n  ```\n  code inside bullet\n  ```",
        )

    def test_deleted_list_item_removes_only_that_item(self) -> None:
        """Splitting keeps each bullet independently addressable for removed_blocks."""
        document = "- Keep one\n- Keep two\n- Keep three\n"
        self.assertEqual(
            split_blocks(document),
            ["- Keep one", "- Keep two", "- Keep three"],
        )


class TestSplitSentencesPunctuation(unittest.TestCase):
    """Defect 6: split_sentences on a block mixing ';' and '.' terminators."""

    @covers("REQ-0.35.0-14-02")
    def test_semicolon_and_period_both_terminate_sentences(self) -> None:
        """A block with a ';'-joined clause and a '.'-terminated clause splits into two."""
        block = "First clause here; second clause here."
        sentences = split_sentences(block)
        self.assertEqual(sentences, ["First clause here;", "second clause here."])


class TestRemovedBlocksDelta(unittest.TestCase):
    """Defect 6: removed_blocks coverage — reorder, edit, and per-item delete."""

    def test_reordered_block_is_not_removed(self) -> None:
        """Moving a block to a different position never counts as removed."""
        prior = "- First\n- Second\n- Third\n"
        candidate = "- Third\n- First\n- Second\n"
        self.assertEqual(removed_blocks(prior, candidate), [])

    def test_changed_word_block_is_removed(self) -> None:
        """A block whose wording changed is removed (the old text is gone)."""
        prior = "- The quick fox\n"
        candidate = "- The slow fox\n"
        self.assertEqual(removed_blocks(prior, candidate), ["- The quick fox"])

    def test_deleted_list_item_removes_only_that_item(self) -> None:
        """Deleting one bullet from a three-item list removes only that bullet's block."""
        prior = "- First\n- Second\n- Third\n"
        candidate = "- First\n- Third\n"
        self.assertEqual(removed_blocks(prior, candidate), ["- Second"])


class TestValidateRetentionCoverageGaps(unittest.TestCase):
    """Defect 6: uncovered-sentence firing, and a legitimate non_binding declaration."""

    @covers("REQ-0.35.0-14-02")
    def test_uncovered_sentence_fires_when_no_condition_or_non_binding_names_it(self) -> None:
        """A removed block sentence named by no condition and no non_binding is a violation."""
        removed = ["## Block\n\nFirst sentence is covered. Second sentence is not covered."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="First sentence is covered",
                            disposition="dropped",
                            reason="dropped, fully named",
                        )
                    ],
                )
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "approve C1")
        uncovered = [v for v in violations if v.kind == "uncovered-sentence"]
        self.assertTrue(
            uncovered, "The unnamed second sentence must fire an uncovered-sentence violation"
        )

    @covers("REQ-0.35.0-14-02")
    def test_non_binding_declaration_legitimately_covers_a_sentence(self) -> None:
        """A non-empty non_binding quote covering every character satisfies coverage.

        Both the heading label "Block" and the paragraph sentence sit inside
        the same sentence span (no terminator separates them), so both need
        a non_binding declaration under character coverage (Change Log
        2026-09-24, character coverage).
        """
        removed = ["## Block\n\nThis sentence binds nothing important."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[],
                    non_binding=[
                        NonBinding(
                            quote="Block",
                            reason="heading label, non-binding",
                        ),
                        NonBinding(
                            quote="This sentence binds nothing important.",
                            reason="editorial framing only, no operative content",
                        ),
                    ],
                )
            ],
        )

        violations = validate_retention(removed, candidate, map_obj, "")
        uncovered = [v for v in violations if v.kind == "uncovered-sentence"]
        self.assertFalse(
            uncovered, "A legitimate non_binding declaration must satisfy sentence coverage"
        )


class TestValidateRetentionGHI1090Replay(unittest.TestCase):
    """REQ-0.35.0-14-06: #1090 replay fixture, a COMPLETE retention map.

    Prior block is the verbatim text of ``c3582975f:AGENTS.md:234`` — every
    condition quote below is checked against it, and together the KEPT and
    DROPPED conditions cover every meaningful character (Requirement 3 /
    amended 2026-09-24 § Change Log). The candidate is the compressed bullet
    the 2026-09-17 diet landed.
    """

    # Verbatim c3582975f:AGENTS.md:234, without its trailing newline.
    PRIOR_BLOCK = (
        "**REQ-coverage gate (ADR-0.0.25, ADR-0.0.59).** Every **BEHAVIOR** "
        "REQ must have a covering passing test before `gz obpi complete`; "
        "it cannot be waived — `--accept-uncovered` is refused on every "
        "lane, because BEHAVIOR's only proof channel is a `@covers` test "
        "(GHI #537). SUPPORT and STRUCTURAL-FENCE REQs are exempt by "
        "proof channel and never reach the waiver path. Failing-cover "
        "REQs cannot be waived."
    )

    # Candidate from the 2026-09-17 compression.
    CANDIDATE = (
        "- REQ-coverage gate: every BEHAVIOR REQ needs a passing "
        "`@covers` test before `gz obpi complete`; this cannot be waived. "
        "SUPPORT and STRUCTURAL-FENCE REQs use their declared proof "
        "channels."
    )

    # The condition naming the clause ADR-0.35.0 Decision 10's example
    # names: "`--accept-uncovered` is refused on every lane" has no KEPT
    # span in the candidate.
    ACCEPT_UNCOVERED_ID = "C8"
    ACCEPT_UNCOVERED_QUOTE = "— `--accept-uncovered` is refused on every lane"

    # Every other DROPPED condition's id, for building the attestation text.
    OTHER_DROPPED_IDS = ("C2", "C3", "C5", "C7", "C8b", "C9", "C10")

    def _kept_conditions(self) -> list[Condition]:
        """KEPT conditions: text present verbatim in the candidate."""
        return [
            Condition(
                id="C1",
                quote="REQ-coverage gate",
                disposition="kept",
                span="REQ-coverage gate",
            ),
            Condition(id="C4", quote="BEHAVIOR", disposition="kept", span="BEHAVIOR"),
            Condition(
                id="C6",
                quote="gz obpi complete",
                disposition="kept",
                span="gz obpi complete",
            ),
        ]

    def _other_dropped_conditions(self) -> list[Condition]:
        """DROPPED conditions covering every meaningful character NOT kept."""
        return [
            Condition(
                id="C2",
                quote="(ADR-0.0.25, ADR-0.0.59).",
                disposition="dropped",
                reason="citation dropped in the 2026-09-17 diet",
            ),
            Condition(
                id="C3",
                quote="Every",
                disposition="dropped",
                reason="recapitalized to 'every' in the 2026-09-17 diet",
            ),
            Condition(
                id="C5",
                quote=" REQ must have a covering passing test before",
                disposition="dropped",
                reason=(
                    "reworded to 'REQ needs a passing `@covers` test before' in the 2026-09-17 diet"
                ),
            ),
            Condition(
                id="C7",
                quote="; it cannot be waived",
                disposition="dropped",
                reason="reworded to '; this cannot be waived' in the 2026-09-17 diet",
            ),
            Condition(
                id="C8b",
                quote=", because BEHAVIOR's only proof channel is a `@covers` test (GHI #537).",
                disposition="dropped",
                reason="rationale clause dropped in the 2026-09-17 diet",
            ),
            Condition(
                id="C9",
                quote=(
                    "SUPPORT and STRUCTURAL-FENCE REQs are exempt by proof "
                    "channel and never reach the waiver path."
                ),
                disposition="dropped",
                reason=(
                    "reworded to 'SUPPORT and STRUCTURAL-FENCE REQs use their "
                    "declared proof channels.' in the 2026-09-17 diet"
                ),
            ),
            Condition(
                id="C10",
                quote="Failing-cover REQs cannot be waived.",
                disposition="dropped",
                reason="redundant restatement dropped in the 2026-09-17 diet",
            ),
        ]

    def _build_map(self, accept_uncovered_condition: Condition) -> RetentionMap:
        conditions = [
            *self._kept_conditions(),
            accept_uncovered_condition,
            *self._other_dropped_conditions(),
        ]
        return RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[RemovedBlock(removed=self.PRIOR_BLOCK, conditions=conditions)],
        )

    @covers("REQ-0.35.0-14-06")
    def test_complete_map_with_accept_uncovered_dropped_and_attested_passes(self) -> None:
        """Every dropped id attested: a COMPLETE map returns exactly no violations."""
        accept_uncovered = Condition(
            id=self.ACCEPT_UNCOVERED_ID,
            quote=self.ACCEPT_UNCOVERED_QUOTE,
            disposition="dropped",
            reason="Compressed in the 2026-09-17 diet; dropped by operator ruling (GHI #1090)",
        )
        map_obj = self._build_map(accept_uncovered)
        all_dropped_ids = (self.ACCEPT_UNCOVERED_ID, *self.OTHER_DROPPED_IDS)
        attestation = "approve " + ", ".join(all_dropped_ids) + " as drops"

        violations = validate_retention([self.PRIOR_BLOCK], self.CANDIDATE, map_obj, attestation)

        self.assertEqual(
            violations, [], f"A complete, fully-attested map must pass, got: {violations}"
        )

    @covers("REQ-0.35.0-14-06")
    def test_accept_uncovered_id_missing_from_attestation_is_the_only_violation(self) -> None:
        """GHI #1090: the accept-uncovered drop's id absent from attestation is refused alone."""
        accept_uncovered = Condition(
            id=self.ACCEPT_UNCOVERED_ID,
            quote=self.ACCEPT_UNCOVERED_QUOTE,
            disposition="dropped",
            reason="Compressed in the 2026-09-17 diet; dropped by operator ruling (GHI #1090)",
        )
        map_obj = self._build_map(accept_uncovered)
        # Every OTHER dropped id is attested; the accept-uncovered id is not.
        attestation = "approve " + ", ".join(self.OTHER_DROPPED_IDS) + " as drops"

        violations = validate_retention([self.PRIOR_BLOCK], self.CANDIDATE, map_obj, attestation)

        self.assertEqual(len(violations), 1, f"Expected exactly one violation, got: {violations}")
        self.assertEqual(violations[0].kind, "dropped-id-not-attested")
        self.assertIn(self.ACCEPT_UNCOVERED_ID, violations[0].message)

    @covers("REQ-0.35.0-14-06")
    def test_accept_uncovered_marked_kept_at_absent_span_fails(self) -> None:
        """GHI #1090: marking the accept-uncovered clause KEPT at a missing span fails."""
        accept_uncovered = Condition(
            id=self.ACCEPT_UNCOVERED_ID,
            quote=self.ACCEPT_UNCOVERED_QUOTE,
            disposition="kept",
            span=self.ACCEPT_UNCOVERED_QUOTE,  # NOT a substring of self.CANDIDATE
        )
        map_obj = self._build_map(accept_uncovered)
        attestation = "approve " + ", ".join(self.OTHER_DROPPED_IDS) + " as drops"

        violations = validate_retention([self.PRIOR_BLOCK], self.CANDIDATE, map_obj, attestation)

        span_violations = [
            v
            for v in violations
            if v.kind == "kept-span-not-in-candidate" and self.ACCEPT_UNCOVERED_ID in v.message
        ]
        self.assertTrue(
            span_violations,
            f"A KEPT span absent from the candidate must be a violation, got: {violations}",
        )


class TestValidateRetentionCharacterCoverage(unittest.TestCase):
    """ADR-0.35.0 Decision 10 / Change Log 2026-09-24: character coverage, not overlap.

    Every alphanumeric character of a removed block must be marked by some
    occurrence of a non-empty condition or non_binding quote; a quote naming
    only part of a sentence leaves the rest unaccounted for.
    """

    _BLOCK = (
        "- **REQ-coverage gate.** Every BEHAVIOR REQ must have a covering "
        "passing test; it cannot be waived — `--accept-uncovered` is refused "
        "on every lane."
    )
    _CANDIDATE = (
        "- REQ-coverage gate: every BEHAVIOR REQ needs a passing `@covers` "
        "test before `gz obpi complete`; this cannot be waived."
    )

    @covers("REQ-0.35.0-14-06")
    def test_ghi_1090_bypass_is_now_caught_by_character_coverage(self) -> None:
        """A map quoting only three fragments of the sentence is NOT coverage.

        This is the exact bypass GHI #1090 observed: C1/C2/C3 together quote
        only "REQ-coverage gate", "BEHAVIOR REQ" and "cannot be waived",
        leaving "`--accept-uncovered` is refused on every lane" unmarked.
        The overlap rule returned zero violations for this map; character
        coverage must not.
        """
        removed = [self._BLOCK]

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=self._BLOCK,
                    conditions=[
                        Condition(
                            id="C1",
                            quote="REQ-coverage gate",
                            disposition="kept",
                            span="REQ-coverage gate",
                        ),
                        Condition(
                            id="C2",
                            quote="BEHAVIOR REQ",
                            disposition="kept",
                            span="BEHAVIOR REQ",
                        ),
                        Condition(
                            id="C3",
                            quote="cannot be waived",
                            disposition="kept",
                            span="cannot be waived",
                        ),
                    ],
                )
            ],
        )

        violations = validate_retention(removed, self._CANDIDATE, map_obj, "")

        uncovered = [v for v in violations if v.kind == "uncovered-sentence"]
        self.assertTrue(
            uncovered, "The unaccounted '--accept-uncovered' clause must fire a violation"
        )
        self.assertTrue(
            any("accept-uncovered" in v.message for v in uncovered),
            f"An uncovered-sentence violation must quote the missed clause, got: {uncovered}",
        )

    @covers("REQ-0.35.0-14-02")
    def test_full_legitimate_map_covering_every_character_yields_no_violations(self) -> None:
        """A map whose KEPT/DROPPED conditions together cover every character passes.

        Every phrase present in the candidate is KEPT at that span; every
        phrase absent from the candidate is DROPPED with a reason and its id
        in the attestation text. Together the seven conditions mark every
        alphanumeric character of the removed block.
        """
        removed = [self._BLOCK]

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=self._BLOCK,
                    conditions=[
                        Condition(
                            id="C1",
                            quote="REQ-coverage gate.",
                            disposition="kept",
                            span="REQ-coverage gate",
                        ),
                        Condition(
                            id="C2",
                            quote="BEHAVIOR REQ",
                            disposition="kept",
                            span="BEHAVIOR REQ",
                        ),
                        Condition(
                            id="C3",
                            quote="cannot be waived",
                            disposition="kept",
                            span="cannot be waived",
                        ),
                        Condition(
                            id="C4",
                            quote="Every",
                            disposition="dropped",
                            reason="compressed away; capitalization not in candidate",
                        ),
                        Condition(
                            id="C5",
                            quote="must have a covering passing test;",
                            disposition="dropped",
                            reason="reworded in the 2026-09-17 diet",
                        ),
                        Condition(
                            id="C6",
                            quote="it",
                            disposition="dropped",
                            reason="leading pronoun dropped with the reworded clause",
                        ),
                        Condition(
                            id="C7",
                            quote="— `--accept-uncovered` is refused on every lane.",
                            disposition="dropped",
                            reason="Compressed in 2026-09-17 diet; dropped by operator ruling",
                        ),
                    ],
                )
            ],
        )
        attestation = "approve C4, C5, C6 and C7 as drops"

        violations = validate_retention(removed, self._CANDIDATE, map_obj, attestation)
        self.assertEqual(violations, [])

    @covers("REQ-0.35.0-14-02")
    def test_sentence_split_across_two_conditions_together_covers_it(self) -> None:
        """Two conditions whose quotes together span a sentence satisfy coverage."""
        removed = ["The quick brown fox jumps over the lazy dog."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="The quick brown fox",
                            disposition="dropped",
                            reason="split part one",
                        ),
                        Condition(
                            id="C2",
                            quote="jumps over the lazy dog.",
                            disposition="dropped",
                            reason="split part two",
                        ),
                    ],
                )
            ],
        )
        attestation = "approve C1 and C2"

        violations = validate_retention(removed, candidate, map_obj, attestation)
        uncovered = [v for v in violations if v.kind == "uncovered-sentence"]
        self.assertFalse(
            uncovered,
            "Two conditions whose quotes together cover the sentence must not "
            "produce a coverage violation",
        )

    @covers("REQ-0.35.0-14-02")
    def test_partially_covered_sentence_names_the_unmarked_remainder(self) -> None:
        """A quote covering only a prefix of the sentence names the missed remainder."""
        removed = ["Heavy lane stops completion unless foundation kind applies."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Heavy lane stops completion",
                            disposition="dropped",
                            reason="only the prefix is named",
                        ),
                    ],
                )
            ],
        )
        attestation = "approve C1"

        violations = validate_retention(removed, candidate, map_obj, attestation)
        uncovered = [v for v in violations if v.kind == "uncovered-sentence"]
        self.assertTrue(uncovered, "The unmarked remainder must fire a coverage violation")
        self.assertTrue(
            any("unless foundation kind applies" in v.message for v in uncovered),
            f"The violation must name the unmarked remainder, got: {uncovered}",
        )

    @covers("REQ-0.35.0-14-02")
    def test_symbol_outside_quotes_is_meaningful_and_reported(self) -> None:
        """Amended Requirement 3: a symbol like '>=' counts even though it is not alnum.

        Quoting the words on either side of '>=' is not coverage of '>=' itself:
        the prior ``isalnum()`` check treated symbols as free, so a dropped
        qualifier expressed only in punctuation could vanish silently.
        """
        removed = ["- Retry at most 3 times when latency >= 200 ms."]
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed[0],
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Retry at most 3 times when latency",
                            disposition="dropped",
                            reason="reworded",
                        ),
                        Condition(
                            id="C2",
                            quote="200 ms",
                            disposition="dropped",
                            reason="reworded",
                        ),
                    ],
                )
            ],
        )
        attestation = "approve C1 and C2"

        violations = validate_retention(removed, candidate, map_obj, attestation)
        uncovered = [v for v in violations if v.kind == "uncovered-sentence"]
        self.assertTrue(uncovered, "The unquoted '>=' must fire a coverage violation")
        self.assertTrue(
            any(">=" in v.message for v in uncovered),
            f"The violation must name the unquoted '>=', got: {uncovered}",
        )


class TestValidateRetentionSpanNormalization(unittest.TestCase):
    """Requirement 4: a KEPT span is normalized exactly as the candidate is."""

    @covers("REQ-0.35.0-14-02")
    def test_crlf_candidate_with_span_present_in_lf_form_is_not_a_violation(self) -> None:
        """A CRLF candidate holding the span's LF-normalized text passes the span check."""
        removed_block = "Line one text.\nLine two text."
        candidate_crlf = "Preamble.\r\nLine one text.\r\nLine two text.\r\n"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed_block,
                    conditions=[
                        Condition(
                            id="C1",
                            quote="Line one text.\nLine two text.",
                            disposition="kept",
                            span="Line one text.\nLine two text.",
                        ),
                    ],
                )
            ],
        )

        violations = validate_retention([removed_block], candidate_crlf, map_obj, "")
        span_violations = [v for v in violations if v.kind == "kept-span-not-in-candidate"]
        self.assertFalse(
            span_violations,
            f"A span present in the candidate's LF-normalized form must not be a "
            f"violation, got: {span_violations}",
        )


class TestValidateRetentionWholeMapValidation(unittest.TestCase):
    """Requirement 3/6: every RemovedBlock in the map is validated, whichever

    lookup order is used — duplicate and unknown entries are never silently
    skipped, and their DROPPED conditions are still checked.
    """

    @covers("REQ-0.35.0-14-02")
    def test_two_entries_for_the_same_removed_block_is_a_violation(self) -> None:
        """Two map entries naming the same removed block text is duplicate-removed-block."""
        removed_block = "## Block\n\nSome text."
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=removed_block,
                    conditions=[
                        Condition(id="C1", quote="Block", disposition="dropped", reason="r1")
                    ],
                ),
                RemovedBlock(
                    removed=removed_block,
                    conditions=[
                        Condition(id="C2", quote="Some text", disposition="dropped", reason="r2")
                    ],
                ),
            ],
        )

        violations = validate_retention([removed_block], candidate, map_obj, "approve C1 and C2")
        duplicate_violations = [v for v in violations if v.kind == "duplicate-removed-block"]
        self.assertTrue(
            duplicate_violations, "Two entries for the same removed block must be flagged"
        )

    @covers("REQ-0.35.0-14-02")
    def test_entry_naming_no_removed_block_is_flagged_and_its_dropped_conditions_checked(
        self,
    ) -> None:
        """A map entry for a block absent from this delta is unknown-removed-block,

        and its DROPPED condition is still checked for reason/attestation —
        an unknown entry is never silently skipped.
        """
        extraneous_block = "## Never Removed\n\nGhost text."
        candidate = "## Other"

        map_obj = RetentionMap(
            surface="AGENTS.md",
            consumer="root",
            extracted_by="Reviewer",
            mapped_by="Author",
            blocks=[
                RemovedBlock(
                    removed=extraneous_block,
                    conditions=[
                        Condition(id="C1", quote="Ghost text", disposition="dropped", reason="")
                    ],
                ),
            ],
        )

        # No block was actually removed in this delta.
        violations = validate_retention([], candidate, map_obj, "")

        unknown_violations = [v for v in violations if v.kind == "unknown-removed-block"]
        self.assertTrue(unknown_violations, "An entry naming no removed block must be flagged")

        reason_violations = [v for v in violations if v.kind == "dropped-without-reason"]
        self.assertTrue(
            reason_violations,
            "A DROPPED condition on an unknown entry is still checked for a reason",
        )
