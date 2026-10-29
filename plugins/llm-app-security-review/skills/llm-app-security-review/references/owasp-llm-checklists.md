# OWASP Top 10 for LLM Applications 2025: review checklists

IDs and names follow the 2025 list (v2.0). Old 2023/24 names are given as aliases only. Items marked (verify) are standard practice that should be checked against the current OWASP pages at https://genai.owasp.org/llm-top-10/ before quoting them as OWASP text.

## LLM01:2025 Prompt Injection
- Direct: from the user prompt. Indirect: from websites, files, retrieved documents, tool output. Jailbreaking is a subtype.
- Injected text need not be human-readable, only parseable by the model (hidden HTML, white-on-white text, metadata, image text).
- Check: external content concatenated into prompts unlabelled; no delimiters; no output format validation; privileged tools reachable in the same context as untrusted content.
- Mitigations: constrain role and scope; define and validate output formats; input and output filtering (defence in depth); least privilege; human approval for high-risk actions; segregate and mark external content (spotlighting); route untrusted sources through a lower-privilege model; block auto-loading images and untrusted links; adversarial testing.
- RAG and fine-tuning do not fully mitigate injection. No fool-proof prevention is known.

## LLM02:2025 Sensitive Information Disclosure
- Check: PII, credentials or other users' data in context, logs and traces; cross-tenant retrieval; training or fine-tuning on user data; verbose errors.
- Mitigations: sanitisation and redaction; access control; tenant-scoped retrieval; do not log raw prompts with PII.

## LLM03:2025 Supply Chain (secondary)
- Check: unpinned model, package and plugin versions; unvetted MCP servers; models downloaded from unverified sources.

## LLM04:2025 Data and Model Poisoning
- Check: who can write to the retrieval corpus or fine-tuning data; ingestion without source allow-list or validation.

## LLM05:2025 Improper Output Handling (alias: Insecure Output Handling)
- Treat model output as untrusted user input.
- Sinks to grep: `innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `|safe`, unsanitised markdown renderers, string-concatenated SQL, `eval`, `exec`, `subprocess(..., shell=True)`, `os.system`, file paths and URLs chosen by the model.
- Mitigations: context-aware encoding (HTML escape for HTML); parameterised queries for SQL; allow-listed argv commands without a shell; path canonicalisation inside a base directory; URL allow-lists and SSRF protection; CSP restricting `img-src`; do not auto-render remote images. (verify)
- Markdown images and links are an exfiltration vector via URL query strings.

## LLM06:2025 Excessive Agency
Three root causes:
1. Excessive functionality: tools not needed, dev-era tools left registered, open-ended tools (shell, `fetch(url)`).
2. Excessive permissions: shared or admin identities, broad OAuth scopes, write access where read suffices.
3. Excessive autonomy: high-impact actions without human approval.
- Mitigations: minimise tools and their functionality; narrow tools over open-ended ones; run tools in the user's own security context; require approval for high-impact actions; enforce authorisation in downstream systems, not in the LLM. (verify)

## LLM07:2025 System Prompt Leakage (new in 2025)
- Developers cannot safely assume prompt contents stay secret.
- The risk is secrets or authorisation logic in the prompt: API keys, connection strings, role rules, internal URLs.
- Mitigations: keep secrets out of prompts; enforce controls outside the LLM; assume the prompt is extractable.

## LLM08:2025 Vector and Embedding Weaknesses (new in 2025)
- Check: no per-user or per-tenant ACL filter at retrieval time; shared index across tenants; unvalidated ingestion (poisoned or hidden-text documents); embedding inversion. (verify)

## LLM09:2025 Misinformation
- Check: answers presented as authoritative with no grounding or citations; no human review in high-stakes domains. Mention only if relevant to scope.

## LLM10:2025 Unbounded Consumption
- Covers DoS, Denial of Wallet, degraded service, model extraction through many queries, side channels.
- Check: input size limits; `max_tokens` on every call; agent loop and tool-call caps; retrieval `top_k` and chunk size; history and upload bounds; per-user quotas on cumulative tokens, time or cost; `logit_bias` and `logprobs` exposure; timeouts; bounded retries with backoff; provider budget alerts or hard caps; unrestricted network or API access for the model.
- Follow-up turns re-send the growing history, so each turn costs more than the last.

## Sources
- OWASP Top 10 for LLM Applications 2025 PDF: https://owasp.github.io/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf
- Per-risk pages: https://genai.owasp.org/llmrisk/llm01-prompt-injection/ and the sibling pages for each ID.
