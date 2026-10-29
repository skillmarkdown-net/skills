---
type: llm
---

PASS if Identifies that replicas 1 with minAvailable 1 blocks node drains indefinitely, recommends 2+ replicas (3 for zone spread) with topologySpreadConstraints or changing the PDB, and gives YAML.
FAIL if Approves the PDB as good practice without noticing the drain deadlock.
