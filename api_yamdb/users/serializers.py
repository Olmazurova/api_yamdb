import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
# from rest_framework_simplejwt.serializers import (
#     api_settings, TokenObtainSerializer, update_last_login
# )
# from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации пользователя.
    Проверяет уникальность email и username, а также запрещает username 'me'.
    """
    email = serializers.EmailField(max_length=254)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя "me" недопустимо в качестве username.'
            )
        return value

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')

        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        if user_by_email and user_by_username:
            if user_by_email != user_by_username:
                raise serializers.ValidationError(
                    'Пользователь с таким username и email уже существует, '
                    'но принадлежат разным аккаунтам.'
                )
        elif user_by_email:
            raise serializers.ValidationError('Этот email уже используется.')
        elif user_by_username:
            raise serializers.ValidationError('Этот username уже используется.')

        return attrs


# class TokenSerializer(TokenObtainSerializer):
#     """
#     Сериализатор для получения токена
#     с использованием username и confirmation_code.
#     Наследован от сериализатора из rest_framework_simplejwt.
#     """
#
#     @classmethod
#     def get_token(cls, user):
#         return RefreshToken.for_user(user)
#
#     def validate(self, attrs):
#         data = super().validate(attrs)
#
#         confirmation_code = data.get('request').get('confirmation_code')
#         if confirmation_code != self.user.confirmation_code:
#             raise serializers.ValidationError(
#                 'Неверный код подтверждения!'
#             )
#
#         refresh = self.get_token(self.user)
#
#         data['token'] = str(refresh)
#
#         if api_settings.UPDATE_LAST_LOGIN:
#             update_last_login(None, self.user)
#
#         return data




class TokenObtainSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена с использованием username и confirmation_code.
    """
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для полной информации о пользователе.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя,
    с полями username, email и ролью в режиме только для чтения.
    """
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('username', 'email', 'role')

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError("Email слишком длинный")
        return value

    def validate_username(self, value):
        if len(value) > 150:
            raise serializers.ValidationError("Username слишком длинный")
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError("Недопустимые символы в username")
        return value
