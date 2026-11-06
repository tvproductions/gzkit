"""Typed exceptions for :mod:`gzkit.content.parse.markdown_parser`.

Held apart from the parser module, which is at the module-size guidance in
``.gzkit/rules/pythonic.md``. Each message leads with the source file path when
one was supplied.
"""


def _fp(file_path: str | None) -> str:
    """Format file_path prefix for error messages."""
    return f"{file_path}: " if file_path else ""


class UnexpectedH1PrefixError(ValueError):
    """The first H1 heading does not start with the expected prefix."""

    def __init__(self, file_path: str | None, prefix: str, line: str) -> None:
        """Name the file, the expected prefix and the H1 line found."""
        self.file_path = file_path
        super().__init__(f"{_fp(file_path)}Expected H1 starting with '# {prefix}', got {line!r}")


class MissingH1Error(ValueError):
    """The document carries no H1 heading."""

    def __init__(self, file_path: str | None) -> None:
        """Name the file."""
        self.file_path = file_path
        super().__init__(f"{_fp(file_path)}No H1 heading found")


class MissingPrefixedLineError(ValueError):
    """No line starts with the required inline-value prefix."""

    def __init__(self, file_path: str | None, prefix: str) -> None:
        """Name the file and the missing prefix."""
        self.file_path = file_path
        super().__init__(f"{_fp(file_path)}Expected line starting with {prefix!r}")


class MissingParagraphError(ValueError):
    """No paragraph text follows the required anchor line."""

    def __init__(self, file_path: str | None, after_prefix: str) -> None:
        """Name the file and the anchor prefix."""
        self.file_path = file_path
        super().__init__(f"{_fp(file_path)}No paragraph found after {after_prefix!r}")


class MissingFeatureLineError(ValueError):
    """A scenario document carries no ``Feature:`` line."""

    def __init__(self, file_path: str | None) -> None:
        """Name the file."""
        self.file_path = file_path
        super().__init__(f"{_fp(file_path)}No 'Feature:' line found")


class MissingScenarioLineError(ValueError):
    """A scenario document carries no ``Scenario:`` line."""

    def __init__(self, file_path: str | None) -> None:
        """Name the file."""
        self.file_path = file_path
        super().__init__(f"{_fp(file_path)}No 'Scenario:' line found")


class MissingBulletLineError(ValueError):
    """A bullet document carries no bullet line."""

    def __init__(self, file_path: str | None) -> None:
        """Name the file."""
        self.file_path = file_path
        super().__init__(f"{_fp(file_path)}No bullet line found")


class UnknownContentTypeError(KeyError):
    """The requested content type is not a registered content model."""

    def __init__(self, as_type: str, valid_types: list[str]) -> None:
        """Name the requested type and the registered ones."""
        self.as_type = as_type
        super().__init__(f"Unknown content type {as_type!r}; valid types: {valid_types}")
