"""BDD steps for gz content land -- OBPI-0.35.0-07 (ADR-0.35.0 Decision 6).

Every scenario builds an isolated synthetic project in the per-scenario temp
directory ``features/environment.py`` chdirs into: surface ``LandSurface.md``
routed to consumers alpha, beta and gamma, built by the same fixture the unit
tier uses (``tests.commands.test_content_land.build_land_project``), so the
two runners exercise one project shape. Nothing here touches this repository's
``.gzkit/``.

Interruptions are induced the way the unit tier induces them: the landing
module's ``_stage_artifact`` / ``_replace_artifact`` seams are patched for one
in-process CLI run. A process kill is a ``BaseException`` the landing cannot
catch, so no cleanup runs -- the state a real kill leaves.

Shared steps reused, never redefined (behave's AmbiguousStep):
``I run the gz command "{command}"``, ``the command exits with code {N}`` and
``the output contains "{text}"`` from ``gz_steps.py``; ``no "{event}" ledger
event was written`` from ``content_commit_retention_steps.py``.
"""

from __future__ import annotations

import builtins
import contextlib
import hashlib
import io
import json
import os
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path, PurePosixPath
from unittest import mock

from behave import given, then, when
from tests.commands.test_content_land import (
    LAND_CONSUMERS,
    LAND_PRIOR_TEXT,
    LAND_PRIOR_WITH_DOOMED,
    LAND_SURFACE,
    build_land_project,
    committed_artifacts,
    landed_events,
    snapshot_tree,
    write_dropped_map,
)

import gzkit.content.landing as landing_mod
from gzkit.cli.main import main
from gzkit.content.corpus_store import load_corpus
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    fingerprint_path,
    rendition_path,
)
from gzkit.content.retention import retention_path

_ROOT = Path(".")
_ATTESTED = ["--attestor", "g0", "--attestation-text", "corpus delta attested"]


class _ProcessKilled(BaseException):
    """A hard kill: unlike OSError, nothing in the landing gets to clean up."""


def _invoke(args: list[str]) -> tuple[int, str]:
    """In-process CLI driver (mirrors content_own_steps.py:_invoke)."""
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


def _land(context, *extra: str) -> None:
    context.exit_code, context.output = _invoke(["content", "land", LAND_SURFACE, *extra])


def _consumer_of(path: str) -> str:
    return PurePosixPath(path).name.split(".", 1)[0]


def _sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _journal(context):
    journal = landing_mod.load_journal(_ROOT, LAND_SURFACE)
    assert journal is not None, f"expected an active landing journal:\n{context.output}"
    context.landing_id = journal.landing_id
    context.journal = journal
    return journal


def _consumer_bytes(consumer: str) -> dict[str, bytes]:
    return {
        path.name: path.read_bytes()
        for path in sorted((_ROOT / ".gzkit" / "renditions" / LAND_SURFACE).iterdir())
        if path.is_file() and path.name.startswith(f"{consumer}.")
    }


def _build(context, *, prior_text: str = LAND_PRIOR_TEXT, new_delta: bool = True) -> None:
    build_land_project(_ROOT, prior_text=prior_text, new_delta=new_delta)
    context.snapshot = snapshot_tree(_ROOT)
    context.committed = committed_artifacts(context.snapshot)


# --- Given ------------------------------------------------------------------


@given("a three-consumer landing project with a new corpus delta")
def step_project_new_delta(context) -> None:
    _build(context)


@given("a three-consumer landing project with an unchanged corpus")
def step_project_unchanged(context) -> None:
    _build(context, new_delta=False)


@given("a three-consumer landing project whose candidates remove a block")
def step_project_doomed(context) -> None:
    _build(context, prior_text=LAND_PRIOR_WITH_DOOMED)


@given('the provenance sidecar of consumer "{consumer}" claims bytes that are not on disk')
def step_forge_sidecar(context, consumer: str) -> None:
    path = fingerprint_path(_ROOT, LAND_SURFACE, consumer)
    forged = json.loads(path.read_text(encoding="utf-8"))
    forged["rendition_fingerprint"] = hashlib.sha256(b"other bytes").hexdigest()
    path.write_bytes(json.dumps(forged).encode("utf-8"))
    context.snapshot = snapshot_tree(_ROOT)


@given('a retention map dropping condition "{condition_id}" for each consumer')
def step_retention_maps(context, condition_id: str) -> None:
    for consumer in LAND_CONSUMERS:
        write_dropped_map(_ROOT, consumer, condition_id=condition_id)
    context.snapshot = snapshot_tree(_ROOT)


