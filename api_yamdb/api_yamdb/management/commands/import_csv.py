import csv

from django.core.management.base import BaseCommand

from reviews.models import (Comment, Genre, GenreTitle, Group, Review, Title,
                            User)


class Command(BaseCommand):

    def handle(self, *args, **options):

        with open(
            'static/data/category.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:
                Group.objects.create(**row)

        with open(
            'static/data/genre.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:
                Genre.objects.create(**row)

        with open(
            'static/data/users.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:
                User.objects.create(**row)

        with open(
            'static/data/titles.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:
                group_id = row.pop('category')
                group = Group.objects.get(id=group_id)
                row['group'] = group
                Title.objects.create(**row)

        with open(
            'static/data/genre_title.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:
                GenreTitle.objects.create(**row)

        with open(
            'static/data/review.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                user_id = row.pop('author')
                user = User.objects.get(id=user_id)
                row['author'] = user
                Review.objects.create(**row)

        with open(
            'static/data/comments.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                user_id = row.pop('author')
                user = User.objects.get(id=user_id)
                row['author'] = user
                Comment.objects.create(**row)
