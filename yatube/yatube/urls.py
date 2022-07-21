from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('posts.urls', namespace='posts')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/', include('users.urls', namespace='users')),
    path('about/', include('about.urls', namespace='about'))
]

handler404 = 'core.views.page_not_found'

CSRF_FAILURE_VIEW = 'core.views.csrf_failure'

handler403 = 'core.views.permission_denied'

handler500 = 'core.views.server_error'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
