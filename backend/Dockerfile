FROM python:3.9 AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/bridgeapp

FROM base AS builder

RUN set -ex; pip install poetry==1.1.12; python -m venv /usr/venv/bridgeapp

COPY pyproject.toml poetry.lock ./
RUN poetry export | /usr/venv/bridgeapp/bin/pip install -r /dev/stdin

COPY . .
RUN set -ex; poetry build; /usr/venv/bridgeapp/bin/pip install dist/*.whl

FROM base

COPY start.sh ./
COPY --from=builder /usr/venv /usr/venv

ENTRYPOINT ["./start.sh"]
CMD ["gunicorn", "--forwarded-allow-ips", "*", "-b", "0.0.0.0", "-k", "uvicorn.workers.UvicornWorker", "bridgeapp"]
