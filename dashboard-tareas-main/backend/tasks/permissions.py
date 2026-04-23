from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "rol", "") == "ADMIN")


class IsAdminOrOwner(BasePermission):
    """
    Admin: puede todo.
    Ejecutor: solo puede ver/modificar tareas donde asignada_a == request.user.
    """
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "rol", "") == "ADMIN":
            return True
        return obj.asignada_a_id == request.user.id
