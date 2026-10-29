---
type: llm
---

PASS if Inspects the initContainer too (runs as root, no drop ALL), notes missing allowPrivilegeEscalation false, capabilities drop ALL, seccompProfile RuntimeDefault for restricted; labels readOnlyRootFilesystem as best practice rather than PSS; suggests fsGroup instead of the chown init container; mentions emptyDir for writable paths.
FAIL if Only reviews the main container, calls readOnlyRootFilesystem a PSS requirement, or provides no patch.
