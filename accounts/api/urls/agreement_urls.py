from django.urls import include, path

from rest_framework.routers import DefaultRouter

from accounts.api.views.agreement_views import AgreementViewSet, UserAgreementViewSet

router = DefaultRouter()
router.register(r"user-agreements", UserAgreementViewSet, basename="user_agreements")
router.register(r"agreements", AgreementViewSet, basename="agreements")

urlpatterns = [
    path("", include(router.urls)),
]
