VERDICT: REFUTED

The green suite does not establish the claim. I reproduced invariant-attestor bypasses, a false “verbatim” append-only assertion, missing REQ-08 evidence, schema/model disagreement, broken recovery commands, and sequence-level partial writes.

## 1. Tautological tests

Commands:

```text
$ uv run -m unittest tests.commands.test_content_retire tests.test_schemas -v
----------------------------------------------------------------------
Ran 56 tests in 0.146s

OK

$ uv run gz test
Running 570 test suites (8824 total tests) across 10 workers
----------------------------------------------------------------------
Ran 8824 tests in 45.671s

OK

Unit tests passed.
```

Despite that:

```text
$ uv run gz covers OBPI-0.35.0-02-content-withdraw-verb --json
"total_reqs": 8,
"covered_reqs": 7,
"uncovered_reqs": 1,
"coverage_percent": 87.5,
...
"req_id": "REQ-0.35.0-02-08",
"covered": false,
"ledger_event_ids": []
```

Strict deletion/falsifiability mapping against [retire.py](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/retire.py:61) and [content/__init__.py](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/content/__init__.py:324):

- REQ-01:
  - BDD missing-attestor and unit missing-attestor tests: deletion of `retire.py:142` makes them fail.
  - `test_invariant_tier_retirement_without_reason_fails_closed`: no single-line kill. Argparse `required=True` and the handler gate independently reject it.
- REQ-02:
  - BDD/unit invariant whitespace-attestor tests: no single-line kill; both `retire.py:113` and `:142` independently reject it.
  - Compressible whitespace-attestor: `retire.py:113`.
  - Whitespace reason: `retire.py:124`.
- REQ-03:
  - BDD scenario only asserts exit 0; removing the corpus append at `retire.py:161` would still satisfy it.
  - Unit row-growth test: `retire.py:161`.
  - Validator test: `retire.py:207`.
- REQ-04:
  - BDD and unit projection tests: `retire.py:157`.
  - Neither test witnesses byte-verbatim preservation; production already violates it, shown below.
- REQ-05:
  - Unknown/absent-store recovery tests: retry prose at `retire.py:82-83`.
  - Already-retired recovery: `retire.py:94-95`.
  - Citation test: `retire.py:135`.
- REQ-06:
  - Parser tests: `content/__init__.py:362-366`.
  - Help-description test: `content/__init__.py:339-343`.
- REQ-07:
  - BDD and pair-content/order test: `retire.py:207`.
  - `test_dual_events_survive_the_real_validator_both_tiers` does not assert that either event exists. A no-op ledger writer leaves the command green and the validator green:

```text
RETIRE_EXIT=0
CORPUS_EVENTS=[{'event': 'corpus_entry_appended', ...}]  # remember event only
VALIDATOR_ERRORS=[]
```

- REQ-08: no covering test by design, but its required ledger proof is also absent.

The replacement recovery-command helper is itself weak. It accepts a useless help command as “runnable”:

```text
$ uv run python -c '<invoke _assert_recovery_commands_run with fake prose>'
HELPER_RESULT=PASS
FAKE_RECOVERY=Retry with `gz content retire --help`.
```

It checks only for `unrecognized arguments` and `invalid choice`; it does not require successful or relevant recovery.

## 2. Gate bypass

### Invisible “attestor” retires an invariant

U+200B is an invisible format character. It is not removed by `str.strip()`:

```text
REMEMBER_EXIT=0
ATTESTOR_CODEPOINTS=['0x200b']
STRIP_RESULT='\u200b'
RETIRE_EXIT=0
ROW_DELTA=1
LEDGER_ATTESTOR='\u200b'
OUTPUT=Retired corpus entry ...
```

Strictly, U+200B is not in Unicode’s formal `White_Space` property. Nevertheless, it is visually blank and is not a real named attestor, so the stated human-name guarantee is false.

### Direct handler call bypasses required reason

