FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Create a dedicated non-root application user.
RUN useradd \
    --create-home \
    --uid 10001 \
    --shell /usr/sbin/nologin \
    appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app/dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]