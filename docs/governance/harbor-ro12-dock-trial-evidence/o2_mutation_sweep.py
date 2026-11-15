# noqa: INP001 — a dated evidence script run by path, never imported as a package
"""RP-12 O2's dock trial: every refusal shown red then green by a mutation sweep.

A dated evidence script (`docs/governance/harbor-ro12-contractor-kit.md`, rulings 27,
90, 91 and 92). Ruling 27 has each order's dock trial run its own refusal tests at full
strength, each refusal shown red then green; ruling 90 chose a mutation sweep for O2, and
ruling 92 takes its scope from O2's rows of § Mode Contract: every function and verb
those rows cite, its O2 arms where it also serves a package, against the test modules
those rows name as self-tests.

Most mutants are derived, not hand-picked: an AST pass over O2's guard functions finds
every ``if`` whose body refuses (a ``_refuse`` call, a raised ``PolicyBreachError``,
``ResourceNotFoundError`` or ``OrderStoreError``, a returned refusal sentence or list of
them, a breach appended) and, in the catalog audit, every comprehension filter that
collects a breach, and writes one mutant per guard that replaces its test with
``False``, the refusal switched off. The rest are written by hand (``MANUAL``) for
guards the pass cannot see: an O2 arm of a shared function, a guard that returns early,
a refusal spliced in by an if-expression, and the schema's conditionals, which compile
as Python and so run through the same instrument. Each mutant runs through
:func:`gzkit.mutation_witness.run_mutation_sweep` in an isolated copy of the tree,
against O2's test modules, nominating every test those modules execute, so a kill is
an O2 test failing on an assertion; the record lists the tests that failed, for the
inspector to judge that they assert that refusal. The unmutated tree is the green
run. Usage:

    uv run python docs/governance/harbor-ro12-dock-trial-evidence/o2_mutation_sweep.py <out.json>
"""

import ast
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(REPO / "src")]

from gzkit.mutation_witness import Mutation, MutationSweep, run_mutation_sweep  # noqa: E402

