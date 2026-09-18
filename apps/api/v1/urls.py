from rest_framework.routers import DefaultRouter

from . import views

app_name = "api_v1"

router = DefaultRouter()
router.register("me", views.MeView, basename="me")
router.register("organizations", views.OrganizationViewSet, basename="organization")

urlpatterns = router.urls
