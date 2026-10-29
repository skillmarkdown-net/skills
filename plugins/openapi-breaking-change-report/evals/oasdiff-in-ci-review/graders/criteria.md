---
type: llm
---

PASS if Checks that oasdiff is available and reads its --help for flags, uses changelog/breaking against the base from main (via git show or a revision), maps ERR/WARN/INFO to breaking/risky/safe, and still applies rename and security checks plus a semver suggestion.
FAIL if Assumes flags without checking, only pastes raw tool output, or skips semver and migration notes.
