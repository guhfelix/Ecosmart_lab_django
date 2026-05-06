from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from coleta.models import PontoColeta, Descarte
from recompensas.models import Beneficio


def index(request):
    return render(request, 'index.html')


@login_required
def dashboard(request):
    descartes = (
        Descarte.objects
        .filter(usuario=request.user)
        .select_related('ponto')
        .order_by('-data_hora')
    )
    total_descartes = descartes.count()
    total_peso = sum(d.peso_kg for d in descartes) if descartes else 0
    ultimos_descartes = list(descartes[:5])

    return render(request, 'dashboard.html', {
        'total_descartes': total_descartes,
        'total_peso': total_peso,
        'ultimos_descartes': ultimos_descartes,
    })


def api_pontos(request):
    pontos = list(PontoColeta.objects.all().values(
        'id', 'nome', 'endereco', 'tipos_aceitos', 'horario_funcionamento', 'latitude', 'longitude'
    ))
    return JsonResponse(pontos, safe=False)


def api_beneficios(request):
    beneficios = list(Beneficio.objects.filter(ativo=True).values(
        'id', 'nome', 'descricao', 'custo_pontos', 'tipo'
    ))
    return JsonResponse(beneficios, safe=False)


def api_estatisticas(request):
    from django.db.models import Count, Sum

    total_descartes = Descarte.objects.count()
    total_peso = Descarte.objects.aggregate(total=Sum('peso_kg'))['total'] or 0

    peso_por_tipo = list(
        Descarte.objects
        .values('tipo_residuo')
        .annotate(total_peso=Sum('peso_kg'), total_descartes=Count('id'))
        .order_by('-total_peso')
    )

    return JsonResponse({
        'total_descartes': total_descartes,
        'total_peso_kg': total_peso,
        'por_tipo': peso_por_tipo,
    })
