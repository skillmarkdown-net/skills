---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

On Postgres 14, my search `SELECT id, name FROM products WHERE name ILIKE '%wireless%' LIMIT 20;` does a Parallel Seq Scan on 8 million rows and takes 1.4s. I already have a btree index on name. What should I do?
