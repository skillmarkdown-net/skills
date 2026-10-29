---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Please audit this for security problems before we ship.

```python
# agent.py
chunks = vectordb.search(query, top_k=50)
prompt = SYSTEM + "\n" + "\n".join(c.text for c in chunks) + "\nUser: " + query
reply = client.chat.completions.create(model='gpt-4o', messages=[{'role':'user','content':prompt}])
while True:
    call = parse_tool(reply)
    if not call: break
    result = TOOLS[call.name](**call.args)
    reply = client.chat.completions.create(model='gpt-4o', messages=[{'role':'user','content':str(result)}])
# tools.py
def send_email(to, body): smtp.send(to, body)
def run_shell(cmd): return subprocess.run(cmd, shell=True, capture_output=True).stdout
```
Anyone can upload documents to the knowledge base.
