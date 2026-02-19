from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.http.response import Http404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import RedirectView
from django.views.static import serve

from .conf import sphinx_settings


def superuser_required(view_func: Callable) -> Callable:
    """
    Decorator for views that checks that the user is logged in and is a superuser,
    displaying the login page if necessary using the standard Django patterns.
    """

    @wraps(view_func)
    def _checklogin(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        user = getattr(request, "user", None)

        if user and user.is_active and user.is_superuser:
            return view_func(request, *args, **kwargs)

        assert hasattr(request, "session"), (
            "The Django admin requires session middleware to be installed. "
            "Edit your MIDDLEWARE setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware'."
        )

        defaults = {
            "template_name": "admin/login.html",
            "redirect_field_name": request.get_full_path(),
            "authentication_form": AdminAuthenticationForm,
            "extra_context": {
                "title": _("Log in"),
                "app_path": request.get_full_path(),
            },
        }
        return LoginView.as_view(**defaults)(request)

    return _checklogin


def superuser_required_simple(view_func: Callable) -> Callable:
    """
    A simpler version of superuser_required using user_passes_test.
    """
    return user_passes_test(lambda u: u.is_active and u.is_superuser)(view_func)


def public(function: Callable | None = None) -> Callable | None:
    """
    Dummy decorator that doesn't check anything.
    """
    return function


class DocsAccessSettingError(ValueError):
    pass


class DocsRootSettingError(ValueError):
    pass


DOCS_ACCESS_CHOICES = (
    "public",
    "login_required",
    "staff",
    "superuser",
)


def get_decorator() -> Callable:
    """
    Returns the appropriate decorator based on the DOCS_ACCESS setting.
    """
    access = sphinx_settings.ACCESS

    if access == "public" or access not in DOCS_ACCESS_CHOICES:
        return public
    if access == "login_required":
        return login_required
    if access == "staff":
        return staff_member_required
    if access == "superuser":
        return superuser_required

    return public


def serve_docs(request: HttpRequest, path: str, **kwargs: Any) -> HttpResponse:
    """
    Serves the documentation files.
    """
    access = sphinx_settings.ACCESS

    if access not in DOCS_ACCESS_CHOICES:
        raise DocsAccessSettingError(
            f"DOCS_ACCESS setting value is incorrect: {access} "
            f"(choices are: {DOCS_ACCESS_CHOICES})"
        )

    document_root = kwargs.get("document_root") or sphinx_settings.ROOT

    if not document_root:
        raise DocsRootSettingError(
            f"DOCS_ROOT setting value is incorrect: {document_root} "
            "(must be a valid path)"
        )

    kwargs["document_root"] = document_root

    # Apply the decorator dynamically
    decorator = get_decorator()

    @decorator
    def _serve(request, path, **kwargs):
        try:
            return serve(request, path, **kwargs)
        except Http404:
            if sphinx_settings.DIRHTML:
                index_path = str(Path(path) / "index.html")
                return serve(request, index_path, **kwargs)
            raise

    return _serve(request, path, **kwargs)


class DocsRootView(RedirectView):
    """
    Redirects to the root of the documentation.
    """

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str | None:
        del args, kwargs
        namespace = (
            self.request.resolver_match.namespace
            if self.request.resolver_match
            else None
        )
        view_name = ":".join(filter(None, [namespace, "docs_files"]))

        return reverse(view_name, kwargs={"path": "index.html"})
