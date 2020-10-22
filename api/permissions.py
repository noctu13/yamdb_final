from rest_framework.permissions import SAFE_METHODS, BasePermission

from api.models import Role


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAdminClient(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.ADMIN
        )


class IsModeratorClient(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.MODERATOR
        )


class IsAuthorOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and bool(
                request.user == obj.author
                or request.user.role == Role.MODERATOR
                or request.user.role == Role.ADMIN
            )
        )
