from rest_framework.permissions import BasePermission


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