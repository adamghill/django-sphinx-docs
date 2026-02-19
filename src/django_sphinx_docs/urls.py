from django.urls import re_path

from .conf import sphinx_settings
from .views import DocsRootView, serve_docs

urlpatterns = []

if not sphinx_settings.DIRHTML:
    urlpatterns += [
        re_path(r"^$", DocsRootView.as_view(permanent=True), name="docs_root"),
    ]

urlpatterns += [
    re_path(r"^(?P<path>.*)$", serve_docs, name="docs_files"),
]
