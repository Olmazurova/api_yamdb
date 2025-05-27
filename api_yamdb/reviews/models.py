from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(models.Model):
    pass


class Genre(models.Model):
    pass


class Title(models.Model):
    pass


class Comment(models.Model):
    pass


class Review(models.Model):
    pass
