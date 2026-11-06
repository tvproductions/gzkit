"""Typed RED-witness failures (RO-9, TRY003).

Kept beside :mod:`gzkit.red_witness` because that module is over the
authoring-time module size limit (``.gzkit/rules/pythonic.md``).
"""


class BaseCommitUnresolvedError(RuntimeError):
    """``git rev-parse HEAD`` could not resolve the base commit."""

    def __init__(self, stderr: str) -> None:
        """Build the message from ``stderr``."""
        super().__init__(f"cannot resolve base commit: {stderr}")


class BaseWorktreeError(RuntimeError):
    """``git worktree add`` could not create the base-tree worktree."""

    def __init__(self, stderr: str) -> None:
        """Build the message from ``stderr``."""
        super().__init__(f"cannot create base worktree: {stderr}")


class NoCoveringTestsError(ValueError):
    """A RED witness was requested for a REQ with no covering tests."""

    def __init__(self, req_id: str) -> None:
        """Build the message from ``req_id``."""
        self.req_id = req_id
        super().__init__(f"no covering tests supplied for {req_id}; nothing to witness")
