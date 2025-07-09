from typing import Optional

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    func,
    Table,
    UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(100))
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    words: Mapped[list["Word"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    answers: Mapped[list["UserAnswer"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_word: Mapped[str] = mapped_column(String(100), nullable=False)
    example: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    owner: Mapped["User"] = relationship(back_populates="words")
    translations: Mapped[list["Translation"]] = relationship(back_populates="word", cascade="all, delete-orphan")
    answers: Mapped[list["UserAnswer"]] = relationship(back_populates="word")
    categories: Mapped[list["Category"]] = relationship(secondary="word_categories", back_populates="words")

    __table_args__ = (UniqueConstraint("original_word", "user_id", name="uq_user_word"),)

class Translation(Base):
    __tablename__ = "translations"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    translation: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    word: Mapped["Word"] = relationship(back_populates="translations")
    user_answers: Mapped[list["UserAnswer"]] = relationship(back_populates="translation", cascade="all, delete-orphan")


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    word_id: Mapped[int | None] = mapped_column(ForeignKey("words.id", ondelete="SET NULL"))
    translation_id: Mapped[int | None] = mapped_column(ForeignKey("translations.id", ondelete="SET NULL"))
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship(back_populates="answers")
    word: Mapped[Optional["Word"]] = relationship(back_populates="answers")
    translation: Mapped[Optional["Translation"]] = relationship(back_populates="user_answers")
# Optional 2x
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    words: Mapped[list["Word"]] = relationship(secondary="word_categories", back_populates="categories")


word_categories = Table(
    "word_categories",
    Base.metadata,
    Column("word_id", Integer, ForeignKey("words.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
)