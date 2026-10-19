"""The identity seam's composition and spelling-fallback helpers (drydock RO-2 tranche 5).

`docs/governance/harbor-ro2-identity-seam.md` § The seam, item 3 and § Tranches
row 5. Nothing outside the seam composes an id from parts, scans a child prefix,
normalizes input to an id, or recovers a parent from spelling; every such reader
calls these helpers, which are the seam's marked fallback for the places that
hold no ledger.
"""

from __future__ import annotations

import unittest

from gzkit.core import models
from gzkit.core.id_resolver import IdentityContext, parent_of


class TestComposition(unittest.TestCase):
    def test_each_kind_composes_from_its_parts(self) -> None:
        self.assertEqual(models.compose_adr_id("0.3.1"), "ADR-0.3.1")
        self.assertEqual(models.compose_adr_full_id("0.3.1", "foo"), "ADR-0.3.1-foo")
        self.assertEqual(models.compose_pool_adr_id("foo"), "ADR-pool.foo")
        self.assertEqual(models.compose_obpi_id("0.3.1", "04"), "OBPI-0.3.1-04")
        self.assertEqual(models.compose_obpi_id("0.3.1", "04", "bar"), "OBPI-0.3.1-04-bar")
        self.assertEqual(models.compose_req_id("0.3.1", "04", "02"), "REQ-0.3.1-04-02")
        self.assertEqual(models.compose_task_id("0.3.1", "04", "02", "01"), "TASK-0.3.1-04-02-01")

    def test_an_integer_part_is_zero_padded_to_the_grammar_width(self) -> None:
        self.assertEqual(models.compose_obpi_id("0.3.1", 4), "OBPI-0.3.1-04")
        self.assertEqual(models.compose_req_id("0.3.1", 4, 2), "REQ-0.3.1-04-02")
        self.assertEqual(models.compose_task_id("0.3.1", 4, 2, 1), "TASK-0.3.1-04-02-01")

    def test_composed_ids_parse_back_through_the_grammar(self) -> None:
        self.assertEqual(
            str(models.TaskId.parse(models.compose_task_id("0.3.1", 4, 2, 1))),
            "TASK-0.3.1-04-02-01",
        )
        self.assertEqual(
            str(models.ReqId.parse(models.compose_req_id("0.3.1", 4, 2))), "REQ-0.3.1-04-02"
        )

    def test_child_prefixes_end_where_the_next_part_begins(self) -> None:
        self.assertEqual(models.adr_prefix("0.3.1"), "ADR-0.3.1-")
        self.assertEqual(models.obpi_prefix("0.3.1"), "OBPI-0.3.1-")
        self.assertEqual(models.req_prefix("0.3.1"), "REQ-0.3.1-")
        self.assertEqual(models.req_prefix("0.3.1", "04"), "REQ-0.3.1-04-")
        self.assertEqual(models.task_prefix("0.3.1", "04", "02"), "TASK-0.3.1-04-02-")

    def test_a_prefix_never_reaches_a_longer_semver(self) -> None:
        self.assertFalse("REQ-0.3.10-01-01".startswith(models.req_prefix("0.3.1")))
        self.assertTrue("REQ-0.3.1-01-01".startswith(models.req_prefix("0.3.1")))


class TestInputNormalization(unittest.TestCase):
    def test_a_bare_adr_input_gains_its_kind_and_a_full_one_is_unchanged(self) -> None:
        self.assertEqual(models.normalize_adr_input("0.3.1-foo"), "ADR-0.3.1-foo")
        self.assertEqual(models.normalize_adr_input("ADR-0.3.1-foo"), "ADR-0.3.1-foo")

    def test_a_bare_obpi_input_gains_its_kind(self) -> None:
        self.assertEqual(models.normalize_obpi_input("0.3.1-04"), "OBPI-0.3.1-04")
        self.assertEqual(models.normalize_obpi_input("OBPI-0.3.1-04"), "OBPI-0.3.1-04")

    def test_a_bare_pool_input_gains_the_pool_prefix(self) -> None:
        self.assertEqual(models.normalize_pool_adr_input("foo"), "ADR-pool.foo")
        self.assertEqual(models.normalize_pool_adr_input("ADR-pool.foo"), "ADR-pool.foo")


class TestSpellingFallback(unittest.TestCase):
    def test_each_kind_names_the_parent_its_spelling_carries(self) -> None:
        self.assertEqual(models.spelled_parent("OBPI-0.3.1-04-bar"), "ADR-0.3.1")
        self.assertEqual(models.spelled_parent("OBPI-0.3.1-04"), "ADR-0.3.1")
        self.assertEqual(models.spelled_parent("REQ-0.3.1-04-02"), "OBPI-0.3.1-04")
        self.assertEqual(models.spelled_parent("TASK-0.3.1-04-02-01"), "REQ-0.3.1-04-02")

    def test_an_id_with_no_spelled_parent_names_none(self) -> None:
        self.assertIsNone(models.spelled_parent("ADR-0.3.1-foo"))
        self.assertIsNone(models.spelled_parent("ADR-pool.foo"))
        self.assertIsNone(models.spelled_parent("TASK-direct-fix"))
        self.assertIsNone(models.spelled_parent("not-an-id"))

    def test_a_parent_chain_ends_at_the_adr(self) -> None:
        self.assertEqual(
            models.spelled_chain("TASK-0.3.1-04-02-01"),
            ("REQ-0.3.1-04-02", "OBPI-0.3.1-04", "ADR-0.3.1"),
        )
        self.assertEqual(models.spelled_chain("ADR-0.3.1"), ())

    def test_the_resolver_fallback_agrees_with_the_pure_helper(self) -> None:
        context = IdentityContext(graph={}, task_obpis={"TASK-0.3.1-04-02-01": "OBPI-0.3.1-04"})
        link = parent_of("TASK-0.3.1-04-02-01", context)
        assert link is not None
        self.assertEqual(link.parent_id, models.spelled_parent("TASK-0.3.1-04-02-01"))
        self.assertEqual(link.source, "spelling")


