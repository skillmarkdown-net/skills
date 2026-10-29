---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Look over this plan before we apply it. aws_security_group.web is being created with one ingress block: from_port 5432, to_port 5432, protocol tcp, cidr_blocks ["10.0.0.0/8"], ipv6_cidr_blocks ["::/0"]. Egress is 0.0.0.0/0 on all ports.
