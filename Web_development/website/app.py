from flask import Flask, render_template, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__, 
    template_folder='templates',  # явно указываем папку с шаблонами
    static_folder='static'        # явно указываем папку со статическими файлами
)

# Исправленная конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1@localhost:5432/photos_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для фотографий
class Photo(db.Model):
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    return render_template('web6.html')

@app.route('/atre-akihabara/')  # добавляем слеш в конце
def atre_akihabara():
    try:
        return render_template('atre.html')
    except Exception as e:
        print(f"Ошибка при рендеринге шаблона: {e}")
        return str(e), 500

@app.route('/yodobashi/')
def yodobashi():
    return render_template('yodobashi.html')

@app.route('/api/photos')
def get_photos():
    try:
        photos = Photo.query.all()
        print("Получено фотографий из БД:", len(photos))
        result = [{
            "image_path": photo.image_path, 
            "caption": photo.caption
        } for photo in photos]
        print("Отправляемые данные:", result)
        return jsonify(result)
    except Exception as e:
        print(f"Ошибка при получении фотографий: {e}")
        return jsonify({'error': str(e)}), 500

# Тестовый маршрут для проверки подключения к БД
@app.route('/test-db')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return "Подключение к БД работает!"
    except Exception as e:
        return f"Ошибка подключения к БД: {e}"

# Создаем таблицы при запуске приложения
with app.app_context():
    try:
        db.create_all()
        
        # Проверяем есть ли данные в таблице
        count = Photo.query.count()
        
        # Если таблица пустая, добавляем тестовые данные
        if count == 0:
            test_photos = [
                Photo(image_path='1.jpg', caption='Токио, район Синдзюку'),
                Photo(image_path='2.jpg', caption='Храм Сэнсо-дзи'),
                Photo(image_path='3.jpg', caption='Башня Скайтри')
            ]
            
            for photo in test_photos:
                db.session.add(photo)
            
            db.session.commit()
            print("Тестовые данные добавлены")
    except Exception as e:
        print(f"Ошибка при инициализации БД: {e}")

if __name__ == '__main__':
    app.run(debug=True)