"""Typed errors for the patch-release ceremony (``patch_release.py``)."""

from gzkit.commands.common import GzCliError


class GhNotAuthenticatedError(GzCliError):
    """The ``gh`` CLI is missing or not authenticated."""

    def __init__(self, detail: str) -> None:
        """Build the message from *detail*."""
        self.detail = detail
        super().__init__(
            "BLOCKERS:\n"
            "  gh CLI is not authenticated.  Run `gh auth login` first.\n"
            f"  Detail: {detail}"
        )


class ReleaseCommitFailedError(GzCliError):
    """The release commit could not be created."""

    def __init__(self, detail: str) -> None:
        """Build the message from *detail*."""
        self.detail = detail
        super().__init__(f"Commit failed: {detail}")


class QualitySweepFailedError(GzCliError):
    """The full quality sweep (``gz check --full``) failed before the release push."""

    def __init__(self, detail: str) -> None:
        """Build the message from *detail*."""
        self.detail = detail
        super().__init__(
            f"The full quality sweep (`gz check --full`) failed. Fix before releasing.\n{detail}"
        )


class ReleasePushFailedError(GzCliError):
    """The release push to ``origin/main`` failed."""

    def __init__(self, detail: str) -> None:
        """Build the message from *detail*."""
        self.detail = detail
        super().__init__(f"Push failed: {detail}")


class GhReleaseCreateFailedError(GzCliError):
    """``gh release create`` failed."""

    def __init__(self, detail: str) -> None:
        """Build the message from *detail*."""
        self.detail = detail
        super().__init__(f"gh release create failed: {detail}")


class VersionInconsistencyError(GzCliError):
    """The version surfaces disagree after the release."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Version inconsistency after release.")
