---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

We have a public chat endpoint that calls the OpenAI API, sends the full conversation history each turn, no max_tokens, and rate-limits only by IP at 60 requests per minute. Users can upload PDFs of any size for Q&A. How exposed are we to cost abuse?
