# Version notes

Supported majors at time of writing: 14 to 18 (18 released 2025-09-25). Confirm against the live docs.

| Feature | Version |
|---|---|
| EXPLAIN option SETTINGS | 12 |
| EXPLAIN option WAL | 13 |
| HashAggregate disk usage in EXPLAIN | 13 |
| Memoize node | 14 |
| Expression statistics (CREATE STATISTICS on expressions) | 14 |
| EXPLAIN GENERIC_PLAN | 16 |
| pg_stat_io | 16 |
| EXPLAIN SERIALIZE, MEMORY | 17 (recalled; verify) |
| BUFFERS included automatically with ANALYZE | 18 |
| Fractional actual rows (`rows=100.00`) | 18 |
| Disabled nodes shown in EXPLAIN ANALYZE | 18 |
| Skip scan on multicolumn B-tree, better OR/IN index use | 18 |
| Asynchronous I/O (`io_method`) | 18 |
| Planner statistics preserved across pg_upgrade | 18 |
| `Index Searches: N` line on index scans | 18 (recalled; verify on a real instance) |

Defaults worth knowing: `work_mem` 4MB, `hash_mem_multiplier` 2.0 on current versions (1.0 in PG13; changed in PG15), `default_statistics_target` 100, `random_page_cost` 4.0, `join_collapse_limit` 8, `jit_above_cost` 100000, `max_parallel_workers_per_gather` 2.

Before PG18: run `ANALYZE` after a major upgrade (for example `vacuumdb --all --analyze-in-stages`).
