Feature: gz issue file cross-repo defect filing wrapper (ADR-0.0.23 / OBPI-0.0.23-04)
  As an agent or operator inside a gzkit-consuming repository,
  I want a wrapper that auto-stamps a provenance trailer, validates
  that the issue body references a gzkit-owned surface, and routes the
  issue at tvproductions/gzkit regardless of my git remote,
  so that gzkit-surface defects cannot be misrouted to the consumer's
  tracker even by accident, closing the Safeguard circumvention shape.

  @REQ-0.0.23-04-04
  @REQ-0.0.23-04-05
  Scenario: Provenance trailer auto-stamps consumer slug and gz version
    Given a fixture git remote "git@github.com:acme/widget.git"
    When I run the gz command "issue file --title T --body 'gz validate fails on stale ledger' --enhancement --dry-run"
    Then the command exits with code 0
    And the output contains "Filed from acme/widget running gz v"
    And the output contains "Target: tvproductions/gzkit"
    And the output contains "Label: enhancement"

  @REQ-0.0.23-04-05
  Scenario: Issue is routed to tvproductions/gzkit regardless of consumer remote
    Given a fixture git remote "https://github.com/other/consumer.git"
    When I run the gz command "issue file --title T --body 'gz cli audit miscounts manpages' --defect --dry-run"
    Then the command exits with code 0
    And the output contains "Target: tvproductions/gzkit"
    And the output contains "Filed from other/consumer running gz v"

  @REQ-0.0.23-04-06
  Scenario: Body without a gzkit-owned surface marker is hard-rejected
    Given a fixture git remote "git@github.com:acme/widget.git"
    When I run the gz command "issue file --title T --body 'consumer auth flow regression' --defect --dry-run"
    Then the command exits with code 1
    And the output contains "gzkit-owned surface"
