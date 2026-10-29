---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Harden this for supply-chain risk, we want everything pinned.

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: softprops/action-gh-release@v2
      - uses: ./.github/actions/setup
      - uses: docker://alpine:3.20
