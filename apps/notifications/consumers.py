import logging
import os
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from apps.companies.access import get_company_membership

User = get_user_model()
logger = logging.getLogger(__name__)

_ALLOW_UNSAFE_SYNC = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE") == "true"


def _authenticate_sync(token: str):
    try:
        access = AccessToken(token)
        return User.objects.get(id=int(access["user_id"]))
    except (TokenError, User.DoesNotExist, KeyError, TypeError, ValueError):
        return None


def _get_company_for_member_sync(user, slug: str):
    try:
        membership = get_company_membership(slug=slug, user=user)
        return membership.company
    except NotFound:
        return None


_authenticate = database_sync_to_async(_authenticate_sync, thread_sensitive=False)
_get_company_for_member = database_sync_to_async(
    _get_company_for_member_sync, thread_sensitive=False
)


class CompanyDashboardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            self.slug = self.scope["url_route"]["kwargs"]["slug"]
            self.company_id = None
            self.group_name = None

            token = self._get_token()
            if not token:
                await self.close(code=4401)
                return

            if _ALLOW_UNSAFE_SYNC:
                user = _authenticate_sync(token)
            else:
                user = await _authenticate(token)
            if user is None:
                await self.close(code=4401)
                return

            if _ALLOW_UNSAFE_SYNC:
                company = _get_company_for_member_sync(user, self.slug)
            else:
                company = await _get_company_for_member(user, self.slug)
            if company is None:
                await self.close(code=4404)
                return

            if self.channel_layer is None:
                await self.close(code=1011)
                return

            self.company_id = company.id
            self.group_name = f"company_{company.id}_dashboard"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        except Exception:
            logger.exception("WebSocket connect failed")
            await self.close(code=1011)

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        return

    async def dashboard_event(self, event):
        await self.send_json(event["payload"])

    def _get_token(self) -> str | None:
        query_string = self.scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        tokens = params.get("token", [])
        return tokens[0] if tokens else None
