---
type: llm
---

PASS if Labels LLM06:2025 root causes: excessive functionality (fetch_url, old_debug_shell), excessive permissions (admin account), excessive autonomy (delete_record); recommends removing tools, user-scoped credentials, read-only access, human approval, enforcement in downstream systems; notes the summariser needs read-only; severity ranked.
FAIL if Misses one of the three root causes, suggests prompt instructions as the control, or lacks severity.
