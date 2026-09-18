from django.urls import path

from . import views

app_name = "organizations"

urlpatterns = [
    path("create/", views.create_organization, name="create"),
    path("switch/<uuid:org_id>/", views.switch_organization, name="switch"),
    path("team/", views.team, name="team"),
    path("team/invite/", views.invite_member, name="invite"),
    path("team/remove/<int:membership_id>/", views.remove_member, name="remove_member"),
    path("invitations/<uuid:token>/accept/", views.accept_invitation, name="accept_invitation"),
]
