"""Steps for `features/patch_release.feature`.

`gz patch release` fails closed when `gh` is unauthenticated, so a scenario that
asserts the dry-run path exits 0 has to ARRANGE that authentication rather than
inherit it. It used to inherit it twice over: from the operator's own logged-in
`gh` locally, and in CI from a fake `gh` an earlier feature left installed on the
shared `subprocess` module. Neither is a precondition the scenario declares, and
both vanished the moment Behave sharding (GHI #906) ran the feature in its own
process. Stubbing the auth probe here makes the dependency the scenario's own.
"""

from unittest import mock

from behave import given

from gzkit.utils import run_exec as _real_run_exec


@given("the gh CLI is authenticated")
def step_gh_authenticated(_context) -> None:
    """Stub the `gh auth status` probe only; every other exec stays real.

    Delegating the rest keeps discovery honest — the scenario still walks real
    git history and still renders from a real DiscoveryResult, so it can fail
    when the discovery it is named for breaks. Blanket-faking `run_exec` would
    make it pass over an empty command surface.

    The patcher is stopped by `features/environment.py` `after_scenario`, which
    calls `mock.patch.stopall()` — the same teardown that stops this class of
    leak from reaching the next scenario.
    """

    def fake_run_exec(cmd, cwd, timeout=None):
        if list(cmd[:3]) == ["gh", "auth", "status"]:
            return (0, "Logged in to github.com as fixture-bot", "")
        return _real_run_exec(cmd, cwd, timeout)

    mock.patch("gzkit.commands.patch_release.run_exec", side_effect=fake_run_exec).start()
