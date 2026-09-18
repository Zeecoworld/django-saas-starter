from django.contrib import admin

from .models import Invitation, Membership, Organization


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "owner", "is_active", "created_at"]
    search_fields = ["name", "slug", "owner__email"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MembershipInline]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["email", "organization", "role", "accepted", "created_at"]
    list_filter = ["accepted", "role"]
