---
type: llm
---

PASS if Classifies the RDS entry as a replace (not just a delete), HIGH severity stateful, includes reason replace_because_cannot_update and the engine path, verdict NO-GO with what to confirm (backup, intent).
FAIL if Only checks for ["delete"] and misses the replace, or says GO.
