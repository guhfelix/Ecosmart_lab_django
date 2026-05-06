from django.urls import path
from . import views, views_gestor

app_name = 'coleta'

urlpatterns = [
    # Cidadao
    path('pontos/', views.PontosListView.as_view(), name='pontos'),
    path('descarte/', views.RegistrarDescarteView.as_view(), name='descarte'),
    path('relatorio/', views.relatorio_pessoal, name='relatorio'),
    path('relatorio/exportar/', views.exportar_relatorio_csv, name='exportar_csv'),

    # GestorA
    path('admin/relatorios/', views_gestor.relatorios_gestor, name='relatorios_gestor'),
    path('admin/relatorios/exportar/', views_gestor.exportar_relatorios_csv, name='exportar_relatorios_csv'),
    path('admin/relatorios/resumo/', views_gestor.exportar_resumo_pontos_csv, name='exportar_resumo_csv'),
]
