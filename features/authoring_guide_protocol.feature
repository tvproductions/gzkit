Feature: Complexity Guide Protocol
  The gzkit complexity guide protocol server implements a JSON-over-stdio
  LSP-style protocol for editor/IDE integration. Editor authors consume
  this contract to surface authoring-time complexity hints inline.

  @REQ-0.0.30-04-01
  @REQ-0.0.30-04-02
  @REQ-0.0.30-04-05
  @REQ-0.0.30-04-07
  Scenario: Editor client completes handshake, analyze, and shutdown
    Given a complexity guide protocol server is started
    When a client sends an initialize request with version "1.0"
    Then the server responds with protocol version "1.0" and supported capabilities
    When a client sends an analyze request for a Python fixture file
    Then the server responds with a hints list
    When a client sends a shutdown request
    Then the server exits cleanly

  @REQ-0.0.30-04-03
  Scenario: Analyze on a clean file returns an empty hints list
    Given a complexity guide protocol server is started
    When a client sends an analyze request for a clean Python fixture file
    Then the server responds with an empty hints list
    When a client sends a shutdown request
    Then the server exits cleanly

  @REQ-0.0.30-04-04
  Scenario: Malformed request envelope produces a named parse error
    Given a complexity guide protocol server is started
    When a client sends a malformed envelope
    Then the server responds with parse error code -32700

  @REQ-0.0.30-04-06
  Scenario: Major version mismatch produces a named version-mismatch error
    Given a complexity guide protocol server is started
    When a client sends an initialize request with version "99.0"
    Then the server responds with version mismatch error code -32099
