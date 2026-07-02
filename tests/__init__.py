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
"""

import os

os.environ.pop("FORCE_COLOR", None)