BOOTSTRAP = "import sys; sys.path[:0] = ['src', '.']; import unittest; unittest.main(module=None)"
MODULES = (
    "tests.test_order_ledger",
    "tests.test_order_ledger_schema",
    "tests.test_order_run",
    "tests.test_work_package_ledger",
    "tests.commands.test_wp_order",
    "tests.commands.test_wp_order_run",
    "tests.commands.test_wp_order_acceptance",
    "tests.commands.test_wp_req",
    "tests.governance.test_catalog_orders",
    "tests.governance.test_catalog_repair_reqs",
    # Ruling 92, as put: the two modules join the rows' ten self-test modules.
    "tests.commands.test_wp_run",
    "tests.commands.test_wp_acceptance",
)
#: O2's guard functions per file; ``None`` takes every function in the file.
GUARDS: dict[str, tuple[str, ...] | None] = {
    "src/gzkit/order_ledger.py": None,
    "src/gzkit/commands/wp_order.py": None,
    "src/gzkit/governance/trust_audits/catalog.py": (
        "_repair_req_breaches",
        "req_breaches",
        "_supersession_cycles",
        "_alias_breaches",
        "order_breaches",
        "_booked_order_findings",
        "_booked_req_findings",
    ),
    "src/gzkit/work_package_run.py": (
        "_require_order",
        "_package_order",
        "_order_subject",
        "_check_not_stopped",
        "_dispatch_subject",
        "record_work_package_dispatch",
        "_check_blockable",
        "record_work_package_block",
        "record_work_package_unblock",
        "open_unclaimed_dispatches",
        "run_positions",
    ),
    "src/gzkit/work_package_ledger.py": (
        "_check_repair_close",
        "_check_baselined",
        "footprint_sealed",
        "declared_modules",
    ),
    "src/gzkit/order_store.py": ("stage_order",),
    "src/gzkit/commands/wp_req.py": None,
    "src/gzkit/req_store.py": ("stage_repair_req",),
    # Ruling 92: each cited function, verb and module swept whole.
    "src/gzkit/work_package_fence.py": None,
    "src/gzkit/commands/wp.py": ("wp_dispatch_cmd", "wp_block_cmd", "wp_unblock_cmd"),
    "src/gzkit/acceptance_package.py": ("order_contract",),
    "src/gzkit/acceptance_store.py": (
        "resolve_brief",
        "_without_departed",
        "initialize",
        "record_human_review",
        "owed_ids",
        "round_bound_refusal",
    ),
    "src/gzkit/schemas/ledger.json": (),
}
_SCHEMA_INDENT = " " * 12
REFUSERS = {
    "_refuse",
    "_refuse_move",
    "store_broken",
    "PolicyBreachError",
    "ResourceNotFoundError",
    "OrderStoreError",
    "ReqStoreError",
}
#: Guards the AST pass cannot see, each written by hand: an order store guard that
#: skips the breach with ``continue``, two booked-record checks that return their
#: finding as a list, the id series built with no ``if`` filter, the round bound
#: spliced in by an if-expression, and the order arms of the run module's guards,
#: whose functions also hold package arms outside O2.
#: The schema conditionals' property rules (the third inspection's finding 3).
_SCHEMA_PROPERTY_MUTANTS: tuple[Mutation, ...] = (
    Mutation(
        find=(
            '              "attestor": {\n'
            '                "type": "string",\n'
            '                "min_length": 1\n'
            "              },\n"
        ),
        replace='              "attestor": {\n                "type": "string"\n              },\n',
        label="ledger.json:order_transitioned a blank attestor passes",
    ),
    Mutation(
        find=(
            '              "attestation_text": {\n'
            '                "type": "string",\n'
            '                "min_length": 1\n'
            "              }\n"
        ),
        replace=(
            '              "attestation_text": {\n'
            '                "type": "string"\n'
            "              }\n"
        ),
        label="ledger.json:order_transitioned a blank attestation_text passes",
    ),
    Mutation(
        find=(
            '              "residual_risk": {\n'
            '                "type": "string",\n'
            '                "min_length": 1\n'
            "              }\n"
        ),
        replace=(
            '              "residual_risk": {\n'
            '                "type": "string"\n'
            "              }\n"
        ),
        label="ledger.json:order_transitioned a blank residual_risk passes",
    ),
    Mutation(
        find=(
            '              "superseded_by": {\n'
            '                "type": "string",\n'
            '                "min_length": 1\n'
            "              }\n"
        ),
        replace=(
            '              "superseded_by": {\n'
            '                "type": "string"\n'
            "              }\n"
        ),
        label="ledger.json:order_transitioned a blank superseded_by passes",
    ),
    Mutation(
        find=(
            '              "revisit_condition": {\n'
            '                "type": "string",\n'
            '                "min_length": 1\n'
            "              }\n"
        ),
        replace=(
            '              "revisit_condition": {\n'
            '                "type": "string"\n'
            "              }\n"
        ),
        label="ledger.json:order_transitioned a blank revisit_condition passes",
    ),
    Mutation(
        find=(
            '              "acceptance_ready": {\n'
            '                "type": "boolean"\n'
            "              }\n"
        ),
        replace=(
            '              "acceptance_ready": {\n'
            '                "type": ["boolean", "null"]\n'
            "              }\n"
        ),
        label="ledger.json:order_transitioned a null acceptance_ready passes",
    ),
)

