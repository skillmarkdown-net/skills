---
name: stripe-webhook-reviewer
description: Reviews a Stripe webhook endpoint implementation for signature verification, replay protection, idempotency, event handling, retry behavior, API version pinning and CLI testing, then reports ranked risks with code fixes. Use when asked to review, audit or debug a Stripe webhook handler, constructEvent errors, Stripe-Signature failures, duplicate events, or checkout.session.completed and invoice.paid fulfillment.
---

# Stripe Webhook Reviewer

Review a Stripe webhook endpoint (code the user pastes or points to) and return ranked risks with minimal code fixes. Facts marked UNVERIFIED in [references/stripe-webhook-checklist.md](references/stripe-webhook-checklist.md) must be presented as "confirm in Stripe docs", not as certain.

## Steps

1. **Locate the pieces.** Find the webhook route, the framework body parsing config, where the secret comes from, the event switch/dispatcher, the dedupe store, and any queue or worker. Optionally run `python scripts/scan_webhook.py <file-or-dir>` for a quick static pass over Node, Python, Ruby, Go and PHP sources; it prints candidate findings with line numbers. Treat its output as hints and confirm by reading the code.
2. **Signature verification** (highest priority).
   - The SDK verifier must receive the raw bytes, the `Stripe-Signature` header and the endpoint `whsec_` secret (`stripe.webhooks.constructEvent` in Node, equivalents elsewhere).
   - Flag: `express.json()` or any body parser mounted globally before the webhook route (fix: `express.raw({type: 'application/json'})` on that route only); `JSON.parse`/`JSON.stringify` before verification; reading re-serialized JSON in Flask/FastAPI instead of `request.get_data()` / `await request.body()`.
   - Flag hand-rolled HMAC unless it signs `{timestamp}.{raw_body}` with HMAC-SHA256, compares in constant time, tests every `v1` value and checks the timestamp.
   - Flag: hardcoded secret, the `stripe listen` secret used in production (or a Dashboard secret used locally), one endpoint's secret on another endpoint, verification skipped in test or dev mode, a failure that returns 200 (must be 400).
3. **Tolerance and replay.** Default tolerance is 300 seconds. Flag any tolerance argument that is very large, `0` or `None`/null. Explain that the timestamp check stops stale replays only; replays inside the window need event-ID dedupe. Retries are re-signed with a fresh timestamp, so a correct tolerance does not break retries. Suggest NTP-synced servers (UNVERIFIED background advice).
4. **Idempotency.** Require event-ID dedupe with an atomic claim, not check-then-act:
   - `INSERT INTO stripe_events (id, status) VALUES ($1, 'processing') ON CONFLICT (id) DO NOTHING`; if zero rows inserted, return 200.
   - Mark `done` only after the work succeeds; reclaim stale `processing` rows after a lease timeout; release or fail the row on error so retries can reprocess.
   - Put the dedupe insert and business write in one transaction where possible.
   - Stripe may generate two distinct Event objects for the same change, so also make the business effect idempotent (unique key on `data.object.id` such as session, invoice or PaymentIntent ID).
   - Do not use `created` for ordering or dedupe (whole seconds, can tie). Do not confuse the outbound `Idempotency-Key` header with inbound dedupe.
5. **Ordering.** Events can arrive out of order. Handlers should fetch the current object (for example `subscription.retrieve`) or guard transitions so a stale `customer.subscription.updated` cannot revive a deleted subscription, and must not assume `customer.subscription.created` precedes `invoice.paid`.
6. **Event handling.** Check each type against the table in [references/stripe-webhook-checklist.md](references/stripe-webhook-checklist.md):
   - `checkout.session.completed`: fulfill only if `payment_status == 'paid'`; handle `checkout.session.async_payment_succeeded` and `checkout.session.async_payment_failed`; line items need a retrieve with `expand: ['line_items']`; map to the order via `client_reference_id` or `metadata`; fulfillment may run more than once, even concurrently with the success-page path, so dedupe on session ID too.
   - Subscriptions: provision/renew on `invoice.paid`; do not grant access from both `invoice.paid` and `invoice.payment_succeeded`; start dunning on `invoice.payment_failed`; revoke on `customer.subscription.deleted` or status `unpaid`/`canceled`; read status from the subscription object, not the event name; use `data.previous_attributes` on updates.
   - PaymentIntent: `payment_intent.succeeded` / `payment_failed` for direct integrations; avoid double fulfillment when Checkout and PaymentIntent events both fire.
   - Also check `charge.refunded` and `charge.dispute.created`.
   - Prefer fetching fresh objects over trusting payload amounts or state for money decisions.