# --- When -------------------------------------------------------------------


@when('I land the delta with staging failing at consumer "{consumer}"')
def step_land_staging_fails(context, consumer: str) -> None:
    real_stage = landing_mod._stage_artifact

    def stage(path: Path, data: bytes) -> None:
        if _consumer_of(path.name) == consumer:
            raise OSError(f"injected: disk full while staging {consumer}")
        real_stage(path, data)

    with mock.patch.object(landing_mod, "_stage_artifact", side_effect=stage):
        _land(context, *_ATTESTED)


@when("I land the delta with replacement failing after the first published file")
def step_land_replace_fails(context) -> None:
    real_replace = landing_mod._replace_artifact
    done: list[str] = []

    def replace(root: Path, staging: Path, artifact) -> None:  # noqa: ANN001
        if done:
            raise OSError("injected: replace failed between a rendition and its sidecars")
        real_replace(root, staging, artifact)
        done.append(artifact.path)

    with mock.patch.object(landing_mod, "_replace_artifact", side_effect=replace):
        _land(context, *_ATTESTED)
    _journal(context)


@when('I land the delta and interrupt it after consumer "{consumer}"')
def step_land_interrupted(context, consumer: str) -> None:
    order = list(LAND_CONSUMERS)
    stop_at = order[order.index(consumer) + 1]
    real_replace = landing_mod._replace_artifact

    def replace(root: Path, staging: Path, artifact) -> None:  # noqa: ANN001
        if _consumer_of(artifact.path) == stop_at:
            raise OSError(f"injected: interrupted after consumer {consumer}")
        real_replace(root, staging, artifact)

    with mock.patch.object(landing_mod, "_replace_artifact", side_effect=replace):
        _land(context, *_ATTESTED)
    _journal(context)


@when("I land the delta and the process is killed after one staged file")
def step_land_killed_mid_staging(context) -> None:
    real_stage = landing_mod._stage_artifact
    staged: list[Path] = []

    def stage(path: Path, data: bytes) -> None:
        if staged:
            raise _ProcessKilled
        real_stage(path, data)
        staged.append(path)

    with (
        mock.patch.object(landing_mod, "_stage_artifact", side_effect=stage),
        contextlib.suppress(_ProcessKilled),
        redirect_stdout(io.StringIO()),
        redirect_stderr(io.StringIO()),
    ):
        main(["content", "land", LAND_SURFACE, *_ATTESTED])
    assert staged, "the kill must land after the journal and one staged file"
    _journal(context)


@when("I resume the landing while recording every replaced file")
def step_resume_recording(context) -> None:
    journal = _journal(context)
    context.already_new = {
        artifact.path
        for plan in journal.consumers
        for artifact in plan.artifacts
        if _sha(_ROOT / artifact.path) == artifact.new_sha256
    }
    assert context.already_new, "the interrupted landing must have published a file"
    real_replace = landing_mod._replace_artifact
    context.replaced = []

    def replace(root: Path, staging: Path, artifact) -> None:  # noqa: ANN001
        context.replaced.append(artifact.path)
        real_replace(root, staging, artifact)

    with mock.patch.object(landing_mod, "_replace_artifact", side_effect=replace):
        _land(context)


