from django.contrib import admin
from .models import Beneficio, Resgate, Auditoria


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'custo_pontos', 'ativo')
    list_filter = ('tipo', 'ativo')
    search_fields = ('nome', 'descricao')
    list_editable = ('ativo',)
    actions = ['ativar_beneficios', 'desativar_beneficios']

    @admin.action(description='Ativar beneficios selecionados')
    def ativar_beneficios(self, request, queryset):
        queryset.update(ativo=True)

    @admin.action(description='Desativar beneficios selecionados')
    def desativar_beneficios(self, request, queryset):
        queryset.update(ativo=False)


@admin.register(Resgate)
class ResgateAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'beneficio', 'pontos_utilizados', 'codigo_voucher', 'status', 'data_resgate')
    list_filter = ('status', 'data_resgate')
    search_fields = ('usuario__email', 'usuario__nome', 'codigo_voucher')
    readonly_fields = ('data_resgate', 'codigo_voucher', 'pontos_utilizados')
    date_hierarchy = 'data_resgate'


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('data', 'usuario', 'acao')
    list_filter = ('data',)
    search_fields = ('usuario__email', 'acao')
    readonly_fields = ('data', 'usuario', 'acao')
    date_hierarchy = 'data'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
