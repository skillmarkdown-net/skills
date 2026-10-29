---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Is this S3 bucket policy safe? Fix whatever's wrong.
{"Version":"2012-10-17","Statement":[{"Sid":"ReadAll","Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::acme-reports/*"}]}
Our whole AWS org (o-exampleorgid) should be able to read it, nobody else.
