"""Disposable writable checkout for the Step-4b independent adversary (GHI #961).

Step 4b's reviewer must be able to REPLAY the proof it is judging: run the
baseline, apply the substitution, watch the named test fail on its own
assertion, restore the source byte-identically, and re-run. The mandated
``adversarial-review`` transport pins ``sandbox: "read-only"``, so while it was
the only permitted dispatch the reviewer could audit that record but never
reproduce it -- and a gate that cannot reproduce cannot tell "I verified this
works" from "I could not check".

The repair is not to make the operator's tree writable. It is to hand the
reviewer a *disposable* checkout of the reviewed source and point the sandbox
at that instead, so ``workspace-write`` supplies genuine execution while the
active checkout stays protected by the sandbox boundary rather than by
convention.

Two separable jobs live here:

* :func:`materialize_adversary_workspace` builds the checkout and records the
  identity of the source it copied, so a replay cannot silently run against
  some other tree.
* :func:`validate_replay_records` judges a claimed replay, because an enabled
  capability is not a used one: an execution error, a skipped selector, or a
  record the reviewer merely read must never count as independent replay.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.red_witness import classify_failure

_SUBPROCESS_TIMEOUT_S = 300


class AdversaryWorkspace(BaseModel):
    """Identity of a materialized disposable checkout.

    ``source_digest`` is what keeps proof identity honest: it digests the
    reviewed file set as copied, so a replay record naming this workspace is
    bound to the exact bytes the reviewer was handed.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = Field(min_length=1, description="Absolute path of the disposable checkout")
    head_commit: str = Field(min_length=1, description="Commit the checkout was built from")
    dirty: bool = Field(description="Whether uncommitted changes were overlaid onto the checkout")
    source_digest: str = Field(min_length=1, description="Digest of the reviewed source as copied")
    file_count: int = Field(ge=1, description="Files materialized into the checkout")
    interpreter: str = Field(min_length=1, description="Interpreter that runs the checkout's tests")
    python_path: str = Field(min_length=1, description="PYTHONPATH redirecting imports to the copy")


class ReplayRun(BaseModel):
    """One executed run inside the disposable checkout."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    exit_status: int = Field(description="Observed process exit status")
    tests_run: int = Field(ge=0, description="Tests the runner reported executing")
    output_tail: str = Field(default="", description="Observed output, retained for the record")


class ReplayRecord(BaseModel):
    """A reviewer's claim that it independently replayed one obligation's proof.

    Every field is an observation, never a verdict. :func:`validate_replay_records`
    decides whether the observations amount to a replay.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    obligation_id: str = Field(min_length=1, description="Obligation whose proof was replayed")
    proof_id: str = Field(min_length=1, description="Proof record this replay reproduces")
    workspace_digest: str = Field(min_length=1, description="source_digest of the checkout used")
    selectors: tuple[str, ...] = Field(default=(), description="Fully qualified tests executed")
    mutation_label: str = Field(default="", description="Substitution the reviewer applied")
    baseline: ReplayRun | None = Field(default=None, description="Run before the substitution")
    mutated: ReplayRun | None = Field(default=None, description="Run under the substitution")
    restored: ReplayRun | None = Field(default=None, description="Run after restoring the source")
    source_digest_before: str = Field(default="", description="Mutated file digest before the edit")
    source_digest_after: str = Field(default="", description="Mutated file digest after restore")


def _run(
    args: list[str], cwd: Path, stdin: bytes | None = None
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        args,
        cwd=cwd,
        input=stdin,
        capture_output=True,
        check=False,
        timeout=_SUBPROCESS_TIMEOUT_S,
    )


def _refuse(step: str, completed: subprocess.CompletedProcess[bytes]) -> None:
    """Refuse a half-built checkout.

    A partial tree would let a replay report against source nobody reviewed.
    """
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()[:400]
        raise RuntimeError(f"adversary workspace: cannot {step}: {detail}")


def _digest_tree(root: Path, files: Sequence[Path]) -> str:
    """Digest *files* by relative path and content, order-independent."""
    accumulator = hashlib.sha256()
    for rel in sorted(path.relative_to(root).as_posix() for path in files):
        accumulator.update(rel.encode("utf-8"))
        accumulator.update(b"\0")
        accumulator.update(hashlib.sha256((root / rel).read_bytes()).digest())
    return accumulator.hexdigest()


