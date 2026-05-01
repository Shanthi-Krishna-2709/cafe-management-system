from django.apps import AppConfig


class CafeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cafe_app'

    def ready(self):
        from django.db.models.signals import post_migrate

        from .signals import sync_menu_catalog

        post_migrate.connect(sync_menu_catalog, sender=self)
