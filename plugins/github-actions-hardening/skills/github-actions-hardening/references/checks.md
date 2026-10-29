# Workflow hardening checks

Read on demand. Items marked UNVERIFIED come from background knowledge; list them under Verify in the report.

## Attacker-controlled contexts (treat as untrusted in run: or script:)

- github.event.issue.title, .body
- github.event.pull_request.title, .body, .head.ref, .head.label, .head.repo.default_branch
- github.event.comment.body, github.event.review.body, github.event.review_comment.body
- github.event.pages.*.page_name
- github.event.commits.*.message, .author.email, .author.name
- github.event.head_commit.message, .author.email, .author.name
- github.head_ref
- github.event.workflow_run.head_branch, .head_commit.message
- Step outputs derived from the above (for example a comment found by peter-evans/find-comment), spoofed bot comments, artifact contents

(UNVERIFIED as a complete list.)

Safe pattern:

```yaml
env:
  TITLE: ${{ github.event.issue.title }}
run: echo "$TITLE"
```

For actions/github-script: put the value in env: and read process.env.TITLE; never interpolate into script:. Passing as `with:` input is not shell-injectable unless the action evals it.

## Trigger trust

| Trigger | Secrets / write token | Danger |
|---|---|---|
| pull_request (fork) | read-only token, no secrets | low |
| pull_request_target | base repo token and secrets, workflow from default branch | checkout/execution of PR code |
| workflow_run | secrets and write token, default branch file | executing artifacts, checking out head_sha |
| issue_comment | base repo context | running fork PR code on /run commands |

## Pwn request patterns

- actions/checkout ref: head.sha, head.ref, refs/pull/N/head, refs/pull/N/merge
- repository: github.event.pull_request.head.repo.full_name
- allow-unsafe-pr-checkout: true (Critical)
- Execution includes npm install lifecycle hooks, make, build scripts, test runners, linters reading PR config, local actions loaded from the PR.
- Safe uses of pull_request_target: labeling, commenting, no checkout of PR code, minimal permissions, untrusted values in env:.

## Permissions (UNVERIFIED details; confirm in Workflow syntax docs)

- Scopes: actions, attestations, checks, contents, deployments, discussions, id-token, issues, models, packages, pages, pull-requests, security-events, statuses.
- Values: read, write, none. id-token supports write or none.
- Specifying any key sets all unspecified scopes to none. `permissions: {}` disables all.
- Job-level block replaces workflow-level block.

| Need | Grant |
|---|---|
| checkout only | contents: read |
| release publishing | contents: write |
| comment/label PR | pull-requests: write |
| label issue | issues: write |
| OIDC to cloud | id-token: write (job level only) |
| SARIF upload | security-events: write |
| package publish | packages: write |
| provenance | attestations: write |

## Pinning

- Format: `uses: owner/repo@<40-hex> # vX.Y.Z`
- Pin reusable workflows too. Docker: `docker://image@sha256:<digest>` (UNVERIFIED).
- Skip local `./` references.
- Derive SHA: `git ls-remote https://github.com/OWNER/REPO refs/tags/vX.Y.Z`; annotated tags: `refs/tags/vX.Y.Z^{}`.
- Dependabot needs `package-ecosystem: "github-actions"`, `directory: "/"`, and a `schedule` (UNVERIFIED).
- tj-actions incident: tags v1 through v45.0.7 were moved to one malicious commit in a day.

## Secrets

- secrets: inherit on reusable-workflow calls (Medium)
- secrets in workflow/job env: instead of the one step
- toJSON(secrets), echo of secrets
- Prefer OIDC over long-lived cloud keys; use environments with required reviewers for deploy secrets.
- Derived values are not auto-masked; use ::add-mask::. (UNVERIFIED)

## Self-hosted runners

- Flag runs-on self-hosted on pull_request, pull_request_target, issue_comment, workflow_run.
- Prefer ephemeral/JIT runners, isolated VM or container, runner groups limited to repos and workflows.
- A node24 action needs runner >= 2.327.1.

## Timeouts and concurrency (UNVERIFIED)

- timeout-minutes default is 360. Suggest 10-30 for CI.
- Group: `${{ github.workflow }}-${{ github.ref }}`; cancel-in-progress true for CI, false (or `${{ github.ref != 'refs/heads/main' }}`) for deploy.
