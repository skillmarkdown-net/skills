---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Is this workflow safe? Please audit it.

```yaml
name: PR check
on:
  pull_request_target:
    types: [opened, synchronize]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm install && npm test
      - run: echo "Deploying with ${{ secrets.DEPLOY_KEY }}"
```
