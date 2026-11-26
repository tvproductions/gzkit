"""Every relative link in a canonical skill, rule, chore, persona or agent file resolves.

GHI #1379.

Three skill links were written one level short (`../../docs/…` from
`.gzkit/skills/<name>/SKILL.md`, which lands in `.gzkit/`), and nothing resolved skill
links: the pointer-integrity validator reads `> See [...]` blockquotes in the root
contracts and `.claude/rules/**` only (REQ-0.0.33-03-04), and the docs build does not
build skills.

The test reads every `.md` file under `.gzkit/skills`, `.gzkit/rules`, `.gzkit/chores`,
`.gzkit/personas` and `.gzkit/agents`, skipping any path through a `proofs` or `archive`
directory and every `AGENTS.md`, which is generated and checked under #922. It drops fenced
code blocks and inline code spans, then resolves each `[text](target)` whose target has no
URL scheme and does not start with `#` or `<`. The part before any `#` is resolved against
the linking file's directory, as a Markdown viewer would. A target that does not exist on
disk is refused. Anchors are not checked.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOTS = tuple(
    REPO / part
    for part in (
        ".gzkit/skills",
        ".gzkit/rules",
        ".gzkit/chores",
        ".gzkit/personas",
        ".gzkit/agents",
    )
)
SKIPPED_PARTS = {"proofs", "archive"}

_FENCE = re.compile(r"^\s*(```|~~~)")
_INLINE_CODE = re.compile(r"`[^`]*`")
_LINK = re.compile(r"\]\(([^()\s]+)\)")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def unresolved_links(path: Path, text: str) -> list[str]:
    """Return each relative link target in *text* that does not resolve from *path*'s directory."""
    found: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in _LINK.finditer(_INLINE_CODE.sub("", line)):
            target = match.group(1)
            if _SCHEME.match(target) or target.startswith(("#", "<")):
                continue
            relative = target.split("#", 1)[0]
            if relative and not (path.parent / relative).exists():
                found.append(target)
    return found


def _canonical_files() -> list[Path]:
    return [
        path
        for root in ROOTS
        for path in sorted(root.rglob("*.md"))
        if path.name != "AGENTS.md" and not SKIPPED_PARTS.intersection(path.relative_to(REPO).parts)
    ]


class TestCanonRelativeLinksResolve(unittest.TestCase):
    def test_every_root_exists(self):
        missing = [root for root in ROOTS if not root.is_dir()]
        self.assertEqual(missing, [], "a link-check root moved; update the roots")

    def test_every_relative_link_resolves(self):
        offenders = [
            f"{path.relative_to(REPO).as_posix()}: {target}"
            for path in _canonical_files()
            for target in unresolved_links(path, path.read_text(encoding="utf-8", errors="replace"))
        ]
        self.assertEqual(
            offenders,
            [],
            "a relative link resolves from the linking file's directory; from "
            ".gzkit/skills/<name>/ the repo root is ../../../ (GHI #1379): " + "; ".join(offenders),
        )

    def test_resolution_is_from_the_linking_file(self):
        skill = REPO / ".gzkit/skills/gz-ontology/SKILL.md"
        self.assertEqual(
            unresolved_links(
                skill, "- Manpage: [`gz ontology`](../../docs/user/manpages/ontology.md)"
            ),
            ["../../docs/user/manpages/ontology.md"],
        )
        self.assertEqual(
            unresolved_links(
                skill, "- Manpage: [`gz ontology`](../../../docs/user/manpages/ontology.md)"
            ),
            [],
        )

    def test_code_urls_and_anchors_are_not_links(self):
        skill = REPO / ".gzkit/skills/gz-ontology/SKILL.md"
        text = (
            "every `See [text](path)` link resolves\n"
            "```\n"
            "[broken](../nowhere.md)\n"
            "```\n"
            "[site](https://example.com/x) and [here](#reference) and [mail](mailto:a@b.c)\n"
            "[anchored](../../../docs/user/manpages/ontology.md#examples)\n"
        )
        self.assertEqual(unresolved_links(skill, text), [])


if __name__ == "__main__":
    unittest.main()
