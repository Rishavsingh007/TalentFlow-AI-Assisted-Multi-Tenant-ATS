from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.auth import EmailTokenObtainPairView
from apps.accounts.views import RegisterView
from apps.applications.views import (
    ApplicationScoreView,
    ApplicationStageUpdateView,
    ApplyView,
    CompanyApplicationDetailView,
    CompanyApplicationListView,
)
from apps.audit.views import CompanyAuditLogListView
from apps.companies.views import CompanyDetailView
from apps.core.views import health_check
from apps.jobs.views import (
    CompanyJobDetailView,
    CompanyJobListCreateView,
    JobPublishView,
    PublicJobDetailView,
    PublicJobListView,
)

api_v1_patterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", EmailTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("companies/<slug:slug>/", CompanyDetailView.as_view(), name="company-detail"),
    path(
        "companies/<slug:slug>/jobs/",
        CompanyJobListCreateView.as_view(),
        name="company-job-list",
    ),
    path(
        "companies/<slug:slug>/jobs/<int:id>/",
        CompanyJobDetailView.as_view(),
        name="company-job-detail",
    ),
    path(
        "companies/<slug:slug>/jobs/<int:id>/publish/",
        JobPublishView.as_view(),
        name="company-job-publish",
    ),
    path(
        "companies/<slug:slug>/applications/",
        CompanyApplicationListView.as_view(),
        name="company-application-list",
    ),
    path(
        "companies/<slug:slug>/applications/<int:id>/",
        CompanyApplicationDetailView.as_view(),
        name="company-application-detail",
    ),
    path(
        "companies/<slug:slug>/applications/<int:id>/stage/",
        ApplicationStageUpdateView.as_view(),
        name="company-application-stage",
    ),
    path(
        "companies/<slug:slug>/applications/<int:id>/score/",
        ApplicationScoreView.as_view(),
        name="company-application-score",
    ),
    path(
        "companies/<slug:slug>/audit-logs/",
        CompanyAuditLogListView.as_view(),
        name="company-audit-log-list",
    ),
    path("jobs/", PublicJobListView.as_view(), name="public-job-list"),
    path("jobs/<int:id>/", PublicJobDetailView.as_view(), name="public-job-detail"),
    path("jobs/<int:id>/apply/", ApplyView.as_view(), name="job-apply"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
    path("api/v1/", include(api_v1_patterns)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
