from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешает редактирование только владельцу привычки"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """Проверка, что пользователь является владельцем"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user