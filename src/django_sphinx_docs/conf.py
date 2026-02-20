from django.conf import settings
from django.core.signals import setting_changed
from django.dispatch import receiver


class AppSettings:
    """
    AppSettings handles settings for django-sphinx-docs.
    """

    prefix = "DOCS"

    def __init__(self):
        self._defaults = {
            "ROOT": None,
            "ACCESS": "public",
            "DIRHTML": False,
        }
        self._cache = {}

    def __getattr__(self, name):
        if name not in self._defaults:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

        if name not in self._cache:
            setting_name = f"{self.prefix}_{name}"
            self._cache[name] = getattr(settings, setting_name, self._defaults[name])

        return self._cache[name]

    def clear_cache(self):
        self._cache = {}


sphinx_settings = AppSettings()


@receiver(setting_changed)
def reload_settings(setting, **_kwargs):
    if setting.startswith(sphinx_settings.prefix):
        sphinx_settings.clear_cache()
