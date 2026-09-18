from .base import *  # noqa

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += ["debug_toolbar", "django_extensions"]  # noqa: F405
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]

CELERY_TASK_ALWAYS_EAGER = True  # tasks run synchronously, no worker needed in dev

# Relaxed email verification while building locally — flip to "mandatory" when ready
ACCOUNT_EMAIL_VERIFICATION = "optional"
