from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.authentication.permissions import IsSuperAdmin
from apps.users.models import User

from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """Platform-level company management — reserved to Super Admins.

    Company Admins can still read their own company through this endpoint,
    filtered to a single row, but only Super Admins can list, create,
    update or delete companies (proper RBAC enforcement lands in Part 3).
    """

    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ('list', 'create', 'update', 'partial_update', 'destroy'):
            return (IsAuthenticated(), IsSuperAdmin())
        return (IsAuthenticated(),)

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.SUPER_ADMIN:
            return Company.objects.all()
        if user.company_id:
            return Company.objects.filter(id=user.company_id)
        return Company.objects.none()
