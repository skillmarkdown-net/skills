---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

I want to see the plan for this statement on our production Postgres 17 database, I'm going to run EXPLAIN ANALYZE on it: UPDATE accounts SET status = 'closed' WHERE last_login < now() - interval '3 years'; It's affecting a lot of rows I think. Is it okay and how should I get the plan?