7. **Retries and response timing.**
   - Verify, claim the ID, enqueue, return 2xx, then do heavy work in a worker. Do not state a specific timeout number.
   - Return 400 for bad signature or malformed payload; 2xx for duplicates and deliberately ignored types; 5xx only for transient failures you want retried. A 4xx on an unknown event type causes useless retries and failure emails. Permanent business errors: log and acknowledge.
   - Live mode retries up to 3 days with exponential backoff; sandbox retries three times over a few hours. If the endpoint does not respond properly to `invoice.created` in the successful-finalization flow, Stripe will not charge the invoice until it gets a success, so slow handlers can stall billing.
   - Recovery: list Events with `delivery_success=false` (last 30 days); Dashboard resend up to 15 days, `stripe events resend` up to 30 days.
8. **API version pinning** (UNVERIFIED details; say so). The endpoint has its own API version, which can differ from the account default and the SDK version. Recommend an explicit version on endpoint creation and on the SDK client, and upgrading by creating a new endpoint on the new version, running both, then removing the old one. Flag code reading fields that moved in the Basil version (2025-03-31), such as `invoice.subscription` (now `invoice.parent.subscription_details.subscription`) and subscription-level `current_period_end` (now on items). Confirm against https://docs.stripe.com/changelog.
9. **Testing plan.** Give Stripe CLI commands from the checklist and cover failure paths: bad signature, old timestamp, duplicate event, out-of-order events. Triggered fixtures create fresh objects, so use `stripe events resend` to test dedupe.
10. **Hygiene.** Flag logging of full payloads (PII) or the raw `Stripe-Signature` header, and references to the old Developers > Webhooks page (now Workbench / event destinations). If thin events are used, verification still needs the raw body and endpoint secret; parsing differs by SDK (UNVERIFIED).

## Output format

Start with a one-line verdict, then findings ordered Critical, High, Medium, Low. Each finding: title, location (file:line), why it matters, and a code fix. End with a test plan and a list of items to confirm in Stripe docs.

Example:

```
Verdict: not safe to ship; 2 critical, 2 high.

[Critical] Body parsed before verification - server.js:12
Why: app.use(express.json()) runs first, so constructEvent sees re-serialized JSON and fails, or the team may have disabled verification to cope.
Fix:
  app.post('/webhook', express.raw({type: 'application/json'}), handler);
  app.use(express.json()); // after the webhook route

[High] Check-then-act dedupe - webhook.js:40
Why: concurrent retry can pass the SELECT before the first insert.
Fix: INSERT ... ON CONFLICT (id) DO NOTHING; return 200 if rowCount is 0.

Test plan: stripe listen --forward-to localhost:4242/webhook; stripe trigger invoice.paid; stripe events resend evt_...
Confirm in docs: api_version field on endpoint create.
```

## Gotchas

- The `whsec_` printed by `stripe listen` is not the Dashboard endpoint secret; most "works locally, fails in prod" reports are this.
- Returning 200 inside a catch block that swallows errors hides failures and loses events; return 5xx for transient errors.
- A 2xx on a manual resend does not cancel automatic retries.
- A disabled or deleted endpoint gets no further retries for pending events.
- Do not invent exact timeouts, retry intervals or auto-disable rules; say they are not confirmed.
- Review only; do not change the user's code unless asked, and never print real secrets back.
