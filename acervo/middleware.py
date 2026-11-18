from functools import wraps

from django.shortcuts import redirect

from .models import OrganizacaoUsuario


class OrganizacaoAtualMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organizacao = None
        request.organizacoes = []

        if request.user.is_authenticated:
            request.organizacoes = list(
                OrganizacaoUsuario.objects.filter(usuario=request.user)
                .select_related("organizacao")
                .order_by("organizacao__nome")
            )
            organizacao_id = request.session.get("organizacao_id")
            vinculo_ativo = next(
                (vinculo for vinculo in request.organizacoes if str(vinculo.organizacao_id) == str(organizacao_id)),
                None,
            )

            if vinculo_ativo is None and request.organizacoes:
                vinculo_ativo = request.organizacoes[0]
                request.session["organizacao_id"] = vinculo_ativo.organizacao_id

            if vinculo_ativo:
                request.organizacao = vinculo_ativo.organizacao
                request.vinculo_organizacao = vinculo_ativo
            else:
                request.session.pop("organizacao_id", None)
                request.vinculo_organizacao = None

        return self.get_response(request)


def organizacao_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if request.organizacao is None:
            return redirect("organizacoes")
        return view_func(request, *args, **kwargs)

    return wrapped
