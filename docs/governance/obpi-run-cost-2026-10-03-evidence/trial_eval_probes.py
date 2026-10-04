"""Read-only OBPI-10 evaluation: all mutations occur inside temporary fixtures."""

from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from gzkit.acceptance_execution import _file_roster
from gzkit.content.corpus_store import append_entry
from gzkit.content.models.corpus import CorpusEntry
from gzkit.content.ownership import declaration_path, sections_digest
from gzkit.content.parse import section_id
from gzkit.governance.events import emit_section_ownership_genesis
from gzkit.governance.trust_audits.bullet_retention import (
    _parse_scorecard,
    audited_population,
    validate_bullet_retention,
)

RULE = "The independent example must be retained."
SCORECARD = Path("docs/governance/advisory-rules-audit.md")


def seed(root: Path, *, classification: Literal["Mechanical", "Ambiguous"] = "Mechanical") -> None:
    """Create a witnessed enrollment and corpus inside a temporary project."""
    unowned = "## Unowned\nAn unowned paragraph.\n"
    (root / "AGENTS.md").write_text("## Owned\n\n" + unowned, encoding="utf-8")
    sections = {"owned": "corpus-owned", "unowned": "unowned"}
    digest = sections_digest(sections)
    event_id = "section-ownership-genesis-AGENTS.md-" + digest[:12]
    floor = len(unowned.encode())
    emit_section_ownership_genesis(root, event_id, "AGENTS.md", digest, floor)
    declaration = declaration_path(root, "AGENTS.md")
    declaration.parent.mkdir(parents=True)
    declaration.write_text(
        json.dumps(
            {
                "surface": "AGENTS.md",
                "sections": sections,
                "unowned_byte_floor": floor,
                "measured_at": "2026-10-04T00:00:00Z",
                "floor_event_id": event_id,
            }
        ),
        encoding="utf-8",
    )
    append_entry(
        root,
        "AGENTS.md",
        CorpusEntry(
            id="independent-entry",
            surface="AGENTS.md",
            section="owned",
            tier="invariant",
            classification=classification,
            text=RULE,
            origin="independent-trial-evaluation",
            ts="2026-10-04T00:00:00Z",
        ),
    )


def scorecard(
    root: Path,
    source: str,
    *,
    classification: str = "Judgment",
    entry: bool = False,
    rule: str = RULE,
) -> None:
    """Write one attributed scorecard row inside the temporary project."""
    path = root / SCORECARD
    path.parent.mkdir(parents=True, exist_ok=True)
    note = f"source={source}" + (" entry=independent-entry" if entry else "")
    path.write_text(
        "### Independent contract\n\n| # | Rule | Score | Notes |\n"
        "|---|---|---|---|\n"
        f"| 1 | {rule} | **{classification}** | `{note}` |\n",
        encoding="utf-8",
    )


def observe(root: Path, label: str) -> dict:
    """Record the audit result, including malformed-input exceptions."""
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            errors = validate_bullet_retention(root)
            population = audited_population(root)
        except (AttributeError, TypeError) as exc:
            return {"case": label, "exception": type(exc).__name__, "message": str(exc)}
    return {
        "case": label,
        "errors": len(errors),
        "messages": [error.message for error in errors],
        "population": [row.model_dump() for row in population],
    }