MANUAL: dict[str, tuple[Mutation, ...]] = {
    "src/gzkit/order_ledger.py": (
        Mutation(
            find="    if not (later := successors.get(req)):\n        return\n",
            replace="    if True:\n        return\n",
            label="order_ledger.py:_check_not_superseded a superseded REQ freezes",
        ),
        Mutation(
            find="    if not footprint_sealed(ledger, package.id):\n        return\n",
            replace="    if True:\n        return\n",
            label="order_ledger.py:_check_seal_grows a sealed footprint drops a path",
        ),
    ),
    "src/gzkit/commands/wp_order.py": (
        Mutation(
            find=(
                "    package = _package(catalog, work_package)\n"
                "    _booked_lost(catalog, ledger)\n"
            ),
            replace="    package = _package(catalog, work_package)\n",
            label="wp_order.py:wp_order_new_cmd a lost order record takes a new order",
        ),
        Mutation(
            find='    to_state = str(fields["to_state"])\n    _booked_lost(catalog, ledger)\n',
            replace='    to_state = str(fields["to_state"])\n',
            label="wp_order.py:wp_order_transition_cmd a lost order record takes a move",
        ),
        Mutation(
            find="    _booked_lost(catalog, ledger)\n    order = _order(catalog, order_id)\n",
            replace="    order = _order(catalog, order_id)\n",
            label="wp_order.py:wp_order_accept_cmd a lost order record takes an accept",
        ),
        Mutation(
            find=(
                "    _booked_lost(catalog, ledger)\n"
                '    order = _order(catalog, str(fields["order"]))\n'
                '    if refusal := order_move_refusal(ledger, order, "closed"):'
            ),
            replace=(
                '    order = _order(catalog, str(fields["order"]))\n'
                '    if refusal := order_move_refusal(ledger, order, "closed"):'
            ),
            label="wp_order.py:wp_order_close_cmd a lost order record takes a close",
        ),
        Mutation(
            find="        *([refusal] if refusal else []),\n",
            replace="        *([]),\n",
            label="wp_order.py:wp_order_accept_cmd the round bound's refusal is dropped",
        ),
        Mutation(
            find="    if state == _OPEN:\n        return None\n",
            replace="    if True:\n        return None\n",
            label="wp_order.py:open_package_refusal a package not initiated takes an order",
        ),
    ),
    "src/gzkit/work_package_ledger.py": (
        Mutation(
            find="    return bool(_seals(ledger, work_package))\n",
            replace="    return False\n",
            label="work_package_ledger.py:footprint_sealed no freeze seals the footprint",
        ),
        Mutation(
            find="    if not frozen:\n        return package.modules\n",
            replace="    if True:\n        return package.modules\n",
            label=(
                "work_package_ledger.py:declared_modules the store, not the seal, is the footprint"
            ),
        ),
        Mutation(
            find='        if row.ts > seal.ts and row.extra.get("rung") == "change_order"\n',
            replace="        if False\n",
            label="work_package_ledger.py:declared_modules a change order adds nothing to the seal",
        ),
        Mutation(
            find='    if package.kind == "repair":\n        _check_repair_close(',
            replace="    if False:\n        _check_repair_close(",
            label="work_package_ledger.py:_check_closed a repair close skips its order checks",
        ),
    ),
    "src/gzkit/work_package_fence.py": (
        Mutation(
            find='        return (FencedPackage(work_package=_UNREADABLE, reason="unreadable"),)\n',
            replace="        return ()\n",
            label="work_package_fence.py:fenced_packages an unreadable ledger fences nothing",
        ),
        Mutation(
            find='        if state == "closed":\n            continue\n',
            replace="        if False:\n            continue\n",
            label="work_package_fence.py:_read_fence a closed package is read for the fence",
        ),
        Mutation(
            find='        if is_blocked(ledger, work_package):\n            reason = "blocked"\n',
            replace='        if False:\n            reason = "blocked"\n',
            label="work_package_fence.py:_read_fence a blocked package holds no fence",
        ),
        Mutation(
            find=(
                '        elif state == "accepted":\n'
                '            reason = "accepted"\n'
                "        elif took_stopping_exit"
            ),
            replace=(
                "        elif False:\n"
                '            reason = "accepted"\n'
                "        elif took_stopping_exit"
            ),
            label="work_package_fence.py:_read_fence an accepted package holds no fence",
        ),
        Mutation(
            find="        elif took_stopping_exit(ledger, work_package):\n",
            replace="        elif False:\n",
            label="work_package_fence.py:_read_fence a stopped package holds no fence",
        ),
        Mutation(
            find="        if state not in _ORDER_FENCEABLE:\n            continue\n",
            replace="        if True:\n            continue\n",
            label="work_package_fence.py:_read_order_fence no order holds the fence",
        ),
        Mutation(
            find='        if is_order_blocked(ledger, order):\n            reason = "blocked"\n',
            replace='        if False:\n            reason = "blocked"\n',
            label="work_package_fence.py:_read_order_fence a blocked order holds no fence",
        ),
        Mutation(
            find='        elif state == "accepted":\n            reason = "accepted"\n'
            "        elif order_took_stopping_exit",
            replace='        elif False:\n            reason = "accepted"\n'
            "        elif order_took_stopping_exit",
            label="work_package_fence.py:_read_order_fence an accepted order holds no fence",
        ),
        Mutation(
            find="        elif order_took_stopping_exit(ledger, order):\n",
            replace="        elif False:\n",
            label="work_package_fence.py:_read_order_fence a stopped order holds no fence",
        ),
    ),
    "src/gzkit/commands/wp.py": (
        Mutation(
            find="    if move.dropped and footprint_sealed(ledger, held.id):\n",
            replace="    if False:\n",
            label="wp.py:_with_modules a change order drops a sealed path",
        ),
        Mutation(
            find='            *([str(fields["order"])] if fields.get("order") else []),\n',
            replace="            *([]),\n",
            label="wp.py:wp_dispatch_cmd an order's round bound is not read at dispatch",
        ),
    ),
    "src/gzkit/acceptance_package.py": (
        Mutation(
            find='    if order is None:\n        msg = f"Order {order_id!r} is not in',
            replace='    if False:\n        msg = f"Order {order_id!r} is not in',
            label="acceptance_package.py:order_contract an unknown order takes a contract",
        ),
        Mutation(
            find='    if state not in _ACCEPTABLE_STATES:\n        msg = f"Order {order.id}',
            replace='    if False:\n        msg = f"Order {order.id}',
            label="acceptance_package.py:order_contract an order not commenced takes a contract",
        ),
        Mutation(
            find='    if not requirements:\n        msg = f"Order {order.id} holds',
            replace='    if False:\n        msg = f"Order {order.id} holds',
            label="acceptance_package.py:order_contract an order owing nothing takes a contract",
        ),
    ),
    "src/gzkit/acceptance_store.py": (
        Mutation(
            find="    if brief is None:\n        raise NoCanonicalBriefError(obpi_id)\n",
            replace="    if False:\n        raise NoCanonicalBriefError(obpi_id)\n",
            label="acceptance_store.py:resolve_brief a missing brief takes a contract",
        ),
        Mutation(
            find="    if not departed:\n        return history\n",
            replace="    if True:\n        return history\n",
            label="acceptance_store.py:_without_departed a departure removes no proof",
        ),
        Mutation(
            find="        if not same:\n            raise AcceptanceAlreadyInitializedError\n",
            replace="        if False:\n            raise AcceptanceAlreadyInitializedError\n",
            label="acceptance_store.py:initialize a changed contract re-initializes",
        ),
        Mutation(
            find="        if refusal:\n            raise ValueError(refusal)\n",
            replace="        if False:\n            raise ValueError(refusal)\n",
            label=(
                "acceptance_store.py:record_human_review a run past its round bound takes a review"
            ),
        ),
        Mutation(
            find=(
                "    if refuted_rounds(root, work_package) < review_round_limit():\n"
                "        return None\n"
            ),
            replace="    if True:\n        return None\n",
            label="acceptance_store.py:round_bound_refusal a run past its rounds is not refused",
        ),
        Mutation(
            find="    if is_order_id(work_package):\n        package = order_work_package(",
            replace="    if False:\n        package = order_work_package(",
            label=(
                "acceptance_store.py:round_bound_refusal an order's block recovery names no order"
            ),
        ),
        Mutation(
            find="    if is_run_id(obpi_id):\n        try:\n            return run_contract(",
            replace="    if False:\n        try:\n            return run_contract(",
            label="acceptance_store.py:resolve_brief a run's contract is read as a brief's",
        ),
        Mutation(
            find="    if not is_run_id(obpi_id):\n        return history\n",
            replace="    if True:\n        return history\n",
            label="acceptance_store.py:_without_departed a run's departures are not read",
        ),
        Mutation(
            find="            is_run_id(obpi_id) and previous.author_id == contract.author_id\n",
            replace="            False and previous.author_id == contract.author_id\n",
            label="acceptance_store.py:initialize a run's departure loses its author exemption",
        ),
        Mutation(
            find="    if is_run_id(obpi_id):\n"
            "        refusal = round_bound_refusal(root, obpi_id)\n",
            replace="    if False:\n        refusal = round_bound_refusal(root, obpi_id)\n",
            label="acceptance_store.py:record_human_review a run's round bound is not read",
        ),
        Mutation(
            find="    if is_run_id(obpi_id):\n        owed -= departed_reqs(",
            replace="    if False:\n        owed -= departed_reqs(",
            label="acceptance_store.py:owed_ids a run owes what it departed",
        ),
    ),
    "src/gzkit/schemas/ledger.json": _SCHEMA_PROPERTY_MUTANTS + tuple(
        Mutation(
            find=_SCHEMA_INDENT + '"required": [\n'
            + ",\n".join(f'{_SCHEMA_INDENT}  "{field}"' for field in fields)
            + f"\n{_SCHEMA_INDENT}],\n",
            replace=_SCHEMA_INDENT + '"required": [],\n',
            label=f"ledger.json:order_transitioned {when} books without {fields[0]}",
        )
        for when, fields in (
            ("accepted", ("acceptance_ready",)),
            ("closed", ("decision", "attestor", "attestation_text")),
            ("proceed", ("residual_risk",)),
            ("redirect", ("superseded_by",)),
            ("pause", ("revisit_condition",)),
        )
    ),
    "src/gzkit/work_package_run.py": (
        Mutation(
            find="_package_order(catalog, package, request.order)",
            replace="next(o for o in catalog.orders if o.id == request.order)",
            label="work_package_run.py:_dispatch_subject another package's order takes a dispatch",
        ),
        Mutation(
            find=(
                "    _package_order(catalog, package, order)\n"
                "    state = order_state(ledger, order)\n"
            ),
            replace="    state = order_state(ledger, order)\n",
            label="work_package_run.py:_check_blockable another package's order takes a block",
        ),
        Mutation(
            find='            if held.get("order")\n',
            replace="            if False\n",
            label="work_package_run.py:open_unclaimed_dispatches an order's dispatch reads "
            "its package's state",
        ),
        Mutation(
            find="    orders = (order_run_position(catalog, ledger, order) for order in "
            "catalog.orders)\n",
            replace="    orders = ()\n",
            label="work_package_run.py:run_positions no order is read as a run in flight",
        ),
    ),
    "src/gzkit/governance/trust_audits/catalog.py": (
        Mutation(
            find="        if current is not None and current != path[-1]:\n            cycles.add(",
            replace="        if False:\n            cycles.add(",
            label="catalog.py:_supersession_cycles a supersession cycle is not named",
        ),
        Mutation(
            find="        for number in _repeated(numbers)\n",
            replace="        for number in []\n",
            label="catalog.py:order_breaches a repeated order number passes",
        ),
        Mutation(
            find='        if kind == "repair":\n            continue\n',
            replace="        if True:\n            continue\n",
            label="catalog.py:order_breaches an order outside a repair package is accepted",
        ),
    ),
}

