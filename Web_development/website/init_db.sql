CREATE TABLE IF NOT EXISTS photo (
    id SERIAL PRIMARY KEY,
    image_path VARCHAR(200) NOT NULL,
    caption VARCHAR(200) NOT NULL
);

-- Добавляем тестовые данные
INSERT INTO photo (image_path, caption) VALUES
    ('/static/images/1.jpg', 'Токио, район Синдзюку'),
    ('/static/images/2.jpg', 'Храм Сэнсо-дзи'),
    ('/static/images/3.jpg', 'Башня Скайтри');
