from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from reviews.constants import LIMIT_TEXT, MAX_LENGTH

User = get_user_model()



class CreatedAt(models.Model):
    """Абстрактная модель автодобавления даты создания записи"""

    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено"
    )

    class Meta:
        abstract = True

class Group(models.Model):
    """Категории."""

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name="Заголовок"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title[:LIMIT_TEXT]

class Title(models.Model):
    """Произведения."""

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name="Заголовок"
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="Год выпуска"
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Категория",
    )

class Review(CreatedAt):
    """Рецензии."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Произведение", 
    )
    text = models.TextField(
        verbose_name="Текст"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор отзыва"
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Оценка"
    )

class Genre(models.Model):
    """Жанры."""
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name="Заголовок"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
    )

class Comment(CreatedAt):
    """Комментарии к произведениям."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')

class GenreTitle(models.Model):
    """Соответствие произведения жанрам."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Произведение", 
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Жанр", 
    )
