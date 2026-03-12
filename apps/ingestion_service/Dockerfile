FROM m.daocloud.io/docker.io/library/python:3.12-slim

WORKDIR /workspace

COPY requirements/base.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /workspace

ENV PYTHONPATH=/workspace

CMD ["uvicorn", "apps.ingestion_service.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
