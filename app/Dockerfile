FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY app /app

# Создаем папку для логов
RUN mkdir -p /app/logs

# Копируем файл конфигурации
COPY .env /app/.env

# Определяем команду для запуска приложения
CMD ["python", "main.py"]

