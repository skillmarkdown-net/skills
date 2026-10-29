---
type: llm
---

PASS if Reports a likely rename of /pets to /animals (heuristic) as breaking for both operations, says 3.2.0 is an under-bump and recommends MAJOR (or a new /v2 prefix if the API versions by URL), and includes migration notes with old and new paths.
FAIL if Treats it as two removals plus two safe additions with no link, or calls it a MINOR change.
