# Dockerfile.fast
FROM jjanzic/docker-python3-opencv:latest

WORKDIR /app

COPY mse_console.py .

RUN mkdir -p /app/input /app/output

ENTRYPOINT ["python", "mse_console.py"]


# # Dockerfile
# FROM python:3.9-slim-bullseye
#
# # Установка только необходимых зависимостей
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     ffmpeg \
#     libgl1 \
#     && rm -rf /var/lib/apt/lists/*
#
# WORKDIR /app
#
# # Копируем только requirements сначала для лучшего кэширования
# COPY requirements.txt .
#
# # Устанавливаем зависимости (используем кэш pip)
# RUN pip install --no-cache-dir -r requirements.txt
#
# # Копируем основной скрипт
# COPY mse_console.py .
#
# # Создаем директории
# RUN mkdir -p /app/input /app/output
#
# ENTRYPOINT ["python", "mse_console.py"]


# # Dockerfile
# FROM python:3.9
#
# # Установка системных зависимостей
# RUN apt-get update && apt-get install -y \
#     ffmpeg \
#     && rm -rf /var/lib/apt/lists/*
#
# WORKDIR /app
#
# # Сначала устанавливаем OpenCV и numpy
# RUN pip install opencv-python==4.8.1.78 numpy==1.24.3
#
# COPY mse_console.py .
#
# RUN mkdir -p /app/input /app/output
#
# ENTRYPOINT ["python", "mse_console.py"]