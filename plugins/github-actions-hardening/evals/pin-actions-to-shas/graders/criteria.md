---
type: llm
---

PASS if Recommends full 40-char SHA pins with version comments for the external actions, skips the local action, pins the docker image by sha256 digest, gives the git ls-remote command (with ^{} for annotated tags) or a placeholder instead of inventing hashes, mentions Dependabot or Renovate.
FAIL if Fabricates specific SHA values, pins the local action, or ignores the docker image.
