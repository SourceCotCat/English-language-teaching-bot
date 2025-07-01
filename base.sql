-- Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY, -- Уникальный идентификатор пользователя в БД
    telegram_id BIGINT UNIQUE NOT NULL, -- Telegram ID пользователя
    username VARCHAR(100),  -- Имя пользователя в Telegram
    first_name VARCHAR(100),  -- Имя пользователя
    last_name VARCHAR(100), -- Фамилия пользователя
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Дата и время регистрации пользователя в системе
);

-- Оригинальные слова (шаблон)
CREATE TABLE words (
    id SERIAL PRIMARY KEY, -- Уникальный идентификатор слова
    original_word VARCHAR(100) NOT NULL UNIQUE, -- Основное слово
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Дата и время создания слова
);

-- Перевод
CREATE TABLE translations (
    id SERIAL PRIMARY KEY, -- Уникальный ID перевода
    word_id INT REFERENCES words(id) ON DELETE CASCADE, -- Ссылка на слово из таблицы words
    translation VARCHAR(100) NOT NULL, -- Перевод слова 
    example TEXT, -- Пример использования перевода
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Время добавления перевода
);

-- Персональные слова пользователей
CREATE TABLE user_words (
    id SERIAL PRIMARY KEY, -- Уникальный идентификатор записи
    user_id INT REFERENCES users(id) ON DELETE CASCADE, -- Ссылка на пользователя из таблицы users если он удален то и его данные удаляются
    word_id INT REFERENCES words(id) ON DELETE CASCADE, -- Ссылка на слово из таблицы words
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Дата и время добавления слова 
);

-- История ответов
CREATE TABLE user_answers (
    id SERIAL PRIMARY KEY, -- Уникальный идентификатор ответа
    user_id INT REFERENCES users(id) ON DELETE CASCADE, -- Ссылка на пользователя из таблицы users
    word_id INT REFERENCES words(id) ON DELETE SET NULL, -- Ссылка на слово из таблицы words
    translation_id INT REFERENCES translations(id) ON DELETE SET NULL, -- Ссылка на конкретный перевод слова
    is_correct BOOLEAN NOT NULL, -- Результат ответа true или false
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Время, когда ответил пользователь
);

-- Создаем таблицу для хранения категорий слов 
CREATE TABLE categories (
    id SERIAL PRIMARY KEY, -- Уникальный идентификатор категории
    name VARCHAR(100) UNIQUE NOT NULL, -- Название категории, должно быть уникальным
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Время создания категории
);

-- Создаем таблицу для связи между словами и категориями
CREATE TABLE word_categories (
    word_id INT REFERENCES words(id) ON DELETE CASCADE, -- Ссылка на слово
    category_id INT REFERENCES categories(id) ON DELETE CASCADE, -- Ссылка на категорию
    PRIMARY KEY (word_id, category_id) -- Комбинированный первичный ключ
);


CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users (telegram_id);
CREATE INDEX IF NOT EXISTS idx_words_original_word ON words (original_word);
CREATE INDEX IF NOT EXISTS idx_translations_word_id ON translations (word_id);
CREATE INDEX IF NOT EXISTS idx_user_words_user_id ON user_words (user_id);
CREATE INDEX IF NOT EXISTS idx_user_answers_user_id ON user_answers (user_id);
CREATE INDEX IF NOT EXISTS idx_user_answers_word_id ON user_answers (word_id);


-- ALTER TABLE words ADD COLUMN example TEXT; поместила в итоговый sql в сами таблицы тк изначально было не так
-- ALTER TABLE translations DROP COLUMN IF EXISTS example;


INSERT INTO words (original_word, example) VALUES
('Red', 'His face turns red when he gets angry.'),
('Blue', 'Why is the sky blue?'),
('Green', 'Green color harmonizes with red one.'),
('Yellow', 'The leaves turned yellow.'),
('Black', 'He had a black suit on.'),
('White', 'He had a long, white beard.'),
('Pink', 'Her dress is pale pink.'),
('Purple', 'The King was clothed in a purple gown.'),
('Orange', 'I think orange goes perfectly with my hair.'),
('Brown', 'Her hair is dark brown like mine.'),
('I', 'Chris and I have been married for twelve years.'),
('You', 'I love you.'),
('He', 'He was rich.'),
('She', 'I want no angel, only she.'),
('We', 'Shall we stop for a coffee?'),
('They', 'They all want to come to the wedding.'),
('It', 'Is it still raining?');

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'Red'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'being the same colour as blood' FROM word_info
UNION ALL
SELECT id, 'Красный' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'Blue'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'being the same colour as the sky when there are no clouds' FROM word_info
UNION ALL
SELECT id, 'Синий' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'Green'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'being the same colour as grass' FROM word_info
UNION ALL
SELECT id, 'Зелёный' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'Yellow'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'being the same colour as a lemon or the sun' FROM word_info
UNION ALL
SELECT id, 'Жёлтый' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'Black'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'being the colour of coal or of the sky on a very dark night' FROM word_info
UNION ALL
SELECT id, 'Чёрный' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'White'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'being the colour of snow or milk' FROM word_info
UNION ALL
SELECT id, 'Белый' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'Pink'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'being a pale red colour' FROM word_info
UNION ALL
SELECT id, 'Розовый' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'Purple'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'being a colour that is a mixture of red and blue' FROM word_info
UNION ALL
SELECT id, 'Фиолетовый' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'Orange'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'being a colour that is a mixture of red and yellow' FROM word_info
UNION ALL
SELECT id, 'Оранжевый' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'Brown'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'being the same colour as chocolate or soil' FROM word_info
UNION ALL
SELECT id, 'Коричневый' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'I'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'Я' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'You'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'Вы' FROM word_info
UNION ALL
SELECT id, 'Ты' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'He'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'Он' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'She'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'Она' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'We'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'Мы' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'They'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'Они' FROM word_info;

WITH word_info AS (
    SELECT id FROM words WHERE original_word = 'It'
)
INSERT INTO translations (word_id, translation)
SELECT id, 'Оно' FROM word_info;

INSERT INTO categories (name) VALUES
('Цвета'),
('Местоимения')
ON CONFLICT (name) DO NOTHING;

INSERT INTO word_categories (word_id, category_id)
SELECT w.id, c.id
FROM words w
JOIN categories c ON c.name = 'Цвета'
WHERE w.original_word IN (
    'Red', 'Blue', 'Green', 'Yellow',
    'Black', 'White', 'Pink', 'Purple',
    'Orange', 'Brown'
);

INSERT INTO word_categories (word_id, category_id)
SELECT w.id, c.id
FROM words w
JOIN categories c ON c.name = 'Местоимения'
WHERE w.original_word IN (
    'I', 'You', 'He', 'She', 'We', 'They', 'It'
);

