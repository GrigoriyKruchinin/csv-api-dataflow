# CSV API Dataflow

## Установка и запуск

1. Склонируйте репозиторий:
    ```bash
    git clone https://github.com/GrigoriyKruchinin/csv-api-dataflow.git
    cd csv-api-dataflow
    ```

2. Создайте и активируйте виртуальное окружение:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
    ```

3. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

4. Запустите Prefect сервер:
    ```bash
    prefect server start
    ```

   Если сервер запущен, откройте Prefect UI в браузере по адресу:
    ```bash
    prefect dashboard
    ```
   Или вручную перейдите по адресу [http://127.0.0.1:4200](http://127.0.0.1:4200).

5. Создайте и примените развертывание Flow:
    ```bash
    prefect deployment build app/flows/data_flow.py:data_processing_flow -n data_processing_flow
    prefect deployment apply data_processing_flow-deployment.yaml
    ```

6. Запустите развертывание:
    ```bash
    prefect deployment run data_processing_flow
    ```

## Docker

1. Сборка Docker образа:
    ```bash
    docker build -t csv-api-dataflow .
    ```

2. Запуск контейнера:
    ```bash
    docker run -it --rm csv-api-dataflow
    ```

## Архитектура

Проект состоит из следующих компонентов:
- **Flows**: Основной flow для обработки данных.
- **Utils**: Утилиты для работы с API, обработки данных и отправки уведомлений.
- **Prefect**: Конфигурационные файлы для Prefect.

## Скриншоты и отчеты

Скриншоты и отчеты о производительности можно найти в папке `docs`.
