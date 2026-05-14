import csv
import io
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy

from .models import PontoColeta, Descarte
from .forms import DescarteForm


class PontosListView(LoginRequiredMixin, ListView):
    model = PontoColeta
    template_name = 'pontos.html'
    context_object_name = 'pontos'

    def get_queryset(self):
        return PontoColeta.objects.filter(ativo=True).order_by('nome')


class RegistrarDescarteView(LoginRequiredMixin, CreateView):
    model = Descarte
    form_class = DescarteForm
    template_name = 'descarte.html'
    success_url = reverse_lazy('coleta:relatorio')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pontos'] = PontoColeta.objects.filter(ativo=True).order_by('nome')
        return ctx

    def form_valid(self, form):
        descarte = form.save(commit=False)
        descarte.usuario_id = self.request.user.id
        descarte.save()

        self.object = descarte

        self.request.user.refresh_from_db(fields=['saldo_pontos'])

        messages.success(
            self.request,
            f'Descarte registrado! Você ganhou {descarte.pontos_gerados} pontos. '
            f'Saldo atual: {self.request.user.saldo_pontos} pontos.'
        )

        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(
            self.request,
            f'Erro ao registrar descarte: {form.errors}'
        )
        return super().form_invalid(form)


@login_required
def relatorio_pessoal(request):
    tipo_filtro = request.GET.get('tipo', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()
    pagina = request.GET.get('pagina', 1)

    qs = Descarte.objects.filter(usuario=request.user)

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

    peso_por_tipo = {}
    for d in todos:
        tipo = d.tipo_residuo or 'Nao informado'
        peso_por_tipo[tipo] = peso_por_tipo.get(tipo, 0.0) + d.peso_kg

    labels_tipos = list(peso_por_tipo.keys())
    pesos_tipos = list(peso_por_tipo.values())

    paginator = Paginator(qs.order_by('-data_hora'), 10)
    paginacao = paginator.get_page(pagina)

    tipos_unicos = list(
        Descarte.objects.filter(usuario=request.user)
        .values_list('tipo_residuo', flat=True)
        .distinct()
    )
    tipos_unicos = [t for t in tipos_unicos if t]

    return render(request, 'relatorio.html', {
        'descartes': paginacao.object_list,
        'paginacao': paginacao,
        'total_pontos': total_pontos,
        'total_descartes': total_descartes,
        'total_peso': total_peso,
        'labels_tipos': labels_tipos,
        'pesos_tipos': pesos_tipos,
        'tipo_filtro': tipo_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipos_unicos': tipos_unicos,
    })


@login_required
def exportar_relatorio_csv(request):
    descartes = Descarte.objects.filter(usuario=request.user).order_by('-data_hora').select_related('ponto')

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Data/Hora', 'Ponto de Coleta', 'Tipo de Residuo', 'Peso (kg)', 'Pontos Gerados'])

    for d in descartes:
        writer.writerow([
            d.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
            d.ponto.nome if d.ponto else f'Ponto #{d.ponto_id}',
            d.tipo_residuo,
            f'{d.peso_kg:.2f}',
            d.pontos_gerados,
        ])

    response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=relatorio_pessoal_ecosmart.csv'
    return response
