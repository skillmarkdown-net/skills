---
type: llm
---

PASS if Explains quotes do not prevent injection because expansion happens before the shell, flags title and body as High, provides a diff moving them into env: and using "$TITLE" and "$BODY".
FAIL if Accepts quoting as protection or suggests only escaping the strings.
