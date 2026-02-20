from django.conf.urls import include, re_path
from django.contrib import admin

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^docs/", include("django_sphinx_docs.urls")),
]
