from functools import wraps

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def organization_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.organization is None:
            messages.warning(request, "You need to create or join an organization first.")
            return redirect("organizations:create")
        return view_func(request, *args, **kwargs)

    return wrapper


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            membership = request.organization.memberships.filter(user=request.user).first()
            if membership is None or membership.role not in roles:
                raise PermissionDenied("You don't have permission to do that.")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
