"""Shared skill metadata compatibility contract."""

import json
from importlib.resources import files

SKILL_DESCRIPTION_MAX_CHARS = 1024
SUPPORTED_SKILL_HARNESSES = "Claude Code and Codex"

# Skill-authoring-quality § Body Quality: physical body lines after frontmatter.
SKILL_BODY_ALIAS_MIN_LINES = 30
SKILL_BODY_NORMAL_MAX_LINES = 200
SKILL_BODY_MAX_LINES = 300
# Fixed cutover ceilings (GHI #1037, 2026-09-19). Source edits may only
# remove entries or lower ceilings; projects cannot add local exemptions.
SKILL_BODY_GRANDFATHER: dict[str, int] = json.loads(
    files("gzkit").joinpath("skill_body_grandfather.json").read_text(encoding="utf-8")
)
