import psycopg2
from config import DB_CONFIG
import random

def connect():
    """
    Устанавливаем соединение с БД.
    """        
    return psycopg2.connect(**DB_CONFIG)


def new_user(user_data):
    print("Получен пользователь:", user_data.id, user_data.first_name)

    conn = connect()  
    cur = conn.cursor()
    print("[DEBUG] Подключение к БД установлено")

    telegram_id = user_data.id
    username = user_data.username
    first_name = user_data.first_name
    last_name = user_data.last_name if user_data.last_name else None

    try:
        cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        result = cur.fetchone()
        if result:
            print(f"Пользователь {telegram_id} уже существует. ID: {result[0]}")
            cur.close()
            return result[0]

        cur.execute("""
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (telegram_id, username, first_name, last_name))

        new_id = cur.fetchone()[0]
        print(f"Добавлен новый пользователь: {telegram_id}, ID: {new_id}")
        conn.commit()  
        return new_id

    except Exception as e:
        print(f"[ERROR] Ошибка при регистрации пользователя: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
    

def get_categories():
    """
    Возвращает список всех доступных категорий.

    :return: список кортежей (id, name)
    """
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM categories;")
        return cur.fetchall()


def get_words_by_category(category_id):
    """
    Возвращает случайное слово из указанной категории.

    :param category_id: id категории
    :return: (word_id, original_word, translation)
    """
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT w.id, w.original_word, t.translation 
            FROM words w
            JOIN word_categories wc ON w.id = wc.word_id
            JOIN translations t ON w.id = t.word_id
            WHERE wc.category_id = %s
            ORDER BY RANDOM()
            LIMIT 1;
        """, (category_id,))
        return cur.fetchone()


def get_word_and_vars():
    """
    Возвращает случайное слово и варианты перевода (1 правильный + 3 неправильных).

    :return: (original_word, options, correct_translation)
    """
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT w.id, w.original_word, t.translation 
            FROM words w
            JOIN translations t ON w.id = t.word_id
            ORDER BY RANDOM() LIMIT 1;
        """)
        correct = cur.fetchone()

        word_id, original, correct_translation = correct

        cur.execute("""
            SELECT translation FROM translations
            WHERE word_id != %s
            ORDER BY RANDOM() LIMIT 3;
        """, (word_id,))

        wrong_translations = [row[0] for row in cur.fetchall()]
        options = [correct_translation] + wrong_translations
        random.shuffle(options)

        return original, options, correct_translation


def add_word(user_id, original, translation, example):
    """
    Добавляет новое слово и его перевод в БД для конкретного пользователя.

    :param user_id: ID пользователя из БД
    :param original: оригинальное слово (например, "кот")
    :param translation: перевод (например, "cat")
    :param example: пример использования
    :return: True если успешно, иначе False
    """
    with connect() as conn:
        cur = conn.cursor()

        # Проверяем, есть ли уже такое слово
        cur.execute("SELECT id FROM words WHERE original_word = %s", (original,))
        word_row = cur.fetchone()

        if word_row:
            word_id = word_row[0]
        else:
            # Добавляем новое слово
            cur.execute("""
                INSERT INTO words (original_word, example)
                VALUES (%s, %s) RETURNING id
            """, (original, example))
            word_id = cur.fetchone()[0]

        # Добавляем перевод
        cur.execute("""
            INSERT INTO translations (word_id, translation)
            VALUES (%s, %s)
        """, (word_id, translation))

        # Связываем пользователем со словом
        cur.execute("""
            INSERT INTO user_words (user_id, word_id)
            VALUES (%s, %s)
        """, (user_id, word_id))

        conn.commit()
        return True


def delete_word(user_id, original_word):
    """
    Удаляет пользовательское слово по оригинальному слову.

    :param user_id: ID пользователя
    :param original_word: слово на родном языке
    :return: True если удалено, иначе False
    """
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM user_words
            USING words
            WHERE user_words.user_id = %s
              AND words.original_word = %s
              AND user_words.word_id = words.id;
        """, (user_id, original_word))
        conn.commit()
        return cur.rowcount > 0


def get_wrong_translations(word_id):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT translation FROM translations
            WHERE word_id != %s
            ORDER BY RANDOM() LIMIT 3;
        """, (word_id,))
        return [row[0] for row in cur.fetchall()]

