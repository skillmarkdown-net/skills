---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this Stripe webhook, signature checks keep failing:

```js
const app = express();
app.use(express.json());
app.post('/webhook', (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;
  try {
    event = stripe.webhooks.constructEvent(JSON.stringify(req.body), sig, 'whsec_abc123def456ghi789');
  } catch (e) {
    return res.status(200).send('bad');
  }
  if (event.type === 'checkout.session.completed') { fulfill(event.data.object); }
  res.sendStatus(200);
});
```
