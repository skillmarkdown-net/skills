---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Customers got two shipments for one order. Here's our handler:

```python
@app.post('/stripe')
def hook():
    event = stripe.Webhook.construct_event(request.get_data(), request.headers['Stripe-Signature'], SECRET)
    if db.query('select 1 from processed where id=%s', event['id']):
        return '', 200
    if event['type'] == 'checkout.session.completed':
        ship_order(event['data']['object']['client_reference_id'])
    db.execute('insert into processed values (%s)', event['id'])
    return '', 200
```
What's wrong?
