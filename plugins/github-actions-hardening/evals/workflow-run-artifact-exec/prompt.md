---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Audit this deploy workflow:

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
permissions: write-all
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build
          run-id: ${{ github.event.workflow_run.id }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
      - run: chmod +x deploy.sh && ./deploy.sh
        env:
          TOKEN: ${{ secrets.PROD_TOKEN }}
