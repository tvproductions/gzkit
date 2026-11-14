# Canonical role bodies

These neutral Markdown definitions own the role instruction bodies delivered to
Codex and Claude. They were captured verbatim, excluding YAML frontmatter, from the
shipped Claude definitions on 2026-09-12 at commit
`464dd4ff8fa2ee12d98afe99a867280e1b82b431`. `roles.json` records the capture and
the previous Codex body fingerprints for a bounded migration. Edit the role here,
never in a vendor copy: since 2026-11-14 the Claude copies are generated too
(GHI #1328; operator, *"A: Generate from canon"*).

`gzkit.codex_roles.sync_claude_roles` writes each registered role's body into
`.claude/agents/<name>.md`, keeping the file's frontmatter (`tools`, `model`,
`maxTurns`, an `effort:` once roles carry one) byte for byte; a missing file gets
only `name` and `description`. The pipeline's dispatch paths are unchanged.
`gz validate --surfaces` reports a hand edit to either vendor copy.

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
