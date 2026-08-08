"""Release-discipline trust audits.

* ``audit_version_release`` — every ``pyproject.toml`` version bump must
  have a matching ``vX.Y.Z`` git tag (or a ``docs/releases/{PATCH,RELEASE}-vX.Y.Z.md``
  manifest in flight). GHI #205 / GHI #217 / GHI #739.
* ``audit_advisory_scorecard`` — every rule under ``.gzkit/rules/`` must be
  scored in ``docs/governance/advisory-rules-audit.md`` *at its current
  rule-version*, so the scorecard remains a complete index. GHI #212, GHI #754.
  The same scope also fences the Summary roll-up against the rows it summarizes,
  so the transcribed counts cannot drift from the scorecard they describe.
"""

from __future__ import annotations

import json
import re
import tomllib
from collections import Counter
from pathlib import Path

from gzkit.validate import ValidationError
from gzkit.validators.rule_version_markers import canonical_rule_files, rule_version_of

#: Filename prefixes accepted as in-flight release evidence (GHI #217, GHI #739).
#: ``PATCH-`` is written by ``gz patch release``; ``RELEASE-`` by ``gz closeout``,
#: whose bumps are minor. Both denote the same window — between the bump commit
#: and ``gh release create`` — so both are equivalent evidence. The prefix names
#: the ceremony that bumped, never a different kind of proof.
IN_FLIGHT_MANIFEST_PREFIXES: tuple[str, ...] = ("PATCH", "RELEASE")


def in_flight_manifest_path(project_root: Path, version: str, prefix: str = "RELEASE") -> Path:
    """Return the manifest path a bump of *version* must file to stay syncable.

    Single source for the path contract shared by the writers
    (``gz patch release``, ``gz closeout``) and the audit that reads it.
    """
    return project_root / "docs" / "releases" / f"{prefix}-v{version}.md"


