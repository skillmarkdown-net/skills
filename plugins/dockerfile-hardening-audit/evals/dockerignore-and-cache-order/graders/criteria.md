---
type: llm
---

PASS if Copies package*.json first, runs npm ci, then copies source; adds a .dockerignore (allowlist or blocklist with .git, .env*, node_modules); flags secrets exposure via COPY . . as HIGH; suggests non-root USER and checks the Node base is not end of life.
FAIL if Only reorders layers without a .dockerignore, or ignores the .env and .git exposure.
