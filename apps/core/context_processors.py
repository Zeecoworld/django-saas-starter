from django.conf import settings


def site_settings(request):
    return {"SITE_NAME": settings.SITE_NAME, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY}
