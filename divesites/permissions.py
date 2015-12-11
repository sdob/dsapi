from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Return True if the request is a safe method or the requesting
    user is the object's owner; otherwise false."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.owner

class IsDiverOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.diver
