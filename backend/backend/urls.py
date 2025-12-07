from django.conf import settings
from django.conf.urls.static import static   # <-- IMPORT OBLIGATOIRE
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('search_api.urls')),
]

# Ajout pour les images
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
