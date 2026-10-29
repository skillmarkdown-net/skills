---
type: llm
---

PASS if Flags Critical public principal without condition, adds aws:PrincipalOrgID StringEquals o-exampleorgid, mentions Block Public Access checks and aws:SecureTransport deny, and gives check-no-public-access with AWS::S3::Bucket.
FAIL if Leaves Principal * unconditioned, or does not mention how to verify it is not public.
