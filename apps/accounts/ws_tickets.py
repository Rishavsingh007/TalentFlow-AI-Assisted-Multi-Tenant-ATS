import uuid

from django.core.cache import cache

WS_TICKET_PREFIX = "ws_ticket:"
WS_TICKET_TTL_SECONDS = 30


def issue_ws_ticket(user_id: int) -> str:
    ticket = str(uuid.uuid4())
    cache.set(f"{WS_TICKET_PREFIX}{ticket}", user_id, timeout=WS_TICKET_TTL_SECONDS)
    return ticket


def consume_ws_ticket(ticket: str) -> int | None:
    if not ticket:
        return None
    key = f"{WS_TICKET_PREFIX}{ticket}"
    user_id = cache.get(key)
    if user_id is None:
        return None
    cache.delete(key)
    return int(user_id)