def audit_version_release(project_root: Path) -> list[ValidationError]:
    """Fail if ``pyproject.toml`` version has no matching ``vX.Y.Z`` git tag.

    Every version bump is a release (CLAUDE.md local rule 11). This audit
    compares the declared pyproject version against the local git-tag set;
    if the bump landed without a tag, the release step was skipped.

    Per GHI #217, the audit also accepts an in-flight release manifest under
    ``docs/releases/`` as equivalent evidence, written before the bump commit
    is attempted, so it satisfies the audit during the brief window between
    the commit and ``gh release create`` (which creates the tag).

    Per GHI #739 the lookup accepts both ``IN_FLIGHT_MANIFEST_PREFIXES``.
    ``PATCH-`` alone was hardcoded here, which had two consequences: minor
    releases from ``gz closeout`` had to file an artifact mislabelled as a
    patch (``PATCH-v0.30.0.md``, ``PATCH-v0.34.0.md``), and because
    ``gz closeout`` wrote no manifest at all, its bump made ``gz test`` red
    while the ceremony's own Step 10 ran that gate before creating the tag —
    a deadlock on every minor release.
    """
    import subprocess  # noqa: PLC0415

    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        return []
    version = _read_pyproject_version(pyproject)
    if version is None:
        return []
    expected = f"v{version}"
    if any(
        in_flight_manifest_path(project_root, version, prefix).is_file()
        for prefix in IN_FLIGHT_MANIFEST_PREFIXES
    ):
        return []
    try:
        result = subprocess.run(
            ["git", "tag", "--list", "v*"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            errors="replace",
            encoding="utf-8",
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    tags = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    if expected in tags:
        return []
    return [
        ValidationError(
            type="version_release",
            artifact=f"pyproject.toml::version={version}",
            message=(
                f"Declared version `{version}` has no matching git tag `{expected}`. "
                "Every version bump is a release (CLAUDE.md local rule 11) — "
                f"create one via `gh release create {expected} --target main "
                f'--title "{expected}" --latest --notes "..."`.'
            ),
        )
    ]


def _read_pyproject_version(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("version"):
            continue
        match = re.match(r'version\s*=\s*"([^"]+)"', stripped)
        if match:
            return match.group(1)
    return None


#: The scorecard's per-rule review ledger: ``| `<file>.md` | `X.Y.Z` |``.
#: Version equality against the rule's own ``<!-- rule-version: -->`` marker is
#: the whole check — deliberately not a prose or clause-shape heuristic. A
#: heuristic clause extractor would itself grade by shape, reintroducing the
#: ``shape-graded-not-substance`` theater signature this audit exists to close
#: (ADR-0.0.73; ``theater_signature_scan`` § "Deliberately NOT detected").
_LEDGER_ROW_RE = re.compile(
    r"^\|\s*`(?P<file>[^`]+\.md)`\s*\|\s*`(?P<version>\d+\.\d+\.\d+)`\s*\|",
    re.MULTILINE,
)

_SCORECARD_REL = "docs/governance/advisory-rules-audit.md"
_SCORES = "Mechanical / Promotable / Judgment / Ambiguous"
_GRANDFATHER_REL = Path("data") / "advisory_scorecard_grandfather.json"

#: The four scores a rule row may carry. A row may name *two* — row 65 scores
#: changelog structure ``**Mechanical**`` and release-notes curation
#: ``**Judgment**`` — in which case it counts toward both. Splitting is the
#: honest reading of a rule whose halves genuinely score differently; the
#: consequence is that the four counts sum above the row total, which the
#: Summary table states rather than hides.
_SCORE_NAMES: tuple[str, ...] = ("Mechanical", "Promotable", "Judgment", "Ambiguous")

#: A scored rule row: ``| 23 | no lazy imports | **Promotable** | ... |``. The
#: id may carry a letter suffix (``6a``, ``45a``, ``60a``).
_SCORED_ROW_RE = re.compile(r"^\|\s*\d+[a-z]?\s*\|", re.MULTILINE)

#: A cell boundary — a pipe the row author did **not** escape. Rows 22, 27 and
#: 52 carry ``\|`` inside a code span (``` `str \| None` ```), and a naive
#: ``line.split("|")`` reads those as column breaks, shifting the Score cell
#: rightward and silently dropping all three from the count. That is a
#: three-row undercount that looks exactly like a correct answer.
_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")

#: A Summary roll-up row: ``| **Promotable** | 9 | 10% |``. Requiring the count
#: cell to be a bare integer is what separates a roll-up row from the legend row
#: (``| **Promotable** | Could become mechanical; ... |``) without the regex
#: needing to know where either table sits in the document.
_SUMMARY_ROW_RE = re.compile(
    r"^\|\s*\*\*(?P<score>" + "|".join(_SCORE_NAMES) + r")\*\*\s*\|\s*(?P<count>\d+)\s*\|",
    re.MULTILINE,
)


def _scorecard_coverage_ledger(scorecard_text: str) -> dict[str, str]:
    """Return ``{rule filename: scored-at rule-version}`` from the scorecard."""
    return {m.group("file"): m.group("version") for m in _LEDGER_ROW_RE.finditer(scorecard_text)}


def _scorecard_section(scorecard_text: str) -> str:
    """Return the ``## Scorecard`` body only, stopping at the next H2.

    Slicing is load-bearing: ``## Recommended promotion order`` is *also* a
    numbered table, so a document-wide row scan counts its 20 rows as scored
    rules and inflates every total.
    """
    marker = "\n## Scorecard\n"
    start = scorecard_text.find(marker)
    if start < 0:
        return ""
    rest = scorecard_text[start + len(marker) :]
    end = rest.find("\n## ")
    return rest if end < 0 else rest[:end]


def _scorecard_row_scores(scorecard_text: str) -> Counter[str]:
    """Count scored rule rows per score, reading only the Score column.

    Reading the Score cell rather than the whole line is what makes this a
    truth check instead of an existence check: row 53's *Notes* recount that it
    "Scored **Promotable** until ``0.4.0``" while scoring **Mechanical** today,
    and row 60a's notes argue against a **Promotable** score it does not carry.
    A substring scan over the line counts both as Promotable — which is exactly
    how the 2026-08-08 measurement reported two ``Ambiguous`` rules that do not
    exist, having counted the legend row and the Summary row as rules.
    """
    counts: Counter[str] = Counter()
    for line in _scorecard_section(scorecard_text).splitlines():
        if not _SCORED_ROW_RE.match(line):
            continue
        cells = _CELL_SPLIT_RE.split(line)
        if len(cells) < 4:
            continue
        for name in _SCORE_NAMES:
            if f"**{name}**" in cells[3]:
                counts[name] += 1
    return counts


def _scorecard_summary_counts(scorecard_text: str) -> dict[str, int]:
    """Return ``{score: transcribed count}`` from the Summary roll-up table."""
    matches = _SUMMARY_ROW_RE.finditer(scorecard_text)
    return {m.group("score"): int(m.group("count")) for m in matches}


def _summary_drift_errors(scorecard_text: str) -> list[ValidationError]:
    """Fail when the Summary roll-up disagrees with the rows it summarizes.

    A scorecard with no Summary table is clean by construction — there is no
    transcribed count to be wrong. The check fences a claim that was made, and
    never demands the claim be made.
    """
    summary = _scorecard_summary_counts(scorecard_text)
    if not summary:
        return []
    measured = _scorecard_row_scores(scorecard_text)
    drifted = sorted(name for name, claimed in summary.items() if claimed != measured[name])
    if not drifted:
        return []
    detail = "; ".join(
        f"{name} says {summary[name]}, rows show {measured[name]}" for name in drifted
    )
    return [
        ValidationError(
            type="advisory_scorecard",
            artifact=_SCORECARD_REL,
            message=(
                f"The Summary roll-up disagrees with the scored rows beneath it — {detail}. "
                "A hand-maintained count inside the document it summarizes is a derived view "
                "with no regenerator (Architectural Boundary 6 — do not let derived views "
                "silently become source-of-truth), and the Promotable/Ambiguous figures are "
                "the completion criterion of the Movement C family-closure box, so a wrong "
                "count retargets real work. Recount the Score column of "
                f"`{_SCORECARD_REL}` § Scorecard and correct the Summary table — or delete "
                "the roll-up, which is a valid disposition, rather than restate it by hand."
            ),
        )
    ]


#: A ruff diagnostic code as it appears in prose: ``BLE001``, ``PLC0415``, ``F401``.
#: The shape is shared with markdownlint (``MD013``) and others, which is why
#: extraction is anchored on the row naming ruff — see
#: :func:`_unreachable_ruff_claim_errors`.
_RUFF_CODE_RE = re.compile(r"\b([A-Z]{1,4}\d{3,4})\b")


def _ruff_selection(project_root: Path) -> tuple[list[str], list[str]] | None:
    """Return ``(select, ignore)`` from ``[tool.ruff.lint]``, or None if unreadable.

    None means "no answer available", never "clean": with no parseable config
    there is no configuration for a row's claim to disagree with, so the caller
    reports nothing rather than inventing a verdict from a default it guessed.
    """
    path = project_root / "pyproject.toml"
    if not path.is_file():
        return None
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError, UnicodeDecodeError):
        return None
    lint = payload.get("tool", {}).get("ruff", {}).get("lint", {})
    select = lint.get("select")
    if not isinstance(select, list):
        return None
    ignore = lint.get("ignore", [])
    return (
        [s for s in select if isinstance(s, str)],
        [i for i in ignore if isinstance(i, str)] if isinstance(ignore, list) else [],
    )


def _ruff_code_is_reachable(code: str, select: list[str], ignore: list[str]) -> bool:
    """Report whether ruff runs *code*: some ``select`` prefixes it, no ``ignore`` does.

    Reachability is the *conjunction*. Reading ``select`` alone would pass a code
    whose family is selected while the code itself is switched off one table
    down — the same report-green-while-blind state row 18 was in, reached from
    the other direction.
    """
    if any(code.startswith(entry) for entry in ignore):
        return False
    return any(entry == "ALL" or code.startswith(entry) for entry in select)


def _unreachable_ruff_claim_errors(
    scorecard_text: str, project_root: Path
) -> list[ValidationError]:
    """Fail when a **Mechanical** row cites a ruff code ruff would not run.

    **A false Mechanical row is strictly worse than a Promotable one, and the
    Movement C family-closure criterion counts only the latter.** Promotable is
    honest — it says no witness yet. A Mechanical row naming a lint rule that is
    not enabled reports green while blind, and is invisible to the criterion, so
    driving Promotable to zero leaves every false row untouched while making the
    number look better. Four such rows shipped: rows 18 and 23 named ruff families
    (``BLE``, ``PL``) absent from ``select``, so both ran nowhere — six live blind
    excepts sat unreported, one behind a ``# noqa: BLE0001`` typo that suppressed
    nothing and *could not be noticed while the rule was off*.

    All six wrong rows found in that pass were found by opening the enforcement
    surface by hand. Nothing compared a row's claim against the thing it named;
    this is the narrow, mechanically decidable arm of that gap.

    Two boundaries keep it a truth check rather than a keyword scan:

    * **The score gates it.** Only a **Mechanical** row is asserting enforcement.
      A **Judgment** row naming a disabled code is *disclosing* it — exactly what
      ``.gzkit/rules/pythonic.md`` § Imports does with PLC0415's 138 measured
      violations — and flagging that would punish the disclosure this family
      exists to produce.
    * **The ruff anchor gates extraction.** The bare code shape is shared with
      markdownlint and pydocstyle, so a row is read for codes only when it names
      ruff at all. An unanchored scan would invent findings against tools
      configured elsewhere.

    Two limits, stated so a green is not read as total:

    * **Reachability is not existence.** ``BLE0001`` (the typo row 18 carried) is
      reachable under ``select = ["BLE"]`` because the prefix matches, so this
      check would pass it. Proving a code *exists* means asking ruff, which is a
      subprocess this validator does not own.
    * **A Mechanical row cannot narrate a disabled code by its bare token.** The
      check reads every code in the row and cannot tell a witness citation from a
      disclaimer, so "we also considered X, which is off" reads as a false claim.
      That constraint is accepted rather than worked around: a Mechanical row's
      job is to name its witness, and commentary about non-witnesses belongs in
      the rule's own text or in a Judgment row. Name the ruff *rule* instead of
      the code when narrating one — row 44 does, and it is the clearer prose.
    """
    selection = _ruff_selection(project_root)
    if selection is None:
        return []
    select, ignore = selection
    errors: list[ValidationError] = []
    for line in _scorecard_section(scorecard_text).splitlines():
        if not _SCORED_ROW_RE.match(line):
            continue
        cells = _CELL_SPLIT_RE.split(line)
        if len(cells) < 5 or "**Mechanical**" not in cells[3]:
            continue
        claim = "|".join(cells[2:])
        if "ruff" not in claim.lower():
            continue
        cited = set(_RUFF_CODE_RE.findall(claim))
        unreachable = sorted(c for c in cited if not _ruff_code_is_reachable(c, select, ignore))
        if not unreachable:
            continue
        row_id = cells[1].strip()
        errors.append(
            ValidationError(
                type="advisory_scorecard",
                artifact=_SCORECARD_REL,
                message=(
                    f"Scorecard row {row_id} is scored **Mechanical** and cites ruff "
                    f"{', '.join(unreachable)}, which ruff would not run under the current "
                    "`tool.ruff.lint` configuration in `pyproject.toml` — no `select` entry "
                    "reaches the code, or an `ignore` entry switches it off. A Mechanical row "
                    "claims a fail-closed witness exists; when the named rule runs nowhere the "
                    "row reports green while blind, which is strictly worse than a Promotable "
                    "row that honestly says there is no witness yet (and invisible to the "
                    "family-closure criterion, which counts only Promotable). Either add the "
                    "code to the `select` list under `tool.ruff.lint` and fix the violations it "
                    f"surfaces, or re-score row {row_id} to the posture that is actually true "
                    f"and state it in the rule's own text — see `{_SCORECARD_REL}` row 18 for "
                    "the worked correction."
                ),
            )
        )
    return errors


#: A citation naming the specific clause a sentence is talking about:
#: ``Invariant #10a``, ``Invariants 2 and 3``, ``row 29``, ``rows 29/30``. Its
#: presence is what separates *assigning* a score to a named clause from
#: *explaining* what the score means.
_CLAUSE_CITATION_RE = re.compile(r"\b(?:Invariants?\s+#?\d+|rows?\s+\d+)", re.IGNORECASE)


def _prose_promotable_errors(scorecard_text: str) -> list[ValidationError]:
    """Fail when prose outside § Scorecard assigns **Promotable** to a named clause.

    The rules arm drove the Scorecard's Promotable column to zero, and
    :func:`_summary_drift_errors` fences the roll-up against those rows. Three
    prose sites survived both and still asserted a live Promotable band:

    * ``**Invariant #10a**`` ("When a skill step names a tool, invoke it in the
      same turn") was declared **promotable** with no scorecard row at all — a
      *skill* mandate sitting in the forbidden third state, invisible to the
      family-closure criterion precisely because it was never a row to count.
      The arm was reported "unmeasured" on the belief that skill mandates were
      uncovered; the audit covers them (rows 28–33, 52, 62b). What was actually
      missing was this one, hiding in prose outside the table.
    * "The remaining Promotable band (Invariants 2/3 of the tool-skill-runbook
      rule, lazy imports, …)" — rows 29, 30 and 23 all read **Judgment**.
    * "Invariants 2 and 3 … (rows 29/30 above) remain Promotable" — naming the
      very rows that contradict it.

    This is Architectural Boundary 6 one surface over from the Summary table: a
    second, unfenced authority on scores. Fencing the roll-up while leaving prose
    free to assign them would have moved the defect rather than closed it.

    Two boundaries, each load-bearing:

    * **A clause citation is required.** "A row returning to **Promotable** means
      a clause was found declaring a discipline with neither a witness nor an
      admission" explains what the score *means* and assigns it to nothing — it
      is the sentence that makes the empty third state legible, and a fence that
      cost it would trade the explanation for the enforcement.
    * **Scored ROWS are exempt — not the § Scorecard section.** Rows 53, 60a, 61
      and 62 each recount the Promotable score they used to carry and why it
      moved, which is how a reader tells a corrected row from one that was always
      right. Exempting the whole *section* instead would have missed the worst of
      the three sites: `**Invariant #10a**` sits inside § Scorecard as free prose
      between two subsections, which is precisely how a clause gets scored
      without ever becoming a row anyone counts.

    Scoped to **Promotable** on purpose: it is the third state the criterion
    counts. A Mechanical or Judgment narration (the promotion-wave paragraph
    cites a dozen) is history, not a live classification.
    """
    errors: list[ValidationError] = []
    for number, line in enumerate(scorecard_text.splitlines(), start=1):
        if "romotable" not in line or _SCORED_ROW_RE.match(line):
            continue
        citation = _CLAUSE_CITATION_RE.search(line)
        if citation is None:
            continue
        errors.append(
            ValidationError(
                type="advisory_scorecard",
                artifact=_SCORECARD_REL,
                message=(
                    f"Line {number} assigns **Promotable** to a named clause "
                    f"({citation.group(0)}) in prose outside the § Scorecard section. A "
                    "clause's score is assigned in a Scorecard ROW and nowhere else — prose "
                    "that scores a named invariant is a second, unfenced authority on the "
                    "same fact (Architectural Boundary 6: do not let derived views silently "
                    "become source-of-truth), and it is how a skill mandate stayed in the "
                    "forbidden third state while the fenced Summary reported zero Promotable "
                    "rows. Either give the clause a real Scorecard row and score it there, or "
                    "rewrite the sentence to explain what the score means rather than who "
                    "carries it. Narration of a row's own Promotable history is exempt inside "
                    "§ Scorecard, where rows 53 and 62 do exactly that."
                ),
            )
        )
    return errors


def _grandfathered_rules(project_root: Path) -> dict[str, str]:
    """Return ``{rule filename: version at which its coverage debt froze}``.

    Pre-ledger scorecard coverage is real but unattributable — the rows exist,
    but nothing records which version of the rule they were written against.
    Rather than stamp them all "reviewed" (which would launder exactly the
    unreviewed coverage this audit exists to surface), today's debt is frozen at
    today's versions, shrink-only, per the ``fidelity_presence_grandfather``
    precedent ADR-0.0.73 established.

    The freeze is version-pinned on purpose: a grandfathered rule that is *edited*
    leaves its pinned version behind and must be scored for real. Debt cannot grow
    and cannot silently follow a rule forward.
    """
    path = project_root / _GRANDFATHER_REL
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    entries = payload.get("grandfathered_rules", [])
    return {e["file"]: e["version"] for e in entries if "file" in e and "version" in e}


def audit_advisory_scorecard(project_root: Path) -> list[ValidationError]:
    """Every rule under ``.gzkit/rules/`` must be scored at its current version.

    The scorecard at ``docs/governance/advisory-rules-audit.md`` catalogues
    rules and scores their enforceability (trust-doctrine §3 — doctrine that
    survives agent rotation is doctrine that's mechanical).

    **Filename presence is not coverage (GHI #754).** This audit previously
    asked only whether a rule's *filename stem* appeared anywhere in the
    scorecard, which no edit to an existing rule file could ever falsify. Two
    drifts shipped behind it: ``tests.md`` § Verification exit-code integrity
    (added in rule ``0.8.0``) was never scored, and row 60 still described
    ``task-discovery.md`` behavior that rule ``0.7.0`` had retired.

    The check is now version equality against each rule's
    ``<!-- rule-version: X.Y.Z -->`` marker — the same marker
    ``gz validate --rule-version-markers`` already enforces as present on every
    canonical rule. Bumping a rule without re-scoring it is unreviewed coverage
    and fails closed.

    **The Summary roll-up is fenced against its own rows.** The scorecard
    carries a hand-maintained count table summarizing the rows beneath it — a
    derived view living inside its own source, with no regenerator. It went
    stale (last stamped 2026-05-26, describing 69 rows of a 91-row scorecard)
    and a 2026-08-08 re-measurement taken by substring grep reported figures
    that reproduce against neither. Those Promotable/Ambiguous figures are the
    completion criterion of the Movement C family-closure box, so a wrong count
    retargets real work. The roll-up is optional; transcribing it wrongly is not.
    """
    scorecard = project_root / _SCORECARD_REL
    rules_root = project_root / ".gzkit" / "rules"
    if not scorecard.is_file() or not rules_root.is_dir():
        return []
    text = scorecard.read_text(encoding="utf-8")
    ledger = _scorecard_coverage_ledger(text)
    grandfathered = _grandfathered_rules(project_root)
    errors: list[ValidationError] = []
    errors.extend(_summary_drift_errors(text))
    errors.extend(_unreachable_ruff_claim_errors(text, project_root))
    errors.extend(_prose_promotable_errors(text))
    for rule_md in canonical_rule_files(rules_root):
        artifact = rule_md.relative_to(project_root).as_posix()
        current = rule_version_of(rule_md.read_text(encoding="utf-8", errors="replace"))
        if current is None:
            # Missing markers are `--rule-version-markers`' finding, not this
            # scope's; flagging here would double-report one defect.
            continue
        frozen = grandfathered.get(rule_md.name)
        if frozen is not None and frozen == current:
            # Unmoved pre-ledger debt; visible in the grandfather file, shrink-only.
            continue
        if frozen is not None:
            errors.append(
                ValidationError(
                    type="advisory_scorecard",
                    artifact=artifact,
                    message=(
                        f"Rule `{rule_md.name}` was grandfathered into the advisory "
                        f"scorecard at version {frozen} but is now at {current}. The "
                        "grandfather freezes pre-existing debt; it does not extend to "
                        "clauses added after it. Score the rule's clauses "
                        f"({_SCORES}), add `| \\`{rule_md.name}\\` | \\`{current}\\` |` to "
                        f"the Coverage Ledger of `{_SCORECARD_REL}`, and drop its entry "
                        f"from `{_GRANDFATHER_REL.as_posix()}`."
                    ),
                )
            )
            continue
        scored = ledger.get(rule_md.name)
        if scored is None:
            errors.append(
                ValidationError(
                    type="advisory_scorecard",
                    artifact=artifact,
                    message=(
                        f"Rule `{rule_md.name}` (version {current}) has no entry in the "
                        f"Coverage Ledger of `{_SCORECARD_REL}`, so no clause of it has "
                        f"been scored. Score its binding clauses ({_SCORES}), then add "
                        f"`| \\`{rule_md.name}\\` | \\`{current}\\` |` to the ledger."
                    ),
                )
            )
        elif scored != current:
            errors.append(
                ValidationError(
                    type="advisory_scorecard",
                    artifact=artifact,
                    message=(
                        f"Rule `{rule_md.name}` is at version {current} but the Coverage "
                        f"Ledger of `{_SCORECARD_REL}` last scored it at {scored} — the "
                        "clauses added or changed since then are unreviewed. Re-read the "
                        f"rule, add or correct its scorecard rows ({_SCORES}), then set "
                        f"its ledger row to `{current}`."
                    ),
                )
            )
    return errors
