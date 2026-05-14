from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import render

from coleta.models import PontoColeta, Descarte
from recompensas.models import Beneficio


def index(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    """
    Dashboard do utilizador autenticado.
    Usa aggregate() para calcular totais directamente na base de dados
    (mais eficiente do que carregar todos os registos para Python).
    """
    qs = Descarte.objects.filter(usuario=request.user)

    agregados = qs.aggregate(
        total_descartes=Count('id'),
        total_peso=Sum('peso_kg'),
        total_pontos_gerados=Sum('pontos_gerados'),
    )

    ultimos_descartes = (
        qs.select_related('ponto')
        .order_by('-data_hora')[:5]
    )

    return render(request, 'dashboard.html', {
        'total_descartes': agregados['total_descartes'] or 0,
        'total_peso': agregados['total_peso'] or 0,
        'total_pontos_gerados': agregados['total_pontos_gerados'] or 0,
        'ultimos_descartes': ultimos_descartes,
    })


# ─────────────────────────────────────────────────────────────────
# API REST v1
# ─────────────────────────────────────────────────────────────────

def api_pontos(request):
    """
    GET /api/v1/pontos/
    Retorna todos os pontos de coleta com coordenadas para uso em mapas.
    """
    pontos = list(PontoColeta.objects.all().values(
        'id', 'nome', 'endereco', 'tipos_aceitos',
        'horario_funcionamento', 'latitude', 'longitude',
    ))
    return JsonResponse(pontos, safe=False)


def api_beneficios(request):
    """
    GET /api/v1/beneficios/
    Retorna benefícios activos disponíveis para resgate.
    """
    beneficios = list(
        Beneficio.objects.filter(ativo=True).values(
            'id', 'nome', 'descricao', 'custo_pontos', 'tipo',
        )
    )
    return JsonResponse(beneficios, safe=False)


def api_estatisticas(request):
    """
    GET /api/v1/estatisticas/
    Retorna estatísticas globais do sistema (descartes, peso, distribuição por tipo).
    """
    total_descartes = Descarte.objects.count()
    total_peso = Descarte.objects.aggregate(total=Sum('peso_kg'))['total'] or 0
    total_pontos = Descarte.objects.aggregate(total=Sum('pontos_gerados'))['total'] or 0

    peso_por_tipo = list(
        Descarte.objects
        .values('tipo_residuo')
        .annotate(
            total_peso=Sum('peso_kg'),
            total_descartes=Count('id'),
        )
        .order_by('-total_peso')
    )

    return JsonResponse({
        'total_descartes': total_descartes,
        'total_peso_kg': float(total_peso),
        'total_pontos_distribuidos': total_pontos,
        'por_tipo': peso_por_tipo,
    })
