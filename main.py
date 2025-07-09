# Импортируем библиотеку для Tg-бота
import telebot
from telebot import types

from config import init_bd

# Импортируем функции работы с БД через SQLAlchemy ORM
from database import (
    new_user,
    get_categories,
    get_words_by_category,
    get_word_and_vars,
    add_word,
    delete_word,
    get_wrong_translations
)

# Импорт стандартных библиотек
import os
import random
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Получаем токен из переменной окружения
bot = telebot.TeleBot(os.getenv("TOKEN"))

# Словарь для хранения состояний пользователя (что он делает)
user_states = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def welcome(message):
    user = message.from_user  # Получаем информацию о пользователе

    try:
        # Регистрируем пользователя в БД
        user_id_db = new_user(user)
        print(f"[INFO] Пользователь {user.id} зарегистрирован с ID в БД: {user_id_db}")
    except Exception as e:
        # Ошибка при регистрации
        print(f"[ERROR] Не удалось зарегистрировать пользователя: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка при регистрации. Попробуйте позже.")
        return

    # Приветственное сообщение
    first_name = user.first_name
    last_name = user.last_name if user.last_name else ""
    bot.reply_to(message, f"Привет, {first_name} {last_name}! Начнём учить английский!")

    # Отображаем главное меню
    menu(message.chat.id)


def menu(chat):
    # Создаём клавиатуру
    keyb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    press_learn = types.KeyboardButton('🧠 Учить слова')
    press_category = types.KeyboardButton('📑 Выбрать категорию')
    press_add = types.KeyboardButton('📝 Добавить слово')
    press_delete = types.KeyboardButton('🗑 Удалить слово')
    keyb.add(press_learn, press_category, press_add, press_delete)

    # Отправляем сообщение с меню
    bot.send_message(chat, "Выбери действие:", reply_markup=keyb)


# Обработчик выбора категории
@bot.message_handler(func=lambda m: m.text == '📑 Выбрать категорию')
def choose_category(message):
    categories = get_categories()  # Получаем категории из БД
    if not categories:
        bot.send_message(message.chat.id, "Категории пока не добавлены.")
        return

    # Создаём inline-кнопки
    inline_keyb = types.InlineKeyboardMarkup(row_width=1)
    for id, name in categories:
        inline_keyb.add(types.InlineKeyboardButton(name, callback_data=f"category_{id}"))

    # Отправляем список категорий
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=inline_keyb)


# Обработка нажатия на inline-кнопку с категорией
@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def category(call):
    category_id = int(call.data.split("_")[1])  # Получаем ID категории из текста
    user_states[call.from_user.id] = {'category_id': category_id, 'attempts': 0}  # Сохраняем состояние
    send_next_word(call.message.chat.id, call.from_user.id, category_id)  # Отправляем слово из категории


# Отправка следующего слова
def send_next_word(chat_id, user_id, category_id=None):
    if category_id:
        word_data = get_words_by_category(category_id, user_id)  # Получаем слово по категории
        if not word_data:
            bot.send_message(chat_id, "Нет больше слов в этой категории.")
            menu(chat_id)
            return

        word_id, original, correct_translation = word_data
        wrong_translations = get_wrong_translations(word_id, user_id)  # Получаем 3 неверных перевода
        options = [correct_translation] + wrong_translations
        random.shuffle(options)  # Перемешиваем варианты

        user_states[chat_id] = {
            'correct': correct_translation,
            'category_id': category_id,
            'attempts': 0
        }

    else:
        result = get_word_and_vars(user_id)  # Получаем случайное слово и варианты
        if not result:
            bot.send_message(chat_id, "Нет доступных слов.")
            menu(chat_id)
            return

        original, options, correct_translation = result

        user_states[chat_id] = {
            'correct': correct_translation,
            'category_id': None,
            'attempts': 0
        }

    # Создаём кнопки для вариантов перевода
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [types.KeyboardButton(option) for option in options]
    buttons.append(types.KeyboardButton("⬅ Назад"))
    markup.add(*buttons)

    # Отправляем вопрос пользователю
    bot.send_message(
        chat_id,
        f"Переведи слово: *{original}*",
        parse_mode="Markdown",
        reply_markup=markup
    )