@when("I resume the landing with any prompt failing the scenario")
def step_resume_no_prompt(context) -> None:
    def refuse_prompt(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("resume prompted for input; it must reuse the recorded attestation")

    with mock.patch.object(builtins, "input", side_effect=refuse_prompt):
        _land(context)


@when('I set different mtimes on the renditions of consumers "{first}" and "{second}"')
def step_set_mtimes(_context, first: str, second: str) -> None:
    one = rendition_path(_ROOT, LAND_SURFACE, first)
    two = rendition_path(_ROOT, LAND_SURFACE, second)
    assert one.read_bytes() == two.read_bytes(), "the two renditions must hold identical bytes"
    os.utime(one, (1_000_000_000, 1_000_000_000))
    os.utime(two, (2_000_000_000, 2_000_000_000))


@when("I query the status of the recorded landing")
def step_query_status(context) -> None:
    before = snapshot_tree(_ROOT)
    _land(context, "--status", context.landing_id)
    context.status_snapshots = (before, snapshot_tree(_ROOT))


@when('I overwrite the rendition of consumer "{consumer}" beside its good sidecar')
def step_overwrite_rendition(_context, consumer: str) -> None:
    rendition_path(_ROOT, LAND_SURFACE, consumer).write_bytes(b"altered bytes\n")


@when('I record the bytes of consumer "{consumer}"')
def step_record_bytes(context, consumer: str) -> None:
    context.recorded_bytes = _consumer_bytes(consumer)
    assert context.recorded_bytes, f"consumer {consumer} has no artifacts"


# --- Then -------------------------------------------------------------------


@then("no committed landing artifact changed")
def step_committed_unchanged(context) -> None:
    assert committed_artifacts(snapshot_tree(_ROOT)) == context.committed, context.output


@then("the project tree is byte-unchanged")
def step_tree_unchanged(context) -> None:
    assert snapshot_tree(_ROOT) == context.snapshot, context.output


@then("the project tree is byte-unchanged since the last status query")
def step_tree_unchanged_by_status(context) -> None:
    before, after = context.status_snapshots
    assert before == after, "--status must write nothing"


@then("no landing journal exists")
def step_no_journal(_context) -> None:
    assert not landing_mod.journal_path(_ROOT, LAND_SURFACE).exists()


@then('the landing journal is in phase "{phase}"')
def step_journal_phase(context, phase: str) -> None:
    assert _journal(context).phase == phase, context.journal.phase


@then('the landing journal names consumers "{consumers}" and the live corpus fingerprint')
def step_journal_contents(context, consumers: str) -> None:
    journal = _journal(context)
    expected = [name.strip() for name in consumers.split(",")]
    assert [plan.consumer for plan in journal.consumers] == expected, journal.consumers
    live = corpus_fingerprint(load_corpus(_ROOT, LAND_SURFACE))
    assert journal.new_corpus_fingerprint == live, (journal.new_corpus_fingerprint, live)
    assert journal.landing_id.startswith("landing-"), journal.landing_id


@then("the resume replaced no file that was already at its new hash")
def step_resume_no_rewrite(context) -> None:
    rewritten = context.already_new.intersection(context.replaced)
    assert not rewritten, f"resume rewrote verified files: {sorted(rewritten)}"
    assert context.replaced, "resume must publish the files still pending"


@then("every landing target is at its recorded new hash")
def step_targets_new(context) -> None:
    for plan in context.journal.consumers:
        for artifact in plan.artifacts:
            actual = _sha(_ROOT / artifact.path)
            assert actual == artifact.new_sha256, (artifact.path, actual, artifact.new_sha256)


@then('exactly one "rendition_landed" ledger event carries the landing id')
def step_one_event(context) -> None:
    ids = [event["landing_id"] for event in landed_events(_ROOT)]
    expected = getattr(context, "landing_id", None) or context.sidecar_landing_id
    assert ids == [expected], ids


@then('every consumer sidecar carries attestation text "{text}" and one shared landing id')
def step_sidecars_shared(context, text: str) -> None:
    sidecars = [
        RenditionProvenance.model_validate_json(
            fingerprint_path(_ROOT, LAND_SURFACE, consumer).read_text(encoding="utf-8")
        )
        for consumer in LAND_CONSUMERS
    ]
    assert {s.attestation_text for s in sidecars} == {text}, [s.attestation_text for s in sidecars]
    landing_ids = {s.landing_id for s in sidecars}
    assert len(landing_ids) == 1 and None not in landing_ids, landing_ids
    (context.sidecar_landing_id,) = landing_ids
    if getattr(context, "landing_id", None) is not None:
        assert context.sidecar_landing_id == context.landing_id, landing_ids


@then('the status classifies "{consumer}" as "{verdict}"')
def step_status_verdict(context, consumer: str, verdict: str) -> None:
    lines = [line.strip() for line in context.output.splitlines()]
    assert f"{consumer}: {verdict}" in lines, context.output


@then('the bytes of consumer "{consumer}" are unchanged')
def step_bytes_unchanged(context, consumer: str) -> None:
    assert _consumer_bytes(consumer) == context.recorded_bytes


@then("every consumer has a published retention sidecar")
def step_retention_sidecars(_context) -> None:
    for consumer in LAND_CONSUMERS:
        path = retention_path(_ROOT, LAND_SURFACE, consumer)
        assert path.exists(), f"missing {path.as_posix()}"
        assert json.loads(path.read_text(encoding="utf-8"))["consumer"] == consumer
