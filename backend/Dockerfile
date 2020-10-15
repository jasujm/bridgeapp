FROM python:3.8 AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/bridgeapp

FROM base AS builder

RUN set -ex; pip install poetry==1.1.3; python -m venv /usr/venv/bridgeapp

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt | /usr/venv/bridgeapp/bin/pip install -r /dev/stdin

FROM base

COPY --from=builder /usr/venv /usr/venv
COPY . .

CMD ["/usr/venv/bridgeapp/bin/gunicorn", "--proxy-protocol", "-b", "0.0.0.0", "-k", "uvicorn.workers.UvicornWorker", "bridgeapp"]