def materialize_adversary_workspace(
    project_root: Path, destination: Path, *, interpreter: Path | None = None
) -> AdversaryWorkspace:
    """Copy the reviewed source into *destination* as a disposable writable checkout.

    The checkout carries tracked content at ``HEAD`` plus any uncommitted tracked
    modifications, because the reviewed source is the working tree the proof
    executed against, not the last commit. Ignored paths are deliberately NOT
    copied: the checkout is the source under review, and the reviewer runs it
    with the active environment's interpreter under a ``PYTHONPATH`` that
    redirects imports into the copy.

    Raises:
        RuntimeError: when the reviewed source cannot be reproduced.

    """
    destination.mkdir(parents=True, exist_ok=True)

    head = _run(["git", "rev-parse", "HEAD"], project_root)
    _refuse("resolve HEAD", head)
    head_commit = head.stdout.decode("utf-8", errors="replace").strip()

    archive = _run(["git", "archive", "--format=tar", head_commit], project_root)
    _refuse("archive the reviewed source", archive)
    _refuse(
        "extract the reviewed source",
        _run(["tar", "-x", "-C", str(destination)], project_root, stdin=archive.stdout),
    )

    diff = _run(["git", "diff", "HEAD"], project_root)
    _refuse("read uncommitted changes", diff)
    dirty = bool(diff.stdout.strip())
    if dirty:
        _refuse(
            "overlay uncommitted changes",
            _run(["git", "apply", "--whitespace=nowarn", "-"], destination, stdin=diff.stdout),
        )

    files = [path for path in destination.rglob("*") if path.is_file()]
    if not files:
        raise RuntimeError("adversary workspace: materialized no files")

    return AdversaryWorkspace(
        path=str(destination.resolve()),
        head_commit=head_commit,
        dirty=dirty,
        source_digest=_digest_tree(destination, files),
        file_count=len(files),
        interpreter=str(interpreter or (project_root / ".venv" / "bin" / "python")),
        python_path=str((destination / "src").resolve()),
    )


def remove_adversary_workspace(workspace: AdversaryWorkspace) -> None:
    """Delete the disposable checkout; a leftover writable tree is a hazard, not evidence."""
    shutil.rmtree(workspace.path, ignore_errors=True)


def validate_replay_records(
    records: Sequence[ReplayRecord],
    *,
    workspace_digest: str,
    expected_obligations: Sequence[str] = (),
) -> list[str]:
    """Return the reasons *records* fail to establish independent replay.

    An empty list means every record observed a real replay: a green baseline,
    a substitution whose named tests failed on an ASSERTION, a byte-identical
    restoration, and a green restored run, all inside the named workspace.

    The rejections are the point. A run that errored proves the module was
    broken, not that the guard was load-bearing; a selector that executed zero
    tests proves nothing at all; a record with no substitution is an inspection
    wearing a replay's name. Each is refused by name rather than collapsed into
    a truthy "replay present" check.
    """
    reasons: list[str] = []
    replayed: set[str] = set()

    for record in records:
        subject = f"{record.obligation_id} (proof {record.proof_id})"
        replayed.add(record.obligation_id)

        if record.workspace_digest != workspace_digest:
            reasons.append(
                f"{subject}: replay names workspace {record.workspace_digest[:12]} but the "
                f"materialized checkout is {workspace_digest[:12]} - replayed against another tree"
            )
            continue
        if not record.selectors:
            reasons.append(f"{subject}: replay names no executed test selector")
            continue
        if not record.mutation_label.strip():
            reasons.append(
                f"{subject}: replay applied no substitution - an inspected record is not a replay"
            )
            continue
        if record.baseline is None or record.mutated is None or record.restored is None:
            reasons.append(
                f"{subject}: replay is missing a baseline, mutated or restored run; all three are "
                "required to tell a load-bearing guard from a broken module"
            )
            continue

        if record.baseline.exit_status != 0:
            reasons.append(
                f"{subject}: baseline run was not green (exit {record.baseline.exit_status})"
            )
        if record.baseline.tests_run < 1:
            reasons.append(f"{subject}: baseline executed no tests - the selector was skipped")

        failure_class = classify_failure(record.mutated.exit_status, record.mutated.output_tail)
        if failure_class != "assertion":
            reasons.append(
                f"{subject}: substitution produced failure_class={failure_class!r}, "
                "not 'assertion' - an error or a pass is not an expected assertion failure"
            )
        if record.mutated.tests_run < 1:
            reasons.append(f"{subject}: mutated run executed no tests - the selector was skipped")

        if record.restored.exit_status != 0:
            reasons.append(
                f"{subject}: restored run was not green (exit {record.restored.exit_status})"
            )
        if not record.source_digest_before or not record.source_digest_after:
            reasons.append(f"{subject}: replay does not record the source digest around the edit")
        elif record.source_digest_before != record.source_digest_after:
            reasons.append(
                f"{subject}: source was not restored byte-identically "
                f"({record.source_digest_before[:12]} != "
                f"{record.source_digest_after[:12]})"
            )

    for obligation in expected_obligations:
        if obligation not in replayed:
            reasons.append(f"{obligation}: no independent replay record")

    return reasons


__all__ = [
    "AdversaryWorkspace",
    "ReplayRecord",
    "ReplayRun",
    "materialize_adversary_workspace",
    "remove_adversary_workspace",
    "validate_replay_records",
]
