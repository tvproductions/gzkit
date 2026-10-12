"""BDD steps for the pipeline run position (OBPI-0.35.0-15, GHI #1172).

Two kinds of run are set up here. The launch-value and reader scenarios write
the markers and the launch event directly, because what they hold fixed is the
launch itself. The boundary scenarios launch a seeded project through
``gz obpi pipeline`` and cross every boundary through the command that marks
it, so a command that records the wrong stage, kind or label fails them. Where
a command judges evidence a seeded project does not hold, the work it computes
is replaced with the stand-ins the unit fixture uses; the command, the ledger
and the marker files are real.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
from collections.abc import Callable
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from behave import given, then, when
from tests.test_pipeline_position import (
    COMPLETE_ARGS,
    completion_gates_replaced,
    precomplete_checks_replaced,
    seed_launchable_obpi,
    stage4_work_replaced,
    verification_replaced,
    write_review_receipt,
    write_stage4_packet,
)

from gzkit import obpi_dispatch_channel as chan
from gzkit.cli import main
from gzkit.ledger import (
    Ledger,
    pipeline_launched_event,
    pipeline_stage_transition_event,
)
from gzkit.pipeline_runtime import (
    STALE_MARKER_HOURS,
    advance_pipeline_markers,
    load_dispatch_state,
    pipeline_marker_paths,
    pipeline_marker_payload,
    pipeline_resume_command,
    pipeline_stage_output,
    replay_pipeline_position,
    write_pipeline_markers,
)
from gzkit.pipeline_stage_fence import marker_stage, refuses_production_write

_OBPI = "OBPI-0.99.0-01-run-position-demo"
_ADR = "ADR-0.99.0-run-position-demo"
_BOUNDARY = "gz obpi pipeline"
_UNCHANGED_KEYS = ("nonce", "started_at", "entry", "receipt_state")

_CLI_OBPI = "OBPI-0.13.0-01-runtime-command-contract"
_CLI_SHORT_OBPI = "OBPI-0.13.0-01"
_CLI_REQ = "REQ-0.13.0-01-01"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ledger(context) -> Ledger:
    return Ledger(context.run_root / ".gzkit" / "ledger.jsonl")


@given('a pipeline run launched with entry "{entry}"')
def step_launch_run(context, entry: str) -> None:
    """Write both markers and the launch event, in the order the launcher does."""
    tmp = tempfile.TemporaryDirectory()
    context.add_cleanup(tmp.cleanup)
    context.run_root = Path(tmp.name)
    context.run_plans = context.run_root / ".claude" / "plans"
    (context.run_root / ".gzkit").mkdir(parents=True)
    (context.run_root / ".gzkit" / "ledger.jsonl").touch()

    start_from = None if entry == "full" else entry
    payload = pipeline_marker_payload(
        _OBPI, _ADR, "heavy", start_from, "pass", requires_human_attestation=True
    )
    per_obpi, _legacy = write_pipeline_markers(context.run_plans, payload)
    _ledger(context).append(
        pipeline_launched_event(
            obpi_id=_OBPI,
            parent_adr=_ADR,
            lane="heavy",
            nonce=str(payload["nonce"]),
            marker_path=per_obpi.relative_to(context.run_root).as_posix(),
            entry=str(payload["entry"]),
        )
    )
    context.run_markers = pipeline_marker_paths(context.run_plans, _OBPI)
    context.run_obpi = _OBPI
    context.launch_payload = payload


@given("the run has recorded a Stage 2 dispatch")
def step_record_dispatch(context) -> None:
    chan.record_dispatch(context.run_root, _OBPI, role="Implementer", model="sonnet", task_id=1)
    context.dispatched_before = load_dispatch_state(context.run_plans, _OBPI)
    assert len(context.dispatched_before) == 1, context.dispatched_before


@when("both marker files are deleted")
def step_delete_markers(context) -> None:
    for marker_path in context.run_markers:
        marker_path.unlink()


@when("the launch markers and the ledger replay are read")
def step_read_launch(context) -> None:
    per_obpi, legacy = context.run_markers
    context.marker = _read(per_obpi)
    context.legacy_marker = _read(legacy)
    context.replay = replay_pipeline_position(_ledger(context).read_all(), _OBPI)


@when('the run records a crossing into "{stage}" at phase "{label}"')
def step_cross_boundary(context, stage: str, label: str) -> None:
    """Ledger first, marker second: the marker takes the event's own time."""
    ledger = _ledger(context)
    ledger.append(
        pipeline_stage_transition_event(
            obpi_id=_OBPI,
            parent_adr=_ADR,
            stage=stage,
            position_kind="phase",
            position_label=label,
            boundary=_BOUNDARY,
        )
    )
    replay = replay_pipeline_position(Ledger(ledger.path).read_all(), _OBPI)
    assert replay is not None and replay.position is not None, replay
    advance_pipeline_markers(
        context.run_plans,
        _OBPI,
        stage=replay.stage,
        position=replay.position.model_dump(),
        updated_at=replay.updated_at,
        blockers=replay.blockers,
        requires_human_attestation=True,
    )
    context.stage_reached = stage
    context.crossed_at = replay.updated_at


