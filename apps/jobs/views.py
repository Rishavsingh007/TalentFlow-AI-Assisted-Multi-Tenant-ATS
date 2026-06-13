from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.companies.access import (
    get_company_for_member,
    get_company_membership,
    get_job_for_company,
    require_recruiter_or_admin,
)
from apps.jobs.models import Job
from apps.jobs.serializers import JobCreateUpdateSerializer, JobSerializer, PublicJobSerializer
from apps.jobs.utils import get_open_job


class PublicJobListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicJobSerializer

    @extend_schema(tags=["jobs"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Job.objects.open().select_related("company")


class PublicJobDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicJobSerializer
    lookup_url_kwarg = "id"

    @extend_schema(tags=["jobs"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return get_open_job(self.kwargs["id"])


class CompanyJobListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["jobs"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=["jobs"])
    def post(self, request, *args, **kwargs):
        membership = get_company_membership(slug=self.kwargs["slug"], user=request.user)
        require_recruiter_or_admin(membership)
        return super().post(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return JobCreateUpdateSerializer
        return JobSerializer

    def get_queryset(self):
        company = get_company_for_member(slug=self.kwargs["slug"], user=self.request.user)
        return Job.objects.for_company(company)

    def perform_create(self, serializer):
        company = get_company_for_member(slug=self.kwargs["slug"], user=self.request.user)
        serializer.save(company=company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(JobSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)


class CompanyJobDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    @extend_schema(tags=["jobs"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=["jobs"])
    def patch(self, request, *args, **kwargs):
        membership = get_company_membership(slug=self.kwargs["slug"], user=request.user)
        require_recruiter_or_admin(membership)
        return super().patch(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return JobCreateUpdateSerializer
        return JobSerializer

    def get_object(self):
        return get_job_for_company(
            slug=self.kwargs["slug"],
            job_id=self.kwargs["id"],
            user=self.request.user,
        )


class JobPublishView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    @extend_schema(tags=["jobs"], request=None, responses=JobSerializer)
    def post(self, request, slug, id):
        membership = get_company_membership(slug=slug, user=request.user)
        require_recruiter_or_admin(membership)

        job = get_job_for_company(slug=slug, job_id=id, user=request.user)
        from apps.jobs.services import publish_job

        job = publish_job(job, actor=request.user)
        return Response(JobSerializer(job).data, status=status.HTTP_200_OK)
