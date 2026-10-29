---
type: llm
---

PASS if Flags High workflow_run executing artifact content with secrets, missing check of workflow_run.event/conclusion and branch filter, write-all permissions, and proposes treating artifacts as data with narrow permissions, in a table with diffs.
FAIL if Treats workflow_run as inherently safe or misses the artifact execution.
