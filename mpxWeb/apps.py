from django.apps import AppConfig
import logging
import os


logger = logging.getLogger(__name__)


class MpxwebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mpxWeb'

    def ready(self):
        # Run lightweight startup initialization once when Django loads apps
        if os.getenv("DJANGO_SKIP_INIT"):
            return
        try:
            from .initialization import initialize_app

            initialize_app()
        except Exception:  # pragma: no cover - defensive
            logger.exception("mpxWeb startup initialization failed")
