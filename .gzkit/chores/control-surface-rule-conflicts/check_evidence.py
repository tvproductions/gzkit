"""Acceptance gate for the control-surface-rule-conflicts chore.

Enforces the audit-row schema declared in
ADR-pool.control-surface-rule-pair-conflict-audit § Audit-row schema.
A conflict-matrix.md that is empty, missing the Evidence/Severity columns,
or carries rows whose Evidence cell does not resolve via
`gh issue view <N>`, `git log -1 <SHA>`, or
`grep <id> .gzkit/insights/agent-insights.jsonl`
fails this check. Authored under GHI #448.

Resolution semantics:
  - SHA references resolve via `git log -1 <SHA>` (local, binding).
  - Insight tokens resolve via grep against `.gzkit/insights/agent-insights.jsonl`
    (local, binding).
  - GHI references resolve via `gh issue view <N>` when `gh` is authenticated;
    otherwise a shape-only fallback accepts any well-formed number within the
    plausible-range floor (`MAX_PLAUSIBLE_GHI`). The fallback documents the
    chores-lite "no network" doctrine without silently weakening the GHI's
    prescription.

Modes:
  default       Validate .gzkit/chores/control-surface-rule-conflicts/proofs/conflict-matrix.md
  --self-test   Validate parser semantics against embedded fixtures
                (deterministic, no I/O — what acceptance.json invokes)

Exit codes:
  0  matrix valid
  1  matrix invalid (empty, schema drift, unresolvable evidence)
  2  parser/self-test regression
  3  configuration error (missing matrix file, bad arguments)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # ty: ignore[call-non-callable]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")  # ty: ignore[call-non-callable]


DEFAULT_MATRIX_PATH = Path(".gzkit/chores/control-surface-rule-conflicts/proofs/conflict-matrix.md")
INSIGHTS_PATH = Path(".gzkit/insights/agent-insights.jsonl")
MAX_PLAUSIBLE_GHI = 9_999

REQUIRED_COLUMN_TOKENS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("rule_a", ("rule a",)),
    ("rule_b", ("rule b",)),
    ("worked_example", ("worked example", "example")),
    ("evidence", ("evidence",)),
    ("winner", ("winner", "wins")),
    ("resolution", ("resolution",)),
    ("severity", ("severity",)),
)


class Ref(NamedTuple):
    """Single evidence reference extracted from a matrix cell."""

    kind: str  # "ghi" | "sha" | "insight"
    value: str


class Table(NamedTuple):
    """Parsed markdown table from the conflict matrix.

    ``malformed`` carries rows the parser could not read as data (cell count
    disagreeing with the header). They are reported rather than skipped: a
    truncated parse that validates clean is indistinguishable from a healthy
    one, which is the failure this field exists to make loud.
    """

    headers: list[str]
    rows: list[list[str]]
    malformed: list[str] = []


class ValidationResult(NamedTuple):
    """Outcome of validating a conflict-matrix.md document."""

    exit_code: int
    messages: list[str]


_GHI_RE = re.compile(r"#(\d{1,5})\b")
_SHA_RE = re.compile(r"\b([0-9a-f]{7,40})\b")
_INSIGHT_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{3,}-\d{4}-\d{2}-\d{2}")


def _split_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c) for c in cells)


def parse_table(text: str) -> Table | None:
    """Return the first markdown table in ``text`` or None when absent."""
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if "|" not in line or idx + 1 >= len(lines):
            continue
        header = _split_row(line)
        separator = _split_row(lines[idx + 1])
        if not _is_separator(separator) or len(header) != len(separator):
            continue
        rows: list[list[str]] = []
        malformed: list[str] = []
        for offset, row_line in enumerate(lines[idx + 2 :], start=idx + 3):
            if "|" not in row_line or not row_line.strip().startswith("|"):
                break
            cells = _split_row(row_line)
            if _is_separator(cells):
                continue
            if len(cells) != len(header):
                # Do NOT break: a silent truncation here yields a partial table
                # that validates clean, so a 25-row matrix reports "8 rows, all
                # evidence resolves". Record and keep reading.
                malformed.append(
                    f"line {offset}: {len(cells)} cells, header has {len(header)} "
                    f"(unescaped `|` in a cell? use `&#124;`)"
                )
                continue
            rows.append(cells)
        return Table(headers=header, rows=rows, malformed=malformed)
    return None


def validate_header(headers: list[str]) -> list[str]:
    """Return list of missing-column messages for ``headers``."""
    issues: list[str] = []
    lowered = [h.lower() for h in headers]
    for column, tokens in REQUIRED_COLUMN_TOKENS:
        if not any(any(tok in h for tok in tokens) for h in lowered):
            issues.append(f"header missing required column: {column} (any of {tokens!r})")
    return issues


def _find_column_index(headers: list[str], tokens: tuple[str, ...]) -> int | None:
    for idx, header in enumerate(headers):
        lowered = header.lower()
        if any(tok in lowered for tok in tokens):
            return idx
    return None


def extract_refs(cell: str) -> list[Ref]:
    """Extract GHI numbers, SHAs, and insight-id tokens from ``cell``."""
    if not cell or not cell.strip():
        return []
    refs: list[Ref] = []
    seen: set[tuple[str, str]] = set()
    for match in _GHI_RE.finditer(cell):
        key = ("ghi", match.group(1))
        if key not in seen:
            seen.add(key)
            refs.append(Ref(kind="ghi", value=match.group(1)))
    for match in _SHA_RE.finditer(cell):
        if match.group(1) in {r.value for r in refs}:
            continue
        key = ("sha", match.group(1))
        if key not in seen:
            seen.add(key)
            refs.append(Ref(kind="sha", value=match.group(1)))
    for match in _INSIGHT_RE.finditer(cell):
        token = match.group(0)
        key = ("insight", token)
        if key not in seen:
            seen.add(key)
            refs.append(Ref(kind="insight", value=token))
    return refs


def _git_log_resolves(sha: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", sha],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _gh_issue_resolves(number: str) -> bool:
    try:
        result = subprocess.run(
            ["gh", "issue", "view", number, "--json", "number"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _insight_grep_resolves(token: str) -> bool:
    if not INSIGHTS_PATH.exists():
        return False
    try:
        text = INSIGHTS_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return token in text


def resolve_ref(ref: Ref, *, gh_authenticated: bool) -> bool:
    """Return True when ``ref`` resolves under the ADR's audit-row schema."""
    if ref.kind == "sha":
        return _git_log_resolves(ref.value)
    if ref.kind == "insight":
        return _insight_grep_resolves(ref.value)
    if ref.kind == "ghi":
        if gh_authenticated:
            return _gh_issue_resolves(ref.value)
        try:
            number = int(ref.value)
        except ValueError:
            return False
        return 1 <= number <= MAX_PLAUSIBLE_GHI
    return False


