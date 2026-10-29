---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Here is our agent's tool registry, please check for risks:

tools = [
  {"name": "fetch_url", "desc": "GET any URL"},
  {"name": "query_db", "desc": "run SQL, uses admin service account"},
  {"name": "delete_record", "desc": "delete by id, no confirmation"},
  {"name": "old_debug_shell", "desc": "left from dev"}
]
The agent summarises tickets for support staff.
