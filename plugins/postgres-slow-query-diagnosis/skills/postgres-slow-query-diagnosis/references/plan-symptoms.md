# Plan symptoms and likely causes

Heuristics, not official thresholds, unless stated.

| Symptom in plan | Likely cause | First action |
|---|---|---|
| Estimated rows vs actual rows x loops differ 10x or more | Stale stats, correlated columns, expression the planner cannot estimate, generic plan | `ANALYZE`; `SET STATISTICS`; `CREATE STATISTICS`; expression index or expression stats (PG14+) |
| Seq Scan, large table, high `Rows Removed by Filter` | Missing or unusable index, or bad estimate | Check sargability, then index; check estimate first |
| Seq Scan returning more than about 5-10% of the table | Seq scan is correct | Do not add an index; reduce columns or rows read |
| Nested Loop, inner side loops in the thousands | Outer rows underestimated | Fix estimate; then check for join index on inner |
| Hash Join with `Batches` > 1 | Hash exceeded work_mem x hash_mem_multiplier | Raise work_mem for this query via `SET LOCAL`; or raise hash_mem_multiplier |
| `Sort Method: external merge Disk: NkB` | Sort exceeded work_mem | SET LOCAL work_mem above the disk size; or an index that provides the order |
| HashAggregate with `Disk Usage` / `Batches` > 1 | Aggregate spilled (PG13+) | Same as above; reduce grouping cardinality |
| Any `temp read` / `temp written` in Buffers | Spill (sort, hash, Materialize) | Find the node whose own count is non-zero |
| `Heap Blocks: lossy`, high `Rows Removed by Index Recheck` | Bitmap exceeded work_mem | Raise work_mem or make the index more selective |
| Index Only Scan with large `Heap Fetches` | Stale visibility map | `VACUUM tbl`; check autovacuum lag and long transactions |
| Index Scan with large `Rows Removed by Filter` | Index covers only part of the predicate | Extend index columns, or partial index |
| `Workers Launched` < `Workers Planned` | Worker pool exhausted | Check `max_parallel_workers` and concurrency |
| `JIT:` block with large timing on a short query | JIT compile overhead | Test `SET LOCAL jit = off`; consider raising `jit_above_cost` |
| Trigger time at end of DML plan | Unindexed foreign key referencing column | Index the referencing column |
| `Settings:` shows `enable_* = off` | Session was tweaked | Reset it and re-plan |
| Disabled node noted (PG18) | A planner method was forced off | Find which `enable_*` is off |
| Large `shared hit`, tiny result | Wasted work (loops, recheck, filter) | Look at loops and filter removal, not I/O |
| Large `shared read` | Cold cache or data too big for cache | Compare warm runs; check `track_io_timing = on` for read times |
| `Planning Time` large relative to execution | Many partitions, many joins, or extended statistics | Prepared statements, reduce partitions scanned |

## Reading arithmetic

- Node total time = actual total time x loops.
- Node own time = node total minus the sum of its children totals.
- Buffer counts at a node include its children.
- Text format prints only non-zero buffer values.
- Row counts may be fractional on PG18 (`rows=100.00`).
