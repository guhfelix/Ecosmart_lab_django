from django.contrib import admin
from .models import PontoColeta, Descarte


@admin.register(PontoColeta)
class PontoColetaAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'endereco',
        'tipos_aceitos',
        'horario_funcionamento',
        'ativo',
    )

    list_filter = ('ativo', 'tipos_aceitos')
    search_fields = ('nome', 'endereco', 'tipos_aceitos')
    list_editable = ('ativo',)


@admin.register(Descarte)
class DescarteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ponto', 'tipo_residuo', 'peso_kg', 'pontos_gerados', 'data_hora')
    list_filter = ('tipo_residuo', 'ponto', 'data_hora')
    search_fields = ('usuario__email', 'usuario__nome', 'tipo_residuo')
    date_hierarchy = 'data_hora'
    readonly_fields = ('pontos_gerados', 'data_hora')
