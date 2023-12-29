from django.apps import AppConfig


class MultiuserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'multiuser'

    def ready(self):
        import multiuser.signals  # noqa