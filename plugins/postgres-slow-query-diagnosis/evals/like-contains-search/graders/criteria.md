---
type: llm
---

PASS if Explains a B-tree cannot serve a leading-wildcard ILIKE; proposes pg_trgm with CREATE INDEX CONCURRENTLY ... USING gin (name gin_trgm_ops); notes trigram limits for 1-2 character patterns; advises ANALYZE and verifying with buffers over several runs.
FAIL if Suggests a plain btree or text_pattern_ops index as the fix for a contains search, or suggests disabling seqscan globally.