#: Ruling 91: the broad pass's non-kills, each re-run against only the tests that assert
#: its refusal, named here by the label's prefix. A row the narrowed run still cannot
#: grade is disclosed in the record, its failing tests named.
NARROWED: dict[str, tuple[str, ...]] = {
    "order_ledger.py:_order:": (
        "tests.test_order_ledger.LifecycleTests.test_an_order_the_store_lacks_is_refused",
    ),
    "order_ledger.py:_check_alterations:": (
        "tests.test_order_ledger.AlterationApprovalTests.test_the_first_freeze_approves_every_planned_alteration",
        "tests.test_order_ledger.AlterationApprovalTests.test_a_later_freeze_approves_only_what_was_planned_since",
    ),
    "order_ledger.py:_check_decision_fields:": (
        "tests.test_order_ledger.GateFiveTests.test_each_decision_carries_its_own_field_and_refuses_the_others",
        "tests.test_order_ledger.GateFiveTests.test_a_blank_field_of_another_decision_is_refused_too",
    ),
    "order_ledger.py:_check_closed:451": (
        "tests.test_order_ledger.GateFiveTests.test_the_attestor_the_words_and_the_decision_are_required",
    ),
    "order_ledger.py:order_move_refusal:532": (
        "tests.test_order_ledger.LifecycleTests.test_a_skipped_or_backward_step_is_refused",
    ),
    "order_ledger.py:record_order_transition:568": (
        "tests.test_order_ledger.LifecycleTests.test_empty_evidence_is_refused",
    ),
    "order_ledger.py:record_order_transition:571": (
        "tests.test_order_ledger.LifecycleTests.test_a_skipped_or_backward_step_is_refused",
    ),
    "wp_order.py:wp_order_new_cmd:197": (
        "tests.commands.test_wp_order.OrderNewTests.test_a_store_broken_before_the_call_names_the_store_to_repair",
    ),
    "wp_order.py:wp_order_accept_cmd:358": (
        "tests.commands.test_wp_order_acceptance.TestTheOrdersGate.test_the_sealed_footprint_holds_a_ready_order",
        "tests.commands.test_wp_order_acceptance.TestTheOrdersGate.test_the_footprint_is_named_beside_another_blocker",
    ),
    "wp_order.py:wp_order_close_cmd:404": (
        "tests.commands.test_wp_order_acceptance.TestTheOrdersAcceptRefusal.test_a_commenced_order_is_refused_a_close_for_its_lifecycle_first",
    ),
    "catalog.py:_repair_req_breaches:147": (
        "tests.governance.test_catalog_repair_reqs.TestRepairReqStore.test_a_repair_req_held_on_its_repair_package_passes",
    ),
    "catalog.py:_repair_req_breaches:148": (
        "tests.commands.test_wp_req.ReqNewTests.test_a_delivery_package_takes_no_repair_req",
    ),
    "work_package_run.py:_package_order:351": (
        "tests.test_order_run.UnblockOnAnOrder.test_another_packages_blocked_order_is_refused",
    ),
    "work_package_run.py:record_work_package_unblock:855": (
        "tests.test_order_run.UnblockOnAnOrder.test_an_order_not_blocked_is_refused",
    ),
    "work_package_ledger.py:_check_baselined:269": (
        "tests.test_work_package_ledger.FreezeTests.test_the_baseline_holds_the_catalogs_revision_of_the_packages_own_outcome",
    ),
    "work_package_run.py:_dispatch_subject another": (
        "tests.test_order_run.DispatchOnAnOrder.test_another_packages_commenced_order_takes_no_dispatch",
    ),
    "acceptance_store.py:_without_departed a departure": (
        "tests.commands.test_wp_order_acceptance.TestTheOrdersDeparture.test_a_departed_req_leaves_the_orders_obligations_and_roster",
        "tests.commands.test_wp_acceptance.TestDeparture.test_a_finding_on_a_departed_req_leaves_a_review_of_both",
    ),
    "acceptance_store.py:_without_departed a run's": (
        "tests.commands.test_wp_order_acceptance.TestTheOrdersDeparture.test_a_departed_req_leaves_the_orders_obligations_and_roster",
        "tests.commands.test_wp_acceptance.TestDeparture.test_a_finding_on_a_departed_req_leaves_a_review_of_both",
    ),
    "work_package_run.py:run_positions ": (
        "tests.test_order_run.InFlightOnAnOrder.test_an_order_not_commenced_is_not_in_flight",
        "tests.commands.test_wp_order_run.OrderRunOutputContract.test_each_verb_names_the_order",
    ),
    "work_package_ledger.py:_check_closed a repair": (
        "tests.test_work_package_ledger.RepairLifecycleTests.test_a_package_with_no_closed_order_does_not_close",
        "tests.test_work_package_ledger.RepairLifecycleTests.test_a_repair_close_books_no_gate_5_decision_of_its_own",
    ),
    "acceptance_package.py:order_contract an unknown": (
        "tests.commands.test_wp_order_acceptance.TestTheOrdersContract.test_an_order_the_store_lacks_is_refused",
    ),
    "acceptance_store.py:resolve_brief a run's contract": (
        "tests.commands.test_wp_order_acceptance.TestAStoppedOrdersGateFive.test_a_stopped_order_whose_acceptance_reads_ready_may_proceed",
        "tests.commands.test_wp_order_acceptance.TestAStoppedOrdersGateFive.test_readiness_earned_after_acceptance_earns_no_proceed",
    ),
    "work_package_ledger.py:_check_repair_close:351": (
        "tests.test_work_package_ledger.RepairLifecycleTests.test_the_close_waits_for_every_order_and_records_their_decisions",
    ),
}


