from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.companies.access import get_company_for_member

from .models import AuditLog
from .serializers import AuditLogSerializer


class CompanyAuditLogListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AuditLogSerializer

    @extend_schema(tags=["audit"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        company = get_company_for_member(slug=self.kwargs["slug"], user=self.request.user)
        queryset = AuditLog.objects.filter(company=company).select_related("actor")

        action = self.request.query_params.get("action")
        if action:
            queryset = queryset.filter(action=action)

        object_type = self.request.query_params.get("object_type")
        if object_type:
            queryset = queryset.filter(object_type=object_type)

        return queryset
