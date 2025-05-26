from http import HTTPStatus

import pytest

from tests.utils import (
    check_name_and_slug_patterns, check_pagination, check_permissions,
    create_genre
)


@pytest.mark.django_db(transaction=True)
class Test03GenreAPI:

    GENRES_URL = '/api/v1/genres/'
    GENRES_SLUG_TEMPLATE_URL = '/api/v1/genres/{slug}/'

    def test_01_genre_not_auth(self, client):
        response = client.get(self.GENRES_URL)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.GENRES_URL}` не найден. Проверьте настройки в '
            '*urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к  '
            f'`{self.GENRES_URL}` возвращает ответ со статусом 200.'
        )

    def test_02_genre(self, admin_client, client):
        genres_count = 0

        data = {}
        response = admin_client.post(self.GENRES_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос администратора к `{self.GENRES_URL}` '
            'содержит некорректные данные - должен вернуться ответ со '
            'статусом 400.'
        )

        data = {'name': 'Ужасы', 'slug': 'horror'}
        response = admin_client.post(self.GENRES_URL, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора к `{self.GENRES_URL}` содержит '
            'корректные данные - должен вернуться ответ со статусом 201.'
        )
        genres_count += 1

        data = {'name': 'Триллер', 'slug': 'horror'}
        response = admin_client.post(self.GENRES_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если в POST-запросе администратора, отправленном к '
            f'`{self.GENRES_URL}`, передан уже существующий `slug` - должен '
            'вернуться ответ со статусом 400.'
        )

        post_data = {'name': 'Комедия', 'slug': 'comedy'}
        response = admin_client.post(self.GENRES_URL, data=post_data)
        assert response.status_code == HTTPStatus.CREATED, (
            'Если POST-запрос администратора, отправленный к '
            f'`{self.GENRES_URL}`, содержит корректные данные - должен '
            'вернуться ответ со статусом 201.'
        )
        genres_count += 1

        response = client.get(self.GENRES_URL)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{self.GENRES_URL}` возвращает ответ со статусом 200.'
        )
        data = response.json()
        check_pagination(self.GENRES_URL, data, genres_count, post_data)

        response = admin_client.get(
            f'{self.GENRES_URL}?search={post_data["name"]}'
        )
        data = response.json()
        assert len(data['results']) == 1, (
            f'Проверьте, что GET-запрос к `{self.GENRES_URL}?search=<name>` '
            'возвращает данные только тех жанров, поле `name` которых '
            'удовлетворяет условию поиска.'
        )

    @pytest.mark.parametrize('data,massage', check_name_and_slug_patterns)
    def test_03_category_fields_validation(self, data, massage, admin_client):
        response = admin_client.post(self.GENRES_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            massage[0].format(url=self.GENRES_URL)
        )

    def test_04_genres_delete(self, admin_client):
        genres = create_genre(admin_client)
        response = admin_client.delete(
            self.GENRES_SLUG_TEMPLATE_URL.format(slug=genres[0]['slug'])
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос администратора к '
            f'`{self.GENRES_SLUG_TEMPLATE_URL}` возвращает ответ со  статусом '
            '204.'
        )
        response = admin_client.get(self.GENRES_URL)
        test_data = response.json()['results']
        assert len(test_data) == len(genres) - 1, (
            'Проверьте, что DELETE-запрос администратора к '
            f'`{self.GENRES_SLUG_TEMPLATE_URL}` удаляет жанр из БД.'
        )
        response = admin_client.get(
            self.GENRES_SLUG_TEMPLATE_URL.format(slug=genres[0]['slug'])
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что GET-запрос администратора к '
            f'`{self.GENRES_SLUG_TEMPLATE_URL}` возвращает ответ со статусом '
            '405.'
        )
        response = admin_client.patch(
            self.GENRES_SLUG_TEMPLATE_URL.format(slug=genres[0]['slug'])
        )
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что PATCH-запрос администратора к '
            f'`{self.GENRES_SLUG_TEMPLATE_URL}` возвращает ответ со статусом '
            '405.'
        )

    def test_05_genres_check_permission(self, client,
                                        user_client,
                                        moderator_client,
                                        admin_client):
        genres = create_genre(admin_client)
        data = {
            'name': 'Боевик',
            'slug': 'action'
        }
        check_permissions(client, self.GENRES_URL, data,
                          'неавторизованного пользователя',
                          genres, HTTPStatus.UNAUTHORIZED)
        check_permissions(user_client, self.GENRES_URL, data,
                          'пользователя с ролью `user`', genres,
                          HTTPStatus.FORBIDDEN)
        check_permissions(moderator_client, self.GENRES_URL, data,
                          'модератора', genres, HTTPStatus.FORBIDDEN)
