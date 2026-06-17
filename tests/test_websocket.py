import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator

from apps.accounts.ws_tickets import issue_ws_ticket
from apps.ai_scoring.services import run_scoring
from apps.applications.services import move_stage, submit_application
from apps.jobs.models import DEFAULT_PIPELINE_STAGES, Job
from config.asgi import application as asgi_application
from tests.factories import ApplicationFactory, CompanyMemberFactory, JobFactory, make_pdf_file

WS_HOST_HEADERS = [
    (b"host", b"localhost"),
    (b"origin", b"http://localhost"),
]


def _ws_ticket(user) -> str:
    return issue_ws_ticket(user.id)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_ws_connect_with_valid_ticket():
    membership = CompanyMemberFactory(company__slug="acme-corp")
    ticket = _ws_ticket(membership.user)

    communicator = WebsocketCommunicator(
        asgi_application,
        f"/ws/companies/acme-corp/dashboard/?ticket={ticket}",
        headers=WS_HOST_HEADERS,
    )
    connected, close_code = await communicator.connect()
    assert connected, f"expected connect, got close_code={close_code}"
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_ws_rejects_missing_ticket():
    CompanyMemberFactory(company__slug="acme-corp")

    communicator = WebsocketCommunicator(
        asgi_application,
        "/ws/companies/acme-corp/dashboard/",
        headers=WS_HOST_HEADERS,
    )
    connected, close_code = await communicator.connect()
    assert not connected
    assert close_code == 4401


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_ws_rejects_non_member():
    CompanyMemberFactory(company__slug="acme-corp")
    outsider = CompanyMemberFactory(company__slug="other-co")
    ticket = _ws_ticket(outsider.user)

    communicator = WebsocketCommunicator(
        asgi_application,
        f"/ws/companies/acme-corp/dashboard/?ticket={ticket}",
        headers=WS_HOST_HEADERS,
    )
    connected, close_code = await communicator.connect()
    assert not connected
    assert close_code == 4404


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_move_stage_broadcasts_event():
    membership = CompanyMemberFactory(company__slug="acme-corp")
    job = JobFactory(company=membership.company, pipeline_stages=list(DEFAULT_PIPELINE_STAGES))
    app = ApplicationFactory(job=job, company=membership.company, current_stage="Screening")
    ticket = _ws_ticket(membership.user)

    communicator = WebsocketCommunicator(
        asgi_application,
        f"/ws/companies/acme-corp/dashboard/?ticket={ticket}",
        headers=WS_HOST_HEADERS,
    )
    connected, close_code = await communicator.connect()
    assert connected, f"expected connect, got close_code={close_code}"

    await sync_to_async(move_stage, thread_sensitive=False)(app, new_stage="Interview", actor=membership.user)

    event = await communicator.receive_json_from()
    assert event["event"] == "application.stage_changed"
    assert event["application_id"] == app.id
    assert event["from_stage"] == "Screening"
    assert event["to_stage"] == "Interview"
    assert event["actor"] == membership.user.email

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_run_scoring_broadcasts_event():
    membership = CompanyMemberFactory(company__slug="acme-corp")
    app = ApplicationFactory(
        company=membership.company,
        parsed_resume_text="Django engineer with Celery experience.",
    )
    ticket = _ws_ticket(membership.user)

    communicator = WebsocketCommunicator(
        asgi_application,
        f"/ws/companies/acme-corp/dashboard/?ticket={ticket}",
        headers=WS_HOST_HEADERS,
    )
    connected, close_code = await communicator.connect()
    assert connected, f"expected connect, got close_code={close_code}"

    await sync_to_async(run_scoring, thread_sensitive=False)(app, actor=None)

    event = await communicator.receive_json_from()
    assert event["event"] == "application.scored"
    assert event["application_id"] == app.id
    assert event["ai_score"] is not None

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_submit_broadcasts_received(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    membership = CompanyMemberFactory(company__slug="acme-corp")
    job = JobFactory(company=membership.company, status=Job.Status.OPEN)
    ticket = _ws_ticket(membership.user)

    communicator = WebsocketCommunicator(
        asgi_application,
        f"/ws/companies/acme-corp/dashboard/?ticket={ticket}",
        headers=WS_HOST_HEADERS,
    )
    connected, close_code = await communicator.connect()
    assert connected, f"expected connect, got close_code={close_code}"

    await sync_to_async(submit_application, thread_sensitive=False)(
        job,
        full_name="Jane Doe",
        email="jane.ws@example.com",
        phone="555-1234",
        resume_file=make_pdf_file(),
    )

    event = await communicator.receive_json_from()
    assert event["event"] == "application.received"
    assert event["job_id"] == job.id
    assert event["candidate_email"] == "jane.ws@example.com"
    assert event["current_stage"] == "Applied"

    await communicator.disconnect()
