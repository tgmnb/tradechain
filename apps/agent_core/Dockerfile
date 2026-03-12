FROM python:3.11-slim

WORKDIR /workspace

COPY requirements/base.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /workspace

ENV PYTHONPATH=/workspace

CMD ["uvicorn", "apps.agent_core.app.main:app", "--host", "0.0.0.0", "--port", "8002"]
