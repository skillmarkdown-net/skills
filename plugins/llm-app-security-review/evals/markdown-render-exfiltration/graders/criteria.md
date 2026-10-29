---
type: llm
---

PASS if Identifies improper output handling (LLM05) and XSS, plus markdown image exfiltration via URL query strings combined with indirect injection from emails; recommends sanitiser such as DOMPurify, CSP img-src, no auto-loading remote images, domain allow-list; gives a canary test prompt; rates High or Critical given the combination.
FAIL if Only says to be careful, misses exfiltration channel, or suggests telling the model not to output HTML.
