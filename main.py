import telebot
from telebot import types
from database import (
    connect,
    new_user,
    get_categories,
    get_words_by_category,
    get_word_and_vars,
    add_word,
    delete_word,
    get_wrong_translations
)
import os
import random
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))
user_states = {}  # временное хранилище состояния пользователя


@bot.message_handler(commands=['start'])
def welcome(message):
    user = message.from_user

    # Регистрация пользователя в БД
    try:
        user_id_db = new_user(user)  
        print(f"[INFO] Пользователь {user.id} зарегистрирован с ID в БД: {user_id_db}")
    except Exception as e:
        print(f"[ERROR] Не удалось зарегистрировать пользователя: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка при регистрации. Попробуйте позже.")
        return

    first_name = user.first_name
    last_name = user.last_name if user.last_name else ""
    bot.reply_to(message, f"Привет, {first_name} {last_name}! Начнём учить английский!")
    
    menu(message.chat.id)

def menu(chat):
    keyb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    press_learn = types.KeyboardButton('🧠 Учить слова')
    press_category = types.KeyboardButton('📑 Выбрать категорию')
    press_add = types.KeyboardButton('📝 Добавить слово')
    press_delete = types.KeyboardButton('🗑 Удалить слово')
    keyb.add(press_learn, press_category, press_add, press_delete)
    bot.send_message(chat, "Выбери действие:", reply_markup=keyb)


@bot.message_handler(func=lambda m: m.text == '📑 Выбрать категорию')
def choose_category(message):
    categories = get_categories()
    if not categories:
        bot.send_message(message.chat.id, "Категории пока не добавлены.")
        return
    inline_keyb = types.InlineKeyboardMarkup(row_width=1)
    for id, name in categories:
        inline_keyb.add(types.InlineKeyboardButton(name, callback_data=f"category_{id}"))
    bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=inline_keyb)


@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def category(call):
    category_id = int(call.data.split("_")[1])
    user_states[call.from_user.id] = {'category_id': category_id, 'attempts': 0}
    send_next_word(call.from_user.id, category_id)


def send_next_word(chat_id, category_id=None):
    if category_id:
        word_data = get_words_by_category(category_id)
        if not word_data:
            bot.send_message(chat_id, "Нет больше слов в этой категории.")
            menu(chat_id)
            return

        word_id, original, correct_translation = word_data
        wrong_translations = get_wrong_translations(word_id)

        # Формируем варианты ответов
        options = [correct_translation] + wrong_translations
        random.shuffle(options)

        user_states[chat_id] = {
            'correct': correct_translation,
            'category_id': category_id,
            'attempts': 0
        }

    else:
        original, options, correct_translation = get_word_and_vars()
        if not options:
            bot.send_message(chat_id, "Нет доступных слов.")
            menu(chat_id)
            return

        # Подстраховка на случай, если что-то пошло не так
        if len(options) < 4:
            with connect() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT translation FROM translations
                    WHERE word_id != %s
                    ORDER BY RANDOM() LIMIT 3
                """, (word_id,))
                extra_wrongs = [row[0] for row in cur.fetchall()]
                options = list(set([correct_translation] + extra_wrongs))[:4]

        random.shuffle(options)

        user_states[chat_id] = {
            'correct': correct_translation,
            'category_id': None,
            'attempts': 0
        }

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [types.KeyboardButton(option) for option in options]
    buttons.append(types.KeyboardButton("⬅ Назад"))  # добавляем кнопку назад
    markup.add(*buttons)

    bot.send_message(
        chat_id,
        f"Переведи слово: *{original}*",
        parse_mode="Markdown",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == '🧠 Учить слова')  # взаимодействие с кнопочкой press_learn
def lear_words(message):
    send_next_word(message.chat.id)


@bot.message_handler(func=lambda m: m.text == '📝 Добавить слово')
def handle_add_word(message):
    bot.send_message(message.chat.id, 'Введите слово, которое хотите добавить:(на английском языке)')
    user_states[message.chat.id] = {'stage': 'original'}


@bot.message_handler(func=lambda m: m.text == '🗑 Удалить слово')
def handle_delete_word(message):
    bot.send_message(message.chat.id, 'Введите слово, которое хотите удалить:')
    user_states[message.chat.id] = {'stage': 'delete'}


@bot.message_handler(func=lambda message: True)
def handle_input(message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states.get(chat_id, {})

    # Кнопка "Назад"
    if text == "⬅ Назад":
        menu(chat_id)
        return

    # Проверка ответа на перевод
    if state.get('correct') is not None:
        if text == state['correct']:
            bot.send_message(chat_id, "✅ Правильно!")
            if state.get('category_id') is not None:
                send_next_word(chat_id, state['category_id'])
            else:
                send_next_word(chat_id)
            return
        else:
            attempts = state.get('attempts', 0) + 1
            if attempts < 2:
                bot.send_message(chat_id, f"❌ Неправильно. У вас {attempts}/2 попытки. Попробуйте снова:")
                user_states[chat_id]['attempts'] = attempts
            else:
                bot.send_message(chat_id, f"❌ Неправильно. Правильный ответ: *{state['correct']}*", parse_mode="Markdown")
                menu(chat_id)
            return

    # Логика добавления слова
    if state.get('stage') == 'original':
        user_states[chat_id]['original'] = text
        user_states[chat_id]['stage'] = 'translation'
        bot.send_message(chat_id, "Введите перевод на русский:")

    elif state.get('stage') == 'translation':
        user_states[chat_id]['translation'] = text
        user_states[chat_id]['stage'] = 'example'
        bot.send_message(chat_id, "Введите пример использования:")

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

    # Логика удаления слова
    elif state.get('stage') == 'delete':
        deleted = delete_word(new_user(message.from_user), text)
        if deleted:
            bot.send_message(chat_id, "✅ Слово удалено.")
        else:
            bot.send_message(chat_id, "❌ Такого слова нет в вашем списке.")
        menu(chat_id)

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
    print('Бот запущен')
    bot.polling(none_stop=True)