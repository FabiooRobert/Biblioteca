from rest_framework.permissions import BasePermission


class TemPerfil(BasePermission):
    message = "Usuário sem perfil e organização vinculados."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, "perfil"))