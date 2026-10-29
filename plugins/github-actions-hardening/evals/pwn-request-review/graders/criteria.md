---
type: llm
---

PASS if Flags a Critical pwn request (pull_request_target plus checkout of PR head SHA and npm install), suggests pull_request or removing the ref, notes missing permissions and timeout, includes a findings table and YAML diffs.
FAIL if Says the workflow is fine, or only comments on style, or omits a findings table and diffs.
