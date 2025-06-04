from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import MAX_LENGTH_CODE, MAX_LENGTH_PSW, MAX_LENGTH_ROLE


class User(AbstractUser):
    """Кастомная модель пользователя с дополнительными полями"""

    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    email = models.EmailField(unique=True, verbose_name='Email')
    bio = models.TextField(blank=True, verbose_name='Биография')
    role = models.CharField(
        max_length=MAX_LENGTH_ROLE,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(
        max_length=MAX_LENGTH_CODE,
        blank=True,
        verbose_name='Код подтверждения'
    )
    password = models.CharField(
        'password', max_length=MAX_LENGTH_PSW, blank=True, null=True
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR
