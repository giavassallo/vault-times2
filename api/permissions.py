from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsRole(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == self.required_role


class IsJournalist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'journalist'


class IsEditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'editor'


class IsReader(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'reader'


class IsJournalistOrEditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('journalist', 'editor')


class CanModifyArticle(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'editor':
            return True
        if request.user.role == 'journalist' and obj.author == request.user:
            return True
        return False


class CanModifyNewsletter(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'editor':
            return True
        if request.user.role == 'journalist' and obj.author == request.user:
            return True
        return False