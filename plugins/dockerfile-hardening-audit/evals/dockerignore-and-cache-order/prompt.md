---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

My docker builds always reinstall all npm packages even when I only change one source file, and the image contains my .env and .git folder. Dockerfile:

FROM node:20-slim
WORKDIR /app
COPY . .
RUN npm ci
CMD ["node","server.js"]

Fix it.
