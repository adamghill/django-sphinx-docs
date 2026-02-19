#!/usr/bin/env python
"""
This script is a trick to setup a fake Django environment, since this reusable
app will be developed and tested outside any specific Django project.

Via ``settings.configure`` you will be able to set all necessary settings
for your app and run the tests as if you were calling ``./manage.py test``.

"""

import sys

from django.conf import settings
from django.test.utils import get_runner

EXTERNAL_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.sites",
]
INTERNAL_APPS = [
    "django_sphinx_docs",
]
INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS

if not settings.configured:
    settings.configure(
        SECRET_KEY="sdfkjsdfsdiuy7yruhsdvyggvbis",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=INSTALLED_APPS,
        ROOT_URLCONF="tests.urls",
        USE_TZ=True,
        PASSWORD_HASHERS=("django.contrib.auth.hashers.MD5PasswordHasher",),
        STATIC_URL="/static/",
    )


def runtests(*test_args):
    """
    Run the tests using the default Django test runner.
    """
    if not test_args:
        test_args = ["tests"]

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False)
    failures = test_runner.run_tests(test_args)
    sys.exit(bool(failures))


if __name__ == "__main__":
    runtests(*sys.argv[1:])
