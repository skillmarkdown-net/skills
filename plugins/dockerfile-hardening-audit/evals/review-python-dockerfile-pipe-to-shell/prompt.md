---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Security review this Dockerfile please:

FROM python:3.12
RUN curl -sSL https://example.com/install.sh | sh
ADD https://example.com/tool.tar.gz /opt/
RUN apt-get update
RUN apt-get install -y gcc libpq-dev
COPY . /app
RUN pip install -r /app/requirements.txt
USER root
CMD ["python","/app/main.py"]
