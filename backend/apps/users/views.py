from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.authentication.permissions import IsCompanyAdmin

from .models import User
from .serializers import UserCreateSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Company-scoped user management for Admins/Super Admins."""

    permission_classes = (IsAuthenticated, IsCompanyAdmin)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.SUPER_ADMIN:
            return User.objects.all()
        return User.objects.filter(company_id=user.company_id)
