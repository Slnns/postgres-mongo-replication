#!/usr/bin/env python3
import os
import logging
from pathlib import Path

import psycopg2
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

env_path = Path('/scripts') / '.env'
load_dotenv(dotenv_path=env_path)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Файл для времени синхронизации
SYNC_FILE = '/sync_state.txt'


def get_last_sync():
    try:
        with open(SYNC_FILE, 'r') as f:
            last_sync = f.read().strip()
            if last_sync:
                logger.info(f"Последняя синхронизация: {last_sync}")
                return last_sync
    except FileNotFoundError:
        logger.info("Первый запуск. Копируем все данные.")
    return '1970-01-01 00:00:00'


def main():
    try:
        last_sync = get_last_sync()

        pg_conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        logger.info("Подключились к PostgreSQL")

        mongo_client = MongoClient(
            host=os.getenv('MONGO_HOST'),
            port=int(os.getenv('MONGO_PORT'))
        )
        mongo_coll = mongo_client[os.getenv('MONGO_DB')][os.getenv('MONGO_COLLECTION')]
        logger.info("Подключились к MongoDB")

        cursor = pg_conn.cursor()
        cursor.execute("""
            SELECT id, name, email, created_at 
            FROM customers 
            WHERE created_at > %s
        """, (last_sync,))
        new_customers = cursor.fetchall()

        cursor.execute("""
            SELECT o.id, o.customer_id, o.product, o.amount, 
                   o.status, o.created_at
            FROM orders o
            WHERE o.updated_at > %s
        """, (last_sync,))
        new_orders = cursor.fetchall()

        logger.info(f"Найдено: {len(new_customers)} покупателей, {len(new_orders)} заказов")

        # Сохраняем покупателей
        customers_loaded = 0
        for c in new_customers:
            doc = {
                '_id': c[0],
                'name': c[1],
                'email': c[2],
                'created_at': str(c[3]),
                'synced_at': datetime.now().isoformat(),
                'orders': []
            }
            mongo_coll.update_one({'_id': c[0]}, {'$set': doc}, upsert=True)
            customers_loaded += 1

        # Добавляем заказы
        orders_loaded = 0
        for o in new_orders:
            order_doc = {
                'order_id': o[0],
                'product': o[2],
                'amount': float(o[3]),
                'status': o[4],
                'placed_at': str(o[5])
            }
            mongo_coll.update_one(
                {'_id': o[1]},  # customer_id
                {'$push': {'orders': order_doc}}
            )
            orders_loaded += 1

        # Сохраняем время синхронизации
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(SYNC_FILE, 'w') as f:
            f.write(current_time)

        logger.info(f"Загружено: {customers_loaded} покупателей, {orders_loaded} заказов")
        logger.info(f"Синхронизация завершена. Время: {current_time}")

        # Закрываем соединения
        cursor.close()
        pg_conn.close()
        mongo_client.close()

    except Exception as e:
        logger.error(f"ОШИБКА: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())