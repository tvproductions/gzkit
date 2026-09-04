#!/usr/bin/env python
"""Tier every `gz validate` scope by what invokes it, and ratchet the ungated set.

Passes A/B/C of the control-surface family all ask about **content
relationships** — rule vs rule, skill vs rule, rule prose vs check semantics.
None asks whether a check *runs*. A validator can cover its rule's prose
exactly (Pass C green) and be cited by the right skill (Pass B green) and still
execute on no commit path, in which case it protects nothing.

Established 2026-08-15. The ungated count is NOT restated here — read it from
``data/validator_reachability_grandfather.json`` or run ``--report``; a figure
copied into prose is a derived view pretending to be canon (Architectural
Boundary 6), and this file's whole job is to stop that. What is durable: every
failing scope found by that session's sweep was in the ungated set, so
``gz check`` was green while they failed, and two of them were regressions
introduced by the fix for the previous defect (GHI #704, #705).

Tiers
-----
A  gated       — in the `gz check` registry, or invoked by a hook / CI / pre-commit
B  test-only   — referenced only from `tests/**` or `features/**`
C  doc-only    — named in docs or skills, invoked by nothing
D  orphan      — no caller anywhere

Tier B is an upper bound, not a coverage figure: all three 2026-08-15 failures
were Tier B, which means those tests exercise their validator against fixtures
rather than against this repository. The test passes, the repo is dirty, and
nobody is told.

Exit codes follow the CLI doctrine 4-code map: 0 clean, 1 user/config error,
2 system/IO error, 3 policy breach (the ungated set grew).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

#: Flags that are presentation or mutation, never a check to be reached.
#: Value-taking flags are derived from the parser rather than listed here, so a
#: new `--scope VALUE` needs no edit to this file; these six cannot be derived
#: because they are `store_true` like every real scope.
_NON_SCOPE_FLAGS = frozenset(
    {
        "--json",
        "--quiet",
        "--verbose",
        "--debug",  # presentation
        "--regenerate",
        "--recalibrate",  # mutate state; running them is not an audit
    }
)

#: Caller classes that constitute *gating* — the scope runs without anyone
#: choosing to run it.
_GATING = frozenset({"HOOK", "CI", "PRECOMMIT"})

_CHECK_REGISTRY_RE = re.compile(r'"([a-z][a-z0-9-]+)",\s*_mx_levels')
#: One invocation may gate several scopes — `.pre-commit-config.yaml:68` runs
#: `gz validate --bullet-retention --surface-weight --pointer-anchors`. Capturing
#: only the first flag mis-tiered the other two as doc-only, understating the
#: gated set by two and overstating the ratchet by the same. Consume the whole
#: run of flags, then split.
_INVOCATION_RE = re.compile(r"gz validate((?:\s+--[a-z0-9-]+)+)")
_FLAG_RE = re.compile(r"--[a-z0-9-]+")

_SKIP_DIRS = frozenset({".git", "__pycache__", ".venv", "node_modules", "dist", "build"})

#: This chore's own surfaces are excluded from the caller scan, in BOTH the
#: canonical and wheel-shipped copies. Its CHORE.md, README and this module all
#: quote `gz validate --…` strings as examples, and counting them would tier a
#: scope mentioned only here as C (doc-only) rather than D (orphan) — the
#: instrument hiding the exact finding it exists to surface.
_SELF_DIRS = (
    ".gzkit/chores/control-surface-validator-reachability",
    "src/gzkit/chores/control-surface-validator-reachability",
)


#: Audit SUBJECT, not a resource path (GHI #938). `.github/workflows/` is a
#: CLASSIFIER PREDICATE in `_classify_path` below: it decides that a caller
#: found at that prefix is class CI. The scan is handed paths; it does not
#: resolve this one to read anything.
_AUDIT_SUBJECT_LITERALS: tuple[str, ...] = (".github/workflows/",)


def _classify_path(rel: str) -> str:
    """Map a repo-relative path to the caller class it represents."""
    if rel.startswith(".claude/hooks/"):
        return "HOOK"
    if rel.startswith(".github/workflows/"):
        return "CI"
    if rel.startswith(".pre-commit"):
        return "PRECOMMIT"
    if rel.startswith(("tests/", "features/")):
        return "TEST"
    if rel.startswith("src/"):
        return "SRC"
    if rel.startswith("docs/"):
        return "DOC"
    return "OTHER"


def runnable_scopes() -> list[str]:
    """Every `gz validate` flag that names a check and can be run bare.

    Derived from the live parser, never a hardcoded roster: a scope registered
    tomorrow is covered without editing this chore. `--evaluation-justify-binding`
    survives the value-taking filter because its argument is optional (`nargs="?"`),
    so it runs bare like any other scope.
    """
    from gzkit.cli.main import _build_parser  # noqa: PLC0415

    parser = _build_parser()
    validate = None
    for action in parser._actions:
        # `isinstance` rather than a truthiness test: `choices` is `object` on
        # the base Action, and `in` against it is not a supported operation.
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and "validate" in choices:
            validate = choices["validate"]
            break
    if validate is None:
        msg = "validate subparser not found — CLI shape changed"
        raise SystemExit(msg)

    scopes: list[str] = []
    for action in validate._actions:
        if not action.option_strings:
            continue
        flag = action.option_strings[0]
        if flag in _NON_SCOPE_FLAGS or flag == "--help":
            continue
        kind = action.__class__.__name__
        if kind == "_StoreTrueAction" or (kind == "_StoreAction" and action.nargs == "?"):
            scopes.append(flag)
    return sorted(set(scopes))


def check_registry_members(root: Path) -> set[str]:
    """Scope stems wired into the `gz check` step registry."""
    quality = root / "src" / "gzkit" / "commands" / "quality.py"
    if not quality.is_file():
        return set()
    return set(_CHECK_REGISTRY_RE.findall(quality.read_text(encoding="utf-8", errors="replace")))


def _repo_files(root: Path) -> Iterator[Path]:
    """Yield repo CONTENT — tracked files plus untracked ones git does not ignore.

    Deliberately git's list rather than ``rglob("*")``. Every caller class this
    module tiers (hook, workflow, test, doc) is repo content by construction, so
    the two answers agree on what matters; where they differ is generated output,
    which can only add false callers.

    The difference is not marginal. Measured 2026-08-28 against this repo:
    ``rglob("*")`` returns **367,088 paths against 7,241 tracked files**, and
    **324,827** of them are extensionless entries under the gitignored
    ``.ruff_cache/``. The suffix filter below excludes ``.pyc/.png/.jpg/.gz/.zip``
    and nothing else, so every one of those was READ in full, searching for a
    string a ruff cache entry cannot contain -- ~36s of this hook's 42.7s, paid
    on every commit including a whitespace-only one (GHI #902).

    Naming ``.ruff_cache`` in :data:`_SKIP_DIRS` would fix that instance and
    leave the class open: the set already names six directories, every one of
    them gitignored, and the next tool to add a cache re-opens it. Asking git is
    the same question without a list to maintain.

    Falls back to the pruned walk when git cannot answer -- an export, a tarball,
    an adopter running the chore outside a repository -- so the scan degrades to
    slow rather than to empty. Silently scanning nothing is the false-green this
    ratchet exists to prevent.
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
        for path in root.rglob("*"):
            if path.is_file() and not any(
                part in _SKIP_DIRS for part in path.relative_to(root).parts
            ):
                yield path
        return
    for rel in proc.stdout.split("\0"):
        if rel:
            yield root / rel


def callers(root: Path) -> dict[str, set[str]]:
    """Map each `--flag` to the set of caller classes that invoke it."""
    found: dict[str, set[str]] = {}
    for path in _repo_files(root):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(p in _SKIP_DIRS for p in path.relative_to(root).parts):
            continue
        if rel.startswith(_SELF_DIRS):
            continue
        if path.suffix in {".pyc", ".png", ".jpg", ".gz", ".zip"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "gz validate --" not in text:
            continue
        cls = _classify_path(rel)
        for run in _INVOCATION_RE.findall(text):
            for flag in _FLAG_RE.findall(run):
                found.setdefault(flag, set()).add(cls)
    return found


def tier_of(flag: str, *, in_check: bool, caller_classes: set[str]) -> str:
    """Return the reachability tier for one scope."""
    if in_check or (caller_classes & _GATING):
        return "A"
    if "TEST" in caller_classes:
        return "B"
    if caller_classes:
        return "C"
    return "D"


def build_matrix(root: Path) -> dict[str, str]:
    """Return {flag: tier} for every runnable scope."""
    registry = check_registry_members(root)
    seen = callers(root)
    return {
        flag: tier_of(flag, in_check=flag[2:] in registry, caller_classes=seen.get(flag, set()))
        for flag in runnable_scopes()
    }


def ungated(matrix: dict[str, str]) -> list[str]:
    """Scopes that run on no commit, push, or CI path."""
    return sorted(f for f, t in matrix.items() if t != "A")


def _baseline_scopes(ratchet: dict[str, object]) -> set[str]:
    """Narrow the ratchet payload's scope list without suppressing the checker.

    `json.loads` yields `object`; a `# type: ignore` here would assert past that
    rather than handle it, and `.claude/rules/pythonic.md` forbids a bracketed
    marker carrying no `ty:`-prefixed code anyway. A malformed baseline reads as
    empty, which fails the ratchet closed rather than passing it vacuously.
    """
    raw = ratchet.get("ungated_scopes")
    return {str(x) for x in raw} if isinstance(raw, list) else set()


def _load_ratchet(root: Path) -> dict[str, object]:
    path = root / "data" / "validator_reachability_grandfather.json"
    if not path.is_file():
        msg = (
            f"Ratchet baseline missing at {path.relative_to(root).as_posix()}.\n"
            "  Why: the ungated set is shrink-only (ADR-0.0.73 Boundary Invariant #8); "
            "with no baseline on disk every new ungated scope is a silent bypass.\n"
            "  Next step: uv run python .gzkit/chores/control-surface-validator-reachability/"
            "check_reachability.py --report  # then commit the emitted baseline"
        )
        raise SystemExit(msg)
    return json.loads(path.read_text(encoding="utf-8"))


def enforce(root: Path) -> int:
    """Fail closed when the ungated set grows against its baseline."""
    matrix = build_matrix(root)
    current = set(ungated(matrix))
    ratchet = _load_ratchet(root)
    baseline = _baseline_scopes(ratchet)

    added = sorted(current - baseline)
    drained = sorted(baseline - current)

    if drained:
        print(f"drained {len(drained)} scope(s) since baseline: {', '.join(drained)}")
    if not added:
        print(f"ungated: {len(current)} (baseline {len(baseline)}) — ratchet holds")
        return 0

    print(
        f"POLICY BREACH: {len(added)} scope(s) entered the ungated set: {', '.join(added)}\n"
        "  Why: the ungated set is shrink-only. A validator reachable from nothing "
        "protects nothing — it reads as coverage while running on no commit path, "
        "which is how three failing scopes sat under a green `gz check` (2026-08-15).\n"
        "  Next step: wire the scope into the `gz check` registry "
        "(src/gzkit/commands/quality.py), a hook, or CI — or retire it. Only then "
        "re-baseline: --report --write.",
        file=sys.stderr,
    )
    return 3


def report(root: Path, *, write: bool) -> int:
    """Print the tier census; optionally re-baseline the ratchet (shrink only)."""
    matrix = build_matrix(root)
    counts = {t: sum(1 for v in matrix.values() if v == t) for t in "ABCD"}
    print(f"runnable scopes: {len(matrix)}")
    for tier, label in (("A", "gated"), ("B", "test-only"), ("C", "doc-only"), ("D", "orphan")):
        print(f"  {tier} {label:<10} {counts[tier]:>3}")
    current = ungated(matrix)
    print(f"ungated (B+C+D): {len(current)}")
    orphans = sorted(f for f, t in matrix.items() if t == "D")
    if orphans:
        print(f"orphans (delete candidates): {', '.join(orphans)}")

    if not write:
        return 0

    path = root / "data" / "validator_reachability_grandfather.json"
    prior = _baseline_scopes(_load_ratchet(root)) if path.is_file() else set(current)
    if set(current) - prior:
        print(
            "Refusing to re-baseline: the set grew. A ratchet that rewrites itself "
            "upward is not a ratchet.",
            file=sys.stderr,
        )
        return 3
    payload = {
        "schema_version": 1,
        "rationale": (
            "Shrink-only baseline of `gz validate` scopes reachable from no gz check step, "
            "hook, CI workflow, or pre-commit entry. An ungated validator reads as coverage "
            "and runs on no commit path. Drain by wiring the scope into a gate or retiring it; "
            "this list may only decrease."
        ),
        "ungated_scopes": current,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"re-baselined: {len(current)} ungated scope(s)")
    return 0


def sweep(root: Path) -> int:
    """Run every scope in its own process and report its OWN exit code.

    Individually is not a stylistic choice. Solo-only scopes refuse combination
    outright (GHI #704), and `--audits` was found broken precisely because it was
    run alone. Nothing is piped: a verifier's truth is its own exit status, never
    a downstream filter's (`.gzkit/rules/tests.md` § Verification exit-code
    integrity, enforced by the `verifier-pipe-gate.py` hook).

    Argv is a sequence and the interpreter is re-entered as `-m gzkit`, so the
    code under test is the working tree rather than whatever `gz` resolves to on
    PATH — the wheel-vs-tree trap `_qc_nc_entrypoints` documents.
    """
    matrix = build_matrix(root)
    failures: list[tuple[int, str, str]] = []
    for flag in sorted(matrix):
        proc = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "gzkit", "validate", flag],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if proc.returncode != 0:
            failures.append((proc.returncode, flag, matrix[flag]))

    print(f"swept {len(matrix)} scope(s); {len(failures)} non-zero")
    if not failures:
        return 0
    for code, flag, tier in failures:
        gate = "GATED" if tier == "A" else f"UNGATED (tier {tier})"
        print(f"  exit {code}  {flag}  [{gate}]")
    ungated_failures = [f for _, f, t in failures if t != "A"]
    if ungated_failures:
        print(
            f"\n{len(ungated_failures)} failing scope(s) run on no commit path, so "
            "`gz check` stays green while they fail — the headline finding is the "
            "gap, not the failure.",
            file=sys.stderr,
        )
    return 3


def self_test() -> int:
    """Deterministic tiering checks — no repo state, no network."""
    cases = [
        ("gz check membership wins", True, set(), "A"),
        ("a hook gates", False, {"HOOK"}, "A"),
        ("CI gates", False, {"CI"}, "A"),
        ("pre-commit gates", False, {"PRECOMMIT"}, "A"),
        ("tests alone are not a gate", False, {"TEST", "DOC"}, "B"),
        ("docs alone invoke nothing", False, {"DOC", "SRC"}, "C"),
        ("no caller is an orphan", False, set(), "D"),
    ]
    failures = [
        f"{name}: expected {want}, got {got}"
        for name, in_check, classes, want in cases
        if (got := tier_of("--x", in_check=in_check, caller_classes=classes)) != want
    ]
    # A scope named by a doc AND a hook is still gated — gating is not diluted
    # by co-occurrence, which is the bug a "first match wins" ordering would have.
    if tier_of("--x", in_check=False, caller_classes={"DOC", "HOOK"}) != "A":
        failures.append("gating must dominate co-occurring non-gating classes")

    # One invocation, several scopes — the real `.pre-commit-config.yaml` shape.
    # The first version of this scanner captured only the leading flag and
    # mis-tiered the trailing two as doc-only, which would have frozen them into
    # the ratchet as ungated when pre-commit gates them on every commit.
    line = "entry: uv run gz validate --bullet-retention --surface-weight --pointer-anchors"
    parsed = [f for run in _INVOCATION_RE.findall(line) for f in _FLAG_RE.findall(run)]
    if parsed != ["--bullet-retention", "--surface-weight", "--pointer-anchors"]:
        failures.append(f"multi-scope invocation must yield all three flags, got {parsed}")
    if failures:
        for f in failures:
            print(f"FAIL {f}", file=sys.stderr)
        return 1
    print(f"self-test: {len(cases) + 1} tiering assertions passed")
    return 0


def _mx_demoted(guard_name: str, root: Path) -> bool:
    """Return True when an open MX hangar demotes this guard to advisory.

    ADR-0.0.74 Boundary Invariant #2 -- every fail-closed funnel resolves its
    severity through the shared checkpoint. This chore runs as its own
    pre-commit entrypoint, so it consults the checkpoint itself rather than
    inheriting the seam in ``gzkit.hooks.guards`` (GHI #843).

    Fails CLOSED: a broken or half-repaired ``gzkit.mx`` is precisely the state
    MX mode exists to survive, so anything unresolvable blocks rather than
    demotes.
    """
    try:
        from gzkit.mx import checkpoint, levels

        return not checkpoint.blocks(guard_name, levels.ERROR, root)
    except Exception:  # noqa: BLE001 - an unreadable checkpoint must never demote a guard
        return False


def _mx_notice(guard_name: str) -> str:
    """Return the shared operator-facing demotion line, or a local fallback."""
    try:
        from gzkit.mx import checkpoint

        return checkpoint.demote_notice(guard_name)
    except Exception:  # noqa: BLE001 - never crash a hook over its own advisory text
        return f"[MX advisory] guard '{guard_name}' demoted by the open MX hangar marker."


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--self-test", action="store_true", help="Run tiering assertions and exit")
    mode.add_argument("--report", action="store_true", help="Print the tier census")
    mode.add_argument("--sweep", action="store_true", help="Run every scope individually")
    parser.add_argument(
        "--write", action="store_true", help="With --report: re-baseline (shrink only)"
    )
    args = parser.parse_args(argv)

    # `Path.cwd()` rather than a positional walk from `__file__` — see the
    # sibling ledger chore for why. Assigning `Path(__file__).resolve()` to a
    # variable first evaded `gz check`'s parents-lint AST match; that was the
    # checker missing it, never this script complying.
    root = Path.cwd()
    if not (root / "pyproject.toml").is_file():
        print("not at a project root (run from the repository root)", file=sys.stderr)
        return 2

    if args.self_test:
        return self_test()
    if args.report:
        return report(root, write=args.write)
    if args.sweep:
        return sweep(root)
    rc = enforce(root)
    if rc and _mx_demoted("validator-reachability", root):
        print(_mx_notice("validator-reachability"), file=sys.stderr)
        return 0
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
