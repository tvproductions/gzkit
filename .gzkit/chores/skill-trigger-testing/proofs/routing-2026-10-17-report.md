# Routing read, skill descriptions cut to one sentence (drydock RO-1 act c)

Record, 2026-10-17. WP-16 effectiveness read for the description cut.

| Set | Description chars (62 skills) | Routed to expected skill | Correct "none" |
|---|---|---|---|
| before | 13,229 | 122 / 124 | 6 / 10 |
| after, first draft | 5,879 | 120 / 124 | 7 / 10 |
| after, as landed | 5,938 | 122 / 124 | 7 / 10 |

Method: the 134 goals of `trigger-basket-2026-10-10.json`, each routed blind by one
sonnet pass that saw only its description list and the goal text. One sample per set;
the figures say no more than that.

The first draft lost three goals, all to vocabulary the cut removed: `gz-airlock`
("seam map", "disturbed", G040 and G111) and `gz-plan` ("pool ADR", G061). Both
descriptions regained those words and the landed set routes as the uncut one did.
The before and landed sets miss the same two goals, G016 (`gz-state`, routed to
`gz-ontology`) and G074 (`gz-adr-audit`, routed to `gz-adr-emit-receipt`); the first
draft happened to route G016 correctly. Inputs and picks: the `routing-2026-10-17-*`
files beside this report.
