---
type: llm
---

PASS if Uses OWASP 2025 IDs; flags indirect injection (LLM01) with unlabelled retrieved text, run_shell shell=True and unrestricted send_email (LLM06/LLM05) as Critical, unbounded while True loop and missing max_tokens (LLM10), open corpus writes (LLM04/LLM08); mitigations in code; canary test prompts; severities ordered; does not claim safety.
FAIL if Gives generic advice, uses old 2023 IDs, relies on prompt wording as the fix, omits severity or test prompts, or says the app is safe.