Calling `content_retire_cmd` directly with an empty reason retires a compressible entry and writes an invalid event:

```text
DIRECT_EXIT=0
ROW_DELTA=1
EVENT_REASON=''
LEDGER_ERRORS=["Field 'reason' must be at least 1 non-whitespace characters."]
```

### Tombstone and supersedes targets are accepted

Retiring a retraction tombstone without an attestor reactivates the original invariant:

```text
FIRST_EXIT=0
TOMBSTONE_TIER=compressible
SECOND_EXIT_NO_ATTESTOR=0
ORIGINAL_EFFECTIVE_AFTER_SECOND=True
SECOND_EVENT_TIER='compressible'
SECOND_EVENT_ATTESTOR=''
```

The same occurs for a compressible `supersedes` row:

```text
EXIT_NO_ATTESTOR=0
ORIGINAL_INVARIANT_EFFECTIVE=True
REPLACEMENT_EFFECTIVE=False
EVENT_TIER='compressible'
EVENT_ATTESTOR=''
```

A normal malformed corpus tier is rejected:

```text
INVALID_TIER=REFUSED
tier
  Input should be 'invariant' or 'compressible'
```

But the ledger factory/model/schema all accept a non-discriminated tier:

```text
FACTORY_TIER='other'
MODEL_TIER='other'
SCHEMA_ERRORS=[]
```

## 3. Append-only / REQ-04

The test really calls `effective_corpus()` at [test_content_retire.py:809](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:809). That part is genuine.

The “survives verbatim” claim is false. [corpus_store.py](/Users/jeff/Documents/Code/gzkit/src/gzkit/content/corpus_store.py:31) reloads and rewrites the entire JSONL store through current serialization. A valid historical-format row changes bytes:

```text
EXIT=0
RAW_ROW_EQUAL=False
BEFORE={"ts": "2026-01-01T00:00:00+00:00", "origin": "probe", "text": "floor text", "classification": "Mechanical", "tier": "invariant", "section": "Prime Directive", "surface": "AGENTS.md", "id": "old", "retires": null, "supersedes": null}
AFTER={"id":"old","surface":"AGENTS.md","section":"Prime Directive","anchor":null,"tier":"invariant","classification":"Mechanical","witness":null,"text":"floor text","origin":"probe","ts":"2026-01-01T00:00:00+00:00"}
TEXT_EQUAL=True
EFFECTIVE_CONTAINS_OLD=False
```

The tests assert only selected semantic fields—`text` and `tier`—not the original row bytes.

## 4. Ledger pair / REQ-07

The ordinary invariant path is correct:

```text
EXIT=0
ORDER=['corpus_entry_appended', 'corpus_entry_retired']
RETIRED_TIER='invariant'
ATTESTOR='g0'
LINK_MATCH=True
```

The unit test explicitly asserts appended-before-retired ordering and `tier == "invariant"` at [test_content_retire.py:840](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:840). This attack did not refute the normal-path ordering or retired-entry tier.

It is refuted at the broader “always” boundary by the partial-write results in check 6.

## 5. Schema, model, and history

Committed-ledger validation passes:

```text
$ uv run gz validate --ledger
Validated: ledger

✓ All validations passed (1 scopes).
```

All five historical rows without `tier` also parse through `parse_typed_event`:

```text
HISTORICAL_WITHOUT_TIER=5
line=13992 id=corpus-entry-retired-2026-07-22T10:31:32.832846+00:00 parsed_tier='' parsed_attestor=''
line=15045 id=corpus-entry-retired-2026-08-17T11:48:53.531900+00:00 parsed_tier='' parsed_attestor=''
line=15047 id=corpus-entry-retired-2026-08-17T11:55:41.972520+00:00 parsed_tier='' parsed_attestor=''
line=15075 id=corpus-entry-retired-2026-08-17T21:47:20.670176+00:00 parsed_tier='' parsed_attestor=''
line=15117 id=corpus-entry-retired-2026-08-17T23:33:17.340677+00:00 parsed_tier='' parsed_attestor=''
```

