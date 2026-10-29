---
type: llm
---

PASS if Explains Allow+NotAction on * grants everything else including future actions, rates Critical, notes it permits things like sts, kms, ec2, lambda and PassRole-adjacent paths (no iam:* though), and offers an explicit allowlist or a Deny guardrail alternative with tightened JSON.
FAIL if Agrees it only blocks IAM and is fine, or provides no tightened policy.