@then('the marker entry is "{entry}" and its stage is "{stage}"')
def step_entry_and_stage(context, entry: str, stage: str) -> None:
    for marker in (context.marker, context.legacy_marker):
        assert marker["entry"] == entry, marker
        assert marker["current_stage"] == stage, marker
    assert context.replay is not None, "the launch is on the ledger to be replayed"
    assert context.replay.stage == stage, context.replay


@then('the marker resume point is "{resume_point}"')
def step_resume_point(context, resume_point: str) -> None:
    expected = None if resume_point == "none" else resume_point
    assert context.marker["resume_point"] == expected, context.marker


@then('the marker carries no blockers and its required human action is "{human_action}"')
def step_blockers_and_human_action(context, human_action: str) -> None:
    """``none`` is no action; any other value is a word the action names."""
    for marker in (context.marker, context.legacy_marker):
        assert marker["blockers"] == [], marker
        required = marker["required_human_action"]
        if human_action == "none":
            assert required is None, marker
        else:
            assert required is not None and human_action in required, marker


@then("neither the marker nor the ledger replay reports a position")
def step_no_position(context) -> None:
    assert "position" not in context.marker, context.marker
    assert "position" not in context.legacy_marker, context.legacy_marker
    assert context.replay.position is None, context.replay


@then('the fence reads stage "{stage}" from both marker files')
def step_fence_reads_stage(context, stage: str) -> None:
    for marker_path in context.run_markers:
        reached = marker_stage(marker_path)
        assert reached == stage, f"{marker_path.name}: {reached}"


@then("the fence refuses a production write at the stage reached")
def step_fence_refuses_write(context) -> None:
    for marker_path in context.run_markers:
        assert refuses_production_write(marker_stage(marker_path), "src/gzkit/example.py"), (
            f"{marker_path.name} did not arm the post-Stage-2 fence"
        )


@then("the resume command is the one the stage reached prescribes")
def step_resume_command(context) -> None:
    marker = _read(context.run_markers[0])
    expected = pipeline_stage_output(_OBPI, context.stage_reached, requires_human_attestation=True)[
        "next_command"
    ]
    actual = pipeline_resume_command(marker)
    assert actual == expected, f"expected {expected!r}, got {actual!r}"
    assert actual != context.launch_payload["next_command"], actual
    assert marker["updated_at"] == context.crossed_at, marker


@then("the recorded dispatch is still read from the marker")
def step_dispatch_still_read(context) -> None:
    after = load_dispatch_state(context.run_plans, _OBPI)
    assert after == context.dispatched_before, after


@then("the launch nonce, start time, entry and receipt state are unchanged")
def step_launch_keys_unchanged(context) -> None:
    for marker_path in context.run_markers:
        marker = _read(marker_path)
        for key in _UNCHANGED_KEYS:
            assert marker[key] == context.launch_payload[key], f"{marker_path.name}: {key}"


@then("both marker files hold the same bytes")
def step_same_bytes(context) -> None:
    per_obpi, legacy = context.run_markers
    assert per_obpi.read_bytes() == legacy.read_bytes(), "the two marker files diverged"


def _transitions(context) -> list[dict[str, Any]]:
    return [
        row.extra
        for row in _ledger(context).read_all()
        if row.event == "pipeline_stage_transition" and row.id == context.run_obpi
    ]


@then('both marker files read stage "{stage}" and not the launch stage')
def step_reads_stage_reached(context, stage: str) -> None:
    launch_stage = context.launch_payload["current_stage"]
    assert stage != launch_stage, "the example must leave the launch stage to prove anything"
    for marker_path in context.run_markers:
        reached = _read(marker_path)["current_stage"]
        assert reached == stage, f"{marker_path.name}: {reached}"
        assert reached != launch_stage, f"{marker_path.name} still reads the launch stage"


