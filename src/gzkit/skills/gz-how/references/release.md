# Release

You are here when shipped work should reach users as a version.

## Steps

1. **`gz-patch-release`** — collect the GHIs closed since the last release,
   draft narrative release notes, and after approval update `RELEASE_NOTES`,
   sync, and publish the GitHub release.
2. Every version bump is a release: the version moves in `pyproject.toml`, the
   package `__init__.py` and the README badge together (`AGENTS.md` § Execution
   Rules), checked by `gz validate --version-release`.

## Branches

- **An ADR just closed** — its closeout ceremony carries its own release steps;
  see [ADR closeout](adr-closeout.md).
- **No GHI qualifies** — there is nothing to release yet.

## Only you can

Approve the release notes and the version.

## Then

[Session end](session-end.md), or the next piece of work.
