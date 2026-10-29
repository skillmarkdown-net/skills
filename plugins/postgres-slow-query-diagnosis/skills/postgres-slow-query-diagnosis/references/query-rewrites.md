# Query pitfalls and rewrites

## Non-sargable predicates

| Pattern | Rewrite |
|---|---|
| `WHERE date(created_at) = '2025-01-01'` | `created_at >= '2025-01-01' AND created_at < '2025-01-02'` |
| `WHERE lower(email) = $1` | Expression index `ON t (lower(email))` (query must match exactly), or store normalized |
| `WHERE col + 1 = 10` | `col = 9` |
| `WHERE col::text = '5'` | Compare in the column's own type: `col = 5` |
| numeric parameter vs int column, or text vs varchar | Cast the parameter, not the column; match types |

## LIKE and pattern matching

- `LIKE 'abc%'` uses a B-tree only if the database collation is C, or the index uses `text_pattern_ops` / `varchar_pattern_ops`.
- Case-insensitive prefix: index `(lower(col) text_pattern_ops)` and query `lower(col) LIKE 'abc%'`.
- `LIKE '%abc%'`, `ILIKE`, regex: `CREATE EXTENSION pg_trgm;` then `CREATE INDEX CONCURRENTLY ... USING gin (col gin_trgm_ops);`. Trigram indexes do not help with 1-2 character patterns.

## OR

- ORs across different columns can use BitmapOr only if each branch has its own usable index; otherwise a seq scan.
- Rewrites: `col = ANY(ARRAY[...])` or `IN`; `UNION ALL` with a second branch that excludes overlap (for example `AND a IS DISTINCT FROM ...` or the negation of the first branch).
- PG18 improves OR and IN planning with indexes: retest on 18 before rewriting.

## Other rewrites

- `NOT IN (subquery)` cannot become an anti-join when NULLs are possible: use `NOT EXISTS`.
- Deep `OFFSET n`: keyset pagination, `WHERE (created_at, id) < ($1, $2) ORDER BY created_at DESC, id DESC LIMIT 50` with a matching index.
- `SELECT *` defeats index-only scans and widens rows; select needed columns.
- `count(*)` on huge tables is a full scan; use an approximate count (`reltuples`) if exactness is not required, or maintain a counter.
- Correlated subquery in the SELECT list may run per row: rewrite as a join or `LATERAL`.
- CTEs: since PG12, non-recursive, side-effect-free CTEs referenced once are inlined. Use `AS MATERIALIZED` to force a fence or `AS NOT MATERIALIZED` to force inlining.
- `join_collapse_limit` and `from_collapse_limit` (default 8): raising them is a last resort.
- Memoize (PG14+) can speed repeated inner index lookups; absence is not a bug.

## After any rewrite

Prove result equivalence: compare row counts and checksums, or `(old EXCEPT new) UNION ALL (new EXCEPT old)` returns zero rows.
