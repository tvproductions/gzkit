"""Scenario content model — target features/**/*.feature surfaces."""

from pydantic import Field

from .base import BaseContentModel


class Scenario(BaseContentModel):
    """Per-turn surface content for a single Gherkin scenario."""

    feature: str
    scenario: str
    given: list[str] = Field(default_factory=list)
    when: list[str] = Field(default_factory=list)
    then: list[str] = Field(default_factory=list)
