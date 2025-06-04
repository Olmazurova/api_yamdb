from django.utils import timezone
from rest_framework.exceptions import ValidationError


def year_validator(value):
    """Валидатор проверяет, что указан год не больше текущего."""
    if value > timezone.now().year:
        raise ValidationError('Год не может быть больше текущего!')
