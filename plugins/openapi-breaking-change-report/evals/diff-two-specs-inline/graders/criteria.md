---
type: llm
---

PASS if Flags the new required `owner` query parameter as breaking, `name` becoming optional and nullable on the response as breaking, suggests MAJOR (2.0.0), notes that declared 1.3.0 is an under-bump, and gives migration notes with locations.
FAIL if Calls the change safe or minor, misses the response-side nullable/required change, or does not suggest a semver bump.