#: Survivors of the twelve modules whose refusal a test outside them asserts: each is
#: re-run against that test alone, and the record keeps the two outcomes apart.
OUTSIDE: dict[str, tuple[str, ...]] = {
    "work_package_run.py:_dispatch_subject:389": (
        "tests.test_work_package_run.Dispatch.test_work_before_commencement_is_refused",
    ),
    "work_package_run.py:_dispatch_subject:391": (
        "tests.test_work_package_run.Dispatch.test_a_dispatch_names_one_held_subject",
    ),
    "work_package_run.py:_dispatch_subject:394": (
        "tests.test_work_package_run.Dispatch.test_a_dispatch_names_one_held_subject",
    ),
    "work_package_run.py:record_work_package_dispatch:486": (
        "tests.test_work_package_run.Dispatch.test_a_blocked_package_takes_no_dispatch_on_any_subject",
    ),
    "work_package_run.py:_check_blockable:766": (
        "tests.test_work_package_run.Block.test_a_closed_package_takes_no_block",
        "tests.test_work_package_run.Block.test_an_accepted_package_takes_no_block",
    ),
    "work_package_run.py:_check_blockable:771": (
        "tests.test_work_package_run.Block.test_a_second_block_while_blocked_is_refused",
    ),
    "work_package_run.py:record_work_package_unblock:857": (
        "tests.test_work_package_run.Unblock.test_an_empty_ruling_is_refused",
    ),
    "work_package_run.py:record_work_package_unblock:865": (
        "tests.test_work_package_run.AcrossPackages.test_reopen_is_once_per_requirement_across_packages",
    ),
    "work_package_ledger.py:declared_modules a change order": (
        "tests.commands.test_wp_airlock.TestAccept.test_the_order_that_adds_a_path_lets_the_package_be_accepted",
    ),
    "work_package_fence.py:fenced_packages an unreadable": (
        "tests.commands.test_wp_fence.TestWhoIsFenced.test_an_unreadable_ledger_fences_the_tree",
    ),
    "work_package_fence.py:_read_fence a blocked": (
        "tests.commands.test_wp_fence.TestTheCommitGuard.test_a_blocked_package_refuses_a_production_commit",
    ),
    "work_package_fence.py:_read_fence an accepted": (
        "tests.commands.test_wp_fence.TestTheCommitGuard.test_an_accepted_package_refuses_a_production_commit",
    ),
    "work_package_fence.py:_read_fence a stopped": (
        "tests.commands.test_wp_fence.TestTheExits.test_terminate_fences_until_the_package_closes",
    ),
    "acceptance_store.py:initialize a changed": (
        "tests.test_acceptance_store.AcceptanceStoreTests.test_reinitialization_cannot_erase_prior_history",
    ),
    "acceptance_store.py:record_human_review:604": (
        "tests.test_acceptance_store.AcceptanceStoreTests.test_a_human_review_closes_each_open_finding_its_current_proof_answers",
    ),
    "acceptance_store.py:resolve_brief a missing": (
        "tests.test_acceptance_store.AcceptanceStoreTests.test_an_obpi_with_no_canonical_brief_is_refused",
    ),
}


