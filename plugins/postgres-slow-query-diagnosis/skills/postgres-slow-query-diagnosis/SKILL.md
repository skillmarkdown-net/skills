---
name: postgres-slow-query-diagnosis
description: "Diagnoses slow PostgreSQL queries from EXPLAIN (ANALYZE, BUFFERS) output and query text: seq scans, bad row estimates, nested loops, disk spills, unused indexes, non-sargable filters. Proposes indexes, rewrites, settings and safe verification. Use when a user pastes an EXPLAIN plan, asks why a Postgres query is slow, or mentions pg_stat_statements, work_mem, CREATE INDEX CONCURRENTLY or ANALYZE."
---

# PostgreSQL Slow Query Diagnosis

Turn an EXPLAIN (ANALYZE, BUFFERS) plan plus the query text into a ranked diagnosis, concrete fixes, and a safe verification plan. Find the root cause, not the most visible symptom.

## Steps

1. **Establish context before judging.** Ask for or infer: PG major version (`SELECT version();`), table sizes, whether the query uses bind parameters, and whether the plan came from production-sized data. If the plan is plain `EXPLAIN` with no ANALYZE, say that only estimates are available and no speedup can be claimed. If a version is unknown, do not rely on PG17/18 fields (see [references/version-notes.md](references/version-notes.md)).

2. **Run the parser if the plan is text.** Save the plan to a file and run `python scripts/plan_flags.py plan.txt`. It prints per-node flags: estimate vs actual (times loops), spills, lossy bitmaps, heap fetches, filters removing many rows, JIT, disabled nodes. Treat its output as leads to confirm by reading the plan, not as the verdict. It accepts integer and fractional row counts (`rows=100.00`, PG18).

3. **Read the plan bottom-up.**
   - Actual time and rows are per-loop averages. Multiply by `loops` for totals.
   - Compare estimated `rows=` with `actual rows x loops`. A 10x or greater gap is a flag (heuristic, not an official threshold). Find the **lowest** node where the error first appears; errors propagate upward.
   - Find the node with the largest share of total time (own time = node time minus children, times loops). Fix that node first.
   - Check the top of the plan: `Planning Time`, `Execution Time`, `JIT:` block, `Workers Planned` vs `Workers Launched`, and `Settings:` (non-default planner GUCs such as `enable_seqscan = off` left on by someone).

4. **Classify each finding** using [references/plan-symptoms.md](references/plan-symptoms.md). Key decision rules:
   - **Seq scan:** only a problem if the table is large AND the filter is selective (roughly the query needs under 5-10% of rows) or `Rows Removed by Filter` dwarfs rows returned. A seq scan chosen because of a bad estimate is an estimate problem, not an index problem.
   - **Nested loop on big inputs:** usually an underestimated outer side. Fix the estimate first (step 5), then reconsider joins.
   - **Spill:** any `temp read/written` in Buffers, `Sort Method: external merge Disk: NkB`, or hash `Batches` > 1 means work_mem was too small for that node. HashAggregate shows `Disk Usage` too.
   - **Bitmap:** `Heap Blocks: lossy` or high `Rows Removed by Index Recheck` means the bitmap exceeded work_mem.
   - **Index Only Scan with large `Heap Fetches`:** the visibility map is stale; VACUUM the table.
   - **Buffers:** `shared read` is disk/OS cache, `shared hit` is cache. Large `shared hit` with slow time and a tiny result points to wasted work (filter, recheck, loops), not I/O.
   - **Per-trigger time** at the end of a DELETE/UPDATE plan usually means an unindexed foreign key column on the referencing table.

5. **Check statistics when estimates are off.**
   ```sql
   SELECT relname, last_analyze, last_autoanalyze, n_mod_since_analyze, n_live_tup
   FROM pg_stat_user_tables WHERE relname = 'tbl';
   ```
   Then, in order: `ANALYZE tbl;` and re-plan; raise `ALTER TABLE t ALTER COLUMN c SET STATISTICS 500; ANALYZE t;` (default target is 100); for correlated columns `CREATE STATISTICS s (dependencies, ndistinct, mcv) ON a, b FROM t; ANALYZE t;` (mcv needs PG12+; expression statistics need PG14+). Partitioned parents are never auto-analyzed: run `ANALYZE parent`. Temp tables are never autovacuumed: ANALYZE after loading. On huge tables lower `autovacuum_analyze_scale_factor` per table (for example 0.01). Before PG18, ANALYZE after a major `pg_upgrade`.

6. **Inspect the query text for pitfalls** (full list with rewrites in [references/query-rewrites.md](references/query-rewrites.md)): functions or casts on indexed columns, implicit type casts, `LIKE '%x'`, `ILIKE`, OR across columns, `NOT IN (subquery)`, deep OFFSET, `SELECT *` blocking index-only scans, correlated subqueries in the SELECT list, CTE materialization.

