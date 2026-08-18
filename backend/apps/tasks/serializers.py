from rest_framework import serializers

from apps.users.models import User
from apps.users.serializers import UserSerializer

from .models import Comment, Task


class CommentSerializer(serializers.ModelSerializer):
    author_detail = UserSerializer(source='author', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'task', 'author', 'author_detail', 'content', 'created_at')
        read_only_fields = ('id', 'task', 'author', 'created_at')


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'priority', 'due_date',
            'estimated_hours', 'actual_hours', 'company', 'project',
            'assigned_to', 'assigned_to_detail', 'comments_count',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'company', 'created_at', 'updated_at')

    def validate_project(self, project):
        request = self.context['request']
        if request.user.role != User.Role.SUPER_ADMIN and project.company_id != request.user.company_id:
            raise serializers.ValidationError('Project must belong to your company.')
        return project

    def validate_assigned_to(self, user):
        if user is None:
            return user
        request = self.context['request']
        if request.user.role != User.Role.SUPER_ADMIN and user.company_id != request.user.company_id:
            raise serializers.ValidationError('Assignee must belong to your company.')
        return user

    def validate(self, attrs):
        project = attrs.get('project') or getattr(self.instance, 'project', None)
        assigned_to = attrs.get('assigned_to') if 'assigned_to' in attrs else getattr(self.instance, 'assigned_to', None)
        if project and assigned_to and not (
            project.manager_id == assigned_to.id
            or project.members.filter(user_id=assigned_to.id).exists()
        ):
            raise serializers.ValidationError({'assigned_to': 'Assignee must be a member of the project.'})
        return attrs


class TaskStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task.Status.choices)

    def save(self, **kwargs):
        self.instance.status = self.validated_data['status']
        self.instance.save(update_fields=['status', 'updated_at'])
        return self.instance
