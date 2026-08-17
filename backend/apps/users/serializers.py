from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'phone', 'photo',
            'position', 'department', 'role', 'company', 'is_active',
            'date_joined',
        )
        read_only_fields = ('id', 'date_joined')


class UserProfileSerializer(serializers.ModelSerializer):
    """Self-service profile update — cannot change role or company."""

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'phone', 'photo',
            'position', 'department', 'role', 'company', 'date_joined',
        )
        read_only_fields = ('id', 'email', 'role', 'company', 'date_joined')


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = (
            'id', 'email', 'password', 'first_name', 'last_name', 'phone',
            'position', 'department', 'role', 'is_active',
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        password = validated_data.pop('password')
        company = self.context['request'].user.company
        user = User(company=company, **validated_data)
        user.set_password(password)
        user.save()
        return user
