import pytest

from apps.billing.models import Plan

from .factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_organization_has_no_subscription_by_default():
    org = OrganizationFactory()
    assert org.is_subscribed is False
    assert org.active_subscription is None


def test_pricing_page_loads(client):
    Plan.objects.create(
        name="Starter", stripe_price_id="price_test", interval="month", amount_cents=1900
    )
    response = client.get("/billing/pricing/")
    assert response.status_code == 200
    assert b"Starter" in response.content
