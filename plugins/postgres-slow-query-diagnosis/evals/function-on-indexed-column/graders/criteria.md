---
type: llm
---

PASS if Explains that functions on columns (date(created_at), lower(email)) make the predicates non-sargable; rewrites to a created_at range (>= '2025-03-01' AND < '2025-03-02'); proposes CREATE INDEX CONCURRENTLY on lower(email) matching the expression exactly; mentions ANALYZE after and verifying with buffers.
FAIL if Says to just add another index on the same columns, or proposes an expression index that does not match the query, or omits CONCURRENTLY.
