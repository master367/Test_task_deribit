FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости и сертификаты одним слоем
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/* # Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создаем пользователя заранее
RUN useradd -m -u 1000 appuser

# Копируем код и сразу назначаем владельца appuser
COPY --chown=appuser:appuser . .

# Переключаемся на пользователя
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]