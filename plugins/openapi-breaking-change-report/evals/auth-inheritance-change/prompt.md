---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our old spec had no root security and GET /reports had no security key. The new spec adds a root `security: [{bearerAuth: []}]` and leaves GET /reports unchanged, while GET /health now has `security: []`. What breaks for clients?
