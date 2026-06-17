import logging
import os
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound

from apps.accounts.ws_tickets import consume_ws_ticket
from apps.companies.access import get_company_membership

User = get_user_model()
logger = logging.getLogger(__name__)

_ALLOW_UNSAFE_SYNC = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE") == "true"


def _authenticate_sync(ticket: str):
    user_id = consume_ws_ticket(ticket)
    if user_id is None:
        return None
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
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

            ticket = self._get_ticket()
            if not ticket:
                await self.close(code=4401)
                return

            if _ALLOW_UNSAFE_SYNC:
                user = _authenticate_sync(ticket)
            else:
                user = await _authenticate(ticket)
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

    def _get_ticket(self) -> str | None:
        query_string = self.scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        tickets = params.get("ticket", [])
        return tickets[0] if tickets else None
