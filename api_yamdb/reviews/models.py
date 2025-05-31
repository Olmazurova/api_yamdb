from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.constants import LIMIT_TEXT, MAX_LENGTH, MAX_SCORE, MIN_SCORE

User = get_user_model()


class CreatedAt(models.Model):
    """Абстрактная модель автодобавления даты создания записи."""

    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено', db_index=True
    )

    class Meta:
        abstract = True


class Group(models.Model):
    """Категории."""

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:LIMIT_TEXT]


class Genre(models.Model):
    """Жанры."""
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:LIMIT_TEXT]


class Title(models.Model):
    """Произведения."""

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска'
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        # null=True,
        # blank=True,
        verbose_name='Категория',
    )
    description = models.TextField()
    genre = models.ManyToManyField(Genre, through='GenreTitle')

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:LIMIT_TEXT]


class GenreTitle(models.Model):
    """Соответствие произведения жанрам."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр',
    )


class Review(CreatedAt):
    """Рецензии."""

    title = models.ForeignKey(
        Title,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews',
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва',
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[MaxValueValidator(MAX_SCORE), MinValueValidator(MIN_SCORE)]
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'
            ),
        ]

    def __str__(self):
        return f'Отзыв {self.author} на {self.title}'


class Comment(CreatedAt):
    """Комментарии к произведениям."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий {self.author} на {self.review}'
