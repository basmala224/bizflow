from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.authentication.mixins import CompanyScopedQuerySetMixin
from apps.authentication.permissions import IsSameCompany, RBACPermission

from .models import User
from .serializers import UserCreateSerializer, UserSerializer


class UserViewSet(CompanyScopedQuerySetMixin, viewsets.ModelViewSet):
    """Company-scoped user management, gated by fine-grained RBAC permissions."""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, RBACPermission, IsSameCompany)
    permission_map = {
        'list': 'users.view',
        'retrieve': 'users.view',
        'create': 'users.create',
        'update': 'users.update',
        'partial_update': 'users.update',
        'destroy': 'users.delete',
    }

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
