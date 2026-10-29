# Stripe webhook review checklist

Legend: (V) verified from Stripe docs and sources; (U) UNVERIFIED background knowledge, tell the user to confirm.

## Response codes

| Situation | Return |
|---|---|
| Bad or missing signature, malformed payload | 400 (V) |
| Duplicate event already processed | 2xx (V) |
| Event type deliberately ignored | 2xx (V) |
| Transient failure (DB down) | 5xx so Stripe retries (V) |
| Permanent business error | log, acknowledge 2xx (V) |

## Event handling table

| Event | Correct action | Common bug |
|---|---|---|
| checkout.session.completed | Fulfill only if payment_status is paid (U); retrieve with expand line_items (U) | Fulfilling on unpaid delayed methods |
| checkout.session.async_payment_succeeded / async_payment_failed | Fulfill or notify (U) | Not handled at all |
| invoice.paid | Provision or renew access (U) | Also granting on invoice.payment_succeeded |
| invoice.payment_failed | Notify, start dunning (V) | Ignored |
| invoice.payment_action_required | Ask customer to authenticate (U) | Ignored |
| customer.subscription.created / updated | Sync status from object, use data.previous_attributes (U) | Trusting event order |
| customer.subscription.deleted | Revoke access (U) | Stale updated event revives it |
| customer.subscription.trial_will_end | Sent 3 days before trial end (V); notify | Missed |
| payment_intent.succeeded / payment_failed | Direct PaymentIntent flows (U) | Double fulfillment with Checkout |
| charge.refunded, charge.dispute.created | Adjust entitlement, alert (U) | Unhandled |

Subscription statuses: active, past_due, unpaid, canceled, incomplete, incomplete_expired, trialing, paused (U). Read status from the object.

## Retry facts

- Live mode: retries up to 3 days, exponential backoff. Sandbox: three retries over a few hours (V).
- Exact intervals and response timeout: not confirmed; do not quote numbers.
- Dashboard resend: up to 15 days; `stripe events resend`: up to 30 days (V, secondary source).
- Undelivered events: list Events with delivery_success=false, last 30 days (V).

## Stripe CLI (U: confirm with `stripe listen --help`)

```
stripe listen --forward-to localhost:4242/webhook
stripe listen --print-secret
stripe listen --events checkout.session.completed,invoice.paid --forward-to localhost:4242/webhook
stripe trigger checkout.session.completed
stripe events resend evt_...
```

The secret from `stripe listen` is session-specific, not the Dashboard secret.

## Failure-path test matrix

| Test | How | Expect |
|---|---|---|
| Bad signature | Alter body or use wrong secret | 400, no side effects |
| Old timestamp | Replay a captured request after more than 300 s | 400 |
| Duplicate | `stripe events resend` same evt id twice | One business effect, 2xx both |
| Out of order | Send subscription.deleted then an older updated | Stays canceled |
| Slow handler | Add a delay in the worker | Endpoint still returns 2xx fast |

## Code fix snippets

Node raw body:
```js
app.post('/webhook', express.raw({type: 'application/json'}), (req, res) => {
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, req.headers['stripe-signature'], process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    return res.status(400).send('invalid signature');
  }
  // claim event.id, enqueue, then:
  res.sendStatus(200);
});
```

Flask raw body:
```python
payload = request.get_data()
event = stripe.Webhook.construct_event(payload, request.headers.get('Stripe-Signature'), endpoint_secret)
```

## Sources

- https://docs.stripe.com/webhooks
- https://docs.stripe.com/billing/subscriptions/webhooks
- https://docs.stripe.com/checkout/fulfillment (to verify)
- https://docs.stripe.com/api/versioning (to verify)
- https://docs.stripe.com/changelog (check Basil 2025-03-31)
- https://docs.stripe.com/cli/listen and https://docs.stripe.com/cli/trigger (to verify)
