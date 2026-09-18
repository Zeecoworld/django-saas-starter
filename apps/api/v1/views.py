from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.organizations.models import Organization

from .serializers import OrganizationSerializer, UserSerializer


class MeView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        return Response(UserSerializer(request.user).data)


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only: organizations are created/joined through the web UI, not the API."""

    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(members=self.request.user)
