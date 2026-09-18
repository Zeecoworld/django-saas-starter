from django.urls import path

from . import views

app_name = "billing"

urlpatterns = [
    path("pricing/", views.pricing, name="pricing"),
    path("checkout/<int:plan_id>/", views.checkout, name="checkout"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("portal/", views.billing_portal, name="portal"),
    path("webhook/", views.stripe_webhook, name="webhook"),
]
