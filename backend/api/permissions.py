from rest_framework import permissions


class BaseOwnerPermission(permissions.BasePermission):
    """Базовое пользовательское разрешение."""

    def has_permission(self, request, view):
        """Определяет право доступа пользователя к представлению."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )


class OwnerOnlyPermission(BaseOwnerPermission):
    """
    Пользовательское разрешение.

    Разрешает чтение или изменение/удаление объекта только автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        """Определяет право доступа пользователя к объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class OwnerOrReadOnlyPermission(BaseOwnerPermission):
    """
    Пользовательское разрешение.

    Разрешает чтение профилей пользователей.
    """

    def has_object_permission(self, request, view, obj):
        """Определяет право доступа пользователя к объекту."""
        return request.method in permissions.SAFE_METHODS
