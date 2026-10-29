# Severity model

Rate each finding by exploitability multiplied by impact, then adjust for the combination rule.

| Severity | Meaning | Typical example |
|----------|---------|-----------------|
| Critical | Remote, low-skill exploit with data loss, account takeover, code execution or irreversible side effects | Retrieved text can trigger an email or shell tool; model output passed to `shell=True` |
| High | Likely exploit with significant data exposure or cost | Model markdown rendered as HTML; cross-tenant retrieval; secrets in system prompt |
| Medium | Exploit needs preconditions or impact is limited | No per-user token quota; verbose errors with stack traces |
| Low | Hardening gap with small impact | Missing `max_tokens` on a low-traffic internal tool |
| Info | Observation or best-practice note | Unpinned dev dependency |

## Combination rule
Raise by one level (up to Critical) when all three line up:
1. Untrusted content reaches the model context (retrieved docs, web pages, uploads, tool output).
2. The model holds privileged tools or sensitive data.
3. An exfiltration or side-effect channel exists: markdown image or link rendering, tool calls to arbitrary URLs, email or webhook tools, file writes.

If only one or two hold, do not raise.

## Do not
- Lower severity because a classifier guardrail or prompt instruction exists. These are probabilistic.
- Raise severity merely because a pattern matched. Confirm the input is model-influenced.
- Mark LLM01 as fixed by prompt wording alone.
