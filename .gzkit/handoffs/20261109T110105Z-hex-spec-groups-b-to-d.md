---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-09T11:01:05Z'
agent: claude-code
continues_from: .gzkit/handoffs/20261108T213120Z-house-style-hex-spec-next.md
---

## Current State Summary

The hexagonal specification R&D run (house-style disposition row 7(c), gz-rnd skill) continued through groups B, C and D. Record: `docs/rnd/hexagonal-specification.md`. Commits this session: `e801c26ac`, `ca71c72ba`, `df0719fe6`, all pushed. The run is mid-frontier: group E opened with the config question (who may read config), which was put and not yet answered. The frontier is open, rows 1 to 6 of the disposition map are empty, and the close (restated challenge, review.md, sign-off) is not started.

## Important Context

- One question at a time, stated first in one sentence, with a recommendation and a rating against the constellation (4/4 hexagonal: Cockburn, Montenegro, Cosmic Python, Khorikov; 6/6 once DDD enters, adding Evans and Khononov). Favour Montenegro unless there is reason to disagree.
- Licensed sources never land in the repo: the Montenegro MEAP, Khorikov and Evans reports are held in the session scratchpad outside the repo, and only short cited key notes enter the record. The licensed PDFs carry a watermark: never copy a name or email from them. Kindle books (Khononov, Cockburn's book) reach the run only as passages the operator pastes; do not work around DRM.
- Two agent citations were wrong this session and corrected in place (Montenegro converts in the handler, not the adapter; no ruled import table existed). Read the source pages before citing a position.
- Ask before each commit and before each push unless the operator says both; the auto-mode classifier refused a push the operator had not asked for.
- The run executes nothing: every consequence is carried to the disposition map. Canon rule 7 and the canon page stay unchanged until a row-level go.
- The mx-session lease expired (MX session 57346836); renew or exit only through gz-mx on the operator's word.

## Decisions Made

- [operator-ruled] One kernel package, a sibling of `core/`, stdlib and Pydantic only, holding no gzkit governance concept; the piece adopters build on (verbatim: "ok").
- [operator-ruled] Value objects are frozen Pydantic models, and a value's rules are methods on its type (verbatim: "yes, A").
- [operator-ruled] Entities are frozen; each change returns a new version with its recorded event (verbatim: "yes, B").
- [operator-ruled] Driving adapters never import the domain; commands and queries carry primitives with their own `create`; the handler converts into value objects (verbatim: "if this constrains vibe coding, then it is worth doing" and "but, yes, let's do A").
- [operator-ruled] The dependency rules are enforced by gzkit's own stdlib import test, widened to every region the package map names and shipped in the kernel (verbatim: "yes, fortify what gzkit already does.").
- [operator-ruled] The per-region dependency table after Montenegro Table 6.1, repository Protocols in the domain, other driven ports DTO-only (verbatim: "yes, and we strongly recommend adopters do this.").
- [operator-ruled] rhea is gzkit's proving ground (verbatim: "rhea is gzkit's proving ground.").
- [operator-ruled] Rebuilding from the ledger never validates and only the repository adapter may call it; every tightened rule declares its strategy for old state, defaulting to revalidate on next change (verbatim: "go with recommendations").
- [operator-ruled] The run keeps its method after the accepted-recommendation check (verbatim: "carry on").
- [operator-ruled] Stored shapes are separate models in their repository adapter with a two-way mapper; closed sets in the domain are `enum.StrEnum` (verbatim: "yes, A and we'd normalize to enums").
- [operator-ruled] Canonical on write, tolerant on read (verbatim: "agree ==> yes, canonical on write and tolerant on read.").
- [operator-ruled] Widening a closed set needs a recorded ruling, witnessed by a shrink-only baseline (verbatim: "yes to this too").
- [operator-ruled] A DTO is a frozen Pydantic model with types and no domain rules (verbatim: "agree with your yes to DTOs").
- [operator-ruled] A command bus and a query bus in the kernel (verbatim: "yes to bus").
- [operator-ruled] The kernel ships ValueObject, Entity, DomainEvent, Command, Query and Dto bases, cross-checked against region by the test (verbatim: "yes").
- [operator-ruled] Decorator kinds are mapped to regions; a decorator never makes a business decision; parameterised decorators state their contract (verbatim: "yes ==> does gzkit adopt this map of decorator kinds to regions, under that rule?").
- [operator-ruled] A decorator opportunity review is row 7(b) (verbatim: "yes: shall I add the decorator opportunity review to row 7 as (b)?").
- [operator-ruled] A domain event and a ledger event are one fact in two shapes (verbatim: "agree and this should bring much better cohesion and discipline").
- [operator-ruled] Every ledger event type belongs to an entity, and no type leaves the ledger (verbatim: "yes, you example above means strict! A" and "we will NOT  leave the ledger").
- [operator-ruled] Follow-on reactions are bus listeners dispatched after the ledger append (verbatim: "yes, A").
- [operator-ruled] New use cases are built outside-in, test first; brownfield code enters by the five-phase migration (verbatim: "do, and we are going to need this, big time").

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with `uv run gz handoff decide`.
2. On the operator's go, resume the run under gz-rnd: append a decision entry quoting the resume words, check the record against git, and recompute the frontier.
3. Put the open config question again: config read only at startup by the configurator through a config adapter, merged (gzkit defaults, adopter overrides), validated into frozen settings and passed as values (59 modules read config files today).
4. Continue group E (integration events and external contracts, bootstrapping and what `gz init` scaffolds), then F (enforcement, uv-build, architecture tests, BDD/TDD and mocking detail) and G (transforming gzkit).
5. When the operator pastes Khononov's passages (ch. 3, ch. 4, aggregates and event sourcing), take aggregates and bounded contexts, including assigning each of the 78 ledger event types an owning entity and a drydock name.

## Pending Work / Open Loops

- Open question: the config ruling (put, unanswered).
- Held for the bounded-context question: the ontology's DDD role; how "one team per context" applies to one operator and many agents; the 78 event types' owners and names.
- Held for the disposition map: gzkit consuming rhea in its repository adapters (agent recommended not now; revisit when rhea ships a write side or gzkit needs several backends); rhea's runtime `py-gzkit` dependency belongs in dev dependencies (row 2, in rhea); whether `@advances` fulfils its declared intent (row 2); the closed-set widening rule and validator (row 4, commissioned); the proving-ground work in rhea (route open).
- Consequences carried from earlier sessions, unexecuted: rule 7 and the canon page rewritten; the formatter port; the airlock split; GzkitError leaves core and pythonic.md Error Handling is revised; Harness-Purity renamed; ADR-pool.hexagonal-folder-structure-realization read before cited; the migration through a classic ADR.
- Disposition rows 1 to 6 empty; the close not started. The kernel's name must not be Shared Kernel, which in Evans means jointly owned domain.
- Other house-style rows and both drydock change orders wait for the operator's go on each.

## Verification Checklist

- `git log --oneline -4` shows `df0719fe6` and the handoff commit on main, level with origin.
- `grep -c '^## decision' docs/rnd/hexagonal-specification.md` counts the decision entries; the newest is the outside-in build order.
- `grep -n '| 7 |' docs/rnd/hexagonal-specification.md` shows row 7 commissioned with (a) and (b).
- `uv run gz handoff rulings --search "kernel"` returns this session's booked rulings.

## Evidence / Artifacts

- `docs/rnd/hexagonal-specification.md`
- `docs/rnd/hexagonal-specification/sources/cosmic-python-reading-2026-11-08.md`
- `src/gzkit/core/models.py`
- `src/gzkit/schemas/obpi.json`
- `src/gzkit/commands/obpi_complete.py`
- `tests/policy/test_import_boundaries.py`

## Settled Rulings

2134 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
