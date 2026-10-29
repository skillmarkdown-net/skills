---
type: llm
---

PASS if Reports the NPM_TOKEN ARG/ENV and .npmrc as CRITICAL, latest tag and root user as HIGH; fixed Dockerfile uses a secret mount, multi-stage, pinned base with digest placeholder, numeric non-root USER, exec-form CMD, manifest-first cache order; includes .dockerignore and a docker build --secret command; advises rotating the token.
FAIL if Only gives generic advice, keeps the token in ARG, invents a sha256 digest, or omits the fixed Dockerfile or severity grouping.
