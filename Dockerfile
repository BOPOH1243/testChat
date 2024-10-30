# Используйте официальный образ Python как базовый образ
FROM python:3.12-slim

# Установка необходимых системных пакетов
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем ваш код приложения в контейнер
WORKDIR /app
COPY fapi /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порты
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