But the schema and typed model disagree when `tier` is explicitly empty:

```text
MODEL_PARSE=PASS tier=''
SCHEMA_ERRORS=["Field 'tier' must be at least 1 non-whitespace characters."]
```

The model defaults were sufficient for history compatibility, but they do not make the two readers semantically equivalent.

## 6. Partial write

Injected failure on the first ledger event:

```text
CASE_FAIL_ON_APPEND=1
EXIT=2
CORPUS_ROW_DELTA=1
TARGET_EFFECTIVE=False
NEW_LEDGER_EVENTS=[]
REPORT=Error writing ledger event 'corpus_entry_appended' ... THE RETIREMENT ALREADY HAPPENED ... the ledger witness is incomplete ...
```

Injected failure on the second:

```text
CASE_FAIL_ON_APPEND=2
EXIT=2
CORPUS_ROW_DELTA=1
TARGET_EFFECTIVE=False
NEW_LEDGER_EVENTS=['corpus_entry_appended']
REPORT=Error writing ledger event 'corpus_entry_retired' ... THE RETIREMENT ALREADY HAPPENED ... the ledger witness is incomplete ...
```

The error text reports the partial state honestly. The state remains serious: canonical corpus state has changed while Layer-2 has zero or one of the required two witnesses.

Its printed recovery is not executable:

```text
$ uv run gz obpi sync
exit=2
BLOCKERS: gz obpi sync: error: the following arguments are required: obpi

$ uv run gz validate --ledger
exit=0
Validated: ledger

✓ All validations passed (1 scopes).
```

The second command cannot repair or detect the missing event pair.

## 7. Claimed-but-not-real commands and citations

The brief’s invariant demo does not test the gate. Its target is already retired:

```text
$ uv run gz content retire AGENTS.md --entry corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00 --attestor "" --reason "probe"
exit=1
Error: corpus entry 'corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00' is already retired.
```

Several printed retry commands are broken:

```text
WS_ATTESTOR COMMAND=gz content retire AGENTS.md --entry <actual-id> --attestor "<your name>"
WS_ATTESTOR RETRY_EXIT=2
WS_ATTESTOR RETRY_FIRST_LINE=BLOCKERS: gz content retire: error: the following arguments are required: --reason

WS_REASON COMMAND=gz content retire AGENTS.md --entry <actual-id> --reason "<why>"
WS_REASON RETRY_EXIT=1
WS_REASON RETRY_FIRST_LINE=Error: corpus entry ... is tier='invariant' ... requires BOTH a named --attestor and a --reason
```

Literal process execution confirms the first failure:

```text
$ uv run gz content retire AGENTS.md --entry corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00 --attestor g0
exit=2
BLOCKERS: gz content retire: error: the following arguments are required: --reason
```

REQ-08’s required documentation event does not exist, although CLI alignment passes:

```text
MANPAGE_ARTIFACT_EDITED_COUNT=0
IDS=[]

$ uv run gz validate --cli-alignment
Validated: cli_alignment

✓ All validations passed (1 scopes).
```

The `AGENTS.md § Operator Doctrine` citation resolves:

```text
336:## Operator Doctrine (verbatim canon)
355:- ATTESTATION GRANULARITY FOR THE CONTENT SURFACE ...
```

But the cited section says attestation on add/remove is “RECORDED PROVENANCE, never a blocking gate,” while parent ADR Decision item 2 says invariant retirement is fail-closed. Thus the citation exists but exposes unresolved canon disagreement; it does not cleanly support the implemented blocking gate.

The referenced [.claude/rules/guardrail-feedback-prose.md](/Users/jeff/Documents/Code/gzkit/.claude/rules/guardrail-feedback-prose.md:28) exists and explicitly requires “a runnable command or named ceremony.” The broken commands above violate that section.
