---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

PG 18 plan, a report query takes 2 minutes. Fragment:

Nested Loop  (cost=0.85..5400.00 rows=15 width=64) (actual time=0.2..118000.0 rows=2400000 loops=1)
  ->  Index Scan using idx_ev_type_status on events e  (cost=0.43..120.00 rows=15 width=32) (actual time=0.1..900.0 rows=2400000 loops=1)
        Index Cond: ((type = 'click') AND (status = 'ok'))
  ->  Index Scan using users_pkey on users u  (cost=0.43..8.00 rows=1 width=40) (actual time=0.04..0.04 rows=1.00 loops=2400000)

n_mod_since_analyze for events is 0 and last_autoanalyze was yesterday. Type and status are strongly correlated. What now?
