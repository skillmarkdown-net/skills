---
type: llm
---

PASS if Identifies the 12x underestimate on orders (est 2,000,000 vs actual 24,000,000), notes the seq scan is justified because about 96% of rows are read so no index is needed, flags the HashAggregate spill (Batches 5, Disk Usage, temp blocks), suggests ANALYZE/stats check and a per-query work_mem via SET LOCAL (not global), and gives a verification plan comparing buffers and temp blocks.
FAIL if Recommends an index on created_at as the main fix, advises raising global work_mem, or ignores the temp/spill evidence and the estimate gap.
