import pytest

from apps.organizations.models import Membership, Organization

from .factories import OrganizationFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_organization_slug_is_generated():
    org = OrganizationFactory(name="Acme Inc")
    assert org.slug == "acme-inc"


def test_duplicate_org_names_get_unique_slugs():
    OrganizationFactory(name="Acme Inc")
    org2 = OrganizationFactory(name="Acme Inc")
    assert org2.slug == "acme-inc-2"


def test_owner_membership_created():
    org = OrganizationFactory()
    membership = Membership.objects.get(organization=org, user=org.owner)
    assert membership.role == Membership.Role.OWNER
    assert membership.can_manage_billing is True


def test_create_organization_view_requires_login(client):
    response = client.get("/org/create/")
    assert response.status_code == 302
    assert "/accounts/login/" in response.url


def test_authenticated_user_can_create_organization(client):
    user = UserFactory()
    client.force_login(user)
    response = client.post("/org/create/", {"name": "My New Org"})
    assert response.status_code == 302
    assert Organization.objects.filter(name="My New Org", owner=user).exists()
