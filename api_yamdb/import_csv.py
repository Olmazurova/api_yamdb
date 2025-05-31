import csv
import sqlite3

con = sqlite3.connect('api_yamdb/db.sqlite3')
cur = con.cursor()

with open('api_yamdb/static/data/category.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute(
            'INSERT INTO reviews_group VALUES(?, ?, ?);',
            (row['id'], row['name'], row['slug'])
        )


with open('api_yamdb/static/data/comments.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute(
            'INSERT INTO reviews_comment VALUES(?, ?, ?, ?, ?);',
            (row['id'], row['pub_date'], row['text'], row['author'], row['review_id'])
        )


with open('api_yamdb/static/data/genre_title.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute(
            'INSERT INTO reviews_genretitle VALUES(?, ?, ?);',
            (row['id'], row['genre_id'], row['title_id'])
        )


with open('api_yamdb/static/data/genre.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute(
            'INSERT INTO reviews_genre VALUES(?, ?, ?);',
            (row['id'], row['name'], row['slug'])
        )


with open('api_yamdb/static/data/review.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute(
            'INSERT INTO reviews_review VALUES(?, ?, ?, ?, ?, ?);',
            (row['id'], row['pub_date'], row['text'], row['score'], row['author'], row['title_id'])
        )


with open('api_yamdb/static/data/titles.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute(
            'INSERT INTO reviews_title VALUES(?, ?, ?, ?, ?);',
            (row['id'], row['name'], row['year'], 'Какое-то описание', row['category'])
        )

# with open('api_yamdb/static/data/users.csv', newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         cur.execute(
#             'INSERT INTO auth_user VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
#             (row['id'], 'password', '', False, row['username'], row['last_name'], row['email'], False, True, '', row['first_name'])
#         )

con.commit()
con.close()
