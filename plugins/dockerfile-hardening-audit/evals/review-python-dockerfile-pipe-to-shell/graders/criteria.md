---
type: llm
---

PASS if Flags the piped download and unchecksummed remote ADD as CRITICAL, USER root and unpinned base as HIGH, apt update split and missing cleanup as MEDIUM; fixes by downloading, verifying checksum, then running in a builder stage, --checksum or verification, slim base, one apt RUN with --no-install-recommends, non-root USER, requirements-first caching.
FAIL if Keeps the pipe to shell, leaves USER root, or skips severity ranking.
