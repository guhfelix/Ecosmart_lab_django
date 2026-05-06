from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('', include('coleta.urls')),
    path('', include('recompensas.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'EcoSmart Solutions - Administracao'
admin.site.site_title = 'EcoSmart Admin'
admin.site.index_title = 'Painel de Controle'
