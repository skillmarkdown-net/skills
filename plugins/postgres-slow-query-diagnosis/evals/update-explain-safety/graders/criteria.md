---
type: llm
---

PASS if Warns that EXPLAIN ANALYZE actually executes the UPDATE and gives a BEGIN; SET LOCAL statement_timeout/lock_timeout; EXPLAIN (ANALYZE, BUFFERS) ...; ROLLBACK; wrapper, optionally WAL, and suggests plain EXPLAIN or a staging copy as alternatives.
FAIL if Says it is safe to run EXPLAIN ANALYZE directly, or omits the rollback wrapper.
