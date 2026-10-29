---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

This query takes 38 seconds on Postgres 15. Can you tell me why and what to change?

SELECT c.region, sum(o.total) FROM orders o JOIN customers c ON c.id = o.customer_id WHERE o.created_at >= '2025-01-01' GROUP BY c.region;

EXPLAIN (ANALYZE, BUFFERS):
HashAggregate  (cost=912000.10..912000.20 rows=8 width=40) (actual time=37800.1..37800.2 rows=8 loops=1)
  Group Key: c.region
  Batches: 5  Memory Usage: 4241kB  Disk Usage: 183000kB
  Buffers: shared hit=1200 read=410000, temp read=22000 written=45000
  ->  Hash Join  (cost=1500.00..850000.00 rows=2000000 width=12) (actual time=120.0..30100.0 rows=24000000 loops=1)
        Hash Cond: (o.customer_id = c.id)
        ->  Seq Scan on orders o  (cost=0.00..700000.00 rows=2000000 width=12) (actual time=0.1..14000.0 rows=24000000 loops=1)
              Filter: (created_at >= '2025-01-01'::timestamp)
              Rows Removed by Filter: 1000000
        ->  Hash  (cost=1000.00..1000.00 rows=40000 width=12) (actual time=100.0..100.0 rows=40000 loops=1)
              Buckets: 65536  Batches: 1  Memory Usage: 2100kB
              ->  Seq Scan on customers c  (cost=0.00..1000.00 rows=40000 width=12) (actual time=0.0..60.0 rows=40000 loops=1)
Planning Time: 0.4 ms
Execution Time: 37801.0 ms
