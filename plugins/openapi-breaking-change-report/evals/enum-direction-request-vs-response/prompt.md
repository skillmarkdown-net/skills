---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

We added the value `paused` to the `Status` enum in our OpenAPI spec. It is used in the response of GET /jobs and ALSO as a query filter on GET /jobs?status=. Is that a breaking change?
