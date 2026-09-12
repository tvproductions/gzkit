# Canonical role bodies

These neutral Markdown definitions own the role instruction bodies delivered to
Codex. They were captured verbatim, excluding YAML frontmatter, from the shipped
Claude definitions on 2026-09-12 at commit
`464dd4ff8fa2ee12d98afe99a867280e1b82b431`. `roles.json` records the capture and
the previous Codex body fingerprints for a bounded migration. Claude's existing
bodies and pipeline dispatch paths remain unchanged; the coherence test detects
future divergence so both delivery surfaces can be updated together.

`gzkit.codex_roles.sync_codex_roles` renders registered bodies into
`.codex/agents/*.toml`. Existing native metadata, including model and sandbox
settings, is preserved. Missing files receive only name, description, and body;
the renderer introduces no model or sandbox policy.

The generated header marks body ownership. An unmarked existing file is adopted
only if its body matches the captured legacy fingerprint or the canonical body.
A customized unmarked body and unregistered roles are preserved. To opt a custom
role into canonical delivery, first reconcile its body to its canonical source.
An absent registry performs no work. All writes pass through the shared surface
capture sink, so a planned sync does not mutate the workspace.
