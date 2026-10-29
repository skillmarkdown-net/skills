# Index design rules

## Syntax

```sql
SET lock_timeout = '3s';
CREATE INDEX CONCURRENTLY idx_t_a_b ON t (a, b);            -- composite
CREATE INDEX CONCURRENTLY idx_t_a_inc ON t (a) INCLUDE (b, c); -- covering (PG11+)
CREATE INDEX CONCURRENTLY idx_t_pending ON t (a) WHERE status = 'pending'; -- partial
CREATE INDEX CONCURRENTLY idx_t_email ON t (lower(email));  -- expression
```

## Rules

1. Equality columns first, then the range or ORDER BY column. PG18 skip scan relaxes this only when the leading column has few distinct values; verify in the plan.
2. A partial index is used only if the planner can prove the query WHERE implies the index predicate. Test with literals AND with the real client driver's bind parameters; generic plans often fail to match.
3. Index-only scans need a current visibility map. Check `Heap Fetches`; run VACUUM.
4. `INCLUDE` columns are returned, not searchable. Keep them small; never large text/jsonb.
5. Every index adds write amplification, disk, cache pressure, and blocks HOT updates on indexed columns.
6. Boolean or other low-selectivity single-column indexes are rarely useful unless partial.
7. Index foreign key referencing columns when deletes or updates on the parent are slow.
8. Expression indexes must match the query expression exactly.

## Before adding: look for unused and duplicate indexes

```sql
SELECT relname, indexrelname, idx_scan, pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE relname = 'tbl'
ORDER BY idx_scan;
```

stats reset time matters: confirm the counters cover a full business cycle, and check replicas before dropping.

## CREATE INDEX CONCURRENTLY

- Cannot run inside a transaction block.
- Scans the table twice and waits for older transactions; can be slow on busy systems.
- If it fails or is cancelled it leaves an INVALID index:
  ```sql
  SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;
  ```
  Drop with `DROP INDEX CONCURRENTLY name;` and retry.
- Rebuild with `REINDEX INDEX CONCURRENTLY name;` (PG12+).
- Non-concurrent CREATE INDEX blocks writes for the whole build.
- Run `ANALYZE tbl;` afterwards.
- Rollback: `DROP INDEX CONCURRENTLY name;`
