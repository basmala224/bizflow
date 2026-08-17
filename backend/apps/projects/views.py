from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.mixins import CompanyScopedQuerySetMixin
from apps.authentication.permissions import IsSameCompany, RBACPermission
from apps.users.models import User

from .models import Project, ProjectMember
from .serializers import ProjectMemberSerializer, ProjectSerializer


class ProjectViewSet(CompanyScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated, RBACPermission, IsSameCompany)
    permission_map = {
        'list': 'projects.view',
        'retrieve': 'projects.view',
        'create': 'projects.create',
        'update': 'projects.update',
        'partial_update': 'projects.update',
        'destroy': 'projects.delete',
        'members': 'projects.view',
        'add_member': 'projects.update',
        'remove_member': 'projects.update',
    }
    filterset_fields = ('status', 'priority', 'manager')
    search_fields = ('name', 'description')
    ordering_fields = ('created_at', 'start_date', 'end_date', 'priority', 'progress', 'name')

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.EMPLOYEE:
            queryset = queryset.filter(Q(manager=user) | Q(members__user=user)).distinct()
        return queryset

    @action(detail=True, methods=['get'], url_path='members')
    def members(self, request, pk=None):
        project = self.get_object()
        serializer = ProjectMemberSerializer(project.members.all(), many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='members/add')
    def add_member(self, request, pk=None):
        project = self.get_object()
        context = self.get_serializer_context()
        context['project'] = project
        serializer = ProjectMemberSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'members/(?P<user_id>\d+)')
    def remove_member(self, request, pk=None, user_id=None):
        project = self.get_object()
        deleted, _ = ProjectMember.objects.filter(project=project, user_id=user_id).delete()
        if not deleted:
            return Response({'detail': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
