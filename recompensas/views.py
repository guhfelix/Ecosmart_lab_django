import random
import string

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404

from .models import Beneficio, Resgate, Auditoria


def _registrar_auditoria(usuario, acao):
    Auditoria.objects.create(usuario=usuario, acao=acao)


@login_required
def beneficios(request):
    lista_beneficios = Beneficio.objects.filter(ativo=True)

    if request.method == 'POST':
        beneficio_id = request.POST.get('beneficio_id')
        beneficio = get_object_or_404(Beneficio, pk=beneficio_id, ativo=True)

        if request.user.saldo_pontos < beneficio.custo_pontos:
            messages.error(request, 'Saldo de pontos insuficiente para este beneficio.')
            return redirect('recompensas:beneficios')

        codigo = 'ECO-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        with transaction.atomic():
            request.user.saldo_pontos -= beneficio.custo_pontos
            request.user.save(update_fields=['saldo_pontos'])

            Resgate.objects.create(
                usuario=request.user,
                beneficio=beneficio,
                pontos_utilizados=beneficio.custo_pontos,
                codigo_voucher=codigo,
                status='ATIVO',
            )

        messages.success(
            request,
            f"Beneficio '{beneficio.nome}' resgatado com sucesso! Codigo: {codigo}"
        )
        return redirect('recompensas:meus_resgates')

    return render(request, 'beneficios.html', {'beneficios': lista_beneficios})


@login_required
def meus_resgates(request):
    resgates = (
        Resgate.objects
        .filter(usuario=request.user)
        .select_related('beneficio')
        .order_by('-data_resgate')
    )

    total_pontos_gastos = sum(r.pontos_utilizados for r in resgates)

    return render(request, 'meus_resgates.html', {
        'resgates': resgates,
        'total_pontos_gastos': total_pontos_gastos,
    })


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


@login_required
@gestor_required
def admin_beneficios(request):
    lista = Beneficio.objects.order_by('nome')
    return render(request, 'beneficios_admin.html', {'beneficios': lista})


@login_required
@gestor_required
def novo_beneficio(request):
    if request.method == 'POST':
        Beneficio.objects.create(
            nome=request.POST['nome'],
            descricao=request.POST.get('descricao', ''),
            custo_pontos=int(request.POST['custo_pontos']),
            tipo=request.POST.get('tipo', ''),
            ativo=True,
        )
        messages.success(request, 'Beneficio cadastrado com sucesso.')
        return redirect('recompensas:admin_beneficios')
    return render(request, 'beneficio_form.html', {'acao': 'Novo', 'beneficio': None})


@login_required
@gestor_required
def editar_beneficio(request, pk):
    beneficio = get_object_or_404(Beneficio, pk=pk)
    if request.method == 'POST':
        beneficio.nome = request.POST['nome']
        beneficio.descricao = request.POST.get('descricao', '')
        beneficio.custo_pontos = int(request.POST['custo_pontos'])
        beneficio.tipo = request.POST.get('tipo', '')
        beneficio.save()
        messages.success(request, 'Beneficio atualizado com sucesso.')
        return redirect('recompensas:admin_beneficios')
    return render(request, 'beneficio_form.html', {'acao': 'Editar', 'beneficio': beneficio})


@login_required
@gestor_required
def toggle_beneficio(request, pk):
    if request.method == 'POST':
        beneficio = get_object_or_404(Beneficio, pk=pk)
        beneficio.ativo = not beneficio.ativo
        beneficio.save()
        estado = 'ativado' if beneficio.ativo else 'desativado'
        messages.success(request, f"Beneficio '{beneficio.nome}' {estado}.")
    return redirect('recompensas:admin_beneficios')


@login_required
@gestor_required
def excluir_beneficio(request, pk):
    if request.method == 'POST':
        beneficio = get_object_or_404(Beneficio, pk=pk)
        beneficio.delete()
        messages.info(request, 'Beneficio excluido com sucesso.')
    return redirect('recompensas:admin_beneficios')


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
