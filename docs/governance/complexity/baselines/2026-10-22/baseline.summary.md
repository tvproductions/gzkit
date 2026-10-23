# Complexity Baseline Summary

- Corpus revision: 1
- Corpus schema version: 1.0.0
- Tool versions:
    - cohesion: 1.2.0
    - lizard: 1.24.1

## django

- Commit SHA: `50bbf71bbd51616e2ce48785336ca3746fbe5f24`
- Archetypal cell: 1

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 85.0 | 208.0 | 361.6 | 568.7 | 1007.22 | 99 |
| lizard_nloc | 5.0 | 10.0 | 19.0 | 28.0 | 49.66 | 1668 |
| lizard_param_count | 2.0 | 2.0 | 4.0 | 4.0 | 8.0 | 1668 |
| lizard_nesting_depth | 1.0 | 2.0 | 4.0 | 5.0 | 10.0 | 1668 |
| lizard_ccn | 2.0 | 3.0 | 6.0 | 8.65 | 16.0 | 1668 |
| cohesion_lcom4 | 20.83 | 50.0 | 100.0 | 100.0 | 100.0 | 316 |

## starlette

- Commit SHA: `7793b925a88ed98f3482325b0eca00b433123030`
- Archetypal cell: 2

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 103.0 | 169.25 | 394.1 | 524.2 | 614.28 | 34 |
| lizard_nloc | 4.0 | 10.0 | 22.0 | 29.7 | 39.0 | 487 |
| lizard_param_count | 2.0 | 3.0 | 4.0 | 6.0 | 11.14 | 487 |
| lizard_nesting_depth | 0.0 | 2.0 | 3.0 | 4.0 | 7.14 | 487 |
| lizard_ccn | 2.0 | 3.0 | 5.0 | 8.0 | 13.14 | 487 |
| cohesion_lcom4 | 40.0 | 78.335 | 100.0 | 108.5 | 149.4999 | 104 |

## urllib3

- Commit SHA: `e90af45bb006c3a452a3a21644a2681523f5c7fc`
- Archetypal cell: 3

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 142.0 | 288.0 | 686.0 | 800.4 | 945.68 | 17 |
| lizard_nloc | 7.0 | 16.0 | 34.0 | 51.2 | 87.08 | 257 |
| lizard_param_count | 2.0 | 3.0 | 5.0 | 7.2 | 16.88 | 257 |
| lizard_nesting_depth | 1.0 | 3.0 | 6.0 | 9.0 | 12.0 | 257 |
| lizard_ccn | 2.0 | 5.0 | 9.0 | 15.0 | 24.0 | 257 |
| cohesion_lcom4 | 15.48 | 40.0 | 62.5 | 70.835 | 85.5 | 31 |

## click

- Commit SHA: `fed9049f7a07550d560a91b30c5b0b3e17d54981`
- Archetypal cell: 4

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 326.0 | 721.0 | 1318.6 | 1517.8 | 1677.16 | 5 |
| lizard_nloc | 7.0 | 13.0 | 26.0 | 31.9 | 64.0 | 262 |
| lizard_param_count | 2.0 | 3.0 | 4.0 | 5.95 | 14.56 | 262 |
| lizard_nesting_depth | 1.0 | 2.0 | 5.0 | 7.0 | 10.78 | 262 |
| lizard_ccn | 2.0 | 4.75 | 8.0 | 11.0 | 23.73 | 262 |
| cohesion_lcom4 | 14.7 | 58.5425 | 100.0 | 100.0 | 100.0 | 54 |

## attrs

- Commit SHA: `69a9729a6879b37cee4930c85017da5dbc5fb6dd`
- Archetypal cell: 5

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 137.0 | 323.0 | 1375.4 | 1726.2 | 2006.84 | 5 |
| lizard_nloc | 6.0 | 13.0 | 28.4 | 44.8 | 97.4 | 173 |
| lizard_param_count | 2.0 | 3.0 | 4.0 | 8.4 | 20.56 | 173 |
| lizard_nesting_depth | 1.0 | 2.0 | 5.0 | 6.0 | 20.12 | 173 |
| lizard_ccn | 2.0 | 3.0 | 7.8 | 9.4 | 35.56 | 173 |
| cohesion_lcom4 | 50.0 | 75.0 | 100.0 | 100.0 | 100.0 | 25 |

## cpython-stdlib-subset

- Commit SHA: `246fe14e7ccfdea62c7d92b49a272abd55acc850`
- Archetypal cell: 6

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| lizard_nloc | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| lizard_param_count | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| lizard_nesting_depth | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| lizard_ccn | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |
| cohesion_lcom4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 |

## hypothesis

- Commit SHA: `84f92dcf29229e37f822ba3ba5eea4212d2abf35`
- Archetypal cell: 7

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 130.5 | 402.5 | 873.5 | 1094.25 | 1609.45 | 46 |
| lizard_nloc | 5.0 | 13.0 | 26.0 | 44.0 | 109.2 | 1041 |
| lizard_param_count | 2.0 | 2.0 | 4.0 | 5.0 | 6.0 | 1041 |
| lizard_nesting_depth | 1.0 | 2.0 | 5.0 | 8.0 | 18.2 | 1041 |
| lizard_ccn | 2.0 | 4.0 | 8.0 | 13.0 | 31.0 | 1041 |
| cohesion_lcom4 | 40.74 | 70.835 | 100.0 | 100.0 | 100.0 | 143 |

## rich

