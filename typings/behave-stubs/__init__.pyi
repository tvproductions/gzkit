# Types for behave's step decorators, which behave ships without. behave binds
# given, when and then to _StepDecorator() placeholders and swaps the real
# decorators in at import, so a checker sees an object with no __call__. This
# partial stub (PEP 561) types those three names alone; every other behave name
# resolves from the installed package (RO-9 tranche 4).

from collections.abc import Callable
from typing import Any, TypeVar

_StepFunction = TypeVar("_StepFunction", bound=Callable[..., Any])

def given(step_text: str, /, **kwargs: object) -> Callable[[_StepFunction], _StepFunction]: ...
def when(step_text: str, /, **kwargs: object) -> Callable[[_StepFunction], _StepFunction]: ...
def then(step_text: str, /, **kwargs: object) -> Callable[[_StepFunction], _StepFunction]: ...
