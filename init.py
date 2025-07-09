from sqlalchemy.orm import Session
from models import Word, Translation, Category
from datetime import datetime

def words(db: Session):
    if db.query(Word).first(): # если есть слова, то ничего не делаем
        return

    color_words = {
        "Red": {
            "example": "His face turns red when he gets angry.",
            "translations": ["being the same colour as blood", "Красный"]
        },
        "Blue": {
            "example": "Why is the sky blue?",
            "translations": ["being the same colour as the sky when there are no clouds", "Синий"]
        },
        "Green": {
            "example": "Green color harmonizes with red one.",
            "translations": ["being the same colour as grass", "Зелёный"]
        },
        "Yellow": {
            "example": "The leaves turned yellow.",
            "translations": ["being the same colour as a lemon or the sun", "Жёлтый"]
        },
        "Black": {
            "example": "He had a black suit on.",
            "translations": ["being the colour of coal or of the sky on a very dark night", "Чёрный"]
        },
        "White": {
            "example": "He had a long, white beard.",
            "translations": ["being the colour of snow or milk", "Белый"]
        },
        "Pink": {
            "example": "Her dress is pale pink.",
            "translations": ["being a pale red colour", "Розовый"]
        },
        "Purple": {
            "example": "The King was clothed in a purple gown.",
            "translations": ["being a colour that is a mixture of red and blue", "Фиолетовый"]
        },
        "Orange": {
            "example": "I think orange goes perfectly with my hair.",
            "translations": ["being a colour that is a mixture of red and yellow", "Оранжевый"]
        },
        "Brown": {
            "example": "Her hair is dark brown like mine.",
            "translations": ["being the same colour as chocolate or soil", "Коричневый"]
        }
    }

    pronoun_words = {
        "I": {
            "example": "Chris and I have been married for twelve years.",
            "translations": ["Я"]
        },
        "You": {
            "example": "I love you.",
            "translations": ["Вы", "Ты"]
        },
        "He": {
            "example": "He was rich.",
            "translations": ["Он"]
        },
        "She": {
            "example": "I want no angel, only she.",
            "translations": ["Она"]
        },
        "We": {
            "example": "Shall we stop for a coffee?",
            "translations": ["Мы"]
        },
        "They": {
            "example": "They all want to come to the wedding.",
            "translations": ["Они"]
        },
        "It": {
            "example": "Is it still raining?",
            "translations": ["Оно"]
        }
    }


    colors_category = Category(name="Цвета")
    pronouns_category = Category(name="Местоимения")
    db.add_all([colors_category, pronouns_category])
    db.flush()  # получаем Idшки категорий

    def add_words(words_dict, category_obj):
        for word, data in words_dict.items():
            new_word = Word(original_word=word, example=data["example"], created_at=datetime.utcnow())
            new_word.categories.append(category_obj)
            db.add(new_word)
            db.flush() # получаем Id для new_word
            for tr in data["translations"]:
                db.add(Translation(word_id=new_word.id, translation=tr))

    add_words(color_words, colors_category)
    add_words(pronoun_words, pronouns_category)

    db.commit()
