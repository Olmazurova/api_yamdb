from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import LIMIT_TEXT, MAX_LENGTH, MAX_SCORE, MIN_SCORE
from .validators import year_validator

User = get_user_model()


class AuthorTextCreateModel(models.Model):
    """Абстрактная модель добавляет поля текст, автор и дата создания записи."""

    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено', db_index=True
    )

    class Meta:
        abstract = True
        ordering = ('pub_date',)


class NameBaseModel(models.Model):
    """Абстрактная модель, добавляющая поле name в модель."""

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )

    class Meta:
        abstract = True
        ordering = ('id',)

    def __str__(self):
        return self.name[:LIMIT_TEXT]


class SlugNameModel(NameBaseModel):
    """Абстрактная модель, добавляющая поле slug в модель."""

    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta(NameBaseModel.Meta):
        abstract = True


class Group(SlugNameModel):
    """Категории."""

    class Meta(SlugNameModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(SlugNameModel):
    """Жанры."""

    class Meta(SlugNameModel.Meta):
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(NameBaseModel):
    """Произведения."""

    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска',
        validators=[year_validator,]
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Категория',
    )
    description = models.TextField(verbose_name='Описание')
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')

    class Meta(NameBaseModel.Meta):
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'


class Review(AuthorTextCreateModel):
    """Рецензии."""

    title = models.ForeignKey(
        Title,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MaxValueValidator(
                MAX_SCORE,
                'Оценка не может быть больше 10'
            ),
            MinValueValidator(
                MIN_SCORE,
                'Оценка не может быть меньше 1'
            )
        ]
    )

    class Meta(AuthorTextCreateModel.Meta):
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'
            ),
        ]

    def __str__(self):
        return f'Отзыв {self.author} на {self.title}'


class Comment(AuthorTextCreateModel):
    """Комментарии к произведениям."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )

    class Meta(AuthorTextCreateModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий {self.author} на {self.review}'
