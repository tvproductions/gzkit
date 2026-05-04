"""BDD steps for the evaluation feedback loop (ADR-0.0.26 / OBPI-0.0.26-05).

Covers REQs from OBPIs 01-05:
- 01 (event emission)   — uses ``Ledger.append`` + ``adr_evaluation_event``
- 02 (binding gate)     — exercises ``gz validate --evaluation-justify-binding``
- 03 (clustering chore) — exercises ``gz chores list``, ``gz validate --chores-layout``,
  and the chore's ``run_cluster`` library
- 04 (propose-ghi)      — patches ``gh`` subprocess and TTY to drive
  ``chores_propose_ghi``; exercises ``gz validate --commit-trailers``
- 05 (full loop)        — synthesizes the cross-cutting transition

Mocking discipline: only the ``gh`` subprocess and the TTY surface
(``isatty`` + ``input``) are patched. Git is real (per-scenario
tempdir), the ledger is real, the chore runs through its public
``run_cluster`` entry point.
"""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from behave import given, then, when  # type: ignore[import-untyped]

from gzkit.chores.eval_feedback_cluster_lib import ProposalRecord, run_cluster
from gzkit.ledger import Ledger
from gzkit.ledger_events import adr_evaluation_event

_PATCHERS_KEY = "_eval_feedback_patchers"
_INPUT_RESPONSE_KEY = "_eval_feedback_input_response"
_GH_RESPONSE_KEY = "_eval_feedback_gh_response"
_GH_LABELS_KEY = "_eval_feedback_gh_labels"
_FIXTURES_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "evaluation"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register_patcher(context, patcher) -> None:
    patchers = getattr(context, _PATCHERS_KEY, None)
    if patchers is None:
        patchers = []
        setattr(context, _PATCHERS_KEY, patchers)
    patcher.start()
    patchers.append(patcher)


def _stop_all_patchers(context) -> None:
    import contextlib  # noqa: PLC0415

    patchers = getattr(context, _PATCHERS_KEY, [])
    for p in patchers:
        with contextlib.suppress(RuntimeError):
            p.stop()
    setattr(context, _PATCHERS_KEY, [])


def _ledger_path() -> Path:
    return Path(".gzkit") / "ledger.jsonl"


def _proofs_dir() -> Path:
    return Path(".gzkit") / "chores" / "eval-feedback-cluster" / "proofs"


def _newest_proposal_path() -> Path:
    proofs = _proofs_dir()
    files = sorted(proofs.glob("proposal-*.json"))
    if not files:
        msg = f"No proposal records under {proofs.as_posix()}"
        raise AssertionError(msg)
    return files[-1]


def _make_event(
    artifact_id: str,
    *,
    dimension: str = "clarity",
    score: float = 4.0,
    weighted_total: float = 4.0,
    challenges: list[str] | None = None,
    timestamp: str | None = None,
):
    return adr_evaluation_event(
        artifact_id=artifact_id,
        artifact_type="ADR",
        dimensions={dimension: score},
        scores={dimension: score},
        weighted_total=weighted_total,
        red_team_challenges_fired=challenges or [],
        evaluator_persona="behave-fixture",
        timestamp=timestamp or "2026-05-03T22:00:00+00:00",
    )


def _append_event(event) -> None:
    Ledger(_ledger_path()).append(event)


