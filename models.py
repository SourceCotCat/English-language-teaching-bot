from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class Categories(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='categories_pkey'),
        UniqueConstraint('name', name='categories_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    word: Mapped[List['Words']] = relationship('Words', secondary='word_categories', back_populates='category')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('telegram_id', name='users_telegram_id_key'),
        Index('idx_users_telegram_id', 'telegram_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[Optional[str]] = mapped_column(String(100))
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user_words: Mapped[List['UserWords']] = relationship('UserWords', back_populates='user')
    user_answers: Mapped[List['UserAnswers']] = relationship('UserAnswers', back_populates='user')


class Words(Base):
    __tablename__ = 'words'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='words_pkey'),
        UniqueConstraint('original_word', name='words_original_word_key'),
        Index('idx_words_original_word', 'original_word')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_word: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    example: Mapped[Optional[str]] = mapped_column(Text)

    category: Mapped[List['Categories']] = relationship('Categories', secondary='word_categories', back_populates='word')
    translations: Mapped[List['Translations']] = relationship('Translations', back_populates='word')
    user_words: Mapped[List['UserWords']] = relationship('UserWords', back_populates='word')
    user_answers: Mapped[List['UserAnswers']] = relationship('UserAnswers', back_populates='word')


class Translations(Base):
    __tablename__ = 'translations'
    __table_args__ = (
        ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE', name='translations_word_id_fkey'),
        PrimaryKeyConstraint('id', name='translations_pkey'),
        Index('idx_translations_word_id', 'word_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    translation: Mapped[str] = mapped_column(String(100))
    word_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    word: Mapped[Optional['Words']] = relationship('Words', back_populates='translations')
    user_answers: Mapped[List['UserAnswers']] = relationship('UserAnswers', back_populates='translation')


class UserWords(Base):
    __tablename__ = 'user_words'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_words_user_id_fkey'),
        ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE', name='user_words_word_id_fkey'),
        PrimaryKeyConstraint('id', name='user_words_pkey'),
        Index('idx_user_words_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    word_id: Mapped[Optional[int]] = mapped_column(Integer)
    added_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='user_words')
    word: Mapped[Optional['Words']] = relationship('Words', back_populates='user_words')


t_word_categories = Table(
    'word_categories', Base.metadata,
    Column('word_id', Integer, primary_key=True, nullable=False),
    Column('category_id', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', name='word_categories_category_id_fkey'),
    ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE', name='word_categories_word_id_fkey'),
    PrimaryKeyConstraint('word_id', 'category_id', name='word_categories_pkey')
)


class UserAnswers(Base):
    __tablename__ = 'user_answers'
    __table_args__ = (
        ForeignKeyConstraint(['translation_id'], ['translations.id'], ondelete='SET NULL', name='user_answers_translation_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_answers_user_id_fkey'),
        ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='SET NULL', name='user_answers_word_id_fkey'),
        PrimaryKeyConstraint('id', name='user_answers_pkey'),
        Index('idx_user_answers_user_id', 'user_id'),
        Index('idx_user_answers_word_id', 'word_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    word_id: Mapped[Optional[int]] = mapped_column(Integer)
    translation_id: Mapped[Optional[int]] = mapped_column(Integer)
    answered_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    translation: Mapped[Optional['Translations']] = relationship('Translations', back_populates='user_answers')
    user: Mapped[Optional['Users']] = relationship('Users', back_populates='user_answers')
    word: Mapped[Optional['Words']] = relationship('Words', back_populates='user_answers')
