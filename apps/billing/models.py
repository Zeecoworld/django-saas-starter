from django.db import models

from apps.organizations.models import Organization


class Plan(models.Model):
    """Mirrors a Stripe Price. Keep this in sync with your Stripe dashboard."""

    name = models.CharField(max_length=100)
    stripe_price_id = models.CharField(max_length=100, unique=True)
    interval = models.CharField(max_length=20, choices=[("month", "Monthly"), ("year", "Yearly")])
    amount_cents = models.PositiveIntegerField(
        help_text="Price in the smallest currency unit, e.g. cents"
    )
    currency = models.CharField(max_length=3, default="usd")
    features = models.JSONField(
        default=list, blank=True, help_text="List of feature strings for pricing page"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.interval})"

    @property
    def display_price(self):
        return f"${self.amount_cents / 100:,.2f}"


class Subscription(models.Model):
    class Status(models.TextChoices):
        TRIALING = "trialing", "Trialing"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past due"
        CANCELED = "canceled", "Canceled"
        INCOMPLETE = "incomplete", "Incomplete"
        UNPAID = "unpaid", "Unpaid"

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, null=True, related_name="subscriptions"
    )
    stripe_customer_id = models.CharField(max_length=100)
    stripe_subscription_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INCOMPLETE)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization} - {self.status}"


class WebhookEvent(models.Model):
    """Log of processed Stripe webhook events, used to guarantee idempotency."""

    stripe_event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} ({self.stripe_event_id})"
