from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class IsAdmin(BasePermission):
    """Разрешение для доступа только администраторам и суперпользователям."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешение для доступа только администраторам и суперпользователям,
    но разрешает чтение (GET, HEAD, OPTIONS) всем.
    """

    def has_permission(self, request, view):
        return (
            request.method in ('GET', 'HEAD', 'OPTIONS') or
            (request.user.is_authenticated and
             (request.user.is_admin or request.user.is_superuser))
        )
        # return (
        #     request.method in SAFE_METHODS or
        #     request.user.is_authenticated and request.user.is_admin
        # )


    # def has_object_permission(self, request, view, obj):

    #     return (
    #         request.method in ('HEAD', 'OPTIONS') or
    #         request.user.is_authenticated and request.user.is_admin
    #     )


class IsAuthorOrAdminOrModerator(BasePermission):
    """
    Разрешение для доступа к объекту автору, администратору,
    модератору или суперпользователю. Чтение разрешено всем.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET', 'HEAD', 'OPTIONS') or
            obj.author == request.user or
            request.user.is_admin or
            request.user.is_moderator or
            request.user.is_superuser
        )


class IsOwnerOrReadOnly(BasePermission):
    """Разрешения: анонимы могут смотреть всё, а CRUD авторизованные юзеры
     и только своё, кому дал право создатель, могут всё."""
    def has_object_permission(self, request, view, obj):

        return (
            request.method in SAFE_METHODS or
            obj.author == request.user or
            request.user.is_admin or
            request.user.is_moderator or
            request.user.is_superuser
        )

    def has_permission(self, request, view):

        return (
            request.method in SAFE_METHODS or
            (request.user and request.user.is_authenticated)
        )
