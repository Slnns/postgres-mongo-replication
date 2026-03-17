# Репликация данных из PostgreSQL в MongoDB

## Описание проекта
ETL-пайплайн для автоматической репликации данных из PostgreSQL в MongoDB. 
Скрипт каждые 5 минут проверяет новые записи в PostgreSQL и добавляет их в MongoDB.
## Структура проекта
- replication/
-  scripts/ - Python скрипты
- - replicate.py - Основной скрипт репликации
- - requirements.txt - Зависимости Python
- - .env 
-  docker-compose.yml
-  init.sql - Создание таблиц в PostgreSQL
-  generate_data.sql - Генерация тестовых данных
-  sync_state.txt - Время последней синхронизации