def _refuses(body: list[ast.stmt]) -> bool:
    """Report whether a statement directly in *body* refuses."""
    for stmt in body:
        node: ast.expr | None = None
        if isinstance(stmt, (ast.Expr, ast.Return)):
            node = stmt.value
        elif isinstance(stmt, ast.Raise):
            node = stmt.exc
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if name in REFUSERS or name in {"append", "extend"}:
                return True
        if isinstance(stmt, ast.Return) and isinstance(node, (ast.JoinedStr, ast.Constant)):
            return bool(getattr(node, "value", True))
        if isinstance(stmt, ast.Return) and isinstance(node, ast.List) and node.elts:
            return True
        if isinstance(stmt, ast.AugAssign) and getattr(stmt.target, "id", "") == "breaches":
            return True
    return False


def _lines(source: str) -> list[str]:
    return source.splitlines(keepends=True)


def _unique_find(source: str, start: int, end: int) -> str | None:
    """Return the text from line *start* to *end*, widened downward until unique."""
    lines = _lines(source)
    stop = end
    while stop <= len(lines):
        text = "".join(lines[start - 1 : stop])
        if source.count(text) == 1:
            return text
        stop += 1
    return None


def mutants(path: Path, functions: tuple[str, ...] | None) -> list[Mutation]:
    """One ``False`` mutant per refusing guard in *functions* of *path*.

    A comprehension filter is a guard only in the catalog audit, whose comprehensions
    collect breach sentences; elsewhere a filter selects ledger rows and refuses nothing.
    """
    if functions == ():
        return []
    breach_lists = path.name == "catalog.py"
    source = path.read_text(encoding="utf-8")
    found: list[Mutation] = []
    for func in ast.walk(ast.parse(source)):
        if not isinstance(func, ast.FunctionDef):
            continue
        if functions is not None and func.name not in functions:
            continue
        for node in ast.walk(func):
            test: ast.expr | None = None
            if isinstance(node, ast.If) and _refuses(node.body):
                test = node.test
            elif breach_lists and isinstance(node, ast.comprehension) and node.ifs:
                test = node.ifs[-1]
            if test is None or test.lineno is None or test.end_lineno is None:
                continue
            find = _unique_find(source, test.lineno, test.end_lineno)
            segment = ast.get_source_segment(source, test)
            if find is None or segment is None or segment not in find:
                continue
            replace = find.replace(segment, "False", 1)
            label = f"{path.name}:{func.name}:{test.lineno} {segment.splitlines()[0][:70]}"
            found.append(Mutation(find=find, replace=replace, label=label))
    return found