def _read_proposal(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_thresholds(low_score: float | None = None, recurrence: int | None = None) -> None:
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "eval_feedback_thresholds.json"
    if path.exists():
        thresholds = json.loads(path.read_text(encoding="utf-8"))
    else:
        thresholds = {"low_score_threshold": 3.0, "red_team_count_threshold": 3}
    if low_score is not None:
        thresholds["low_score_threshold"] = low_score
    if recurrence is not None:
        thresholds["cluster_min_recurrence"] = recurrence
    path.write_text(json.dumps(thresholds, indent=2) + "\n", encoding="utf-8")


def _seed_chore_registry() -> None:
    """Copy the canonical chore registry + eval-feedback-cluster slug into the tempdir.

    ``gz chores list`` and ``gz validate --chores-layout`` resolve from
    ``.gzkit/chores`` first. The package fallback works for ``run`` paths
    but the validator and list verb walk the project-local tree, so the
    minimal scaffolding has to land here.
    """
    project_chores = Path(".gzkit") / "chores"
    project_chores.mkdir(parents=True, exist_ok=True)

    # Copy the canonical eval-feedback-cluster slug from the package source
    pkg_root = Path(__file__).resolve().parents[2] / "src" / "gzkit" / "chores"
    src_slug = pkg_root / "eval-feedback-cluster"
    dst_slug = project_chores / "eval-feedback-cluster"
    if src_slug.is_dir() and not dst_slug.exists():
        shutil.copytree(src_slug, dst_slug)
    (dst_slug / "proofs").mkdir(parents=True, exist_ok=True)

    # Minimal registry pointing at the project-local slug
    registry_path = project_chores / "registry.json"
    if not registry_path.exists():
        registry_path.write_text(
            json.dumps(
                {
                    "specVersion": "2.0",
                    "description": "Per-scenario chore registry seed.",
                    "project": {
                        "name": "test-project",
                        "root": ".",
                        "choresDir": ".gzkit/chores",
                        "proofsPattern": ".gzkit/chores/{slug}/proofs",
                    },
                    "lanes": {
                        "lite": {"timeoutSeconds": 120, "allowNetwork": False},
                        "medium": {"timeoutSeconds": 300, "allowNetwork": False},
                        "heavy": {"timeoutSeconds": 900, "allowNetwork": True},
                    },
                    "chores": [
                        {
                            "slug": "eval-feedback-cluster",
                            "title": "Evaluation Feedback Clustering",
                            "version": "1.0.0",
                            "path": ".gzkit/chores/eval-feedback-cluster",
                            "lane": "medium",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def _seed_threshold_defaults() -> None:
    pkg_default = Path(__file__).resolve().parents[2] / "data" / "eval_feedback_thresholds.json"
    target = Path("data") / "eval_feedback_thresholds.json"
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if pkg_default.is_file():
        target.write_text(pkg_default.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        _write_thresholds(low_score=3.0, recurrence=3)


def _make_gh_run_dispatcher(context):
    """Return a subprocess.run side_effect that intercepts gh and delegates everything else."""
    real_run = subprocess.run

    def fake_run(cmd, *args, **kwargs):  # type: ignore[no-untyped-def]
        if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == "gh":
            sub = list(cmd[1:])
            if sub[:2] == ["issue", "create"]:
                url = getattr(context, _GH_RESPONSE_KEY, "https://github.com/owner/repo/issues/1")
                result = mock.MagicMock()
                result.returncode = 0
                result.stdout = url + "\n"
                result.stderr = ""
                return result
            if sub[:2] == ["issue", "view"] and len(sub) >= 3:
                labels = getattr(context, _GH_LABELS_KEY, {}).get(sub[2], [])
                payload = {"labels": [{"name": label} for label in labels]}
                result = mock.MagicMock()
                result.returncode = 0
                result.stdout = json.dumps(payload)
                result.stderr = ""
                return result
            result = mock.MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result
        return real_run(cmd, *args, **kwargs)

    return fake_run


# ---------------------------------------------------------------------------
# Background — workspace bootstrap
# ---------------------------------------------------------------------------


@given("the workspace is initialized for the evaluation-feedback loop")
def step_workspace_init(context) -> None:  # type: ignore[no-untyped-def]
    from tests.commands.common import _quick_init  # noqa: PLC0415

    _quick_init(mode="heavy")
    _seed_chore_registry()
    _seed_threshold_defaults()
    _stop_all_patchers(context)
    setattr(context, _GH_LABELS_KEY, {})


# ---------------------------------------------------------------------------
# Ledger seeding
# ---------------------------------------------------------------------------


_EVENT_WITH_TOTAL = (
    'an adr-evaluation event for "{artifact_id}" '
    'with weighted total {weighted:f} and timestamp "{timestamp}"'
)


@given(_EVENT_WITH_TOTAL)
def step_event_with_total(context, artifact_id: str, weighted: float, timestamp: str) -> None:  # type: ignore[no-untyped-def]
    _append_event(
        _make_event(artifact_id, score=weighted, weighted_total=weighted, timestamp=timestamp)
    )


_LOW_SCORE_EVENT = (
    'a low-score adr-evaluation event for "{artifact_id}" '
    'with dimension "{dimension}" scoring {score:f}'
)


@given(_LOW_SCORE_EVENT)
def step_low_score_event(context, artifact_id: str, dimension: str, score: float) -> None:  # type: ignore[no-untyped-def]
    _append_event(
        _make_event(
            artifact_id,
            dimension=dimension,
            score=score,
            weighted_total=score,
            timestamp="2026-05-03T22:00:00+00:00",
        )
    )


@given('an adr-evaluation event for "{artifact_id}" with dimension "{dimension}" scoring {score:f}')
def step_dimension_event(context, artifact_id: str, dimension: str, score: float) -> None:  # type: ignore[no-untyped-def]
    _append_event(
        _make_event(
            artifact_id,
            dimension=dimension,
            score=score,
            weighted_total=score,
            timestamp="2026-05-03T22:00:00+00:00",
        )
    )


@given('an adr-evaluation event for "{artifact_id}" firing red-team challenges "{challenges}"')
def step_redteam_event(context, artifact_id: str, challenges: str) -> None:  # type: ignore[no-untyped-def]
    challenge_ids = [c.strip() for c in challenges.split(",") if c.strip()]
    _append_event(
        _make_event(
            artifact_id,
            score=4.0,
            weighted_total=4.0,
            challenges=challenge_ids,
            timestamp="2026-05-03T22:00:00+00:00",
        )
    )


@when('I attempt to record a malformed adr-evaluation for "{artifact_id}"')
def step_malformed_event(context, artifact_id: str) -> None:  # type: ignore[no-untyped-def]
    """REQ-0.0.26-01-02: a malformed evaluation must not reach the ledger.

    Production path validates payloads through the ``AdrEvaluationEvent``
    typed model before emission. Construct one with a bad ``dimensions``
    type and assert it raises; the absence of an ``_append_event`` call in
    the catch branch is the proof the ledger stays clean.
    """
    from gzkit.events import AdrEvaluationEvent  # noqa: PLC0415

    try:
        AdrEvaluationEvent(
            event="adr-evaluation",
            artifact_id=artifact_id,
            artifact_type="ADR",
            dimensions="not-a-mapping",  # type: ignore[arg-type]
            scores={},
            weighted_total=0.0,
            red_team_challenges_fired=[],
            evaluator_persona="behave-fixture",
            timestamp="2026-05-03T22:00:00+00:00",
        )
    except Exception:
        # Expected: malformed payload rejected before any emission could occur.
        return
    msg = f"AdrEvaluationEvent unexpectedly accepted malformed payload for {artifact_id!r}"
    raise AssertionError(msg)


@then('the ledger contains {count:d} "{event_name}" events for "{artifact_id}"')
def step_ledger_event_count(context, count: int, event_name: str, artifact_id: str) -> None:  # type: ignore[no-untyped-def]
    path = _ledger_path()
    events = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("event") == event_name and rec.get("id") == artifact_id:
                events.append(rec)
    assert len(events) == count, (
        f"Expected {count} {event_name!r} events for {artifact_id!r}, got {len(events)}"
    )


# ---------------------------------------------------------------------------
# Justify scaffold + threshold steps
# ---------------------------------------------------------------------------


@given('a complete justify scaffold exists for "{artifact_id}"')
def step_justify_scaffold(context, artifact_id: str) -> None:  # type: ignore[no-untyped-def]
    src = _FIXTURES_DIR / "justify-scaffold.md"
    dst_dir = Path("artifacts") / "justify"
    dst_dir.mkdir(parents=True, exist_ok=True)
    slug = artifact_id.replace(".", "-").lower()
    body = src.read_text(encoding="utf-8")
    body = body.replace("ADR-0.99.0-fixture", artifact_id)
    (dst_dir / f"{slug}-2026-05-03T22-00-00.md").write_text(body, encoding="utf-8")


@given('the eval-feedback threshold "{key}" is set to {value:f}')
def step_set_threshold(context, key: str, value: float) -> None:  # type: ignore[no-untyped-def]
    if key == "low_score_threshold":
        _write_thresholds(low_score=value)
    elif key == "cluster_min_recurrence":
        _write_thresholds(recurrence=int(value))


# ---------------------------------------------------------------------------
# Clustering chore
# ---------------------------------------------------------------------------


@when("the eval-feedback-cluster chore runs")
@when("the eval-feedback-cluster chore runs again")
def step_run_cluster_chore(context) -> None:  # type: ignore[no-untyped-def]
    run_cluster(Path.cwd())


@then('{count:d} proposal records exist under "{rel_dir}"')
@then('{count:d} proposal record exists under "{rel_dir}"')
def step_proposal_count(context, count: int, rel_dir: str) -> None:  # type: ignore[no-untyped-def]
    proofs = Path(rel_dir)
    files = sorted(proofs.glob("proposal-*.json")) if proofs.exists() else []
    assert len(files) == count, (
        f"Expected {count} proposal records under {rel_dir}, got {len(files)}"
    )


# ---------------------------------------------------------------------------
# Proposal records / propose-ghi
# ---------------------------------------------------------------------------


@given('a proposal record for cluster "{cluster_key}" exists in the eval-feedback-cluster proofs')
def step_seed_proposal(context, cluster_key: str) -> None:  # type: ignore[no-untyped-def]
    proofs = _proofs_dir()
    proofs.mkdir(parents=True, exist_ok=True)
    template = json.loads((_FIXTURES_DIR / "proposal-template.json").read_text(encoding="utf-8"))
    template["cluster_key"] = cluster_key
    (proofs / "proposal-20260503T220000000000.json").write_text(
        json.dumps(template, indent=2) + "\n", encoding="utf-8"
    )


@given('a filed proposal record for cluster "{cluster_key}" exists with url "{url}"')
def step_seed_filed_proposal(context, cluster_key: str, url: str) -> None:  # type: ignore[no-untyped-def]
    proofs = _proofs_dir()
    proofs.mkdir(parents=True, exist_ok=True)
    template = json.loads((_FIXTURES_DIR / "proposal-template.json").read_text(encoding="utf-8"))
    template["cluster_key"] = cluster_key
    template["filed"] = True
    template["ghi_url"] = url
    (proofs / "proposal-20260503T210000000000.json").write_text(
        json.dumps(template, indent=2) + "\n", encoding="utf-8"
    )


@given("the environment is interactive")
def step_env_interactive(context) -> None:  # type: ignore[no-untyped-def]
    fake_sys = mock.MagicMock(wraps=sys)
    fake_sys.stdin.isatty.return_value = True
    fake_sys.stdout.isatty.return_value = True
    _register_patcher(context, mock.patch("gzkit.commands.chores_propose_ghi_cmd.sys", fake_sys))


@given("the environment is headless")
def step_env_headless(context) -> None:  # type: ignore[no-untyped-def]
    fake_sys = mock.MagicMock(wraps=sys)
    fake_sys.stdin.isatty.return_value = False
    fake_sys.stdout.isatty.return_value = False
    _register_patcher(context, mock.patch("gzkit.commands.chores_propose_ghi_cmd.sys", fake_sys))


@given('the operator confirms with "{response}"')
def step_operator_input(context, response: str) -> None:  # type: ignore[no-untyped-def]
    setattr(context, _INPUT_RESPONSE_KEY, response)
    _register_patcher(context, mock.patch("builtins.input", return_value=response))


@given('gh issue create returns "{url}"')
def step_gh_create_returns(context, url: str) -> None:  # type: ignore[no-untyped-def]
    setattr(context, _GH_RESPONSE_KEY, url)
    fake_run = _make_gh_run_dispatcher(context)
    _register_patcher(
        context, mock.patch("gzkit.commands.chores_propose_ghi_cmd.subprocess.run", fake_run)
    )


@when('I invoke chores_propose_ghi for "{slug}"')
def step_invoke_propose_ghi(context, slug: str) -> None:  # type: ignore[no-untyped-def]
    from gzkit.commands.chores import chores_propose_ghi  # noqa: PLC0415

    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        chores_propose_ghi(slug)
    context.output = output.getvalue()


@then('the most recent proposal record has "{field}" equal to true')
def step_proposal_field_true(context, field: str) -> None:  # type: ignore[no-untyped-def]
    record = _read_proposal(_newest_proposal_path())
    assert record.get(field) is True, f"Expected {field}=true; record: {record}"


@then('the most recent proposal record has "{field}" equal to false')
def step_proposal_field_false(context, field: str) -> None:  # type: ignore[no-untyped-def]
    record = _read_proposal(_newest_proposal_path())
    assert record.get(field) is False, f"Expected {field}=false; record: {record}"


@then('the most recent proposal record has "{field}" equal to "{expected}"')
def step_proposal_field_equals(context, field: str, expected: str) -> None:  # type: ignore[no-untyped-def]
    record = _read_proposal(_newest_proposal_path())
    assert record.get(field) == expected, f"Expected {field}={expected!r}; record: {record}"


# ---------------------------------------------------------------------------
# ProposalRecord schema (REQ-0.0.26-04-10)
# ---------------------------------------------------------------------------


@given("a minimal proposal record without filed, ghi_url, or advisory fields")
def step_minimal_proposal_record(context) -> None:  # type: ignore[no-untyped-def]
    payload = {
        "cluster_key": "dim:clarity:low",
        "recurrence_count": 3,
        "source_artifact_ids": ["ADR-0.99.0-a", "ADR-0.99.0-b", "ADR-0.99.0-c"],
        "source_artifact_paths": [
            "artifacts/justify/ADR-0.99.0-a.md",
            "artifacts/justify/ADR-0.99.0-b.md",
            "artifacts/justify/ADR-0.99.0-c.md",
        ],
        "summary": "fixture",
        "proposed_rule_target": "docs/governance/clarity-low-improvement.md",
        "content_hash": "abcdef0123456789",
    }
    context.minimal_proposal = ProposalRecord.model_validate(payload)


@then('the proposal record deserializes with "{field}" equal to false')
def step_minimal_proposal_field_false(context, field: str) -> None:  # type: ignore[no-untyped-def]
    value = getattr(context.minimal_proposal, field)
    assert value is False, f"Expected {field}=false on minimal record; got {value!r}"


@then('the proposal record deserializes with "{field}" equal to None')
def step_minimal_proposal_field_none(context, field: str) -> None:  # type: ignore[no-untyped-def]
    value = getattr(context.minimal_proposal, field)
    assert value is None, f"Expected {field}=None on minimal record; got {value!r}"


# ---------------------------------------------------------------------------
# Trailer validator (REQ-0.0.26-04-04, -05, REQ-0.0.26-05-03)
# ---------------------------------------------------------------------------


def _git(*args: str) -> None:
    subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _bootstrap_git_repo() -> None:
    _git("init", "-b", "main")
    _git("config", "user.name", "Behave Fixture")
    _git("config", "user.email", "behave@users.noreply.github.com")
    _git("add", ".")
    _git("commit", "--allow-empty", "-m", "seed")


_RULE_EDIT_NO_TRAILER = (
    "a git repo with a rule-edit commit closing GHI {number:d} "
    "without an Eval-feedback-source trailer"
)


@given(_RULE_EDIT_NO_TRAILER)
def step_rule_edit_no_trailer(context, number: int) -> None:  # type: ignore[no-untyped-def]
    _bootstrap_git_repo()
    rules_dir = Path(".gzkit") / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_file = rules_dir / "fixture-rule.md"
    rule_file.write_text("# Fixture rule\n\nfixture body\n", encoding="utf-8")
    _git("add", str(rule_file))
    _git("commit", "-m", f"docs: tighten fixture rule\n\nCloses #{number}\n")


_RULE_EDIT_WITH_TRAILER = (
    "a git repo with a rule-edit commit closing GHI {number:d} with an Eval-feedback-source trailer"
)


@given(_RULE_EDIT_WITH_TRAILER)
def step_rule_edit_with_trailer(context, number: int) -> None:  # type: ignore[no-untyped-def]
    _bootstrap_git_repo()
    rules_dir = Path(".gzkit") / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_file = rules_dir / "fixture-rule.md"
    rule_file.write_text("# Fixture rule (with trailer)\n\nfixture body\n", encoding="utf-8")
    _git("add", str(rule_file))
    _git(
        "commit",
        "-m",
        (
            f"docs: tighten fixture rule\n\nCloses #{number}\n\n"
            "Eval-feedback-source: artifacts/justify/fixture-cluster-record.md\n"
        ),
    )


@given('gh issue view labels for {number:d} include "{label}"')
def step_gh_issue_labels(context, number: int, label: str) -> None:  # type: ignore[no-untyped-def]
    labels_map = getattr(context, _GH_LABELS_KEY, {})
    labels_map.setdefault(str(number), []).append(label)
    setattr(context, _GH_LABELS_KEY, labels_map)
    fake_run = _make_gh_run_dispatcher(context)
    _register_patcher(context, mock.patch("gzkit.commands.validate_cmd.subprocess.run", fake_run))
