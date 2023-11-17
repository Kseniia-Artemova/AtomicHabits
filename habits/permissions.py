from rest_framework.permissions import BasePermission


class OnlyOwnerOrSuperuser(BasePermission):
    """Доступ только для владельца объекта или суперюзера"""

    def has_object_permission(self, request, view, obj):
        return bool(obj.user == request.user or request.user.is_superuser)