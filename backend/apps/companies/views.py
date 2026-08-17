from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.authentication.permissions import IsSameCompany, RBACPermission
from apps.users.models import User

from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """Platform-level company management — reserved to Super Admins.

    Company Admins can still read (and only read) their own company through
    this endpoint; only Super Admins can list all companies or create,
    update, suspend or delete one.
    """

    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated, RBACPermission, IsSameCompany)
    permission_map = {
        'list': 'companies.manage',
        'create': 'companies.manage',
        'update': 'companies.manage',
        'partial_update': 'companies.manage',
        'destroy': 'companies.manage',
        # 'retrieve' is intentionally absent: any authenticated user may
        # attempt it, IsSameCompany then restricts it to their own company.
    }

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.SUPER_ADMIN:
            return Company.objects.all()
        if user.company_id:
            return Company.objects.filter(id=user.company_id)
        return Company.objects.none()
