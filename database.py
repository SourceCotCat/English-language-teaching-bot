from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Users, Categories, Words, Translations, UserWords
from config import SessionLocal
from sqlalchemy import func
import random


def new_user(user_data):
    """
    Регистрирует пользователя, если его ещё нет в базе.
    Возвращает ID пользователя.
    """
    session: Session = SessionLocal()
    try:
        user = session.query(Users).filter_by(telegram_id=user_data.id).first()
        if user:
            return user.id

        new_user = Users(
            telegram_id=user_data.id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        session.add(new_user)
        session.flush()  # получаем ID, но без commit
        return new_user.id

    except SQLAlchemyError as e:
        session.rollback()
        print(f"[ERROR] Ошибка при регистрации пользователя: {e}")
        raise
    finally:
        session.close()

def get_categories():
    """
    Возвращает список всех доступных категорий.
    :return: список кортежей (id, name)
    """
    session: Session = SessionLocal()
    try:
        categories = session.query(Categories).all()
        return [(c.id, c.name) for c in categories]
    finally:
        session.close()


def get_words_by_category(category_id):
    """
    Возвращает случайное слово из указанной категории.
    :param category_id: id категории
    :return: (word_id, original_word, translation)
    """
    session: Session = SessionLocal()
    try:
        category = session.query(Categories).get(category_id)
        if not category or not category.word:
            return None

        word = random.choice(category.word)
        if not word.translations:
            return None

        translation = random.choice(word.translations)
        return word.id, word.original_word, translation.translation

    finally:
        session.close()


def get_word_and_vars():
    """
    Возвращает случайное слово и варианты перевода (1 правильный + 3 неправильных).
    :return: (original_word, options, correct_translation)
    """
    session: Session = SessionLocal()
    try:
        word = session.query(Words).order_by(func.random()).first()
        if not word or not word.translations:
            return None

        correct_translation = random.choice(word.translations).translation

        wrongs = (
            session.query(Translations)
            .filter(Translations.word_id != word.id)
            .order_by(func.random())
            .limit(3)
            .all()
        )
        options = [correct_translation] + [w.translation for w in wrongs]
        random.shuffle(options)

        return word.original_word, options, correct_translation

    finally:
        session.close()


def add_word(user_id, original, translation, example):
    """
    Добавляет новое слово и его перевод в БД для конкретного пользователя.

    :param user_id: ID пользователя из БД
    :param original: оригинальное слово (например, "кот")
    :param translation: перевод (например, "cat")
    :param example: пример использования
    :return: True если успешно, иначе False
    """
    session: Session = SessionLocal()
    try:
        word = session.query(Words).filter_by(original_word=original).first()
        if not word:
            word = Words(original_word=original, example=example)
            session.add(word)
            session.flush()

        # Добавляем перевод
        t = Translations(word_id=word.id, translation=translation)
        session.add(t)

        # Связываем с пользователем
        link = UserWords(user_id=user_id, word_id=word.id)
        session.add(link)

        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        print(f"[ERROR] Ошибка при добавлении слова: {e}")
        return False
    finally:
        session.close()


def delete_word(user_id, original_word):
    """
    Удаляет пользовательское слово по оригинальному слову.

    :param user_id: ID пользователя
    :param original_word: слово на родном языке
    :return: True если удалено, иначе False
    """
    session = SessionLocal()
    try:
        # Приводим к нижнему регистру
        word = (
            session.query(Words)
            .filter(func.lower(Words.original_word) == original_word.lower())
            .first())

        if not word:
            return False

        link = (
            session.query(UserWords)
            .filter_by(user_id=user_id, word_id=word.id)
            .first())

        if not link:
            return False

        session.delete(link)
        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        print(f"[ERROR] Ошибка при удалении слова: {e}")
        return False
    finally:
        session.close()

def get_wrong_translations(word_id):
    session: Session = SessionLocal()
    try:
        wrongs = (
            session.query(Translations)
            .filter(Translations.word_id != word_id)
            .order_by(func.random())
            .limit(3)
            .all()
        )
        return [t.translation for t in wrongs]
    finally:
        session.close()
