---
type: llm
---

PASS if Flags the repo:* wildcard sub and missing aud condition as High, proposes StringEquals aud sts.amazonaws.com and a specific repo/branch sub, suggests validating as RESOURCE_POLICY with validate-policy.
FAIL if Declares the policy fine because a sub condition exists, or misses the missing aud condition.
