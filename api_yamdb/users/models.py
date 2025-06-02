from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

class User(AbstractUser):
    """Кастомная модель пользователя с дополнительными полями"""
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    email = models.EmailField(unique=True, verbose_name='Email')
    bio = models.TextField(blank=True, verbose_name='Биография')
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Код подтверждения'
    )
    password = models.CharField(_('password'), max_length=128, blank=True, null=True)

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

