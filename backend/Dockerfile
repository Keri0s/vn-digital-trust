FROM python:3.13-slim-trixie@sha256:57b29a7c050c4e679e4bea572e14b3965cf4b5839de2da49d55e49ffc4024f39
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.lock /app/requirements.lock
RUN pip install --no-cache-dir --require-hashes -r requirements.lock
COPY backend /app/backend
COPY tests /app/tests
COPY docs/design /app/docs/design
COPY docs/planning/verification /app/docs/planning/verification
COPY docs/planning/lab-fixtures-v0.1.json /app/docs/planning/lab-fixtures-v0.1.json
COPY docs/use-cases/flow-fixtures-v0.2.json /app/docs/use-cases/flow-fixtures-v0.2.json
COPY lab/local /app/lab/local
RUN useradd --uid 10001 --create-home vdt
USER 10001
WORKDIR /app/backend
CMD ["gunicorn","--bind","0.0.0.0:8000","--workers","2","vdt.wsgi:application"]
