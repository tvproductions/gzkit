"""Rule content model — target .gzkit/rules/*.md surfaces."""

import re

from pydantic import Field, field_validator

from .base import BaseContentModel
from .bullet import Bullet

_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")


class Rule(BaseContentModel):
    """Per-turn surface content for a single rule file."""

    title: str
    version: str
    paths: list[str] = Field(default_factory=list)
    body: list[Bullet] = Field(default_factory=list)

    @field_validator("version")
    @classmethod
    def _validate_semver(cls, v: str) -> str:
        if not _SEMVER_RE.match(v):
            raise ValueError(f"version must match X.Y.Z; got {v!r}")
        return v

    @field_validator("paths")
    @classmethod
    def _validate_paths(cls, v: list[str]) -> list[str]:
        for path in v:
            if not path:
                raise ValueError("path element must be non-empty")
            if path.startswith("/") or _WINDOWS_DRIVE_RE.match(path):
                raise ValueError(f"path must be relative; got absolute {path!r}")
            if ".." in path.replace("\\", "/").split("/"):
                raise ValueError(f"path must not contain parent traversal; got {path!r}")
        return v
