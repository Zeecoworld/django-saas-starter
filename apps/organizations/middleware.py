from .models import Organization


class CurrentOrganizationMiddleware:
    """
    Resolves the "current" organization for a request from the session,
    falling back to the user's first membership. Exposes it as request.organization.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        if request.user.is_authenticated:
            org_id = request.session.get("current_organization_id")
            org = None
            if org_id:
                org = Organization.objects.filter(id=org_id, members=request.user).first()
            if org is None:
                membership = request.user.memberships.select_related("organization").first()
                org = membership.organization if membership else None
                if org:
                    request.session["current_organization_id"] = str(org.id)
            request.organization = org
        return self.get_response(request)
