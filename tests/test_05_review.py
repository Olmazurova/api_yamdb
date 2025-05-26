from http import HTTPStatus

import pytest
from django.db.utils import IntegrityError

from tests.utils import (
    check_fields, check_pagination, create_reviews, create_single_review,
    create_titles
)


@pytest.mark.django_db(transaction=True)
class Test05ReviewAPI:

    TITLE_DETAIL_URL_TEMPLATE = '/api/v1/titles/{title_id}/'
    REVIEWS_URL_TEMPLATE = '/api/v1/titles/{title_id}/reviews/'
    REVIEW_DETAIL_URL_TEMPLATE = (
        '/api/v1/titles/{title_id}/reviews/{review_id}/'
    )

    def test_01_review_not_auth(self, client, admin_client, admin, user_client,
                                user, moderator_client, moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)
        new_data = {'text': 'new_text', 'score': 7}

        response = client.get(
            self.REVIEWS_URL_TEMPLATE.format(title_id=titles[0]['id'])
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.REVIEWS_URL_TEMPLATE}` не найден, проверьте '
            'настройки в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращает ответ со статусом 200.'
        )

        response = client.post(
            self.REVIEWS_URL_TEMPLATE.format(title_id=titles[0]['id']),
            data=new_data
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращает ответ со статусом 401.'
        )

        response = client.patch(
            self.REVIEW_DETAIL_URL_TEMPLATE.format(
                title_id=titles[0]['id'], review_id=reviews[1]['id']
            ),
            data=new_data
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что PATCH-запрос неавторизованного пользователя к '
            f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` возвращает ответ со '
            'статусом 401.'
        )

        response = client.delete(
            self.REVIEW_DETAIL_URL_TEMPLATE.format(
                title_id=titles[0]['id'], review_id=reviews[1]['id']
            )
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что DELETE-запрос неавторизованного пользователя к '
            f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` возвращает ответ со '
            'статусом 401.'
        )

    def test_02_review_post(self, admin_client, user_client,
                            moderator_client, admin):
        titles, _, _ = create_titles(admin_client)
        title_0_reviews_count = 0
        first_title_reviews_url = self.REVIEWS_URL_TEMPLATE.format(
            title_id=titles[0]['id']
        )
        second_title_reviews_url = self.REVIEWS_URL_TEMPLATE.format(
            title_id=titles[1]['id']
        )

        data = {}
        response = user_client.post(first_title_reviews_url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если POST-запрос авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` содержит некорректные данные - '
            'должен вернуться ответ со статусом 400.'
        )

        post_data = {
            'text': 'Неочень',
            'score': 5
        }
        create_single_review(
            admin_client,
            titles[0]['id'],
            post_data['text'],
            post_data['score']
        )
        title_0_reviews_count += 1

        data = {
            'text': 'Шляпа',
            'score': 1
        }
        response = admin_client.post(first_title_reviews_url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что при попытке пользователя создать второй отзыв на '
            'одно и то же произведение POST-запрос к '
            f'`{self.REVIEWS_URL_TEMPLATE}` вернёт ответ со статусом 400.'
        )

        try:
            from reviews.models import Review, Title
        except Exception as e:
            assert False, (
                'Не удалось импортировать модели из приложения reviews. '
                f'Ошибка: {e}'
            )
        title = Title.objects.get(pk=titles[0]['id'])
        review = None
        try:
            review = Review.objects.create(
                text='Текст второго отзыва',
                score='5',
                author=admin,
                title=title
            )
        except IntegrityError:
            pass

        assert review is None, (
            'Проверьте, что на уровне модели запрещено повторное '
            'создание отзыва на произведение от имени пользователя, отзыв '
            'которого уже существует.'
        )

        response = admin_client.put(first_title_reviews_url, data=data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что PUT-запрос авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращает ответ со статусом 405.'
        )

        create_single_review(user_client, titles[0]['id'], 'Ну такое', 3)
        title_0_reviews_count += 1
        response = create_single_review(
            moderator_client, titles[0]['id'], 'Ниже среднего', 4
        )
        title_0_reviews_count += 1

        assert type(response.json().get('id')) == int, (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращает данные созданного '
            'объекта. Сейчас поля `id` нет в ответе или его значение не '
            'является целым числом.'
        )

        data = {'text': 'На один раз', 'score': 4}
        response = user_client.post(
            self.REVIEWS_URL_TEMPLATE.format(title_id='999'), data=data
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` для несуществующего произведения '
            'возвращает ответ со статусом 404.'
        )

        data = {'text': 'Супер!', 'score': 11}
        response = user_client.post(second_title_reviews_url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если в POST-запросе авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` передана оценка выше 10 баллов - '
            'должен вернуться ответ со статусом 400.'
        )

        data = {'text': 'Ужас!', 'score': 0}
        response = user_client.post(first_title_reviews_url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если в POST-запросе авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` передана оценка ниже 1 балла - '
            'должен вернуться ответ со статусом 400.'
        )

        response = user_client.get(first_title_reviews_url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращает ответ со статусом 200.'
        )
        data = response.json()
        check_pagination(first_title_reviews_url, data, title_0_reviews_count)

        expected_data = {
            'text': post_data['text'],
            'score': post_data['score'],
            'author': admin.username
        }
        review = None
        for value in data['results']:
            if value.get('text') == post_data['text']:
                review = value
        assert review, (
            'Проверьте, что при GET-запросе к '
            f'`{self.REVIEWS_URL_TEMPLATE}` возвращается вся информация '
            'об отзывах. В ответе на запрос не обнаружен текст отзыва.'
        )
        check_fields(
            'review', self.REVIEWS_URL_TEMPLATE, review, expected_data
        )

        response = admin_client.get(
            self.TITLE_DETAIL_URL_TEMPLATE.format(title_id=titles[0]['id'])
        )
        data = response.json()
        assert data.get('rating') == 4, (
            'Проверьте, что произведениям присваивается рейтинг, '
            'равный средной оценке оставленных отзывов. '
            'Поле `rating` не найдено в ответе на GET-запрос к '
            f'`{self.TITLE_DETAIL_URL_TEMPLATE}` или содержит некорректное '
            'значение.'
        )

    def test_03_review_detail_get(self, client, admin_client, admin, user,
                                  user_client, moderator, moderator_client):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)

        response = client.get(
            self.REVIEW_DETAIL_URL_TEMPLATE.format(
                title_id=titles[0]['id'], review_id=reviews[0]['id']
            )
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.REVIEW_DETAIL_URL_TEMPLATE}` не найден. '
            'Проверьте настройки в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` возвращает ответ со '
            'статусом 200.'
        )
        review = response.json()

        expected_data = {
            key: value for key, value in reviews[0].items() if key != 'id'
        }
        check_fields(
            'review', self.REVIEW_DETAIL_URL_TEMPLATE, review, expected_data,
            detail=True
        )

    def test_04_review_detail_user(self, admin_client, admin, user,
                                   user_client, moderator, moderator_client):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)
        new_data = {
            'text': 'Top score',
            'score': 10
        }
        user_review_url = self.REVIEW_DETAIL_URL_TEMPLATE.format(
            title_id=titles[0]['id'], review_id=reviews[1]['id']
        )

        response = user_client.patch(user_review_url, data=new_data)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос пользователя с ролью `user` к его '
            f'собственному отзыву через `{self.REVIEW_DETAIL_URL_TEMPLATE}` '
            'возвращает ответ со статусом 200.'
        )
        data = response.json()
        assert data.get('text') == new_data['text'], (
            'Проверьте, что ответ на успешный PATCH-запрос к '
            f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` содержит обновлённые данные '
            'отзыва. Сейчас поле `text` не найдено или содержит некорректные '
            'данные.'
        )

        response = user_client.get(user_review_url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос авторизованного пользователя к '
            f'{self.REVIEW_DETAIL_URL_TEMPLATE} возвращает ответ со статусом '
            '200.'
        )
        data = response.json()
        assert_msg_template = (
            'Проверьте, что если в PATCH-запросе авторизованного пользователя '
            'к его собственному отзыву через `{url_template}` содержится поле '
            '`{field}` - то это поле отзыва будет изменено.'
        )
        assert data.get('text') == new_data['text'], (
            assert_msg_template.format(
                url_template=self.REVIEW_DETAIL_URL_TEMPLATE, field='text'
            )
        )
        assert data.get('score') == new_data['score'], (
            assert_msg_template.format(
                url_template=self.REVIEW_DETAIL_URL_TEMPLATE, field='score'
            )
        )

        moderator_review_url = self.REVIEW_DETAIL_URL_TEMPLATE.format(
            title_id=titles[0]['id'], review_id=reviews[2]['id']
        )
        response = user_client.patch(moderator_review_url, data=new_data)
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что PATCH-запрос пользователя с ролью `user` к '
            f'чужому отзыву через `{self.REVIEW_DETAIL_URL_TEMPLATE}` '
            'возвращает ответ со статусом 403.'
        )

        response = user_client.delete(user_review_url)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к его '
            f'собственному отзыву через `{self.REVIEW_DETAIL_URL_TEMPLATE}` '
            'возвращает ответ со статусом 204.'
        )
        response = user_client.get(
            self.REVIEWS_URL_TEMPLATE.format(title_id=titles[0]['id'])
        )
        test_data = response.json()['results']
        assert len(test_data) == len(reviews) - 1, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к его '
            f'собственному отзыву через `{self.REVIEW_DETAIL_URL_TEMPLATE}` '
            'удаляет отзыв.'
        )

        response = user_client.delete(moderator_review_url)
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что DELETE-запрос пользователя с ролью `user` к '
            f'чужому отзыву через `{self.REVIEW_DETAIL_URL_TEMPLATE}` '
            'возвращает ответ со статусом 403.'
        )

    def test_05_reviews_detail_moderator_and_admin(self, admin_client, admin,
                                                   user_client, user,
                                                   moderator_client,
                                                   moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)
        new_data = {
            'text': 'Top score',
            'score': 10
        }

        for idx, (client, role) in enumerate((
                (moderator_client, 'модератора'),
                (admin_client, 'администратора')
        ), 1):
            response = client.patch(
                self.REVIEW_DETAIL_URL_TEMPLATE.format(
                    title_id=titles[0]['id'], review_id=reviews[idx]['id']
                ),
                data=new_data
            )
            assert response.status_code == HTTPStatus.OK, (
                f'Проверьте, что PATCH-запросе {role} к  чужому отзыву через '
                f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` возвращает ответ со '
                'статусом 200.'
            )

            response = client.delete(
                self.REVIEW_DETAIL_URL_TEMPLATE.format(
                    title_id=titles[0]['id'], review_id=reviews[idx]['id']
                )
            )
            assert response.status_code == HTTPStatus.NO_CONTENT, (
                f'Проверьте, что DELETE-запрос {role} к чужому отзыву через '
                f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` возвращает ответ со '
                'статусом 204.'
            )
            response = client.get(
                self.REVIEWS_URL_TEMPLATE.format(title_id=titles[0]['id'])
            )
            test_data = response.json()['results']
            assert len(test_data) == len(reviews) - idx, (
                f'Проверьте, что DELETE-запрос {role} к чужому отзыву через '
                f'`{self.REVIEW_DETAIL_URL_TEMPLATE}` удаляет отзыв.'
            )

    def test_06_reviews_detail_put_not_allowed(
            self, admin_client, admin, user_client, user, moderator_client,
            moderator):
        author_map = {
            admin: admin_client,
            user: user_client,
            moderator: moderator_client
        }
        reviews, titles = create_reviews(admin_client, author_map)
        review = reviews[0]
        review['text'] = 'Новвый текст отзыва.'
        response = admin_client.put(
            self.REVIEW_DETAIL_URL_TEMPLATE.format(
                title_id=titles[0]['id'], review_id=reviews[0]['id']
            ),
            data=review
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            f'Проверьте, что PUT-запрос к `{self.REVIEW_DETAIL_URL_TEMPLATE} '
            'не предусмотрен и возвращает статус 405.'
        )
