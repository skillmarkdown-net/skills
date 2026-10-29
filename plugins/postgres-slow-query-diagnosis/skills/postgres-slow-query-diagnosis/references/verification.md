# Verifying an improvement safely

1. **Baseline.** `EXPLAIN (ANALYZE, BUFFERS, SETTINGS) <query>;` and save the full text. Add `WAL` for DML. Wrap DML:
   ```sql
   BEGIN;
   SET LOCAL statement_timeout = '30s';
   SET LOCAL lock_timeout = '2s';
   EXPLAIN (ANALYZE, BUFFERS) UPDATE ...;
   ROLLBACK;
   ```
2. **Realistic environment.** Use a staging copy or replica with production-sized data and statistics. Tiny dev data produces misleading plans.
3. **Hypothetical index (optional).** The third-party `hypopg` extension: `SELECT * FROM hypopg_create_index('CREATE INDEX ON t (a)');` then plain `EXPLAIN` only (not ANALYZE). Check compatibility with your PG version.
4. **Build for real** with `CREATE INDEX CONCURRENTLY`, then `ANALYZE`.
5. **Re-run 3 or more times**, cold and warm. Compare:
   - shared hit + read buffers and temp blocks (far less noisy than time)
   - actual rows (should be unchanged)
   - Execution Time as the secondary signal
6. **Result equivalence** for rewrites: same row count and checksum, or `EXCEPT` both ways.
7. **Workload impact** with `pg_stat_statements`: compare `mean_exec_time`, `total_exec_time`, `calls`, `shared_blks_read`, `temp_blks_written` before and after (use `pg_stat_statements_reset()` only if the owner agrees).
8. **Regressions:** watch other queries, write latency, index size (`pg_relation_size`).
9. **Rollback ready:** `DROP INDEX CONCURRENTLY`. Roll out settings per session first, then per role (`ALTER ROLE ... SET`), and globally only with evidence.

## Production capture

`auto_explain` logs plans of slow queries: `auto_explain.log_min_duration`, `log_analyze`, `log_buffers`, `log_timing` (off to cut overhead), `log_nested_statements`, `sample_rate`. Use sampling when `log_analyze` is on.

Also useful: `track_io_timing = on` (adds read times to BUFFERS), `pg_stat_io` (PG16+), `log_temp_files = 0` and `pg_stat_database.temp_files/temp_bytes` to find spillers.
