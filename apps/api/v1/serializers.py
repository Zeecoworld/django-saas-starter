from rest_framework import serializers

from apps.organizations.models import Membership, Organization
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "avatar", "created_at"]
        read_only_fields = ["id", "email", "created_at"]


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "user", "role", "joined_at"]


class OrganizationSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "is_active", "is_subscribed", "created_at"]
        read_only_fields = ["id", "slug", "is_subscribed", "created_at"]
