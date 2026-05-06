import csv
import io
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import PontoColeta, Descarte


def gestor_required(view_func):
    """Decorator que exige papel GESTOR ou ADMIN."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_gestor:
            messages.error(request, 'Acesso restrito a gestores municipais.')
            return redirect('core:index')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@gestor_required
def relatorios_gestor(request):
    ponto_filtro = request.GET.get('ponto_id', '').strip()
    tipo_filtro = request.GET.get('tipo', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()
    pagina = request.GET.get('pagina', 1)

    qs = Descarte.objects.select_related('usuario', 'ponto')

    if ponto_filtro:
        qs = qs.filter(ponto_id=ponto_filtro)
    if tipo_filtro:
        qs = qs.filter(tipo_residuo__icontains=tipo_filtro)
    if data_inicio:
        try:
            qs = qs.filter(data_hora__gte=datetime.strptime(data_inicio, '%Y-%m-%d'))
        except ValueError:
            pass
    if data_fim:
        try:
            qs = qs.filter(data_hora__lt=datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1))
        except ValueError:
            pass

    todos = list(qs)
    total_descartes = len(todos)
    total_peso = sum(d.peso_kg for d in todos) if todos else 0
    total_pontos = sum(d.pontos_gerados for d in todos) if todos else 0

    # Ranking por ponto
    estatistica_por_ponto = {}
    for d in todos:
        pid = d.ponto_id
        if pid not in estatistica_por_ponto:
            estatistica_por_ponto[pid] = {
                'nome': d.ponto.nome if d.ponto else f'Ponto #{pid}',
                'peso_total': 0.0,
                'pontos_totais': 0,
                'qtd_descartes': 0,
            }
        estatistica_por_ponto[pid]['peso_total'] += d.peso_kg
        estatistica_por_ponto[pid]['pontos_totais'] += d.pontos_gerados
        estatistica_por_ponto[pid]['qtd_descartes'] += 1

    ranking_pontos = sorted(
        estatistica_por_ponto.values(),
        key=lambda x: x['qtd_descartes'],
        reverse=True
    )

    paginator = Paginator(qs.order_by('-data_hora'), 15)
    paginacao = paginator.get_page(pagina)

    todos_pontos = PontoColeta.objects.order_by('nome')
    tipos_unicos = list(
        Descarte.objects.values_list('tipo_residuo', flat=True).distinct()
    )
    tipos_unicos = [t for t in tipos_unicos if t]

    return render(request, 'relatorios_gestor.html', {
        'total_descartes': total_descartes,
        'total_peso': total_peso,
        'total_pontos': total_pontos,
        'ranking_pontos': ranking_pontos,
        'paginacao': paginacao,
        'todos_pontos': todos_pontos,
        'tipos_unicos': tipos_unicos,
        'ponto_filtro': ponto_filtro,
        'tipo_filtro': tipo_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    })


@login_required
@gestor_required
def exportar_relatorios_csv(request):
    descartes = Descarte.objects.order_by('-data_hora').select_related('usuario', 'ponto')

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow([
        'Data/Hora', 'Usuario (ID)', 'Usuario (Nome)', 'Usuario (E-mail)',
        'Papel do Usuario', 'Ponto de Coleta', 'Tipo de Residuo', 'Peso (kg)', 'Pontos Gerados'
    ])

    for d in descartes:
        writer.writerow([
            d.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
            d.usuario_id,
            d.usuario.nome if d.usuario else '',
            d.usuario.email if d.usuario else '',
            d.usuario.papel if d.usuario else '',
            d.ponto.nome if d.ponto else f'Ponto #{d.ponto_id}',
            d.tipo_residuo,
            f'{d.peso_kg:.2f}',
            d.pontos_gerados,
        ])

    response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=relatorio_gestor_detalhado_ecosmart.csv'
    return response


@login_required
@gestor_required
def exportar_resumo_pontos_csv(request):
    descartes = Descarte.objects.select_related('ponto')
    estatistica_por_ponto = {}

    for d in descartes:
        pid = d.ponto_id
        if pid not in estatistica_por_ponto:
            estatistica_por_ponto[pid] = {
                'nome': d.ponto.nome if d.ponto else f'Ponto #{pid}',
                'peso_total': 0.0,
                'pontos_totais': 0,
                'qtd_descartes': 0,
            }
        estatistica_por_ponto[pid]['peso_total'] += d.peso_kg
        estatistica_por_ponto[pid]['pontos_totais'] += d.pontos_gerados
        estatistica_por_ponto[pid]['qtd_descartes'] += 1

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Ponto de Coleta', 'Quantidade de Descartes', 'Peso Total (kg)', 'Pontos Totais'])

    for dados in estatistica_por_ponto.values():
        writer.writerow([
            dados['nome'],
            dados['qtd_descartes'],
            f"{dados['peso_total']:.2f}",
            dados['pontos_totais'],
        ])

    response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=relatorio_gestor_resumo_pontos_ecosmart.csv'
    return response