def _gh_authenticated() -> bool:
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def validate_matrix_text(
    text: str,
    *,
    gh_authenticated: bool,
) -> ValidationResult:
    """Validate the conflict-matrix.md document text."""
    messages: list[str] = []
    if not text.strip():
        return ValidationResult(exit_code=1, messages=["matrix is empty"])
    table = parse_table(text)
    if table is None:
        return ValidationResult(exit_code=1, messages=["no markdown table found in matrix"])
    header_issues = validate_header(table.headers)
    if header_issues:
        return ValidationResult(exit_code=1, messages=header_issues)
    if table.malformed:
        return ValidationResult(
            exit_code=1,
            messages=[
                "matrix has unparseable rows — validating the remainder would "
                "report a clean partial read:",
                *table.malformed,
            ],
        )
    if not table.rows:
        return ValidationResult(
            exit_code=1,
            messages=["matrix has zero data rows; observed-hit evidence required"],
        )
    evidence_idx = _find_column_index(table.headers, ("evidence",))
    severity_idx = _find_column_index(table.headers, ("severity",))
    assert evidence_idx is not None and severity_idx is not None
    for row_num, row in enumerate(table.rows, start=1):
        evidence_cell = row[evidence_idx]
        severity_cell = row[severity_idx]
        if not evidence_cell.strip():
            messages.append(f"row {row_num}: evidence cell is empty")
            continue
        if not severity_cell.strip():
            messages.append(f"row {row_num}: severity cell is empty")
        refs = extract_refs(evidence_cell)
        if not refs:
            messages.append(f"row {row_num}: evidence cell has no GHI/SHA/insight reference")
            continue
        if not any(resolve_ref(ref, gh_authenticated=gh_authenticated) for ref in refs):
            messages.append(
                f"row {row_num}: evidence cell carries no resolvable reference "
                f"(tried {len(refs)} ref(s))"
            )
    if messages:
        return ValidationResult(exit_code=1, messages=messages)
    return ValidationResult(
        exit_code=0,
        messages=[f"matrix valid: {len(table.rows)} row(s), all evidence resolves"],
    )


_FIXTURE_HEADER = (
    "| # | Rule A + § | Rule B + § | Worked Example | Evidence "
    "| Mechanical Winner | Suggested Resolution | Severity |\n"
    "|---|------------|------------|----------------|----------"
    "|-------------------|----------------------|----------|\n"
)


