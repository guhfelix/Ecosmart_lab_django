from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nome', 'papel', 'saldo_pontos', 'is_active', 'data_cadastro')
    list_filter = ('papel', 'is_active', 'is_staff')
    search_fields = ('email', 'nome')
    ordering = ('nome',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Informacoes Pessoais', {'fields': ('nome', 'first_name', 'last_name')}),
        ('EcoSmart', {'fields': ('papel', 'saldo_pontos')}),
        ('Permissoes', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'nome', 'papel', 'password1', 'password2'),
        }),
    )
