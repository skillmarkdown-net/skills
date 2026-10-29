---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this terraform plan before I apply. Here is the relevant part of tfplan.json: {"format_version":"1.2","terraform_version":"1.9.8","resource_changes":[{"address":"aws_vpc_security_group_ingress_rule.ssh","mode":"managed","type":"aws_vpc_security_group_ingress_rule","change":{"actions":["create"],"after":{"cidr_ipv4":"0.0.0.0/0","from_port":22,"to_port":22,"ip_protocol":"tcp"},"after_unknown":{}}},{"address":"aws_s3_bucket.logs","mode":"managed","type":"aws_s3_bucket","change":{"actions":["update"],"after":{},"after_unknown":{}}}]}
