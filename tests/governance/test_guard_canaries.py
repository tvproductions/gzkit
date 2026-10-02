"""GHI #1154 item 5 — a reviewed mutant is bound to each registered claim.

A claim's proof can be erased without anyone deciding to: the guard changes, or the test that
kills a mutant of it is renamed, weakened or deleted. Operator ruling (defaults taken
2026-10-01, "approve all three"): a canary is bound by a hash of the guard source, the claim
and the designated failing test id. These tests derive from that ruling: they hold the live
registry to its binding, run every canary's mutant on an isolated copy, and drive each way a
binding can go stale.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit import guard_canary as gc
from gzkit.enforcement import production_enforcement_registry
from gzkit.guard_canary import Canary, CanaryMutation
from gzkit.registries import registry_path

_ROOT = Path(__file__).resolve().parents[2]
_GUARD = "gzkit.guard_canary:binding_hash"
_CLAIM = "arb-receipt-red-run-refused"
_PASSING_TEST = "tests.governance.test_guard_canaries.TestBindingHash.test_the_hash_is_stable"


def _resolved(guard: str) -> tuple[str, Path]:
    """Return the guard's (source, file), failing the test when it does not resolve."""
    found = gc.resolve_guard(guard)
    if found is None:
        raise AssertionError(f"guard {guard!r} does not resolve")
    return found


def _registered() -> set[str]:
    return {r.claim_id for r in production_enforcement_registry()}


def _canary(**overrides) -> Canary:
    """Return a canary bound to ``binding_hash`` itself, with *overrides* applied."""
    source, _ = _resolved(_GUARD)
    fields = {
        "claim_id": _CLAIM,
        "guard": _GUARD,
        "failing_test": _PASSING_TEST,
        "mutation": CanaryMutation(
            find='"\\n".join((guard_source,', replace='"\\n".join((', label="m"
        ),
        "authority": "test",
    }
    fields.update(overrides)
    fields.setdefault(
        "binding_sha256",
        gc.binding_hash(source, str(fields["claim_id"]), str(fields["failing_test"])),
    )
    return Canary(**fields)


class _Project:
    """A throwaway project root holding a canary registry and its roster."""

    def __init__(self, canaries: list[Canary], roster: list[str]) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        files = {
            "guard_canaries.json": {"canaries": [c.model_dump() for c in canaries]},
            "guard_canary_grandfather.json": {"claims": roster},
        }
        registry_path(self.root, "guard_canaries.json").parent.mkdir()
        for name, payload in files.items():
            registry_path(self.root, name).write_text(json.dumps(payload), encoding="utf-8")

    def __enter__(self) -> Path:
        return self.root

    def __exit__(self, *_exc) -> None:
        self._tmp.cleanup()


def _findings(canaries: list[Canary], roster: list[str] | None = None) -> list[str]:
    registered = _registered()
    covered = {c.claim_id for c in canaries}
    disclosed = sorted(registered - covered) if roster is None else roster
    with _Project(canaries, disclosed) as root:
        return [e.message for e in gc.check_canaries(root, registered)]


class TestBindingHash(unittest.TestCase):
    def test_the_hash_is_stable(self):
        self.assertEqual(gc.binding_hash("g", "c", "t"), gc.binding_hash("g", "c", "t"))

    def test_the_hash_is_the_sha256_of_the_three_subjects_joined_by_newlines(self):
        expected = hashlib.sha256(b"guard\nclaim\ntest").hexdigest()
        self.assertEqual(gc.binding_hash("guard", "claim", "test"), expected)

    def test_each_subject_changes_the_hash(self):
        base = gc.binding_hash("g", "c", "t")
        for variant in (("g2", "c", "t"), ("g", "c2", "t"), ("g", "c", "t2")):
            with self.subTest(variant=variant):
                self.assertNotEqual(gc.binding_hash(*variant), base)


class TestTheLiveRegistry(unittest.TestCase):
    def test_every_registered_claim_has_a_bound_canary_or_a_disclosure(self):
        self.assertEqual(gc.check_canaries(_ROOT, _registered()), [])

    def test_every_canary_mutant_is_killed_by_its_designated_test(self):
        runs = gc.run_canaries(_ROOT)
        self.assertEqual({r.claim_id for r in runs}, {c.claim_id for c in gc.load_canaries(_ROOT)})
        self.assertEqual([r for r in runs if r.outcome != "killed"], [])

    def test_a_canary_run_leaves_the_working_tree_as_it_found_it(self):
        guard_file = _resolved(gc.load_canaries(_ROOT)[0].guard)[1]
        before = guard_file.read_bytes()
        gc.run_canaries(_ROOT, claim_ids={gc.load_canaries(_ROOT)[0].claim_id})
        self.assertEqual(guard_file.read_bytes(), before)


