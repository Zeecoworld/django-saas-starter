import logging
from datetime import datetime, timezone

from apps.organizations.models import Organization

from .models import Plan, Subscription, WebhookEvent

logger = logging.getLogger(__name__)


def handle_event(event):
    """Dispatch a verified Stripe event. Idempotent: duplicate event IDs are skipped."""
    if WebhookEvent.objects.filter(stripe_event_id=event["id"]).exists():
        return

    WebhookEvent.objects.create(
        stripe_event_id=event["id"], event_type=event["type"], payload=event
    )

    handler = _HANDLERS.get(event["type"])
    if handler:
        handler(event["data"]["object"])
    else:
        logger.info("Unhandled Stripe event type: %s", event["type"])


def _upsert_subscription(stripe_sub):
    org_id = stripe_sub.get("metadata", {}).get("organization_id")
    organization = None
    if org_id:
        organization = Organization.objects.filter(id=org_id).first()
    if organization is None:
        # Fall back to matching by customer id on an existing row
        existing = Subscription.objects.filter(stripe_customer_id=stripe_sub["customer"]).first()
        organization = existing.organization if existing else None
    if organization is None:
        logger.warning("Could not resolve organization for subscription %s", stripe_sub["id"])
        return

    price_id = stripe_sub["items"]["data"][0]["price"]["id"]
    plan = Plan.objects.filter(stripe_price_id=price_id).first()
    period_end = stripe_sub.get("current_period_end")

    Subscription.objects.update_or_create(
        stripe_subscription_id=stripe_sub["id"],
        defaults={
            "organization": organization,
            "plan": plan,
            "stripe_customer_id": stripe_sub["customer"],
            "status": stripe_sub["status"],
            "current_period_end": (
                datetime.fromtimestamp(period_end, tz=timezone.utc) if period_end else None
            ),
            "cancel_at_period_end": stripe_sub.get("cancel_at_period_end", False),
        },
    )


def _on_checkout_completed(session):
    # The subscription.created/updated events carry the full subscription object;
    # this just logs completion for observability.
    logger.info("Checkout completed for customer %s", session.get("customer"))


def _on_subscription_change(stripe_sub):
    _upsert_subscription(stripe_sub)


def _on_subscription_deleted(stripe_sub):
    Subscription.objects.filter(stripe_subscription_id=stripe_sub["id"]).update(status="canceled")


_HANDLERS = {
    "checkout.session.completed": _on_checkout_completed,
    "customer.subscription.created": _on_subscription_change,
    "customer.subscription.updated": _on_subscription_change,
    "customer.subscription.deleted": _on_subscription_deleted,
}
