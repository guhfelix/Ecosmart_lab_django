from django.urls import path
from . import views

app_name = 'recompensas'

urlpatterns = [
    # ── Cidadão ──────────────────────────────────────────────
    path('beneficios/', views.BeneficiosView.as_view(), name='beneficios'),
    path('meus-resgates/', views.MeusResgatesView.as_view(), name='meus_resgates'),

    # ── Admin — Gestão de Benefícios ───────────────────────────
    # As rotas manuais de CRUD de benefícios foram removidas.
    # A gestão é feita exclusivamente pelo Django Admin:
    # /django-admin/recompensas/beneficio/

    # ── Admin — Utilizadores e Auditoria ───────────────────────
    path('admin/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin/usuarios/<int:user_id>/papel/', views.alterar_papel, name='alterar_papel'),
    path('admin/usuarios/<int:user_id>/status/', views.alterar_status_usuario, name='alterar_status'),
    path('admin/auditoria/', views.admin_auditoria, name='auditoria'),
]