7. **Propose fixes, cheapest and safest first:** (a) ANALYZE / statistics, (b) query rewrite, (c) index, (d) per-query settings, (e) global settings last. For indexes follow [references/index-design.md](references/index-design.md): equality columns first, then range/sort; partial when the query filters a small constant subset; `INCLUDE` for index-only scans; check `pg_stat_user_indexes.idx_scan` for unused or duplicate indexes before adding more. Always use `CREATE INDEX CONCURRENTLY`, outside a transaction block, with `SET lock_timeout`.

8. **Settings advice.** Set `work_mem` with `SET LOCAL` or `ALTER ROLE ... SET`, never raise it globally (it is per sort/hash node, per query, per session). `Disk: NkB` is a lower bound for the memory needed. Hash nodes get `work_mem x hash_mem_multiplier` (default 2.0 on current versions). `enable_*` settings are diagnostic only, via `SET LOCAL` in a transaction. `random_page_cost` 1.1-2.0 is common on SSD/NVMe; test per session first.

9. **Give a verification plan** (see [references/verification.md](references/verification.md)): baseline saved, staging with production-sized stats, optional hypopg with plain EXPLAIN only, real build, ANALYZE, 3+ runs cold and warm, compare buffers and temp blocks (not just time), result equivalence for rewrites, `pg_stat_statements` before/after, rollback with `DROP INDEX CONCURRENTLY`.

## Output format

Reply with these sections, in order. Keep each finding to the evidence line, the cause, and the fix.

```
## Verdict
One or two sentences: the dominant cause and expected gain.

## Findings (ranked by time share)
1. <node> - <evidence from plan, with numbers> - <cause>

## Fixes
1. <SQL, copy-pasteable> - <why> - <risk/cost>

## Verify
Numbered steps with the exact commands and what to compare.

## Not confirmed
Assumptions and what to check (version, bind parameters, data size).
```

Example (abridged):

```
## Verdict
The 41 s comes from a nested loop driven by a 1,000x row underestimate on orders; fix statistics first, then add a partial index.

## Findings
1. Seq Scan on orders - rows=12 estimated, actual rows=48,000 x loops=1; Rows Removed by Filter 9,952,000 - stale stats on status (n_mod_since_analyze 6.1M).
2. Nested Loop - inner Index Scan on items loops=48,000 (3.1 ms each = 149 s total of node time) - follows from finding 1.

## Fixes
1. ANALYZE orders; - refreshes stats, no locks beyond a light share lock - re-plan before anything else.
2. CREATE INDEX CONCURRENTLY idx_orders_pending ON orders (created_at) WHERE status = 'pending'; - serves the 0.5% subset - write cost small; test with literals and the real driver.

## Verify
1. Save baseline: EXPLAIN (ANALYZE, BUFFERS, SETTINGS) ...
2. After the fix, run 3 times and compare shared hit+read and Execution Time.
```

## Gotchas

- `EXPLAIN ANALYZE` executes the statement. For INSERT/UPDATE/DELETE/MERGE or functions with side effects, give: `BEGIN; SET LOCAL statement_timeout = '30s'; SET LOCAL lock_timeout = '2s'; EXPLAIN (ANALYZE, BUFFERS) ...; ROLLBACK;`.
- PG18 includes BUFFERS automatically with ANALYZE; on PG14-17 write it explicitly. Writing it on 18 is harmless.
- Use `TIMING OFF` when clock overhead distorts many tiny nodes; row counts and buffers stay valid.
- `SERIALIZE` (PG17+) exposes detoasting and output conversion cost that plain ANALYZE hides; suggest it when execution is fast but the client is slow.
- Parameterized queries: use `EXPLAIN (GENERIC_PLAN)` on PG16+; earlier, PREPARE/EXECUTE with `plan_cache_mode`. Partial indexes often fail to match under generic plans.
- PG18 skip scan weakens the old rule that a missing leading column makes a multicolumn index useless; it only pays off when the skipped column has few distinct values. Confirm in the plan (and the `Index Searches` line if present) rather than assuming. PG18 also improves OR/IN index use, so retest before rewriting.
- Expression indexes must match the query expression exactly.
- Do not claim a speedup from plain EXPLAIN, from one warm run, or from cost numbers alone.
- A newly built index needs ANALYZE; an invalid index (`pg_index.indisvalid = false`) after a failed concurrent build must be dropped with `DROP INDEX CONCURRENTLY` and retried.
- Never advise leaving `enable_*` off, or raising global work_mem, as the fix.
- Do not invent numbers: say a threshold is a heuristic when it is.