# Обработка кнопки "Учить слова"
@bot.message_handler(func=lambda m: m.text == '🧠 Учить слова')
def lear_words(message):
    send_next_word(message.chat.id, message.from_user.id)

# Обработка добавления слова
@bot.message_handler(func=lambda m: m.text == '📝 Добавить слово')
def handle_add_word(message):
    bot.send_message(message.chat.id, 'Введите слово, которое хотите добавить (на английском):')
    user_states[message.chat.id] = {'stage': 'original'}

# Обработка удаления слова
@bot.message_handler(func=lambda m: m.text == '🗑 Удалить слово')
def handle_delete_word(message):
    bot.send_message(message.chat.id, 'Введите слово, которое хотите удалить:')
    user_states[message.chat.id] = {'stage': 'delete'}

# Обработка всех остальных сообщений
@bot.message_handler(func=lambda message: True)
def handle_input(message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states.get(chat_id, {})

    if text == "⬅ Назад":
        menu(chat_id)
        return

    # Проверка ответа
    if state.get('correct') is not None:
        if text == state['correct']:
            bot.send_message(chat_id, "✅ Правильно!")
            if state.get('category_id') is not None:
                send_next_word(chat_id, message.from_user.id, state['category_id'])
            else:
                send_next_word(chat_id, message.from_user.id)
        else:
            attempts = state.get('attempts', 0) + 1
            if attempts < 2:
                bot.send_message(chat_id, f"❌ Неправильно. Попробуйте снова ({attempts}/2):")
                user_states[chat_id]['attempts'] = attempts
            else:
                bot.send_message(chat_id, f"❌ Правильный ответ: *{state['correct']}*", parse_mode="Markdown")
                menu(chat_id)
        return

    # Этап 1: Добавление слова — оригинал(на англ)
    if state.get('stage') == 'original':
        user_states[chat_id]['original'] = text
        user_states[chat_id]['stage'] = 'translation'
        bot.send_message(chat_id, "Введите перевод на русский:")

    # Этап 2: перевод
    elif state.get('stage') == 'translation':
        user_states[chat_id]['translation'] = text
        user_states[chat_id]['stage'] = 'example'
        bot.send_message(chat_id, "Введите пример использования:")

    # Этап 3: пример
    elif state.get('stage') == 'example':
        example = text
        success = add_word(
            user_id=new_user(message.from_user),
            original=user_states[chat_id]['original'],
            translation=user_states[chat_id]['translation'],
            example=example
        )
        if success:
            bot.send_message(chat_id, "✅ Слово успешно добавлено!")
        else:
            bot.send_message(chat_id, "❌ Ошибка при добавлении слова.")
        menu(chat_id)

    # Удаление слова
    elif state.get('stage') == 'delete':
        deleted = delete_word(new_user(message.from_user), text)
        if deleted:
            bot.send_message(chat_id, "✅ Слово удалено.")
        else:
            bot.send_message(chat_id, "❌ Такого слова нет в вашем списке.")
        menu(chat_id)

# Поддержка ввода через текст 
@bot.message_handler(func=lambda message: message.text.lower() in ['учить слова', '🧠 учить слова'])
def handle_learn_words_text(message):
    lear_words(message)


@bot.message_handler(func=lambda message: message.text.lower() in ['выбрать категорию', '📑 выбрать категорию'])
def handle_choose_category_text(message):
    choose_category(message)


@bot.message_handler(func=lambda message: message.text.lower() in ['добавить слово', '📝 добавить слово'])
def handle_add_word_text(message):
    handle_add_word(message)


@bot.message_handler(func=lambda message: message.text.lower() in ['удалить слово', '🗑 удалить слово'])
def handle_delete_word_text(message):
    handle_delete_word(message)


if __name__ == '__main__':
    init_bd()
    print('База данных инициализирована')
    print('Бот запущен, кусь')
    bot.polling(none_stop=True)
