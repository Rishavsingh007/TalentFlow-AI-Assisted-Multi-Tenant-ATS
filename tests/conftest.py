import os
from pathlib import Path

import pytest
from rest_framework.test import APIClient

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture(autouse=True)
def _channel_layers():
    from channels.layers import channel_layers

    channel_layers.backends = {}


@pytest.fixture(autouse=True)
def _cleanup_test_db():
    yield
    from django.conf import settings

    db_path = Path(settings.TEST_DATABASE_PATH)
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def api_client():
    return APIClient()
