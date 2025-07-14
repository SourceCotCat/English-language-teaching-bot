from sqlalchemy.exc import SQLAlchemyError
from models import User, Category, Word, Translation, UserAnswer, word_categories  
from config import SessionLocal
from sqlalchemy import func
import random
from sqlalchemy.orm import aliased
from sqlalchemy.sql import label


def new_user(user_data):
    """
    Регистрирует пользователя, если его ещё нет в базе.
    Возвращает ID пользователя.
    """
    with SessionLocal() as session:
        user = session.query(User).filter_by(telegram_id=user_data.id).first()
        if user:
            return user.id

        new_user = User(
            telegram_id=user_data.id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        session.add(new_user)
        session.commit()
        user_id = new_user.id
        return user_id


def get_categories():
    """
    Возвращает список всех доступных категорий.
    :return: список кортежей (id, name)
    """
    with SessionLocal() as session:
        categories = session.query(Category).all()
        return [(c.id, c.name) for c in categories]



def get_words_by_category(category_id, user_id):
    """
    Возвращает случайное слово из указанной категории.
    :param category_id: id категории
    :return: (word_id, original_word, translation)
    """
    with SessionLocal() as session:
        word = (
            session.query(Word)
            .join(word_categories, word_categories.c.word_id == Word.id)
            .filter(word_categories.c.category_id == category_id)
            .filter((Word.user_id == None) | (Word.user_id == user_id))
            .order_by(func.random())
            .first()
        )

        if not word or not word.translations:
            return None

        translation = random.choice(word.translations)
        return word.id, word.original_word, translation.translation


def get_word_and_vars(user_id):
    """
    Возвращает случайное слово и варианты перевода (1 правильный + 3 неправильных).
    :return: (original_word, options, correct_translation)
    """
    with SessionLocal() as session:
        subquery = (
            session.query(
                Word.id.label("word_id"),
                Word.original_word.label("original_word"),
                Translation.translation.label("translation"),
            )
            .join(Translation, Translation.word_id == Word.id)
            .filter((Word.user_id == None) | (Word.user_id == user_id))
            .order_by(func.random())
            .limit(4)
            .subquery()
        )

        results = session.query(subquery).all()

        if len(results) < 4:
            return None

        # 1ую пару берём как основную
        main = results[0]
        correct_translation = main.translation
        original_word = main.original_word

        # Остальные 3 — как неправильные переводы
        wrong_translations = [r.translation for r in results[1:]]

        options = [correct_translation] + wrong_translations
        random.shuffle(options)

        return original_word, options, correct_translation


def add_word(user_id, original, translation, example):
    """
    Добавляет новое слово и его перевод в БД для конкретного пользователя.
    """
    try:
        with SessionLocal() as session:
            word = (
                session.query(Word)
                .filter(func.lower(Word.original_word) == original.lower())
                .filter((Word.user_id == None) | (Word.user_id == user_id))
                .first())

            if word:
                # если это не общее слово и не пользователя, то запрещаем
                if word.user_id is not None and word.user_id != user_id:
                    return False
            else:
                # создаём новое слово для пользователя
                word = Word(original_word=original, example=example, user_id=user_id)
                session.add(word)
                session.flush() 

            # проверяем, есть ли уже такой перевод у этого слова
            existing_translation = (
                session.query(Translation)
                .filter_by(word_id=word.id, translation=translation)
                .first()
            )
            if not existing_translation:
                # добавляем перевод
                t = Translation(word=word, translation=translation)
                session.add(t)

            # связываем с пользователем через UserAnswer
            existing_link = (
                session.query(UserAnswer)
                .filter_by(user_id=user_id, word=word)
                .first()
            )
            if not existing_link:
                link = UserAnswer(user_id=user_id, word=word, is_correct=False)
                session.add(link)

            session.commit()
            return True

    except SQLAlchemyError as e:
        print(f"[ERROR] Ошибка при добавлении слова: {e}")
        return False


def delete_word(user_id, original_word):
    """
    Удаляет пользовательское слово по оригинальному слову.

    :param user_id: ID пользователя
    :param original_word: слово на родном языке
    :return: True если удалено, иначе False
    """
    try:
        with SessionLocal() as session:
            word = (
                session.query(Word)
                .filter(func.lower(Word.original_word) == original_word.lower())
                .filter(Word.user_id == user_id)  # Только пользовательское слово
                .first()
            )

            if not word:
                return False

            session.delete(word)
            session.commit()
            return True

    except SQLAlchemyError as e:
        print(f"[ERROR] Ошибка при удалении слова: {e}")
        return False


def get_wrong_translations(word_id, user_id):
    with SessionLocal() as session:
        wrongs = (
            session.query(Translation)
            .join(Word, Translation.word_id == Word.id)
            .filter(Translation.word_id != word_id)
            .filter((Word.user_id == None) | (Word.user_id == user_id))
            .order_by(func.random())
            .limit(3)
            .all()
        )
        return [t.translation for t in wrongs]