def _copy(root: Path) -> None:
    """Copy what O2's tests read into *root*, leaving bytecode behind."""
    names = ("src", "tests", "data", ".gzkit", "docs", ".claude", "pyproject.toml", ".gzkit.json")
    for name in names:
        source = REPO / name
        if source.is_dir():
            shutil.copytree(source, root / name, ignore=shutil.ignore_patterns("__pycache__"))
        elif source.exists():
            shutil.copy2(source, root / name)


def _sweep_entry(relative: str, sweep: MutationSweep) -> dict[str, object]:
    """Return one broad sweep as a record entry."""
    return {
        "source": relative,
        "baseline_green": sweep.baseline_green,
        "baseline_tests_run": sweep.baseline_tests_run,
        "source_restored": sweep.source_sha256 == sweep.restored_source_sha256,
        "conclusive": sweep.is_conclusive,
        "counts": {
            "killed": sweep.killed,
            "survived": sweep.survived,
            "invalid": sweep.invalid,
            "inconclusive": sweep.inconclusive,
        },
        "mutants": [
            {
                "label": w.label,
                "outcome": w.outcome,
                "reason": w.reason,
                "failure_class": w.failure_class,
                "failing_tests": w.failing_tests,
            }
            for w in sweep.witnesses
        ],
    }


