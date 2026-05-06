from django.urls import path
from .views import EcosmartLoginView, EcosmartLogoutView, RegistroView

app_name = 'accounts'

urlpatterns = [
    path('login/', EcosmartLoginView.as_view(), name='login'),
    path('logout/', EcosmartLogoutView.as_view(), name='logout'),
    path('register/', RegistroView.as_view(), name='register'),
]
