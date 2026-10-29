---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Check this SNS topic policy for confused deputy problems:
{"Version":"2012-10-17","Statement":[{"Sid":"AllowS3","Effect":"Allow","Principal":{"Service":"s3.amazonaws.com"},"Action":"sns:Publish","Resource":"arn:aws:sns:us-east-1:111122223333:uploads"}]}
The bucket is arn:aws:s3:::acme-uploads in the same account.
