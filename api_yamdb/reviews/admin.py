from django.contrib import admin

from users.models import User
from .models import Comment, Genre, Group, Review, Title

admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Genre)
admin.site.register(Review)
admin.site.register(Title)
admin.site.register(User)
