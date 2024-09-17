FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /bot

# Копируем файл с зависимостями
COPY telegram_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY telegram_bot /bot

# Создаем папку для логов
RUN mkdir -p /bot/logs

# Копируем файл конфигурации
COPY .env /bot/.env

# Определяем команду для запуска бота
CMD ["python", "main.py"]
