from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Beneficio, Resgate, Auditoria


def _registrar_auditoria(usuario, acao):
    Auditoria.objects.create(usuario=usuario, acao=acao)


# ─────────────────────────────────────────────────────────────────
# Decoradores de permissão
# ─────────────────────────────────────────────────────────────────

def gestor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_gestor:
            messages.error(request, 'Acesso restrito a gestores municipais.')
            return redirect('core:index')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin_ecosmart:
            messages.error(request, 'Acesso restrito ao administrador.')
            return redirect('core:index')
        return view_func(request, *args, **kwargs)
    return wrapper


# ───────────────────────────────────────────────────────────────
# Cidadão — Benefícios e Resgates
# ───────────────────────────────────────────────────────────────


class BeneficiosView(LoginRequiredMixin, View):
    """
    Catálogo de benefícios disponíveis para resgate.
    GET  — lista todos os benefícios activos.
    POST — processa o resgate do benefício seleccionado.
    Convertida de função para Class-Based View para seguir
    o padrão do projeto e facilitar futuras extensões.
    """
    template_name = 'beneficios.html'

    def get(self, request):
        beneficios = Beneficio.objects.filter(ativo=True)
        return render(request, self.template_name, {'beneficios': beneficios})

    def post(self, request):
        beneficio_id = request.POST.get('beneficio_id')
        beneficio = get_object_or_404(Beneficio, pk=beneficio_id, ativo=True)

        try:
            # Toda a lógica de negócio (verificação de saldo, dedução de pontos,
            # geração de voucher e transação atômica) está encapsulada no modelo.
            resgate = beneficio.resgatar_para_usuario(request.user)
            # Recarrega o utilizador para refletir o novo saldo na sessão
            request.user.refresh_from_db(fields=['saldo_pontos'])
            messages.success(
                request,
                f"Benefício '{beneficio.nome}' resgatado com sucesso! "
                f"Código: {resgate.codigo_voucher}"
            )
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('recompensas:meus_resgates')


class MeusResgatesView(LoginRequiredMixin, ListView):
    """
    Histórico de resgates do utilizador autenticado.
    Substituiu a função meus_resgates() para seguir o padrão
    de Class-Based Views do Django e eliminar lógica manual.
    """
    model = Resgate
    template_name = 'meus_resgates.html'
    context_object_name = 'resgates'
    ordering = ['-data_resgate']

    def get_queryset(self):
        return (
            Resgate.objects
            .filter(usuario=self.request.user)
            .select_related('beneficio')
            .order_by('-data_resgate')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_pontos_gastos'] = sum(
            r.pontos_utilizados for r in ctx['resgates']
        )
        return ctx


# ─────────────────────────────────────────────────────────────────
# Admin — Gestão de Benefícios
# NOTA: A gestão de Benefícios foi migrada para o Django Admin.
# Acesse /django-admin/recompensas/beneficio/ para criar, editar,
# ativar/desativar e excluir benefícios sem código manual.
# ─────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────
# Admin — Gestão de Utilizadores e Auditoria
# ─────────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_usuarios(request):
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    usuarios = Usuario.objects.order_by('nome')
    return render(request, 'usuarios_admin.html', {'usuarios': usuarios})


@login_required
@admin_required
def alterar_papel(request, user_id):
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=user_id)
        novo_papel = request.POST['papel']
        usuario.papel = novo_papel
        usuario.save(update_fields=['papel'])
        _registrar_auditoria(
            request.user,
            f'Alterou papel do usuario {usuario.email} para {novo_papel}'
        )
        messages.success(request, 'Papel atualizado!')
    return redirect('recompensas:admin_usuarios')


@login_required
@admin_required
def alterar_status_usuario(request, user_id):
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=user_id)
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=['is_active'])
        acao = 'Desativou' if not usuario.is_active else 'Ativou'
        _registrar_auditoria(request.user, f'{acao} o usuario {usuario.email}')
        messages.success(request, 'Status atualizado!')
    return redirect('recompensas:admin_usuarios')


@login_required
@admin_required
def admin_auditoria(request):
    registros = Auditoria.objects.select_related('usuario').order_by('-data')
    return render(request, 'auditoria.html', {'registros': registros})
