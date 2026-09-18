from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Invitation


@shared_task
def send_invitation_email(invitation_id):
    invite = Invitation.objects.select_related("organization", "invited_by").get(id=invitation_id)
    accept_url = f"{settings.SITE_URL}/org/invitations/{invite.id}/accept/"
    context = {"invite": invite, "accept_url": accept_url}
    message = render_to_string("organizations/email/invitation.txt", context)
    send_mail(
        subject=f"You've been invited to join {invite.organization.name}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invite.email],
    )