class TestABindingGoesStale(unittest.TestCase):
    def test_a_fresh_canary_is_clean(self):
        self.assertEqual(_findings([_canary()]), [])

    def test_a_changed_guard_source_makes_the_binding_stale(self):
        canary = _canary()  # bound to the guard as it is now
        source, path = _resolved(_GUARD)
        with mock.patch.object(gc, "resolve_guard", lambda _g: (source + "# edited\n", path)):
            messages = _findings([canary])
        self.assertTrue(any("binding is stale" in m for m in messages), messages)

    def test_a_different_claim_makes_the_binding_stale(self):
        canary = _canary().model_copy(update={"claim_id": "tidy-breach-exits-three"})
        self.assertTrue(any("binding is stale" in m for m in _findings([canary])))

    def test_a_different_designated_test_makes_the_binding_stale(self):
        other = _PASSING_TEST.replace(
            "test_the_hash_is_stable", "test_each_subject_changes_the_hash"
        )
        canary = _canary().model_copy(update={"failing_test": other})
        self.assertTrue(any("binding is stale" in m for m in _findings([canary])))

    def test_a_deleted_designated_test_is_the_silent_erasure_and_is_refused(self):
        gone = "tests.governance.test_guard_canaries.TestBindingHash.test_no_such_test"
        messages = _findings([_canary(failing_test=gone)])
        self.assertTrue(any("no longer resolves" in m for m in messages), messages)

    def test_a_designated_test_in_a_module_that_does_not_exist_is_refused(self):
        messages = _findings([_canary(failing_test="tests.no_such_module.TestX.test_y")])
        self.assertTrue(any("no longer resolves" in m for m in messages), messages)

    def test_a_designated_test_under_no_importable_package_is_refused(self):
        # No prefix of the id is a module at all, unlike `tests.no_such_module`, whose
        # top-level package resolves and whose miss is a missing definition.
        for test_id in ("no_such_package.TestX.test_y", "no_such_package"):
            with self.subTest(test_id=test_id):
                self.assertFalse(gc.resolves_test_id(test_id))
                messages = _findings([_canary(failing_test=test_id)])
                self.assertTrue(any("no longer resolves" in m for m in messages), messages)

    def test_a_guard_that_does_not_resolve_is_refused(self):
        messages = _findings([_canary(guard="gzkit.guard_canary:no_such_function")])
        self.assertTrue(any("does not resolve" in m for m in messages), messages)

    def test_a_canary_for_a_claim_that_is_not_registered_is_refused(self):
        messages = _findings([_canary(claim_id="no-such-claim")], roster=sorted(_registered()))
        self.assertTrue(any("not registered" in m for m in messages), messages)

    def test_a_no_op_mutation_is_refused(self):
        mutation = CanaryMutation(find="guard_source", replace="guard_source", label="noop")
        messages = _findings([_canary(mutation=mutation)])
        self.assertTrue(any("not a single change" in m for m in messages), messages)

    def test_a_mutation_target_absent_from_the_guard_is_refused(self):
        mutation = CanaryMutation(find="text that is not there", replace="x", label="absent")
        messages = _findings([_canary(mutation=mutation)])
        self.assertTrue(any("not a single change" in m for m in messages), messages)

    def test_a_mutation_target_in_the_guard_but_repeated_in_the_file_is_refused(self):
        # "Return " occurs once in `binding_hash` and again in other docstrings of the file.
        mutation = CanaryMutation(find="Return ", replace="Yield ", label="dup")
        messages = _findings([_canary(mutation=mutation)])
        self.assertTrue(any("not unique" in m for m in messages), messages)

    def test_a_mutation_target_repeated_inside_the_guard_is_refused_as_not_single(self):
        mutation = CanaryMutation(find="claim_id", replace="claim_idx", label="dup")
        messages = _findings([_canary(mutation=mutation)])
        self.assertTrue(any("not a single change" in m for m in messages), messages)


class TestTheRosterIsShrinkOnly(unittest.TestCase):
    def test_a_claim_with_no_canary_and_no_disclosure_is_refused(self):
        messages = _findings([_canary()], roster=[])
        self.assertTrue(any("has no guard mutation canary" in m for m in messages))

    def test_a_claim_that_gained_a_canary_must_leave_the_roster(self):
        everything = sorted(_registered())
        messages = _findings([_canary()], roster=everything)
        self.assertTrue(any("now has a canary" in m for m in messages))

    def test_a_claim_that_is_no_longer_registered_must_leave_the_roster(self):
        roster = [*sorted(_registered() - {_CLAIM}), "retired-claim"]
        messages = _findings([_canary()], roster=roster)
        self.assertTrue(any("no longer registered" in m for m in messages))


class TestARunThatDoesNotKill(unittest.TestCase):
    def test_a_mutant_no_test_catches_survives_and_is_not_reported_killed(self):
        # The designated test is unrelated to the guard, so the mutant is never caught.
        with mock.patch.object(gc, "load_canaries", lambda _root: [_canary()]):
            runs = gc.run_canaries(_ROOT)
        self.assertEqual([r.outcome for r in runs], ["survived"])

    def test_an_unresolvable_guard_is_invalid_not_killed(self):
        canary = _canary(guard="gzkit.guard_canary:no_such_function")
        with mock.patch.object(gc, "load_canaries", lambda _root: [canary]):
            runs = gc.run_canaries(_ROOT)
        self.assertEqual([r.outcome for r in runs], ["invalid"])


class TestRunsCanBeNarrowed(unittest.TestCase):
    def test_a_run_limited_to_a_claim_runs_only_that_claim(self):
        canaries = [_canary(), _canary(claim_id="tidy-breach-exits-three")]
        with mock.patch.object(gc, "load_canaries", lambda _root: canaries):
            runs = gc.run_canaries(_ROOT, claim_ids={"tidy-breach-exits-three"})
        self.assertEqual([r.claim_id for r in runs], ["tidy-breach-exits-three"])


class TestUnreviewedCanariesAreNamed(unittest.TestCase):
    def test_a_canary_with_no_reviewer_is_listed_and_a_reviewed_one_is_not(self):
        pending, reviewed = _canary(), _canary(claim_id="tidy-breach-exits-three")
        reviewed = reviewed.model_copy(update={"reviewed_by": "g0"})
        with mock.patch.object(gc, "load_canaries", lambda _root: [pending, reviewed]):
            self.assertEqual(gc.unreviewed(_ROOT), [_CLAIM])


if __name__ == "__main__":
    unittest.main()
