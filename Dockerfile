# Берем официальный и легкий образ Python
FROM python:3.11-slim

# Создаем рабочую папку внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код (твой main.py)
COPY . .

# Говорим, что контейнер будет слушать порт 8000
EXPOSE 8000

# Команда для запуска сервера внутри контейнера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]