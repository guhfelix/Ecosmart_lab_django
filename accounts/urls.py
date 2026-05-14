from django.urls import path
from .views import (
    EcosmartLoginView,
    EcosmartLogoutView,
    RegistroView,
    PerfilView,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', EcosmartLoginView.as_view(), name='login'),
    path('logout/', EcosmartLogoutView.as_view(), name='logout'),
    path('register/', RegistroView.as_view(), name='register'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
]