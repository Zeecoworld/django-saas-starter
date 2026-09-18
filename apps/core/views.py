from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def landing(request):
    if request.user.is_authenticated:
        from django.shortcuts import redirect

        return redirect("core:dashboard")
    return render(request, "core/landing.html")


@login_required
def dashboard(request):
    return render(request, "core/dashboard.html")
