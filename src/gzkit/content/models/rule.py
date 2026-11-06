"""Rule content model — target .gzkit/rules/*.md surfaces."""

import re

from pydantic import Field, field_validator

from .base import BaseContentModel
from .bullet import Bullet

_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")


class InvalidRuleVersionError(ValueError):
    """A rule's version is not X.Y.Z."""

    def __init__(self, version: str) -> None:
        """Name the offending version."""
        self.version = version
        super().__init__(f"version must match X.Y.Z; got {version!r}")


class EmptyRulePathError(ValueError):
    """A rule's paths list carries an empty element."""

    def __init__(self) -> None:
        """Build the fixed empty-path message."""
        super().__init__("path element must be non-empty")


class AbsoluteRulePathError(ValueError):
    """A rule's paths list carries an absolute path."""

    def __init__(self, path: str) -> None:
        """Name the offending path."""
        self.path = path
        super().__init__(f"path must be relative; got absolute {path!r}")


class RulePathTraversalError(ValueError):
    """A rule's paths list carries a parent-traversal segment."""

    def __init__(self, path: str) -> None:
        """Name the offending path."""
        self.path = path
        super().__init__(f"path must not contain parent traversal; got {path!r}")


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
            raise InvalidRuleVersionError(v)
        return v

    @field_validator("paths")
    @classmethod
    def _validate_paths(cls, v: list[str]) -> list[str]:
        for path in v:
            if not path:
                raise EmptyRulePathError
            if path.startswith("/") or _WINDOWS_DRIVE_RE.match(path):
                raise AbsoluteRulePathError(path)
            if ".." in path.replace("\\", "/").split("/"):
                raise RulePathTraversalError(path)
        return v
