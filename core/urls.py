from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # API v1
    path('api/v1/pontos/', views.api_pontos, name='api_pontos'),
    path('api/v1/beneficios/', views.api_beneficios, name='api_beneficios'),
    path('api/v1/estatisticas/', views.api_estatisticas, name='api_estatisticas'),
]
