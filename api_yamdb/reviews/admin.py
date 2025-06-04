from django.contrib import admin

from users.models import User
from .models import Comment, Genre, Group, Review, Title

admin.site.empty_value_display = 'Не задано'


class LinkedReviewsInline(admin.TabularInline):
    """Класс для отражения в админке связанных с произведением отзывов."""

    model = Review
    fields = ('author', 'text')
    extra = 0


class LinkedCommentsInline(admin.TabularInline):
    """Класс для отражения в админке связанных с отзывом комментариев."""

    model = Comment
    fields = ('author', 'text')
    extra = 0


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Администрирование комментариев."""

    list_display = ('author', 'review', 'pub_date', 'text')
    list_filter = ('author', 'review', 'pub_date')
    list_display_links = ('author', 'review')


@admin.register(Group)
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Администрирование категорий и жанров."""

    list_display = ('name', 'slug')
    list_filter = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Администрирование отзывов."""

    list_display = ('author', 'title', 'pub_date', 'score', 'text')
    list_filter = ('author', 'title', 'pub_date', 'score')
    list_display_links = ('author', 'title')
    list_editable = ('score',)
    inlines = (LinkedCommentsInline,)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Администрирование произведений."""

    list_display = ('name', 'year', 'group', 'description')
    list_filter = ('name', 'year', 'group', 'genre')
    inlines = (LinkedReviewsInline,)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Администрирование пользователей."""

    list_display = ('username', 'role', 'email', 'first_name', 'last_name',)
    list_filter = ('role', 'email', 'username', 'first_name', 'last_name',)
    list_display_links = ('username',)
