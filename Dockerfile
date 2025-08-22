# Используем официальный образ Python
FROM python:3.11-slim

# Установка зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Установка yt-dlp
RUN pip install yt-dlp

# Настройка переменной окружения
ENV BOT_TOKEN=${BOT_TOKEN}

# Команда для запуска
CMD ["python", "bot.py"]
