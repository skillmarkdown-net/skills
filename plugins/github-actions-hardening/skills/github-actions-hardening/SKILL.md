---
name: github-actions-hardening
description: "Audits GitHub Actions workflow files and reports a severity-ranked findings table with YAML diff fixes: unpinned actions, broad permissions, pull_request_target and workflow_run misuse, script injection, secrets, self-hosted runners, missing timeouts. Use when reviewing .github/workflows/*.yml, hardening CI, pinning actions to SHAs, or checking a pwn request."
---

# GitHub Actions Hardening Audit

Review workflow YAML for security weaknesses and return a findings table plus a minimal YAML diff for each fix. Never claim a workflow is safe without reading every job.

## Steps

1. **Collect inputs.** Read every file in `.github/workflows/*.yml` and `*.yaml`, plus local composite actions under `.github/actions/`. If the user pasted YAML, audit that. Optionally run the bundled scanner for a fast first pass: `python3 scripts/scan_workflows.py .github/workflows` (see [scripts/scan_workflows.py](scripts/scan_workflows.py)). It finds only pattern-level issues; you must still read the files for logic problems (taint flow, checkout of PR code).
2. **Classify each workflow by trigger trust.** Privileged triggers: `pull_request_target`, `workflow_run`, `issue_comment`, `issues`, `schedule` with secrets. Unprivileged: `pull_request`, `push` to non-default branches. Anything privileged that touches fork code or fork-controlled data is the highest-risk area. Details: [references/checks.md](references/checks.md).
3. **Run the checks in this order** (critical first):
   1. Pwn request: privileged trigger plus checkout or execution of untrusted code. Flag `actions/checkout` with `ref:` set to `github.event.pull_request.head.sha`, `.head.ref`, `refs/pull/<n>/head` or `refs/pull/<n>/merge`, or `repository:` set to the head repo. Any `allow-unsafe-pr-checkout: true` is a finding too (see severity table).
   2. `workflow_run` misuse: executing artifact content while holding secrets, checking out `workflow_run.head_sha` or `head_branch`, interpolating `head_branch`, `head_commit.message` or `pull_requests[0]` into `run:`, no `branches:` filter, no check of `github.event.workflow_run.event` and `conclusion`.
   3. Script injection: any `${{ ... }}` of an attacker-controlled field inside `run:` or `actions/github-script` `script:`. Field list in [references/checks.md](references/checks.md). Also untrusted data written to `$GITHUB_ENV`, `$GITHUB_PATH` or `$GITHUB_OUTPUT`.
   4. Unpinned actions: every `uses:` that is not local (`./`) and not a 40-hex SHA. Include reusable workflows and `docker://` images (pin by `@sha256:` digest).
   5. Permissions: missing top-level `permissions:`, `write-all`, `id-token: write` or write scopes at workflow level, job blocks broader than needed.
   6. Secrets: `secrets: inherit`, secrets in workflow-level or job-level `env:`, `toJSON(secrets)`, secrets in jobs that also run untrusted code.
   7. Self-hosted runners: `runs-on` containing `self-hosted` on a privileged or fork-reachable trigger.
   8. Reliability: jobs without `timeout-minutes`, missing `concurrency`, `cancel-in-progress: true` on deploy or release.
   9. `actions/checkout` without `persist-credentials: false` where the job later runs third-party code or uploads the workspace.
