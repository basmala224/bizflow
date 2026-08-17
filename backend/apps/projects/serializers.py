from rest_framework import serializers

from apps.users.models import User
from apps.users.serializers import UserSerializer

from .models import Project, ProjectMember


class ProjectMemberSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ProjectMember
        fields = ('id', 'project', 'user', 'user_detail', 'role', 'joined_at')
        read_only_fields = ('id', 'project', 'joined_at')

    def validate_user(self, user):
        request = self.context['request']
        company_id = self.context['project'].company_id
        if request.user.role != User.Role.SUPER_ADMIN and user.company_id != company_id:
            raise serializers.ValidationError('User does not belong to this project\'s company.')
        return user


class ProjectSerializer(serializers.ModelSerializer):
    manager_detail = UserSerializer(source='manager', read_only=True)
    members_count = serializers.IntegerField(source='members.count', read_only=True)

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'status', 'priority', 'start_date',
            'end_date', 'budget', 'progress', 'company', 'manager',
            'manager_detail', 'members_count', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'company', 'created_at', 'updated_at')

    def validate_manager(self, manager):
        if manager is None:
            return manager
        request = self.context['request']
        company = request.user.company
        if request.user.role != User.Role.SUPER_ADMIN and manager.company_id != company.id:
            raise serializers.ValidationError('Manager must belong to the same company.')
        return manager

    def validate_progress(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError('Progress must be between 0 and 100.')
        return value
