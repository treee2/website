from flask import Flask, render_template, jsonify, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
import json
import logging

# Настройка логирования
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

# Конфигурация
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)

# Создаем папки если они не существуют
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)

# Настройка конфигурации
app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH,
    SQLALCHEMY_DATABASE_URI='postgresql://postgres:1@localhost:5432/photos_db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='your-secret-key-here'
)

db = SQLAlchemy(app)

# Данные администратора (в реальном приложении должны храниться в базе данных)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = generate_password_hash('password123')

# Модель для фотографий
class Photo(db.Model):
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(200), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('web6.html')

@app.route('/atre-akihabara/')  # добавляем слеш в конце
def atre_akihabara():
    try:
        return render_template('atre.html')
    except Exception as e:
        logging.error(f"Ошибка при рендеринге шаблона: {e}")
        return str(e), 500

@app.route('/yodobashi/')
def yodobashi():
    return render_template('yodobashi.html')

@app.route('/api/photos')
def get_photos():
    try:
        with open('static/photos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify(data['photos'])
    except Exception as e:
        logging.error(f"Ошибка при чтении JSON: {e}")
        return jsonify({'error': str(e)}), 500

# Тестовый маршрут для проверки подключения к БД
@app.route('/test-db')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return "Подключение к БД работает!"
    except Exception as e:
        return f"Ошибка подключения к БД: {e}"

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD, password):
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Неверное имя пользователя или пароль')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    try:
        with open('static/photos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            photos = data.get('photos', [])
    except:
        photos = []
    return render_template('admin.html', photos=photos)

@app.route('/admin/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'photo' not in request.files:
            logging.warning('Нет файла в запросе')
            return jsonify({'error': 'Нет файла в запросе'}), 400
        
        file = request.files['photo']
        caption = request.form.get('caption', '').strip()
        
        if not caption:
            logging.warning('Не указана подпись к фото')
            return jsonify({'error': 'Необходимо указать подпись к фото'}), 400
        
        if file.filename == '':
            logging.warning('Пустое имя файла')
            return jsonify({'error': 'Файл не выбран'}), 400
        
        # Проверяем файл
        is_valid, error_message = validate_image(file)
        if not is_valid:
            logging.warning(f'Ошибка валидации файла: {error_message}')
            return jsonify({'error': error_message}), 400
        
        # Генерируем уникальное имя файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        logging.info(f'Сохранение файла: {file_path}')
        
        try:
            file.save(file_path)
        except Exception as e:
            logging.error(f'Ошибка при сохранении файла: {str(e)}')
            return jsonify({'error': 'Ошибка при сохранении файла'}), 500
        
        if not os.path.exists(file_path):
            logging.error('Файл не был сохранен')
            return jsonify({'error': 'Ошибка при сохранении файла'}), 500
        
        # Обновляем JSON файл
        json_path = os.path.join('static', 'photos.json')
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'photos': []}
            
            # Генерируем новый ID
            new_id = max([p['id'] for p in data['photos']] + [0]) + 1
            
            # Добавляем новое фото
            new_photo = {
                'id': new_id,
                'image_path': f'images/{filename}',
                'caption': caption
            }
            data['photos'].append(new_photo)
            
            # Сохраняем обновленный JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            logging.info(f'Файл успешно загружен: {filename}')
            return jsonify({
                'success': True, 
                'message': 'Файл успешно загружен',
                'photo': new_photo
            })
            
        except Exception as e:
            logging.error(f'Ошибка при обновлении JSON: {str(e)}')
            # В случае ошибки удаляем загруженный файл
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': f'Ошибка при обновлении данных: {str(e)}'}), 500
            
    except Exception as e:
        logging.error(f'Внутренняя ошибка сервера: {str(e)}')
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500

@app.route('/admin/delete/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    try:
        with open('static/photos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Находим фото для удаления
        photo = next((p for p in data['photos'] if p['id'] == photo_id), None)
        if photo:
            # Удаляем файл
            file_path = os.path.join('static', photo['image_path'])
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Удаляем запись из JSON
            data['photos'] = [p for p in data['photos'] if p['id'] != photo_id]
            
            # Сохраняем обновленный JSON
            with open('static/photos.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            return jsonify({'success': True})
    except Exception as e:
        logging.error(f'Ошибка при удалении фото: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/admin/edit/<int:photo_id>', methods=['POST'])
@login_required
def edit_photo(photo_id):
    try:
        new_caption = request.form.get('caption')
        if not new_caption:
            return jsonify({'error': 'Подпись обязательна'}), 400

        with open('static/photos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Обновляем подпись
        for photo in data['photos']:
            if photo['id'] == photo_id:
                photo['caption'] = new_caption
                break
        
        # Сохраняем обновленный JSON
        with open('static/photos.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f'Ошибка при редактировании фото: {str(e)}')
        return jsonify({'error': str(e)}), 500

def validate_image(file):
    try:
        # Проверка расширения
        if not allowed_file(file.filename):
            return False, f'Недопустимый тип файла. Разрешены только: {", ".join(ALLOWED_EXTENSIONS)}'
        
        # Проверка размера файла
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size > MAX_CONTENT_LENGTH:
            return False, 'Файл слишком большой. Максимальный размер: 16MB'
        
        return True, ''
    except Exception as e:
        logging.error(f'Ошибка при проверке файла: {str(e)}')
        return False, 'Ошибка при проверке файла'

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
        logging.error(f"Ошибка при инициализации БД: {e}")

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("Сервер запущен! Откройте в браузере:")
    print("http://localhost:5000/")
    print("=" * 50 + "\n")
    app.run(debug=True)