---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our support chatbot returns markdown and the React frontend renders it with dangerouslySetInnerHTML after marked.parse(reply). The bot also reads customer emails. Is this a security problem? What should we change?
