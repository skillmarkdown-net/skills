---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Can you check this CI file for runner and reliability problems?

on:
  pull_request:
  push:
    branches: [main]
jobs:
  build:
    runs-on: [self-hosted, linux]
    steps:
      - uses: actions/checkout@v4
      - run: make test
  release:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: ./release.sh
