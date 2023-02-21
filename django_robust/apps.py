from django.apps import AppConfig


class DjangoRobustConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_robust'

    def ready(self):
        import django_robust.checks  # noqa