class TestHopsAndTerms(unittest.TestCase):
    def test_each_hop_names_only_its_own_parent_kind(self) -> None:
        self.assertEqual(models.obpi_adr_id("OBPI-0.3.1-04-bar"), "ADR-0.3.1")
        self.assertIsNone(models.obpi_adr_id("REQ-0.3.1-04-02"))
        self.assertEqual(models.req_obpi_id("REQ-0.3.1-04-02"), "OBPI-0.3.1-04")
        self.assertIsNone(models.req_obpi_id("OBPI-0.3.1-04"))
        self.assertEqual(models.task_req_id("TASK-0.3.1-04-02-01"), "REQ-0.3.1-04-02")
        self.assertEqual(models.task_obpi_id("TASK-0.3.1-04-02-01"), "OBPI-0.3.1-04")
        self.assertIsNone(models.task_obpi_id("TASK-fix-a-thing"))

    def test_obpi_parts_give_semver_and_item_whatever_the_slug_case(self) -> None:
        self.assertEqual(models.obpi_parts("OBPI-0.3.1-04-Bar"), ("0.3.1", "04"))
        self.assertIsNone(models.obpi_parts("OBPI-0.3.1"))

    def test_the_version_term_is_the_token_after_the_kind(self) -> None:
        self.assertEqual(models.adr_version_term("ADR-0.3.1-foo"), "0.3.1")
        self.assertEqual(models.adr_version_term("ADR-pool.foo-bar"), "pool.foo")

    def test_a_req_stem_has_no_trailing_separator(self) -> None:
        self.assertEqual(models.req_stem("0.3.1", 4), "REQ-0.3.1-04")

    def test_an_obpi_name_is_its_slug_else_its_item_else_itself(self) -> None:
        self.assertEqual(models.obpi_display_name("OBPI-0.3.1-04-bar"), "bar")
        self.assertEqual(models.obpi_display_name("OBPI-0.3.1-04"), "04")
        self.assertEqual(models.obpi_display_name("odd"), "odd")

    def test_an_item_reference_matches_a_bare_item_whatever_its_padding(self) -> None:
        import re

        pattern = models.obpi_item_reference_pattern(4)
        self.assertTrue(re.search(pattern, "(OBPI-04)"))
        self.assertTrue(re.search(pattern, "(OBPI-4)"))
        self.assertFalse(re.search(pattern, "(OBPI-40)"))

    def test_a_probe_id_composes_from_a_kind_and_names_no_artifact(self) -> None:
        probe = models.compose_probe_id(models.IdKind.OBPI, "nc-x")
        self.assertEqual(probe, "OBPI-nc-x")
        self.assertIsNone(models.spelled_parent(probe))

    def test_the_hook_template_composes_the_same_adr_id(self) -> None:
        self.assertEqual(models.ADR_ID_TEMPLATE.format(semver="0.3.1"), "ADR-0.3.1")


class TestPartsOfAnId(unittest.TestCase):
    def test_an_obpi_gives_its_item_slug_and_short_form(self) -> None:
        self.assertEqual(models.obpi_slug("OBPI-0.28.0-01-context-core"), "context-core")
        self.assertIsNone(models.obpi_slug("OBPI-0.28.0-01"))
        self.assertEqual(models.obpi_short_id("OBPI-0.28.0-01-context-core"), "OBPI-0.28.0-01")
        self.assertEqual(models.obpi_item("OBPI-0.28.0-01-context-core"), "01")
        self.assertIsNone(models.obpi_item("ADR-0.28.0"))

    def test_a_pool_adr_gives_its_slug(self) -> None:
        self.assertEqual(models.pool_slug("ADR-pool.some-idea"), "some-idea")
        self.assertIsNone(models.pool_slug("ADR-0.1.0-x"))

    def test_a_full_adr_gives_its_slug(self) -> None:
        self.assertEqual(models.adr_slug("ADR-0.1.0-some-idea"), "some-idea")
        self.assertIsNone(models.adr_slug("ADR-0.1.0"))
        self.assertIsNone(models.adr_slug("ADR-pool.x"))

    def test_a_req_gives_its_item(self) -> None:
        self.assertEqual(models.req_obpi_item("REQ-0.3.1-04-02"), "04")
        self.assertIsNone(models.req_obpi_item("OBPI-0.3.1-04"))


if __name__ == "__main__":
    unittest.main()
