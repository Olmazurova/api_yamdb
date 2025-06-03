from rest_framework.permissions import SAFE_METHODS, BasePermission


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
            request.method in SAFE_METHODS or
            (request.user.is_authenticated and
             (request.user.is_admin or request.user.is_superuser))
        )


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешения: анонимы могут смотреть всё, а CRUD авторизованные юзеры
    и только своё, кому дал право создатель, могут всё.
    """

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