- Commit SHA: `46cebbb032f920eb096efbaf23cdc6fe9dd541f7`
- Archetypal cell: 8

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 820.5 | 1074.5 | 1425.0 | 1570.0 | 1686.0 | 6 |
| lizard_nloc | 7.0 | 17.0 | 31.0 | 42.9 | 101.62 | 352 |
| lizard_param_count | 2.0 | 3.0 | 6.9 | 10.0 | 17.98 | 352 |
| lizard_nesting_depth | 1.0 | 2.0 | 5.0 | 7.0 | 14.49 | 352 |
| lizard_ccn | 2.0 | 4.0 | 8.0 | 12.0 | 22.43 | 352 |
| cohesion_lcom4 | 28.34 | 75.0 | 100.0 | 100.0 | 100.0 | 49 |

## mypy

- Commit SHA: `0ea16df0c86243e095b4aab1b45e0179dd4c3f14`
- Archetypal cell: 9

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 3709.0 | 6214.0 | 6598.6 | 6726.8 | 6829.36 | 5 |
| lizard_nloc | 7.0 | 14.0 | 29.0 | 45.0 | 93.39 | 1588 |
| lizard_param_count | 2.0 | 3.0 | 4.0 | 6.0 | 9.0 | 1588 |
| lizard_nesting_depth | 1.0 | 2.25 | 5.0 | 9.0 | 18.13 | 1588 |
| lizard_ccn | 2.0 | 5.0 | 10.0 | 16.0 | 36.26 | 1588 |
| cohesion_lcom4 | 25.0 | 35.71 | 69.26 | 100.0 | 100.0 | 164 |

## flit

- Commit SHA: `ef7f31925305a50bd097f06b913717192490ad44`
- Archetypal cell: 10

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 52.5 | 170.0 | 326.0 | 550.75 | 650.95 | 36 |
| lizard_nloc | 10.0 | 17.0 | 28.0 | 40.0 | 80.56 | 217 |
| lizard_param_count | 1.0 | 2.0 | 3.0 | 4.0 | 7.0 | 217 |
| lizard_nesting_depth | 2.0 | 3.0 | 6.0 | 8.0 | 17.68 | 217 |
| lizard_ccn | 3.0 | 6.0 | 9.0 | 13.0 | 22.84 | 217 |
| cohesion_lcom4 | 5.73 | 43.75 | 70.836 | 95.0 | 100.0 | 29 |

## textual

- Commit SHA: `5fdea0dd0538451399762dcb75efefde7f6ddcdc`
- Archetypal cell: 8

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 1037.0 | 2714.0 | 2852.0 | 2898.0 | 2934.8 | 5 |
| lizard_nloc | 5.0 | 12.0 | 23.0 | 31.4 | 57.34 | 667 |
| lizard_param_count | 2.0 | 2.0 | 4.0 | 7.0 | 11.0 | 667 |
| lizard_nesting_depth | 1.0 | 2.0 | 4.0 | 5.0 | 10.34 | 667 |
| lizard_ccn | 2.0 | 4.0 | 6.0 | 8.0 | 18.0 | 667 |
| cohesion_lcom4 | 0.0 | 0.74 | 63.556 | 90.001 | 100.0 | 39 |

## flask

- Commit SHA: `7374c85ddefc3f4b177a698ab9f0cbb6a5c0b392`
- Archetypal cell: 1

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 92.0 | 158.0 | 473.6 | 578.8 | 662.96 | 5 |
| lizard_nloc | 6.0 | 12.0 | 20.7 | 40.55 | 56.7 | 84 |
| lizard_param_count | 2.0 | 3.0 | 4.0 | 4.0 | 11.0 | 84 |
| lizard_nesting_depth | 1.0 | 2.0 | 4.0 | 5.85 | 7.34 | 84 |
| lizard_ccn | 2.0 | 4.0 | 6.7 | 8.0 | 13.51 | 84 |
| cohesion_lcom4 | 4.48 | 25.835 | 50.0 | 75.0 | 95.0 | 11 |

## pip

- Commit SHA: `4943e17e7dd079b3f58e88009d10308f2c55a3ed`
- Archetypal cell: 10

| Metric | p50 | p75 | p90 | p95 | p99 | n |
|---|---|---|---|---|---|---|
| lizard_file_nloc | 88.0 | 339.0 | 487.0 | 523.0 | 661.2 | 41 |
| lizard_nloc | 7.0 | 15.0 | 27.0 | 39.9 | 78.34 | 512 |
| lizard_param_count | 2.0 | 3.0 | 4.0 | 5.0 | 8.0 | 512 |
| lizard_nesting_depth | 1.0 | 2.0 | 5.0 | 6.45 | 12.0 | 512 |
| lizard_ccn | 2.0 | 4.0 | 7.0 | 11.0 | 18.0 | 512 |
| cohesion_lcom4 | 25.0 | 55.0 | 78.332 | 100.0 | 100.0 | 67 |

## Cross-Project Aggregate

| Metric | p50 | p75 | p90 | p95 | p99 | inter-project variance | projects |
|---|---|---|---|---|---|---|---|
| lizard_file_nloc | 105.0 | 307.25 | 716.5 | 1031.9 | 3130.24 | 1085300.657197 | 13 |
| lizard_nloc | 6.0 | 13.0 | 25.0 | 37.0 | 77.0 | 2.424242 | 13 |
| lizard_param_count | 2.0 | 3.0 | 4.0 | 5.0 | 11.0 | 0.083333 | 13 |
| lizard_nesting_depth | 1.0 | 2.0 | 5.0 | 7.0 | 14.0 | 0.181818 | 13 |
| lizard_ccn | 2.0 | 4.0 | 8.0 | 11.0 | 25.0 | 0.083333 | 13 |
| cohesion_lcom4 | 25.0 | 55.14 | 100.0 | 100.0 | 100.0 | 242.446209 | 13 |
