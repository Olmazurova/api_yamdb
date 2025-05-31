from django.contrib import admin

from .models import Group, Comment, Genre, Review, Title, User

admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Genre)
admin.site.register(Review)
admin.site.register(Title)
admin.site.register(User)
