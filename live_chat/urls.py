from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_title = "LiveChat"
admin.site.site_header = "LiveChat"
admin.site.app_index = "Welcome to LiveChat"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("core.urls"))
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
