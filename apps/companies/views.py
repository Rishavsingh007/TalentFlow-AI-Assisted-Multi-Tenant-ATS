from rest_framework import generics
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Company, CompanyMember
from .serializers import CompanySerializer, CompanyUpdateSerializer


class CompanyDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        return Company.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return CompanyUpdateSerializer
        return CompanySerializer

    def get_object(self):
        slug = self.kwargs.get("slug")
        try:
            company = Company.objects.get(slug=slug, is_active=True)
        except Company.DoesNotExist:
            raise NotFound()

        membership = CompanyMember.objects.filter(user=self.request.user, company=company).first()
        if not membership:
            raise NotFound()

        if self.request.method in ("PUT", "PATCH") and membership.role != CompanyMember.Role.ADMIN:
            raise PermissionDenied()

        return company
