---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

My Go service image is 900 MB. Dockerfile:

FROM golang:1.22
WORKDIR /src
COPY . .
RUN go build -o /app ./cmd/server
CMD /app

It listens on 8080 and doesn't need cgo. Can you slim and secure it?
