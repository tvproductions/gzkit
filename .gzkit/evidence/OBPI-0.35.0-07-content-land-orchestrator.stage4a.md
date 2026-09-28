# Stage 4a — OBPI-0.35.0-07-content-land-orchestrator

## Value

Before: promoting a corpus change to committed renditions was `gz content commit`, one consumer at a time, each write non-atomic, with no shared record that a multi-consumer change was in flight. Now: `gz content land <surface>` generates every routed consumer's candidate, verifies lineage, runs the OBPI-14 retention gate, and publishes the whole set under ONE corpus attestation and a shared `landing_id`, through a journal written before the first byte and cleared last, with hash-based `--status` and a non-destructive resume that never re-prompts.

## Key proof

The CLI contract is registered with its required positional surface:

```text
$ uv run gz content land --help
usage: gz content land [-h] [--attestor ATTESTOR]
                       [--attestation-text ATTESTATION_TEXT]
                       [--retention-map RETENTION_MAPS] [--dry-run]
                       [--status LANDING_ID] [--quiet | --verbose] [--debug]
                       surface
```

The covering unit tests pass:

```text
$ uv run -m unittest tests.content.test_landing tests.commands.test_content_land
...
OK
```

Stage-2 acceptance is ready over all ten obligations (every current proof approved by spec and quality review, every mapped finding independently closed):

```text
$ uv run gz obpi acceptance OBPI-0.35.0-07-content-land-orchestrator status --stage stage2 --json
  "ready": true,
```

## Executed acceptance proofs (current)

| REQ | Kind | Proof | Controls |
|-----|------|-------|----------|
| REQ-0.35.0-07-01 | BEHAVIOR | proof-730833314c9e4afdab11249f698dffcc | 1/1 killed on assertion |
| REQ-0.35.0-07-02 | BEHAVIOR | proof-f159c695fa9c4d0abd6cfc98c5374c5d | 5/5 |
| REQ-0.35.0-07-03 | BEHAVIOR | proof-0bce2a9066b3498ca160fcc459a69086 | 3/3 |
| REQ-0.35.0-07-04 | BEHAVIOR | proof-92e2f786830f4983839dcbbff1a926a1 | 2/2 |
| REQ-0.35.0-07-05 | BEHAVIOR | proof-1058fa7598a549f5a699957cb99a17b4 | 3/3 |
| REQ-0.35.0-07-06 | BEHAVIOR | proof-d477011537e5493bbdb096d47b3f9627 | 1/1 |
| REQ-0.35.0-07-07 | BEHAVIOR | proof-fa5927ac2a5e40ee804830bb15a56b70 | 3/3 |
| REQ-0.35.0-07-08 | BEHAVIOR | proof-778caef14d8049ea8fc89c25c26a9aae | 3/3 |
| REQ-0.35.0-07-09 | SUPPORT | proof-3f38b80e476845d6b564fda7ceeb003c | SUPPORT resolver pass |
| REQ-0.35.0-07-10 | BEHAVIOR | proof-4bc2cb4107d2413ab3ef0e40c17fb8f4 | 4/4 |

Stage-2 reviews on these proofs: spec `arb-step-specreview-7c33d579e6404c22981224557428c375`, quality `arb-step-qualityreview-f4d2438d928f460491f31b9a1bb4453a`.

## Receipts (Stage 3; cited, not replayed)

```text
arb-ruff-4f4e80dbc54b43d1b09d556ad8b58179
arb-step-typecheck-4ab83c7ed25a431289ede565e3d62682
arb-step-unittest-92545fa88b7244189c1b3d02080b97a0
arb-step-mkdocs-87b2feb3938545c19f4ef3792429a58a
arb-step-behave-6cd45fd061784845ab93f0fab462ab0e
```

These predate the final rollback-prose edit; they are re-run before attestation.

## Limits disclosed

- `landing.py` is about 1,660 lines (advisory `pythonic.md` 600-line guidance; `gz check` module band and xenon pass).
- The rollback command is written in seven message sites; `git restore` leaves untracked new sidecars when a landing is rolled back before it is committed; REQ-09's SUPPORT proof passes on the artifact-exists arm (recorded as insights).
- The RED witness receipts are `failure_class=error` (no landing module at base); the executed mutation proofs above are the behavioural evidence.
