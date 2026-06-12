from rest_framework.permissions import BasePermission

from apps.companies.models import CompanyMember


class IsCompanyMember(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        slug = view.kwargs.get("slug")
        if not slug:
            return False
        return CompanyMember.objects.filter(
            user=request.user,
            company__slug=slug,
            company__is_active=True,
        ).exists()


class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        slug = view.kwargs.get("slug")
        if not slug:
            return False
        return CompanyMember.objects.filter(
            user=request.user,
            company__slug=slug,
            company__is_active=True,
            role=CompanyMember.Role.ADMIN,
        ).exists()
