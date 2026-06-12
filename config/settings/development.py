from .base import *  # noqa: F403

DEBUG = True
DJANGO_ENV = "development"

CORS_ALLOWED_ORIGINS = env.list(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:5173", "http://127.0.0.1:5173"],
)
