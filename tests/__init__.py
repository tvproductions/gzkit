"""gzkit test suite.

Test hermeticity: neutralize ambient color-forcing so captured CLI output is
deterministic plain text regardless of the operator's terminal. Modern
terminals (Ghostty, etc.) export ``FORCE_COLOR``, which makes Rich emit ANSI
SGR codes — color *and* bold — even into non-TTY test captures, breaking every
plain-substring assertion. ``NO_COLOR`` alone is insufficient: it suppresses
color but not bold, because ``FORCE_COLOR`` still forces terminal mode. Popping
``FORCE_COLOR`` here lets Rich auto-detect the non-TTY capture and render plain
text. This package is imported by both invocation paths — the direct
``uv run -m unittest`` path (shell env carries FORCE_COLOR) and the ``gz check``
subprocess path (inherits it via ``run_command``'s ``{**os.environ}``) — so this
single chokepoint covers all of them. Tests that specifically exercise
TTY/ANSI rendering construct their own ``force_terminal=True`` Console and are
unaffected.

Git repository selection (GHI #977): the same chokepoint drops git's repo-local
variables — ``GIT_DIR``, ``GIT_WORK_TREE``, ``GIT_INDEX_FILE``, ``GIT_COMMON_DIR``
and the rest of git's own ``local_repo_env`` set, plus the ``GIT_CONFIG*``
injection variables. A git hook exports an absolute ``GIT_DIR``; from a linked
worktree it names ``<repo>/.git/worktrees/<name>``, and every git this process
or the code it drives then spawns against a temp root re-initialises the
HOSTING repository instead (guessing bare) and writes fixture identity and
config into it. Per-call ``env=_isolated_git_env()`` at every fixture site is
the explicit local statement; this pop is what also covers the git that
PRODUCTION code spawns when a test drives it. A test that needs a planted
``GIT_DIR`` sets it after import (``patch.dict``), so nothing here is lost to
it. Commands run inside a checkout still discover that checkout by ``cwd``.
"""

import os

from gzkit.git_spawn_boundary import scrub_repo_local_git_env

os.environ.pop("FORCE_COLOR", None)
scrub_repo_local_git_env(os.environ)
