---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Postgres 16. This is slow and there is an index on users(created_at) and one on users(email). Why aren't they used?

SELECT * FROM users WHERE date(created_at) = '2025-03-01' AND lower(email) = 'bob@example.com';

EXPLAIN (ANALYZE, BUFFERS) shows:
Seq Scan on users  (cost=0.00..250000.00 rows=5 width=200) (actual time=900.0..2100.0 rows=1 loops=1)
  Filter: ((date(created_at) = '2025-03-01'::date) AND (lower(email) = 'bob@example.com'::text))
  Rows Removed by Filter: 4999999
  Buffers: shared hit=40 read=124960
Execution Time: 2101.3 ms
