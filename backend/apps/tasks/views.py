from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.authentication.mixins import CompanyScopedQuerySetMixin
from apps.authentication.permissions import IsSameCompany, RBACPermission
from apps.users.models import User

from .models import Comment, Task
from .serializers import CommentSerializer, TaskSerializer, TaskStatusSerializer


class TaskViewSet(CompanyScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, RBACPermission, IsSameCompany)
    permission_map = {
        'list': 'tasks.view',
        'retrieve': 'tasks.view',
        'create': 'tasks.create',
        'update': 'tasks.update',
        'partial_update': 'tasks.update',
        'destroy': 'tasks.delete',
        'set_status': 'tasks.update',
        'comments': 'comments.view',
        'add_comment': 'comments.create',
    }
    filterset_fields = ('status', 'priority', 'project', 'assigned_to')
    search_fields = ('title', 'description')
    ordering_fields = ('created_at', 'due_date', 'priority', 'status', 'title')

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.EMPLOYEE:
            queryset = queryset.filter(
                Q(assigned_to=user) | Q(project__manager=user) | Q(project__members__user=user)
            ).distinct()
        return queryset

    @action(detail=True, methods=['patch'], url_path='status')
    def set_status(self, request, pk=None):
        task = self.get_object()
        serializer = TaskStatusSerializer(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TaskSerializer(task, context=self.get_serializer_context()).data)

    @action(detail=True, methods=['get'], url_path='comments')
    def comments(self, request, pk=None):
        task = self.get_object()
        serializer = CommentSerializer(task.comments.all(), many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='comments/add')
    def add_comment(self, request, pk=None):
        task = self.get_object()
        serializer = CommentSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
