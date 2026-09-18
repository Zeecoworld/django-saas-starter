from django import forms

from .models import Invitation, Membership, Organization


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"placeholder": "Acme Inc."})}


class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ["email", "role"]
        widgets = {"email": forms.EmailInput(attrs={"placeholder": "teammate@company.com"})}


class MembershipRoleForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["role"]
