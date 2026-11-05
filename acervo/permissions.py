from functools import wraps
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


def usuario_eh_administrador(user):
    perfil = getattr(user, "perfil", None)
    return perfil is not None and perfil.papel == "admin"


def administrador_requerido(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not usuario_eh_administrador(request.user):
            raise PermissionDenied("Apenas administradores podem alterar livros.")
        return view_func(request, *args, **kwargs)

    return wrapped


class TemPerfil(BasePermission):
    message = "Usuário sem perfil e organização vinculados."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, "perfil"))


class AdministradorPodeEscrever(BasePermission):
    message = "Apenas administradores podem alterar livros."

    def has_permission(self, request, view):
        return request.method in self.safe_methods or usuario_eh_administrador(request.user)

    safe_methods = ("GET", "HEAD", "OPTIONS")