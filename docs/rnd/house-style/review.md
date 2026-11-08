# House style — review account

A readable view over [the run's record](../house-style.md), written for the operator's review before
sign-off. It holds no authority; the record does. Each name is marked **ruled** (the operator's
selection or words), **sourced** (read from a primary source), **contradicted** (a source disagrees)
or **unsourced**.

## The problem

You asked how to express hexagonal design intent strongly, and how to make the model aware of it
when designing, repairing or doing any code work. What exists is weak: a 7 KB rule that loads on
every Python file read, a canon page, and one gate that checks only `core/` and runs only in
`gz check --full` and CI (**sourced**: the rule, the test, `quality.py:1382`). gzkit has no hexagonal
chore. The Astral alliance shows what strong looks like (**sourced**: RP-9, RP-15).

## The model

- **A house style** is a named set of preferences, each carried the RP-9 way wherever a check can
  catch a violation, with its judgment part carried by design-time work and a chore. Prose explains
  and is never the authority (**ruled**, Q1).
- **Membership** is by your ruling, one candidate at a time, with a stated test reported: does it
  shape how every project built with gzkit is designed? Presence in gzkit admits nothing (**ruled**,
  Q6 and your correction).
- **Hexagonal is the first member** (**ruled**, Q7). The other five candidates (the Astral alliance,
  stdlib first, Pydantic, unittest, argparse) await their own rulings.
- **Hexagonal is the whole system**, not the core: core, ports, driving and driven adapters, the
  composition root (**ruled**, your correction; **sourced**: the canon page, gz-skills' audit).
- **The map** of the whole system is drawn up front, every module placed in a region, approved once
  as a classic ADR, kept current: a change to it is a new classic ADR (**ruled**, Q12).
- **Reach into adopters:** every project built with gzkit declares its map; a fresh scaffold starts
  conformant; an existing project is reported, then proven; Not Applicable only with a recorded
  reason (**ruled**, Q3).
- **gzkit itself:** the map covers the whole package; today's out-of-place imports go on a
  shrink-only baseline that closes at zero (**ruled**, Q4). This settles the direction of RP-7's H1.
- **Where it's declared:** facts about how code is designed go in `pyproject.toml` under
  `[tool.py-gzkit]`, beside uv and Ruff; `.gzkit.json` keeps governance settings (**ruled**, Q8 and
  Q15; **sourced**: PEP 518, uv's and Ruff's docs, PyPI).
- **Three reaches into the work** (**ruled**, Q9, your words: *"we really need all three"*):
  1. *the design-time imperative*: a boundary-sensitivity signal computed at intake from each
     outcome's `modules` (**ruled**, Q10), enforced at the work package freeze, where no baseline
     freezes until every module is placed and any map change cites a Current classic ADR
     (**ruled**, Q13);
  2. *airlock guidance*: the door tells the model at entry how the slice sits in the map, and judges
     drift at exit (**sourced**: the airlock's code; see the caveat below);
  3. *chore tidyings*: a periodic implementation audit of what neither gate nor door judges, after
     gz-skills' audit (**sourced**).
- **Route:** corrections of shipped intent (H1, F22) go into the drydock under RP-7; the new
  machinery is built at civil rule, admitted through the R&D door, carried as correction, not
  enhancement (**ruled**, Q14).

**Contradicted:** the canon page calls hexagonal the *"primary code-architecture directive"* and,
in § Departures, *"a conceptual borrowing, not a code-organization rule"*. Row 4(c) reconciles them.

**Caveat on the airlock** (**sourced**, the call sites): no production caller supplies
`parent_invariants` today, and reach is the governance ontology, not Python imports. Feeding the map
in is plausible from the code's shape, not proven. Row 7(b) traces whether that falls short of
ADR-0.33.0's intent.

## What each row would produce

1. **ADR (proposed only; you initiate):** the whole-system map as a classic ADR, once the classic ADR
   form and crossover land (CO-1, CO-2 on RP-6); and the machinery admitted at civil rule as catalog
   outcomes: the map as data, the intake signal, the freeze check, the airlock feed, `gz init`
   delivery.
2. **Direct fix, under RP-7:** H1 booked to the whole package with a baseline; F22 repaired so the
   boundary test runs per change.
3. **Chore (advised; you direct admission):** the hexagonal tidying chore.
4. **Drafts, on your go per item:** the house style named in canon; the hexagonal rule cut to its
   judgment residue; the canon page's contradiction reconciled; the design-time imperative in the
   design surfaces.
5. **Refactoring program (you select its route):** out-of-place imports to zero through the baseline;
   the cognitive ceiling moved to `[tool.py-gzkit]`.
6. **No action:** no folder partitions (canon rule 7; the map is data, not layout); no PyPI
   registration of `gzkit` (your choice of `[tool.py-gzkit]`).
7. **Further research (you open each):** the admission of the other five candidates; an intent trace
   of the airlock's empty invariant channel.

## Your rulings at a glance

Fifteen questions were put. You took the recommendation on most, held two for discussion (Q9, Q10),
corrected the run three times (candidates not members; the config home reopened; the whole system,
not the core), and chose against the recommendation once (Q15). The record keeps each verbatim.