def _fixture_matrix(rows: str) -> str:
    return "# Conflict Matrix\n\n" + _FIXTURE_HEADER + rows


# A row carrying an unescaped `|` inside a cell: 9 cells against an 8-cell header.
_MALFORMED_ROW = (
    '| 2 | `a.md` § A — *"one | two"* | `b.md` § B | Worked | GHI #1 | a.md '
    "| reconcile-in-A | blocking |\n"
)

_VALID_ROW = (
    "| 1 | `tests.md` § A | `arb.md` § B | Worked | GHI #1 | tests.md "
    "| reconcile-in-A | blocking |\n"
)
_EMPTY_EVIDENCE_ROW = (
    "| 1 | `tests.md` § A | `arb.md` § B | Worked |  | tests.md | reconcile-in-A | blocking |\n"
)
_NO_REF_ROW = (
    "| 1 | `tests.md` § A | `arb.md` § B | Worked | none | tests.md | reconcile-in-A | blocking |\n"
)


def run_self_test() -> int:
    """Run embedded fixtures and return non-zero on any regression."""
    errors: list[str] = []
    ran: list[str] = []

    def expect(label: str, result: ValidationResult, want_zero: bool) -> None:
        ran.append(label)
        ok = (result.exit_code == 0) if want_zero else (result.exit_code != 0)
        if not ok:
            errors.append(
                f"FIXTURE FAILURE [{label}]: exit_code={result.exit_code} "
                f"messages={result.messages}"
            )

    expect("empty", validate_matrix_text("", gh_authenticated=False), want_zero=False)
    expect(
        "no_table",
        validate_matrix_text("# heading\n\nprose\n", gh_authenticated=False),
        want_zero=False,
    )
    expect(
        "missing_evidence_column",
        validate_matrix_text(
            "# x\n\n| Rule A | Rule B | Example | Winner | Resolution | Severity |\n"
            "|---|---|---|---|---|---|\n"
            "| a | b | c | d | e | blocking |\n",
            gh_authenticated=False,
        ),
        want_zero=False,
    )
    expect(
        "zero_rows",
        validate_matrix_text(_fixture_matrix(""), gh_authenticated=False),
        want_zero=False,
    )
    expect(
        "empty_evidence_cell",
        validate_matrix_text(_fixture_matrix(_EMPTY_EVIDENCE_ROW), gh_authenticated=False),
        want_zero=False,
    )
    # Regression: a row with an unescaped `|` used to `break` the parser, so the
    # remainder went unread and the partial table validated clean — a 25-row
    # matrix reported "8 rows, all evidence resolves". Truncation must fail loud.
    expect(
        "malformed_row_does_not_truncate_silently",
        validate_matrix_text(_fixture_matrix(_VALID_ROW + _MALFORMED_ROW), gh_authenticated=False),
        want_zero=False,
    )
    expect(
        "evidence_with_no_refs",
        validate_matrix_text(_fixture_matrix(_NO_REF_ROW), gh_authenticated=False),
        want_zero=False,
    )
    expect(
        "valid_ghi_ref",
        validate_matrix_text(_fixture_matrix(_VALID_ROW), gh_authenticated=False),
        want_zero=True,
    )

    parser_checks = [
        (parse_table("") is None, "parse_table('')"),
        (parse_table("# x") is None, "parse_table('# x')"),
        (
            extract_refs("GHI #195 and 5e8174ba") != [],
            "extract_refs sees GHI + SHA",
        ),
    ]
    for ok, label in parser_checks:
        if not ok:
            errors.append(f"PARSER FAILURE [{label}]")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 2
    # Counts are derived, never literals: a hardcoded tally silently stops
    # tracking the fixtures it claims to describe the moment one is added.
    print(f"OK ({len(ran)} matrix fixtures + {len(parser_checks)} parser checks)")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entrypoint for the chore-acceptance evidence gate."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=DEFAULT_MATRIX_PATH,
        help="Path to conflict-matrix.md (default: project-local proofs/)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run embedded fixtures only (deterministic; no filesystem dependency)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force shape-only GHI resolution (skip `gh issue view`)",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if not args.matrix.exists():
        print(f"error: matrix not found at {args.matrix}", file=sys.stderr)
        return 3
    try:
        text = args.matrix.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read {args.matrix}: {exc}", file=sys.stderr)
        return 3

    gh_authenticated = False if args.offline else _gh_authenticated()
    result = validate_matrix_text(text, gh_authenticated=gh_authenticated)
    stream = sys.stdout if result.exit_code == 0 else sys.stderr
    for message in result.messages:
        print(message, file=stream)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
