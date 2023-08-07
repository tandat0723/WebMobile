from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
import debug_toolbar

schema_view = get_schema_view(
    openapi.Info(
        title="Mobile API",
        default_version='v1',
        description="APIs",
        contact=openapi.Contact(email="trantandat0723@gmail.com"),
        license=openapi.License(name="Version 2023"),
    ),
    public=True, permission_classes=[permissions.AllowAny, ]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mobilephoneapp.urls')),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    re_path(r'^swagger/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
    re_path(r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
    path('__debug__/', include(debug_toolbar.urls)),
]
