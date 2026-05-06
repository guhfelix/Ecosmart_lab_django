from django.urls import path
from . import views

app_name = 'recompensas'

urlpatterns = [
    # Cidadao
    path('beneficios/', views.beneficios, name='beneficios'),
    path('meus-resgates/', views.meus_resgates, name='meus_resgates'),

    # Gestor - Beneficios
    path('admin/beneficios/', views.admin_beneficios, name='admin_beneficios'),
    path('admin/beneficios/novo/', views.novo_beneficio, name='novo_beneficio'),
    path('admin/beneficios/<int:pk>/editar/', views.editar_beneficio, name='editar_beneficio'),
    path('admin/beneficios/<int:pk>/toggle/', views.toggle_beneficio, name='toggle_beneficio'),
    path('admin/beneficios/<int:pk>/excluir/', views.excluir_beneficio, name='excluir_beneficio'),

    # Admin - Usuarios e Auditoria
    path('admin/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin/usuarios/<int:user_id>/papel/', views.alterar_papel, name='alterar_papel'),
    path('admin/usuarios/<int:user_id>/status/', views.alterar_status_usuario, name='alterar_status'),
    path('admin/auditoria/', views.admin_auditoria, name='auditoria'),
]