def population_evidence(root: Path) -> dict:
    """Compare historical and current identities using an independent table reader."""

    def identities(text: str) -> dict:
        body = text.split("\n## Scorecard\n", 1)[1].split("\n## ", 1)[0]
        result, section = {}, None
        for line in body.splitlines():
            if line.startswith("### "):
                section = section_id(line[4:])
            cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line)]
            if (
                len(cells) >= 5
                and re.fullmatch(r"\d+[a-z]?", cells[1])
                and re.search(r"\*\*(Mechanical|Promotable|Judgment|Ambiguous)\*\*", cells[3])
            ):
                result[(section, cells[1])] = cells[2:]
        return result

    before = identities(
        subprocess.check_output(
            ["git", "show", "4893b7321^:" + str(SCORECARD)],
            cwd=root,
            text=True,
        )
    )
    after = identities((root / SCORECARD).read_text(encoding="utf-8"))
    parsed = {(row.section_id, row.number) for row in _parse_scorecard(root / SCORECARD)}
    return {
        "actual_before": len(before),
        "actual_after": len(after),
        "removed": sorted(set(before) - set(after)),
        "added": sorted(set(after) - set(before)),
        "audited_count": len(parsed),
        "omitted": [
            {"identity": key, "score": after[key][1], "attributed": "source=" in after[key][2]}
            for key in sorted(set(after) - parsed)
        ],
    }


def freshness_evidence() -> dict:
    """Measure whether changes to live governance data change the proof file roster."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        before = _file_roster(root)
        names = [
            str(SCORECARD),
            "docs/user/manpages/validate.md",
            ".gzkit/corpus/AGENTS.md.jsonl",
            ".gzkit/ownership/AGENTS.md.json",
            "AGENTS.md",
        ]
        for name in names:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Changed review input\n", encoding="utf-8")
        after = _file_roster(root)
        return {
            "files_changed": names,
            "roster_unchanged": before == after,
            "included": {name: name in after for name in names},
        }


def main() -> None:
    """Print reproducible observations without changing the evaluated repository."""
    observations = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        original = (root / "AGENTS.md").read_text(encoding="utf-8")
        (root / "AGENTS.md").write_text(
            original.replace("## Owned\n", "## Owned\n" + RULE), encoding="utf-8"
        )
        scorecard(root, "AGENTS.md#owned", entry=True)
        observations.append(observe(root, "valid canonical owned mapping retains rule"))
        (root / "AGENTS.md").write_text(original, encoding="utf-8")
        scorecard(root, "AGENTS.md#owned", entry=True)
        observations.append(observe(root, "owned Mechanical overrides Judgment"))
        scorecard(root, "AGENTS.md#owned")
        observations.append(observe(root, "canonical owned source missing entry"))
        scorecard(root, "./AGENTS.md#owned")
        observations.append(observe(root, "same owned source with dot slash missing entry"))
        skill = root / ".gzkit/skills/example/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("Different skill content.\n", encoding="utf-8")
        (root / "CLAUDE.md").write_text(RULE, encoding="utf-8")
        scorecard(root, ".gzkit/skills/example/SKILL.md", classification="Mechanical")
        observations.append(observe(root, "canonical skill source lacks rule"))
        scorecard(root, "./.gzkit/skills/example/SKILL.md", classification="Mechanical")
        observations.append(observe(root, "same skill source with dot slash lacks rule"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root, classification="Ambiguous")
        scorecard(root, "AGENTS.md#unowned")
        observations.append(observe(root, "unmapped Ambiguous entry with ownership"))
        declaration_path(root, "AGENTS.md").unlink()
        observations.append(observe(root, "ownership declaration deleted genesis remains"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root, classification="Ambiguous")
        scorecard(root, "AGENTS.md#owned", entry=True)
        (root / SCORECARD).write_text("### Empty scorecard\n", encoding="utf-8")
        observations.append(observe(root, "no parsed rows despite owned Ambiguous entry"))
        scorecard(root, "AGENTS.md#owned", entry=True)
        path = declaration_path(root, "AGENTS.md")
        original_declaration = json.loads(path.read_text(encoding="utf-8"))
        path.write_text("[]", encoding="utf-8")
        observations.append(observe(root, "ownership JSON is a list"))
        original_declaration["unowned_byte_floor"] = None
        path.write_text(json.dumps(original_declaration), encoding="utf-8")
        observations.append(observe(root, "ownership floor is null"))
    print(
        json.dumps(
            {
                "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                "behavior_probes": observations,
                "population": population_evidence(Path.cwd()),
                "freshness": freshness_evidence(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
