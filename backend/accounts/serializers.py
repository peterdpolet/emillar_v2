"""accounts/serializers.py"""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

User = None  # resolved lazily


def get_user():
    global User
    if User is None:
        User = get_user_model()
    return User


class UserCreateSerializer(BaseUserCreateSerializer):
    """Extends Djoser's serializer to include name, role, company."""

    class Meta(BaseUserCreateSerializer.Meta):
        model = get_user_model()
        fields = ('id', 'email', 'name', 'company', 'phone',
                  'password', 're_password')

    def create(self, validated_data):
        # New accounts inactive until staff approves (invitation-only)
        validated_data['is_active'] = False
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'name', 'role', 'company',
                  'phone', 'totp_enabled', 'is_active',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'email', 'role', 'is_active',
                            'totp_enabled', 'created_at', 'updated_at')


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TOTPVerifySerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=6)


class TOTPSetupConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=6)


class TOTPDisableSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=6)
