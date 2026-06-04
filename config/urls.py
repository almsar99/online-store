from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import permission_denied


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('catalog.urls')),
    path('blogs/', include('blog.urls')),
    path('users/', include('users.urls')),
    path('mailing/', include('mailing.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )


handler403 = permission_denied
