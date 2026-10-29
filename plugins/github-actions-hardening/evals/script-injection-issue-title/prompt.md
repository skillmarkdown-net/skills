---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our triage workflow does this and a teammate says it's fine because it's quoted. Check it:

on: issues
jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "New issue: ${{ github.event.issue.title }}"
          ./label.sh "${{ github.event.issue.body }}"
