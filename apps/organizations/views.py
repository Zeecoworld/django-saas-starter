from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import InvitationForm, OrganizationForm
from .models import Invitation, Membership, Organization
from .permissions import organization_required, role_required
from .tasks import send_invitation_email


@login_required
def create_organization(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            org = form.save(commit=False)
            org.owner = request.user
            org.save()
            Membership.objects.create(
                organization=org, user=request.user, role=Membership.Role.OWNER
            )
            request.session["current_organization_id"] = str(org.id)
            messages.success(request, f"{org.name} is ready to go.")
            return redirect("core:dashboard")
    else:
        form = OrganizationForm()
    return render(request, "organizations/create.html", {"form": form})


@login_required
def switch_organization(request, org_id):
    org = get_object_or_404(Organization, id=org_id, members=request.user)
    request.session["current_organization_id"] = str(org.id)
    return redirect("core:dashboard")


@login_required
@organization_required
def team(request):
    members = request.organization.memberships.select_related("user").order_by(
        "-role", "user__email"
    )
    pending_invites = request.organization.invitations.filter(accepted=False)
    invite_form = InvitationForm()
    return render(
        request,
        "organizations/team.html",
        {"members": members, "pending_invites": pending_invites, "invite_form": invite_form},
    )


@login_required
@organization_required
@role_required(Membership.Role.OWNER, Membership.Role.ADMIN)
def invite_member(request):
    if request.method == "POST":
        form = InvitationForm(request.POST)
        if form.is_valid():
            invite = form.save(commit=False)
            invite.organization = request.organization
            invite.invited_by = request.user
            invite.save()
            send_invitation_email.delay(str(invite.id))
            messages.success(request, f"Invitation sent to {invite.email}.")
        else:
            messages.error(request, "Please correct the errors below.")
    return redirect("organizations:team")


@login_required
@organization_required
@role_required(Membership.Role.OWNER, Membership.Role.ADMIN)
@require_POST
def remove_member(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id, organization=request.organization)
    if membership.role == Membership.Role.OWNER:
        raise PermissionDenied("The owner can't be removed.")
    membership.delete()
    messages.success(request, "Member removed.")
    return redirect("organizations:team")


@login_required
def accept_invitation(request, token):
    invite = get_object_or_404(Invitation, id=token, accepted=False)
    if invite.email.lower() != request.user.email.lower():
        messages.error(request, "This invitation was sent to a different email address.")
        return redirect("core:dashboard")
    Membership.objects.get_or_create(
        organization=invite.organization, user=request.user, defaults={"role": invite.role}
    )
    invite.accepted = True
    invite.save(update_fields=["accepted"])
    request.session["current_organization_id"] = str(invite.organization.id)
    messages.success(request, f"You've joined {invite.organization.name}.")
    return redirect("core:dashboard")
