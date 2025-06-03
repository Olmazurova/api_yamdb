from django.utils import timezone
from rest_framework.exceptions import ValidationError


def year_validator(value):
    if value > timezone.now().year:
        raise ValidationError('Год не может быть больше текущего!')
