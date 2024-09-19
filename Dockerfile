FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install prefect

ENV PYTHONPATH=/app

CMD ["prefect", "worker", "start", "--pool", "default-agent-pool"]

# Установите ограничение на память и CPU при запуске контейнера
# docker run --memory="512m" --cpus="1.0" your_image