# Stripe Webhook Reviewer

Audits a Stripe webhook handler and returns ranked risks with concrete code fixes and Stripe CLI test steps.

> **Triggers on:** Reviews a Stripe webhook endpoint implementation for signature verification, replay protection, idempotency, event handling, retry behavior, API version pinning and CLI testing, then reports ranked risks with code fixes. Use when asked to review, audit or debug a Stripe webhook handler, constructEvent errors, Stripe-Signature failures, duplicate events, or checkout.session.completed and invoice.paid fulfillment.

## What it does

Reviews a Stripe webhook endpoint and produces ranked risks with code fixes. It checks signature verification on the raw body, tolerance and replay protection, idempotent handling by event id, checkout, invoice, PaymentIntent and subscription events, retry and 2xx behavior, API version pinning, and Stripe CLI testing.

## When it triggers

- "Review my Stripe webhook handler"
- "constructEvent keeps throwing No signatures found matching the expected signature"
- "We got a duplicate checkout.session.completed and shipped twice"
- "Is my invoice.paid and subscription handling correct?"
- "How do I test this webhook with the Stripe CLI?"

## What is inside

- `SKILL.md`: the review procedure and output format.
- `references/stripe-webhook-checklist.md`: response codes, event table, retry facts, CLI commands, test matrix, code snippets.
- `scripts/scan_webhook.py`: standard-library static scanner that flags likely issues with line numbers.

## Example output

```
Verdict: not safe to ship; 2 critical, 2 high.
[Critical] Body parsed before verification - server.js:12
Fix: express.raw({type: 'application/json'}) on the webhook route.
[High] Check-then-act dedupe - webhook.js:40
Fix: INSERT ... ON CONFLICT (id) DO NOTHING; return 200 on zero rows.
```

## Customising it

Edit the event table in the checklist to match the events your product uses, add your own queue or ORM conventions to the fix snippets, and extend the rules in `scan_webhook.py`.

## Limits

Some points (CLI flags, API version fields, Checkout async details, thin events) come from background knowledge and are marked UNVERIFIED; the skill tells users to confirm them in Stripe docs. It does not state the exact response timeout, retry intervals or auto-disable rules. The scanner is regex based and is a hint only.

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add skillmarkdown-net/skills
/plugin install stripe-webhook-reviewer@skillmarkdown
```

### Any app that reads Agent Skills

Copy `skills/stripe-webhook-reviewer/` into your app's skills folder:

| App | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/stripe-webhook-reviewer/` | `.claude/skills/stripe-webhook-reviewer/` |
| OpenAI Codex | `~/.agents/skills/stripe-webhook-reviewer/` | `.agents/skills/stripe-webhook-reviewer/` |
| Cursor | `~/.cursor/skills/stripe-webhook-reviewer/` | `.cursor/skills/stripe-webhook-reviewer/` |
| Gemini CLI | `~/.gemini/skills/stripe-webhook-reviewer/` | `.gemini/skills/stripe-webhook-reviewer/` |
| Other Agent Skills apps | `~/.agents/skills/stripe-webhook-reviewer/` | `.agents/skills/stripe-webhook-reviewer/` |

Start a new session and ask for the task in your own words; the app loads the skill when your request matches its description.

## Test it

The `evals/` folder holds 8 test cases (5 that should trigger the skill, 3 that should not). With Claude Code installed:

```
claude plugin eval .
```

## License

MIT. See `LICENSE`.

---
Built with [SkillMarkdown](https://skillmarkdown.net).
