from sqlalchemy import create_engine, text
import logging

# Настройка логирования
logging.basicConfig(filename='db_connection_test.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    # Создаем подключение
    engine = create_engine('postgresql://postgres:1@localhost:5432/photos_db')
    
    # Пробуем подключиться
    with engine.connect() as connection:
        logger.info("Успешное подключение к базе данных!")
        print("Подключение успешно!")
        
        # Проверяем существование таблицы
        result = connection.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'photo')"))
        table_exists = result.scalar()
        
        if table_exists:
            print("Таблица 'photo' существует")
            # Проверяем количество записей
            result = connection.execute(text("SELECT COUNT(*) FROM photo"))
            count = result.scalar()
            print(f"Количество записей в таблице: {count}")
        else:
            print("Таблица 'photo' не существует")
            # Создаем таблицу
            connection.execute(text("""
                CREATE TABLE photo (
                    id SERIAL PRIMARY KEY,
                    image_path VARCHAR(200) NOT NULL,
                    caption VARCHAR(200) NOT NULL
                )
            """))
            connection.commit()
            print("Таблица 'photo' создана")

except Exception as e:
    error_msg = f"Ошибка подключения: {str(e)}"
    logger.error(error_msg)
    print(error_msg)