def _narrowed(
    root: Path, relative: str, planned: list[Mutation], sweep: MutationSweep
) -> list[dict[str, object]]:
    """Re-run each non-kill against only the tests asserting its refusal (ruling 91).

    Returns:
        One record entry per re-run mutant.

    """
    entries: list[dict[str, object]] = []
    for witness in sweep.witnesses:
        if witness.outcome == "killed":
            continue
        table = OUTSIDE if witness.outcome == "survived" else NARROWED
        prefix = next((key for key in table if witness.label.startswith(key)), None)
        if prefix is None:
            continue
        mutation = next(m for m in planned if m.label == witness.label)
        tests = list(table[prefix])
        narrow = [sys.executable, "-c", BOOTSTRAP, "-v", *tests]
        rerun = run_mutation_sweep(
            root, root / relative, [mutation.model_copy(update={"expected_tests": tests})], narrow
        )
        w = rerun.witnesses[0]
        entries.append(
            {
                "source": relative,
                "label": w.label,
                "broad_outcome": witness.outcome,
                "tests": tests,
                "baseline_green": rerun.baseline_green,
                "outcome": w.outcome,
                "reason": w.reason,
                "failure_class": w.failure_class,
                "failing_tests": w.failing_tests,
                "errors": [line for line in w.output_tail.splitlines() if "Error" in line][-4:],
            }
        )
        sys.stdout.write(f"  narrowed {w.outcome} {w.label}\n")
    return entries


def main(out: Path) -> int:
    """Run the broad sweep and the narrowed re-runs, and write the record to *out*.

    Returns:
        Zero once the record is written.

    """
    command = [sys.executable, "-c", BOOTSTRAP, "-v", *MODULES]
    record: dict[str, list] = {"modules": list(MODULES), "sweeps": [], "narrowed": []}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _copy(root)
        for relative, functions in GUARDS.items():
            target = root / relative
            planned = [*mutants(target, functions), *MANUAL.get(relative, ())]
            probe = run_mutation_sweep(root, target, [], command)
            tests = probe.baseline_executed_tests
            nominated = [m.model_copy(update={"expected_tests": tests}) for m in planned]
            sweep = run_mutation_sweep(root, target, nominated, command)
            record["sweeps"].append(_sweep_entry(relative, sweep))
            counts = (sweep.killed, sweep.survived, sweep.invalid, sweep.inconclusive)
            sys.stdout.write(f"{relative} {counts}\n")
            record["narrowed"].extend(_narrowed(root, relative, planned, sweep))
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
