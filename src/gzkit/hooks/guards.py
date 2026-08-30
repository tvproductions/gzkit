"""Policy enforcement guards.

Unittest-only policy enforcement: scan for pytest usage and reject it.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

from gzkit.mx import levels as _mx_levels

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "site",
    "build",
    "dist",
    "htmlcov",
}

SCAN_EXTS = {".py", ".toml", ".ini", ".cfg", ".yaml", ".yml", ".txt"}

PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^\s*import\s+pytest\b"),
    re.compile(r"^\s*from\s+pytest\s+import\b"),
    # Require an identifier char after the dot so module-attribute access
    # (pytest.fixture / pytest.mark) is caught but a prose sentence ending in
    # "...pytest. " (a quoted policy reference) is not (GHI #621).
    re.compile(r"\bpytest\.\w"),
    re.compile(r"@\s*pytest\.\w"),
    re.compile(r"\bpy\.test\b"),
]

EXCLUDE_PATH_SNIPPETS = (
    "/.venv/",
    "/venv/",
    "/env/",
    "/site/",
    "/build/",
    "/dist/",
    "/htmlcov/",
    "/site-packages/",
    # Allow pytest mentions in guard enforcement files themselves
    "/gzkit/hooks/guards.py",
    # Allow pytest mentions in the guards test module (tests must exercise the detected patterns)
    "/tests/test_hooks_guards.py",
)


def _repo_files(root: Path) -> Iterator[Path]:
    """Yield repo CONTENT — tracked files plus untracked ones git does not ignore.

    ``rglob("*")`` enumerates the whole filesystem under ``root`` and discards
    the excluded directories only AFTER visiting them, which is the cost this
    guard was paying: 367,088 paths walked against 7,241 tracked files, 324,827
    of them under the gitignored ``.ruff_cache/`` (measured 2026-08-28,
    GHI #902). The suffix filter below then dropped every one, so the work was
    pure enumeration -- but enumeration of 45x the repository.

    :data:`EXCLUDE_DIRS` names eight directories and every one is gitignored, so
    asking git subsumes the list rather than competing with it. The filters below
    are kept regardless: they encode SEMANTIC exclusions (``docs/``, this
    module's own test file) that have nothing to do with what git tracks.

    Falls back to the walk when git cannot answer, so the guard degrades to slow
    rather than to scanning nothing -- a pytest-import guard that silently
    inspects zero files is exactly the false-green it exists to prevent.
    """
    proc = subprocess.run(  # noqa: S603
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        yield from root.rglob("*")
        return
    for rel in proc.stdout.split("\0"):
        if rel:
            yield root / rel


def iter_files(root: Path) -> Iterable[Path]:
    """Iterate over files to scan, excluding common generated/virtual paths."""
    for p in _repo_files(root):
        if p.is_dir() or not p.is_file():
            continue
        if p.suffix.lower() not in SCAN_EXTS:
            continue
        # Prune any descendant of an excluded directory (rglob does not prune).
        if any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts[:-1]):
            continue
        posix = p.as_posix()
        if "/docs/" in posix or posix.startswith("docs/"):
            continue
        if any(snippet in posix for snippet in EXCLUDE_PATH_SNIPPETS) or posix.startswith("site/"):
            continue
        yield p


def scan_file(path: Path) -> list[str]:
    """Scan a single file for pytest usage violations.

    Returns list of violation messages (empty if clean).
    """
    violations: list[str] = []
    if path.name == "conftest.py":
        violations.append("contains pytest-specific conftest.py")
        return violations
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        return [f"unreadable file: {e}"]

    if path.name in {"pyproject.toml", "requirements.txt", "requirements-dev.txt"}:
        if re.search(r"(?i)\bpytest\b", text):
            violations.append("declares pytest dependency")
        return violations

    for i, line in enumerate(text.splitlines(), start=1):
        for pat in PATTERNS:
            if pat.search(line):
                violations.append(f"L{i}: {line.strip()}")
                break
    return violations


def forbid_pytest(root: Path) -> int:
    """Scan repository for pytest usage and return exit code.

    Args:
        root: Project root directory to scan.

    Returns:
        0 if no pytest usage found
        1 if pytest usage detected

    """
    findings: list[tuple[Path, list[str]]] = []
    for f in iter_files(root):
        v = scan_file(f)
        if v:
            findings.append((f, v))

    if findings:
        print("pytest usage detected; this repository enforces unittest-only.")  # noqa: T201
        for path, msgs in findings:
            _safe_print(f"- {path}")
            for m in msgs:
                _safe_print(f"    {m}")
        print("\nPlease remove pytest references or dependencies.")  # noqa: T201
        return 1
    return 0


def _safe_print(s: str) -> None:
    """Print a string with ASCII-escape fallback for narrow-encoding terminals.

    The pre-commit hook invocation path (``uv run -m gzkit.hooks.guards``)
    bypasses the CLI entrypoint's ``sys.stdout.reconfigure(encoding='utf-8')``
    guard, so finding output that contains non-ASCII bytes can raise
    ``UnicodeEncodeError`` on Windows cp1252 terminals. Fall back to a
    backslash-escaped ASCII form rather than crashing the hook.
    """
    try:
        print(s)  # noqa: T201
    except UnicodeEncodeError:
        print(s.encode("ascii", "backslashreplace").decode("ascii"))  # noqa: T201


def _run_git(args: list[str], cwd: Path) -> str:
    """Return stdout of ``git <args>`` from ``cwd``; empty string on failure."""
    import subprocess  # noqa: PLC0415

    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
            encoding="utf-8",
        )
    except (FileNotFoundError, OSError):
        return ""
    return result.stdout or ""


def forbid_manual_ledger_edits(root: Path) -> int:
    """Reject staged ledger edits that are not strict appends (GHI #207).

    Every write to ``.gzkit/ledger.jsonl`` must go through ``gz`` commands,
    which append-only. A staged diff that modifies or deletes existing lines
    is a manual-edit signal and fails closed. New trailing append-only lines
    are allowed — the agent may have legitimately emitted an event via
    ``gz`` before staging.
    """
    staged = _run_git(["diff", "--cached", ".gzkit/ledger.jsonl"], root)
    if not staged:
        return 0
    # Hunks: look for ``-`` lines that aren't ``---`` or ``+++``, and ``+``
    # lines that aren't ``+++``. A strict append only contains ``+`` bodies
    # after the final hunk header; no ``-`` bodies anywhere.
    for raw in staged.splitlines():
        if raw.startswith("---") or raw.startswith("+++"):
            continue
        if raw.startswith("-") and not raw.startswith("--"):
            _safe_print(
                "Manual edit to .gzkit/ledger.jsonl detected — ledger is "
                "append-only via gz commands (CLAUDE.md governance rule 16)."
            )
            _safe_print(f"  offending line: {raw}")
            return 1
    return 0


def _parse_staged_name_status(staged: str) -> dict[str, str]:
    r"""Parse ``git diff --cached --name-status`` into a ``{path: code}`` map.

    Rename/copy entries are the three-field form ``R<score>\\t<old>\\t<new>``:
    the new path maps to the rename code, the old path maps to ``D``. Plain
    entries are the two-field ``<code>\\t<path>`` form.
    """
    status: dict[str, str] = {}
    for line in staged.splitlines():
        fields = line.split("\t")
        if len(fields) < 2:
            continue
        code = fields[0].strip()[:1]
        if not code:
            continue
        if code in ("R", "C") and len(fields) >= 3:
            old_path, new_path = fields[1].strip(), fields[2].strip()
            if old_path:
                status[old_path] = "D"
            if new_path:
                status[new_path] = code
        else:
            path = fields[1].strip()
            if path:
                status[path] = code
    return status


def _vendor_mirror_roots(root: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return ``(skill_mirror_roots, rule_mirror_roots)`` for the enabled vendors.

    Derived from ``.gzkit.json`` rather than transcribed here (GHI #921). The
    roots were hardcoded to ``.claude/**`` and ``.github/**``, so after the
    Copilot drop this guard told operators to produce ``.github/skills/`` and
    ``.github/instructions/`` mirrors under trees that no longer exist, while
    never checking the live Codex tree at all. ``has_vendor_declaration``
    distinguishes a declared vendor set from ``VendorsConfig``'s defaults --
    matching ``skills_audit`` and ``sync_all``, which must ask the same
    question this does.

    Codex consumes rules through the nested ``AGENTS.md`` projection and has no
    ``.agents/rules/`` tree, so the rule-mirror set is Claude's alone.

    Loading is defensive: a pre-commit guard that aborts the commit because the
    project config is absent or unparseable would be a worse failure than the
    drift it exists to catch, so an unreadable config falls back to the model
    defaults.
    """
    from gzkit.config import GzkitConfig  # noqa: PLC0415
    from gzkit.sync_surfaces import has_vendor_declaration  # noqa: PLC0415

    try:
        config = GzkitConfig.load(root / ".gzkit.json")
    except (TypeError, OSError, ValueError):
        config = GzkitConfig()
    vendor_aware = has_vendor_declaration(config)
    skills = tuple(
        path
        for path, vendor in (
            (config.paths.claude_skills, config.vendors.claude),
            (config.paths.codex_skills, config.vendors.codex),
            (config.paths.copilot_skills, config.vendors.copilot),
        )
        if not vendor_aware or vendor.enabled
    )
    rules = tuple(
        path
        for path, vendor in ((config.paths.claude_rules, config.vendors.claude),)
        if not vendor_aware or vendor.enabled
    )
    return skills, rules


def _missing_mirror_error(
    path: str, rel: str, mirror_roots: tuple[str, ...], staged_paths: set[str]
) -> str | None:
    """Return the drift message for *path*, or ``None`` when a mirror is staged.

    Both surfaces ask the same question of different roots, so they share one
    implementation: an inlined second copy is what let the skill arm and the
    rule arm drift apart on which vendors they named (GHI #921).
    """
    mirrors = [f"{mirror_root}/{rel}" for mirror_root in mirror_roots]
    if not mirrors or any(mirror in staged_paths for mirror in mirrors):
        return None
    named = " / ".join(f"`{mirror}`" for mirror in mirrors)
    return f"{path} edited without {named} mirror. Run `uv run gz agent sync control-surfaces`."


def forbid_skill_sync_drift(root: Path) -> int:
    r"""Reject canonical skill/rule edits without their vendor mirrors (GHI #210).

    Every modification to ``.gzkit/skills/**/SKILL.md`` must carry its
    mirror in the same commit, under every enabled vendor's surface root.
    The roots come from ``.gzkit.json`` via :func:`_vendor_mirror_roots`, never
    from a list written here. The mirror is generated by
    ``gz agent sync control-surfaces`` — if it's missing from the staged diff
    for a modification, sync was skipped.

    Deletions are exempt: the retire-on-delete doctrine
    (``.gzkit/rules/skill-surface-sync.md`` § Retirement policy, GHI #464)
    permits canonical deletions where the mirror is already absent. A
    deletion that requires mirror cleanup will surface in the next sync
    pass; absence is not drift.

    Renames (a skill directory ``gz-`` prefix migration, GHI #488) stage as
    ``git diff --name-status`` three-field ``R<score>\\t<old>\\t<new>``
    entries. Detection keys on the new path; the old path is treated as a
    deletion.
    """
    staged = _run_git(["diff", "--cached", "--name-status"], root)
    if not staged:
        return 0
    # Renames key on the new path; this also sidesteps git rename detection
    # cross-pairing byte-identical SKILL.md files across vendor trees when
    # several are renamed at once (GHI #488). See _parse_staged_name_status.
    staged_status = _parse_staged_name_status(staged)
    staged_paths = set(staged_status)
    skill_roots, rule_roots = _vendor_mirror_roots(root)

    errors: list[str] = []
    for path in sorted(staged_paths):
        if staged_status.get(path) == "D":
            continue
        if path.startswith(".gzkit/skills/") and path.endswith("SKILL.md"):
            rel = path[len(".gzkit/skills/") :]
            error = _missing_mirror_error(path, rel, skill_roots, staged_paths)
            if error:
                errors.append(error)
        if path.startswith(".gzkit/rules/") and path.endswith(".md"):
            rel = path[len(".gzkit/rules/") :]
            if Path(rel).name == "AGENTS.md":
                continue
            error = _missing_mirror_error(path, rel, rule_roots, staged_paths)
            if error:
                errors.append(error)
    if errors:
        _safe_print("Skill/rule sync drift detected:")
        for err in errors:
            _safe_print(f"  - {err}")
        return 1
    return 0


def forbid_post_authoring_src_commits(root: Path) -> int:
    """Refuse a commit carrying production code past Stage 2 (GHI #844).

    This is the arm of the post-Stage-2 fence that no tool choice evades. Its
    sibling — the generated ``.claude/hooks/pipeline-gate.py`` PreToolUse hook —
    binds the ``Write|Edit|NotebookEdit`` matcher and keys on
    ``tool_input.file_path``, a field a Bash payload does not carry. Measured
    2026-08-21 across the three sessions that implemented OBPI-0.35.0-09: 348
    Bash calls, zero Write/Edit calls, ~350 lines of production code authored at
    ``current_stage: verify``, and the hook never executed once.

    Reading the staged diff answers the question the hook was asked but could
    not hear: did production code change while the pipeline was past its
    authoring stage? ``sed``, a heredoc, inline ``python``, and an editor
    outside the session all land in ``git diff --cached`` identically.

    The decision itself lives in :mod:`gzkit.pipeline_stage_fence` so this guard
    and the hook cannot drift apart.
    """
    from gzkit.pipeline_stage_fence import (  # noqa: PLC0415
        marker_stage,
        post_authoring_commit_message,
        refuses_production_commit,
    )

    plans_dir = root / ".claude" / "plans"
    if not plans_dir.is_dir():
        return 0
    staged = _run_git(["diff", "--cached", "--name-status"], root)
    if not staged:
        return 0
    changed = [path for path, code in _parse_staged_name_status(staged).items() if code != "D"]
    if not changed:
        return 0

    for marker_path in sorted(plans_dir.glob(".pipeline-active*.json")):
        stage = marker_stage(marker_path)
        if stage is None:
            continue
        offending = [p for p in changed if refuses_production_commit(stage, p)]
        if not offending:
            continue
        obpi_id = _marker_obpi_id(marker_path)
        _safe_print(post_authoring_commit_message(obpi_id, stage, offending))
        return 1
    return 0


def forbid_unattested_obpi_completion_commits(root: Path) -> int:
    """Refuse a commit that FLIPS an OBPI brief to Completed without its evidence (GHI #847).

    Sibling of :func:`forbid_post_authoring_src_commits`, same remedy shape. The
    PreToolUse hook this backstops — ``.claude/hooks/obpi-completion-validator.py``
    — binds ``Write|Edit|NotebookEdit`` and keys on ``tool_input.file_path``, a
    field a Bash payload does not carry, so a ``sed``, heredoc, or inline-``python``
    edit reaches the commit having passed no gate at all. Reading ``git diff
    --cached`` answers the question the hook was asked but could not hear: is a
    brief becoming Completed, and is the evidence there?

    Scoped to the TRANSITION, never to the state. A brief already Completed at
    ``HEAD`` is skipped, so an unrelated edit to a long-landed brief — a typo, a
    link repair — does not have to re-satisfy a bar its era never applied. That is
    the same scoping the hook does with ``old_string``, and without it this guard
    would refuse ordinary maintenance on historical briefs.

    The rule lives in :mod:`gzkit.obpi_completion_fence` so this guard, the hook,
    and ``gz obpi complete``'s own pre-flight cannot drift apart.
    """
    from gzkit.obpi_completion_fence import (  # noqa: PLC0415
        completion_blockers,
        has_audit_evidence,
        is_obpi_brief_path,
        marks_completed,
        obpi_id_from_path,
        unattested_completion_commit_message,
    )

    staged = _run_git(["diff", "--cached", "--name-status"], root)
    if not staged:
        return 0

    for path, code in sorted(_parse_staged_name_status(staged).items()):
        if code == "D" or not is_obpi_brief_path(path):
            continue
        staged_text = _run_git(["show", f":{path}"], root)
        if not staged_text or not marks_completed(staged_text):
            continue
        # Only the transition is gated: an empty HEAD blob means the brief is new.
        head_text = _run_git(["show", f"HEAD:{path}"], root)
        if head_text and marks_completed(head_text):
            continue
        obpi_id = obpi_id_from_path(path)
        if obpi_id is None:
            continue
        blockers = completion_blockers(staged_text)
        adr_dir = (root / path).parent.parent
        if not has_audit_evidence(adr_dir, obpi_id):
            blockers.append(
                "No completion entry in <ADR>/logs/obpi-audit.jsonl "
                "(the brief says Completed; the audit ledger does not)"
            )
        if blockers:
            _safe_print(unattested_completion_commit_message(obpi_id, path, blockers))
            return 1
    return 0


def _marker_obpi_id(marker_path: Path) -> str:
    """Return a marker's ``obpi_id``, falling back to its filename stem."""
    import json  # noqa: PLC0415

    try:
        payload = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return marker_path.stem
    if isinstance(payload, dict):
        obpi_id = str(payload.get("obpi_id") or "").strip()
        if obpi_id:
            return obpi_id
    return marker_path.stem


def _run_enforcement_floor(root: Path) -> int:
    """Run the enforcement-claim meta-validator as a pre-push guard. READ-ONLY on clean."""
    from gzkit.quality import run_enforcement_floor_audit  # noqa: PLC0415

    result = run_enforcement_floor_audit(root)
    if not result.success:
        _safe_print(f"[pre-push] Enforcement floor failed:\n{result.stdout}")
        return 1
    return 0


# ---------------------------------------------------------------------------
# MX checkpoint seam for the pre-commit enforcement surface (GHI #843)
# ---------------------------------------------------------------------------
#
# ADR-0.0.74 Boundary Invariant #2: "Every fail-closed funnel/guard resolves its
# effective GZ_<LEVEL> by passing through the shared checkpoint ... a guard that
# decides its own severity OR its own disposition without the checkpoint is the
# named coverage defect."
#
# Every guard below did exactly that -- a bare `return 1` -- so an open hangar
# had no authority over the pre-commit surface at all, one of the two surfaces
# governance is enforced on. `gz mx --help` advertises the hangar so "the
# operator can repair governance itself", and its own worked example is
# `gz mx enter --reason "repair ledger"`.
#
# ONE inventory, ONE seam -- the shape OBPI-0.0.74-20 established for the ~30
# `gz check` steps in src/gzkit/commands/quality.py, not N inline substitutions.
#
# Floor membership is expressed two ways, both borrowed rather than invented:
#
#   * by NAME -- `ledger` and `gate5-attestation` are literal GATE5_INVARIANTS
#     members, so checkpoint.resolve pins them CRITICAL in and out of the hangar
#     (BI#3). A hangar-open ledger hand-repair is therefore STILL refused, by
#     design: the governed route for that is an append-only corrective-action
#     primitive (GHI #611), never a demoted integrity guard.
#   * by LEVEL -- a guard that must never demote but is not a floor member emits
#     CRITICAL, exactly as quality.py pins "Enforcement floor" after GHI #651.
#     `post-authoring-src-commits` is pinned here to PRESERVE today's behaviour
#     rather than to rule on it; whether the hangar should be able to demote the
#     Stage-2 production-code fence is an operator call, disclosed on GHI #843.
#
# Entries are (mx guard name, module attribute, emitted level). The attribute
# indirection keeps this tuple the single source of truth: `run_guards` never
# names a guard, so one added without an entry is unreachable rather than
# silently unchecked -- the inventory gap that produced this defect.
_GUARD_META: tuple[tuple[str, str, int], ...] = (
    ("forbid-pytest", "forbid_pytest", _mx_levels.ERROR),
    ("ledger", "forbid_manual_ledger_edits", _mx_levels.ERROR),
    ("skill-sync-drift", "forbid_skill_sync_drift", _mx_levels.ERROR),
    ("post-authoring-src-commits", "forbid_post_authoring_src_commits", _mx_levels.CRITICAL),
    ("gate5-attestation", "forbid_unattested_obpi_completion_commits", _mx_levels.ERROR),
    ("enforcement-floor", "_run_enforcement_floor", _mx_levels.CRITICAL),
)


def _guard_grounds(guard_name: str, emitted_level: int, root: Path) -> bool:
    """Return True when *guard_name*'s finding must block the commit.

    Fails CLOSED. A broken or half-repaired ``gzkit.mx`` is precisely the state
    MX mode exists to survive, so an unresolvable checkpoint blocks the commit
    rather than silently demoting the guard that could not be resolved.
    """
    try:
        from gzkit.mx import checkpoint  # noqa: PLC0415

        return checkpoint.blocks(guard_name, emitted_level, root)
    except Exception:  # noqa: BLE001 - an unreadable checkpoint must never demote a guard
        return True


def run_guards(root: Path) -> int:
    """Run every registered pre-commit guard through the shared MX checkpoint.

    Returns the first grounding guard's exit code, or 0 when every guard either
    passed or resolved to advisory under an open hangar marker.

    A demoted finding is ANNOUNCED, never discarded. Collecting findings and
    dropping them with nothing said is the complaint recorded on GHI #843
    itself: an operator otherwise cannot tell a clean run from a hangar run.
    """
    module = sys.modules[__name__]
    for guard_name, attr, emitted_level in _GUARD_META:
        rc = getattr(module, attr)(root)
        if not rc:
            continue
        if _guard_grounds(guard_name, emitted_level, root):
            return rc
        from gzkit.mx import checkpoint  # noqa: PLC0415

        _safe_print(checkpoint.demote_notice(guard_name))
    return 0


def main() -> int:
    """Entry point for command-line usage."""
    return run_guards(Path.cwd())


if __name__ == "__main__":
    raise SystemExit(main())
