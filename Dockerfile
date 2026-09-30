FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --home-dir /app --no-create-home appuser

COPY --chown=appuser:appuser app.py ./
COPY --chown=appuser:appuser templates ./templates
COPY --chown=appuser:appuser static ./static

USER appuser
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "app:app"]