4. **Resolve pin SHAs correctly.** Never invent a SHA. Derive it from the tag: `git ls-remote https://github.com/OWNER/REPO refs/tags/vX.Y.Z` and for annotated tags `refs/tags/vX.Y.Z^{}` (use the dereferenced commit). If you have no network access, write the diff with the placeholder `<FULL-40-CHAR-SHA>` and the exact `git ls-remote` command for the user. Never fabricate a hash.
5. **Pin checkout carefully.** The checkout fork-PR protections (v7.0.0 and the backports v2.8.0, v3.7.0, v4.4.0, v5.1.0, v6.1.0) reach mutable tags automatically but not SHA pins. When pinning `actions/checkout`, choose a SHA at or after one of those patched releases. Recommend Dependabot or Renovate so pins keep moving.
6. **Write the fixes** as minimal unified diffs (`-`/`+` lines) per finding, with enough context to place them. Prefer the fix that removes the risk over a mitigation:
   - pwn request: switch to `pull_request`; or keep `pull_request_target` for metadata work only and never check out PR code.
   - injection: move the expression into `env:` and use `"$VAR"` in the shell; quoting the expression does not help.
   - permissions: `permissions: {}` or `contents: read` at the top, then per-job grants. A job-level block replaces the workflow-level one, it does not merge.
7. **Add the unverifiable items to a Verify list** instead of asserting them (see Gotchas).

## Output format

Start with a one-line verdict (counts per severity), then the table, then one diff per finding, then a short Verify list.

Severity: Critical = pwn request or `allow-unsafe-pr-checkout`; High = script injection, `workflow_run` executing artifacts, unpinned third-party actions in privileged workflows, self-hosted on fork-reachable triggers; Medium = missing `permissions:`, `secrets: inherit`, secrets at wide scope; Low = missing timeouts or concurrency.

```
Verdict: 1 critical, 1 high, 1 medium, 1 low in .github/workflows/pr.yml

| # | Sev | File:line | Finding | Fix |
|---|-----|-----------|---------|-----|
| 1 | Critical | pr.yml:12 | pull_request_target checks out PR head SHA and runs npm install | Use pull_request, or drop the ref |
| 2 | High | pr.yml:20 | github.event.pull_request.title interpolated in run | Pass via env: |
| 3 | Medium | pr.yml:1 | No permissions block | permissions: contents: read |
| 4 | Low | pr.yml:8 | No timeout-minutes (default 360) | timeout-minutes: 15 |
```

```diff
# Finding 2
       - name: Print title
-        run: echo "${{ github.event.pull_request.title }}"
+        env:
+          TITLE: ${{ github.event.pull_request.title }}
+        run: echo "$TITLE"
```

## Gotchas

- Quotes around `${{ }}` do not prevent injection; the expression is expanded before the shell runs.
- A SHA that exists only in a fork (impostor commit) passes a regex check. Confirm the SHA is on the official repo's tagged release; zizmor's `impostor-commit` audit detects it.
- A wrong version comment misleads reviewers. Keep `# vX.Y.Z` matching the SHA.
- Do not flag local actions (`./path`) as unpinned.
- `workflow_run` is only safe if artifacts are treated as data. Parse values with a strict regex (for example a numeric PR number) and never execute them.
- Label gating ("safe to test") is fragile: the attacker can push after the label. Say so if you see it.
- The checkout block does not cover `issue_comment` and other triggers, and does not stop executing a downloaded artifact. Do not treat a v7 checkout as a fix for those.
- Self-hosted runners that are not ephemeral keep disk state (`~/.npm`, `~/.cache/pip`, build dirs) between jobs. Recommend ephemeral or JIT runners and restricted runner groups.
- `concurrency` group of only `${{ github.workflow }}` serializes all PRs; include `github.ref` or the PR number. For `pull_request_target` and `issue_comment`, `github.ref` is the base branch, so use the PR number. Use `cancel-in-progress: false` for deploys.
- Claims about a default event policy blocking `pull_request_target` (a date of 2 November 2026 appears in a secondary source only) are unconfirmed; tell the user to check repo and org Actions settings.
- Some details are from background knowledge and not re-verified: the full permission scope list, the SHA-pinning policy checkbox in Settings, the 360-minute default timeout. State these in the Verify list with the GitHub Docs page (Workflow syntax, secure use reference) to check.
- Recommend complementary tools by name only: CodeQL with Actions scanning, OpenSSF Scorecard, zizmor, actionlint, pinact, ratchet. Do not invent flags for them.