@then("the marker was updated later than the run started")
def step_updated_after_start(context) -> None:
    for marker_path in context.run_markers:
        marker = _read(marker_path)
        started_at = datetime.fromisoformat(marker["started_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(marker["updated_at"].replace("Z", "+00:00"))
        assert updated_at > started_at, f"{marker_path.name}: {updated_at} <= {started_at}"


@then("the ledger holds {count:d} stage transition for the run")
@then("the ledger holds {count:d} stage transitions for the run")
def step_transition_count(context, count: int) -> None:
    transitions = _transitions(context)
    assert len(transitions) == count, transitions


@then('the ledger says the run has reached stage "{stage}"')
def step_ledger_stage(context, stage: str) -> None:
    """What an in-place boundary decides from: the ledger, with no marker to read."""
    reached = replay_pipeline_position(_ledger(context).read_all(), context.run_obpi)
    assert reached is not None and reached.stage == stage, reached
    assert not any(path.exists() for path in context.run_markers), "the read rebuilt a marker"


# ---------------------------------------------------------------------------
# A run driven through the real commands
# ---------------------------------------------------------------------------


def _gz(context, *args: str, exit_code: int = 0) -> str:
    """Run one ``gz`` command in the scenario's project and assert its exit code."""
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(list(args))
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
    code = 0 if code is None else int(code)
    assert code == exit_code, f"gz {' '.join(args)} exited {code}: {output.getvalue()}"
    return output.getvalue()


def _task_rows(context, event: str) -> list[str]:
    return [row.extra["task_id"] for row in _ledger(context).read_all() if row.event == event]


def _fail_verification(context) -> None:
    with verification_replaced(failing=True):
        _gz(context, "obpi", "pipeline", _CLI_OBPI, "--from=verify", exit_code=1)


def _pass_verification(context) -> None:
    with verification_replaced():
        _gz(context, "obpi", "pipeline", _CLI_OBPI, "--from=verify")


def _enter_ceremony(context) -> None:
    with verification_replaced():
        _gz(context, "obpi", "pipeline", _CLI_OBPI, "--from=ceremony")


def _complete(context) -> None:
    with completion_gates_replaced():
        _gz(context, *COMPLETE_ARGS)


def _complete_with_a_failed_write(context) -> None:
    """Reach ``sync`` and stay in flight: the completion rolls back before its receipt."""
    with completion_gates_replaced(failing_write=True):
        _gz(context, *COMPLETE_ARGS, exit_code=2)


def _present_evidence(context) -> None:
    with stage4_work_replaced():
        _gz(context, "obpi", "present-evidence", _CLI_OBPI, "--json")


def _verify_packet(context) -> None:
    with stage4_work_replaced():
        _gz(context, "obpi", "verify-packet", write_stage4_packet(_CLI_OBPI), "--json")


def _import_adversarial_review(context) -> None:
    receipt = write_review_receipt()
    with stage4_work_replaced(review_stage="adversarial"):
        _gz(context, "obpi", "acceptance", _CLI_OBPI, "review", "--receipt", receipt)


def _import_human_review(context) -> None:
    human_review = ("human-review", "--attestor", "g0", "--ruling", "accepted as shown")
    with stage4_work_replaced():
        _gz(context, "obpi", "acceptance", _CLI_OBPI, *human_review)


def _precomplete(context, obpi_id: str = _CLI_OBPI) -> None:
    with precomplete_checks_replaced():
        _gz(context, "obpi", "precomplete", obpi_id, "--json")


def _start_task(context) -> None:
    _gz(context, "task", "start", "--req", _CLI_REQ, "--seq", "next")
    context.named_task = _task_rows(context, "task_started")[-1]


def _dispatch_task_2(context) -> None:
    dispatch = ("obpi", "dispatch", _CLI_OBPI, "--role", "Implementer", "--model", "sonnet")
    _gz(context, *dispatch, "--task", "2")


def _task_verb(verb: str, *extra: str) -> Callable[..., None]:
    """Return a crossing that runs ``gz task <verb>`` on a TASK the launch started."""

    def _cross(context) -> None:
        context.named_task = _task_rows(context, "task_started")[0]
        _gz(context, "task", verb, context.named_task, *extra)

    return _cross


#: How a run launched in full is brought to each stage, through its commands.
_REACH: dict[str, Callable[..., None]] = {
    "implement": lambda _context: None,
    "verify": _fail_verification,
    "ceremony": _pass_verification,
    "sync": _complete_with_a_failed_write,
}

#: Each boundary a scenario crosses, by the command line the feature names.
_BOUNDARIES: dict[str, Callable[..., None]] = {
    "gz obpi pipeline --from=verify with a failing command": _fail_verification,
    "gz obpi pipeline --from=verify with every command passing": _pass_verification,
    "gz obpi pipeline --from=ceremony": _enter_ceremony,
    "gz obpi present-evidence": _present_evidence,
    "gz obpi complete": _complete,
    "gz task start": _start_task,
    "gz obpi dispatch --task 2": _dispatch_task_2,
    "gz obpi precomplete": _precomplete,
    "gz obpi precomplete with the short id": lambda context: _precomplete(context, _CLI_SHORT_OBPI),
    "gz obpi verify-packet": _verify_packet,
    "gz obpi acceptance review": _import_adversarial_review,
    "gz obpi acceptance human-review": _import_human_review,
    "gz task complete": _task_verb("complete"),
    "gz task block": _task_verb("block", "--reason", "waits on a ruling"),
    "gz task escalate": _task_verb("escalate", "--reason", "needs a ruling"),
}


@given("a project whose run was launched in full through gz obpi pipeline")
def step_launch_through_the_command(context) -> None:
    """Seed the scenario's project and launch its OBPI with the real launcher."""
    context.run_root = Path.cwd()
    context.run_plans = context.run_root / ".claude" / "plans"
    context.run_markers = seed_launchable_obpi(with_reqs=True)
    context.run_obpi = _CLI_OBPI
    _gz(context, "obpi", "pipeline", _CLI_OBPI)
    context.launch_payload = _read(context.run_markers[0])
    assert context.launch_payload["entry"] == "full", context.launch_payload
    assert _transitions(context) == [], "a bare launch records no position"


@given('the run has reached stage "{stage}"')
def step_reach_stage(context, stage: str) -> None:
    _REACH[stage](context)
    for marker_path in context.run_markers:
        reached = _read(marker_path)["current_stage"]
        assert reached == stage, f"{marker_path.name}: {reached}"


@when('the run crosses the boundary "{boundary}"')
def step_cross_boundary_through_its_command(context, boundary: str) -> None:
    before = len(_transitions(context))
    _BOUNDARIES[boundary](context)
    context.appended = _transitions(context)[before:]


@then("the command appended {count:d} stage transitions")
def step_appended_count(context, count: int) -> None:
    assert len(context.appended) == count, context.appended


@then('the command recorded the "{kind}" "{label}" inside stage "{stage}"')
def step_command_recorded(context, kind: str, label: str, stage: str) -> None:
    """``TASK`` stands for the TASK id the command named."""
    expected = context.named_task if label == "TASK" else label
    matching = [row for row in context.appended if row["position_label"] == expected]
    assert len(matching) == 1, f"expected one {expected!r} crossing in {context.appended}"
    (recorded,) = matching
    assert recorded["stage"] == stage, recorded
    assert recorded["position_kind"] == kind, recorded


@then("both marker files name what the ledger last recorded")
def step_markers_name_last_crossing(context) -> None:
    recorded = _transitions(context)[-1]
    position = {
        "kind": recorded["position_kind"],
        "label": recorded["position_label"],
        "boundary": recorded["boundary"],
    }
    for marker_path in context.run_markers:
        marker = _read(marker_path)
        assert marker["current_stage"] == recorded["stage"], marker
        assert marker["position"] == position, marker
    per_obpi, legacy = context.run_markers
    assert per_obpi.read_bytes() == legacy.read_bytes(), "the two marker files diverged"


@then('the marker entry is still "{entry}" and its nonce is the launch\'s')
def step_launch_still_stands(context, entry: str) -> None:
    for marker_path in context.run_markers:
        marker = _read(marker_path)
        assert marker["entry"] == entry, marker
        assert marker["nonce"] == context.launch_payload["nonce"], marker
        assert marker["started_at"] == context.launch_payload["started_at"], marker


@then("the ledger holds {count:d} launch for the run")
def step_launch_count(context, count: int) -> None:
    launches = [
        row
        for row in _ledger(context).read_all()
        if row.event == "pipeline_launched" and row.id == context.run_obpi
    ]
    assert len(launches) == count, launches


# ---------------------------------------------------------------------------
# The session orientation's reading of a run
# ---------------------------------------------------------------------------

_ORIENTATION_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "session_orientation.py"


def _orientation_module() -> Any:
    """Load the session-orientation script, which lives outside the package."""
    spec = importlib.util.spec_from_file_location("session_orientation", _ORIENTATION_SCRIPT)
    assert spec is not None and spec.loader is not None, f"cannot load {_ORIENTATION_SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_orientation"] = module
    spec.loader.exec_module(module)
    return module


@when("the session orientation is collected")
def step_collect_orientation(context) -> None:
    """Collect the runs and render the section a new process is shown."""
    orientation = _orientation_module()
    context.orientation_runs = orientation.collect_adr_pipeline(context.run_root)
    rendered = orientation.render({"adr_pipeline": context.orientation_runs}, datetime.now(UTC))
    section = rendered.split("## Active ADR pipeline state", 1)[1].split("\n## ", 1)[0]
    context.orientation_section = section.splitlines()


def _oriented_run(context) -> dict[str, Any]:
    named = [run for run in context.orientation_runs if run["obpi_id"] == context.run_obpi]
    assert len(named) == 1, context.orientation_runs
    return named[0]


@then('the orientation reports the run at stage "{stage}" with a "{kind}" position')
def step_orientation_stage_and_kind(context, stage: str, kind: str) -> None:
    run = _oriented_run(context)
    launch_stage = context.launch_payload["current_stage"]
    assert stage != launch_stage, "the example must leave the launch stage to prove anything"
    assert run["stage"] == stage, run
    assert run["position"] is not None, run
    assert run["position"]["kind"] == kind, run


@then("the orientation position is the last boundary the ledger recorded")
def step_orientation_position_is_the_ledgers(context) -> None:
    recorded = _transitions(context)[-1]
    position = _oriented_run(context)["position"]
    expected = {
        "kind": recorded["position_kind"],
        "label": recorded["position_label"],
        "boundary": recorded["boundary"],
    }
    assert position == expected, (position, expected)


@then('the orientation section names stage "{stage}" and that position, not the launch stage')
def step_orientation_section(context, stage: str) -> None:
    launch_stage = context.launch_payload["current_stage"]
    position = _oriented_run(context)["position"]
    lines = context.orientation_section
    named = [index for index, line in enumerate(lines) if line.startswith(f"- {context.run_obpi}")]
    assert len(named) == 1, lines
    headline = lines[named[0]]
    assert stage in headline, headline
    assert launch_stage not in headline, headline
    under = []
    for line in lines[named[0] + 1 :]:
        if not line.startswith("  "):
            break
        under.append(line)
    positioned = [line for line in under if position["kind"] in line and position["label"] in line]
    assert len(positioned) == 1, under
    assert launch_stage not in positioned[0], positioned


# ---------------------------------------------------------------------------
# A marker rebuilt by gz state --repair
# ---------------------------------------------------------------------------


def _run_rows(context, event: str) -> list[Any]:
    return [
        row
        for row in _ledger(context).read_all()
        if row.event == event and row.id == context.run_obpi
    ]


def _rebuilt_markers(context) -> list[dict[str, Any]]:
    """Return both marker files, each of which the repair must have written."""
    for marker_path in context.run_markers:
        assert marker_path.is_file(), f"{marker_path.name} was not rebuilt"
    return [_read(marker_path) for marker_path in context.run_markers]


@given("every ledger event of the run is older than the stale bound")
def step_age_the_run(context) -> None:
    """Rewrite the scenario project's own ledger so the run was abandoned long ago."""
    ledger_path = context.run_root / ".gzkit" / "ledger.jsonl"
    assert not (context.run_root / "pyproject.toml").exists(), "never a real repository's ledger"
    long_ago = (datetime.now(UTC) - timedelta(hours=STALE_MARKER_HOURS + 1)).isoformat()
    aged: list[str] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("id") == context.run_obpi and row.get("event") in (
            "pipeline_launched",
            "pipeline_stage_transition",
        ):
            row["ts"] = long_ago
        aged.append(json.dumps(row))
    ledger_path.write_text("\n".join(aged) + "\n", encoding="utf-8")
    context.aged_to = long_ago


@when("gz state --repair is run")
def step_repair(context) -> None:
    context.markers_before = [
        marker_path.read_bytes() if marker_path.exists() else None
        for marker_path in context.run_markers
    ]
    printed = _gz(context, "state", "--repair", "--json")
    report, _end = json.JSONDecoder().raw_decode(printed[printed.index("{") :])
    context.repair = report["markers"]


@when("gz obpi pipeline --clear-stale is run")
def step_clear_stale(context) -> None:
    _gz(context, "obpi", "pipeline", "--clear-stale")


@then('the repair reports the run rebuilt at stage "{stage}"')
def step_reported_rebuilt(context, stage: str) -> None:
    assert context.repair["declined"] == [], context.repair
    assert len(context.repair["rebuilt"]) == 1, context.repair
    (rebuilt,) = context.repair["rebuilt"]
    assert rebuilt["obpi_id"] == context.run_obpi, rebuilt
    assert rebuilt["current_stage"] == stage, rebuilt


@then("the rebuilt marker carries the time of the last recorded crossing")
def step_rebuilt_time_of_last_crossing(context) -> None:
    last = _run_rows(context, "pipeline_stage_transition")[-1]
    for marker in _rebuilt_markers(context):
        assert marker["updated_at"] == last.ts, (marker["updated_at"], last.ts)


@then("the rebuilt marker carries the time of the launch event")
def step_rebuilt_time_of_launch(context) -> None:
    launch = _run_rows(context, "pipeline_launched")[-1]
    for marker in _rebuilt_markers(context):
        assert marker["updated_at"] == launch.ts, (marker["updated_at"], launch.ts)
        assert marker["started_at"] == launch.ts, (marker["started_at"], launch.ts)


@then("the rebuilt marker carries the nonce and the entry the launch event recorded")
def step_rebuilt_nonce(context) -> None:
    """The run is its latest launch: a ``--from`` re-entry is a launch with its own nonce."""
    launch = _run_rows(context, "pipeline_launched")[-1]
    for marker in _rebuilt_markers(context):
        assert marker["nonce"] == launch.extra["nonce"], marker
        assert marker["entry"] == launch.extra["entry"], marker
    per_obpi, legacy = context.run_markers
    assert per_obpi.read_bytes() == legacy.read_bytes(), "the two marker files diverged"


@then('both rebuilt marker files read stage "{stage}" and no position')
def step_rebuilt_launch_values(context, stage: str) -> None:
    for marker in _rebuilt_markers(context):
        assert marker["current_stage"] == stage, marker
        assert "position" not in marker, marker
        for key in ("blockers", "required_human_action", "resume_point"):
            assert marker[key] == context.launch_payload[key], (key, marker)


@then("both marker files are byte for byte what they were before the repair")
def step_markers_untouched(context) -> None:
    after = [marker_path.read_bytes() for marker_path in context.run_markers]
    assert None not in context.markers_before, "the scenario needs both markers on disk"
    assert after == context.markers_before, "the repair moved a marker that was on disk"


@then("the repair reports nothing rebuilt and nothing declined")
def step_nothing_reported(context) -> None:
    assert context.repair == {"rebuilt": [], "restored": [], "declined": []}, context.repair


@when("the legacy marker file is deleted")
def step_delete_legacy_marker(context) -> None:
    _per_obpi, legacy = context.run_markers
    legacy.unlink()


@then("the per-OBPI marker file is byte for byte what it was before the repair")
def step_per_obpi_untouched(context) -> None:
    per_obpi, _legacy = context.run_markers
    assert context.markers_before[0] is not None, "the scenario needs the per-OBPI marker on disk"
    assert per_obpi.read_bytes() == context.markers_before[0], "the repair moved the file on disk"


@then("the repair reports the legacy marker file restored and nothing rebuilt or declined")
def step_reported_restored(context) -> None:
    per_obpi, legacy = context.run_markers
    assert context.markers_before[1] is None, "the scenario needs the legacy marker deleted"
    assert context.repair["rebuilt"] == [], context.repair
    assert context.repair["declined"] == [], context.repair
    expected = {"obpi_id": context.run_obpi, "file": legacy.name, "copied_from": per_obpi.name}
    assert context.repair["restored"] == [expected], context.repair


@then("no marker file is on disk")
def step_no_marker(context) -> None:
    left = sorted(path.name for path in context.run_plans.glob(".pipeline-active*.json"))
    assert left == [], left


@then("the repair declines the run and says why")
def step_declined(context) -> None:
    assert context.repair["rebuilt"] == [], context.repair
    assert len(context.repair["declined"]) == 1, context.repair
    (declined,) = context.repair["declined"]
    assert declined["obpi_id"] == context.run_obpi, declined
    assert context.aged_to in declined["reason"], declined
