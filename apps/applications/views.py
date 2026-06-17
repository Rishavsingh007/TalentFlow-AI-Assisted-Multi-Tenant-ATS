from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.applications.models import Application
from apps.applications.serializers import (
    ApplicationCreatedSerializer,
    ApplicationDetailSerializer,
    ApplicationListSerializer,
    ApplicationScoreQueuedSerializer,
    ApplicationScoreSerializer,
    ApplySerializer,
    StageMoveSerializer,
)
from apps.applications.services import move_stage, submit_application
from apps.ai_scoring.services import rescore_application
from apps.companies.access import (
    get_application_for_company,
    get_company_for_member,
    get_company_membership,
    require_recruiter_or_admin,
)
from apps.jobs.utils import get_open_job


class ApplyView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ApplySerializer

    @extend_schema(tags=["applications"], request=ApplySerializer, responses=ApplicationCreatedSerializer)
    def post(self, request, id):
        job = get_open_job(id)
        serializer = ApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application = submit_application(
            job,
            full_name=serializer.validated_data["full_name"],
            email=serializer.validated_data["email"],
            phone=serializer.validated_data.get("phone", ""),
            resume_file=serializer.validated_data["resume"],
        )

        return Response(
            ApplicationCreatedSerializer(application).data,
            status=status.HTTP_201_CREATED,
        )


class CompanyApplicationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationListSerializer

    @extend_schema(tags=["applications"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        company = get_company_for_member(slug=self.kwargs["slug"], user=self.request.user)
        queryset = Application.objects.filter(company=company).select_related("candidate", "job")

        job_id = self.request.query_params.get("job")
        if job_id:
            queryset = queryset.filter(job_id=job_id)

        current_stage = self.request.query_params.get("current_stage")
        if current_stage:
            queryset = queryset.filter(current_stage=current_stage)

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset


class CompanyApplicationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationDetailSerializer

    @extend_schema(tags=["applications"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return get_application_for_company(
            slug=self.kwargs["slug"],
            application_id=self.kwargs["id"],
            user=self.request.user,
        )


class ApplicationStageUpdateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StageMoveSerializer

    @extend_schema(tags=["applications"], request=StageMoveSerializer, responses=ApplicationDetailSerializer)
    def patch(self, request, slug, id):
        membership = get_company_membership(slug=slug, user=request.user)
        require_recruiter_or_admin(membership)

        application = get_application_for_company(slug=slug, application_id=id, user=request.user)
        serializer = StageMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application = move_stage(
            application,
            new_stage=serializer.validated_data["current_stage"],
            actor=request.user,
        )
        return Response(ApplicationDetailSerializer(application).data, status=status.HTTP_200_OK)


class ApplicationScoreView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationScoreSerializer

    def get_application(self):
        return get_application_for_company(
            slug=self.kwargs["slug"],
            application_id=self.kwargs["id"],
            user=self.request.user,
        )

    @extend_schema(tags=["applications"], responses=ApplicationScoreSerializer)
    def get(self, request, slug, id):
        application = self.get_application()
        return Response(ApplicationScoreSerializer(application).data)

    @extend_schema(tags=["applications"], responses=ApplicationScoreSerializer)
    def post(self, request, slug, id):
        membership = get_company_membership(slug=slug, user=request.user)
        require_recruiter_or_admin(membership)

        application = self.get_application()
        rescore_application(application, actor=request.user)
        return Response(
            ApplicationScoreQueuedSerializer(
                {"status": "queued", "application_id": application.id}
            ).data,
            status=status.HTTP_202_ACCEPTED,
        )
