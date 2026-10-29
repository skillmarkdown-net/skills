---
type: llm
---

PASS if Proposes multi-stage with CGO_ENABLED=0 and distroless static (or scratch) with nonroot, digest pin placeholder, exec-form entrypoint, notes no shell for debugging (:debug), cache-friendly go.mod/go.sum copy, .dockerignore, and flags HEALTHCHECK needs an in-binary check or orchestrator probe.
FAIL if Uses a full golang runtime image, keeps shell-form CMD, or recommends curl-based HEALTHCHECK on distroless.
