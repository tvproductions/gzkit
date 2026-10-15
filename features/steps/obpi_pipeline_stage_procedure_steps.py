"""BDD steps for the served stage procedures (OBPI-0.35.0-17, cut over in OBPI-0.35.0-20).

Every scenario launches a seeded project through the real ``gz obpi pipeline``
and reads the pointers the launch prints. Where an entry runs stage work a
seeded project cannot hold (the verification commands, the Stage 2 acceptance
check), that work is replaced with the stand-ins the unit fixture uses; the
launcher, the resolver and the files it serves are real.
"""

from __future__ import annotations

import hashlib
import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then, when
from tests.test_pipeline_position import seed_launchable_obpi, verification_replaced

from gzkit.cli import main
from gzkit.pipeline_procedure import REFERENCES_DIR, STAGE_PROCEDURES

_CLI_OBPI = "OBPI-0.13.0-01-runtime-command-contract"


def _gz(*args: str, exit_code: int = 0) -> str:
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


def _procedure(number: str):
    return next(p for p in STAGE_PROCEDURES if p.number == int(number))


def _flat(context) -> str:
    """The console wraps long lines; a pointer is one line of text."""
    return " ".join(context.output.split())


@given("a project seeded so its OBPI can be launched")
def step_seed(context) -> None:
    context.run_root = Path.cwd()
    context.run_markers = seed_launchable_obpi()
    context.run_obpi = _CLI_OBPI


@given("the served procedure for stage {number:d} is missing")
def step_remove_procedure(context, number: int) -> None:
    path = Path.cwd() / REFERENCES_DIR / _procedure(str(number)).filename
    path.unlink()
    context.disturbed = path


@given("the served procedure for stage {number:d} has been altered")
def step_alter_procedure(context, number: int) -> None:
    path = Path.cwd() / REFERENCES_DIR / _procedure(str(number)).filename
    path.write_text(path.read_text(encoding="utf-8") + "\nextra line\n", encoding="utf-8")
    context.disturbed = path
    context.found_digest = hashlib.sha256(path.read_bytes()).hexdigest()


@when("the pipeline is launched in full")
def step_launch_full(context) -> None:
    context.output = _gz("obpi", "pipeline", _CLI_OBPI)


@when("the pipeline is launched in full and exits {code:d}")
def step_launch_full_refused(context, code: int) -> None:
    context.output = _gz("obpi", "pipeline", _CLI_OBPI, exit_code=code)


@when('the pipeline is launched with "{flag}" and its stage work stood in for')
def step_launch_from(context, flag: str) -> None:
    with verification_replaced():
        context.output = _gz("obpi", "pipeline", _CLI_OBPI, flag)


@then('the launch output serves the procedures for stages "{numbers}"')
def step_served(context, numbers: str) -> None:
    flat = _flat(context)
    context.served_numbers = [n.strip() for n in numbers.split(",")]
    for number in context.served_numbers:
        procedure = _procedure(number)
        expected = (
            f"Stage {number} procedure: {REFERENCES_DIR.as_posix()}/{procedure.filename} (sha256 "
        )
        assert expected in flat, f"{expected!r} not in: {flat}"


@then('the launch output serves no procedure for stages "{numbers}"')
def step_not_served(context, numbers: str) -> None:
    flat = _flat(context)
    for number in (n.strip() for n in numbers.split(",")):
        assert f"Stage {number} procedure:" not in flat, f"Stage {number} was served: {flat}"


@then("every served procedure's digest is the digest of its file")
def step_digest_matches_file(context) -> None:
    flat = _flat(context)
    for number in context.served_numbers:
        procedure = _procedure(number)
        on_disk = hashlib.sha256((Path.cwd() / REFERENCES_DIR / procedure.filename).read_bytes())
        pointer = (
            f"Stage {number} procedure: {REFERENCES_DIR.as_posix()}/{procedure.filename} "
            f"(sha256 {on_disk.hexdigest()})"
        )
        assert pointer in flat, f"{pointer!r} not in: {flat}"
        # One file per stage: the digest through --from is the digest in sequence.
        assert on_disk.hexdigest() == procedure.sha256, procedure.filename


@then("the output names the missing file, the rule it breaks and the recovery command")
def step_refusal_prose(context) -> None:
    flat = _flat(context)
    rel = context.disturbed.relative_to(Path.cwd()).as_posix()
    for needle in (
        f"{rel} is missing",
        "WHY:",
        "OBPI-0.35.0-17",
        "NEXT STEP:",
        "gz agent sync control-surfaces",
    ):
        assert needle in flat, f"{needle!r} not in: {flat}"


@then("the output names the altered file with the digest found and the digest expected")
def step_refusal_digests(context) -> None:
    flat = _flat(context)
    rel = context.disturbed.relative_to(Path.cwd()).as_posix()
    expected = _procedure(context.disturbed.name.split("-")[1]).sha256
    for needle in (rel, context.found_digest, expected, "WHY:", "NEXT STEP:"):
        assert needle in flat, f"{needle!r} not in: {flat}"


@then("no pipeline marker was written")
def step_no_marker(context) -> None:
    for marker in context.run_markers:
        assert not marker.exists(), f"{marker} was written"
