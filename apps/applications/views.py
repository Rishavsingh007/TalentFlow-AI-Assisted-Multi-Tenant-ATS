from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.applications.serializers import ApplicationCreatedSerializer, ApplySerializer
from apps.applications.services import submit_application
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
