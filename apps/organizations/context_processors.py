def current_organization(request):
    org = getattr(request, "organization", None)
    memberships = []
    if request.user.is_authenticated:
        memberships = list(
            request.user.memberships.select_related("organization").order_by("organization__name")
        )
    return {
        "current_organization": org,
        "user_organizations": [m.organization for m in memberships],
    }
