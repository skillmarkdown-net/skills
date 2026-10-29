---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Stripe endpoint sends emails, generates PDFs and updates three services inside the request, then returns 200. For event types we don't handle we return 400. Stripe keeps emailing us about failures and we see repeated deliveries. Review this design and suggest the fix.
