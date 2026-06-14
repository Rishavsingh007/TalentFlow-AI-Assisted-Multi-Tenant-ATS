from .base import *  # noqa: F403

DEBUG = True
DJANGO_ENV = "development"

CORS_ALLOWED_ORIGINS = env.list(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:5173", "http://127.0.0.1:5173"],
)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="mailhog")  # noqa: F405
EMAIL_PORT = env.int("EMAIL_PORT", default=1025)  # noqa: F405
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@talentflow.local")  # noqa: F405
