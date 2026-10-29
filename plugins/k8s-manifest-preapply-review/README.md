# Kubernetes Manifest Pre-Apply Review

Pre-apply review of Kubernetes YAML: security, resources, probes, images, PDB, NetworkPolicy and RBAC, with severity-ranked findings and fixes.

> **Triggers on:** Reviews Kubernetes manifests (Deployments, StatefulSets, Services, Ingress, RBAC, NetworkPolicy, Helm-rendered YAML) before kubectl apply and reports findings by severity with YAML fixes. Use when asked to review, audit or harden k8s YAML, check securityContext, probes, resource limits, image tags, PDB, NetworkPolicy, RBAC or Pod Security Standards.

## What it does

Reviews Kubernetes manifests (and Helm-rendered YAML) before `kubectl apply`. It checks securityContext and Pod Security Standards, resources, probes, image pinning, replicas and PodDisruptionBudgets, NetworkPolicy, RBAC, Services, Ingress, Secrets and removed APIs. It returns a verdict plus findings ranked Critical to Info, each with the object, YAML path and a paste-ready fix.

## When it triggers

- "Review this Deployment before I apply it"
- "Is this Helm chart output safe to deploy to prod?"
- "Harden this StatefulSet's securityContext"
- "Audit my Role and RoleBinding for least privilege"
- "Check these manifests against Pod Security Standards restricted"

## What is inside

- `SKILL.md`: the review workflow, output format and gotchas.
- `references/checklist.md`: detailed checks per area with field names, defaults and sample NetworkPolicies.
- `references/severity.md`: severity rubric and verdict rule.
- `scripts/k8s_inventory.py`: stdlib-only scanner that lists objects and mechanical red flags.

## Example output

```
Verdict: Block - 1 Critical, 2 High, 3 Medium
C1. Privileged container - Deployment/agent/monitoring
Path: spec.template.spec.containers[0].securityContext.privileged
Fix: privileged: false, allowPrivilegeEscalation: false, capabilities.drop: [ALL]
```

## Customising it

Edit `references/severity.md` to match your organisation's risk appetite (for example, make a missing PDB High for production). Add internal rules, such as an approved registry list, to `references/checklist.md`. Extend the heuristics in the script if you use other workload kinds.

## Limits

The skill reads YAML; it cannot see namespace PSA labels, CNI enforcement, LimitRanges or live cluster state, and reports those as "cannot determine". The script is heuristic and line-based, and does not evaluate Helm templates, so render first. Version-specific facts (GA releases, ingress-nginx retirement dates) were not live-verified; confirm them on kubernetes.io before relying on them.

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add skillmarkdown-net/skills
/plugin install k8s-manifest-preapply-review@skillmarkdown
```

### Any app that reads Agent Skills

Copy `skills/k8s-manifest-preapply-review/` into your app's skills folder:

| App | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/k8s-manifest-preapply-review/` | `.claude/skills/k8s-manifest-preapply-review/` |
| OpenAI Codex | `~/.agents/skills/k8s-manifest-preapply-review/` | `.agents/skills/k8s-manifest-preapply-review/` |
| Cursor | `~/.cursor/skills/k8s-manifest-preapply-review/` | `.cursor/skills/k8s-manifest-preapply-review/` |
| Gemini CLI | `~/.gemini/skills/k8s-manifest-preapply-review/` | `.gemini/skills/k8s-manifest-preapply-review/` |
| Other Agent Skills apps | `~/.agents/skills/k8s-manifest-preapply-review/` | `.agents/skills/k8s-manifest-preapply-review/` |

Start a new session and ask for the task in your own words; the app loads the skill when your request matches its description.

## Test it

The `evals/` folder holds 8 test cases (6 that should trigger the skill, 2 that should not). With Claude Code installed:

```
claude plugin eval .
```

## License

MIT. See `LICENSE`.

---
Built with [SkillMarkdown](https://skillmarkdown.net).
