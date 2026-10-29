---
type: llm
---

PASS if Flags missing aws:SourceArn and aws:SourceAccount as Medium, adds ArnLike/ArnEquals SourceArn for arn:aws:s3:::acme-uploads paired with SourceAccount 111122223333 because the bucket ARN has no account ID, and gives validation commands.
FAIL if Does not add SourceArn plus SourceAccount, or says S3 bucket ARNs include the account ID.
