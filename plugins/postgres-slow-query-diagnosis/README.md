# Postgres Slow Query Diagnosis

Reads PostgreSQL EXPLAIN ANALYZE plans, finds the real cause of slowness, and proposes indexes, rewrites and a safe way to verify them.

> **Triggers on:** Diagnoses slow PostgreSQL queries from EXPLAIN (ANALYZE, BUFFERS) output and query text: seq scans, bad row estimates, nested loops, disk spills, unused indexes, non-sargable filters. Proposes indexes, rewrites, settings and safe verification. Use when a user pastes an EXPLAIN plan, asks why a Postgres query is slow, or mentions pg_stat_statements, work_mem, CREATE INDEX CONCURRENTLY or ANALYZE.

## What it does

Helps an agent diagnose slow PostgreSQL queries from `EXPLAIN (ANALYZE, BUFFERS)` output and the query text. It ranks findings by time share, separates real problems (bad estimates, spills, non-sargable filters) from harmless ones (a justified seq scan), proposes indexes, rewrites and per-query settings, and gives a safe verification plan.

## When it triggers

- "Why is this query slow? Here is the EXPLAIN ANALYZE output..."
- "Postgres is doing a seq scan on my 50M row table, what index do I need?"
- "My sort says external merge Disk, should I raise work_mem?"
- "Estimated rows 12 but actual 48000, what is wrong?"
- "How do I add this index without locking the table?"

## What is inside

- `SKILL.md`: the workflow, decision rules, output format and gotchas.
- `references/plan-symptoms.md`: symptom to cause to action table.
- `references/query-rewrites.md`: sargability, LIKE, OR and other rewrites.
- `references/index-design.md`: index syntax, rules and CONCURRENTLY handling.
- `references/verification.md`: safe before/after testing and monitoring.
- `references/version-notes.md`: what changed per PostgreSQL version (14 to 18).
- `scripts/plan_flags.py`: parses a text plan and flags estimate errors, spills, heap fetches and more.

## Example output

```
## Verdict
The 41 s comes from a nested loop driven by a 1,000x row underestimate on orders.

## Fixes
1. ANALYZE orders;
2. CREATE INDEX CONCURRENTLY idx_orders_pending ON orders (created_at) WHERE status = 'pending';
```

## Customising it

Edit the thresholds in `scripts/plan_flags.py` (10x estimate error, 10,000 removed rows) and in `references/plan-symptoms.md` to match your workload. Add your own naming conventions and migration tooling to `references/index-design.md`.

## Limits

The parser reads TEXT format only. Some version-specific details (PG17/18 fields such as `Index Searches`, option introduction versions) were recalled from documentation and should be checked on a real instance. It cannot run queries; all advice depends on the plan and data you provide. Thresholds are heuristics, not official limits.

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add skillmarkdown-net/skills
/plugin install postgres-slow-query-diagnosis@skillmarkdown
```

### Any app that reads Agent Skills

Copy `skills/postgres-slow-query-diagnosis/` into your app's skills folder:

| App | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/postgres-slow-query-diagnosis/` | `.claude/skills/postgres-slow-query-diagnosis/` |
| OpenAI Codex | `~/.agents/skills/postgres-slow-query-diagnosis/` | `.agents/skills/postgres-slow-query-diagnosis/` |
| Cursor | `~/.cursor/skills/postgres-slow-query-diagnosis/` | `.cursor/skills/postgres-slow-query-diagnosis/` |
| Gemini CLI | `~/.gemini/skills/postgres-slow-query-diagnosis/` | `.gemini/skills/postgres-slow-query-diagnosis/` |
| Other Agent Skills apps | `~/.agents/skills/postgres-slow-query-diagnosis/` | `.agents/skills/postgres-slow-query-diagnosis/` |

Start a new session and ask for the task in your own words; the app loads the skill when your request matches its description.

## Test it

The `evals/` folder holds 8 test cases (5 that should trigger the skill, 3 that should not). With Claude Code installed:

```
claude plugin eval .
```

## License

MIT. See `LICENSE`.

---
Built with [SkillMarkdown](https://skillmarkdown.net).
