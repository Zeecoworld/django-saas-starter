"""
Thin wrapper around the Stripe SDK. Keeping all Stripe calls in one place
makes it easy to mock in tests and to swap providers later if you ever need to.
"""

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_or_create_customer(organization):
    from .models import Subscription

    existing = (
        Subscription.objects.filter(organization=organization)
        .exclude(stripe_customer_id="")
        .first()
    )
    if existing:
        return existing.stripe_customer_id

    customer = stripe.Customer.create(
        name=organization.name,
        email=organization.owner.email,
        metadata={"organization_id": str(organization.id)},
    )
    return customer.id


def create_checkout_session(organization, price_id, success_url, cancel_url):
    customer_id = get_or_create_customer(organization)
    return stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        subscription_data={"metadata": {"organization_id": str(organization.id)}},
        allow_promotion_codes=True,
    )


def create_billing_portal_session(customer_id, return_url):
    return stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)


def construct_webhook_event(payload, sig_header):
    return stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
