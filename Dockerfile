FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5050

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/instance \
    && useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 5050

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5050/health', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "1", "--timeout", "60", "run:app"]
