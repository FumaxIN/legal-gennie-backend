from rest_framework.permissions import BasePermission

class IsSelf(BasePermission):
    """
    Custom permission to allow only the logged-in user to update their own data.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user
