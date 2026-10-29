---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Harden this Dockerfile, it builds a Node API on port 3000:

FROM node:latest
ARG NPM_TOKEN
ENV NPM_TOKEN=$NPM_TOKEN
WORKDIR /app
COPY . .
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc && npm install
EXPOSE 3000
CMD npm start
