# Используем официальный образ Python 3.11 slim для минимизации размера
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы requirements.txt и main.py
COPY requirements.txt main.py ./

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 8000 для веб-приложения
EXPOSE 8000

# Команда для запуска приложения с помощью gunicorn и uvicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--timeout", "15"]
