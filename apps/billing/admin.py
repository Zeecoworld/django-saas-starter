from django.contrib import admin

from .models import Plan, Subscription, WebhookEvent


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "interval", "display_price", "is_active"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["organization", "plan", "status", "current_period_end"]
    list_filter = ["status"]
    search_fields = ["organization__name", "stripe_customer_id", "stripe_subscription_id"]


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ["event_type", "stripe_event_id", "processed_at"]
    readonly_fields = ["stripe_event_id", "event_type", "payload", "processed_at"]
