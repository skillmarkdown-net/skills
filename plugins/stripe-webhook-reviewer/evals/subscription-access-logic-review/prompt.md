---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Audit our subscription webhook logic. We grant access on both invoice.payment_succeeded and invoice.paid, we set status from the event name (customer.subscription.updated => 'active'), and we read invoice.subscription to find the sub. We are on an upgraded API version. What are the risks?
