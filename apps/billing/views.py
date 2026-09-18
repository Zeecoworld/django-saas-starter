import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.organizations.models import Membership
from apps.organizations.permissions import organization_required, role_required

from . import services, webhooks
from .models import Plan


def pricing(request):
    plans = Plan.objects.filter(is_active=True).order_by("amount_cents")
    return render(request, "billing/pricing.html", {"plans": plans})


@login_required
@organization_required
@role_required(Membership.Role.OWNER, Membership.Role.ADMIN)
def checkout(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)
    session = services.create_checkout_session(
        organization=request.organization,
        price_id=plan.stripe_price_id,
        success_url=request.build_absolute_uri(reverse("billing:checkout_success")),
        cancel_url=request.build_absolute_uri(reverse("billing:pricing")),
    )
    return redirect(session.url, permanent=False)


@login_required
@organization_required
def checkout_success(request):
    messages.success(
        request, "Thanks! Your subscription is being set up — it'll show up in a moment."
    )
    return redirect("core:dashboard")


@login_required
@organization_required
@role_required(Membership.Role.OWNER, Membership.Role.ADMIN)
def billing_portal(request):
    subscription = request.organization.active_subscription
    if not subscription:
        messages.info(request, "No active subscription yet — pick a plan first.")
        return redirect("billing:pricing")
    session = services.create_billing_portal_session(
        customer_id=subscription.stripe_customer_id,
        return_url=request.build_absolute_uri(reverse("core:dashboard")),
    )
    return redirect(session.url, permanent=False)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = services.construct_webhook_event(payload, sig_header)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest("Invalid webhook signature")

    webhooks.handle_event(event)
    return HttpResponse(status=200)
